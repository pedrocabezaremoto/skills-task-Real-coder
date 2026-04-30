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
Implement an append-only `telemetry` table AND a `channel_status` table. A background coroutine MUST run on startup AND repeat every 60 seconds performing: (1) Flatline check — fetch the last 5 readings per `(well_id, channel)`; if all 5 values are identical, set `signal_condition = "suspected_flatline"`. (2) Outage check — if `current_time - last_seen > 2 * expected_cadence_minutes`, mark `connectivity_condition = "overdue"`; group overdue channels by `(facility_id, transport)`: if count ≥ 3 set `probable_cause = "transport_outage"`, else set `probable_cause = "isolated_local_fault"`.

**R02 — Scale & Sample Data**
The `SampleDataGenerator` MUST insert exactly 200 wells AND 40 facilities (5 wells/facility). Transport cadence bands: wells 1–80 → radio/1 min, 81–160 → cellular/15 min, 161–200 → satellite/60 min. Seed exactly 72 hours of telemetry (pressure, temperature, AND GOR channels), 30 days of alarm history, AND all production log tables. Use a fixed seed for reproducibility.

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
`GET /archive/telemetry`: The archive MUST support append-only long-term retention, no downsampling of raw telemetry, continued ingestion support beyond seeded data, AND storage query behavior sized for historical investigations. To support keyset pagination efficiently, you MUST split the query shapes: for channel-filtered requests use index `(well_id, channel, timestamp, id)` AND base64 cursor `"well_id:channel:timestamp:id"`; for unfiltered requests use a second index `(well_id, timestamp, id)` AND base64 cursor `"well_id:timestamp:id"`. Results ordered timestamp ASC AND id ASC.

**R08 — Multi-Organization RBAC**
Store contract operator facility scope in a normalized join table `user_role_facility_scopes(user_role_id, facility_id)`. **Crucial Security Constraint:** Require authorization checks on EVERY endpoint AND service that returns operational, historical, AND regulatory data. All reads MUST resolve asset ownership server-side AND call `AuthorizationService.authorize` before data access. Every authorization decision MUST record a specific reason code in `audit_logs`.

---

## Expected Interface

### Models

- **Path:** `src/main/kotlin/model/TelemetryReading.kt`
- **Name:** `TelemetryReading`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `channelId: Int`, `timestamp: String` (ISO-8601), `channel: String`, `transport: String`, `value: Double`, `reportedQualityFlag: String`, `commStatus: String`
- **Output:** N/A (data class)
- **Description:** DTO for telemetry ingestion. Serialized field names use snake_case via `@SerialName`.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ProductionAllocation.kt`
- **Name:** `ProductionAllocation`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `date: String` (ISO-8601 date), `grossVolume: Double`, `netOilVolume: Double`, `averageGor: Double`, `netGasVolume: Double`, `salesMeterVolume: Double`, `varianceOil: Double`, `varianceEstimate: Double`
- **Output:** N/A (data class)
- **Description:** Per-well daily production allocation result. `varianceEstimate` is nullable.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/ChannelStatus.kt`
- **Name:** `ChannelStatus`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `channel: String`, `transport: String`, `signalCondition: String`, `connectivityCondition: String`, `probableCause: String?`, `expectedCadenceMinutes: Int`, `lastSeen: String` (ISO-8601)
- **Output:** N/A (data class)
- **Description:** DTO representing the health state of a telemetry channel.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/WellAnomaly.kt`
- **Name:** `WellAnomaly`
- **Type:** `@Serializable data class`
- **Input (constructor):** `wellId: Int`, `facilityId: Int`, `anomalyType: String`, `details: String`, `detectedAt: String` (ISO-8601)
- **Output:** N/A (data class)
- **Description:** DTO for anomaly detection results.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/Alarm.kt`
- **Name:** `Alarm`
- **Type:** `@Serializable data class`
- **Input (constructor):** `id: Long`, `wellId: Int`, `facilityId: Int`, `alarmType: String`, `severity: String`, `message: String`, `triggeredAt: String` (ISO-8601), `acknowledged: Boolean`, `suppressed: Boolean`
- **Output:** N/A (data class)
- **Description:** DTO for alarm records.
- **Decorators:** `@Serializable`

- **Path:** `src/main/kotlin/model/RegulatoryReport.kt`
- **Name:** `RegulatoryReport`
- **Type:** `@Serializable data class`
- **Input (constructor):** `reportType: String`, `generatedAt: String` (ISO-8601), `entries: List<RegulatoryReportEntry>`
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
- **Description:** Paginated response for the archive endpoint. `nextCursor` is a Base64-encoded composite key.
- **Decorators:** `@Serializable`

