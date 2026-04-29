# SCADA Data Aggregation and Operations Support Service - v2

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
Implement a telemetry ingestion module. Each reading MUST include: `well_id` (String), `timestamp` (ISO-8601 String), `channel` (Enum: `pressure`, `temperature`, `flow`, `gor`), `value` (Double), `transport` (Enum: `cellular`, `satellite`, `radio`), and `quality_flag` (Enum: `ok`, `flatline`). The system MUST distinguish `flatline` (value unchanged for 5+ consecutive readings). 
Additionally, implement a gap-detection job or query model that infers `signal_loss` when no reading is received for 10+ minutes. The system MUST attribute the cause: if multiple wells sharing the same transport/facility drop simultaneously, classify as `comms_outage` (e.g., cell tower drop); if isolated, classify as `sensor_failure`. Store readings in a `telemetry` table and availability events in a `telemetry_status` table.

**R02 — Sample Dataset**
Include a bundled sample dataset generator. It MUST populate the database with: 50 wells, 3 sales delivery points, 1 gathering system, equipment inventory, lease assignments, and at least 30 days of telemetry history (to support alarm rules). The generator MUST produce mixed sampling cadences based on transport (e.g., radio at 1-minute intervals, cellular at 15-minute intervals) to simulate native resolution. The generator MUST execute automatically on first startup if the database is empty.

**R03 — Per-Well Production Allocation**
Implement a production allocation module. For each well, the system MUST reconcile: metered tank gauge volume, wellhead production estimate, and sales meter reading. The allocation logic MUST subtract `compressor_recycling` volume and `onsite_fuel_use` from gross production to compute `net_volume`. Store results in a `production_allocation` table.

**R04 — Operations Dashboard Endpoint**
Implement a `GET /dashboard/wells/anomalies` endpoint. A well MUST be included in the response if it meets AT LEAST ONE of these conditions:
1. Pressure trend: 3+ consecutive increases > 10% per reading.
2. GOR shift: Shift > 15% within a 6-hour window.
The response MUST be a JSON array of objects with fields: `well_id`, `anomaly_type`, `detected_at`, `current_value`, and `baseline_value`.

**R05 — Alarm Management**
Implement an alarm management module. A "chronic alarm" is defined as any alarm triggered > 20 times in the last 30 days without acknowledgment. The system MUST suppress chronic alarms from the active list. `GET /alarms/active` MUST return only non-suppressed alarms. Store alarms in an `alarms` table.

**R06 — Regulatory Reporting**
Implement a `GET /reports/regulatory` endpoint. The database MUST include `equipment`, `facilities`, and `leases` tables with provenance fields tying calculated values back to measured records. Supported `type` parameters: `state_production`, `federal_ghg`, `blm_lease`.
- `state_production`: Returns monthly well-level net volumes.
- `federal_ghg`: Returns total methane/CO2 equivalent values computed from specific equipment inventory and GOR measured readings.
- `blm_lease`: Returns production totals grouped by `lease_type` (`federal`, `state`).

**R07 — Historical Archive**
Implement a `GET /archive/telemetry` endpoint. Parameters: `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601). It MUST return all raw telemetry readings in the specified range exactly as received at their native mixed cadences, sorted by `timestamp` ascending.

**R08 — Access Control**
Implement organization-aware access control (RBAC). The system MUST include an `organizations` table. Users and wells MUST be linked to an organization. Implement three roles to reflect industry realities: `operator_of_record` (full access to owned assets), `contract_operator` (read/write limited to assigned facilities), and `auditor` (read-only over assigned scope). Authentication MUST use HTTP Basic Auth. Hardcode at least one user per role in the sample dataset.

**R09 — Health Check**
Implement a `GET /health` endpoint. Returns HTTP 200 with `{"status": "ok"}` if the service and database are active.

---

## Expected Interface

| Path | Name | Type | Input | Output | Description |
|------|------|------|-------|--------|-------------|
| `GET /dashboard/wells/anomalies` | getWellAnomalies | API Endpoint | None | JSON Array | Returns wells with pressure trends or GOR shifts |
| `GET /alarms/active` | getActiveAlarms | API Endpoint | None | JSON Array | Returns non-suppressed active alarms |
| `GET /reports/regulatory` | getRegulatoryReport | API Endpoint | `type` (String) | JSON Object | Generates regulatory reports from DB |
| `GET /archive/telemetry` | getArchiveTelemetry | API Endpoint | `well_id` (String), `channel` (String), `from` (ISO-8601), `to` (ISO-8601) | JSON Array | Returns raw telemetry at native resolution |
| `GET /health` | healthCheck | API Endpoint | None | JSON Object | Service and DB liveness check |

---

## Current State
This is a greenfield project. No existing codebase. The solution MUST compile and run with `./gradlew run`. The sample data generator MUST execute automatically on first run if the SQLite database is empty.
