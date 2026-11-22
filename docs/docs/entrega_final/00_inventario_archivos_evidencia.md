# Inventario de Archivos y Evidencias (`00_inventario_archivos_evidencia.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Alcance exclusivo:** Repositorios `biolink-backend`, `biolink-frontend` y `biolink-benchmarking`.  
*(Se excluye por completo cualquier otro directorio externo a estos tres repositorios).*

---

## 1. Documentación Base, Requisitos y Arquitectura (`biolink-benchmarking/docs/docs/`)

Estos archivos respaldan la definición del dominio científico, las reglas `RD-01`–`RD-16`, los requisitos funcionales/no funcionales, el catálogo `OP-01`–`OP-15` y la arquitectura SOA original en tres repositorios (teniendo presente su desactualización en estado de avance):

| Archivo (ruta relativa al workspace) | Respalda |
|---|---|
| `biolink-benchmarking/docs/docs/Guia_Proyecto_Final_Bases_Datos.pdf` | Lineamientos académicos institucionales del proyecto. |
| `biolink-benchmarking/docs/docs/01_etapa_1_biolink.md` | Delimitación ecológica (frugivoría, Montes Azules vs. Playón de la Gloria, presencia vs. interacción). |
| `biolink-benchmarking/docs/docs/01_matriz_evidencias_biolink.csv` | Evidencia primaria derivada de Olea-Wagner et al. (2007) y Camargo-Sanabria & Mendoza (2016). |
| `biolink-benchmarking/docs/docs/02_etapa_2_modelado_y_requisitos_biolink.md` | Modelos lógicos (relacional, documental, grafo), requisitos `RF-01`–`RF-16`, `RNF-01`–`RNF-12` y reglas `RD-01`–`RD-16`. |
| `biolink-benchmarking/docs/docs/02_catalogo_operaciones_biolink.csv` | Especificación de las 15 operaciones (`OP-01` a `OP-15`), entradas, modelos involucrados y criterios de aceptación. |
| `biolink-benchmarking/docs/docs/03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md` | Arquitectura lógica v1.1, tres repositorios SOA, justificación por paradigma y criterios de selección. |
| `biolink-benchmarking/docs/docs/03_matriz_comparativa_motores_biolink.csv` | Matriz comparativa documental previa de los 6 motores candidatos. |
| `biolink-benchmarking/docs/docs/README.md` | Índice documental histórico del directorio global (requiere actualización de estado). |
| `biolink-benchmarking/docs/docs/architecture.md` | Fronteras SOA, contratos OpenAPI v1 y matriz de dependencias permitidas/prohibidas. |
| `biolink-benchmarking/docs/docs/repository_structure.md` | Responsabilidades y estructura objetivo de los tres repositorios. |
| `biolink-benchmarking/docs/docs/deployment.md` | Reglas de despliegue separado, no concurrencia con benchmark y techo de 4,096 MiB. |
| `biolink-benchmarking/docs/docs/benchmarking.md` | Especificación normativa de drivers directos, workloads `R1`–`G4` y campaña de 120 min. |

---

## 2. Evidencias de Diseño Físico e Implementación Backend (`biolink-backend`)

### 2.1 Empaquetado, Configuración y Contratos
- `biolink-backend/pyproject.toml` y `biolink-backend/requirements.lock`: versiones exactas de dependencias Python (`fastapi==0.165.0`, `pydantic==2.14.4`, `psycopg==3.3.9`, `pymongo==4.20.1`, `neo4j==6.4.1`, `uvicorn==0.54.0`, `pytest==9.2.0`).
- `biolink-backend/Dockerfile` y `biolink-backend/docker-compose.yaml`: imagen `python:3.14-slim-bookworm` y topología privada (`biolink_backend_net`) con `postgres:18.7` (`768m`), `mongo:8.0.38` (`768m`), `neo4j:2026.10.2-community` (`1024m`, límites transaccionales `256m`/`64m`), `api` (`320m`) y `worker` (`192m`).
- `biolink-backend/.env.example`: plantilla oficial de configuración sin secretos reales.
- `biolink-backend/contracts/openapi-v1.json`: contrato OpenAPI 3.1.0 con 26 rutas bajo `/api/v1` (SHA-256 `58587855B534CAB6AE53B081CE4067B78481E899CF4D8137E806F6E302F6A838`).

