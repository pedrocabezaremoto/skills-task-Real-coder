# KOTLIN IMPLEMENTATION TASK: SCADA Backend Service

## Context

An oil field operations team manages 200 wells across 40 facilities connected to sales delivery points. Build a Kotlin backend service that ingests field telemetry, monitors channel health, reconciles production allocation, manages alarms, generates regulatory reports, AND archives raw data. 

**No-Egress Constraint:** The service MUST NOT make any outbound network calls. Prohibit use of `java.net`, Ktor HTTP client, OkHttp, outbound socket connections, AND remote JDBC URLs. The server MUST bind only to `127.0.0.1`. All inputs MUST come solely from the bundled sample data AND local SQLite database.

## Tech Stack

- **Language:** Kotlin 1.9
- **Framework:** Ktor 2.3
- **Database:** SQLite via Exposed ORM 0.44

## Requirements

**R01 — Telemetry & Channel Status**
Implement an append-only `telemetry` table AND a `channel_status` table. A background coroutine MUST run on startup AND repeat every 60 seconds performing probabilistic diagnostics: (1) Flatline check — fetch the last 5 readings per `(well_id, channel)`; if all 5 values are identical, set `diagnostic_signal = "potential_flatline"`. (2) Outage check — if `current_time - last_seen > 2 * expected_cadence_minutes`, mark `connectivity_status = "overdue"`; group overdue channels by `(facility_id, transport)`: if count ≥ 3 set `inferred_cause = "transport_outage"`, else set `inferred_cause = "isolated_local_fault"`.

**R02 — Scale & Sample Data**
The `SampleDataGenerator` MUST insert exactly 200 wells AND 40 facilities (5 wells/facility). Transport cadence bands: wells 1–80 → radio/1 min, 81–160 → cellular/15 min, 161–200 → satellite/60 min. **Data Horizon:** Seed 72 hours of telemetry (including `source_timestamp` AND `ingest_timestamp`), but MUST seed at least **30 days of alarm history** to satisfy suppression rules. Use a fixed seed for reproducibility.

**R03 — Production Allocation**
Compute daily per-well allocation grounded in measured sources:
1. `gross_volume` MUST prioritize actual measured data: use `tank_gauge_readings` as the primary source; fallback to `wellhead_estimates` only when tank gauge data is missing for that date. Record `source_flag` as `"tank"` AND `"estimate"` respectively.
2. `net_oil_volume` = `gross_volume − compressor_recycled − fuel_used`.
3. `average_gor` = mean GOR telemetry for that well AND date.
4. `net_gas_volume` = `net_oil_volume * average_gor`.
5. `sales_meter_volume` = `meter_reading * (well_net_oil / Σ net_oil_at_point)`.
6. `variance_oil` = `net_oil_volume − sales_meter_volume`.

**R04 — Anomaly Detection**
`GET /dashboard/wells/anomalies`: return wells with pressure trend (3 consecutive increases > 10%) AND GOR shift (> 15% change). **Feasibility Constraint:** The GOR shift evaluation MUST compute window means on resampled 1-hour buckets with explicit missing-data handling AND a minimum completeness threshold before comparing adjacent 6-hour windows.

**R05 — Alarm Suppression**
Suppress any `(well_id, alarm_type)` triggered ≥ 20 times in 30 days without acknowledgment. `GET /alarms/active` MUST filter suppressed alarms AND apply RBAC scope.

**R06 — Regulatory Reporting**
`GET /reports/regulatory`: (1) `federal_ghg` — methane AND CO2e from `net_gas_volume` with `calculation_basis` sourced from the allocation `source_flag`. (2) `state_production` — per-well totals. (3) `blm_lease` — totals grouped by `lease_id`.

**R07 — Keyset Pagination Archive**
`GET /archive/telemetry`: The archive MUST preserve source-native resolution including `source_timestamp`, `ingest_timestamp`, AND `source_quality_code`. To support keyset pagination efficiently, you MUST implement TWO indexes: `idx_telemetry_well_channel_ts` on `(well_id, channel, timestamp, id)` AND `idx_telemetry_well_ts` on `(well_id, timestamp, id)`. The `next_cursor` MUST be an opaque Base64-encoded string representing the state of ALL continuation predicates.

**R08 — Multi-Organization RBAC**
Store facility scope in a join table `user_role_facility_scopes(user_role_id, facility_id)`. **Trust Link Constraint:** Resolve user identity AND organization context server-side using a seeded `api_token` mapping; MUST NOT rely on caller-supplied headers for identity. Require authorization checks on EVERY endpoint. Every authorization decision MUST record a specific reason code in `audit_logs`.

---

## Expected Interface

### Models

