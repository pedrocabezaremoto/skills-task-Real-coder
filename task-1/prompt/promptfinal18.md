# KOTLIN IMPLEMENTATION TASK: SCADA Backend Service

## Context

An oil field operations team manages 200 wells across 40 facilities connected to sales delivery points. Build a Kotlin backend service that ingests field telemetry, monitors channel health, reconciles production allocation, manages alarms, generates regulatory reports, AND archives raw data.

**Strict Air-Gap & No-Egress Constraint:** Explicitly forbid ALL outbound network access in code AND dependencies, including `java.net` sockets, Ktor HTTP clients, OkHttp, WebSockets, SMTP, cloud SDKs, telemetry exporters, AND any non-local JDBC targets. The server MUST bind ONLY to `127.0.0.1`. All inputs MUST come solely from the bundled sample data AND local SQLite database.

## Tech Stack

- **Language:** Kotlin 1.9
- **Framework:** Ktor 2.3
- **Database:** SQLite via Exposed ORM 0.44

## Requirements

**R01 — Telemetry & Channel Status**
Implement an append-only `telemetry` table AND a `channel_status` table. Each telemetry row MUST include `modem_diagnostic_code` (RTU-reported comm result code) AND `poll_result_code` (transport-layer poll outcome). A background coroutine MUST run on startup AND repeat every 60 seconds performing: (1) Flatline check — fetch the last 5 readings per `(well_id, channel)`; if all 5 values are identical AND `modem_diagnostic_code = "OK"`, set `signal_condition = "potential_sensor_flatline"`. (2) Outage check — if `current_time - last_seen > 2 * expected_cadence_minutes`, mark `connectivity_condition = "overdue"`; group overdue channels by `(facility_id, transport)`: if count ≥ 3 set `inferred_cause = "probable_transport_path_outage"`, otherwise set `inferred_cause = "isolated_local_fault"`.

**R02 — Scale & Sample Data**
The `SampleDataGenerator` MUST insert exactly 200 wells AND 40 facilities (5 wells/facility). Transport cadence bands: wells 1–80 → radio/1 min, 81–160 → cellular/15 min, 161–200 → satellite/60 min. **Data Horizon:** Seed 72 hours of telemetry strictly for bootstrap purposes. MUST seed at least **31 days of alarm history** (both acknowledged AND unacknowledged entries) to satisfy suppression rules. Use `Random(42)` for full reproducibility.

**R03 — Production Allocation**
Compute daily per-well allocation using engineering estimates derived from mixed measured AND estimated inputs:
1. `gross_volume` MUST use `tank_gauge_readings` as the primary source; fallback to `wellhead_estimates` only when tank gauge data is absent for that date. Record `source_flag` as `"measured"` when tank gauge is used AND `"estimated"` when wellhead estimate is used.
2. `net_oil_volume` = `gross_volume − compressor_recycled − fuel_used`.
3. `average_gor` = arithmetic mean of all GOR telemetry readings for that well AND date.
4. `net_gas_volume` = `net_oil_volume × average_gor`.
5. If `Σ net_oil_at_point > 0`, set `sales_meter_volume = meter_reading × (well_net_oil / Σ net_oil_at_point)`. If `Σ net_oil_at_point <= 0`, set `sales_meter_volume = 0`.
6. `allocationStatus` MUST be set to `"unallocatable"` if `Σ net_oil_at_point <= 0`, otherwise it MUST be set to `"allocated"`.
7. `variance_oil` = `net_oil_volume − sales_meter_volume`.

**R04 — Anomaly Detection**
`GET /dashboard/wells/anomalies`: return wells where BOTH conditions are met: pressure trend (3 consecutive increases > 10%) AND GOR shift (> 15% mean difference). **Feasibility Constraint:** The GOR shift evaluation MUST compute window means on resampled 1-hour buckets with explicit missing-data handling AND a minimum completeness threshold before comparing adjacent 6-hour windows.

