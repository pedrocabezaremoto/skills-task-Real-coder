# Prompt Creation & Audit Protocol — Real Coder (Outlier)

> Protocolo paso a paso para escribir un prompt desde cero y auditarlo con los checkers.
> Sigue este orden en CADA proyecto nuevo. No te saltes ningún paso.

---

## Material necesario

Antes de empezar, asegúrate de tener esto abierto:

| Recurso | Para qué sirve |
|---|---|
| Seed task original | La descripción de tarea que te dio Outlier |
| `promptchecker.md` | Lista de verificación para auditar el prompt después de escribirlo |
| `promptchecker_resultado.md` | Ejemplo real de cómo se ve un prompt auditado correctamente |
| `docs/G01_guidelines.md` | Reglas generales del proyecto |
| Tu Cursor/OpenCode | Donde vas a escribir el prompt |

---

## FASE 0 — Entender el seed task (5 minutos)

**Objetivo:** Saber exactamente qué te pide la tarea antes de escribir nada.

**Paso 0.1:** Lee el seed task completo de Outlier. Identifica:

- ¿Qué tipo de tarea es? (Full Stack, Backend API, CLI tool, Data Science library...)
- ¿Qué lenguaje/stack usa?
- ¿Cuáles son los requisitos funcionales? (subráyalos)
- ¿Tiene UI o es solo backend/CLI?
- ¿Requiere base de datos? ¿Cuál?

**Paso 0.2:** Anota los requisitos en una lista. Ejemplo:

```
R01: Parsear archivos CSV
R02: Calcular promedios por grupo
R03: Generar reporte en JSON
R04: Interfaz CLI con --input y --output
```

Esta lista la vas a usar en el Bloque 6 del checker.

---

## FASE 1 — Escribir el prompt (30-45 minutos)

**Objetivo:** Redactar el rewritten prompt siguiendo el patrón correcto (Pattern A o B).

### Estructura del prompt (Pattern A — el más común)

```
# Title (nombre corto del proyecto)

## Description / Context (1-3 párrafos: qué necesita el cliente, para qué)
## Tech Stack (lenguaje + framework + versiones exactas)
## Key Requirements (lista numerada de lo que hay que implementar)
## Expected Interface (cada función/clase/endpoint pública con sus 6 campos)
## Current State ("Empty repository with test files only")
```

### Paso 1.1 — Escribe el Title
Sé corto y descriptivo. Ej: `# Audio Fingerprinting and Matching Library`

### Paso 1.2 — Escribe el Description / Context
Explica el problema de negocio como lo haría un freelance. Incluye:
- Quién usa el sistema
- Para qué sirve
- Restricciones importantes (ruido, rendimiento, etc.)

### Paso 1.3 — Escribe el Tech Stack
**REGLA:** Todo debe tener versión exacta. NUNCA pongas "any", "latest", "your choice".

| ✅ Correcto | ❌ Incorrecto |
|---|---|
| Python 3.11, numpy 1.26, scipy 1.13 | Python, numpy, scipy |
| React 18.2, TypeScript 5.4 | React, JavaScript |
| Node.js 20 LTS | Node.js |

### Paso 1.4 — Escribe los Key Requirements
**REGLAS DE ORO:**
- Usa **MUST**, **Implement**, **Create**, **Return** — NUNCA "should", "recommended", "you can"
- Cada requirement describe **comportamiento observable** (qué se ve desde fuera)
- NO dictes nombres de funciones helper, variables internas, ni estructura de archivos que el seed no pida
- NO uses "or" como alternativa (`"usar SQLite OR JSON"` → debes elegir UNA)

Ejemplo:
```
✅ "The system MUST compute the SHA-256 hash of each file."
❌ "You should compute a hash of each file, or maybe just use the filename."
```

### Paso 1.5 — Escribe la Expected Interface

Para CADA componente público (lo que los tests van a importar), completa estos 6 campos:

```
- Path: src/fingerprint.py
- Name: generate_hashes
- Type: function
- Input: audio_path: str, sample_rate: int = 44100
- Output: list[tuple[int, int, int]]
- Description: Reads a WAV file, applies STFT, extracts peak pairs, and returns a list of (hash, offset, peak_freq) tuples.
```

**⚠️ ERRORES COMUNES (evítalos):**
- Documentar helpers internos (solo documenta lo que los tests importan)
- Poner tipos vagos como `any`, `object`, `dict`
- Poner descripciones que filtran cómo implementaste la función por dentro

### Paso 1.6 — Escribe Current State
Siempre es: `"Empty repository with test files only."`

---

## FASE 2 — Auditar el prompt con `promptchecker.md` (15-20 minutos)

**Objetivo:** Pasar el prompt por cada bloque del checker hasta que todos estén en ✅ PASS.

### Cómo usar el checker

Abre `promptchecker.md` en tu agente (Cursor/OpenCode) junto con tu `prompt.md`. Pide al agente:

> "Audita mi prompt.md usando promptchecker.md. Dame el resultado bloque por bloque."

El agente te va a devolver algo como el archivo `promptchecker_resultado.md`. Tú solo revisas los resultados.

### Paso 2.1 — Bloque 0: Pre-Validación (el más IMPORTANTE)

Si falla algo aquí, **para todo** y corrige antes de seguir.

| # | Pregunta clave | Si falla... |
|---|---|---|
| 0.2 | ¿Hay requests imposibles o contradictorias? | Corrige el prompt |
| 0.3 | ¿Pide API keys externas o datasets descargables? | Cambia a datos locales |
| 0.4 | ¿Tiene 3+ constraints apiladas? (ej: "brief + child + no letter e") | Reduce a máx 2 |
| 0.6 | ¿Añadiste funcionalidad que el seed no pide? | Sácala |

### Paso 2.2 — Bloque 1: Estructura

Verifica:
- ¿Usa Pattern A o B?
- ¿Tiene Title, Context, Tech Stack, Requirements, Expected Interface, Current State?
- ¿Los Requirements están numerados y son testeables?

### Paso 2.3 — Bloque 2: Tech Stack

Verifica:
- ¿Todas las versiones son explícitas? (Python 3.11, no "Python")
- ¿Las versiones son compatibles entre sí?
- ¿No hay librerías que requieran API keys?
- ¿No menciona Unsplash?

### Paso 2.4 — Bloque 3: Expected Interface (el más DIFÍCIL)

Este bloque es donde más errores ocurren. Verifica:

| # | Pregunta clave |
|---|---|
| 3.2 | ¿Documentaste helpers internos? → BORRA esos |
| 3.6 | ¿Las descripciones filtran lógica interna? → Reescribe como comportamiento observable |
| 3.8 | ¿Los tipos son exactos? → `list[tuple[str, int]]`, no `list` a secas |
| 3.10 | ¿Cada import de los tests tiene su correspondiente en la interfaz? |

### Paso 2.5 — Bloque 4: Linguistic Determinism

Escanea TODO el prompt por estas palabras prohibidas:

| Palabra | ¿Por qué? |
|---|---|
| **or** (como alternativa) | El agente puede elegir cualquier opción → resultado impredecible |
| **should** | No es un mandato → el agente puede ignorarlo |
| **recommended** | Same as above |
| **you can** | Deja la decisión al agente |
| **etc.** | No defines el límite |
| **alternatively** | Bifurcación explícita |

Si encuentras cualquiera de estas en los Requirements → **FAIL**. Corrígelas por MUST, SHALL, Implement, Create.

### Paso 2.6 — Bloque 5: Requirements Quality

Verifica:
- **5.1:** No dictes nombres de funciones privadas ni variables internas
- **5.4:** Menos del 10% de los requirements deben ser "overly specific" (detalles de implementación que el seed no pide)
- **5.5:** Los requirements cualitativos (UI, diseño) deben estar marcados como "Rubric Only"

