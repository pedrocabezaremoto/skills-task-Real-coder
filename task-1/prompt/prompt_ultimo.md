# KOTLIN IMPLEMENTATION TASK: SCADA Backend Service

## Context

An oil field operations team manages 200 wells across 40 facilities connected to sales
delivery points. Build a Kotlin backend service that ingests field telemetry, monitors
channel health, reconciles production allocation, manages alarms, generates regulatory
reports, AND archives raw data.

**Strict Air-Gap & No-Egress Constraint:** Forbid ALL outbound network access in code
AND dependencies, including `java.net` sockets, Ktor HTTP clients, OkHttp, WebSockets,
SMTP, cloud SDKs, telemetry exporters, AND any non-local JDBC targets. The server MUST
bind ONLY to `127.0.0.1`. All inputs MUST come solely from the bundled sample data AND
local SQLite database.

## Tech Stack

- **Language:** Kotlin 1.9
- **Framework:** Ktor 2.3
- **Database:** SQLite via Exposed ORM 0.44

---

## Requirements

**R01 — Telemetry Ingestion & Channel Quality Flags**

Implement an append-only `telemetry` table AND a `channel_status` table. Each telemetry
row MUST include a `quality_state` field set to exactly one of three values:

- `"NORMAL"`: the reading passes all checks.
- `"SUSPECTED_FLATLINE"`: the last 5 readings for `(well_id, channel)` are all identical
  AND `modem_diagnostic_code = "OK"`. The `modem_diagnostic_code = "OK"` check is
  mandatory to rule out a communication fault before classifying as flatline.
- `"COMM_OVERDUE"`: `current_time − last_seen > 2 × expected_cadence_minutes`.

The `channel_status` table MUST persist this canonical `quality_state` per channel.
Additionally, for all channels with `quality_state = "COMM_OVERDUE"`, group them by
`(facility_id, transport)`: if the count of `COMM_OVERDUE` channels in that group is
≥ 3, set `inferred_cause = "suspected_transport_path_outage"`. Otherwise set
`inferred_cause = "isolated_local_fault"`. Both values are heuristic classifications
derived solely from overdue count and transport grouping. The system does NOT have
access to modem RSSI, satellite terminal state, or radio backbone diagnostics;
therefore these values represent operational heuristics only, NOT ground-truth
transport diagnostics.

A background coroutine MUST launch on application startup AND repeat every 60 seconds,
executing this evaluation AND upserting `channel_status` rows.

**Bounded Scan Constraint:** The coroutine MUST use the composite index
`(well_id, channel, timestamp, id)` to fetch ONLY the most recent 5 readings per
`(well_id, channel)` via indexed queries. Full-table scans are FORBIDDEN.

The system MUST expose `POST /ingest/telemetry` accepting a `TelemetryReading` payload
to support ongoing local ingestion beyond the seeded bootstrap data.

---

**R02 — Scale & Sample Data**

The `SampleDataGenerator` MUST insert exactly 200 wells AND 40 facilities (5 wells per
facility). Transport cadence assignments: wells 1–80 use radio transport with 1-minute
cadence; wells 81–160 use cellular transport with 15-minute cadence; wells 161–200 use
satellite transport with 60-minute cadence.

Seed exactly 72 hours of telemetry strictly as bootstrap demo data; this 72-hour window
represents the size of the bundled sample dataset only and does NOT define the archive
retention limit. The append-only `telemetry` table schema MUST support unbounded
retention at native resolution. The `POST /ingest/telemetry` endpoint MUST accept new
readings indefinitely beyond the 72-hour seed window with no enforced upper bound on
stored rows.

Seed at least 31 days of alarm history containing both acknowledged AND unacknowledged
entries. Use `Random(42)` for full reproducibility.

---

**R03 — Production Allocation**

Compute daily per-well allocation as follows:

1. `gross_volume`: use `tank_gauge_readings` as the primary source. When no tank gauge
   data exists for that well AND date, use `wellhead_estimates` as the fallback. Set
   `source_flag = "measured"` for tank gauge data. Set `source_flag = "estimated"` for
   wellhead estimate data.
2. `net_oil_volume = gross_volume − compressor_recycled − fuel_used`. If this value is
   less than zero, clamp it to zero before any further computation. A well with clamped
   `net_oil_volume = 0` contributes zero to the delivery point denominator.
3. `average_gor` = arithmetic mean of all GOR telemetry readings for that well AND date.
4. `net_gas_volume = net_oil_volume × average_gor`.
5. `delivery_point_net_oil` = sum of `net_oil_volume` (post-clamp) for ALL wells
   assigned to the same `delivery_point_id` on that date. This sum is always ≥ 0.