**R05 — Alarm Suppression**
An alarm MUST be set to `suppressed = true` when the count of records for the same `(well_id, alarm_type)` pair in the last 30 days where `acknowledged = false` is ≥ 20. `GET /alarms/active` MUST exclude suppressed alarms AND enforce RBAC scope.

**R06 — Regulatory Reporting**
`GET /reports/regulatory` generates engineering-estimate reports derived from the production allocation pipeline (R03). Reports are NOT raw-instrument data; they are computed using the measured/estimated inputs defined in R03 with their `source_flag` traceable per entry. (1) `federal_ghg` — methane AND CO2e derived from `net_gas_volume`; include `calculation_basis = source_flag` per entry. (2) `state_production` — per-well `net_oil_volume` totals. (3) `blm_lease` — totals grouped by `lease_id`. **Security Constraint:** The server MUST derive accessible organizations from the authenticated `api_token` context; MUST NOT trust the `orgId` query parameter for authorization decisions.

**R07 — Keyset Pagination Archive**
`GET /archive/telemetry`: Implement append-only long-term persistence with configurable retention. The `channel` query parameter is MANDATORY; requests without it MUST return `400 Bad Request`. Results MUST be ordered by `timestamp ASC` AND `id ASC`. MUST implement a composite index on `(well_id, channel, timestamp, id)`. The endpoint MUST accept a single `cursor: String` query parameter (opaque Base64) that decodes the full composite key `"well_id:channel:timestamp:id"` AND MUST apply the same `(well_id, channel)` filter shape that was active when the cursor was generated.

**R08 — Multi-Organization RBAC**
Facility scope MUST be stored in a normalized join table `user_role_facility_scopes(user_role_id INTEGER, facility_id INTEGER)`. There MUST be NO scalar `facilityAssignmentScope` varchar field anywhere in the schema. **Trust Link Constraint:** Resolve user identity AND organization context server-side using a seeded `api_tokens(token, user_id, organization_id)` table; MUST NOT derive identity from caller-supplied headers. `AuthorizationService.authorize` MUST be the first call in EVERY endpoint handler that returns scoped operational, historical, AND regulatory data. Every call MUST insert one row into `audit_logs`.

---

## Expected Interface

### Models

