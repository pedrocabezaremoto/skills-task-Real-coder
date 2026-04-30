# SCADA Backend Operations Service

## Context

Build a Kotlin backend service that operates as a SCADA data aggregation and operations support system for a small independent oil and gas operator. The operator manages a few hundred wells across a basin and a midstream gathering system connected to sales delivery points. 

**Strict Local/Egress Constraint:** The service MUST run entirely locally on `127.0.0.1`. You MUST NOT use any external APIs or download live data. Any sample dataset used must be generated locally or bundled in the codebase. Explicitly forbid outbound network calls (no `java.net`, no OkHttp, no external JDBC).

## Tech Stack
- **Language:** Kotlin
- **Framework:** Ktor
- **Database:** SQLite (bundled locally)

## Requirements

1. **Telemetry Ingestion:** Ingest telemetry from field RTUs/PLCs via a realistic transport mix (cellular polling, satellite, radio). Implement per-channel quality flags to distinguish a flatlining sensor from a cell tower outage.
2. **Production Allocation:** Reconcile metered tank gauges against wellhead production estimates and the sales meter at the delivery point. Handle deductions for compressor recycling and on-site fuel use.
3. **Operations Dashboard:** Surface wells with abnormal pressure trends or gas-to-oil ratio (GOR) shifts that suggest downhole problems.
4. **Alarm Management:** Suppress chronic alarms that operators typically ignore, while preserving genuine alarm signals.
5. **Regulatory Reporting:** Generate monthly state production filings, federal GHG inventory reports, and BLM/state lease records. **Crucial:** These reports MUST generate exclusively from actual measured data.
6. **Historical Archive:** Preserve raw telemetry at native resolution for engineering investigations. Implement pagination.
7. **Access Boundaries (RBAC):** Enforce audit and operations access boundaries that respect the realities of a contract operator versus an asset owner structure.

## Expected Interface

- **Path:** `src/main/kotlin/Application.kt`
- **Name:** `module`
- **Type:** method
- **Input:** None
- **Output:** Unit
- **Description:** Ktor application module entry point. Configures routing, JSON content negotiation, and initializes the local SQLite database with the required sample data.

- **Path:** `POST /telemetry`
- **Name:** `ingestTelemetry`
- **Type:** API Endpoint
- **Input:** JSON payload containing telemetry data (`wellId`, `channel`, `value`, `transportType`).
- **Output:** `200 OK`
- **Description:** Ingests raw telemetry and evaluates channel quality flags to detect sensor or transport outages.

- **Path:** `GET /dashboard/wells/anomalies`
- **Name:** `getAnomalies`
- **Type:** API Endpoint
- **Input:** None
- **Output:** JSON array of anomaly objects.
- **Description:** Surfaces wells with abnormal pressure trends or GOR shifts.

- **Path:** `GET /alarms/active`
- **Name:** `getActiveAlarms`
- **Type:** API Endpoint
- **Input:** Request Headers containing user identification and role.
- **Output:** JSON array of alarm objects.
- **Description:** Returns active genuine alarms, explicitly filtering out suppressed chronic alarms and applying contract operator access boundaries.

- **Path:** `GET /reports/regulatory`
- **Name:** `getReports`
- **Type:** API Endpoint
- **Input:** Query param `type: String` (e.g., "federal_ghg", "state", "blm").
- **Output:** JSON report object.
- **Description:** Generates regulatory reports based exclusively on measured data.

- **Path:** `GET /archive/telemetry`
- **Name:** `getTelemetryArchive`
- **Type:** API Endpoint
- **Input:** Query params `wellId: Int` and `cursor: String?`
- **Output:** JSON array of telemetry records with a `nextCursor` string for pagination.
- **Description:** Returns paginated historical raw telemetry data at native resolution.
