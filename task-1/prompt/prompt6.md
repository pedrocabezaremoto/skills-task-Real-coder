# SCADA Data Aggregation and Operations Support Service

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
Implement a telemetry ingestion module. Each reading MUST include: `well_id` (String), `facility_id` (String), `timestamp` (ISO-8601 String), `channel` (Enum: `pressure`, `temperature`, `flow`, `gor`), `value` (Double), `transport` (Enum: `cellular`, `satellite`, `radio`), and `reported_quality_flag` (Enum: `ok`, `flatline`). Store readings in an append-only `telemetry` table designed to preserve raw history indefinitely.

The backend MUST compute a heuristic `suspected_flatline` flag at query time (not stored) by comparing the 5 most recent readings ordered by event-time for the same `well_id` and `channel`. If all 5 values are identical, the flag MUST return `suspected_flatline`; otherwise `ok`. Out-of-order arrivals MUST be handled by always sorting by event-time before applying the rule.

To handle gap-detection, the system MUST implement a `channel_inventory` table with columns: `well_id` (String), `facility_id` (String), `channel` (Enum), `transport` (Enum), `expected_cadence_minutes` (Integer), `last_seen` (ISO-8601). The sample dataset MUST assign exactly one transport per well (all channels of one well share the same transport). Implement a scheduled background job that evaluates overdue streams: a stream is overdue when `current_time - last_seen > 2 * expected_cadence_minutes`. The job MUST record inferred outages in a `telemetry_status` table with `inferred_status` (Enum: `ok`, `suspected_outage`) and `probable_cause` (Enum: `cluster_transport_fault`, `isolated_local_fault`). If 3 or more wells sharing the same `facility_id` and `transport` are simultaneously overdue, classify as `cluster_transport_fault`; otherwise classify as `isolated_local_fault`.

**R02 — Sample Dataset**
Include a bundled sample dataset generator. It MUST populate the database with: exactly 50 wells mapped to exactly 10 facilities (5 wells per facility), exactly 3 sales delivery points, exactly 1 gathering system, exactly 10 equipment inventory items, exactly 5 lease assignments mapping wells to `federal` or `state` jurisdictions, measured `gas_composition` data per facility (methane percentage and GWP factor), equipment runtime data per equipment item, and exactly 72 hours of telemetry history. This 72-hour bundled dataset is explicitly a demo fixture while the schema and append-only retention MUST support indefinite accumulation. To support alarm rules, the generator MUST explicitly seed the `alarms` table with exactly 30 days of historical triggered and acknowledged alarm records. Transport assignment MUST follow this rule: wells 1-20 MUST use `radio` (1-minute intervals), wells 21-40 MUST use `cellular` (15-minute intervals), wells 41-50 MUST use `satellite` (60-minute intervals). Seed exactly 3 organizations, exactly 2 users per role (6 users total), with users distributed across organizations and facilities. The generator MUST execute automatically on first startup if the database is empty.

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
Implement a `GET /reports/regulatory` endpoint. The database MUST include `equipment`, `facilities`, `leases`, `well_lease_assignments`, `gas_composition`, and `equipment_runtime` tables. Supported `type` parameters: `state_production`, `federal_ghg`, `blm_lease`.
- `state_production`: Returns monthly well-level net volumes from `production_allocation`.
- `federal_ghg`: Returns a demonstrative GHG estimate with stated assumptions. The system MUST compute methane volume using the formula: `net_gas_volume * gas_composition.methane_fraction`, then convert to CO2e using `gas_composition.gwp_factor`. Vented volume MUST be estimated as `equipment_runtime.vent_hours * equipment.vent_rate_mcf_per_hour` per equipment item. All output fields MUST include a `calculation_basis` string that documents the assumptions used.
- `blm_lease`: Returns production totals grouped by `lease_type` (`federal`, `state`) using the `well_lease_assignments` table.

**R07 — Historical Archive**
Implement a `GET /archive/telemetry` endpoint. Parameters: `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601), `limit` (Integer, maximum 1000), `offset` (Integer). It MUST return raw telemetry readings in the specified range exactly as received, sorted by event-time ascending. The endpoint MUST enforce pagination.

**R08 — Access Control**
Implement organization-aware access control (RBAC). The system MUST include an `organizations` table, an `audit_logs` table, and explicit ownership relations. Assets MUST define `asset_owner_organization_id` and `operating_organization_id`. Users MUST have a `facility_assignment_scope`. Implement three roles: `operator_of_record` (full access to owned assets), `contract_operator` (read/write limited to assigned `facility_assignment_scope`), and `auditor` (read-only over assigned scope). Authentication MUST use HTTP Basic Auth with BCrypt-hashed passwords stored in the database. The system MUST enforce explicit per-endpoint authorization validation. Seed exactly 2 users per role across 3 organizations with different facility scopes.

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