6. If `delivery_point_net_oil > 0`, set
   `sales_meter_volume = sales_meter_readings.volume × (well_net_oil / delivery_point_net_oil)`.
   If `delivery_point_net_oil = 0`, set `sales_meter_volume = 0`.
7. Set `allocation_status = "allocated"` when `delivery_point_net_oil > 0`. Set
   `allocation_status = "unallocatable"` when `delivery_point_net_oil = 0`.
8. `variance_oil = net_oil_volume − sales_meter_volume`.

The `delivery_point_net_oil` denominator MUST be used consistently across all allocation
computations AND all downstream report generation. No facility-level aggregation replaces
the delivery-point-level denominator at any step.

---

**R04 — Anomaly Detection**

`GET /dashboard/wells/anomalies` MUST first call
`AuthorizationService.getAllowedFacilities(token)` to obtain the caller's permitted
facility set. The service MUST prefilter all scanned wells to that facility set before
executing any anomaly computation. Return wells where BOTH of the following conditions
are met:

- Pressure trend: 3 consecutive readings each increase by more than 10% over the prior
  reading.
- GOR shift: the mean difference between adjacent 6-hour windows, computed on resampled
  1-hour buckets, exceeds 15%, with a minimum data completeness threshold applied per
  bucket.

---

**R05 — Alarm Suppression**

An alarm record MUST have `suppressed = true` when the count of records for the same
`(well_id, alarm_type)` pair within the last 30 days where `acknowledged = false` is
≥ 20. This count of unacknowledged records is the sole suppression predicate. The
presence of any acknowledged records for the same pair within that window does NOT affect
the suppression decision.

`GET /alarms/active` MUST first call `AuthorizationService.getAllowedFacilities(token)`
to obtain the permitted facility set. The service MUST filter alarms to wells belonging
to that facility set before applying the suppression exclusion.

---

**R06 — Regulatory Reporting**

`GET /reports/regulatory` generates engineering-estimate reports derived from the R03
production allocation pipeline. All report values are derived from mixed measured AND
estimated inputs traceable via `source_flag`. Reports MUST be restricted to wells within
the caller's permitted facility set obtained from
`AuthorizationService.getAllowedFacilities(token)`. The `orgId` query parameter MUST NOT
be used for any authorization decision.

Report types:

- `"federal_ghg"`: methane AND CO2e derived from `net_gas_volume`. The
  `calculation_basis` field MUST equal the `source_flag` for that entry.
- `"state_production"`: per-well `net_oil_volume` totals.
- `"blm_lease"`: totals grouped by `lease_id`.

---

**R07 — Keyset Pagination Archive**

`GET /archive/telemetry`: both `well_id` AND `channel` query parameters are MANDATORY.
Requests missing `well_id` MUST return `400 Bad Request`. Requests missing `channel`
MUST return `400 Bad Request`. There is NO channel-optional code path in this endpoint.

The implementation MUST define TWO indexes on the `telemetry` table:

- Index A: `(well_id, channel, timestamp, id)` — used when both `well_id` AND `channel`
  are constrained, which is the ONLY permitted query shape for this endpoint.
- Index B: `(well_id, timestamp, id)` — reserved for internal queries only; not used
  by this endpoint.

Results MUST be ordered by `channel ASC, timestamp ASC, id ASC`. The endpoint MUST
accept a `cursor: String?` query parameter containing an opaque Base64 string that
decodes to the composite key `"well_id:channel:timestamp:id"`. The server MUST apply
the same `(well_id, channel)` filter that was active when the cursor was generated.
The cursor MUST NOT be decoded with a channel-absent fallback path.

The endpoint MUST first call `AuthorizationService.authorize(token, facilityId,
"read_archive")` before returning any data. The archive supports append-only long-term
persistence beyond seeded data via `POST /ingest/telemetry`.

---

**R08 — Multi-Organization RBAC**

Facility scope MUST be stored in a normalized join table
`user_role_facility_scopes(user_role_id INTEGER, facility_id INTEGER)`. There MUST be NO
scalar `facilityAssignmentScope` column anywhere in the schema. There is NO varchar
encoding of facility scope anywhere in any table. Facility scope is stored exclusively
in `UserRoleFacilityScopes`.

Resolve user identity AND organization context server-side from a seeded
`api_tokens(token VARCHAR PK, user_id INTEGER, organization_id INTEGER)` table. Identity
MUST NOT be derived from caller-supplied headers.

`AuthorizationService` MUST expose:

- `authorize(token: String, facilityId: Int, operation: String): Boolean` for
  per-facility decisions.
