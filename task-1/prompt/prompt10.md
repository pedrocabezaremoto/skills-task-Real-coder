# SCADA Data Aggregation and Operations Support Service

## Context
A small independent oil and gas operator manages several hundred wells across a basin and a midstream gathering system connected to multiple sales delivery points. You are a senior backend engineer hired to build a Kotlin backend service that ingests field telemetry, reconciles production allocation, manages alarms, generates regulatory reports, and archives raw data. The service MUST run entirely locally using bundled sample data — no external APIs, no live data downloads.

## Tech Stack
- **Language:** Kotlin 1.9
- **Framework:** Ktor 2.3
- **Database:** SQLite via Exposed ORM 0.44
- **Build Tool:** Gradle 8.5 (Kotlin DSL)
- **Runtime:** JVM 17
- **Serialization:** kotlinx.serialization 1.6
- **Testing:** JUnit 5

---

## Requirements

**R01 — Telemetry Ingestion & Channel Status**
Implement a telemetry ingestion module. Each reading MUST include: `well_id` (String), `facility_id` (String), `channel_id` (String, unique per well+channel+transport combination), `timestamp` (ISO-8601 String), `channel` (Enum: `pressure`, `temperature`, `flow`, `gor`), `transport` (Enum: `cellular`, `satellite`, `radio`), `value` (Double), `reported_quality_flag` (Enum: `ok`, `flatline`), and `comm_status` (Enum: `ok`, `timeout`, `poll_error`). Store readings in an append-only `telemetry` table.

The backend MUST maintain a `channel_status` table (keyed by `channel_id`) with the following columns: `signal_condition` (Enum: `ok`, `suspected_flatline`), `connectivity_condition` (Enum: `ok`, `suspected_outage`), `probable_cause` (Enum: `none`, `transport_outage`, `isolated_local_fault`), `expected_cadence_minutes` (Integer), and `last_seen` (ISO-8601 String). This table MUST be updated by a single scheduled background job that runs using server UTC clock and performs both evaluations in sequence on every execution:
1. Flatline check: query the 5 most recent event-time-ordered readings for each `channel_id`. If all 5 values are identical, set `signal_condition = suspected_flatline`; otherwise set `signal_condition = ok`.
2. Outage check: a channel is overdue when `current_utc_time - last_seen > 2 * expected_cadence_minutes`. If 3 or more channels sharing the same `facility_id` and `transport` are simultaneously overdue, set their `connectivity_condition = suspected_outage` and `probable_cause = transport_outage`; otherwise set `connectivity_condition = suspected_outage` and `probable_cause = isolated_local_fault`. `last_seen` MUST be updated to the event-time of every ingested reading.

**R02 — Sample Dataset**
Include a bundled sample dataset generator. This 72-hour dataset is a demo fixture; the schema and append-only retention MUST support indefinite accumulation. The generator MUST populate:
- Exactly 50 wells mapped to exactly 10 facilities (5 wells per facility).
- Each well+channel combination MUST have its own `channel_id` entry in `channel_status`. Each well MUST have one primary transport for all its channels: wells 1–20 use `radio` (expected_cadence = 1 min), wells 21–40 use `cellular` (expected_cadence = 15 min), wells 41–50 use `satellite` (expected_cadence = 60 min).
- Exactly 3 sales delivery points, exactly 1 gathering system.
- Exactly 10 equipment inventory items each with a `vent_rate_mcf_per_hour` (Double) field.
- Lease assignments for all 50 wells: wells 1–25 assigned `lease_type = federal`, wells 26–50 assigned `lease_type = state`.
- Per-facility `gas_composition` records with `methane_fraction` (Double) and `gwp_factor` (Double).
- Per-equipment `equipment_runtime` records with `vent_hours` (Double) and `runtime_hours` (Double).
- Exactly 72 hours of telemetry history.
- Exactly 30 days of seeded alarm history in the `alarms` table to support chronic alarm rules.
- Exactly 3 organizations. The seed MUST assign exactly 6 users total: 2 per role. Each user MUST be assigned a role scoped to exactly one organization via the `user_organization_roles` table. The seed MUST assign user_id=1 to organization_id=1 with role `operator_of_record`, and user_id=2 to organization_id=1 AND organization_id=2 with role `contract_operator` in each, demonstrating multi-organization membership.
- The generator MUST execute automatically on first startup if the database is empty.

