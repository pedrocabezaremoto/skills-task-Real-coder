# KOTLIN IMPLEMENTATION TASK: SCADA Backend Service

## Context

An oil field operations team manages 200 wells across 40 facilities connected to sales delivery points. Build a Kotlin backend service that ingests field telemetry, monitors channel health, reconciles production allocation, manages alarms, generates regulatory reports, AND archives raw data.

**Strict Air-Gap & No-Egress Constraint:** Explicitly forbid ALL outbound network access in code AND dependencies, including `java.net` sockets, Ktor HTTP clients, OkHttp, WebSockets, SMTP, cloud SDKs, telemetry exporters, AND any non-local JDBC targets. The server MUST bind ONLY to `127.0.0.1`. All inputs MUST come solely from the bundled sample data AND local SQLite database.

## Tech Stack

- **Language:** Kotlin 1.9
- **Framework:** Ktor 2.3
- **Database:** SQLite via Exposed ORM 0.44

---

## Requirements

**R01 — Telemetry, Ingestion & Channel Quality Flags**
Implement an append-only `telemetry` table AND a `channel_status` table. Each telemetry row MUST include a canonical `quality_state` field. `quality_state` MUST be set to exactly one of three values: `"NORMAL"` when the reading passes all checks; `"SUSPECTED_FLATLINE"` when the last 5 readings for `(well_id, channel)` are all identical AND `modem_diagnostic_code = "OK"` (ruling out a comm fault); `"COMM_OVERDUE"` when `current_time - last_seen > 2 × expected_cadence_minutes`. The `ChannelStatus` table MUST persist this canonical `quality_state` per channel. Additionally, group `COMM_OVERDUE` channels by `(facility_id, transport)`: if count ≥ 3, set `inferred_cause = "probable_transport_path_outage"`, otherwise set `inferred_cause = "isolated_local_fault"`. A background coroutine MUST run on startup AND repeat every 60 seconds executing this evaluation AND upserting `channel_status` rows. **Bounded Scan Constraint:** The coroutine MUST use indexed queries that fetch ONLY the most recent 5 readings per `(well_id, channel)` via the composite index; full-table scans are FORBIDDEN. The system MUST also expose `POST /ingest/telemetry` accepting a `TelemetryReading` payload to support ongoing local ingestion beyond the seeded bootstrap data.

**R02 — Scale & Sample Data**
The `SampleDataGenerator` MUST insert exactly 200 wells AND 40 facilities (5 wells/facility). Transport cadence bands: wells 1–80 → radio/1 min, 81–160 → cellular/15 min, 161–200 → satellite/60 min. **Data Horizon:** Seed 72 hours of telemetry strictly for bootstrap/demo purposes; the append-only telemetry store MUST support continued local ingestion beyond the initial 72 hours via `POST /ingest/telemetry`. MUST seed at least **31 days of alarm history** including both acknowledged AND unacknowledged entries to satisfy suppression rules. Use `Random(42)` for full reproducibility.

**R03 — Production Allocation**
Compute daily per-well allocation using engineering estimates derived from mixed measured AND estimated inputs:
1. `gross_volume`: use `tank_gauge_readings` as the primary source; fallback to `wellhead_estimates` only when tank gauge data is absent for that date. Record `source_flag = "measured"` for tank gauge AND `source_flag = "estimated"` for wellhead estimate.
2. `net_oil_volume` = `gross_volume − compressor_recycled − fuel_used`.
3. `average_gor` = arithmetic mean of all GOR telemetry readings for that well AND date.
4. `net_gas_volume` = `net_oil_volume × average_gor`.
5. Compute `delivery_point_net_oil` = sum of `net_oil_volume` for ALL wells assigned to the same `delivery_point_id` on that date. If `delivery_point_net_oil > 0`, set `sales_meter_volume = sales_meter_readings.volume × (well_net_oil / delivery_point_net_oil)`. If `delivery_point_net_oil <= 0`, set `sales_meter_volume = 0`.
6. `allocationStatus` MUST be set to `"unallocatable"` if `delivery_point_net_oil <= 0`, otherwise it MUST be set to `"allocated"`.
7. `variance_oil` = `net_oil_volume − sales_meter_volume`.