- `getAllowedFacilities(token: String): List<Int>` for multi-facility pre-filtering.

Every call to either method MUST insert exactly one row into `audit_logs` with a
`reason_code` field populated.

---

**Universal Authorization Requirement**

Every data-bearing endpoint MUST call `AuthorizationService` before processing or
returning any data. The required call per endpoint is:

| Endpoint                       | Required call                                   |
|--------------------------------|-------------------------------------------------|
| GET /dashboard/wells/anomalies | getAllowedFacilities(token) — prefilter wells    |
| GET /alarms/active             | getAllowedFacilities(token) — prefilter alarms   |
| GET /reports/regulatory        | getAllowedFacilities(token) — prefilter entries  |
| GET /archive/telemetry         | authorize(token, facilityId, "read_archive")    |
| POST /ingest/telemetry         | authorize(token, facilityId, "write_telemetry") |

No endpoint returns any well, alarm, telemetry, or report data before the corresponding
AuthorizationService call completes and confirms access.

---

## Expected Interface

### Models

- **Path:** `src/main/kotlin/model/TelemetryReading.kt`
- **Name:** `TelemetryReading`
- **Type:** `@Serializable data class`
- **Input:** `id: Long`, `wellId: Int`, `facilityId: Int`, `ingestTimestamp: String`,
  `sourceTimestamp: String`, `channel: String`, `value: Double`,
  `qualityState: String`, `modemDiagnosticCode: String`
- **Output:** N/A
- **Description:** DTO for a single telemetry reading. `qualityState` MUST be exactly
  one of: `"NORMAL"`, `"SUSPECTED_FLATLINE"`, `"COMM_OVERDUE"`.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/ProductionAllocation.kt`
- **Name:** `ProductionAllocation`
- **Type:** `@Serializable data class`
- **Input:** `wellId: Int`, `date: String`, `grossVolume: Double`,
  `netOilVolume: Double`, `averageGor: Double`, `netGasVolume: Double`,
  `salesMeterVolume: Double`, `varianceOil: Double`, `sourceFlag: String`,
  `allocationStatus: String`
- **Output:** N/A
- **Description:** Per-well daily allocation. `allocationStatus` is `"allocated"` when
  `delivery_point_net_oil > 0`; `"unallocatable"` when `delivery_point_net_oil = 0`.
  `salesMeterVolume` uses the `delivery_point_net_oil` denominator as defined in R03.
  `net_oil_volume` is clamped to zero before summation if the raw value is negative.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/ChannelStatus.kt`
- **Name:** `ChannelStatus`
- **Type:** `@Serializable data class`
- **Input:** `wellId: Int`, `facilityId: Int`, `channel: String`,
  `qualityState: String`, `inferredCause: String?`, `lastSeen: String`
- **Output:** N/A
- **Description:** Persisted canonical quality state per channel. `qualityState` MUST
  be exactly one of: `"NORMAL"`, `"SUSPECTED_FLATLINE"`, `"COMM_OVERDUE"`.
  `inferredCause` is non-null only when `qualityState = "COMM_OVERDUE"` and contains
  a heuristic classification only.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/WellAnomaly.kt`
- **Name:** `WellAnomaly`
- **Type:** `@Serializable data class`
- **Input:** `wellId: Int`, `facilityId: Int`, `anomalyType: String`,
  `details: String`, `detectedAt: String`
- **Output:** N/A
- **Description:** DTO for anomaly detection results.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/Alarm.kt`
- **Name:** `Alarm`
- **Type:** `@Serializable data class`
- **Input:** `id: Long`, `wellId: Int`, `facilityId: Int`, `alarmType: String`,
  `severity: String`, `message: String`, `triggeredAt: String`,
  `acknowledged: Boolean`, `suppressed: Boolean`
- **Output:** N/A
- **Description:** DTO for alarm records.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/RegulatoryReport.kt`
- **Name:** `RegulatoryReport`
- **Type:** `@Serializable data class`
- **Input:** `reportType: String`, `generatedAt: String`,
  `entries: List<RegulatoryReportEntry>`
- **Output:** N/A
- **Description:** Top-level regulatory report wrapper.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/RegulatoryReport.kt`
- **Name:** `RegulatoryReportEntry`
- **Type:** `@Serializable data class`
- **Input:** `wellId: Int?`, `facilityId: Int?`, `leaseId: String?`,
  `volume: Double`, `methane: Double?`, `co2e: Double?`,
  `calculationBasis: String`
- **Output:** N/A
- **Description:** Individual report line item. `calculationBasis` MUST equal the
  `source_flag` from R03 for that entry.