**R03 — Per-Well Production Allocation**
Implement a production allocation module. For each well, the system MUST reconcile: metered tank gauge volume, wellhead production estimate, and sales meter reading. The allocation MUST subtract `compressor_recycling` volume and `onsite_fuel_use` from gross production. The `production_allocation` table MUST store: `well_id`, `date`, `gross_volume`, `compressor_recycling`, `fuel_use`, `net_oil_volume` (Double), `net_gas_volume` (Double), `sales_meter_volume`, and `variance`.

**R04 — Operations Dashboard Endpoint**
Implement a `GET /dashboard/wells/anomalies` endpoint. A well MUST be included in the response if it meets AT LEAST ONE of these conditions:
1. Pressure trend: 3 consecutive increases > 10% per reading.
2. GOR shift: Shift > 15% within a 6-hour window.
Response MUST be a JSON array with fields: `well_id`, `anomaly_type`, `detected_at`, `current_value`, `baseline_value`.

**R05 — Alarm Management**
Implement an alarm management module. A "chronic alarm" is defined as any alarm triggered 20 or more times in the last 30 days without acknowledgment. The system MUST suppress chronic alarms from the active list. `GET /alarms/active` MUST return only non-suppressed alarms. Store alarms in an `alarms` table with fields: `alarm_id`, `well_id`, `channel`, `triggered_at`, `acknowledged` (Boolean), `suppressed` (Boolean).

**R06 — Regulatory Reporting**
Implement a `GET /reports/regulatory` endpoint. The database MUST include `equipment`, `facilities`, `leases`, `well_lease_assignments`, `gas_composition`, and `equipment_runtime` tables. Supported `type` parameters:
- `state_production`: Returns monthly well-level net volumes from `production_allocation.net_oil_volume`.
- `federal_ghg`: Methane volume MUST be computed as: `net_gas_volume * gas_composition.methane_fraction`. CO2e MUST be computed as: `methane_volume * gas_composition.gwp_factor`. Vented volume MUST be computed as: `equipment_runtime.vent_hours * equipment.vent_rate_mcf_per_hour`. Every response object MUST include a `calculation_basis` field (String) with value: `"Demo estimate derived from measured production and seeded equipment data"`.
- `blm_lease`: Returns production totals grouped by `lease_type` (`federal`, `state`) using `well_lease_assignments`.

