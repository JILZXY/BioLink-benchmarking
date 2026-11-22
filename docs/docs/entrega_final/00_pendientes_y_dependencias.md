# Pendientes y Dependencias del Proyecto BioLink (`00_pendientes_y_dependencias.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Ubicación:** `biolink-benchmarking/docs/docs/entrega_final/00_pendientes_y_dependencias.md`  
**Alcance exclusivo:** Repositorios `biolink-backend`, `biolink-frontend` y `biolink-benchmarking`.

Este documento clasifica las actividades pendientes identificadas durante la auditoría según su dependencia técnica real, evitando mezclar tareas ya ejecutables con etapas condicionadas al cierre visual del frontend, integración completa o despliegue.

---

## 1. Actividades que pueden realizarse ahora (sin esperar cambios de código o despliegue)

1. **Actualizar la documentación histórica desactualizada en `biolink-benchmarking/`:**
   - Corregir `biolink-benchmarking/docs/docs/README.md`, `architecture.md`, `repository_structure.md`, `deployment.md`, `benchmarking.md` y `03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md` para retirar el estatus de *"pendientes"* en el diseño físico, `biolink-backend`, `biolink-frontend` y la campaña de 120 minutos.
   - Actualizar la Sección F de `biolink-benchmarking/README.md` reflejando que la campaña sobre `1,000`, `10,000` y `50,000` afirmaciones ya fue ejecutada (`20261121T050159Z_campaign_all_volumes_20261120.md`).
   - Revisar la codificación de caracteres de `biolink-benchmarking/reports/20261121T050159Z_campaign_all_volumes_20261120.md` (presenta signos `?` por pérdida de tildes/símbolos en su escritura original) para la síntesis en la memoria académica, sin alterar los CSV/JSON crudos.
2. **Redactar el informe comparativo y los ADRs definitivos en `entrega_final/`:**
   - Consolidar en `entrega_final/` las tablas comparativas reales (`1k`, `10k`, `50k`) extraídas de `results/summaries/*.json` y `reports/*_compare_*.md` justificando formalmente la elección de **PostgreSQL 18.7**, **MongoDB 8.0.38** y **Neo4j 2026.10.2**.
   - Documentar con evidencia técnica las dos lecciones de ingeniería derivadas del benchmark y ya aplicadas en `biolink-backend`:
     1. El índice parcial cubriente `idx_assertion_published_r2_covering` ante la degradación `R2` en PostgreSQL a `50k`.
     2. Los parámetros transaccionales `NEO4J_TX_TOTAL_MAX` / `NEO4J_TX_MAX` y borrado por lotes (`1000 ROWS`) ante el `MemoryPoolOutOfMemoryError` de Neo4j a `50k`.
   - Documentar el diseño físico implementado en `biolink-backend/database/` (Etapa 4), el desarrollo del backend y worker (Etapas 5–6) y el estado actual del frontend (Etapa 7).
3. **Documentar limitaciones ya observadas del alcance actual (V1):**
   - Registrar explícitamente que `GET /api/v1/sources/{source_id}` no cuenta con endpoint de listado general (`GET /api/v1/sources`) y que `biolink-frontend/app/interactions/page.tsx` consulta interacciones globales reutilizando `OP-05` (`GET /api/v1/network/subgraph`).
4. **Ordenar cambios locales pendientes en `biolink-frontend` (decisión de control de versiones):**
   - Evaluar e integrar (o descartar según criterio del proyecto) los cambios locales detectados por `git status` en `biolink-frontend`: `M next.config.ts` (`allowedDevOrigins`), `M README.md` y el archivo sin trackear `AGENTS.md` autogenerado por Next.js 16 en desarrollo.

---

## 2. Actividades que dependen de terminar y validar el Frontend

1. **Validación final del diseño visual y de experiencia de usuario:**
   - Confirmar si la paleta archival/botánica (`styles/globals.css`), tipografía, navegación y disposición actual de vistas en `biolink-frontend` se aceptan como versión definitiva o requieren ajustes gráficos/UX.
2. **Re-verificación de calidad frontend tras modificaciones definitivas:**
   - Volver a ejecutar `npm run typecheck`, `npm run lint`, `npm test` (`Vitest` + `axe-core`), `npm run build` y `npm run test:e2e` (`Playwright` en escritorio y móvil) sobre la versión congelada del frontend (incluyendo el ajuste en `next.config.ts` o posteriores).