### 2.2 Esquemas Físicos, Migraciones y Semillas (`biolink-backend/database/`)
- `biolink-backend/database/postgresql/migrations/001_create_schema.sql`: definición física de 20 tablas, claves foráneas, restricciones `CHECK` (`DRAFT`/`IN_REVIEW`/`PUBLISHED`/`REJECTED`/`WITHDRAWN`, `reviewed_by`, fechas, `occurrence` vs. `interaction_assertion`) y tabla `outbox_event`.
- `biolink-backend/database/postgresql/migrations/002_create_indexes.sql`: índices de búsqueda taxonómica, `idx_assertion_published_r2_covering` (índice parcial cubriente con `INCLUDE`), índices de vecindario e índice parcial `idx_outbox_pending_polling`.
- `biolink-backend/database/postgresql/migrations/003_admin_curation_extensions.sql`: extensiones de lotes (`import_batch`, `import_record`), `aggregate_version`, `projection_status`, `payload_version` en Outbox y `dossier_version`/`dossier_sync_status` en `taxon`.
- `biolink-backend/database/postgresql/seeds/001_reference_fixture.sql`: fixture científico verificado en SQL (3 usuarios RBAC, 2 fuentes, 3 localidades, 32 taxones, 21 afirmaciones `PUBLISHED`, 1 `DRAFT`, 3 ocurrencias `OCC_SCI_*`).
- `biolink-backend/database/mongodb/schemas/taxon_dossier.schema.json`, `study_dossier.schema.json`, `raw_source_record.schema.json`: validadores `$jsonSchema` estrictos.
- `biolink-backend/database/mongodb/indexes/create_indexes.js`: creación de colecciones (incluida `taxon_dossier_versions`) e índices únicos/multikey.
- `biolink-backend/database/neo4j/constraints/001_create_constraints.cypher` y `biolink-backend/database/neo4j/indexes/001_create_indexes.cypher`: 5 restricciones `UNIQUE` y 6 índices secundarios en grafo.
- `biolink-backend/database/neo4j/projections/project_assertion.cypher`, `withdraw_assertion.cypher`, `reconcile_projections.cypher`: proyección idempotente `MERGE`, retiro puntual/lotes (`IN TRANSACTIONS OF 1000 ROWS`) y auditoría estructural.

### 2.3 Código Fuente del Monolito Modular (`biolink-backend/src/biolink_backend/`)
- **Dominio y seguridad:** `domain/vocabularies.py`, `domain/entities.py`, `domain/value_objects.py`, `domain/rules.py` (reglas `RD-01`, `RD-02`, `RD-03`, `RD-04`, `RD-05`, `RD-13`, `RD-16`, máquina de estados), `security/passwords.py` (PBKDF2 600,000 iteraciones), `security/tokens.py` (SHA-256), `security/rbac.py`.
- **Aplicación, puertos y configuración:** `config/settings.py`, `application/ports.py`, `application/dto.py`, `application/services/{health_service,auth_service,public_query_service,admin_curation_service}.py`, `shared/{exceptions,ids,logging,time}.py`.
- **Infraestructura, seeder y repositorios nativos:** `infrastructure/{manager,postgresql,mongodb,neo4j,reference_seeder}.py`, `repositories/relational/{health_repository,auth_repository,public_catalog_repository,admin_curation_repository,outbox_repository}.py`, `repositories/document/{health_repository,public_dossier_repository,admin_dossier_repository}.py`, `repositories/graph/{health_repository,public_network_repository,projection_repository}.py`.
- **Capa HTTP y Worker:** `main.py`, `api/{dependencies,errors,middleware}.py`, `api/v1/router.py`, `api/v1/schemas/*.py`, `api/v1/endpoints/{health,auth,taxa,interactions,network,sources,occurrences,admin}.py`, `workers/outbox_worker.py`.

### 2.4 Pruebas y Documentación Técnica de Backend
- **11 archivos de pruebas (`44` casos recolectados):** `biolink-backend/tests/conftest.py`, `test_config_validation.py` (7 defs / 10 casos parametrizados), `test_app_startup.py` (3), `test_health_and_errors.py` (4), `test_domain_and_security.py` (4), `test_database_connections.py` (5), `test_public_queries_repositories.py` (3), `test_public_queries_service.py` (5), `test_public_queries_api.py` (3), `test_admin_curation_and_sync.py` (5), `test_public_queries_live.py` (1 `@pytest.mark.live`), `test_admin_workflow_live.py` (1 `@pytest.mark.live`).
- **Documentación interna (5 documentos + README):** `biolink-backend/README.md`, `biolink-backend/docs/{architecture,configuration,database_connections,development,security}.md`.