**R07 — Historical Archive**
Implement a `GET /archive/telemetry` endpoint with keyset pagination. Parameters: `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601), `limit` (Integer, maximum 1000), `after_id` (Long, cursor for keyset pagination). The `telemetry` table MUST have a composite index on `(well_id, channel, timestamp)`. The endpoint MUST return results ordered by `(timestamp ASC, id ASC)` and include a `next_cursor` field in the response.

**R08 — Access Control**
Implement organization-scoped RBAC. The system MUST include:
- `organizations` table.
- `user_organization_roles` table with columns: `user_id` (Long), `organization_id` (Long), `role` (Enum: `operator_of_record`, `contract_operator`, `auditor`). This table is the single source of role assignment. One user MUST be assigned to multiple organizations in the seed data.
- `assets` table linked to `asset_owner_organization_id` and `operating_organization_id`.
- `users` table with `facility_assignment_scope` (comma-separated list of `facility_id` values).
- `audit_logs` table recording every access decision.
- Authorization policy: permissions are evaluated per request using the `user_organization_roles` entry that matches `(authenticated_user_id, asset_owner_organization_id)`. `operator_of_record` MUST have full access to assets where `asset_owner_organization_id` matches. `contract_operator` MUST have read/write access only to facilities in their `facility_assignment_scope`. `auditor` MUST have read-only access over their assigned scope.
- Authentication MUST use HTTP Basic Auth with BCrypt-hashed passwords.
- The system MUST enforce per-endpoint authorization using the ownership/assignment rules above.

**R09 — Health Check**
Implement a `GET /health` endpoint that returns HTTP 200 with `{"status": "ok"}` when service and database are active.

---

## Expected Interface

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `Application.module`
- **Type:** function (Ktor application module)
- **Input:** None (receiver: `Application`)
- **Output:** `Unit`
- **Description:** Ktor application entry point invoked by `./gradlew run`. Configures `ContentNegotiation` (kotlinx.serialization JSON), `Authentication` (HTTP Basic with BCrypt), database initialization (SQLite via Exposed), conditional seed-data generation (delegates to `SampleDataGenerator.generate` if DB is empty), the channel-status background scheduled job, and all route installations. Server MUST bind to `127.0.0.1`.

---

- **Path:** `src/main/kotlin/service/TelemetryService.kt`
- **Name:** `TelemetryService.ingest`
- **Type:** method
- **Input:** `reading: TelemetryReading` — `@Serializable data class` with fields: `well_id` (String), `facility_id` (String), `channel_id` (String), `timestamp` (String, ISO-8601), `channel` (ChannelType enum: `pressure`, `temperature`, `flow`, `gor`), `transport` (TransportType enum: `cellular`, `satellite`, `radio`), `value` (Double), `reported_quality_flag` (QualityFlag enum: `ok`, `flatline`), `comm_status` (CommStatus enum: `ok`, `timeout`, `poll_error`)
- **Output:** `Unit`
- **Description:** Inserts a single telemetry reading into the append-only `telemetry` table. Updates `channel_status.last_seen` for the matching `channel_id` to the reading's event `timestamp`. Throws `IllegalArgumentException` if the `channel_id` is unknown.

---

- **Path:** `src/main/kotlin/service/ChannelStatusService.kt`
- **Name:** `ChannelStatusService.evaluate`
- **Type:** method
- **Input:** `currentUtcTime: java.time.Instant`
- **Output:** `Unit`
- **Description:** Executes both channel-status evaluations in sequence on every invocation. (1) Flatline check: for each `channel_id`, queries the 5 most recent event-time-ordered readings; if all 5 `value` fields are identical, sets `signal_condition = suspected_flatline`, otherwise `signal_condition = ok`. (2) Outage check: a channel is overdue when `currentUtcTime − last_seen > 2 × expected_cadence_minutes`. If ≥3 channels sharing the same `facility_id` AND `transport` are simultaneously overdue, sets their `connectivity_condition = suspected_outage` and `probable_cause = transport_outage`; otherwise sets `connectivity_condition = suspected_outage` and `probable_cause = isolated_local_fault`. Channels that are not overdue have `connectivity_condition = ok` and `probable_cause = none`.

---

- **Path:** `src/main/kotlin/service/SampleDataGenerator.kt`
- **Name:** `SampleDataGenerator.generate`
- **Type:** method
- **Input:** None
- **Output:** `Unit`
- **Description:** Populates the entire SQLite database with deterministic sample data. MUST create: exactly 50 wells mapped to exactly 10 facilities (5 per facility); a `channel_status` entry per well+channel combination with transport-based cadence (wells 1–20 radio/1 min, 21–40 cellular/15 min, 41–50 satellite/60 min); exactly 3 sales delivery points; exactly 1 gathering system; exactly 10 equipment inventory items each with `vent_rate_mcf_per_hour`; lease assignments (wells 1–25 federal, 26–50 state); per-facility `gas_composition` records (`methane_fraction`, `gwp_factor`); per-equipment `equipment_runtime` records (`vent_hours`, `runtime_hours`); 72 hours of telemetry history; 30 days of seeded alarm history; exactly 3 organizations; exactly 6 users (2 per role); `user_organization_roles` entries including user_id=1→org 1 as operator_of_record and user_id=2→org 1 & org 2 as contract_operator. Executes automatically on first startup only when the database is empty.

---

- **Path:** `src/main/kotlin/service/ProductionAllocationService.kt`
- **Name:** `ProductionAllocationService.allocate`
- **Type:** method
- **Input:** `wellId: String`, `date: String` (ISO-8601 date, e.g. `"2024-01-15"`)
- **Output:** `ProductionAllocation` — `@Serializable data class` with fields: `well_id` (String), `date` (String), `gross_volume` (Double), `compressor_recycling` (Double), `fuel_use` (Double), `net_oil_volume` (Double), `net_gas_volume` (Double), `sales_meter_volume` (Double), `variance` (Double)
- **Description:** Computes production allocation for a single well on a given date. Reconciles metered tank gauge volume, wellhead production estimate, and sales meter reading. Subtracts `compressor_recycling` and `onsite_fuel_use` from gross production to derive net volumes. Stores the result in the `production_allocation` table and returns the record. `variance` = `net_oil_volume + net_gas_volume − sales_meter_volume`.

---

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService.suppressChronicAlarms`
- **Type:** method
- **Input:** None
- **Output:** `Int` (count of alarms suppressed)
- **Description:** Scans the `alarms` table for chronic alarms: any `(well_id, channel)` combination triggered ≥20 times in the last 30 days where `acknowledged = false`. Sets `suppressed = true` on all matching alarm rows. Returns the number of rows updated.

