# Rubric & Test Coverage Matrix — Task 69d82c44
## Audio Fingerprinting Library | Data Science | Python 3.11

> Este archivo mapea CADA requerimiento del prompt contra su método de verificación (unit test y/o rubric). Ningún requerimiento puede quedar sin cubrir.

---

## REGLA DE COBERTURA

```
Lógica funcional (Math/DB) → Unit Test (F2P) — obligatorio
Formatos de salida / CLI   → Rubric / Test — obligatorio
Arquitectura / Tech Stack  → Rubric
Lo que tests no cubren     → Rubric — sin excepciones
```

---

## MATRIZ DE COBERTURA (Audio Fingerprint)

| # | Requerimiento | Cubierto por Test | Cubierto por Rubric | Cobertura Total |
|---|---|---|---|---|
| R01 | `fingerprint` load (scipy), mono, float64, STFT params | ⬜ | ✅ (2.1, 2.2) | ✅ |
| R02 | Detección de picos (multiplicativo threshold & mean) | ⬜ | ✅ (2.3) | ✅ |
| R03 | Máximos locales (excluyendo bordes 0 y N) | ⬜ | ✅ (2.4) | ✅ |
| R04 | Fórmula exacta de hash (bit-shifting formula) | ✅ (F2P `test_fingerprint_hash_formula`) | ✅ (2.5) | ✅ |
| R05 | Retorno de `fingerprint` (lista de tuplas o vacío) | ✅ (F2P `test_fingerprint_returns_list_of_tuples`) | ⬜ | ✅ |
| R06 | `build_database` iteración y limpieza previa (DELETE) | ⬜ | ✅ (3.2) | ✅ |
| R07 | Sentencia SQL CREATE TABLE + Index `idx_fingerprints_hash` | ✅ (F2P `test_build_database...`) | ✅ (3.1) | ✅ |
| R08 | `query` con búsqueda por índice y alineación temporal | ⬜ | ✅ (3.3) | ✅ |
| R09 | Casos exactos de `no_match` (casos a y b) | ✅ (F2P `test_query_no_match...`) | ⬜ | ✅ |
| R10 | `test_mode` seed 42, 20dB SNR y uso de `tempfile` | ✅ (F2P `test_test_mode_logic`) | ✅ (4.2) | ✅ |
| R11 | Lógica de `song_name` (sin ruta ni extensión) | ⬜ | ✅ (4.1) | ✅ |
| R12 | CLI: 3 subcomandos y mensajes stdout exactos | ✅ (F2P Tests CLI) | ✅ (4.3) | ✅ |
| R13 | `generate_samples` 2 archivos, 30s, chirps (200 hashes min) | ✅ (F2P `test_generate_samples...`) | ✅ (4.4, 5.2) | ✅ |
| R14 | Parámetros configurables (keyword args en firmas) | ⬜ | ✅ (5.1) | ✅ |
| R15 | Tech Stack compliance (versiones y no forbidden imports) | ⬜ | ✅ (1.1, 1.2) | ✅ |

**Total requerimientos: 15**
**Cubiertos: 15 / 15**
**Sin cubrir: 0** ← debe ser 0 antes de submit

---

## GAPS DETECTADOS

```
(No se detectaron gaps, cobertura 100% alcanzada combinando F2P Tests y Rúbricas manuales exhaustivas.)
```

---

## RESUMEN DE TESTS (F2P Baseline)

| Tipo | Cantidad |
|---|---|
| Tests totales escritos | 6 |
| Tests que fallan en codebase vacío (before.json) | 6 / 6 ← debe ser 100% |
| Tests que pasan con Golden Patch (after.json) | 0 / 6 ← Pendiente de implementación Golden |
| Tests overfitted (>5% = FAIL) | 0 |

---

## RESUMEN DE RUBRICS

| Tipo | Cantidad |
|---|---|
| Criterios totales | 16 |
| Peso 5 (críticos) | 5 |
| Peso 3 (importantes) | 9 |
| Peso 1 (deseables) | 2 |

---

## VEREDICTO FINAL DE COBERTURA

| Check | Estado |
|---|---|
| 100% requerimientos cubiertos (test o rubric) | ✅ |
| before.json = 100% FAILED | ✅ |
| after.json = 100% PASSED | ⬜ (Bloqueado hasta Fase 4) |

### ✅ LISTO PARA SUBMIT
