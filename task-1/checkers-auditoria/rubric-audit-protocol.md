# Rubric Audit Protocol — Real Coder (Outlier)

> Protocolo paso a paso para auditar rúbricas usando las herramientas en `checkers-auditoria/`.
> Úsalo al inicio de cada proyecto para garantizar calidad y evitar regresiones.

---

## Antes de empezar

### Archivos que necesitas tener listos

| Archivo | Descripción |
|---|---|
| `prompt.md` | Rewritten prompt con Expected Interface |
| `tests/` | Carpeta con los unit tests (F2P) |
| `rubrics.md` | Tus criterios de rúbrica con pesos y dimensiones |
| `docs/G04_rubric_changelog.md` | Referencia oficial QC del proyecto |
| `checkers-auditoria/rubricChecker.md` | Checker de calidad por criterio |
| `checkers-auditoria/rubricndTestcoverage.md` | Checker de cobertura tests + rúbricas |

### Carga estos archivos en tu agente (Cursor/OpenCode)

Agrega todos los archivos anteriores al contexto del agente antes de comenzar.

---

## FASE 1 — Mapear cobertura (usa `rubricndTestcoverage.md`)

**Objetivo:** Verificar que NO HAY GAPS entre lo que cubren los tests y lo que cubren las rúbricas.

### Paso 1.1 — Identifica todos los requirements del prompt

Lista cada requirement explícito del prompt. Incluye los de la Expected Interface.

### Paso 1.2 — Llena la Coverage Matrix

```
| # | Requirement | Covered by Test | Covered by Rubric | Total Coverage |
|---|---|---|---|---|
| R01 | ... | test_xyz | Rúbrica #3 | ✅ |
| R02 | ... | — | Rúbrica #1, #2 | ✅ |
| R03 | ... | test_abc | — | ✅ |
```

**Reglas:**
- Si un requirement tiene Total Coverage = ⬜ → es un **GAP**
- Si hay **>5% de gaps** → **FAIL** (el 5% es margen permitido por G04)
- Un requirement necesita cobertura de **test O rubric**, no necesariamente ambos

### Paso 1.3 — Verifica V1 a V10

Revisa cada uno de los 10 checks en el template. Por ejemplo:

| # | Check | Ejemplo de falla |
|---|---|---|
| V1 | Atómico | Un criterio mezcla "validar input" + "generar reporte" |
| V2 | Self-contained | Dice "maneja el error del prompt" sin especificar cuál |
| V6 | Sin overfitting | Exige nombre de variable interna que el prompt no pidió |
| V10 | Tests overly specific | >10% de tests проверяют detalles que el prompt no menciona |

---

## FASE 2 — Auditar cada criterio individual (usa `rubricChecker.md`)

**Objetivo:** Validar que cada criterio de rúbrica es correcto, medible y justo.

### Paso 2.1 — Toma cada criterio y pásalo por el Bloque 2

Evalúa estas 8 propiedades por cada criterio:

| Propiedad | Pregunta guía |
|---|---|
| **Atomicidad** | ¿Verifica UNA sola cosa? |
| **Self-contained** | ¿Se entiende sin leer el prompt? |
| **Positive framing** | ¿Evalúa a YES cuando es correcto? |
| **Framing** | ¿Está redactado en positivo? |
| **No subjetivo** | ¿Evita "apropiado", "buenas prácticas" sin definir? |
| **Overfitting** | ¿Acepta implementaciones alternativas válidas? |
| **Underfitting** | ¿Rechaza implementaciones inválidas? |
| **Incorrect Criteria** | ¿Evalúa algo que el prompt realmente pide? |

### Paso 2.2 — Clasifica cada issue encontrado

Usa el Bloque 4 como referencia:

```
MAJOR:   Missing Criteria (critical), Not Self Contained, Not Atomic,
         Incorrect Criteria, Framing, Overfitting, Underfitting

MODERATE: Missing Criteria (non-critical), Overlapping/Redundant,
          Subjective Criteria, Incorrect Weights (1↔5)

MINOR:   Incorrect Weights (1↔3 o 3↔5), Miscategorized Criteria
```

**Regla importante:** Si un criterio tiene 1 MAJOR + 1 MODERATE, cuenta solo como 1 MAJOR (no doble contabilizar).

### Paso 2.3 — Lleva el conteo en el Bloque 5

```
Total criterios: 10
MAJOR:       1 → 10%  → ❌ FAIL (>5%)
MODERATE:    2 → 20%  → ❌ FAIL (>15%)
MINOR:       3 → 30%  → ❌ FAIL (>25%)
```

---

## FASE 3 — Decisión final

| Bloque | Estado |
|---|---|
| Bloque 1 — Reglas generales | ⬜ PASS / ⬜ FAIL |
| Bloque 2 — Calidad por criterio | ⬜ PASS / ⬜ FAIL |
| Bloque 3 — 5 dimensiones cubiertas | ⬜ PASS / ⬜ FAIL |
| Bloque 4 — Tipos de issue correctos | ⬜ PASS / ⬜ FAIL |
| Bloque 5 — Error rate OK | ⬜ PASS / ⬜ FAIL |

- **Todos los bloques en PASS** → ✅ Rúbricas listas para entregar
- **Uno o más bloques en FAIL** → ❌ Corrige los criterios problemáticos y repite desde Fase 2

---

## Diagrama de flujo rápido

```
┌─────────────────────────────┐
│ 1. Cargar todos los archivos│
│    en el agente             │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 2. Mapear coverage matrix   │
│    (rubricndTestcoverage)   │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 3. ¿Hay gaps >5%?           │
│    Sí → ❌ Corregir rúbricas │
│    No  → Continuar          │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 4. Auditar cada criterio    │
│    (rubricChecker)          │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 5. Contabilizar errores     │
│    MAJOR/MODERATE/MINOR     │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ 6. ¿Error rate OK?          │
│    Sí → ✅ Entregar         │
│    No  → ❌ Corregir y      │
│           volver a paso 4   │
└─────────────────────────────┘
```

---

## Ejemplo real (para referencia rápida)

### Criterio MALO
> *"La respuesta usa el stack tecnológico adecuado y maneja los errores apropiadamente"*

| Check | Resultado |
|---|---|
| Atomicidad | ❌ — 2 cosas: stack + errores |
| Self-contained | ❌ — "adecuado" sin contexto |
| Subjetivo | ❌ — "adecuado", "apropiadamente" sin medida |
| Framing | ✅ |

**Veredicto:** 2 MAJOR (atomicidad + self-contained) + 1 MODERATE (subjetivo) → **FAIL**

### Criterio BUENO
> *"La aplicación usa SQLite como base de datos, con una tabla `sensors` que contiene las columnas: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), value (REAL NOT NULL), timestamp (TEXT NOT NULL)"*

| Check | Resultado |
|---|---|
| Atomicidad | ✅ — 1 cosa: schema de DB |
| Self-contained | ✅ — se entiende sin leer el prompt |
| No subjetivo | ✅ — todo es concreto y medible |
| Overfitting | ✅ — cualquier schema con esos campos funciona |

**Veredicto:** Sin issues → ✅ PASS
