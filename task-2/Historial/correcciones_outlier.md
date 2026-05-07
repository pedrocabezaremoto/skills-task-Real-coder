# 🔄 Bucle de Corrección Outlier - Tarea 2

Este archivo es el canal de comunicación técnica entre **Pepito (Antigravity)** y **Opencode**. Aquí se registran los feedbacks de Outlier y las instrucciones precisas para las iteraciones del proyecto.

---

## 🚩 Intento #0 — Auditoría Previa (Pre-Submission)
**Fecha:** 2026-05-07
**Estado:** 🟡 REVISIÓN INTERNA RECOMENDADA

### 1. Feedback / Análisis de Pepito
Antes de subir el prompt a Outlier, he identificado 3 puntos críticos que podrían causar un rechazo ("Rebotado") debido a la falta de fidelidad exacta con el *seed task*:

*   **Omisión de variables financieras:** El seed menciona "Operating Costs" y "Additional Services", pero no están definidos en el prompt.
*   **Fórmulas incompletas:** Falta la fórmula explícita del "Profit Margin".
*   **Redondeos faltantes:** El seed pide redondeo a **1 decimal** para Conversion Rate, Profit Margin y Vendor Rating Average.

### 2. Instrucciones para el Próximo Agente (Opencode / Pepito)
- [x] **Ajuste en `prompt.md` (Requirements):** Añadir que el Revenue incluye "Additional Services".
- [x] **Ajuste en `prompt.md` (Financials):** Especificar la fórmula de Profit Margin y los redondeos a 1 decimal.
- [x] **Ajuste en `prompt.md` (Expected Interface):** Actualizar los modelos de datos en `src/types/index.ts` para incluir `operatingCosts` y `additionalServices`.
- [x] **Validación Final:** Ejecutar el `promptchecker.md` una vez aplicados estos cambios.

---

## 🚩 Intento #1 — Feedback Real de Outlier
**Fecha:** 2026-05-07
**Estado:** 🔴 REBOTADO (Fail en Determinismo y Lógica)

### 1. Feedback Original de Outlier
- **Determinismo:** Fallo crítico por usar "at least" (unbounded scope) y "or" (opcionalidad en componentes visuales: table or kanban, bar or table).
- **Lógica:** Falta de trazabilidad de errores, falta de mecanismo de cron/scheduler para flagging automático, y falta de estrategia de concurrencia.
- **Fidelidad (Seed Alignment):** Faltan paquetes de contrato, info de contacto de vendors, tipos específicos de eventos de línea de tiempo y fórmulas exactas de redondeo (1 decimal).

### 2. Análisis Técnico de Pepito
Outlier ha detectado que el prompt permite que el LLM "elija" el diseño, lo cual está prohibido. Además, las omisiones de fórmulas financieras que detectamos en el Intento #0 han sido penalizadas.
Lo más complejo es el "Automatic Flagging": en un frontend puro, debemos especificar que el chequeo se hace **on-load** comparando la fecha actual con la `due_date`.

### 3. Instrucciones Directas para OPENCODE
- [x] **Determinismo:** Reemplazar todos los "at least" por "exactly".
- [x] **UI Fix:** Eliminar opciones. Usar "Kanban board" para Pipeline y "Bar chart" para Revenue.
- [x] **Seed Fidelity:**
    - Añadir tipos de evento: `ceremony, cocktail hour, dinner, first dance, cake cutting`.
    - Añadir paquetes: `ceremony, reception, all-inclusive` (sin "or").
    - Añadir campo `contactInfo` a Vendors.
    - Especificar redondeo a **1 decimal** en: Conversion Rate, Profit Margin, YoY Growth y Vendor Rating Average.
- [x] **Lógica de Negocio:**
    - Incluir fórmula de Revenue: `Venue Fee + Additional Services`.
    - Incluir fórmula de Profit: `(Revenue - Operating Costs) / Revenue * 100`.
- [x] **Mecanismo de Flagging:** Especificar en el `calculations.ts` que el status `overdue` se calcula dinámicamente al cargar comparando `current_date` con `due_date + 7 days`.