**R04 — Anomaly Detection**
`GET /dashboard/wells/anomalies`: return wells where BOTH conditions are met: pressure trend (3 consecutive increases > 10%) AND GOR shift (> 15% mean difference between adjacent 6-hour windows computed on resampled 1-hour buckets with a minimum completeness threshold). The server MUST first call `AuthorizationService.getAllowedFacilities(token)` to obtain the caller's permitted facility set AND prefilter all scanned wells to that set before returning results.

**R05 — Alarm Suppression**
An alarm MUST be set to `suppressed = true` when the count of records for the same `(well_id, alarm_type)` pair in the last 30 days where `acknowledged = false` is ≥ 20. `GET /alarms/active` MUST first call `AuthorizationService.getAllowedFacilities(token)` to obtain the permitted facility set AND filter alarms to wells belonging to that set before applying suppression exclusion.

**R06 — Regulatory Reporting**
`GET /reports/regulatory` generates engineering-estimate reports derived from the R03 production allocation pipeline. Reports are derived from mixed measured AND estimated inputs traceable via `source_flag`. (1) `federal_ghg` — methane AND CO2e derived from `net_gas_volume`; `calculation_basis` MUST equal the `source_flag` for that entry. (2) `state_production` — per-well `net_oil_volume` totals. (3) `blm_lease` — totals grouped by `lease_id`. The server MUST first call `AuthorizationService.getAllowedFacilities(token)` AND restrict report entries to wells within the permitted facility set. MUST NOT use the `orgId` query parameter for authorization decisions.

**R07 — Keyset Pagination Archive**
`GET /archive/telemetry`: The `well_id` AND `channel` query parameters are BOTH MANDATORY; requests missing either MUST return `400 Bad Request`. Results MUST be ordered by `channel ASC, timestamp ASC, id ASC` to match the composite index. MUST implement a composite index on `(well_id, channel, timestamp, id)`. The endpoint MUST accept a single `cursor: String?` query parameter (opaque Base64) that decodes to the composite key `"well_id:channel:timestamp:id"`. The server MUST apply the same `(well_id, channel)` filter that was active when the cursor was generated. The archive MUST support append-only long-term persistence beyond seeded data via the `POST /ingest/telemetry` endpoint.

**R08 — Multi-Organization RBAC**
Facility scope MUST be stored in a normalized join table `user_role_facility_scopes(user_role_id INTEGER, facility_id INTEGER)`. There MUST be NO scalar `facilityAssignmentScope` varchar field anywhere in the schema. **Trust Link:** Resolve user identity AND organization context server-side from a seeded `api_tokens(token VARCHAR PK, user_id INTEGER, organization_id INTEGER)` table; MUST NOT derive identity from caller-supplied headers. `AuthorizationService` MUST expose two methods: `authorize(token, facilityId, operation): Boolean` for per-facility decisions AND `getAllowedFacilities(token): List<Int>` for pre-filtering multi-facility queries. Every call to either method MUST insert one row into `audit_logs` with a specific `reason_code`.

---

## Expected Interface

### Models