- **Path:** `src/main/kotlin/model/TelemetryReading.kt`
- **Name:** `TelemetryReading`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `timestamp: String` (ingest time), `sourceTimestamp: String` (event time), `channel: String`, `value: Double`, `sourceQualityCode: String`, `commStatus: String`
- **Output:** N/A (data class)
- **Description:** DTO for telemetry. Preserves native resolution AND provenance.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ProductionAllocation.kt`
- **Name:** `ProductionAllocation`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `date: String`, `grossVolume: Double`, `netOilVolume: Double`, `averageGor: Double`, `netGasVolume: Double`, `salesMeterVolume: Double`, `varianceOil: Double`, `varianceEstimate: Double`
- **Output:** N/A (data class)
- **Description:** Per-well daily production allocation result.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ChannelStatus.kt`
- **Name:** `ChannelStatus`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `channel: String`, `diagnosticSignal: String`, `connectivityStatus: String`, `inferredCause: String?`, `lastSeen: String`
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
- **Input (constructor):** `wellId: Int?`, `facilityId: Int?`, `leaseId: String?`, `volume: Double`, `methane: Double?`, `co2e: Double?`, `calculationBasis: String?`
- **Output:** N/A (data class)
- **Description:** Individual line item in a regulatory report.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ArchivePage.kt`
- **Name:** `ArchivePage`
- **Type:** `@Serializable data class`
- **Input (constructor):** `data: List<TelemetryReading>`, `nextCursor: String?`
- **Output:** N/A (data class)
- **Description:** Paginated response. `nextCursor` is an opaque Base64 string.
- **Decorators:** `@Serializable`

### Exposed ORM Table Definitions

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Wells`
- **Type:** `object : Table("wells")`
- **Description:** Columns: `id`, `name`, `facilityId`, `transport`, `leaseId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Facilities`
- **Type:** `object : Table("facilities")`
- **Description:** Columns: `id`, `name`, `organizationId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TelemetryReadings`
- **Type:** `object : Table("telemetry")`
- **Description:** Columns: `id`, `wellId`, `facilityId`, `timestamp`, `sourceTimestamp`, `channel`, `value`, `sourceQualityCode`. Indexes: `idx_telemetry_well_channel_ts` AND `idx_telemetry_well_ts`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ChannelStatuses`
- **Type:** `object : Table("channel_status")`
- **Description:** Stores health state per R01.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellDeliveryPointAssignments`
- **Type:** `object : Table("well_delivery_point_assignments")`
- **Description:** Maps wells to sales delivery points.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TankGaugeReadings`
- **Type:** `object : Table("tank_gauge_readings")`
- **Description:** Well-level daily tank gauge volume readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellheadEstimates`
- **Type:** `object : Table("wellhead_estimates")`
- **Description:** Well-level daily wellhead estimate volume readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `SalesMeterReadings`
- **Type:** `object : Table("sales_meter_readings")`
- **Description:** Delivery-point-level daily sales meter readings.

- **Path:** `src/main/kotlin/db/Tables.kt"
- **Name:** `CompressorLogs`
- **Type:** `object : Table("compressor_logs")`
- **Description:** Subtracted in R03.

- **Path:** `src/main/kotlin/db/Tables.kt"
- **Name:** `FuelUseLogs`
- **Type:** `object : Table("fuel_use_logs")`
- **Description:** Subtracted in R03.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AlarmsTable`
- **Type:** `object : Table("alarms")`
- **Description:** Alarm records.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `UserOrganizationRoles`
- **Type:** `object : Table("user_organization_roles")`
- **Description:** RBAC role store.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AuditLogs`
- **Type:** `object : Table("audit_logs")`
- **Description:** Immutable append-only audit trail.

### Services

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
- **Name:** `ProductionAllocationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Description:** Service for production allocation logic.

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Description:** Resolves identity AND authorizes access server-side.

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
- **Name:** `ChannelStatusService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Description:** Background telemetry health diagnostics.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
- **Name:** `AnomalyDetectionService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Description:** Service for trend AND shift detection.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Description:** Alarm retrieval AND suppression.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
- **Name:** `RegulatoryReportService`
- **Type:** class
- **Input (constructor):** `db: Database`, `productionAllocationService: ProductionAllocationService`
- **Description:** Report generation service.

### Generator

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator`
- **Type:** `object`
- **Input (method):** `database: Database`
- **Description:** Seeds 72h telemetry AND 30 days of alarms.

### API Endpoints

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getDashboardWellAnomalies`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `orgId: Int?`. Header: `Authorization: String` (api_token).
- **Description:** Anomaly detection endpoint.

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `severity: String?`. Header: `Authorization: String` (api_token).
- **Description:** Active alarms endpoint.

- **Path:** `GET /reports/regulatory`
- **Name:** `getRegulatoryReport`
- **Type:** API Endpoint
- **Input:** Query params: `type: String` (MUST be exactly one of: `"federal_ghg"`, `"state_production"`, `"blm_lease"`), `startDate: String`, `endDate: String`. Header: `Authorization: String` (api_token).
- **Description:** Regulatory reporting endpoint.

- **Path:** `GET /archive/telemetry`
- **Name:** `getArchiveTelemetry`
- **Type:** API Endpoint
- **Input:** Query params: `wellId: Int` (required), `channel: String?`, `cursor: String?`. Header: `Authorization: String` (api_token).
- **Description:** Keyset pagination archive via opaque cursor.

### Application Entry Point

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `Application.module`
- **Type:** Ktor module extension function
- **Description:** Entry point. Binds to `127.0.0.1`.
