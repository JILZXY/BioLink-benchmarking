# Auditoría del Estado Actual del Proyecto BioLink (`00_auditoria_estado_actual.md`)

**Fecha de corte de auditoría:** 21 de noviembre de 2026  
**Ubicación documental global verificada:** `biolink-benchmarking/docs/docs/` (directorio existente y confirmado en disco; el directorio destino `entrega_final/` se ubica dentro de esta ruta).  
**Alcance estricto:** Repositorios `biolink-backend`, `biolink-frontend` y `biolink-benchmarking`.  
*(Conforme a las directrices de alcance, no se utiliza, inspecciona ni documenta ningún otro repositorio fuera de estos tres).*

---

## 1. Resumen Ejecutivo y Estado de Control de Versiones

Los tres repositorios previstos por la arquitectura oficial orientada a servicios (**SOA**) ya existen físicamente, cuentan con código fuente funcional, esquemas/migraciones, pruebas automatizadas y evidencias empíricas de benchmarking ejecutadas. Sin embargo, la **documentación histórica previa** alojada en `biolink-benchmarking/docs/docs/` aún describe a `biolink-backend`, `biolink-frontend` y a la campaña completa de benchmarking como *"pendientes"*, generando un desfase documental respecto al código y resultados reales en disco.

| Repositorio | Rama Git | Último commit registrado | Estado del árbol de trabajo al momento de la auditoría | Madurez global observada |
|---|---|---|---|---|
| `biolink-backend` | `development` | `34c5c2c` (`chore(project): initialize backend packaging, env template, and locked dependencies`) | Limpio en archivos versionados; existe `.env` local (ignorado por Git) y `.venv/` local | **Implementado** (API REST v1, reglas de dominio, persistencia poliglota, Outbox Worker, scripts SQL/Mongo/Cypher y 44 pruebas) |
| `biolink-frontend` | `main` (`origin/main`) | `90b8a87` (`docs(frontend): add architecture, design system, accessibility and routing guides`) | Modificaciones locales sin commit: `M README.md`, `M next.config.ts` (`allowedDevOrigins`), `?? AGENTS.md` (autogenerado por Next.js 16 dev), además de `.env.local` ignorado por Git | **Implementado en arquitectura y flujos base** (sujeto a revisión final de diseño UI y pruebas E2E integrales sin mocks) |
| `biolink-benchmarking` | `development` | `1af5b77` (`results(benchmarking): salidas csv y mds utilizados`) | Árbol limpio respecto a Git; contiene `datasets/` sintéticos y artefactos en `results/` y `reports/` (y `.env` local ignorado) | **Implementado y campaña ejecutada** (6 motores evaluados en fixture + 1k/10k/50k; documentación `docs/docs/` desactualizada) |

---

## 2. Estructura Real de Carpetas y Módulos

### 2.1 `biolink-backend`
Monolito modular en Python sin ORM que concentra la API REST, reglas científicas, repositorios por paradigma, esquema físico de persistencia y worker asíncrono:

- `src/biolink_backend/main.py`: fábrica `create_app()`, ciclo `lifespan`, CORS restringido y metadatos OpenAPI v1 (`/api/v1/openapi.json`, `/api/v1/docs`, `/api/v1/redoc`).
- `src/biolink_backend/config/settings.py`: validación estricta con Pydantic Settings v2 (prohibición de `:latest`, longitudes mínimas de secretos, rechazo de comodín CORS `*` y verificación de tope de memoria `<= 3,072 MiB` en contenedores dentro del techo global de `4,096 MiB`).
- `src/biolink_backend/domain/`: `entities.py`, `vocabularies.py`, `value_objects.py` y `rules.py` (reglas puras del dominio sin dependencias de FastAPI ni drivers).
- `src/biolink_backend/application/`: `dto.py`, `ports.py` (`Protocol`) y servicios (`health_service.py`, `auth_service.py`, `public_query_service.py`, `admin_curation_service.py`).
- `src/biolink_backend/api/`: `dependencies.py`, `errors.py`, `middleware.py` (`RequestContextMiddleware`) y `v1/` con `router.py`, `schemas/` (`common.py`, `health.py`, `public_queries.py`, `admin_curation.py`) y `endpoints/` (`health.py`, `auth.py`, `taxa.py`, `interactions.py`, `network.py`, `sources.py`, `occurrences.py`, `admin.py`).
- `src/biolink_backend/infrastructure/`: `manager.py` (`DatabaseConnectionManager`), `postgresql.py`, `mongodb.py`, `neo4j.py` y `reference_seeder.py` (`apply_reference_fixture`).
- `src/biolink_backend/repositories/`: consultas nativas separadas en `relational/` (`health_repository.py`, `auth_repository.py`, `public_catalog_repository.py`, `admin_curation_repository.py`, `outbox_repository.py`), `document/` (`health_repository.py`, `public_dossier_repository.py`, `admin_dossier_repository.py`) y `graph/` (`health_repository.py`, `public_network_repository.py`, `projection_repository.py`).
- `src/biolink_backend/security/`: `passwords.py` (PBKDF2-HMAC-SHA256), `tokens.py` (SHA-256 sobre tokens opacos) y `rbac.py`.
- `src/biolink_backend/shared/`: `exceptions.py`, `ids.py`, `logging.py` (JSON estructurado con enmascaramiento de credenciales) y `time.py` (fechas parciales `YYYY`, `YYYY-MM`, `YYYY-MM-DD`).
- `src/biolink_backend/workers/outbox_worker.py`: proceso independiente `OutboxProjectionWorker` con `FOR UPDATE SKIP LOCKED`.
- `database/`: scripts físicos propios del backend para PostgreSQL, MongoDB y Neo4j.
- `contracts/openapi-v1.json`: contrato OpenAPI 3.1.0 exportado.
- `tests/`: 11 archivos de pruebas (`test_*.py`) + `conftest.py`.
- `docs/`: `architecture.md`, `configuration.md`, `database_connections.md`, `development.md`, `security.md`.
- Despliegue/empaquetado: `Dockerfile`, `docker-compose.yaml`, `pyproject.toml`, `requirements.lock`, `.env.example`, `README.md`.

### 2.2 `biolink-frontend`
Cliente web desacoplado en Next.js App Router (TypeScript estricto) sin drivers ni credenciales de bases de datos:

- `app/`: rutas App Router (`layout.tsx`, `page.tsx`, `robots.ts`, `taxa/page.tsx`, `taxa/[taxonId]/page.tsx`, `interactions/page.tsx`, `interactions/[assertionId]/page.tsx`, `networks/page.tsx`, `localities/compare/page.tsx`, `sources/page.tsx`, `sources/[sourceId]/page.tsx`, `occurrences/page.tsx`, `administration/layout.tsx`, `administration/page.tsx`).
- `components/`:
  - `layout/`: `Header.tsx`, `Footer.tsx`, `Navigation.tsx`.
  - `ui/`: `DataTable.tsx`, `EmptyState.tsx`, `ErrorMessage.tsx`, `FilterBar.tsx`, `FormField.tsx`, `Modal.tsx`, `Pagination.tsx`, `SearchBar.tsx`, `Skeleton.tsx`, `StatusBadge.tsx`.
  - `domain/`: `BibliographicReference.tsx`, `EvidencePanel.tsx`, `HomeHeroSearch.tsx`, `ScientificName.tsx`, `SourceInfoCard.tsx`, `TaxonCard.tsx`.
- `features/`: `taxonomy/` (`TaxonSearchFeature.tsx`, `TaxonDetailFeature.tsx`), `interactions/` (`InteractionsExplorerFeature.tsx`, `InteractionDetailFeature.tsx`), `networks/` (`NetworkExplorerFeature.tsx`, `CytoscapeNetworkCanvas.tsx`, `AccessibleNetworkTable.tsx`), `localities/` (`LocalityComparisonFeature.tsx`), `sources/` (`SourceDetailFeature.tsx`), `occurrences/` (`OccurrencesExplorerFeature.tsx`), `administration/` (`AdminLoginForm.tsx`, `AdminWorkspaceFeature.tsx`).
- `lib/`: `api/` (`client.ts`, `public-api.ts`, `admin-api.ts`), `formatting/scientific.ts`, `validation/query-params.ts`.
- `hooks/`: `useAsyncQuery.ts`, `useAuthSession.ts`.
- `types/openapi.ts` y `contracts/openapi-v1.json`: tipos 1:1 y copia idéntica del contrato del backend.
- `styles/globals.css`, `eslint.config.mjs`, `vitest.config.mts`, `playwright.config.ts`, `next.config.ts`, `postcss.config.mjs`, `tsconfig.json`, `package.json`, `package-lock.json`, `.env.example`.
- `tests/`: `accessibility.test.tsx`, `components.test.tsx`, `features.test.tsx`, `sync-states.test.tsx`, `setup.ts` y `e2e/biolink.spec.ts`.
- `docs/`: `architecture.md`, `design-system.md`, `accessibility.md`, `routing.md`.
- **Ausencia observable:** no existe `Dockerfile` ni `docker-compose.yaml` propio en `biolink-frontend`.