- **Path:** `src/main/kotlin/model/TelemetryReading.kt`
- **Name:** `TelemetryReading`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `ingestTimestamp: String`, `sourceTimestamp: String`, `channel: String`, `value: Double`, `qualityState: String`, `modemDiagnosticCode: String`
- **Output:** N/A (data class)
- **Description:** DTO for a single telemetry reading. `qualityState` MUST be exactly one of: `"NORMAL"`, `"SUSPECTED_FLATLINE"`, `"COMM_OVERDUE"`.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ProductionAllocation.kt`
- **Name:** `ProductionAllocation`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `date: String`, `grossVolume: Double`, `netOilVolume: Double`, `averageGor: Double`, `netGasVolume: Double`, `salesMeterVolume: Double`, `varianceOil: Double`, `sourceFlag: String`, `allocationStatus: String`
- **Output:** N/A (data class)
- **Description:** Per-well daily allocation. `allocationStatus` MUST be `"allocated"` when `delivery_point_net_oil > 0`, otherwise it MUST be `"unallocatable"`. `salesMeterVolume` uses `delivery_point_id` denominator per R03.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ChannelStatus.kt`
- **Name:** `ChannelStatus`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `channel: String`, `qualityState: String`, `inferredCause: String?`, `lastSeen: String`
- **Output:** N/A (data class)
- **Description:** Persisted canonical quality state per channel. `qualityState` MUST be exactly one of: `"NORMAL"`, `"SUSPECTED_FLATLINE"`, `"COMM_OVERDUE"`.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/WellAnomaly.kt`
- **Name:** `WellAnomaly`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `anomalyType: String`, `details: String`, `detectedAt: String`
- **Output:** N/A (data class)
- **Description:** DTO for anomaly detection results.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/Alarm.kt`
- **Name:** `Alarm`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `alarmType: String`, `severity: String`, `message: String`, `triggeredAt: String`, `acknowledged: Boolean`, `suppressed: Boolean`
- **Output:** N/A (data class)
- **Description:** DTO for alarm records.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/RegulatoryReport.kt`
- **Name:** `RegulatoryReport`
- **Type:** `@Serializable data class`
- **Input (constructor):** `reportType: String`, `generatedAt: String`, `entries: List<RegulatoryReportEntry>`
- **Output:** N/A (data class)
- **Description:** Top-level regulatory report wrapper.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/RegulatoryReport.kt`
- **Name:** `RegulatoryReportEntry`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int?`, `facilityId: Int?`, `leaseId: String?`, `volume: Double`, `methane: Double?`, `co2e: Double?`, `calculationBasis: String`
- **Output:** N/A (data class)
- **Description:** Individual line item. `calculationBasis` equals the `source_flag` from R03.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ArchivePage.kt`
- **Name:** `ArchivePage`
- **Type:** `@Serializable data class`
- **Input (constructor):** `data: List<TelemetryReading>`, `nextCursor: String?`
- **Output:** N/A (data class)
- **Description:** Paginated archive response. `nextCursor` is opaque Base64 encoding `"well_id:channel:timestamp:id"`.
- **Decorators:** `@Serializable`

### Exposed ORM Table Definitions

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ApiTokens`
- **Type:** `object : Table("api_tokens")`
- **Description:** Columns: `token` (varchar PK), `userId` (integer), `organizationId` (integer). Trusted identity source.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Wells`
- **Type:** `object : Table("wells")`
- **Description:** Columns: `id` (PK), `name`, `facilityId`, `transport`, `leaseId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Facilities`
- **Type:** `object : Table("facilities")`
- **Description:** Columns: `id` (PK), `name`, `organizationId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TelemetryReadings`
- **Type:** `object : Table("telemetry")`
- **Description:** Columns: `id`, `wellId`, `facilityId`, `ingestTimestamp`, `sourceTimestamp`, `channel`, `value`, `qualityState`, `modemDiagnosticCode`. Composite index on `(well_id, channel, timestamp, id)`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ChannelStatuses`
- **Type:** `object : Table("channel_status")`
- **Description:** Columns: `wellId`, `facilityId`, `channel`, `qualityState`, `inferredCause`, `lastSeen`. Upserted by background coroutine.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `UserOrganizationRoles`
- **Type:** `object : Table("user_organization_roles")`
- **Description:** Columns: `id` (PK), `userId`, `organizationId`, `role`. No `facilityAssignmentScope` column.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `UserRoleFacilityScopes`
- **Type:** `object : Table("user_role_facility_scopes")`
- **Description:** Normalized join table. Columns: `userRoleId` (FK → UserOrganizationRoles.id), `facilityId` (FK → Facilities.id). One row per facility assignment.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AuditLogs`
- **Type:** `object : Table("audit_logs")`
- **Description:** Columns: `id`, `userId`, `organizationId`, `facilityId`, `operation`, `decision`, `reasonCode`, `timestamp`. One row inserted per AuthorizationService call.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellDeliveryPointAssignments`
- **Type:** `object : Table("well_delivery_point_assignments")`
- **Description:** Maps wells to sales delivery points.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TankGaugeReadings`
- **Type:** `object : Table("tank_gauge_readings")`
- **Description:** Well-level daily volume readings (primary source for R03).

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellheadEstimates`
- **Type:** `object : Table("wellhead_estimates")`
- **Description:** Well-level daily volume estimates (fallback for R03).

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `SalesMeterReadings`
- **Type:** `object : Table("sales_meter_readings")`
- **Description:** Delivery-point-level daily sales meter readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `CompressorLogs`
- **Type:** `object : Table("compressor_logs")`
- **Description:** Well-level daily compressor recycled volume. Subtracted in R03.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `FuelUseLogs`
- **Type:** `object : Table("fuel_use_logs")`
- **Description:** Well-level daily fuel usage volume. Subtracted in R03.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AlarmsTable`
- **Type:** `object : Table("alarms")`
- **Description:** Alarm records.