- **Path:** `src/main/kotlin/model/TelemetryReading.kt`
- **Name:** `TelemetryReading`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `ingestTimestamp: String`, `sourceTimestamp: String`, `channel: String`, `value: Double`, `modemDiagnosticCode: String`, `pollResultCode: String`
- **Output:** N/A (data class)
- **Description:** DTO for a single telemetry reading preserving native resolution AND device-reported comm status.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ProductionAllocation.kt`
- **Name:** `ProductionAllocation`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `date: String`, `grossVolume: Double`, `netOilVolume: Double`, `averageGor: Double`, `netGasVolume: Double`, `salesMeterVolume: Double`, `varianceOil: Double`, `sourceFlag: String`, `allocationStatus: String`
- **Output:** N/A (data class)
- **Description:** Per-well daily allocation. `allocationStatus` MUST be `"allocated"` when `Σ net_oil_at_point > 0`, otherwise it MUST be `"unallocatable"`.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ChannelStatus.kt`
- **Name:** `ChannelStatus`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `channel: String`, `signalCondition: String`, `connectivityCondition: String`, `inferredCause: String?`, `lastSeen: String`
- **Output:** N/A (data class)
- **Description:** DTO for probabilistic channel health diagnostics.
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
- **Description:** Individual line item. `calculationBasis` contains the `source_flag` traceable to R03.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ArchivePage.kt`
- **Name:** `ArchivePage`
- **Type:** `@Serializable data class`
- **Input (constructor):** `data: List<TelemetryReading>`, `nextCursor: String?`
- **Output:** N/A (data class)
- **Description:** Paginated response with opaque Base64 cursor encoding `"well_id:channel:timestamp:id"`.
- **Decorators:** `@Serializable`

### Exposed ORM Table Definitions

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Wells`
- **Type:** `object : Table("wells")`
- **Description:** Columns: `id` (PK), `name`, `facilityId`, `transport`, `leaseId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Facilities`
- **Type:** `object : Table("facilities")`
- **Description:** Columns: `id` (PK), `name`, `organizationId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ApiTokens`
- **Type:** `object : Table("api_tokens")`
- **Description:** Columns: `token` (varchar, PK), `userId` (integer), `organizationId` (integer). Used by AuthorizationService as the trusted identity source.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TelemetryReadings`
- **Type:** `object : Table("telemetry")`
- **Description:** Columns: `id`, `wellId`, `facilityId`, `ingestTimestamp`, `sourceTimestamp`, `channel`, `value`, `modemDiagnosticCode`, `pollResultCode`. MUST include composite index `(well_id, channel, timestamp, id)`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ChannelStatuses`
- **Type:** `object : Table("channel_status")`
- **Description:** Health state store per R01.

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
- **Description:** Immutable audit trail. Columns: `id`, `userId`, `organizationId`, `facilityId`, `operation`, `decision`, `reasonCode`, `timestamp`.

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
- **Description:** Resolves identity from `api_tokens` table server-side. `authorize(token, facilityId, operation): Boolean`. Inserts one `audit_logs` row per call.

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
- **Description:** Background probabilistic diagnostics using `modemDiagnosticCode` AND `pollResultCode`.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
- **Name:** `AnomalyDetectionService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Detects pressure trend AND GOR shift anomalies. MUST call `AuthorizationService.authorize` before returning data.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Suppression: count of unacknowledged records ≥ 20 in 30 days. MUST call `AuthorizationService.authorize` before returning data.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
- **Name:** `RegulatoryReportService`
- **Type:** class
- **Input (constructor):** `db: Database`, `productionAllocationService: ProductionAllocationService`, `authorizationService: AuthorizationService`
- **Output:** N/A
- **Description:** Generates engineering-estimate reports per R06. MUST call `AuthorizationService.authorize` before returning data AND insert audit log rows.

### Generator

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator`
- **Type:** `object`
- **Input (method):** `generate(database: Database): Unit`
- **Output:** `Unit`
- **Description:** Seeds 200 wells, 40 facilities, 72h telemetry (with `modemDiagnosticCode` AND `pollResultCode`), AND 31 days of alarm history including both suppressed AND unsuppressed cases.

### API Endpoints

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getDashboardWellAnomalies`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `List<WellAnomaly>`
- **Description:** MUST call `AuthorizationService.authorize` as the first operation. Derives organization context from `Authorization` header server-side.

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `severity: String?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `List<Alarm>`
- **Description:** MUST call `AuthorizationService.authorize` as the first operation.

- **Path:** `GET /reports/regulatory`
- **Name:** `getRegulatoryReport`
- **Type:** API Endpoint
- **Input:** Query params: `type: String` (MUST be exactly one of: `"federal_ghg"`, `"state_production"`, `"blm_lease"`), `startDate: String`, `endDate: String`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `RegulatoryReport`
- **Description:** MUST call `AuthorizationService.authorize` as the first operation. Organization scope derived from token, NOT from query params.

- **Path:** `GET /archive/telemetry`
- **Name:** `getArchiveTelemetry`
- **Type:** API Endpoint
- **Input:** Query params: `wellId: Int` (required), `channel: String` (required — returns `400` if absent), `cursor: String?`. Header: `Authorization: String` (api_token).
- **Output:** `200 OK` → `ArchivePage`
- **Description:** MUST call `AuthorizationService.authorize` as the first operation. Uses composite index `(well_id, channel, timestamp, id)`. Cursor decodes to `"well_id:channel:timestamp:id"`.

### Application Entry Point

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `Application.module`
- **Type:** Ktor module extension function
- **Input:** None
- **Output:** `Unit`
- **Description:** Entry point. Installs `ContentNegotiation` with kotlinx.serialization. Initializes SQLite via Exposed. Runs `SampleDataGenerator.generate` on empty DB. Launches `ChannelStatusService` background coroutine every 60 seconds. Binds ONLY to `127.0.0.1`.
