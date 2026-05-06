# Prompt Checker — Template Genérico v3.1

> **QA Protocol v3.1** — Basado en: guia1 (Determinism Rule + Task Overfitting), guia2 (ATQAV-P + Dual-Layer Coverage), guia3 (Audit Protocol + Over-Specificity Thresholds), guia6 (SWE Validation + Solution Leakage), guia8 (Operational QA + UI Reachability), guia9 (Task Review + Seed Fidelity), guia10 (Master Audit Guide + Asset Compliance)
>
> **Regla de uso:** Ejecuta los bloques en orden estricto. Un FAIL en cualquier bloque es condición suficiente para rechazar el prompt. **Todos** deben estar en ✅ PASS antes de avanzar a Fase 2. No proceder bajo ninguna circunstancia si existe un FAIL no resuelto.

---

> **⚙ Adaptación por stack:**
> - Items marcados con `{UI}` solo aplican a tareas con frontend/UI visual (Full Stack, React, etc.). Para backend-only o CLI/library, marcar N/A.
> - Items marcados con `{TS}` solo aplican a TypeScript. Para Python/Kotlin/Go/etc., marcar N/A y verificar el equivalente en ese lenguaje (tipado estático, dataclasses, etc.).
> - Items marcados con `{HTTP}` solo aplican a APIs HTTP. Para CLIs o librerías, verificar exit codes o tipos de retorno según corresponda.
> - Items marcados con `{npm}` adaptar al gestor de paquetes del stack (pip, gradle, cargo, go mod, etc.).

---

## BLOQUE 0 — Pre-Validación: Scope, Feasibility & Seed Fidelity

> Ejecutar primero. Si falla aquí, detener inmediatamente — los bloques siguientes no son válidos.

| # | Verificación | Estado |
|---|---|---|
| 0.1 | El tipo de tarea es identificable y categorizable (ej: Full Stack API + React Dashboard, Data Science library, Backend API, CLI tool) — no ambiguo | ⬜ |
| 0.2 | No hay requests imposibles ni instrucciones mutuamente excluyentes — **1 miss = FAIL automático** | ⬜ |
| 0.3 | No se requieren API keys externas, datasets descargables ni servicios live en runtime | ⬜ |
| 0.4 | No hay "stacked constraints": máximo 2 restricciones solapadas sobre el mismo elemento (ej: "brief" + "explain to a child" + "no letter e" = FAIL) | ⬜ |
| 0.5 | La tarea exige razonamiento de ingeniería de nivel senior — no es lookup trivial ni tarea de traducción directa (**Reasoning Requirement**) | ⬜ |
| 0.6 | **Seed Fidelity:** el prompt reescrito preserva el contexto y scope original del seed task — no añade funcionalidad core no presente en el seed, ni elimina ningún requerimiento original | ⬜ |
| 0.7 | **Internal Reference Cleanup:** el prompt NO contiene task IDs internos, notas "CB", markers de workflow interno, ni meta-data como budget o timeline — son datos que no aportan valor técnico al agente | ⬜ |

**Resultado Bloque 0:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 1 — Estructura del Prompt (Pattern A / B)

| # | Verificación | Estado |
|---|---|---|
| 1.1 | El prompt usa **Pattern A** (Current State en posición 3) o **Pattern B** (Current State en posición 6) — patrón elegido declarado explícitamente | ⬜ |
| 1.2 | El campo **Title** está presente y describe claramente la tarea sin ambigüedad | ⬜ |
| 1.3 | El campo **Context** explica el problema de negocio y el perfil del usuario final que lo usa | ⬜ |
| 1.4 | El campo **Tech Stack** define lenguaje/framework con versiones exactas — ninguna omisión | ⬜ |
| 1.5 | El campo **Requirements** lista requerimientos numerados, determinísticos y testeables — no cualitativos | ⬜ |
| 1.6 | El campo **Expected Interface** está presente con **todos** los componentes públicos que los tests importarán | ⬜ |
| 1.7 | El campo **Current State** está en la posición correcta según el patrón elegido | ⬜ |
| 1.8 | El prompt usa estilo "freelance-brief" orientado al agente — no raw imperatives de sistema interno | ⬜ |

**Resultado Bloque 1:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 2 — Tech Stack & Compliance