### Services

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A
- **Description:** Resolves identity from `api_tokens` server-side. Exposes `authorize(token: String, facilityId: Int, operation: String): Boolean` for per-facility decisions AND `getAllowedFacilities(token: String): List<Int>` for multi-facility pre-filtering. Every call inserts one `audit_logs` row with a `reason_code`.

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
- **Name:** `ProductionAllocationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A
- **Description:** Implements R03 including zero-denominator guard AND `allocationStatus` assignment.

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
- **Name:** `ChannelStatusService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A
- **Description:** Evaluates all channels AND writes canonical `qualityState` to `ChannelStatuses`. Runs every 60 seconds.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
- **Name:** `AnomalyDetectionService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Calls `getAllowedFacilities(token)` first, prefilters wells to that set, then scans for anomalies.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Calls `getAllowedFacilities(token)` first, prefilters alarms to wells in that facility set, then applies suppression exclusion.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
- **Name:** `RegulatoryReportService`
- **Type:** class
- **Input (constructor):** `db: Database`, `productionAllocationService: ProductionAllocationService`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Calls `getAllowedFacilities(token)` first AND restricts report entries to permitted facilities. Inserts audit log rows for every report access.

### Generator

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator`
- **Type:** `object`
- **Input (method):** `generate(database: Database): Unit`
- **Output:** `Unit`
- **Description:** Seeds 200 wells, 40 facilities, api_tokens, 72h telemetry with canonical `qualityState`, AND 31 days of alarm history with both acknowledged AND unacknowledged entries.

### API Endpoints

- **Path:** `POST /ingest/telemetry`
- **Name:** `ingestTelemetry`
- **Type:** API Endpoint
- **Input:** Body: `TelemetryReading` (JSON). Header: `Authorization: String` (api_token).
- **Output:** `201 Created`
- **Description:** Appends a telemetry reading. Supports ongoing local ingestion beyond seeded bootstrap data.

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getDashboardWellAnomalies`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `List<WellAnomaly>`
- **Description:** Calls `getAllowedFacilities(token)` first AND prefilters wells to permitted set before scanning.

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `severity: String?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `List<Alarm>`
- **Description:** Calls `getAllowedFacilities(token)` first AND prefilters alarms to permitted facility set.

- **Path:** `GET /reports/regulatory`
- **Name:** `getRegulatoryReport`
- **Type:** API Endpoint
- **Input:** Query params: `type: String` (MUST be exactly one of: `"federal_ghg"`, `"state_production"`, `"blm_lease"`), `startDate: String`, `endDate: String`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `RegulatoryReport`
- **Description:** Calls `getAllowedFacilities(token)` first. Organization scope derived from token only.

- **Path:** `GET /archive/telemetry`
- **Name:** `getArchiveTelemetry`
- **Type:** API Endpoint
- **Input:** Query params: `wellId: Int` (required), `channel: String` (required — returns `400` if absent), `cursor: String?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `ArchivePage`
- **Description:** Calls `authorize(token, facilityId, "read_archive")` first. Orders by `channel ASC, timestamp ASC, id ASC`. Cursor decodes to `"well_id:channel:timestamp:id"`.

### Application Entry Point

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `Application.module`
- **Type:** Ktor module extension function
- **Input:** None
- **Output:** `Unit`
- **Description:** Entry point. Installs `ContentNegotiation` with kotlinx.serialization. Initializes SQLite via Exposed. Runs `SampleDataGenerator.generate` on empty DB. Launches `ChannelStatusService` background coroutine every 60 seconds. Binds ONLY to `127.0.0.1`.
