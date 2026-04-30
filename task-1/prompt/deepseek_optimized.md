model.run via local
provider: openrouter
model: deepseek/deepseek-v3.2
outputs: 1
# SCADA Data Aggregation Service (Ktor)

## Contexto
Servicio backend en Kotlin/Ktor para un operador petrolero independiente. Ingresa telemetría de campo, reconcilia producción, gestiona alarmas, genera reportes regulatorios y archiva datos. Ejecución local con datos de muestra embebidos.

## Stack
- **Kotlin 1.9**, **Ktor 2.3**
- **SQLite** via Exposed 0.44
- **Gradle 8.5** (Kotlin DSL)
- **JVM 17**, **kotlinx.serialization 1.6**, **JUnit 5**

---

## Requisitos Funcionales

### R01 – Ingestion y Estado de Canales
- Tabla `telemetry` (append‑only) con campos: `well_id`, `facility_id`, `channel_id`, `timestamp` (ISO‑8601), `channel` (pressure|temperature|flow|gor), `transport` (cellular|satellite|radio), `value` (Double), `reported_quality_flag` (ok|flatline), `comm_status` (ok|timeout|poll_error).
- Tabla `channel_status` (clave `channel_id`) con: `signal_condition` (ok|suspected_flatline), `connectivity_condition` (ok|suspected_outage), `probable_cause` (none|transport_outage|isolated_local_fault), `expected_cadence_minutes` (Int), `last_seen` (ISO‑8601).
- **Job programado** que ejecuta secuencialmente:
  1. **Flatline check**: por cada `channel_id`, las 5 lecturas más recientes (orden evento). Si los 5 `value` son idénticos → `signal_condition = suspected_flatline`; sino `ok`.
  2. **Outage check**: canal `overdue` si `current_utc - last_seen > 2 * expected_cadence_minutes`. Si ≥3 canales con mismo `facility_id` y `transport` están `overdue` simultáneamente → `connectivity_condition = suspected_outage` y `probable_cause = transport_outage`; si solo un canal `overdue` → `suspected_outage` y `probable_cause = isolated_local_fault`; si no `overdue` → `ok` y `none`.
- `last_seen` se actualiza con cada lectura ingerida.

### R02 – Dataset de Muestra
Generador determinista que se ejecuta automáticamente si la BD está vacía. Incluye:
- 50 pozos → 10 instalaciones (5 pozos por instalación).
- Cada pozo+canal tiene entrada única en `channel_status`. Transporte primario: pozos 1‑20 `radio` (cadencia 1 min), 21‑40 `cellular` (15 min), 41‑50 `satellite` (60 min).
- 3 puntos de entrega, 1 sistema de recolección.
- 10 items de equipo con `vent_rate_mcf_per_hour`.
- Asignación de arrendamientos: pozos 1‑25 `federal`, 26‑50 `state`.
- `gas_composition` por instalación (`methane_fraction`, `gwp_factor`).
- `equipment_runtime` por equipo (`vent_hours`, `runtime_hours`).
- **5 tablas de medición** (72 horas de datos para los 50 pozos):
  - `tank_gauge_readings` (well_id, date, volume)
  - `wellhead_estimates` (well_id, date, estimated_volume)
  - `sales_meter_readings` (delivery_point_id, date, metered_volume)
  - `compressor_logs` (facility_id, date, recycled_volume)
  - `fuel_use_logs` (facility_id, date, fuel_volume)
- 30 días de historial de alarmas (`alarms`).
- 3 organizaciones, 6 usuarios (2 por rol). `user_organization_roles` asigna:
  - user_id=1 → org_id=1, rol `operator_of_record`.
  - user_id=2 → org_id=1 y org_id=2, rol `contract_operator` en cada una.
- Otros usuarios con rol único en una organización.