### 2.3 `biolink-benchmarking`
Entorno autónomo de pruebas empíricas directas por driver/protocolo nativo:

- `src/biolink_bench/`: `cli.py`, `config.py`, `datasets/` (`bundle.py`, `scientific_fixture.py`, `synthetic_generator.py`), `drivers/` (`base.py`, `factory.py`, `relational/{mysql_adapter.py,postgresql_adapter.py,_common.py}`, `document/{mongodb_adapter.py,couchdb_adapter.py}`, `graph/{neo4j_adapter.py,memgraph_adapter.py}`), `metrics/` (`collector.py`, `docker_monitor.py`, `exporter.py`), `runners/` (`benchmark_runner.py`, `lifecycle.py`, `smoke_runner.py`) y `workloads/` (`base.py`, `relational.py`, `document.py`, `graph.py`).
- `docker/`: `compose.yaml` (6 perfiles secuenciales) y configuraciones en `relational/mysql/my.cnf`, `document/couchdb/local.ini`, y `README.md` auxiliares por motor.
- `datasets/`: `scientific_fixture/` (`biolink_scientific_fixture.json`, `manifest.json`), `manifests/` (3 manifiestos sintéticos `1000`, `10000`, `50000` con semilla `20261120`) y `synthetic/` (archivos JSONL reproducibles ignorados en `.gitignore`).
- `scripts/`: `engine_control.ps1`, `engine_control.sh`, `cleanup_all.ps1`, `validate_config.ps1`.
- `results/` (`raw/`, `summaries/`, `logs/`, `README.md`) y `reports/`.
- `docs/`: 6 documentos técnicos específicos del benchmark (`benchmark_protocol.md`, `data_strategy.md`, `engine_matrix.md`, `resource_limits.md`, `results_format.md`, `workloads.md`) + `docs/docs/` (documentación general de etapas 1 a 3 y arquitectura SOA).
- `tests/`: `conftest.py`, `test_config.py`, `test_connectivity_smoke.py`, `test_metrics_and_exporter.py`, `test_scientific_fixture.py`, `test_synthetic_generator.py`.

---

## 3. Tecnologías y Versiones Verificadas

### 3.1 `biolink-backend` (`pyproject.toml`, `requirements.lock`, `Dockerfile`, `docker-compose.yaml`)
- **Lenguaje / Runtime:** Python `>=3.12,<3.16`; imagen Docker `python:3.14-slim-bookworm`.
- **Framework Web / Validación / ASGI:** `fastapi==0.165.0`, `starlette==1.10.0`, `pydantic==2.14.4`, `pydantic-settings==2.16.3`, `uvicorn==0.54.0`, `httpx==0.28.1`.
- **Drivers nativos (sin ORM):** `psycopg==3.3.9` (`psycopg-binary==3.3.9`, `psycopg-pool==3.3.3`), `pymongo==4.20.1`, `neo4j==6.4.1`.
- **Motores Docker fijados en `docker-compose.yaml`:** `postgres:18.7`, `mongo:8.0.38`, `neo4j:2026.10.2-community`.
- **Pruebas:** `pytest==9.2.0`.

### 3.2 `biolink-frontend` (`package.json`, `README.md`)
- **Runtime:** Node.js `>=22.0.0 <25.0.0` (validado en entorno local con `v24.22.1`, según `README.md`).
- **Framework y Librerías:** `next@16.4.6` (App Router, Turbopack), `react@19.3.1`, `react-dom@19.3.1`, `typescript@5.9.3` (modo `strict`), `tailwindcss@4.3.5`, `@tailwindcss/postcss@4.3.5`, `cytoscape@3.35.0`.
- **Calidad y Pruebas:** `eslint@10.15.0` (`eslint-config-next@16.4.6`), `vitest@5.1.1`, `@testing-library/react@16.3.3`, `@testing-library/jest-dom@8.0.0`, `@testing-library/user-event@14.6.13`, `axe-core@4.14.1`, `jsdom@^26.1.0`, `@playwright/test@^1.51.1`.