- **Decorators:** `@Serializable`

---

- **Path:** `src/main/kotlin/model/ArchivePage.kt`
- **Name:** `ArchivePage`
- **Type:** `@Serializable data class`
- **Input:** `data: List<TelemetryReading>`, `nextCursor: String?`
- **Output:** N/A
- **Description:** Paginated archive response. `nextCursor` is an opaque Base64 string
  encoding `"well_id:channel:timestamp:id"`.
- **Decorators:** `@Serializable`

---

### Exposed ORM Table Definitions

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `ApiTokens`
  | **Type:** `object : Table("api_tokens")`
  | **Description:** Columns: `token` (varchar PK), `userId` (integer),
  `organizationId` (integer). Trusted identity source; identity MUST NOT be derived
  from caller-supplied headers.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `Wells`
  | **Type:** `object : Table("wells")`
  | **Description:** Columns: `id` (PK), `name`, `facilityId`, `transport`, `leaseId`.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `Facilities`
  | **Type:** `object : Table("facilities")`
  | **Description:** Columns: `id` (PK), `name`, `organizationId`.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `TelemetryReadings`
  | **Type:** `object : Table("telemetry")`
  | **Description:** Columns: `id`, `wellId`, `facilityId`, `ingestTimestamp`,
  `sourceTimestamp`, `channel`, `value`, `qualityState`, `modemDiagnosticCode`.
  Index A: `(well_id, channel, timestamp, id)`. Index B: `(well_id, timestamp, id)`.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `ChannelStatuses`
  | **Type:** `object : Table("channel_status")`
  | **Description:** Columns: `wellId`, `facilityId`, `channel`, `qualityState`,
  `inferredCause`, `lastSeen`. Upserted by the background coroutine every 60 seconds.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `UserOrganizationRoles`
  | **Type:** `object : Table("user_organization_roles")`
  | **Description:** Columns: `id` (PK), `userId`, `organizationId`, `role`.
  There is NO `facilityAssignmentScope` column. There is NO varchar encoding of
  facility scope anywhere in this table or any other table. Facility scope is stored
  exclusively in `UserRoleFacilityScopes`.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `UserRoleFacilityScopes`
  | **Type:** `object : Table("user_role_facility_scopes")`
  | **Description:** Normalized join table. Columns: `userRoleId`
  (FK → UserOrganizationRoles.id), `facilityId` (FK → Facilities.id).
  One row per facility assignment per user role.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `AuditLogs`
  | **Type:** `object : Table("audit_logs")`
  | **Description:** Columns: `id`, `userId`, `organizationId`, `facilityId`,
  `operation`, `decision`, `reasonCode`, `timestamp`.
  One row inserted per `AuthorizationService` method call.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `WellDeliveryPointAssignments`
  | **Type:** `object : Table("well_delivery_point_assignments")`
  | **Description:** Maps wells to sales delivery points via `deliveryPointId`.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `TankGaugeReadings`
  | **Type:** `object : Table("tank_gauge_readings")`
  | **Description:** Well-level daily volume readings. Primary source for R03.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `WellheadEstimates`
  | **Type:** `object : Table("wellhead_estimates")`
  | **Description:** Well-level daily volume estimates. Fallback source for R03 when
  no tank gauge data exists for that well AND date.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `SalesMeterReadings`
  | **Type:** `object : Table("sales_meter_readings")`
  | **Description:** Delivery-point-level daily sales meter readings.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `CompressorLogs`
  | **Type:** `object : Table("compressor_logs")`
  | **Description:** Well-level daily compressor recycled volume. Subtracted in R03
  step 2 before net_oil_volume clamp is applied.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `FuelUseLogs`
  | **Type:** `object : Table("fuel_use_logs")`
  | **Description:** Well-level daily fuel usage volume. Subtracted in R03 step 2
  before net_oil_volume clamp is applied.

- **Path:** `src/main/kotlin/db/Tables.kt` | **Name:** `AlarmsTable`
  | **Type:** `object : Table("alarms")`
  | **Description:** Alarm records with `acknowledged` AND `suppressed` boolean columns.

---

