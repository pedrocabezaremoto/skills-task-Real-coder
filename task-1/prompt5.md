# SCADA Data Aggregation and Operations Support Service - v5

## Context
A small independent oil and gas operator manages several hundred wells across a basin and a midstream gathering system connected to multiple sales delivery points. You MUST build a Kotlin backend service that ingests field telemetry, reconciles production allocation, manages alarms, generates regulatory reports, and archives raw data. The service MUST run entirely locally using bundled sample data — no external APIs, no live data downloads.

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

**R01 — Telemetry Ingestion & Status**
Implement a telemetry ingestion module. Each reading MUST include: `well_id` (String), `facility_id` (String), `timestamp` (ISO-8601 String), `channel` (Enum: `pressure`, `temperature`, `flow`, `gor`), `value` (Double), `transport` (Enum: `cellular`, `satellite`, `radio`), and `reported_quality_flag` (Enum: `ok`, `flatline`). The backend MUST calculate a heuristic suspicion `computed_quality_flag` independently to flag if the value remains unchanged for exactly 5 consecutive readings (`suspected_flatline`).
To handle gap-detection, the system MUST implement a `channel_inventory` table (keyed by `well_id`, `facility_id`, `channel`, `transport`) tracking `expected_cadence` and `last_seen` timestamp. Implement a scheduled background job that evaluates this inventory and infers signal loss when a stream is overdue by exactly 2 times its expected interval. The system MUST attribute the cause: if multiple wells sharing the same `facility_id` and `transport` drop simultaneously, classify `transport_status` as the respective outage type (`cell_outage`, `satellite_outage`, `radio_outage`); if isolated, classify `sensor_quality` as `suspected_bad_sensor`. Store readings in an append-only `telemetry` table designed to preserve raw history indefinitely.

**R02 — Sample Dataset**
Include a bundled sample dataset generator. It MUST populate the database with: exactly 50 wells mapped to exactly 10 facilities, exactly 3 sales delivery points, exactly 1 gathering system, exactly 10 equipment inventory items, exactly 5 lease assignments (mapping wells to `federal` or `state` jurisdictions), measured `gas_composition` data per facility, and exactly 72 hours of telemetry history. This 72-hour bundled dataset is explicitly a demo fixture, while the schema and append-only retention MUST support indefinite accumulation. To support alarm rules without creating a massive database, the generator MUST explicitly seed the `alarms` table with exactly 30 days of historical triggered and acknowledged alarm records. The telemetry generator MUST produce mixed sampling cadences based on transport: radio MUST use 1-minute intervals, cellular MUST use 15-minute intervals, and satellite MUST use 60-minute intervals. The generator MUST execute automatically on first startup if the database is empty.

**R03 — Per-Well Production Allocation**
Implement a production allocation module. For each well, the system MUST reconcile: metered tank gauge volume, wellhead production estimate, and sales meter reading. The allocation logic MUST subtract `compressor_recycling` volume and `onsite_fuel_use` from gross production to compute `net_volume`. Store results in a `production_allocation` table.

**R04 — Operations Dashboard Endpoint**
Implement a `GET /dashboard/wells/anomalies` endpoint. A well MUST be included in the response if it meets AT LEAST ONE of these conditions:
1. Pressure trend: 3 consecutive increases > 10% per reading.
2. GOR shift: Shift > 15% within a 6-hour window.
The response MUST be a JSON array of objects with fields: `well_id`, `anomaly_type`, `detected_at`, `current_value`, and `baseline_value`.

**R05 — Alarm Management**
Implement an alarm management module. A "chronic alarm" is defined as any alarm triggered 20 or more times in the last 30 days without acknowledgment. The system MUST suppress chronic alarms from the active list. `GET /alarms/active` MUST return only non-suppressed alarms. Store alarms in an `alarms` table.

**R06 — Regulatory Reporting**
Implement a `GET /reports/regulatory` endpoint. The database MUST include `equipment`, `facilities`, `leases`, `well_lease_assignments`, and `gas_composition` tables with provenance fields tying calculated values back to measured records. Supported `type` parameters: `state_production`, `federal_ghg`, `blm_lease`.
- `state_production`: Returns monthly well-level net volumes.
- `federal_ghg`: Returns total methane/CO2 equivalent values. The system MUST compute this using actual measured data from the `gas_composition` table and explicit venting rules tied to specific equipment classes and GOR measured readings.
- `blm_lease`: Returns production totals grouped by `lease_type` (`federal`, `state`) using the `well_lease_assignments` table.

**R07 — Historical Archive**
Implement a `GET /archive/telemetry` endpoint. Parameters: `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601), `limit` (Integer, maximum 1000), `offset` (Integer). It MUST return raw telemetry readings in the specified range exactly as received at their native cadences, sorted by `timestamp` ascending. The endpoint MUST enforce pagination to safely retrieve large historical data.

**R08 — Access Control**
Implement organization-aware access control (RBAC). The system MUST include an `organizations` table, an `audit_logs` table for recording access decisions, and explicit ownership relations. Assets MUST define an `asset_owner_organization_id` and an `operating_organization_id`. Users MUST have a `facility_assignment_scope`. Implement three roles: `operator_of_record` (full access to owned assets), `contract_operator` (read/write limited to assigned `facility_assignment_scope`), and `auditor` (read-only over assigned scope). Authentication MUST use HTTP Basic Auth with BCrypt-hashed passwords stored in the database. The system MUST enforce explicit per-endpoint authorization validation derived from these ownership links. Hardcode exactly one user per role in the sample dataset.

**R09 — Health Check**
Implement a `GET /health` endpoint. Returns HTTP 200 with `{"status": "ok"}` if the service and database are active.

---

## Expected Interface

| Path | Name | Type | Input | Output | Description |
|------|------|------|-------|--------|-------------|
| `GET /dashboard/wells/anomalies` | getWellAnomalies | API Endpoint | None | JSON Array | Returns wells with pressure trends or GOR shifts |
| `GET /alarms/active` | getActiveAlarms | API Endpoint | None | JSON Array | Returns non-suppressed active alarms |
| `GET /reports/regulatory` | getRegulatoryReport | API Endpoint | `type` (String) | JSON Object | Generates regulatory reports from DB |
| `GET /archive/telemetry` | getArchiveTelemetry | API Endpoint | `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601), `limit` (Int), `offset` (Int) | JSON Array | Paginated raw telemetry at native resolution |
| `GET /health` | healthCheck | API Endpoint | None | JSON Object | Service and DB liveness check |

---

## Current State
This is a greenfield project. No existing codebase. The solution MUST compile and run with `./gradlew run`. The Ktor server MUST bind exclusively to `127.0.0.1` (localhost). The system MUST NOT use networking client libraries or raw sockets for outbound connections. All data dependencies MUST be bundled on disk. The sample data generator MUST execute automatically on first run if the SQLite database is empty.