### 3.3 `biolink-benchmarking` (`pyproject.toml`, `docker/compose.yaml`, `docs/engine_matrix.md`)
- **Lenguaje y dependencias:** Python `>=3.11,<3.16` (probado con `3.14.7`), `mysql-connector-python>=9.5.0` (probado `26.10.0`), `psycopg[binary]>=3.2.0`, `pymongo>=4.10.0`, `httpx>=0.27.0`, `neo4j>=5.26.0`, `python-dotenv>=1.0.1`, `pytest>=8.3.0`.
- **Seis motores evaluados en contenedores Docker (con digests `RepoDigests` verificados en `docs/engine_matrix.md`):**
  - Relacional: `mysql:8.4.13` (ajuste documentado respecto a la referencia inicial `8.4.12` inexistente en Docker Hub) y `postgres:18.7`.
  - Documental: `mongo:8.0.38` y `couchdb:3.5.3`.
  - Grafo: `neo4j:2026.10.2-community` y `memgraph/memgraph:3.14.0`.

---

## 4. Arquitectura Implementada

1. **Separación estricta de repositorios (SOA):**
   - `biolink-frontend` consume únicamente HTTP/REST (`/api/v1`) y no contiene drivers ni secretos de bases de datos.
   - El contrato `contracts/openapi-v1.json` en `biolink-backend` y `biolink-frontend` es **bit a bit idéntico** (SHA-256 verificado: `58587855B534CAB6AE53B081CE4067B78481E899CF4D8137E806F6E302F6A838`).
   - `biolink-benchmarking` opera de forma completamente autónoma sobre red `biolink_bench_net`, volúmenes propios y puertos desplazados (`3307`, `5433`, `27018`, `5985`, `7688`/`7475`, `7689`).
2. **Monolito modular y consistencia multi-modelo en `biolink-backend`:**
   - **PostgreSQL 18.7** actúa como fuente única de verdad (**SSOT**) para identidades, usuarios/sesiones, fuentes, ocurrencias, lotes, afirmaciones, revisiones, `outbox_event` y auditoría.
   - **Transactional Outbox Pattern (`OP-12`):** la aprobación (`PUBLISHED`) o retiro (`WITHDRAWN`) en PostgreSQL actualiza `interaction_assertion`, inserta `review_event`, `audit_log` y `outbox_event` (`PENDING`) en una sola transacción ACID; `OutboxProjectionWorker` consume lotes mediante `FOR UPDATE SKIP LOCKED`, ejecuta `MERGE` o `DETACH DELETE` idempotente en Neo4j y actualiza `projection_status` (`PENDING` → `SYNCED` o `FAILED` / `DEAD_LETTER`).
   - **Control documental versionado (`OP-13`):** actualiza `taxon_dossier` en MongoDB con control optimista sobre `document_version`, archivando antes el snapshot previo en `taxon_dossier_versions` y sincronizando `dossier_version` / `dossier_sync_status` en la tabla `taxon` de PostgreSQL.
3. **Presupuesto de memoria (4,096 MiB):**
   - `biolink-backend/docker-compose.yaml` limita `relational-db` a `768m`, `document-db` a `768m`, `graph-db` a `1024m`, `api` a `320m` y `worker` a `192m` (**3,072 MiB** combinados; `1,024 MiB` libres para el host).
   - En Neo4j se aplican límites transaccionales específicos (`NEO4J_HEAP_INITIAL=256m`, `NEO4J_HEAP_MAX=384m`, `NEO4J_PAGECACHE=256m`, `NEO4J_TX_TOTAL_MAX=256m`, `NEO4J_TX_MAX=64m`) motivados por el error `MemoryPoolOutOfMemoryError` detectado durante el benchmark a `50,000` afirmaciones.

---

## 5. Esquemas, Migraciones y Modelos de Bases de Datos (`biolink-backend/database/`)