---

## 3. Evidencias de Implementación y Pruebas Frontend (`biolink-frontend`)

### 3.1 Configuración, Contrato y Estado de Dependencias
- `biolink-frontend/package.json` y `biolink-frontend/package-lock.json`: stack exacto (`next@16.4.6`, `react@19.3.1`, `typescript@5.9.3`, `tailwindcss@4.3.5`, `cytoscape@3.35.0`, `vitest@5.1.1`, `axe-core@4.14.1`, `@playwright/test@^1.51.1`).
- `biolink-frontend/tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`, `next.config.ts` *(modificación local sin commit para `allowedDevOrigins`)*, `vitest.config.mts`, `playwright.config.ts`, `.env.example`.
- `biolink-frontend/contracts/openapi-v1.json` y `biolink-frontend/types/openapi.ts`: contrato OpenAPI sincronizado (idéntico SHA-256 al del backend) y tipos TypeScript derivados.

### 3.2 Capa de Cliente API, Rutas, Componentes y Funcionalidades
- **Cliente REST y hooks:** `biolink-frontend/lib/api/{client,public-api,admin-api}.ts`, `lib/formatting/scientific.ts`, `lib/validation/query-params.ts`, `hooks/{useAsyncQuery,useAuthSession}.ts`.
- **Rutas App Router y SEO (`biolink-frontend/app/`):** `layout.tsx`, `page.tsx`, `robots.ts` (`Disallow: /administration`), `taxa/page.tsx`, `taxa/[taxonId]/page.tsx`, `interactions/page.tsx`, `interactions/[assertionId]/page.tsx`, `networks/page.tsx`, `localities/compare/page.tsx`, `sources/page.tsx`, `sources/[sourceId]/page.tsx`, `occurrences/page.tsx`, `administration/{layout,page}.tsx`.
- **Componentes (`biolink-frontend/components/`) y características (`biolink-frontend/features/`):** 3 componentes de layout, 10 primitivos UI, 6 componentes científicos de dominio y 11 módulos funcionales encapsulados en `taxonomy/`, `interactions/`, `networks/`, `localities/`, `sources/`, `occurrences/` y `administration/`.
- **Estilos:** `biolink-frontend/styles/globals.css`.

### 3.3 Pruebas y Documentación Frontend
- **Pruebas unitarias y accesibilidad (`17` pruebas en Vitest):** `biolink-frontend/tests/setup.ts`, `accessibility.test.tsx` (3), `components.test.tsx` (8), `features.test.tsx` (4), `sync-states.test.tsx` (2).
- **Pruebas E2E (`5` especificaciones / `2` perfiles):** `biolink-frontend/tests/e2e/biolink.spec.ts` (usa interceptación HTTP vía `page.route`).
- **Documentación:** `biolink-frontend/README.md` y `biolink-frontend/docs/{architecture,design-system,accessibility,routing}.md`.

---

## 4. Evidencias de Benchmarking y Resultados Empíricos (`biolink-benchmarking`)

### 4.1 Código, Contenedores, Datasets y Scripts
- `biolink-benchmarking/pyproject.toml`, `.env.example`, `README.md`, `docker/compose.yaml`, `docker/relational/mysql/my.cnf`, `docker/document/couchdb/local.ini`.
- **Scripts de control:** `biolink-benchmarking/scripts/{engine_control.ps1,engine_control.sh,cleanup_all.ps1,validate_config.ps1}`.
- **Módulos fuente (`biolink-benchmarking/src/biolink_bench/`):** `cli.py`, `config.py`, `datasets/{bundle,scientific_fixture,synthetic_generator}.py`, `drivers/` (6 adaptadores nativos), `metrics/{collector,docker_monitor,exporter}.py`, `runners/{benchmark_runner,lifecycle,smoke_runner}.py`, `workloads/{base,relational,document,graph}.py`.
- **Datasets y manifiestos:**
  - `biolink-benchmarking/datasets/scientific_fixture/biolink_scientific_fixture.json` y `manifest.json` (`sha256: f4b2ec408f31624723912ad0e34d82880d84c105f967d2b827619368494bed73`).
  - `biolink-benchmarking/datasets/manifests/synthetic_1000_seed_20261120_manifest.json` (SHA-256 `a35e0114457ef4c9690a6ce0f278988e03b27bf52f82cc36b943470e1bc321c0`).
  - `biolink-benchmarking/datasets/manifests/synthetic_10000_seed_20261120_manifest.json` (SHA-256 `0e2e17c2edd6539dc5130ee47293c1ef0c9794052bb766081120061624247c86`).
  - `biolink-benchmarking/datasets/manifests/synthetic_50000_seed_20261120_manifest.json` (SHA-256 `00fef827633f4c730bb2e73ed292199fe06463f128cab63b303aab0554b9b6eb`).