---

- **Path:** `src/main/kotlin/service/AlarmService.kt`
- **Name:** `AlarmService.getActiveAlarms`
- **Type:** method
- **Input:** `userId: Long`
- **Output:** `List<Alarm>` — each element: `alarm_id` (Long), `well_id` (String), `channel` (String), `triggered_at` (String, ISO-8601), `acknowledged` (Boolean), `suppressed` (Boolean, always `false` in returned list)
- **Description:** Returns all alarms where `suppressed = false` within the authenticated user's authorized asset scope (determined via `AuthorizationService.getAuthorizedFacilityIds`). Chronic suppression MUST have been applied before this query.

---

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService.authorize`
- **Type:** method
- **Input:** `userId: Long`, `assetOwnerOrgId: Long`, `facilityId: String?` (nullable; `null` for organization-level checks where facility context is not applicable; non-null when authorizing access to a specific facility resource), `operation: String` (MUST be exactly `"read"` or `"write"`)
- **Output:** `Boolean`
- **Description:** Evaluates authorization for the request. Looks up the user's role in `user_organization_roles` matching `(userId, assetOwnerOrgId)`. `operator_of_record`: full access (read+write) to all assets where `asset_owner_organization_id` matches; `facilityId` is not checked. `contract_operator`: read+write access; if `facilityId` is non-null, returns `true` only when `facilityId` is present in the user's `facility_assignment_scope`. `auditor`: read-only access; returns `true` only when `operation` is `"read"` and, if `facilityId` is non-null, the `facilityId` is present in the user's `facility_assignment_scope`. Returns `false` and logs denial if no matching role entry exists or if scope/operation checks fail. Every decision (allow or deny) MUST be recorded in the `audit_logs` table.

---

- **Path:** `src/main/kotlin/service/AuthorizationService.kt`
- **Name:** `AuthorizationService.getAuthorizedFacilityIds`
- **Type:** method
- **Input:** `userId: Long`
- **Output:** `List<String>` — deduplicated list of `facility_id` values the user is authorized to access
- **Description:** Aggregates the authenticated user's authorized facility scope across all their `user_organization_roles` entries. For each role entry: if the role is `operator_of_record`, includes all `facility_id` values from the `assets` table where `asset_owner_organization_id` matches the entry's `organization_id`; if the role is `contract_operator` or `auditor`, includes the `facility_id` values parsed from the user's `facility_assignment_scope` (comma-separated). Returns the deduplicated union of all collected facility IDs. Used by query-scoped endpoints and service methods (e.g., `AlarmService.getActiveAlarms`, dashboard anomalies, regulatory reports, archive telemetry) to filter results to only the user's authorized data.

---

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getWellAnomalies`
- **Type:** API Endpoint
- **Input:** `Authorization` header (HTTP Basic Auth: `Basic base64(username:password)`)
- **Output:** HTTP 200 with JSON Array of objects, each containing: `well_id` (String), `anomaly_type` (String, one of `"pressure_trend"` or `"gor_shift"`), `detected_at` (String, ISO-8601), `current_value` (Double), `baseline_value` (Double)
- **Description:** Returns all wells with at least one active anomaly, scoped to the authenticated user's authorized assets. A well is included if it meets at least one condition: (1) Pressure trend — 3 consecutive pressure readings each >10% higher than the previous reading; `current_value` is the latest reading, `baseline_value` is the first of the three. (2) GOR shift — GOR value shifted >15% within any 6-hour window; `current_value` is the latest GOR, `baseline_value` is the GOR at the start of the window. Returns HTTP 401 if credentials are invalid, HTTP 403 if unauthorized.