| # | Verificación | Estado |
|---|---|---|
| 2.1 | El Tech Stack NO dice "Any" ni "your choice" — **100% específico** | ⬜ |
| 2.2 | {UI} Se especifica el framework frontend con versión exacta (React, Vue, Svelte, etc.) | ⬜ |
| 2.3 | Se especifica el runtime/lenguaje backend con versión exacta (Node.js, Python 3.x, Kotlin, Go, etc.) | ⬜ |
| 2.4 | Se especifica SQLite como base de datos (si aplica) — si no usa DB, marcar N/A | ⬜ |
| 2.5 | Se especifica el método de autenticación (JWT, API tokens, OAuth, sesiones, o N/A si no aplica) | ⬜ |
| 2.6 | Las versiones de **todas** las dependencias son explícitas (no "latest") | ⬜ |
| 2.7 | Todas las versiones declaradas son factualmente correctas y compatibles entre sí — **cualquier error mayor = FAIL automático; máx 2 errores menores permitidos** | ⬜ |
| 2.8 | No se listan librerías de terceros que requieran setup externo (API keys, licencias, servicios cloud) | ⬜ |
| 2.9 | {UI} **Asset Compliance:** no se mencionan assets de Unsplash — fuentes visuales son exclusivamente Google Fonts, Lucide, Heroicons o Pexels. Para tasks sin UI, marcar N/A | ⬜ |
| 2.10 | **Meta-Data Exclusion:** el prompt NO incluye información de budget, timelines, referencias internas de workflow ni task IDs — son datos de meta omitibles | ⬜ |

**Resultado Bloque 2:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 3 — Expected Interface

> Cada componente público DEBE tener los 6 campos obligatorios + validaciones específicas por lenguaje. La interfaz es el contrato entre los tests y la implementación — su definición determina la calidad de todo el pipeline de verificación.

### Campos requeridos por componente:

| Campo | Requerido | Descripción |
|---|---|---|
| **Path** | ✅ | Ruta exacta del archivo dentro de la estructura del repositorio |
| **Name** | ✅ | Nombre de clase/función/método/endpoint sin ambigüedad |
| **Type** | ✅ | `class` / `function` / `method` / `interface` / `data class` / `API Endpoint` / `CLI command` |
| **Input** | ✅ | Parámetros con tipos explícitos — `N/A` si no hay input |
| **Output** | ✅ | Tipo de retorno con descripción del comportamiento observable — HTTP status codes para endpoints, exit codes para CLIs |
| **Description** | ✅ | Qué hace en 1-2 oraciones, enfocado en comportamiento externo y side effects documentables |

### Checklist de validación:

| # | Verificación | Estado |
|---|---|---|
| 3.1 | Cada componente listado tiene los **6 campos completos** — ningún campo vacío, "N/A" justificado | ⬜ |
| 3.2 | No se documentan helper functions internas (solo interfaces públicas que los tests importarán) | ⬜ |
| 3.3 | No se documentan campos de librerías de terceros como si fueran interfaces propias | ⬜ |
| 3.4 | **Todos** los componentes que los tests van a importar están documentados — ningún import de test sin correspondencia en la interfaz | ⬜ |
| 3.5 | {TS} Componentes que usan herencia o implementan interfaces tienen documentado `extends` / `implements` donde aplica. Para otros lenguajes, verificar equivalente (interfaces, traits, abstract classes) — **omisión = FAIL** | ⬜ |
| 3.6 | **Implementation Agnosticism:** las descripciones NO filtran lógica interna, estructura de helpers, ni decisiones de modularización — solo comportamiento observable desde fuera | ⬜ |
| 3.7 | **Minimal Surface Area:** solo se documenta el entry point primario de cada módulo; no se listan sub-rutas internas ni detalles de implementación como interfaces públicas | ⬜ |
| 3.8 | **Strict Typing:** todos los tipos de Input y Output son explícitos y sin ambigüedad — no hay `any`, `object` sin tipar, `dict` genérico sin estructura, ni tipos vagos que puedan causar pipelines flaky | ⬜ |
| 3.9 | **Solution Leakage Guard:** ningún campo de interfaz expone nombres de funciones privadas, estructura de helpers internos, o archivos no mandatados por el seed task — **1 leakage = FAIL** | ⬜ |
| 3.10 | **Test-Import Cross-Check:** cada import de los archivos de test tiene correspondencia directa en la Expected Interface — sin imports huérfanos que referencien algo no documentado | ⬜ |

**Resultado Bloque 3:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 4 — Linguistic Determinism Audit

> Audit obligatorio basado en la Determinism Rule (guia1). El prompt debe funcionar como una máquina de estados: un solo camino de ejecución predecible. La presencia de lenguaje no-determinístico en contexto de implementación invalida el prompt completo.

### 4A — Términos prohibidos (presencia en contexto de implementación = FAIL automático)

Escanear el prompt completo por estos términos:

| Término prohibido | Motivo | Presente |
|---|---|---|
| `"or"` (como alternativa de implementación) | Introduce bifurcación no-determinística | ⬜ |
| `"alternatively"` | Bifurcación explícita | ⬜ |
| `"either X or Y"` | Alternativa de diseño | ⬜ |
| `"recommended"` | Sugerencia, no mandato | ⬜ |
| `"should"` (sin ser "MUST") | Modal débil | ⬜ |
| `"you can"` | Opción discrecional | ⬜ |
| `"you may"` | Permiso, no instrucción | ⬜ |
| `"etc."` | Lista abierta, ambigua | ⬜ |
| `"something like"` | Vaguedad intencional | ⬜ |
| `"relevant technologies"` | Tech stack no especificado | ⬜ |
| `"If you want"` | Condicional discrecional | ⬜ |
| `"feel free to"` | Permiso no-determinístico | ⬜ |
| `"it's up to you"` | Decisión delegada al agente | ⬜ |

> **Criterio:** 0 ocurrencias en contexto de decisión de implementación. Ocurrencias en ejemplos, nombres de campos propios del dominio o citas del seed son aceptables con justificación explícita.
>
> **Nota sobre "or" del seed original:** Si el seed usa "or" (ej: "SQLite or JSON"), el engineer DEBE elegir una opción en el prompt reescrito (Determinism Rule). La presencia de "or" como alternativa en el prompt reescrito sigue siendo FAIL independientemente del src original.

### 4B — Verificación de phrasing imperativo

| # | Verificación | Estado |
|---|---|---|
| 4.1 | Los requerimientos usan verbos imperativos: `MUST`, `SHALL`, `Implement`, `Create`, `Generate`, `Return` — no modales débiles | ⬜ |
| 4.2 | No aparecen frases como "You should", "It's recommended", "If you want", "Feel free to" en los Requirements | ⬜ |
| 4.3 | Las restricciones de seguridad/acceso usan `MUST NOT` o `is strictly forbidden` — no "avoid" ni "try not to" | ⬜ |
| 4.4 | Los Requirements son **positivamente formulados** (qué DEBE hacer) vs negativamente abiertos (qué evitar) | ⬜ |

**Resultado Bloque 4:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 5 — Requirements Quality & Anti-Overfitting Audit

> Los Requirements son el contrato funcional. Deben ser testeables, determinísticos, y libres de Implementation Leakage. Un Requirement que dicta la solución interna destruye el test de razonamiento del agente.

### 5A — Task Overfitting & Solution Leakage

| # | Verificación | Estado |
|---|---|---|
| 5.1 | Los Requirements definen **comportamiento observable** — no dictan nombres de funciones privadas, helper logic, ni estructura de modularización interna | ⬜ |
| 5.2 | Ningún Requirement impone una arquitectura específica de archivos no mandatada por el seed task (ej: "crear un archivo authHelper.ts" sin que el seed lo requiera) | ⬜ |
| 5.3 | Los Requirements **no exponen** nombres de variables, constantes, o implementación de algoritmos específicos — solo resultados | ⬜ |
| 5.4 | **Over-Specificity Threshold:** menos del 10% de los Requirements imponen detalles de implementación no presentes en el seed task — **>10% = FAIL** (umbral actualizado según Guía 4, Mar 25 2026) | ⬜ |
| 5.5 | Los Requirements cualitativos (UI polish, animaciones, UX aesthetics) están **segregados como "Rubric Only"** — NO aparecen como Requirements testeables via unit tests | ⬜ |

### 5B — Dual-Layer Coverage (Tests + Rubrics)

> Cada requerimiento DEBE estar cubierto por al menos una capa de verificación. Ningún "orphan requirement" es aceptable.

| # | Verificación | Estado |
|---|---|---|
| 5.6 | **Backend/lógica** → cubierto por **Unit Tests** (F2P) | ⬜ |
| 5.7 | {UI} **Frontend/UX/cualitativo** → cubierto por **Rubrics**. Para tasks sin UI, marcar N/A | ⬜ |
| 5.8 | Ningún requerimiento queda sin asignación a al menos una capa (Tests o Rubrics) — 0 "orphan requirements" | ⬜ |
| 5.9 | El split de asignación es coherente: no se asignan a tests features que solo pueden verificarse visualmente, ni a rubrics features que tienen output programáticamente computable | ⬜ |

**Resultado Bloque 5:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 6 — Requirements Coverage

> Cada requerimiento del task description original debe estar en el prompt reescrito.
>
> **Umbral de aprobación:** ≥ 95% cubiertos y testeables. Más de 1 faltante = FAIL (ajustar según N total de requerimientos).

### Checklist de requerimientos de esta tarea:

> **Instrucción:** Reemplaza esta tabla con los requerimientos de TU tarea. Copia los requerimientos del seed task original y verifica que cada uno esté presente y sea testeable en el prompt reescrito.

| # | Requerimiento del seed original | Presente en prompt reescrito | Testeable |
|---|---|---|---|
| R01 | *(copiar req 1 del seed)* | ⬜ | ⬜ |
| R02 | *(copiar req 2 del seed)* | ⬜ | ⬜ |
| R03 | *(copiar req 3 del seed)* | ⬜ | ⬜ |
| R04 | *(copiar req 4 del seed)* | ⬜ | ⬜ |
| R05 | *(copiar req 5 del seed)* | ⬜ | ⬜ |
| R06 | *(copiar req 6 del seed)* | ⬜ | ⬜ |
| R07 | *(copiar req 7 del seed)* | ⬜ | ⬜ |
| R08 | *(copiar req 8 del seed)* | ⬜ | ⬜ |
| R09 | *(copiar req 9 del seed)* | ⬜ | ⬜ |
| R10 | *(copiar req 10 del seed)* | ⬜ | ⬜ |
| R11 | *(copiar req 11 del seed)* | ⬜ | ⬜ |
| R12 | *(copiar req 12 del seed)* | ⬜ | ⬜ |
| R13 | *(copiar req 13 del seed)* | ⬜ | ⬜ |
| R14 | *(copiar req 14 del seed)* | ⬜ | ⬜ |
| R15 | *(copiar req 15 del seed)* | ⬜ | ⬜ |
| R16 | *(copiar req 16 del seed)* | ⬜ | ⬜ |
| R17 | *(copiar req 17 del seed)* | ⬜ | ⬜ |

**Total cubiertos: ___ / ___**

> **Regla del 5%:** Un gap de cobertura > 5% en requerimientos principales de backend = **Major Insufficient Coverage** = FAIL automático.
>
> **Regla de distinción Backend vs. Frontend:** Requerimientos de lógica backend DEBEN estar cubiertos por Unit Tests. Requerimientos de presentación pueden cubrirse por Rubrics. Cualquier backend req sin cobertura de tests = FAIL.

**Resultado Bloque 6:** ⬜ PASS / ⬜ FAIL

---

## BLOQUE 7 — Validaciones Críticas de Ejecución

| # | Verificación | Estado |
|---|---|---|
| 7.1 | No hay instrucciones contradictorias en el prompt — **1 contradicción = FAIL** | ⬜ |
| 7.2 | No se menciona descarga de datasets externos ni live API en runtime | ⬜ |
| 7.3 | El prompt NO incluye instrucciones de unit tests ni rubrics (son artefactos separados al prompt) | ⬜ |
| 7.4 | Current State dice claramente que es greenfield (desde cero) | ⬜ |
| 7.5 | No hay lógica imposible de implementar dentro de un entorno Ubuntu 22.04 + Docker | ⬜ |
| 7.6 | **Factual Precision:** versiones de librerías, nombres de paquetes y comportamientos técnicos declarados son verificablemente correctos — **máx 2 errores menores; 0 errores mayores**. Verificar con gestor de paquetes del stack (`npm`, `pip`, `gradle`, `cargo`, `go mod`, etc.) | ⬜ |
| 7.7 | La solución completa corre en entorno local sin dependencias de red externas (servidor solo en `127.0.0.1`) | ⬜ |
| 7.8 | {UI} **UI Reachability:** toda funcionalidad definida en los Requirements es accesible a través de la UI del frontend — no solo via llamada directa a API o manipulación de URL. Para tasks sin UI, marcar N/A | ⬜ |
| 7.9 | **Startup Contract:** el startup debe ser auto-contenido sin pasos manuales previos (ej: `npm run dev`, `python -m mylib`, `./gradlew run`, `go run .` — sin `npm install` manual, sin setup de DB manual, sin variables de entorno obligatorias no documentadas) | ⬜ |
| 7.10 | **Error/Success Contract:** los entry points documentados declaran códigos de retorno explícitos — HTTP status codes para APIs (200, 201, 400, 401, 403, 404, 422), exit codes para CLIs (0, 1), o tipos de retorno con comportamiento observable para librerías. No se acepta "returns data" sin especificar el código/caso | ⬜ |

**Resultado Bloque 7:** ⬜ PASS / ⬜ FAIL

---

## RESULTADO FINAL

