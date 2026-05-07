# Requirements Coverage Matrix — Template Genérico

> Mapea CADA requirement del prompt a su método de verificación (unit test y/o rubric).
> Basado en: `docs/G04_rubric_changelog.md` (oficial QC)

---

## COVERAGE RULE

```
Functional Logic (Math/DB)   → Unit Test — Mandatory
Output Formats / API         → Rubric o Test — Mandatory
Architecture / Tech Stack    → Rubric
UI/UX (no testeable)         → Rubric
Gaps no cubiertos por tests  → Rubric — Mandatory
```

### Notas importantes (G04):
- **Margen del 5%:** Hasta 5% de backend requirements MAYORES pueden no estar cubiertos por tests NI rubrics (non-fail). Más de 5% = FAIL.
- **Top 30:** Solo necesitas cubrir los top 30 requerimientos más importantes que NO pueden cubrirse con unit tests.
- **UI subjetiva:** No marques falta de cobertura en requirements subjetivos de UI ("elegante", "bonito").
- **Bottleneck test:** Un solo test representativo cubre toda una sección de la Expected Interface si su falla indica colapso de toda esa lógica.

---

## COVERAGE MATRIX

| # | Requirement | Covered by Test | Covered by Rubric | Total Coverage |
|---|---|---|---|---|
| R01 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R02 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R03 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R04 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R05 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R06 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R07 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| R08 | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |
| ... | | ⬜ / ✅ | ⬜ / ✅ | ⬜ |

**Total Requirements:** ___
**Covered (test o rubric):** ___ / ___ = ___%
**Gaps (>5% = FAIL):** ___

---

## VERIFICACIONES ADICIONALES (por criterio)

| # | Check | Estado |
|---|---|---|
| V1 | Cada criterion es **atómico** (1 sola cosa, o features relacionadas agrupadas) | ⬜ PASS / ⬜ FAIL |
| V2 | Cada criterion es **self-contained** (no necesita leer el prompt) | ⬜ PASS / ⬜ FAIL |
| V3 | Cada criterion tiene **positive framing** (evalúa a "Yes") | ⬜ PASS / ⬜ FAIL |
| V4 | Cada criterion tiene peso **1, 3 o 5** correctamente asignado | ⬜ PASS / ⬜ FAIL |
| V5 | Cada criterion está en la **dimensión correcta** (IF, Correctness, Quality, Clarity, Efficiency) | ⬜ PASS / ⬜ FAIL |
| V6 | Sin **overfitting** (no rechaza implementaciones válidas alternativas) | ⬜ PASS / ⬜ FAIL |
| V7 | Sin **underfitting** (no acepta implementaciones inválidas) | ⬜ PASS / ⬜ FAIL |
| V8 | Sin **subjetividad** sin medida ("apropiado", "best practices") | ⬜ PASS / ⬜ FAIL |
| V9 | No hay **redundancia** entre criteria | ⬜ PASS / ⬜ FAIL |
| V10 | Tests no son **overly specific** (>10% del total = FAIL) | ⬜ PASS / ⬜ FAIL |

---

## FINAL COVERAGE VERDICT

| Check | Status |
|---|---|
| 100% requirements cubiertos (test o rubric) — con margen 5% | ⬜ PASS / ⬜ FAIL |
| Todos los pesos son 1, 3 o 5 | ⬜ PASS / ⬜ FAIL |
| Atomicidad correcta en todos los criterios | ⬜ PASS / ⬜ FAIL |
| Sin overfitting/underfitting | ⬜ PASS / ⬜ FAIL |
| Sin redundancias | ⬜ PASS / ⬜ FAIL |
| Tests no overly specific (>10%) | ⬜ PASS / ⬜ FAIL |

### ✅ READY FOR SUBMISSION
### ❌ REGRESA A CORREGIR
