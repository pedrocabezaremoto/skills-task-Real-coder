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

| Path | Name | Type | Input | Output | Description |
|------|------|------|-------|--------|-------------|
| `GET /dashboard/wells/anomalies` | getWellAnomalies | API Endpoint | Auth header | JSON Array | Returns wells with pressure/GOR anomalies |
| `GET /alarms/active` | getActiveAlarms | API Endpoint | Auth header | JSON Array | Returns non-suppressed active alarms |
| `GET /reports/regulatory` | getRegulatoryReport | API Endpoint | `type` (String), Auth header | JSON Object | Generates regulatory reports from measured DB data |
| `GET /archive/telemetry` | getArchiveTelemetry | API Endpoint | `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601), `limit` (Int), `after_id` (Long) | JSON Object with `data` array and `next_cursor` | Keyset-paginated raw telemetry at native resolution |
| `GET /health` | healthCheck | API Endpoint | None | JSON Object | Service and DB liveness check |

---

## Current State
This is a greenfield project. No existing codebase. The solution MUST compile and run with `./gradlew run`. The Ktor server MUST bind exclusively to `127.0.0.1` (localhost). The system MUST NOT use networking client libraries or raw sockets for outbound connections. All data dependencies MUST be bundled on disk. The sample data generator MUST execute automatically on first run if the SQLite database is empty.