### R03 – Asignación de Producción por Pozo
Para cada pozo y fecha:
- Lee `tank_gauge_readings.volume` y `wellhead_estimates.estimated_volume`.
- `gross_volume` = promedio de los dos.
- Resta `compressor_logs.recycled_volume` y `fuel_use_logs.fuel_volume` (de la instalación del pozo).
- `net_oil_volume` = `gross_volume - compressor_recycling - fuel_use`.
- `net_gas_volume` = 0.0 (demo).
- `sales_meter_volume` = volumen atribuido desde `sales_meter_readings`.
- **Varianzas**:
  - `variance_oil` = `net_oil_volume - sales_meter_volume`
  - `variance_estimate` = `tank_gauge_volume - wellhead_estimate_volume`
- Tabla `production_allocation` almacena: `well_id`, `date`, `gross_volume`, `compressor_recycling`, `fuel_use`, `net_oil_volume`, `net_gas_volume`, `sales_meter_volume`, `variance_oil`, `variance_estimate`.

### R04 – Endpoint de Anomalías
`GET /dashboard/wells/anomalies` retorna JSON array con pozos que cumplen al menos una condición:
1. **Tendencia de presión**: 3 lecturas consecutivas de presión, cada una >10% mayor que la anterior.
2. **Shift de GOR**: cambio >15% dentro de una ventana de 6 horas.
Campos: `well_id`, `anomaly_type` ("pressure_trend" o "gor_shift"), `detected_at`, `current_value`, `baseline_value`.

### R05 – Gestión de Alarmas
- Alarma crónica: misma `well_id`+`channel` disparada ≥20 veces en últimos 30 días sin `acknowledged`.
- `suppressChronicAlarms()` marca `suppressed = true` en alarmas crónicas.
- `GET /alarms/active` retorna solo alarmas con `suppressed = false`, dentro del alcance autorizado del usuario.

### R06 – Reportes Regulatorios
`GET /reports/regulatory?type=...` soporta:
- `state_production`: volúmenes netos mensuales por pozo (`net_oil_volume`).
- `federal_ghg`:
  - `methane_volume` = `net_gas_volume * methane_fraction`
  - `co2e` = `methane_volume * gwp_factor`
  - `vented_volume` = `vent_hours * vent_rate_mcf_per_hour`
  - Incluir campo `calculation_basis`: `"Demo estimate derived from measured production and seeded equipment data"`
- `blm_lease`: totales de producción agrupados por `lease_type` (federal/state) usando `well_lease_assignments`.

### R07 – Archivo Histórico
`GET /archive/telemetry` con paginación keyset.
Parámetros: `well_id`, `channel`, `from`, `to` (ISO‑8601), `limit` (max 1000), `after_id`.
Índice compuesto en `(well_id, channel, timestamp, id)`.
Respuesta: `{ "data": [...], "next_cursor": id | null }` ordenado por `(timestamp ASC, id ASC)`.

### R08 – Control de Acceso
- Tablas: `organizations`, `user_organization_roles` (user_id, organization_id, role), `assets`, `users` (con `facility_assignment_scope` CSV), `audit_logs`.
- Roles: `operator_of_record` (acceso completo a activos de su organización), `contract_operator` (lectura/escritura en `facility_assignment_scope`), `auditor` (solo lectura en scope).
- Autenticación HTTP Basic con BCrypt.
- Cada endpoint debe aplicar autorización según rol y scope; registrar decisión en `audit_logs`.

### R09 – Health Check
`GET /health` → 200 `{"status": "ok"}`.

---

## Modelos Principales

