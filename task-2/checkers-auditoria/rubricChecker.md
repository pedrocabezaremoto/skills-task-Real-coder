# Rubric Checker — Template Genérico

> Usa este archivo en Cursor Chat para auditar cada criterio del rubric antes de la entrega.
> Basado en: `docs/G04_rubric_changelog.md` (oficial QC)

---

## INSTRUCCIÓN DE USO

Para cada criterio del rubric, verifica los ítems de abajo. Un criterio con cualquier issue MAJOR = FAIL del rubric completo si supera el 5% del total de criterios.

---

## BLOQUE 1 — Reglas Generales del Rubric

| # | Verificación | Estado |
|---|---|---|
| 1.1 | Hay **mínimo 5 criterios** en total | ⬜ |
| 1.2 | Todos los pesos son **1, 3 o 5** (nunca 2 ni 4) | ⬜ |
| 1.3 | Los criterios cubren los requerimientos **no testeables por unit tests** | ⬜ |
| 1.4 | No hay criterios que duplican cobertura de los unit tests | ⬜ |
| 1.5 | Si hay <30 reqs explícitos: TODOS deben tener cobertura (test o rubric). Si hay >=30: al menos los top 30 más importantes están cubiertos | ⬜ |
| 1.6 | Si faltan >3 reqs explícitos importantes sin cobertura → FAIL | ⬜ |

---

## BLOQUE 2 — Calidad de Cada Criterio

Para cada criterio, verifica:

| Propiedad | Regla | Tipo de error |
|---|---|---|
| **Atomicidad** | Verifica UNA sola cosa. **Excepción:** features relacionadas pueden agruparse (ej: "implementa stack X, Y, Z") | MAJOR |
| **Self-contained** | Se puede evaluar SIN leer el prompt. Mal: "Maneja el edge case del prompt". Bien: "Maneja cantidad negativa retornando 400" | MAJOR |
| **Positive framing** | Evalúa a YES/PASS cuando es correcto | MAJOR |
| **Framing correcto** | "Does not use X" → debe decir en positivo. Se cuenta como MAJOR | MAJOR |
| **No subjetivo** | Sin "apropiado", "correcto", "buenas prácticas" sin definir | MODERATE |
| **Overfitting** | Rechaza implementaciones válidas alternativas (ej: exige nombres de archivo/variable que el prompt no pidió) | MAJOR |
| **Underfitting** | Acepta implementaciones inválidas (demasiado permisivo) | MAJOR |
| **Incorrect Criteria** | Evalúa algo que el prompt no pide, o contiene error factual (ej: "usar selection sort que es O(n log n)") | MAJOR |

---

## BLOQUE 3 — Dimensiones Obligatorias

Todo rubric debe tener **al menos 1 criterio** en cada dimensión:

| Dimensión | Descripción |
|---|---|
| Instruction Following | Cumplimiento de instrucciones explícitas (formato, lenguaje, librerías) |
| Code Correctness | El código produce resultados correctos |
| Code Quality | Robusto, mantenible, patrones idiomáticos |
| Code Clarity | Legible, bien organizado, nombres significativos |
| Code Efficiency | Algoritmos eficientes, sin pasos innecesarios |

---

## BLOQUE 4 — Tipos de Issue (basado en G04)

### MAJOR Issues
- **Missing Criteria - Critical Requirements:** Falta un criterio para un requirement explícito importante
- **Not Self Contained:** Requiere leer el prompt para evaluarse
- **Not Atomic (totally unrelated):** Agrupa constraints completamente no relacionados
- **Incorrect Criteria:** Evalúa algo incorrecto, no alineado con el prompt, o factualmente erróneo
- **Framing:** No está formulado en positivo (no evalúa a "Yes"/"True")
- **Overfitting:** Rechaza implementaciones válidas
- **Underfitting:** Acepta implementaciones inválidas

### MODERATE Issues
- **Missing Criteria - Non-critical:** Falta un criterio para un requirement no crítico
- **Overlapping/Redundant:** Dos o más criterios evalúan lo mismo
- **Subjective Criteria:** Lenguaje vago sin medida ("apropiado", "best practices")
- **Incorrect Weights - Major:** Peso off por 2 niveles (1↔5)

### MINOR Issues
- **Incorrect Weights - Minor:** Peso off por 1 nivel (1↔3 o 3↔5)
- **Miscategorized Criteria:** Dimensión incorrecta (si hay una claramente mejor)

---

## BLOQUE 5 — Conteo de Errores

| Tipo | Cantidad | % del total | ¿FAIL? |
|---|---|---|---|
| MAJOR | | | ⬜ >5% → FAIL |
| MODERATE (incl. major) | | | ⬜ >15% → FAIL |
| MINOR (incl. todos) | | | ⬜ >25% → FAIL |

**Total criterios escritos:** ___
**Umbral MAJOR para FAIL:** ___ criterios (5% de total)
**Umbral MODERATE para FAIL:** ___ criterios (15% de total)

> **Regla:** No doble contabilizar. Si un criterio tiene 1 MAJOR + 1 MODERATE, cuenta solo como 1 MAJOR.

---

## RESULTADO FINAL

| Bloque | Estado |
|---|---|
| Bloque 1 — Reglas generales | ⬜ PASS / ⬜ FAIL |
| Bloque 2 — Calidad por criterio | ⬜ PASS / ⬜ FAIL |
| Bloque 3 — 5 dimensiones cubiertas | ⬜ PASS / ⬜ FAIL |
| Bloque 4 — Tipos de issue correctos | ⬜ PASS / ⬜ FAIL |
| Bloque 5 — Error rate OK | ⬜ PASS / ⬜ FAIL |

### ✅ RUBRIC LISTO — todos los bloques en PASS
### ❌ REGRESA A CORREGIR — uno o más bloques en FAIL

---

## NOTAS / ISSUES ENCONTRADOS

```
(anota aquí cualquier criterio con problema)
```