### 5.1 PostgreSQL 18.7 (`biolink-backend/database/postgresql/`)
- **`migrations/001_create_schema.sql` (20 tablas):** `schema_migrations`, seguridad (`app_user`, `role`, `user_role`, `user_session`), fuentes (`source`, `source_version`), geografía (`locality` con `protected_status` y `spatial_validation_status`), taxonomía (`taxon`, `taxon_name`, `taxon_identifier`), evidencias/presencia (`interaction_type`, `evidence`, `occurrence`), flujo de afirmaciones (`interaction_assertion` con `CHECK` de estados y revisión, `assertion_evidence`, `review_event`), ingestión (`import_batch`, `import_record`) y sincronización/auditoría (`outbox_event`, `audit_log`).
- **`migrations/002_create_indexes.sql`:** índices búsquedas taxonómicas (`lower(name)`), índice parcial cubriente crítico **`idx_assertion_published_r2_covering`** (`ON interaction_assertion (locality_id, period_start, assertion_id) INCLUDE (actor_taxon_id, target_taxon_id, interaction_type_id, method_code, period_end) WHERE status = 'PUBLISHED'`), índices de vecindario publicados, sesión activa parcial e índice `idx_outbox_pending_polling`.
- **`migrations/003_admin_curation_extensions.sql`:** agrega columnas administrativas de lote (`endpoint_or_file`, `provider_version`), normalización (`verbatim_name`, `proposed_external_scheme`, `proposed_external_id`, `matching_rule`, `normalized_by`, `normalized_at`), versionado/proyección de afirmaciones (`aggregate_version`, `projection_status`, `last_projected_at`), versionado en `outbox_event` (`aggregate_version`, `payload_version`) y control documental en `taxon` (`dossier_version`, `dossier_sync_status`), actualizando `idx_outbox_pending_polling` a `WHERE status IN ('PENDING', 'FAILED')`.
- **`seeds/001_reference_fixture.sql`:** 3 usuarios/roles de referencia, 2 fuentes (`BAT2007`, `MAMMAL2016`), 2 localidades contrastantes (`LOC_RBMA_SOUTH`, `LOC_PDLG`) + 1 indeterminada (`LOC_LACANDONA_UNDETERMINED`), 32 taxones (11 animales, 21 plantas con rangos `SPECIES`, `GENUS`, `MORPHOSPECIES` y sinónimos/grafías originales), 21 afirmaciones `PUBLISHED`, 1 borrador `AST_SCI_DRAFT_001` (`DRAFT`) y 3 ocurrencias (`OCC_SCI_001`..`003`).

### 5.2 MongoDB 8.0.38 (`biolink-backend/database/mongodb/`)
- **Validadores `$jsonSchema` estrictos (`schemas/`):**
  - `taxon_dossier.schema.json`: exige `_id`, `document_type: "taxon_dossier"`, `schema_version`, `document_version`, `taxon_id`, `accepted_name`, `summary.description`, `sections` (`morphology`, `ecology`, `conservation`, `distribution`), `claims` con procedencia (`source_id`, `source_locator`) y `updated_at`.
  - `study_dossier.schema.json`: exige `source_id`, `research_question`, `sampling_design` (`methods`, `instruments`), `study_localities`, `focal_taxa`, `interpretation_limits` y `license_and_usage`.
  - `raw_source_record.schema.json`: exige `checksum`, `raw_payload` inmutable, `license_metadata` (`redistribution_permitted`, `full_text_stored`) y `transformation_metadata`.
- **Índices (`indexes/create_indexes.js`):** índices únicos sobre `taxon_dossier.taxon_id`, `study_dossier.source_id`, `taxon_dossier_versions (taxon_id, document_version)` y `raw_source_record (import_batch_id, external_record_id)`, más índices multikey sobre `claims`, `study_localities` y `focal_taxa`.

### 5.3 Neo4j Community 2026.10.2 (`biolink-backend/database/neo4j/`)
- **`constraints/001_create_constraints.cypher`:** 5 restricciones `UNIQUE` sobre `Taxon.taxon_id`, `InteractionAssertion.assertion_id`, `Locality.locality_id`, `Evidence.evidence_id` y `Source.source_id`.
- **`indexes/001_create_indexes.cypher`:** 6 índices sobre `Taxon(accepted_name)`, `Taxon(organism_group)`, `InteractionAssertion(interaction_type_code)`, `InteractionAssertion(period_start, period_end)`, `InteractionAssertion(method_code)` y `Locality(protected_status)`.
- **`projections/`:** `project_assertion.cypher` (`WHERE status = 'PUBLISHED'`, nodos y relaciones `ACTOR_IN`, `TARGETS`, `OBSERVED_AT`, `SUPPORTED_BY`, `CITED_FROM` mediante `MERGE`), `withdraw_assertion.cypher` (`DETACH DELETE` puntual y patrón por lotes `IN TRANSACTIONS OF 1000 ROWS`) y `reconcile_projections.cypher`.

---

## 6. Contratos OpenAPI y Estado Real de Funcionalidades

La especificación `contracts/openapi-v1.json` (OpenAPI 3.1.0) expone **26 rutas HTTP** bajo `/api/v1`:

| Grupo / Operación | Rutas implementadas en `biolink-backend` | Cobertura en `biolink-frontend` | Clasificación |
|---|---|---|---|
| **Salud** | `GET /api/v1/health/live`, `/ready`, `/health` | Indicador en pie/inicio (`getBackendHealth`) | **Implementado** |
| **Autenticación** | `POST /api/v1/auth/login`, `/logout`, `GET /me` | `AdminLoginForm` + `useAuthSession` (cookie `HttpOnly` + token en memoria) | **Implementado** |
| **`OP-01` Buscar taxones** | `GET /api/v1/taxa` | `/taxa` (`TaxonSearchFeature`) + buscador en `/` | **Implementado** |
| **`OP-02` Ficha de taxón** | `GET /api/v1/taxa/{taxon_id}` | `/taxa/[taxonId]` (`TaxonDetailFeature`) | **Implementado** |
| **`OP-03` Interacciones del taxón** | `GET /api/v1/taxa/{taxon_id}/interactions` | Integrado en `/taxa/[taxonId]` y `/interactions` | **Implementado** |
| **`OP-04` Detalle de interacción** | `GET /api/v1/interactions/{assertion_id}` | `/interactions/[assertionId]` (`InteractionDetailFeature`) | **Implementado** |
| **`OP-05` Subred documentada** | `GET /api/v1/network/subgraph` | `/networks` (`NetworkExplorerFeature` + Cytoscape.js + `AccessibleNetworkTable`) y listado global en `/interactions` | **Implementado** *(Nota: `/interactions` reutiliza `OP-05` por no existir un endpoint SQL separado `GET /api/v1/interactions`)* |
| **`OP-06` Comparar localidades** | `GET /api/v1/network/compare-localities` | `/localities/compare` (`LocalityComparisonFeature`) | **Implementado** |
| **`OP-07` Conectividad descriptiva** | `GET /api/v1/taxa/{taxon_id}/connectivity` | Panel descriptivo en `/taxa/[taxonId]` y `/networks` | **Implementado** |
| **`OP-08` Fuente y estudio** | `GET /api/v1/sources/{source_id}` | `/sources` y `/sources/[sourceId]` (`SourceDetailFeature`) | **Parcialmente implementado en catálogo general**: existe consulta directa por `source_id` (`BAT2007`, `MAMMAL2016`), sin endpoint de listado/paginación de fuentes (`GET /api/v1/sources`) |
| **`OP-15` Ocurrencias independientes** | `GET /api/v1/occurrences` | `/occurrences` (`OccurrencesExplorerFeature`) | **Implementado** |
| **`OP-09`..`OP-14` y Reconciliación** | 11 rutas `/api/v1/admin/*` (lotes, bandeja `import-records`, normalizar, crear/ver/enviar/revisar afirmaciones, actualizar `taxon_dossier`, procedencia, `/admin/reconcile`) | `/administration` (`AdminWorkspaceFeature` con 6 pestañas RBAC: `imports`, `normalization`, `assertions`, `review`, `dossiers`, `provenance`) | **Implementado** en backend y cliente administrativo |
| **Diseño UI definitivo, contenerización Frontend y despliegue en producción** | `biolink-backend` tiene `Dockerfile` + `docker-compose.yaml`; `biolink-frontend` solo dev/build local | Estética base en `styles/globals.css`, pendiente validación final de diseño UI, `Dockerfile` frontend y despliegue productivo | **Parcialmente implementado / Pendiente** |

**Estado del frontend respecto al diseño:** `biolink-frontend` cuenta con todas las páginas, componentes reutilizables (`Header`, `Footer`, `Navigation`, `SearchBar`, `FilterBar`, `TaxonCard`, `DataTable`, `StatusBadge`, `SourceInfoCard`, `BibliographicReference`, `EvidencePanel`, `EmptyState`, `Skeleton`, `ErrorMessage`, `Pagination`, `Modal`, `FormField`), formateo nomenclatural y cumplimiento programático WCAG 2.2 AA (`axe-core`); sin embargo, su diseño visual actual responde a la propuesta base implementada sin cierre definitivo formal ni paquete Docker propio.

---

## 7. Pruebas Existentes y Estado Observado