```kotlin
// TelemetryReading.kt
enum class ChannelType { pressure, temperature, flow, gor }
enum class TransportType { cellular, satellite, radio }
enum class QualityFlag { ok, flatline }
enum class CommStatus { ok, timeout, poll_error }
data class TelemetryReading(
    val well_id: String,
    val facility_id: String,
    val channel_id: String,
    val timestamp: String,
    val channel: ChannelType,
    val transport: TransportType,
    val value: Double,
    val reported_quality_flag: QualityFlag,
    val comm_status: CommStatus
)

// ChannelStatus.kt
enum class SignalCondition { ok, suspected_flatline }
enum class ConnectivityCondition { ok, suspected_outage }
enum class ProbableCause { none, transport_outage, isolated_local_fault }
data class ChannelStatus(
    val channel_id: String,
    val well_id: String,
    val facility_id: String,
    val transport: TransportType,
    val signal_condition: SignalCondition,
    val connectivity_condition: ConnectivityCondition,
    val probable_cause: ProbableCause,
    val expected_cadence_minutes: Int,
    val last_seen: String
)

// ProductionAllocation.kt
data class ProductionAllocation(
    val well_id: String,
    val date: String,
    val gross_volume: Double,
    val compressor_recycling: Double,
    val fuel_use: Double,
    val net_oil_volume: Double,
    val net_gas_volume: Double,
    val sales_meter_volume: Double,
    val variance_oil: Double,
    val variance_estimate: Double
)

// Alarm.kt
data class Alarm(
    val alarm_id: Long,
    val well_id: String,
    val channel: String,
    val triggered_at: String,
    val acknowledged: Boolean,
    val suppressed: Boolean
)

// WellAnomaly.kt
data class WellAnomaly(
    val well_id: String,
    val anomaly_type: String, // "pressure_trend" o "gor_shift"
    val detected_at: String,
    val current_value: Double,
    val baseline_value: Double
)

// UserRole.kt
enum class UserRole { operator_of_record, contract_operator, auditor }
```

---

## Servicios (firmas esenciales)

```kotlin
// TelemetryService.kt
fun ingest(reading: TelemetryReading)

// ChannelStatusService.kt
fun evaluate(currentUtcTime: Instant)
fun getStatus(channelId: String): ChannelStatus?

// SampleDataGenerator.kt
fun generate()  // ejecuta solo si BD vacía

// ProductionAllocationService.kt
fun allocate(wellId: String, date: String): ProductionAllocation

// AlarmService.kt
fun suppressChronicAlarms(): Int
fun getActiveAlarms(userId: Long): List<Alarm>

// AuthorizationService.kt
fun authorize(userId: Long, assetOwnerOrgId: Long, facilityId: String?, operation: String): Boolean
fun getAuthorizedFacilityIds(userId: Long): List<String>
```

---

## Endpoints API

| Método | Ruta | Parámetros / Body | Respuesta | Auth |
|--------|------|-------------------|-----------|------|
| POST | `/telemetry` | `TelemetryReading` JSON | 201 vacío | Basic |
| GET | `/dashboard/wells/anomalies` | – | `List<WellAnomaly>` | Basic |
| GET | `/alarms/active` | – | `List<Alarm>` (suppressed=false) | Basic |
| GET | `/reports/regulatory` | `type` (state_production, federal_ghg, blm_lease) | JSON según tipo | Basic |
| GET | `/archive/telemetry` | `well_id`, `channel`, `from`, `to`, `limit?`, `after_id?` | `{data:[…], next_cursor}` | Basic |
| GET | `/health` | – | `{"status":"ok"}` | – |

---

## Notas de Implementación

1. **Generador de datos**: crear datos deterministas para 72 horas en las 5 tablas de medición, 30 días de alarmas, y las estructuras de organización/usuarios.
2. **Job programado**: ejecutar `ChannelStatusService.evaluate` periódicamente (p.ej. cada minuto) usando reloj UTC del servidor.
3. **Índices**: crear índice compuesto `(well_id, channel, timestamp, id)` en `telemetry` para paginación eficiente.
4. **Autenticación**: HTTP Basic; contraseñas almacenadas con BCrypt.
5. **Alcance**: todos los endpoints (excepto `/health`) deben filtrar datos por `getAuthorizedFacilityIds`.
6. **Conexión**: servidor Ktor debe bind a `127.0.0.1`.
7. **Compilación**: `./gradlew run` debe iniciar el servicio y generar datos si la BD está vacía.

---

## Determinismo Requerido

- Las evaluaciones de canal (`flatline`, `outage`) deben seguir exactamente la lógica descrita.
- Las varianzas `variance_oil` y `variance_estimate` deben calcularse como se define.
- El generador de datos debe producir exactamente las entidades especificadas (50 pozos, 10 instalaciones, etc.).
- Los reportes regulatorios deben aplicar las fórmulas indicadas (metano, CO2e, vented).

El prompt anterior es conciso, estructurado y mantiene todos los requisitos funcionales y especificaciones de interfaz, eliminando redundancias mientras preserva el determinismo exigido.