### Exposed ORM Table Definitions

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Wells`
- **Type:** `object : Table("wells")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Base well registry. Columns include `id`, `name`, `facilityId`, `transport`, AND `leaseId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `Facilities`
- **Type:** `object : Table("facilities")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Facility registry. Columns include `id`, `name`, AND `organizationId`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TelemetryReadings`
- **Type:** `object : Table("telemetry")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Append-only telemetry storage. Indexes MUST support the pagination requirements defined in R07.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `ChannelStatuses`
- **Type:** `object : Table("channel_status")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Channel health state.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellDeliveryPointAssignments`
- **Type:** `object : Table("well_delivery_point_assignments")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Maps wells to sales delivery points.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `TankGaugeReadings`
- **Type:** `object : Table("tank_gauge_readings")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Well-level daily tank gauge volume readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `WellheadEstimates`
- **Type:** `object : Table("wellhead_estimates")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Well-level daily wellhead estimate volume readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `SalesMeterReadings`
- **Type:** `object : Table("sales_meter_readings")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Delivery-point-level daily sales meter readings.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `CompressorLogs`
- **Type:** `object : Table("compressor_logs")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Well-level daily compressor recycled volume.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `FuelUseLogs`
- **Type:** `object : Table("fuel_use_logs")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Well-level daily fuel usage volume.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AlarmsTable`
- **Type:** `object : Table("alarms")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Alarm records.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `UserOrganizationRoles`
- **Type:** `object : Table("user_organization_roles")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** RBAC role store. Columns include `id`, `userId`, `organizationId`, AND `role`.

- **Path:** `src/main/kotlin/db/Tables.kt`
- **Name:** `AuditLogs`
- **Type:** `object : Table("audit_logs")`
- **Input:** N/A (table definition)
- **Output:** N/A (table definition)
- **Description:** Immutable append-only audit trail.

### Services

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
- **Name:** `ProductionAllocationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A (class definition)
- **Description:** Service responsible for computing daily per-well production allocation.

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
- **Name:** `ProductionAllocationService.allocate`
- **Type:** method
- **Input:** `wellId: Int`, `date: LocalDate`
- **Output:** `ProductionAllocation`
- **Description:** Computes daily production allocation for a single well.

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A (class definition)
- **Description:** Service responsible for multi-organization RBAC.

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService.authorize`
- **Type:** method
- **Input:** `userId: Int`, `assetOwnerOrgId: Int`, `facilityId: Int`, `operation: String`
- **Output:** `Boolean`
- **Description:** Validates RBAC rules AND writes audit logs.

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
- **Name:** `ChannelStatusService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A (class definition)
- **Description:** Service responsible for evaluating telemetry channel health.

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
- **Name:** `ChannelStatusService.evaluate`
- **Type:** method
- **Input:** `currentTime: Instant`
- **Output:** `List<ChannelStatus>`
- **Description:** Background evaluation of channels.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
- **Name:** `AnomalyDetectionService`
- **Type:** class
- **Input (constructor):** `db: Database`
- **Output:** N/A (class definition)
- **Description:** Service responsible for detecting pressure trend AND GOR shift anomalies.

- **Path:** `src/main/kotlin/service/AnomalyDetectionService.kt`
- **Name:** `AnomalyDetectionService.detectAnomalies`
- **Type:** method
- **Input:** `facilityId: Int?`, `orgId: Int?`
- **Output:** `List<WellAnomaly>`
- **Description:** Scans recent telemetry for anomalies.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService`
- **Type:** class
- **Input (constructor):** `db: Database`, `authorizationService: AuthorizationService`
- **Output:** N/A (class definition)
- **Description:** Service responsible for alarm retrieval AND suppression logic.

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService.getActiveAlarms`
- **Type:** method
- **Input:** `userId: Int`, `orgId: Int`, `facilityId: Int?`, `severity: String?`
- **Output:** `List<Alarm>`
- **Description:** Returns active non-suppressed alarms.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
- **Name:** `RegulatoryReportService`
- **Type:** class
- **Input (constructor):** `db: Database`, `productionAllocationService: ProductionAllocationService`
- **Output:** N/A (class definition)
- **Description:** Service responsible for generating regulatory reports.

- **Path:** `src/main/kotlin/service/RegulatoryReportService.kt`
- **Name:** `RegulatoryReportService.generateReport`
- **Type:** method
- **Input:** `reportType: String`, `startDate: LocalDate`, `endDate: LocalDate`, `orgId: Int`
- **Output:** `RegulatoryReport`
- **Description:** Implements reporting logic.

### Generator

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator`
- **Type:** `object`
- **Input:** N/A
- **Output:** N/A (object definition)
- **Description:** Deterministic seed data generator.

- **Path:** `src/main/kotlin/generator/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator.generate`
- **Type:** method
- **Input:** `database: Database`
- **Output:** `Unit`
- **Description:** Deterministic seed data generator logic.

### API Endpoints

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getDashboardWellAnomalies`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `orgId: Int?`. Header: `X-User-Id: Int`.
- **Output:** `200 OK` → `List<WellAnomaly>`
- **Description:** Anomaly detection endpoint. MUST enforce RBAC.

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** Query params: `facilityId: Int?`, `severity: String?`. Headers: `X-User-Id: Int`, `X-Org-Id: Int`.
- **Output:** `200 OK` → `List<Alarm>`
- **Description:** Active alarms endpoint. MUST enforce RBAC.

- **Path:** `GET /reports/regulatory`
- **Name:** `getRegulatoryReport`
- **Type:** API Endpoint
- **Input:** Query params: `type: String` (MUST be exactly one of: `"federal_ghg"`, `"state_production"`, `"blm_lease"`), `startDate: String`, `endDate: String`, `orgId: Int`. Header: `X-User-Id: Int`.
- **Output:** `200 OK` → `RegulatoryReport`
- **Description:** Regulatory reporting endpoint. MUST enforce RBAC.

- **Path:** `GET /archive/telemetry`
- **Name:** `getArchiveTelemetry`
- **Type:** API Endpoint
- **Input:** Query params: `wellId: Int` (required), `channel: String?`, `cursor: String?`.
- **Output:** `200 OK` → `ArchivePage`
- **Description:** Keyset pagination archive. MUST enforce RBAC.

### Application Entry Point

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `Application.module`
- **Type:** Ktor module extension function
- **Input:** None
- **Output:** `Unit`
- **Description:** Ktor application entry point.