| Repositorio | Suite / Herramienta | Cobertura exacta en disco | Último estado observado / Observaciones |
|---|---|---|---|
| `biolink-backend` | `pytest` (`9.2.0`) | **44 casos recolectados** en 11 archivos: **42** pruebas unitarias/servicio/API/repositorio/seguridad/configuración + **2** pruebas `@pytest.mark.live` (`test_live_all_nine_public_operations_with_scientific_fixture` y `test_live_admin_workflow_rbac_outbox_and_reconciliation`) | Recolección validada (`44 tests collected in 0.97s`); se verificó en vivo el stack levantado contra los 3 motores (`health/ready` `200`, `compare-localities` `200`). *(Nota: las 44 pruebas pytest no se reejecutaron dentro de la auditoría actual).* |
| `biolink-frontend` | `Vitest` (`5.1.1`) + `axe-core` (`4.14.1`) + `@playwright/test` (`^1.51.1`) + `tsc`/`eslint` | **17 pruebas** en 4 archivos Vitest (`accessibility.test.tsx`: 3; `components.test.tsx`: 8; `features.test.tsx`: 4; `sync-states.test.tsx`: 2) + **5 especificaciones E2E** en `tests/e2e/biolink.spec.ts` (ejecutables en 2 proyectos: `desktop-chrome` y `mobile-chrome` = 10 corridas) | Las pruebas Vitest (17/17) y Playwright con mocks de ruta (`10/10`) pasaron antes de la edición local de `allowedDevOrigins` en `next.config.ts` y `README.md`. **No existe aún** suite E2E automatizada ejecutada sin mocks contra los 3 contenedores reales de `biolink-backend`. |
| `biolink-benchmarking` | `pytest` (`9.2.0`) | **16 casos recolectados** en 5 archivos: **10** pruebas unitarias (`test_config.py`: 4; `test_metrics_and_exporter.py`: 2; `test_scientific_fixture.py`: 1; `test_synthetic_generator.py`: 3) + **6** pruebas `@pytest.mark.live` parametrizadas por motor (`test_connectivity_smoke.py`) | Recolección validada (`16 tests collected in 6.53s`). Las validaciones de humo y benchmark completo generaron artefactos verificados en `results/` y `reports/`. |

---

## 8. Scripts, Datasets y Resultados del Benchmarking (`biolink-benchmarking`)

1. **Datasets y manifiestos verificados:**
   - `scientific_fixture_v1` (`datasets/scientific_fixture/biolink_scientific_fixture.json`, SHA-256 `f4b2ec408f31624723912ad0e34d82880d84c105f967d2b827619368494bed73`): 2 fuentes, 2 localidades, 32 taxones, 21 afirmaciones.
   - Tres volúmenes sintéticos (`SYNTHETIC_BENCHMARK`, semilla `20261120`, 16 archivos JSONL por volumen) respaldados por manifiestos SHA-256: `1,000`, `10,000` y `50,000` afirmaciones.
2. **Corridas y artefactos reales producidos el `2026-11-21`:**
   - **Fase de validación inicial (`01:38Z`–`01:45Z` UTC):** 15 corridas de `smoke` y `fixture` sobre los 6 motores (incluye registro de `KeyError: 'name'` en la primera corrida `smoke` de Memgraph `014334Z`, corregida en `014458Z`).
   - **Campaña completa multi-volumen (`04:34Z`–`05:01Z` UTC, duración `27 min 19 s` dentro del límite de `120 min`):** reportada en `reports/20261121T050159Z_campaign_all_volumes_20261120.md`. Ejecutó secuencialmente los 6 motores en `1,000`, `10,000` y `50,000` afirmaciones (18 corridas × 140 filas CSV = 5 iteraciones de calentamiento + 30 medidas por cada una de las 4 operaciones por modelo).
   - **Totales en disco:** `33` CSV en `results/raw/`, `33` JSON en `results/summaries/`, `33` logs en `results/logs/` y `44` reportes Markdown en `reports/`.