### Services

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
  | **Name:** `AuthorizationService` | **Type:** class
  | **Input:** `db: Database`
  | **Description:** Resolves identity from `api_tokens` server-side. Exposes
  `authorize(token: String, facilityId: Int, operation: String): Boolean` AND
  `getAllowedFacilities(token: String): List<Int>`. Every call to either method MUST
  insert exactly one row into `audit_logs` with a `reason_code`.

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
  | **Name:** `ProductionAllocationService` | **Type:** class
  | **Input:** `db: Database`
  | **Description:** Implements R03. Clamps `net_oil_volume` to zero when raw value
  is negative. Uses `delivery_point_net_oil` as the sole denominator for
  `sales_meter_volume`. Applies zero-denominator guard AND sets `allocationStatus`.

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
  | **Name:** `ChannelStatusService` | **Type:** class
  | **Input:** `db: Database`
  | **Description:** Evaluates all channels AND writes canonical `qualityState` to
  `ChannelStatuses`. Runs every 60 seconds using indexed queries only. Full-table
  scans are FORBIDDEN.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
  | **Name:** `AnomalyDetectionService` | **Type:** class
  | **Input:** `db: Database`, `authorizationService: AuthorizationService`
  | **Description:** Calls `getAllowedFacilities(token)` first, prefilters wells to
  that set, then scans for anomalies.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
  | **Name:** `AlarmService` | **Type:** class
  | **Input:** `db: Database`, `authorizationService: AuthorizationService`
  | **Description:** Calls `getAllowedFacilities(token)` first, prefilters alarms to
  wells in that facility set, then applies suppression exclusion based solely on count
  of `acknowledged = false` records ≥ 20 in the last 30 days.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
  | **Name:** `RegulatoryReportService` | **Type:** class
  | **Input:** `db: Database`,
  `productionAllocationService: ProductionAllocationService`,
  `authorizationService: AuthorizationService`
  | **Description:** Calls `getAllowedFacilities(token)` first AND restricts report
  entries to permitted facilities. Inserts one audit log row per report access.

---

### Generator

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
  | **Name:** `SampleDataGenerator` | **Type:** `object`
  | **Input:** `generate(database: Database): Unit`
  | **Description:** Seeds 200 wells, 40 facilities, `api_tokens`, 72 hours of
  telemetry with canonical `qualityState`, AND 31 days of alarm history with both
  acknowledged AND unacknowledged entries. Uses `Random(42)`.

---

### API Endpoints

- **Path:** `POST /ingest/telemetry`
  | **Input:** Body: `TelemetryReading` (JSON). Header: `Authorization: String`.
  | **Output:** `201 Created`
  | **Description:** Calls `authorize(token, facilityId, "write_telemetry")` first.
  Appends one telemetry reading to the append-only store with no upper bound on total
  stored rows.

- **Path:** `GET /dashboard/wells/anomalies`
  | **Input:** Query: `facilityId: Int?`. Header: `Authorization: String`.
  | **Output:** `200 OK` → `List<WellAnomaly>`
  | **Description:** Calls `getAllowedFacilities(token)` AND prefilters wells to
  permitted set before executing any anomaly scan.

- **Path:** `GET /alarms/active`
  | **Input:** Query: `facilityId: Int?`, `severity: String?`.
  Header: `Authorization: String`.
  | **Output:** `200 OK` → `List<Alarm>`
  | **Description:** Calls `getAllowedFacilities(token)` AND prefilters alarms to
  permitted facility set before applying suppression exclusion.

- **Path:** `GET /reports/regulatory`
  | **Input:** Query: `type: String` (MUST be exactly one of: `"federal_ghg"`,
  `"state_production"`, `"blm_lease"`), `startDate: String`, `endDate: String`.
  Header: `Authorization: String`.
  | **Output:** `200 OK` → `RegulatoryReport`
  | **Description:** Calls `getAllowedFacilities(token)` first. Organization scope
  derived from token only. `orgId` query parameter MUST NOT influence authorization.

- **Path:** `GET /archive/telemetry`
  | **Input:** Query: `wellId: Int` (required — returns `400` if absent),
  `channel: String` (required — returns `400` if absent), `cursor: String?`.
  Header: `Authorization: String`.
  | **Output:** `200 OK` → `ArchivePage`
  | **Description:** Calls `authorize(token, facilityId, "read_archive")` first.
  Orders results by `channel ASC, timestamp ASC, id ASC` using Index A
  `(well_id, channel, timestamp, id)`. Cursor decodes to
  `"well_id:channel:timestamp:id"`. There is NO channel-optional fallback path.

---

### Application Entry Point

- **Path:** `src/main/kotlin/Application.kt` | **Name:** `Application.module`
  | **Type:** Ktor module extension function
  | **Description:** Installs `ContentNegotiation` with kotlinx.serialization.
  Initializes SQLite via Exposed. Runs `SampleDataGenerator.generate` on empty DB.
  Launches `ChannelStatusService` background coroutine repeating every 60 seconds.
  Binds ONLY to `127.0.0.1`.