3. **Captura de evidencias visuales definitivas para la documentación académica:**
   - Generar capturas finales de pantallas públicas (`OP-01`–`OP-08`, `OP-15`, grafo Cytoscape.js + tabla accesible, comparación Montes Azules vs. Playón de la Gloria) y de la consola RBAC (`/administration`), una vez cerrado el diseño definitivo.
4. **Empaquetado opcional del frontend en contenedor:**
   - Definir si `biolink-frontend` requerirá su propio `Dockerfile` (actualmente inexistente en el repositorio, a diferencia de `biolink-backend`) antes de pasar al despliegue.

---

## 3. Actividades que dependen de integrar y probar el sistema completo (Backend + Frontend + 3 Motores reales)

1. **Ejecución y registro formal de la suite completa de pruebas de `biolink-backend`:**
   - Correr y guardar bitácora de `pytest -m "not live"` (42 pruebas) y `pytest -m live` (2 pruebas contra PostgreSQL, MongoDB y Neo4j en Docker: `test_live_all_nine_public_operations_with_scientific_fixture` y `test_live_admin_workflow_rbac_outbox_and_reconciliation`) asegurando ausencia de contenedores simultáneos de `biolink-benchmarking`.
2. **Pruebas end-to-end reales sin mocks (`biolink-frontend` ↔ `biolink-backend` ↔ 3 BD + `OutboxProjectionWorker`):**
   - Actualmente `biolink-frontend/tests/e2e/biolink.spec.ts` intercepta llamadas con `page.route`. Falta ejecutar y documentar una batería de aceptación end-to-end en vivo que valide de punta a punta:
     - Consultas públicas `OP-01`–`OP-08` y `OP-15` contra el `reference_seeder` real (verificando exclusión de `AST_SCI_DRAFT_001` y separación `LOC_RBMA_SOUTH` vs. `LOC_PDLG`).
     - Flujo curatorial completo en `/administration`: login RBAC (`curador1@biolink.org` / `revisora1@biolink.org`), registro de lote (`OP-09`), normalización (`OP-10`), creación (`OP-11`), aprobación (`OP-12` → `PUBLISHED` con `projection_status = PENDING` → transición a `SYNCED` tras actuar `OutboxProjectionWorker` en Neo4j), versión de expediente en MongoDB (`OP-13`) y consulta de procedencia (`OP-14`).
     - Prueba de resiliencia y reconciliación (`POST /api/v1/admin/reconcile`) simulando caída y recuperación de Neo4j desde la UI administrativa.
3. **Verificación empírica en PostgreSQL del índice `idx_assertion_published_r2_covering`:**
   - Capturar `EXPLAIN (ANALYZE, BUFFERS)` de la consulta `R2` (`OP-03`/`OP-05`) sobre `biolink-backend` para respaldar con evidencia directa la mitigación de la degradación detectada en el benchmark de `50,000` filas.

---

## 4. Actividades que dependen del despliegue (entorno objetivo / producción)

1. **Configuración de entorno productivo seguro (`APP_ENV=production`):**
   - Sustituir credenciales locales de ejemplo y `AUTH_SECRET_KEY`, habilitar `SESSION_COOKIE_SECURE=true` (exigido por `Settings` en `biolink-backend/src/biolink_backend/config/settings.py`) y ajustar `CORS_ALLOWED_ORIGINS` y `NEXT_PUBLIC_BIOLINK_API_BASE_URL` a los dominios finales HTTPS.
2. **Infraestructura de red, TLS y proxy inverso:**
   - Configurar terminación HTTPS frente a `biolink-backend` (`uvicorn`) y `biolink-frontend` (`next start` o build independiente), manteniendo los puertos de PostgreSQL, MongoDB y Neo4j aislados sin exposición pública.
3. **Persistencia, volúmenes y respaldos en servidor destino:**
   - Definir estrategia de respaldos para `postgresql_prod_data`, `mongodb_prod_data` y `neo4j_prod_data`, monitoreo de memoria dentro del presupuesto operativo y verificación de arranque automático de `OutboxProjectionWorker`.
4. **Pruebas de humo post-despliegue (`smoke` productivo):**
   - Validar `GET /api/v1/health/live`, `GET /api/v1/health/ready`, carga inicial del navegador sobre HTTPS y flujo de autenticación con cookie `HttpOnly` + `Secure`.
