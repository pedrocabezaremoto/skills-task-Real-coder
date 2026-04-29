# SCADA Data Aggregation and Operations Support Service

## Context
A small independent oil and gas operator manages several hundred wells across a basin and a midstream gathering system connected to multiple sales delivery points. You are a backend engineer hired to build a Kotlin service that ingests field telemetry, reconciles production allocation, manages alarms, generates regulatory reports, and archives raw data. The service must run entirely locally using bundled sample data — no external APIs, no live data downloads.

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

**R01 — Telemetry Ingestion**
Implement a telemetry ingestion module that accepts sensor readings from simulated RTUs and PLCs. Each reading MUST include: `well_id`, `timestamp` (ISO-8601), `channel` (one of: `pressure`, `temperature`, `flow`, `gor`), `value` (Double), `transport` (one of: `cellular`, `satellite`, `radio`), and `quality_flag` (one of: `ok`, `flatline`, `signal_loss`). The system MUST distinguish `flatline` (sensor value unchanged for 5 or more consecutive readings) from `signal_loss` (no reading received for 10 or more minutes on that channel). Store all readings in a `telemetry` table in SQLite.

**R02 — Sample Dataset**
Include a bundled sample dataset generator (`SampleDataGenerator.kt`) that populates the database with: 50 wells, 3 sales delivery points, 1 gathering system, and 72 hours of telemetry at 5-minute intervals. The generator MUST run automatically on first startup if the database is empty.

**R03 — Per-Well Production Allocation**
Implement a production allocation module that, for each well, reconciles: the metered tank gauge volume, the wellhead production estimate, and the sales meter reading at the delivery point. The allocation MUST subtract compressor recycling volume and onsite fuel use from gross production before computing net allocated volume. Store results in a `production_allocation` table with fields: `well_id`, `date`, `gross_volume`, `compressor_recycling`, `fuel_use`, `net_volume`, `sales_meter_volume`, `variance`.

**R04 — Operations Dashboard Endpoint**
Implement a `GET /dashboard/wells/anomalies` endpoint that returns wells with abnormal conditions. A well MUST appear in the response if: its pressure trend shows 3 or more consecutive increases greater than 10% per reading, OR its gas-to-oil ratio shifts more than 15% within a 6-hour window. The response MUST be JSON with fields: `well_id`, `anomaly_type` (one of: `pressure_trend`, `gor_shift`), `detected_at`, `current_value`, `baseline_value`.

**R05 — Alarm Management**
Implement an alarm management module. A chronic alarm is defined as an alarm that has triggered more than 20 times in the last 30 days without operator acknowledgment. Chronic alarms MUST be suppressed from the active alarm list. Genuine alarms (non-chronic) MUST remain visible. Store all alarms in an `alarms` table with fields: `alarm_id`, `well_id`, `channel`, `triggered_at`, `acknowledged`, `suppressed`. Implement a `GET /alarms/active` endpoint that returns only non-suppressed alarms.

**R06 — Regulatory Reporting**
Implement a `GET /reports/regulatory` endpoint that accepts a query parameter `type` with accepted values: `state_production`, `federal_ghg`, `blm_lease`. Each report type MUST generate from the data stored in the database. `state_production` returns monthly well-level net volumes. `federal_ghg` returns total methane and CO2 equivalent values computed from flow and GOR readings. `blm_lease` returns production totals grouped by lease type (`federal`, `state`). All reports MUST be returned as JSON.

**R07 — Historical Archive**
Implement a `GET /archive/telemetry` endpoint that accepts `well_id`, `channel`, `from` (ISO-8601), and `to` (ISO-8601) as query parameters and returns all raw telemetry readings for that well and channel in the specified range at native resolution (every stored reading). The response MUST be a JSON array sorted by `timestamp` ascending.

**R08 — Access Control**
Implement role-based access with two roles: `operator` and `auditor`. The `operator` role MUST have access to all endpoints. The `auditor` role MUST have read-only access and MUST NOT access `POST` or `DELETE` endpoints. Authentication MUST use HTTP Basic Auth. Include two hardcoded users in the sample dataset: `operator_user` (role: `operator`) and `audit_user` (role: `auditor`), both with password `test1234`.

**R09 — Quality Flag API**
Implement a `GET /telemetry/quality` endpoint that accepts `well_id` and `channel` as query parameters and returns the current quality flag, the last valid reading timestamp, and the count of consecutive flagged readings.

**R10 — Health Check**
Implement a `GET /health` endpoint that returns HTTP 200 with body `{"status": "ok"}` when the service is running and the database connection is active.

---

## Expected Interface

| Path | Name | Type | Input | Output | Description |
|------|------|------|-------|--------|-------------|
| `GET /dashboard/wells/anomalies` | getWellAnomalies | HTTP Endpoint | Basic Auth header | JSON array of anomaly objects | Returns wells with abnormal pressure trends or GOR shifts |
| `GET /alarms/active` | getActiveAlarms | HTTP Endpoint | Basic Auth header | JSON array of alarm objects | Returns non-suppressed active alarms |
| `GET /reports/regulatory` | getRegulatoryReport | HTTP Endpoint | Query param `type`: `state_production` \| `federal_ghg` \| `blm_lease` | JSON report object | Generates regulatory report from stored data |
| `GET /archive/telemetry` | getArchiveTelemetry | HTTP Endpoint | Query params: `well_id`, `channel`, `from`, `to` | JSON array of telemetry readings | Returns raw telemetry at native resolution |
| `GET /telemetry/quality` | getTelemetryQuality | HTTP Endpoint | Query params: `well_id`, `channel` | JSON quality status object | Returns current quality flag and consecutive flagged count |
| `GET /health` | healthCheck | HTTP Endpoint | None | `{"status": "ok"}` | Service and DB liveness check |

---

## Current State
This is a greenfield project. No existing codebase. The solution MUST compile and run with `./gradlew run`. The sample data generator MUST execute automatically on first run if the SQLite database is empty.