| Bloque | Descripción | Estado |
|---|---|---|
| Bloque 0 — Pre-Validación | Feasibility, Seed Fidelity, Internal Ref Cleanup | ⬜ PASS / ⬜ FAIL |
| Bloque 1 — Estructura | Pattern A/B, campos obligatorios, freelance-brief style | ⬜ PASS / ⬜ FAIL |
| Bloque 2 — Tech Stack & Compliance | Versiones, compatibilidad, Asset Compliance, meta-data exclusion | ⬜ PASS / ⬜ FAIL |
| Bloque 3 — Expected Interface | 6 campos + strict typing + impl agnosticism + solution leakage + test-import cross-check | ⬜ PASS / ⬜ FAIL |
| Bloque 4 — Linguistic Determinism | Términos prohibidos (13) + phrasing imperativo | ⬜ PASS / ⬜ FAIL |
| Bloque 5 — Requirements Quality | Anti-Overfitting + Solution Leakage + Dual-Layer Coverage | ⬜ PASS / ⬜ FAIL |
| Bloque 6 — Requirements Coverage | N/N requerimientos + umbral 95% + backend/frontend split | ⬜ PASS / ⬜ FAIL |
| Bloque 7 — Validaciones Críticas | Contradicciones, factual, greenfield, local, UI Reachability, Contracts | ⬜ PASS / ⬜ FAIL |

### ✅ LISTO PARA FASE 2 — todos los bloques en PASS
### ❌ REGRESA A REVISAR — uno o más bloques en FAIL

---

## SEVERITY REFERENCE

| Tipo | Condición | Impacto |
|---|---|---|
| **FAIL automático** | Instrucción imposible, contradicción lógica, término prohibido en contexto de implementación, gap de cobertura >5%, error factual mayor, 1 miss en instrucción explícita del prompt | Rechazar prompt completo |
| **FAIL acumulativo** | 2+ errores menores en Tech Stack, 2+ requerimientos sin cubrir, >10% requirements con over-specificity (umbral v3.1), 2+ leakages de solución | Rechazar prompt |
| **WARNING** | 1 error menor de factual precision, 1 ítem de interfaz sin campo específico del lenguaje, 1 requirement sin split asignado, 1 término de framing negativo | Corregir antes de avanzar — no bloquea si está aislado |

---

## GUÍA DE REFERENCIA RÁPIDA — Qué NO hacer (Anti-Patterns)

> Esta sección actúa como referencia para el engineer que escribe el prompt. Un prompt que incurre en cualquier anti-pattern listado aquí resultará en FAIL en el bloque correspondiente.

| Anti-Pattern | Ejemplo incorrecto | Corrección |
|---|---|---|
| **Task Overfitting** | "Create `authHelper.ts` with function `validateToken()`" | "Implement JWT validation. Token must be verified on every protected route." |
| **Solution Leakage** | "The `UserService` class must call `memberRepository.findByEmail()`" | "User service must return member profile given a valid email — 404 if not found." |
| **Modal débil** | "You should validate the token" | "The system MUST validate the JWT token on every protected endpoint." |
| **Bifurcación** | "Use SQLite or JSON files" | "Use SQLite via better-sqlite3." |
| **Stacked Constraints** | "Brief + child-friendly + no letter e + TypeScript only" | Máx 2 restricciones solapadas sobre el mismo elemento. |
| **Internal Reference** | "Per CB-147, the member ID..." | Eliminar toda referencia interna — redactar en términos de dominio. |
| **Unsplash** | `<img src="unsplash.com/...">` | Usar solo Lucide, Heroicons, Google Fonts, o Pexels. |
| **UI Bloqueado** | "Admin can filter by date via `GET /api/reports?date=...`" | "Admin can filter reports by date range using a date picker in the dashboard." |
| **Seed Scope Creep** | Añadir módulo de "donaciones online con Stripe" si el seed no lo incluye | Toda funcionalidad nueva debe trazar origen directo al seed task. |

---

## NOTAS / ISSUES ENCONTRADOS

```
(anota aquí el bloque, número de ítem y descripción del problema)

Formato: [BLOQUE X] X.Y — descripción técnica del issue → acción correctiva recomendada

Ejemplos:
[BLOQUE 4] 4A — "or" detectado en Req 5: "weekly or biweekly" → reescribir como enum explícito: "FREQUENCY: 'weekly' | 'biweekly' — MUST be declared at group creation"
[BLOQUE 3] 3.5 — AuthRouter no documenta si implementa alguna interfaz → añadir campo correspondiente
[BLOQUE 5] 5.1 — Req 9 dicta nombre de helper interno "useRSVPHandler" → reescribir como comportamiento: "RSVP state MUST persist per event per member"
[BLOQUE 7] 7.8 — Req 14 solo describe el endpoint API, sin verificar acceso vía UI → añadir "accessible via Announcements panel in staff dashboard"
```