3. **Hallazgos técnicos clave obtenidos a `50,000` afirmaciones (resumen de reportes comparativos):**
   - **Relacional (`20261121T044353Z_compare_relational_c101be.md`):** PostgreSQL 18.7 logró mejor rendimiento en búsqueda (`R1` p50 `0.520 ms`), transacciones ACID Outbox (`R3` p50 `2.797 ms`), lotes (`R4` p50 `3.185 ms`) y pico RAM (`124.8 MiB` vs `614.8 MiB` de MySQL 8.4.13); sin embargo, en `R2_filtered_assertions` PostgreSQL degradó a p50 `6.727 ms` (`p95 = 9.403 ms`), por debajo de MySQL (`p50 = 1.746 ms`), lo que motivó el diseño posterior del índice parcial cubriente `idx_assertion_published_r2_covering` en `biolink-backend`.
   - **Documental (`20261121T044438Z_compare_document_847363.md`):** MongoDB 8.0.38 superó ampliamente a Apache CouchDB 3.5.3 en carga (`773.56 ms` vs `5,015.91 ms`) y en las 4 operaciones (`D1`–`D4` p50 `0.562`–`1.831 ms` vs `3.554`–`17.670 ms` en CouchDB, donde `D2 p95` alcanzó `66.207 ms`), con `269.9 MiB` de pico RAM y 100% de corrección.
   - **Grafo (`20261121T050159Z_compare_graph_e18c84.md`):** Memgraph `3.14.0` obtuvo menor latencia p50 en `G1` (`38.853 ms` vs `54.597 ms`), `G3` (`32.575 ms` vs `70.802 ms`) y menor RAM reportada (`191.2 MiB`), pero tardó `954,975.00 ms` (~15.9 min) en cargar `50,000` afirmaciones; Neo4j `2026.10.2` cargó en `13,839.91 ms`, completó las 140 mediciones con `100%` de corrección (`p50` `4.823`–`70.802 ms`, RAM pico `934.2 MiB / 1,024 MiB`, `OOMKilled: False`), pero falló en la limpieza posterior (`DETACH DELETE`) con `Neo.TransientError.General.MemoryPoolOutOfMemoryError` (`267.0 MiB` frente a límite de `268.8 MiB` en `dbms.memory.transaction.total.max`). Además, `storage_bytes` de Neo4j (`86,428` en 50k) reporta proxy de conteo de nodos y no bytes reales en disco, según advierte el propio reporte.

---

## 9. Documentación Existente vs. Desactualizada y Brechas de Evidencia

### 9.1 Documentos desactualizados detectados en `biolink-benchmarking/`
1. **`biolink-benchmarking/docs/docs/README.md`**, **`architecture.md`**, **`repository_structure.md`**, **`deployment.md`**, **`benchmarking.md`** y **`03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md`** (fechados el `20 de noviembre de 2026`): aún describen que `biolink-backend`, `biolink-frontend` y el diseño físico de Etapa 4 están *"pendientes de inicialización"*, que los motores están solo *"preseleccionados"* y que la campaña completa de 120 minutos *"no se ha ejecutado todavía"*.
2. **`biolink-benchmarking/README.md` (Sección F, líneas 207–249):** marca `run-pair`, `run-campaign` y los volúmenes `1,000`/`10,000`/`50,000` como *"pendientes de campaña"* o *"NO ejecutada todavía"*, pese a que `reports/20261121T050159Z_campaign_all_volumes_20261120.md` documenta la campaña ya ejecutada el `2026-11-21`.
3. **Inconsistencias de ubicación documental:** `biolink-benchmarking/docs/docs/` contiene Etapas 1–3 y arquitectura inicial, mientras que los reportes de campaña residen en `biolink-benchmarking/reports/`, los documentos de arquitectura/seguridad implementada residen en `biolink-backend/docs/` y `biolink-frontend/docs/`, y **no existe todavía dentro de `biolink-benchmarking/docs/docs/`** un informe consolidado de diseño físico ni ADRs de selección definitiva basados en los resultados del benchmark.

### 9.2 Evidencias faltantes identificadas
- **Documento formal de decisión tecnológica (ADR de selección definitiva):** justificación escrita vinculando los resultados de `reports/20261121T050159Z_campaign_all_volumes_20261120.md` con la elección de **PostgreSQL 18.7 + MongoDB 8.0.38 + Neo4j 2026.10.2** en `biolink-backend` y las mitigaciones adoptadas (`idx_assertion_published_r2_covering`, `NEO4J_TX_TOTAL_MAX`, lotes `1000 ROWS`).
- **Verificación re-ejecutada posterior a los últimos cambios en frontend:** `Vitest`, `Playwright` y `npm run build` tras el cambio de `allowedDevOrigins` en `biolink-frontend/next.config.ts`.
- **Evidencia formal de pruebas E2E integradas (Frontend + Backend + 3 motores en Docker sin mocks)** y registro de pruebas de aceptación del flujo completo `OP-09` → `OP-14` + `OutboxProjectionWorker` + visualización en `OP-05`.
- **Validación del `idx_assertion_published_r2_covering`:** plan de ejecución (`EXPLAIN ANALYZE`) en PostgreSQL demostrando la mejora respecto a la degradación observada en el benchmark de 50k.
- **Definición de despliegue productivo y empaquetado de `biolink-frontend`** (ausencia de `Dockerfile`, TLS y configuración `APP_ENV=production`).