### Paso 2.7 — Bloque 6: Requirements Coverage

Llena la tabla con los requisitos del seed original. Verifica que cada uno esté presente en tu prompt y sea testeable.

```
| # | Requerimiento del seed | Presente? | Testeable? |
|---|---|---|---|
| R01 | Parsear CSV con columnas A, B, C | ✅ | ✅ |
| R02 | Calcular promedio por grupo | ✅ | ✅ |
```

**Si cubres menos del 95% → FAIL.** Regresa y agrega los requisitos faltantes.

### Paso 2.8 — Bloque 7: Validaciones Críticas

| # | Pregunta clave |
|---|---|
| 7.1 | ¿Hay instrucciones contradictorias? |
| 7.5 | ¿Todo corre en Ubuntu 22.04 + Docker? |
| 7.6 | ¿Las versiones de librerías son correctas? (verifícalo con `pip`, `npm`, etc.) |
| 7.9 | ¿El startup es auto-contenido? (sin pasos manuales) |

---

## FASE 3 — Interpretar el resultado

| Resultado | Significado | Qué hacer |
|---|---|---|
| **Todos los bloques ✅ PASS** | Prompt listo para Fase 2 (tests) | ✅ Avanza a escribir los tests |
| **1 o más bloques ❌ FAIL** | Prompt tiene errores críticos | ❌ Corrige los ítems que fallaron y repite la auditoría desde el bloque 0 |
| **⚠️ WARNING aislado** | No bloquea, pero anótalo | Anota el warning y sigue. Si hay 3+ warnings, mejor corrige |

---

## Ejemplo real (copy-paste de `promptchecker_resultado.md`)

Cuando termines la auditoría, tu resultado debería verse así:

```
## RESULTADO FINAL

| Bloque | Estado |
|---|---|
| Bloque 0 — Pre-Validación | ✅ PASS |
| Bloque 1 — Estructura | ✅ PASS |
| Bloque 2 — Tech Stack | ✅ PASS |
| Bloque 3 — Expected Interface | ✅ PASS |
| Bloque 4 — Linguistic Determinism | ✅ PASS |
| Bloque 5 — Requirements Quality | ✅ PASS |
| Bloque 6 — Requirements Coverage | ✅ PASS (11/11) |
| Bloque 7 — Validaciones Críticas | ✅ PASS |

### ✅ LISTO PARA FASE 2
```

Si ves ❌ FAIL en cualquier bloque → **NO AVANCES**. Corrige y repite la auditoría.

---

## Diagrama de flujo rápido

```
┌──────────────────────────────────┐
│ 0. Leer seed task + anotar reqs  │
└──────────┬───────────────────────┘
           ▼
┌──────────────────────────────────┐
│ 1. Escribir prompt (Title,       │
│    Context, Tech Stack, Reqs,    │
│    Expected Interface,           │
│    Current State)                │
└──────────┬───────────────────────┘
           ▼
┌──────────────────────────────────┐
│ 2. Abrir promptchecker.md        │
│    + prompt.md en el agente      │
└──────────┬───────────────────────┘
           ▼
┌──────────────────────────────────┐
│ 3. Ejecutar auditoría bloque por │
│    bloque (0 → 1 → 2 → ... → 7) │
└──────────┬───────────────────────┘
           ▼
    ┌──────────────┐
    │ ¿Todo PASS?  │
    ├─────┬────────┤
    │  Sí │  No    │
    ▼     │       ▼
┌────────┐ │ ┌──────────────────────┐
│ ✅ LISTO│ │ │ ❌ Corregir errores  │
│ PASAR A │ │ │    y repetir         │
│ FASE 2  │ │ │    desde Bloque 0    │
└────────┘ │ └──────────────────────┘
           ▼
┌──────────────────────────────────┐
│ 4. Guardar resultado auditado    │
│    (como promptchecker_resultado │
│    _<tarea>.md)                  │
└──────────────────────────────────┘
```