---

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** `Authorization` header (HTTP Basic Auth: `Basic base64(username:password)`)
- **Output:** HTTP 200 with JSON Array of objects, each containing: `alarm_id` (Long), `well_id` (String), `channel` (String), `triggered_at` (String, ISO-8601), `acknowledged` (Boolean), `suppressed` (Boolean, always `false`)
- **Description:** Returns all active, non-suppressed alarms scoped to the authenticated user's authorized assets. Chronic alarms (same `well_id`+`channel` triggered ≥20 times in the last 30 days without acknowledgment) MUST be suppressed and excluded from the response. Returns HTTP 401 if credentials are invalid, HTTP 403 if unauthorized.

---

- **Path:** `GET /reports/regulatory`
- **Name:** `getRegulatoryReport`
- **Type:** API Endpoint
- **Input:** Query parameter `type` (String, required, one of: `"state_production"`, `"federal_ghg"`, `"blm_lease"`), `Authorization` header (HTTP Basic Auth)
- **Output:** HTTP 200 with JSON Object. Structure varies by `type`: (1) `state_production` — `{ "report_type": "state_production", "records": [{ "well_id": String, "month": String, "net_oil_volume": Double }] }`. (2) `federal_ghg` — `{ "report_type": "federal_ghg", "calculation_basis": "Demo estimate derived from measured production and seeded equipment data", "records": [{ "facility_id": String, "methane_volume": Double, "co2e": Double, "vented_volume": Double }] }` where `methane_volume = net_gas_volume × gas_composition.methane_fraction`, `co2e = methane_volume × gas_composition.gwp_factor`, `vented_volume = equipment_runtime.vent_hours × equipment.vent_rate_mcf_per_hour`. (3) `blm_lease` — `{ "report_type": "blm_lease", "records": [{ "lease_type": String, "total_oil_volume": Double, "total_gas_volume": Double }] }` grouped by `lease_type` (`federal`, `state`) via `well_lease_assignments`.
- **Description:** Generates regulatory reports using data from `production_allocation`, `gas_composition`, `equipment`, `equipment_runtime`, `leases`, and `well_lease_assignments` tables. Returns HTTP 400 if `type` is missing or invalid. Returns HTTP 401/403 for auth failures. Scoped to authenticated user's authorized assets.

---

- **Path:** `GET /archive/telemetry`
- **Name:** `getArchiveTelemetry`
- **Type:** API Endpoint
- **Input:** Query parameters: `well_id` (String, required), `channel` (String, required), `from` (String, ISO-8601, required), `to` (String, ISO-8601, required), `limit` (Int, optional, default 100, maximum 1000), `after_id` (Long, optional, keyset pagination cursor); `Authorization` header (HTTP Basic Auth)
- **Output:** HTTP 200 with JSON Object: `{ "data": [{ "id": Long, "well_id": String, "channel": String, "timestamp": String, "value": Double, "reported_quality_flag": String, "comm_status": String }], "next_cursor": Long | null }`. Results ordered by `(timestamp ASC, id ASC)`. `next_cursor` is the `id` of the last returned row, or `null` if no more results.
- **Description:** Returns raw telemetry readings for the specified well and channel within the `[from, to]` time range using keyset pagination. The `telemetry` table MUST have a composite index on `(well_id, channel, timestamp)`. If `after_id` is provided, only rows with `(timestamp, id)` greater than the cursor row are returned. Returns HTTP 400 if required params are missing. Returns HTTP 401/403 for auth failures.

---

- **Path:** `GET /health`
- **Name:** `healthCheck`
- **Type:** API Endpoint
- **Input:** None
- **Output:** HTTP 200 with JSON Object: `{ "status": "ok" }`
- **Description:** Returns HTTP 200 with body `{"status": "ok"}` when the Ktor service is running and the SQLite database connection is responsive. No authentication required.

---

## Current State
This is a greenfield project. No existing codebase. The solution MUST compile and run with `./gradlew run`. The Ktor server MUST bind exclusively to `127.0.0.1` (localhost). The system MUST NOT use networking client libraries or raw sockets for outbound connections. All data dependencies MUST be bundled on disk. The sample data generator MUST execute automatically on first run if the SQLite database is empty.