- **Documentación técnica propia (`biolink-benchmarking/docs/`):** `benchmark_protocol.md`, `data_strategy.md`, `engine_matrix.md`, `resource_limits.md`, `results_format.md`, `workloads.md` y `results/README.md`.
- **Pruebas automatizadas (`16` casos recolectados):** `biolink-benchmarking/tests/{conftest,test_config,test_connectivity_smoke,test_metrics_and_exporter,test_scientific_fixture,test_synthetic_generator}.py`.

### 4.2 Artefactos de Salida de Ejecuciones (`results/` y `reports/`)

En disco residen **33** corridas completas (cada una con su par CSV en `results/raw/`, JSON en `results/summaries/` y bitácora `.log` en `results/logs/`) más **44** reportes Markdown en `biolink-benchmarking/reports/`:

| Grupo cronológico (UTC) | Cantidad de corridas (`csv`/`json`/`log`) | Reportes en `biolink-benchmarking/reports/` | Alcance respaldado |
|---|---|---|---|
| **Validación inicial `smoke` y `fixture` (`2026-11-21T01:38Z` – `01:45Z`)** | 15 corridas (`mysql`, `postgresql`, `mongodb`, `couchdb`, `neo4j` × 2, `memgraph` × 2) | 15 archivos `*_summary.md` (`94cf9b`, `3609b6`, `9c6e22`, `6c9e17`, `5d4593`, `233882`, `f143cd`, `e74d82`, `27953d`, `59c675`, `3b7eb4`, `dae560`, `b46fc2`, `7d69e5`, `8f5203`) | Conectividad nativa, salud, límites Docker, digest SHA256 de imágenes, corrección `100%` en `scientific_fixture_v1` e incidencia inicial de Memgraph (`014334Z` → `014458Z`). |
| **Campaña `10,000` (`2026-11-21T04:34Z` – `04:37Z`)** | 6 corridas (`1693e5`, `4cb5de`, `b65cb2`, `483b5f`, `f70d79`, `e7804e`) | 6 `*_summary.md` + 3 comparativos (`2b1f46` relacional, `1a32e9` documental, `9624da` grafo) + consolidado `20261121T043701Z_campaign_10000_f01a63.md` | Resultados p50/p95/máx/ops/s/RAM/CPU/corrección por pareja a volumen `10,000` (duración `141.6 s`). |
| **Campaña `1,000` (`2026-11-21T04:39Z` – `04:41Z`)** | 6 corridas (`57c194`, `6f16bc`, `e8e5d5`, `00d5d2`, `7dc3b7`, `8e3dac`) | 6 `*_summary.md` + 3 comparativos (`0cfd2f` relacional, `d98c9a` documental, `c95581` grafo) | Resultados comparativos por paradigma a volumen `1,000`. |
| **Campaña `50,000` (`2026-11-21T04:41Z` – `05:01Z`)** | 6 corridas (`a62a14`, `530dc1`, `cddcb0`, `c198d9`, `a63d11`, `118693`) | 6 `*_summary.md` + 3 comparativos (`c101be` relacional, `847363` documental, `e18c84` grafo) + maestro `20261121T050159Z_campaign_all_volumes_20261120.md` | Resultados a escala máxima (`50,000`), degradación `R2` en PostgreSQL, carga `954.98 s` en Memgraph y `MemoryPoolOutOfMemoryError` en limpieza de Neo4j (`934.2 MiB` RAM pico). |
