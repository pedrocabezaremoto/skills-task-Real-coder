# Reporte de Avance — Proyecto Wedding Venue Management System

> **Cliente:** Peterhead (Pedro)
> **Proyecto:** Real Coder Task 2 — Wedding Venue Management System
> **Fecha:** 2026-05-07

---

## Resumen General

Proyecto de tipo **Frontend Development** para crear un sistema de gestión de salones de bodas con 4 vistas de dashboard (Sales, Coordinator, Kitchen, Owner). El objetivo es transformar una descripción de tarea raw en un prompt estructurado, auditarlo, y eventualmente crear tests, rúbricas, y la solución Golden Patch.

---

## FASE 0 — Entendimiento del Seed Task ✅ COMPLETADA

### Actividades realizadas:
- Lectura completa de `Requerimientos-task.md`
- Identificación del tipo de tarea: **Frontend Development**
- Extracción de los 14 requisitos funcionales del seed
- Lectura de toda la documentación del proyecto (`docs/`): 10 guías (G01-G10) + INDEX

### Requisitos identificados del seed:
| # | Requisito |
|---|-----------|
| R01 | Inquiry Management (couple names, date, guest count 20-300, ceremony type, budget) |
| R02 | Workflow states: Received → Tour Scheduled → Proposal Sent → Contracted → Lost |
| R03 | Booking constraints configurable por día (Weekdays max 1, Sat max 3, Sun max 2) |
| R04 | Venue fees: Fri $8k, Sat $12k, Sun $9k, Weekday $5k |
| R05 | Payment schedule: 30% signing, 40% D-90, 30% D-30, rounded 2 decimals |
| R06 | Auto-flag payments overdue >7 days |
| R07 | Vendor management: categories, rating 1-5, no double-booking |
| R08 | Timeline management: duration, location, overlap detection |
| R09 | Catering: guest count + 5% buffer, dietary counts sum to guest count |
| R10 | Floor plan: capacity >= guest count |
| R11 | Sales Dashboard: pipeline, tour calendar, conversion rate |
| R12 | Coordinator Dashboard: timelines, vendor assignments, payment status |
| R13 | Kitchen Dashboard: catering orders, dietary breakdown |
| R14 | Owner Dashboard: revenue, profit margins, booking pace, vendor ratings, YoY growth |

---

## FASE 1 — Escritura del Prompt ✅ COMPLETADA

### Tech Stack seleccionado:
| Tecnología | Versión |
|------------|---------|
| React | 18.2 |
| TypeScript | 5.4 |
| Vite | 5.2 |
| Tailwind CSS | 3.4 |
| Lucide React | 0.344.0 |
| React Router | 6.22 |

### Archivos creados:
1. **`Prompts/prompt.md`** — Rewritten prompt siguiendo el Pattern A:
   - Title
   - Description / Context (freelance brief style)
   - Tech Stack (versiones exactas)
   - Key Requirements (16 requisitos numerados con MUST, sin "should"/"or"/"recommended")
   - Expected Interface (14 entradas públicas con Path, Name, Type, Input, Output, Description)
   - Current State ("Empty repository with test files only")

### Reglas de oro aplicadas:
- ✅ Determinism Rule: Sin "or", "should", "recommended", "you can", "etc."
- ✅ Sin instrucciones de tests ni rúbricas en el prompt
- ✅ Sin API keys ni datasets externos
- ✅ Sin Unsplash o assets con copyright
- ✅ Sin meta-data interna (task IDs, budget, timeline, CB notes)
- ✅ Sin helper functions documentadas en Expected Interface
- ✅ Strict Typing en Input/Output

---

## FASE 2 — Auditoría del Prompt ✅ COMPLETADA

### Herramienta usada:
`checkers-auditoria/promptchecker.md` (QA Protocol v3.1)

### Resultado por bloque:

| Bloque | Descripción | Estado |
|--------|------------|--------|
| Bloque 0 | Pre-Validación (Scope, Feasibility, Seed Fidelity) | ✅ PASS |
| Bloque 1 | Estructura del Prompt (Pattern A) | ✅ PASS |
| Bloque 2 | Tech Stack & Compliance (versiones exactas, compatibilidad) | ✅ PASS |
| Bloque 3 | Expected Interface (6 campos, strict typing, impl agnosticism) | ✅ PASS |
| Bloque 4 | Linguistic Determinism (términos prohibidos, phrasing imperativo) | ✅ PASS |
| Bloque 5 | Requirements Quality (Anti-Overfitting, Dual-Layer Coverage) | ✅ PASS |
| Bloque 6 | Requirements Coverage (14/14 = 100%) | ✅ PASS |
| Bloque 7 | Validaciones Críticas (contradicciones, factual, greenfield) | ✅ PASS |

### Correcciones aplicadas post-auditoría:
| Warning detectado | Corrección |
|-------------------|-----------|
| Lucide React versión `0.344` (incompleta) | Corregido a `0.344.0` (semver completo) |
| R16 usaba "or" como alternativa ("tables, cards, **or** charts") | Corregido a "tables, cards, **and** charts" |

---

## Estado Actual

```
FASE 0: Entender seed task        ✅ COMPLETADA
FASE 1: Escribir prompt.md        ✅ COMPLETADA  
FASE 2: Auditar prompt            ✅ COMPLETADA
FASE 3: Escribir tests F2P        ⏳ PENDIENTE (esperando aprobación en Outlier)
FASE 4: Crear rúbricas            ⏳ PENDIENTE
FASE 5: Golden Patch + Verificación ⏳ PENDIENTE
```

### Próximo paso:
Una vez aprobado el prompt en Outlier, continuar con **FASE 3** — creación de los tests unitarios F2P (Fail-to-Pass) usando Vitest, cubriendo toda la lógica de negocio del archivo `src/utils/calculations.ts`.

---

## Estructura del Proyecto

```
task-2/
├── Prompts/
│   └── prompt.md              ← Rewritten prompt (listo para Outlier)
├── Historial/
│   └── reporte.md             ← Este archivo
├── checkers-auditoria/        ← Templates de auditoría
│   ├── prompt-creation-protocol.md
│   ├── promptchecker.md
│   ├── promptchecker_resultado.md
│   ├── rubric-audit-protocol.md
│   ├── rubricChecker.md
│   └── rubricndTestcoverage.md
├── docs/                      ← Guías del proyecto (G01-G10)
├── Images.png/
│   └── Primera-parte/
└── Requerimientos-task.md     ← Seed task original
```

---

## Notas Técnicas

- **Stack:** React 18.2 + TypeScript 5.4 + Vite 5.2 + Tailwind 3.4 + Lucide React 0.344.0 + React Router 6.22
- **Datos:** Locales embebidos en `src/data/sampleData.ts` — sin live fetching ni APIs externas
- **Estilo del prompt:** Freelance-brief (Pattern A)
- **Tests futuros:** Vitest para lógica de negocio + Rubrics para UI/UX
- **Entorno:** Ubuntu 22.04 + Docker (según especificación del proyecto)
