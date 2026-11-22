# Catálogo Técnico de la API REST v1 (`02_catalogo_api_rest.md`)

**Fecha de corte:** 21 de noviembre de 2026  
**Fuente autoritativa:** `biolink-backend/contracts/openapi-v1.json` (OpenAPI `3.1.0`, `title: "BioLink API"`, `version: "0.1.0"`) y controladores reales en `biolink-backend/src/biolink_backend/api/v1/endpoints/`.  
**Prefijo base:** `/api/v1` (en desarrollo: `http://127.0.0.1:8000/api/v1`).  
**Documentación interactiva generada en ejecución:** `/api/v1/docs` (Swagger UI), `/api/v1/redoc` (ReDoc) y `/api/v1/openapi.json`.

---

## 0. Convenciones Transversales de la API

- **Cabeceras de respuesta:** Todas las respuestas añaden `X-Request-ID`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` y `Cache-Control: no-store`.
- **Autenticación en rutas protegidas (`/auth/me`, `/auth/logout` y `/admin/*`):** Acepta cookie `HttpOnly` (`biolink_session`) o cabecera `Authorization: Bearer <token>`.
- **Contrato estático OpenAPI vs. manejo global de errores en ejecución:** `contracts/openapi-v1.json` documenta los códigos declarados explícitamente en los decoradores (`200`/`201`, `422` de validación FastAPI y, en `/admin/*`, `401`, `403`, `409`, `503`). En tiempo de ejecución, los manejadores globales de `api/errors.py` retornan además `404` (`EntityNotFoundError`), `409` (`BusinessRuleViolationError`), `422` (`DomainValidationError`), `503` (`DatabaseUnavailableError`) y `500` (`INTERNAL_SERVER_ERROR`) en rutas públicas cuando corresponda.
- **Formato uniforme de errores (`ErrorResponse`):**

```json
{
  "error": {
    "code": "RULE_VIOLATION_RD_02",
    "message": "La afirmacion 'AST_001' requiere al menos una evidencia para publicarse.",
    "details": { "rule_id": "RD-02", "assertion_id": "AST_001" },
    "request_id": "5b845ac9cd874e7fa303a0696d1498cc"
  }
}
```

---

## 1. Resumen de los 26 Endpoints Implementados

| # | Método | Ruta (`/api/v1/...`) | Operación | Acceso / Rol | Bases involucradas |
|---:|---|---|---|---|---|
| 1 | `GET` | `/health/live` | Salud | Público | Ninguna |
| 2 | `GET` | `/health/ready` | Salud | Público | PostgreSQL, MongoDB, Neo4j |
| 3 | `GET` | `/health` | Salud | Público | PostgreSQL, MongoDB, Neo4j |
| 4 | `POST` | `/auth/login` | Autenticación | Interno (`app_user`) | PostgreSQL |
| 5 | `POST` | `/auth/logout` | Autenticación | Autenticado | PostgreSQL |
| 6 | `GET` | `/auth/me` | Autenticación | Autenticado | PostgreSQL *(sesión)* |
| 7 | `GET` | `/taxa` | `OP-01` | Público | PostgreSQL |
| 8 | `GET` | `/taxa/{taxon_id}` | `OP-02` | Público | PostgreSQL, MongoDB |
| 9 | `GET` | `/taxa/{taxon_id}/interactions` | `OP-03` | Público | Neo4j, PostgreSQL |
| 10 | `GET` | `/taxa/{taxon_id}/connectivity` | `OP-07` | Público | Neo4j, PostgreSQL |
| 11 | `GET` | `/interactions/{assertion_id}` | `OP-04` | Público | PostgreSQL, MongoDB, Neo4j |
| 12 | `GET` | `/network/subgraph` | `OP-05` | Público | Neo4j, PostgreSQL |
| 13 | `GET` | `/network/compare-localities` | `OP-06` | Público | Neo4j, PostgreSQL |
| 14 | `GET` | `/sources/{source_id}` | `OP-08` | Público | PostgreSQL, MongoDB |
| 15 | `GET` | `/occurrences` | `OP-15` | Público | PostgreSQL (+ MongoDB opcional) |
| 16 | `POST` | `/admin/import-batches` | `OP-09` | `CURATOR` | MongoDB, PostgreSQL |
| 17 | `GET` | `/admin/import-batches/{import_batch_id}` | `OP-09` (lectura) | `CURATOR`, `REVIEWER`, `ADMIN` | PostgreSQL |
| 18 | `GET` | `/admin/import-records` | `OP-10` (bandeja) | `CURATOR`, `REVIEWER`, `ADMIN` | PostgreSQL |
| 19 | `PATCH` | `/admin/import-records/{import_record_id}/normalize` | `OP-10` | `CURATOR` | PostgreSQL, MongoDB |
| 20 | `POST` | `/admin/assertions` | `OP-11` | `CURATOR` | PostgreSQL |
| 21 | `GET` | `/admin/assertions/{assertion_id}` | `OP-11`/`OP-12` (lectura) | `CURATOR`, `REVIEWER`, `ADMIN` | PostgreSQL |
| 22 | `POST` | `/admin/assertions/{assertion_id}/submit` | `OP-11`/`OP-12` | `CURATOR` | PostgreSQL |
| 23 | `POST` | `/admin/assertions/{assertion_id}/review` | `OP-12` | `REVIEWER` | PostgreSQL *(Outbox -> Neo4j vía worker)* |
| 24 | `PUT` | `/admin/taxa/{taxon_id}/dossier` | `OP-13` | `CURATOR` | PostgreSQL, MongoDB |
| 25 | `GET` | `/admin/provenance/{entity_type}/{entity_id}` | `OP-14` | `CURATOR`, `REVIEWER`, `ADMIN` | PostgreSQL (+ MongoDB si `taxon`) |
| 26 | `POST` | `/admin/reconcile` | Reconciliación | `REVIEWER`, `ADMIN` | PostgreSQL, Neo4j, MongoDB |

---

## 2. Endpoints de Salud (`Health`)

### 1. `GET /api/v1/health/live`
- **Propósito:** Confirmar que el proceso FastAPI responde sin consultar bases de datos.
- **Parámetros / Entrada:** Ninguno.
- **Salida:** `LivenessResponse` | **Códigos:** `200`, `500`.
- **Responsable:** `api/v1/endpoints/health.py` → `HealthService.check_liveness()`.
- **Bases involucradas:** Ninguna.
```json
{
  "status": "alive",
  "service": "biolink-backend",
  "version": "0.1.0",
  "environment": "development",
  "uptime_seconds": 12.408,
  "timestamp_utc": "2026-11-22T05:18:50.881618Z"
}
```

### 2. `GET /api/v1/health/ready`
- **Propósito:** Verificar conectividad real contra PostgreSQL 18.7, MongoDB 8.0.38 y Neo4j 2026.10.2.
- **Parámetros / Entrada:** Ninguno.
- **Salida:** `ReadinessResponse` | **Códigos:** `200` (todos sanos), `503` (al menos un motor falla), `500`.
- **Responsable:** `health.py` → `HealthService.check_readiness()` → `PostgresHealthRepository`, `MongoHealthRepository`, `Neo4jHealthRepository`.
- **Bases involucradas:** PostgreSQL, MongoDB, Neo4j.
```json
{
  "status": "ready",
  "ready": true,
  "timestamp_utc": "2026-11-22T05:18:50.881618Z",
  "dependencies": {
    "postgresql": { "healthy": true, "latency_ms": 17.184, "version": "18.7 (Debian 18.7-1.pgdg13+5)", "error": null },
    "mongodb": { "healthy": true, "latency_ms": 39.269, "version": "8.0.38", "error": null },
    "neo4j": { "healthy": true, "latency_ms": 140.41, "version": "2026.10.2", "error": null }
  }
}
```

### 3. `GET /api/v1/health`
- **Propósito:** Resumen consolidado de liveness, readiness real y presupuesto de memoria (`4,096 MiB`).
- **Parámetros / Entrada:** Ninguno.
- **Salida:** `ConsolidatedHealthResponse` | **Códigos:** `200`, `503`.
- **Responsable:** `health.py` → `HealthService.check_consolidated()`.
- **Bases involucradas:** PostgreSQL, MongoDB, Neo4j.
```json
{
  "status": "ok",
  "live": true,
  "ready": true,
  "service": "biolink-backend",
  "version": "0.1.0",
  "environment": "development",
  "uptime_seconds": 41.205,
  "timestamp_utc": "2026-11-22T05:19:07.388135Z",
  "memory_budget_mb": {
    "postgresql_mb": 768,
    "mongodb_mb": 768,
    "neo4j_mb": 1024,
    "backend_api_mb": 320,
    "worker_mb": 192,
    "containers_total_mb": 3072,
    "reserved_headroom_mb": 1024,
    "global_ceiling_mb": 4096
  },
  "dependencies": {
    "postgresql": { "healthy": true, "latency_ms": 4.1, "version": "18.7 (Debian 18.7-1.pgdg13+5)", "error": null },
    "mongodb": { "healthy": true, "latency_ms": 6.2, "version": "8.0.38", "error": null },
    "neo4j": { "healthy": true, "latency_ms": 9.0, "version": "2026.10.2", "error": null }
  }
}
```

---

## 3. Endpoints de Autenticación (`Authentication`)

### 4. `POST /api/v1/auth/login`
- **Propósito:** Autenticar usuarios internos (`app_user`), emitir cookie `HttpOnly` (`biolink_session`) y token Bearer opaco.
- **Parámetros:** Ninguno.
- **Entrada (`LoginRequestSchema`):** `email` (`str`, `4..255`), `password` (`str`, `8..256`).
- **Salida (`AuthSessionResponseSchema`):** `token_type: "Bearer"`, `access_token`, `expires_at`, `user: AuthenticatedUserSchema`.
- **Códigos:** `200`, `401` (`AUTHENTICATION_REQUIRED`), `422` (`REQUEST_VALIDATION_ERROR`), `503`.
- **Responsable:** `api/v1/endpoints/auth.py` → `AuthService.authenticate_internal_user()` → `PostgresAuthRepository`.
- **Bases involucradas:** PostgreSQL (`app_user`, `user_role`, `role`, `user_session`, `audit_log`).
- **Solicitud (`LoginRequestSchema`):**
```json
{
  "email": "curador1@biolink.org",
  "password": "CuratorBioLink2026!"
}
```
- **Respuesta `200` (`AuthSessionResponseSchema`):**
```json
{
  "token_type": "Bearer",
  "access_token": "opaque_256bit_urlsafe_token_example",
  "expires_at": "2026-11-22T17:18:50Z",
  "user": {
    "user_id": "USR_CURATOR_1",
    "email": "curador1@biolink.org",
    "display_name": "Dr. Curador Lacandona",
    "roles": ["CURATOR"],
    "is_active": true
  }
}
```

### 5. `POST /api/v1/auth/logout`
- **Propósito:** Revocar la sesión activa en PostgreSQL (`user_session.revoked_at`) y limpiar la cookie.
- **Seguridad:** `BearerAuth` o `SessionCookieAuth`.
- **Entrada:** Ninguna.
- **Salida (`LogoutResponseSchema`):** `{ "revoked": true, "message": "Sesion revocada exitosamente." }`.
- **Códigos:** `200`, `401`, `503`.
- **Responsable:** `auth.py` → `AuthService.logout()` → `PostgresAuthRepository`.
- **Bases involucradas:** PostgreSQL (`user_session`, `audit_log`).

### 6. `GET /api/v1/auth/me`
- **Propósito:** Retornar identidad, nombre visible, estado activo y roles asignados de la sesión actual.
- **Seguridad:** `BearerAuth` o `SessionCookieAuth` (`get_current_user`).
- **Entrada:** Ninguna.
- **Salida (`AuthenticatedUserSchema`):** `user_id`, `email`, `display_name`, `roles[]`, `is_active`.
- **Códigos:** `200`, `401`, `503`.
- **Responsable:** `auth.py` → `get_current_user` → `AuthService.resolve_session()` → `PostgresAuthRepository`.
- **Bases involucradas:** PostgreSQL.

---

## 4. Endpoints Públicos de Consulta (`OP-01` a `OP-08` y `OP-15`)

### 7. `GET /api/v1/taxa` (`OP-01`)
- **Propósito:** Buscar taxones por nombre aceptado, sinónimo, grafía original o identificador externo.
- **Parámetros Query:** `q` (`min_length=1, max_length=120`), `taxonomic_rank`, `organism_group`, `taxonomic_status`, `sort_by` (`accepted_name | taxon_id | taxonomic_rank`), `sort_order` (`asc | desc`), `page` (`>= 1`), `page_size` (`1..100`, default `20`).
- **Salida:** `TaxonSearchResponse` (`items: TaxonSummarySchema[]`, `pagination: PaginationMeta`, `applied_filters`).
- **Códigos:** `200`, `422`, `503`.
- **Responsable:** `endpoints/taxa.py` → `PublicQueryService.search_taxa()` → `PostgresPublicCatalogRepository`.
- **Bases involucradas:** PostgreSQL (`taxon`, `taxon_name`, `taxon_identifier`).
- **Ejemplo `GET /api/v1/taxa?q=Sturnira%20parvidens` → Respuesta `200` (`TaxonSearchResponse`):**
```json
{
  "items": [
    {
      "taxon_id": "TAX_AN_003",
      "accepted_name": "Sturnira lilium",
      "scientific_authorship": "(É. Geoffroy Saint-Hilaire, 1810)",
      "taxonomic_rank": "SPECIES",
      "organism_group": "ANIMAL",
      "taxonomic_status": "ACCEPTED",
      "matched_name": "Sturnira parvidens",
      "matched_usage": "SYNONYM",
      "matched_verbatim_name": "Sturnira lilium",
      "matched_identifier": null
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1 },
  "applied_filters": { "q": "Sturnira parvidens", "sort_by": "accepted_name", "sort_order": "asc" }
}
```

### 8. `GET /api/v1/taxa/{taxon_id}` (`OP-02`)
- **Propósito:** Consultar ficha completa integrando identidad relacional, variantes nominales, IDs externos y `taxon_dossier`.
- **Parámetros Path:** `taxon_id: str`.
- **Salida:** `TaxonDetailResponse` (`taxon`, `names[]`, `external_identifiers[]`, `has_dossier`, `dossier`, `warnings[]`).
- **Códigos:** `200`, `404` (`ENTITY_NOT_FOUND`), `503` (fallo de PG o MongoDB).
- **Responsable:** `taxa.py` → `PublicQueryService.get_taxon_fiche()` → `PostgresPublicCatalogRepository` + `MongoPublicDossierRepository`.
- **Bases involucradas:** PostgreSQL + MongoDB (`taxon_dossier`, `taxon_dossier_versions`).
```json
{
  "taxon": {
    "taxon_id": "TAX_AN_001",
    "accepted_name": "Artibeus lituratus",
    "scientific_authorship": "(Olfers, 1818)",
    "taxonomic_rank": "SPECIES",
    "organism_group": "ANIMAL",
    "taxonomic_status": "ACCEPTED"
  },
  "names": [
    {
      "taxon_name_id": "NM_TAX_AN_001",
      "name": "Artibeus lituratus",
      "name_usage": "ACCEPTED",
      "language": "la",
      "source_id": "BAT2007",
      "is_preferred": true,
      "verbatim_name": null
    }
  ],
  "external_identifiers": [
    { "taxon_identifier_id": "TID_REF_AN_001", "scheme": "CUSTOM", "external_id": "REF:BAT2007:TAX_AN_001", "source_id": "BAT2007" }
  ],
  "has_dossier": true,
  "dossier": {
    "taxon_id": "TAX_AN_001",
    "schema_version": 1,
    "document_version": 2,
    "history_versions_count": 1,
    "summary_description": "Ficha cientifica documentada para Artibeus lituratus en literatura de Montes Azules.",
    "summary_source_refs": ["BAT2007"],
    "summary_locators": ["Olea-Wagner et al. (2007)"],
    "sections": { "ecology": { "diet": ["Frugivoria documentada en excretas"] } },
    "claims": [],
    "media": [],
    "updated_at": "2026-11-21T00:00:00Z"
  },
  "warnings": []
}
```

### 9. `GET /api/v1/taxa/{taxon_id}/interactions` (`OP-03`)
- **Propósito:** Listar interacciones `PUBLISHED` donde participa un taxón (nunca expone `DRAFT`, `REJECTED` ni `WITHDRAWN`).
- **Parámetros:** Path `taxon_id`; Query `role` (`any | actor | target`), `interaction_type_code`, `locality_id`, `method_code`, `period_start`, `period_end`, `page` (`>=1`), `page_size` (`1..100`).
- **Salida:** `TaxonInteractionsResponse` (`taxon_id`, `items: InteractionListItemSchema[]`, `pagination`, `applied_filters`, `warnings[]`).
- **Códigos:** `200`, `404` (`Taxon` o `Locality`), `409` (`RULE_VIOLATION_RD_05` si `DISPERSES_SEEDS_OF`), `422`, `503`.
- **Responsable:** `taxa.py` → `PublicQueryService.list_taxon_interactions()` → `Neo4jPublicNetworkRepository` + `PostgresPublicCatalogRepository`.
- **Bases involucradas:** Neo4j + PostgreSQL.
- **Respuesta `200` (`TaxonInteractionsResponse`):**
```json
{
  "taxon_id": "TAX_AN_001",
  "items": [
    {
      "assertion_id": "AST_SCI_001",
      "status": "PUBLISHED",
      "interaction_type_code": "CONSUMES_FRUIT_OF",
      "actor_taxon": {
        "taxon_id": "TAX_AN_001",
        "accepted_name": "Artibeus lituratus",
        "scientific_authorship": "(Olfers, 1818)",
        "taxonomic_rank": "SPECIES",
        "organism_group": "ANIMAL",
        "taxonomic_status": "ACCEPTED",
        "matched_name": null,
        "matched_usage": null,
        "matched_verbatim_name": null,
        "matched_identifier": null
      },
      "target_taxon": {
        "taxon_id": "TAX_PL_001",
        "accepted_name": "Cecropia obtusifolia",
        "scientific_authorship": "Bertol.",
        "taxonomic_rank": "SPECIES",
        "organism_group": "PLANT",
        "taxonomic_status": "ACCEPTED",
        "matched_name": null,
        "matched_usage": null,
        "matched_verbatim_name": null,
        "matched_identifier": null
      },
      "locality": {
        "locality_id": "LOC_RBMA_SOUTH",
        "name": "Reserva de la Biosfera Montes Azules (sector sur)",
        "locality_type": "STUDY_AREA",
        "protected_status": "PROTECTED_ANP",
        "spatial_validation_status": "INSIDE_ANP",
        "coordinate_precision": "REGIONAL_STUDY_SECTOR",
        "parent_locality_id": null
      },
      "period_start": "2004-01",
      "period_end": "2004-07",
      "season_label": "Dry and rainy sampling seasons, Jan-Jul 2004",
      "method_code": "FECAL_SEED_IDENTIFICATION",
      "assertion_scope": "REFERENCE_FIXTURE",
      "source_citations": ["Olea-Wagner et al. (2007), Revista Mexicana de Biodiversidad, 78, 191-200."],
      "source_locators": ["Olea-Wagner et al. (2007), pp. 195-197; Results and Table 2"],
      "interpretation_limits": ["No identifica punto GPS exacto de deposicion ni demuestra establecimiento de plantula."]
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1 },
  "applied_filters": { "role": "any" },
  "warnings": [
    "Los resultados muestran unicamente afirmaciones en estado PUBLISHED sustentadas en evidencia documentada (RD-04, RD-16)."
  ]
}
```

### 10. `GET /api/v1/taxa/{taxon_id}/connectivity` (`OP-07`)
- **Propósito:** Calcular socios taxonómicos distintos (`distinct_partner_taxa_count`) separados del número de afirmaciones (`documented_assertions_count`).
- **Parámetros:** Path `taxon_id`; Query `locality_id`, `interaction_type_code`, `period_start`, `period_end`.
- **Salida:** `ConnectivityResponse` (`taxon`, conteos, `partners: PartnerConnectivitySchema[]`, `applied_filters`, `warnings[]`).
- **Códigos:** `200`, `404`, `409`, `422`, `503`.
- **Responsable:** `taxa.py` → `PublicQueryService.calculate_descriptive_connectivity()` → `Neo4jPublicNetworkRepository` + `PostgresPublicCatalogRepository`.
- **Bases involucradas:** Neo4j + PostgreSQL.
```json
{
  "taxon": { "taxon_id": "TAX_AN_001", "accepted_name": "Artibeus lituratus", "scientific_authorship": "(Olfers, 1818)", "taxonomic_rank": "SPECIES", "organism_group": "ANIMAL", "taxonomic_status": "ACCEPTED" },
  "distinct_partner_taxa_count": 2,
  "documented_assertions_count": 4,
  "as_actor_distinct_partners": 2,
  "as_target_distinct_partners": 0,
  "partners": [
    {
      "taxon": { "taxon_id": "TAX_PL_001", "accepted_name": "Cecropia obtusifolia", "scientific_authorship": "", "taxonomic_rank": "SPECIES", "organism_group": "PLANT", "taxonomic_status": "ACCEPTED" },
      "role_of_partner": "target",
      "assertions_count": 2,
      "interaction_type_codes": ["CONSUMES_FRUIT_OF"],
      "locality_ids": ["LOC_PDLG", "LOC_RBMA_SOUTH"]
    }
  ],
  "applied_filters": { "taxon_id": "TAX_AN_001" },
  "warnings": [
    "El grado y los conteos de conectividad representan unicamente taxones asociados distintos y numero de afirmaciones documentadas; no miden abundancia poblacional (RD-12)."
  ]
}
```

### 11. `GET /api/v1/interactions/{assertion_id}` (`OP-04`)
- **Propósito:** Obtener evidencia, localizadores, citas bibliográficas, `study_dossier`, referencia cruda redactada y estado real de proyección en Neo4j para una afirmación `PUBLISHED` (`DRAFT` retorna `404`).
- **Parámetros Path:** `assertion_id: str`.
- **Salida:** `InteractionDetailResponse` (`assertion`, `evidences[]`, `study_dossiers[]`, `raw_source_references[]`, `graph_projected`, `warnings[]`).
- **Códigos:** `200`, `404`, `409` (`RULE_VIOLATION_RD_02`), `503`.
- **Responsable:** `endpoints/interactions.py` → `PublicQueryService.get_interaction_detail()` → `PostgresPublicCatalogRepository` + `MongoPublicDossierRepository` + `Neo4jPublicNetworkRepository`.
- **Bases involucradas:** PostgreSQL + MongoDB + Neo4j.
- **Respuesta `200` (`InteractionDetailResponse`):**
```json
{
  "assertion": {
    "assertion_id": "AST_SCI_001",
    "status": "PUBLISHED",
    "interaction_type_code": "CONSUMES_FRUIT_OF",
    "actor_taxon": {
      "taxon_id": "TAX_AN_001",
      "accepted_name": "Artibeus lituratus",
      "scientific_authorship": "(Olfers, 1818)",
      "taxonomic_rank": "SPECIES",
      "organism_group": "ANIMAL",
      "taxonomic_status": "ACCEPTED",
      "matched_name": null,
      "matched_usage": null,
      "matched_verbatim_name": null,
      "matched_identifier": null
    },
    "target_taxon": {
      "taxon_id": "TAX_PL_001",
      "accepted_name": "Cecropia obtusifolia",
      "scientific_authorship": "Bertol.",
      "taxonomic_rank": "SPECIES",
      "organism_group": "PLANT",
      "taxonomic_status": "ACCEPTED",
      "matched_name": null,
      "matched_usage": null,
      "matched_verbatim_name": null,
      "matched_identifier": null
    },
    "locality": {
      "locality_id": "LOC_RBMA_SOUTH",
      "name": "Reserva de la Biosfera Montes Azules (sector sur)",
      "locality_type": "STUDY_AREA",
      "protected_status": "PROTECTED_ANP",
      "spatial_validation_status": "INSIDE_ANP",
      "coordinate_precision": "REGIONAL_STUDY_SECTOR",
      "parent_locality_id": null
    },
    "period_start": "2004-01",
    "period_end": "2004-07",
    "season_label": "Dry and rainy sampling seasons, Jan-Jul 2004",
    "method_code": "FECAL_SEED_IDENTIFICATION",
    "assertion_scope": "REFERENCE_FIXTURE",
    "source_citations": ["Olea-Wagner et al. (2007), Revista Mexicana de Biodiversidad, 78, 191-200."],
    "source_locators": ["Olea-Wagner et al. (2007), pp. 195-197; Results and Table 2"],
    "interpretation_limits": ["Does not identify exact GPS deposition point or demonstrate seedling establishment"]
  },
  "evidences": [
    {
      "evidence_id": "EVD_AST_SCI_001",
      "source_id": "BAT2007",
      "source_version_id": null,
      "source_locator": "Olea-Wagner et al. (2007), pp. 195-197; Results and Table 2",
      "evidence_kind": "OBSERVATION",
      "method_code": "FECAL_SEED_IDENTIFICATION",
      "reported_term": "CONSUMES_FRUIT_OF",
      "summary": "Identificacion de semillas de Cecropia obtusifolia en excretas de Artibeus lituratus.",
      "interpretation_limit": "Documenta consumo/remocion en muestra fecal, no establecimiento de plantula.",
      "period_start": "2004-01",
      "period_end": "2004-07",
      "license_id": "ACADEMIC_CITATION_ONLY",
      "evidence_role": "PRIMARY",
      "review_note": null,
      "source": {
        "source_id": "BAT2007",
        "source_type": "PUBLICATION",
        "title": "Frugivory and seed ingestion by phyllostomid bats in Lacandona",
        "authors": "Olea-Wagner et al.",
        "publication_year": 2007,
        "citation_text": "Olea-Wagner et al. (2007), Revista Mexicana de Biodiversidad, 78, 191-200.",
        "license_id": "ACADEMIC_CITATION_ONLY",
        "doi": null,
        "uri": null,
        "publisher": "Revista Mexicana de Biodiversidad"
      }
    }
  ],
  "study_dossiers": [],
  "raw_source_references": [
    {
      "raw_document_id": "RAW_AST_SCI_001",
      "import_batch_id": "BAT_REF_001",
      "source_id": "BAT2007",
      "external_record_id": "AST_SCI_001",
      "provider": "BAT2007",
      "checksum": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
      "license_id": "ACADEMIC_CITATION_ONLY",
      "redistribution_permitted": false,
      "raw_payload": null
    }
  ],
  "graph_projected": true,
  "warnings": [
    "La frugivoria documentada no equivale por si sola a dispersion efectiva ni germinacion (RD-04, RD-05)."
  ]
}
```

### 12. `GET /api/v1/network/subgraph` (`OP-05`)
- **Propósito:** Filtrar subred ecológica documentada (1 a 3 saltos) sobre afirmaciones `PUBLISHED`, separando localidades indeterminadas salvo filtro explícito.
- **Parámetros Query:** `taxon_id`, `locality_id`, `protected_status`, `spatial_validation_status`, `interaction_type_code`, `method_code`, `source_id`, `period_start`, `period_end`, `max_depth` (`1..3`, default `1`), `limit` (`1..200`, default `100`).
- **Salida:** `SubgraphResponse` (`applied_filters`, `nodes: SubgraphNodeSchema[]`, `interactions: SubgraphEdgeSchema[]`, `undetermined_locality_excluded_count`, `warnings[]`).
- **Códigos:** `200`, `404`, `409`, `422`, `503`.
- **Responsable:** `endpoints/network.py` → `PublicQueryService.filter_documented_subgraph()` → `Neo4jPublicNetworkRepository` + `PostgresPublicCatalogRepository`.
- **Bases involucradas:** Neo4j + PostgreSQL.
- **Respuesta `200` (`SubgraphResponse`):**
```json
{
  "applied_filters": { "locality_id": "LOC_RBMA_SOUTH", "max_depth": 1, "limit": 100 },
  "nodes": [
    {
      "node_id": "TAX_AN_001",
      "node_type": "TAXON",
      "label": "Artibeus lituratus",
      "properties": { "organism_group": "ANIMAL", "taxonomic_rank": "SPECIES" }
    },
    {
      "node_id": "TAX_PL_001",
      "node_type": "TAXON",
      "label": "Cecropia obtusifolia",
      "properties": { "organism_group": "PLANT", "taxonomic_rank": "SPECIES" }
    }
  ],
  "interactions": [
    {
      "assertion_id": "AST_SCI_001",
      "actor_taxon_id": "TAX_AN_001",
      "actor_name": "Artibeus lituratus",
      "target_taxon_id": "TAX_PL_001",
      "target_name": "Cecropia obtusifolia",
      "interaction_type_code": "CONSUMES_FRUIT_OF",
      "locality_id": "LOC_RBMA_SOUTH",
      "locality_name": "Reserva de la Biosfera Montes Azules (sector sur)",
      "protected_status": "PROTECTED_ANP",
      "period_start": "2004-01",
      "period_end": "2004-07",
      "method_code": "FECAL_SEED_IDENTIFICATION",
      "source_ids": ["BAT2007"]
    }
  ],
  "undetermined_locality_excluded_count": 0,
  "warnings": [
    "Los registros con localidad espacialmente indeterminada se excluyen y contabilizan aparte salvo filtro explicito (RD-07, RD-08)."
  ]
}
```

### 13. `GET /api/v1/network/compare-localities` (`OP-06`)
- **Propósito:** Comparar métricas y taxones compartidos/exclusivos entre dos localidades distintas (ej. `LOC_RBMA_SOUTH` vs. `LOC_PDLG`) manteniendo sus contextos separados y contando localidades indeterminadas aparte.
- **Parámetros Query:** `locality_id_a` **(requerido)**, `locality_id_b` **(requerido)**, `interaction_type_code`, `period_start`, `period_end`.
- **Salida:** `LocalityComparisonResponse` (`locality_a`, `locality_b`, `shared_taxa[]`, `exclusive_to_a_taxa[]`, `exclusive_to_b_taxa[]`, `shared_interaction_pairs[]`, `undetermined_locality_assertions_count`, `applied_filters`, `warnings[]`).
- **Códigos:** `200`, `404`, `409`, `422` (ej. si `locality_id_a == locality_id_b`), `503`.
- **Responsable:** `network.py` → `PublicQueryService.compare_localities()` → `Neo4jPublicNetworkRepository` + `PostgresPublicCatalogRepository`.
- **Bases involucradas:** Neo4j + PostgreSQL.
- **Respuesta `200` (`LocalityComparisonResponse`):**
```json
{
  "locality_a": {
    "locality": {
      "locality_id": "LOC_RBMA_SOUTH",
      "name": "Reserva de la Biosfera Montes Azules (sector sur)",
      "locality_type": "STUDY_AREA",
      "protected_status": "PROTECTED_ANP",
      "spatial_validation_status": "INSIDE_ANP",
      "coordinate_precision": "REGIONAL_STUDY_SECTOR",
      "parent_locality_id": null
    },
    "published_assertions_count": 12,
    "distinct_taxa_count": 10,
    "distinct_animal_taxa_count": 4,
    "distinct_plant_taxa_count": 6,
    "source_ids": ["BAT2007"]
  },
  "locality_b": {
    "locality": {
      "locality_id": "LOC_PDLG",
      "name": "Ejido Playon de la Gloria",
      "locality_type": "EJIDO",
      "protected_status": "OUTSIDE_ANP",
      "spatial_validation_status": "OUTSIDE_ANP",
      "coordinate_precision": "LOCALITY_CENTROID",
      "parent_locality_id": null
    },
    "published_assertions_count": 10,
    "distinct_taxa_count": 9,
    "distinct_animal_taxa_count": 4,
    "distinct_plant_taxa_count": 5,
    "source_ids": ["BAT2007"]
  },
  "shared_taxa": [],
  "exclusive_to_a_taxa": [],
  "exclusive_to_b_taxa": [],
  "shared_interaction_pairs": [
    {
      "actor_taxon_id": "TAX_AN_001",
      "actor_name": "Artibeus lituratus",
      "target_taxon_id": "TAX_PL_001",
      "target_name": "Cecropia obtusifolia",
      "interaction_type_code": "CONSUMES_FRUIT_OF"
    }
  ],
  "undetermined_locality_assertions_count": 0,
  "applied_filters": { "locality_id_a": "LOC_RBMA_SOUTH", "locality_id_b": "LOC_PDLG" },
  "warnings": [
    "Montes Azules (INSIDE_ANP) y Playon de la Gloria (OUTSIDE_ANP) se comparan manteniendo sus contextos separados (RD-07, RD-08)."
  ]
}
```

### 14. `GET /api/v1/sources/{source_id}` (`OP-08`)
- **Propósito:** Consultar metadatos bibliográficos de una fuente, versiones de descarga registradas, conteos de uso y su expediente `study_dossier`.
- **Parámetros Path:** `source_id: str`.
- **Salida:** `SourceDetailResponse` (`source`, `versions[]`, `published_assertions_count`, `evidences_count`, `has_study_dossier`, `study_dossier`, `warnings[]`).
- **Códigos:** `200`, `404`, `503`.
- **Responsable:** `endpoints/sources.py` → `PublicQueryService.get_source_detail()` → `PostgresPublicCatalogRepository` + `MongoPublicDossierRepository`.
- **Bases involucradas:** PostgreSQL + MongoDB.
- **Respuesta `200` (`SourceDetailResponse`):**
```json
{
  "source": {
    "source_id": "BAT2007",
    "source_type": "PUBLICATION",
    "title": "Frugivory and seed ingestion by phyllostomid bats in Lacandona",
    "authors": "Olea-Wagner et al.",
    "publication_year": 2007,
    "citation_text": "Olea-Wagner et al. (2007), Revista Mexicana de Biodiversidad, 78, 191-200.",
    "license_id": "ACADEMIC_CITATION_ONLY",
    "doi": null,
    "uri": null,
    "publisher": "Revista Mexicana de Biodiversidad"
  },
  "versions": [
    {
      "source_version_id": "SRCV_REF_BAT2007",
      "provider_version": "pub-2007",
      "release_date": "2007-06-01",
      "retrieved_at": "2026-11-21T00:00:00Z",
      "endpoint_or_file": "fixtures/bat2007.json",
      "query_parameters": {},
      "filters": {},
      "license_id": "ACADEMIC_CITATION_ONLY",
      "checksum": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    }
  ],
  "published_assertions_count": 22,
  "evidences_count": 22,
  "has_study_dossier": true,
  "study_dossier": {
    "dossier_id": "STD_BAT2007",
    "source_id": "BAT2007",
    "schema_version": 1,
    "doi_or_uri": null,
    "research_question": "Documentar dieta frugivora de murcielagos filostomidos en Chiapas.",
    "sampling_design": { "method": "mist_nets_and_feces" },
    "study_localities": ["LOC_RBMA_SOUTH", "LOC_PDLG"],
    "study_period": { "start": "2004-01", "end": "2004-07" },
    "focal_taxa": ["TAX_AN_001", "TAX_PL_001"],
    "interpretation_limits": ["Muestreo localizado; no mide reclutamiento ni abundancia absoluta."],
    "license_and_usage": { "license_id": "ACADEMIC_CITATION_ONLY", "redistribution_permitted": false },
    "checksum": null
  },
  "warnings": []
}
```

### 15. `GET /api/v1/occurrences` (`OP-15`)
- **Propósito:** Consultar registros de presencia taxonómica separados estrictamente de interacciones (`is_interaction_evidence: false`).
- **Parámetros Query:** `taxon_id`, `locality_id`, `source_id`, `georeference_status`, `date_from`, `date_to`, `include_raw_reference` (`bool`, default `false`), `sort_by` (`occurrence_id | event_date | accepted_name`), `sort_order` (`asc | desc`), `page` (`>=1`), `page_size` (`1..100`).
- **Salida:** `OccurrenceListResponse` (`items: OccurrenceItemSchema[]`, `pagination`, `applied_filters`, `warnings[]`).
- **Códigos:** `200`, `404`, `422`, `503`.
- **Responsable:** `endpoints/occurrences.py` → `PublicQueryService.list_occurrences()` → `PostgresPublicCatalogRepository` (+ `MongoPublicDossierRepository` si `include_raw_reference=true`).
- **Bases involucradas:** PostgreSQL (+ MongoDB opcional).
- **Respuesta `200` (`OccurrenceListResponse`):**
```json
{
  "items": [
    {
      "occurrence_id": "OCC_001",
      "taxon": {
        "taxon_id": "TAX_AN_001",
        "accepted_name": "Artibeus lituratus",
        "scientific_authorship": "(Olfers, 1818)",
        "taxonomic_rank": "SPECIES",
        "organism_group": "ANIMAL",
        "taxonomic_status": "ACCEPTED",
        "matched_name": null,
        "matched_usage": null,
        "matched_verbatim_name": null,
        "matched_identifier": null
      },
      "source": {
        "source_id": "BAT2007",
        "source_type": "PUBLICATION",
        "title": "Frugivory and seed ingestion by phyllostomid bats in Lacandona",
        "authors": "Olea-Wagner et al.",
        "publication_year": 2007,
        "citation_text": "Olea-Wagner et al. (2007), Revista Mexicana de Biodiversidad, 78, 191-200.",
        "license_id": "ACADEMIC_CITATION_ONLY",
        "doi": null,
        "uri": null,
        "publisher": "Revista Mexicana de Biodiversidad"
      },
      "locality": null,
      "source_record_id": "OCC_EXT_001",
      "event_date": "2004-03",
      "latitude": 16.1,
      "longitude": -90.9,
      "coordinate_uncertainty_meters": 500.0,
      "basis_of_record": "HUMAN_OBSERVATION",
      "georeference_status": "VERIFIED",
      "is_interaction_evidence": false,
      "raw_source_reference": null
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1 },
  "applied_filters": { "sort_by": "occurrence_id", "sort_order": "asc" },
  "warnings": [
    "Los registros de ocurrencia representan presencia documentada y no constituyen evidencia de interaccion (RD-01, RD-06)."
  ]
}
```

---

## 5. Endpoints Administrativos, Curación y Sincronización (`OP-09` a `OP-14`)

Todos los endpoints bajo `/api/v1/admin/*` documentan respuestas de seguridad/conflicto `401`, `403`, `409`, `422` y `503`.

### 16. `POST /api/v1/admin/import-batches` (`OP-09`)
- **Seguridad:** Exclusivo `CURATOR`.
- **Propósito:** Registrar lote de importación, versión de fuente (`source_version`) y conservar payloads crudos inmutables (`raw_source_record`) con registros en estado inicial `PENDING` sin autopublicar.
- **Entrada:** `ImportBatchCreateRequestSchema` (`source_id`, `provider_version`, `endpoint_or_file`, `provider`, `query_parameters`, `filters`, `records[]` `1..500`, opcionales `license_id`, `release_date`, `auto_publish=false`).
- **Salida:** `ImportBatchDetailResponseSchema` (`batch`, `records[]`).
- **Códigos:** `201`, `401`, `403`, `404` (`source`), `409` (`RD-13` si `auto_publish=true`), `422`, `503`.
- **Responsable:** `endpoints/admin.py` → `AdminCurationService.register_import_batch()` → `MongoAdminDossierRepository` + `PostgresAdminCurationRepository`.
- **Bases involucradas:** MongoDB (`raw_source_record`) + PostgreSQL (`source_version`, `import_batch`, `import_record`, `audit_log`).
- **Solicitud (`ImportBatchCreateRequestSchema`):**
```json
{
  "source_id": "BAT2007",
  "provider_version": "gbif-2026-11",
  "endpoint_or_file": "imports/bat2007_delta.json",
  "provider": "GBIF",
  "query_parameters": { "taxonKey": 2432896 },
  "filters": { "country": "MX" },
  "records": [
    {
      "external_record_id": "EXT_REC_001",
      "raw_payload": { "scientificName": "Sturnira parvidens", "locality": "Montes Azules" },
      "verbatim_name": "Sturnira parvidens",
      "proposed_external_scheme": "GBIF",
      "proposed_external_id": "2432896",
      "redistribution_permitted": false
    }
  ]
}
```

### 17. `GET /api/v1/admin/import-batches/{import_batch_id}` (`OP-09` lectura)
- **Seguridad:** `CURATOR`, `REVIEWER` o `ADMIN`.
- **Parámetros Path:** `import_batch_id`.
- **Salida:** `ImportBatchDetailResponseSchema` | **Códigos:** `200`, `401`, `403`, `404`, `409`, `503`.
- **Bases involucradas:** PostgreSQL.

### 18. `GET /api/v1/admin/import-records` (`OP-10` bandeja)
- **Seguridad:** `CURATOR`, `REVIEWER` o `ADMIN`.
- **Parámetros Query:** `import_batch_id`, `validation_status` (`PENDING | VALID | INVALID | UNRESOLVED | DUPLICATE`), `limit` (`1..500`, default `100`).
- **Salida:** `list[ImportRecordResponseSchema]` | **Códigos:** `200`, `401`, `403`, `409`, `422`, `503`.
- **Bases involucradas:** PostgreSQL (`import_record`, `taxon`).

### 19. `PATCH /api/v1/admin/import-records/{import_record_id}/normalize` (`OP-10`)
- **Seguridad:** Exclusivo `CURATOR`.
- **Propósito:** Normalizar registro importado guardando `matching_rule`, `canonical_taxon_id`, `verbatim_name` y variantes/IDs externos en PostgreSQL y `transformation_metadata` en MongoDB sin mutar `raw_payload`.
- **Entrada (`NormalizeImportRecordRequestSchema`):** `validation_status` (`VALID | INVALID | UNRESOLVED | DUPLICATE`), `matching_rule`, opcionales `canonical_taxon_id`, `verbatim_name`, `external_scheme`, `external_id`, `validation_notes`, `register_name_variant` (`true`), `register_external_identifier` (`true`).
- **Salida:** `NormalizeImportRecordResponseSchema` (`record`, `batch`, `registered_name_id`, `registered_identifier_id`, `raw_document_updated`).
- **Códigos:** `200`, `401`, `403`, `404`, `409` (`RD-14` si ID externo pertenece a otro taxón), `422`, `503`.
- **Bases involucradas:** PostgreSQL + MongoDB (`raw_source_record`).
- **Solicitud (`NormalizeImportRecordRequestSchema`):**
```json
{
  "validation_status": "VALID",
  "matching_rule": "EXACT_SYNONYM_MATCH",
  "canonical_taxon_id": "TAX_AN_003",
  "verbatim_name": "Sturnira parvidens",
  "external_scheme": "GBIF",
  "external_id": "2432896",
  "validation_notes": "Resuelto a Sturnira lilium sin modificar payload original"
}
```

### 20. `POST /api/v1/admin/assertions` (`OP-11`)
- **Seguridad:** Exclusivo `CURATOR`.
- **Propósito:** Crear nueva afirmación en `DRAFT` o `IN_REVIEW` vinculando al menos una evidencia existente o nueva (`RD-01`..`RD-06`, `RD-09`, `RD-13`).
- **Entrada:** `CreateAssertionRequestSchema` (`actor_taxon_id`, `target_taxon_id`, `interaction_type_code`, `locality_id`, `period_start`, `period_end`, `season_label`, `method_code`, `assertion_scope`, `initial_status`, `evidences[]`, `submission_reason`).
- **Salida:** `AdminAssertionResponseSchema` (`projection_status: "NOT_APPLICABLE"`, `graph_projected: false`).
- **Códigos:** `201`, `401`, `403`, `404`, `409` (`RD-01`, `RD-03`, `RD-05`, `RD-13`), `422`, `503`.
- **Bases involucradas:** PostgreSQL (`interaction_assertion`, `evidence`, `assertion_evidence`, `review_event`, `audit_log`).
- **Solicitud (`CreateAssertionRequestSchema`):**
```json
{
  "actor_taxon_id": "TAX_AN_001",
  "target_taxon_id": "TAX_PL_001",
  "interaction_type_code": "CONSUMES_FRUIT_OF",
  "locality_id": "LOC_RBMA_SOUTH",
  "period_start": "2004-01",
  "period_end": "2004-07",
  "season_label": "Dry and rainy sampling seasons, Jan-Jul 2004",
  "method_code": "FECAL_SEED_IDENTIFICATION",
  "assertion_scope": "BIOLINK_V1",
  "initial_status": "DRAFT",
  "evidences": [
    {
      "evidence_role": "PRIMARY",
      "source_id": "BAT2007",
      "source_locator": "p. 196, Table 2",
      "evidence_kind": "OBSERVATION",
      "method_code": "FECAL_SEED_IDENTIFICATION",
      "reported_term": "frugivory",
      "summary": "Semillas recuperadas en excretas de Artibeus lituratus.",
      "interpretation_limit": "Consumo documentado sin seguimiento post-deposicion.",
      "period_start": "2004-01",
      "period_end": "2004-07",
      "license_id": "ACADEMIC_CITATION_ONLY"
    }
  ],
  "submission_reason": "Carga inicial curada para revision"
}
```

### 21. `GET /api/v1/admin/assertions/{assertion_id}` (`OP-11`/`OP-12` lectura)
- **Seguridad:** `CURATOR`, `REVIEWER` o `ADMIN`.
- **Propósito:** Consultar detalle administrativo completo de una afirmación en cualquier estado (incluyendo `DRAFT`, `projection_status`, `aggregate_version`).
- **Salida:** `AdminAssertionResponseSchema` | **Códigos:** `200`, `401`, `403`, `404`, `409`, `503`.
- **Bases involucradas:** PostgreSQL.

### 22. `POST /api/v1/admin/assertions/{assertion_id}/submit` (`OP-11`/`OP-12`)
- **Seguridad:** Exclusivo `CURATOR`.
- **Propósito:** Transicionar `DRAFT -> IN_REVIEW` con registro en `review_event` y `audit_log`, sin publicar ni generar evento Outbox.
- **Entrada:** `SubmitAssertionRequestSchema` (`{ "reason": "Evidencia verificada y lista para revision cientifica" }`).
- **Salida:** `ReviewAssertionResponseSchema` (`outbox_event: null`, `relational_committed: true`).
- **Códigos:** `200`, `401`, `403`, `404`, `409` (`RD-13`), `422`, `503`.
- **Bases involucradas:** PostgreSQL.

### 23. `POST /api/v1/admin/assertions/{assertion_id}/review` (`OP-12`)
- **Seguridad:** Exclusivo `REVIEWER`.
- **Propósito:** Ejecutar transición editorial `APPROVE` (`IN_REVIEW -> PUBLISHED`), `REJECT` (`IN_REVIEW -> REJECTED`), `WITHDRAW` (`PUBLISHED -> WITHDRAWN`) o `REOPEN` (`REJECTED/WITHDRAWN -> IN_REVIEW`). En `APPROVE` y `WITHDRAW` inserta `outbox_event (PENDING)` en la misma transacción ACID.
- **Entrada (`ReviewAssertionRequestSchema`):** `action` (`APPROVE | REJECT | WITHDRAW | REOPEN`), `reason` (`3..2000`).
- **Salida:** `ReviewAssertionResponseSchema` (`assertion`, `review_event`, `outbox_event`, `relational_committed: true`, `graph_sync_note`).
- **Códigos:** `200`, `401`, `403`, `404`, `409` (`RD-02`, `RD-13`), `422`, `503`.
- **Bases involucradas:** PostgreSQL *(proyección asíncrona posterior hacia Neo4j por `OutboxProjectionWorker`)*.
- **Solicitud (`ReviewAssertionRequestSchema`):**
```json
{
  "action": "APPROVE",
  "reason": "Evidencia primaria verificada contra Olea-Wagner et al. (2007)"
}
```
- **Respuesta `200` (`ReviewAssertionResponseSchema`):**
```json
{
  "assertion": {
    "assertion_id": "AST_01",
    "status": "PUBLISHED",
    "aggregate_version": 2,
    "projection_status": "PENDING",
    "last_projected_at": null,
    "interaction_type_code": "CONSUMES_FRUIT_OF",
    "actor_taxon": { "taxon_id": "TAX_AN_001", "accepted_name": "Artibeus lituratus" },
    "target_taxon": { "taxon_id": "TAX_PL_001", "accepted_name": "Cecropia obtusifolia" },
    "locality": { "locality_id": "LOC_RBMA_SOUTH", "name": "Reserva de la Biosfera Montes Azules (sector sur)" },
    "period_start": "2004-01",
    "period_end": "2004-07",
    "season_label": "Dry and rainy sampling seasons, Jan-Jul 2004",
    "method_code": "FECAL_SEED_IDENTIFICATION",
    "assertion_scope": "BIOLINK_V1",
    "created_by": "USR_CURATOR_1",
    "created_at": "2026-11-22T05:00:00Z",
    "reviewed_by": "USR_REVIEWER_1",
    "reviewed_at": "2026-11-22T05:10:00Z",
    "updated_at": "2026-11-22T05:10:00Z",
    "evidences": [{ "evidence_id": "EVD_01", "source_id": "BAT2007", "evidence_role": "PRIMARY" }],
    "graph_projected": false
  },
  "review_event": {
    "review_event_id": "REV_01",
    "assertion_id": "AST_01",
    "user_id": "USR_REVIEWER_1",
    "previous_status": "IN_REVIEW",
    "new_status": "PUBLISHED",
    "reason": "Evidencia primaria verificada contra Olea-Wagner et al. (2007)",
    "created_at": "2026-11-22T05:10:00Z"
  },
  "outbox_event": {
    "event_id": "OBX_01",
    "event_type": "ASSERTION_PUBLISHED",
    "assertion_id": "AST_01",
    "aggregate_version": 2,
    "payload_version": 1,
    "created_at": "2026-11-22T05:10:00Z",
    "processing_status": "PENDING",
    "attempts": 0,
    "last_error": null,
    "processed_at": null,
    "payload_json": { "assertion_id": "AST_01", "aggregate_version": 2, "status": "PUBLISHED" }
  },
  "relational_committed": true,
  "graph_sync_note": "Transaccion relacional confirmada; evento Outbox PENDING para sincronizacion asincrona con Neo4j."
}
```

### 24. `PUT /api/v1/admin/taxa/{taxon_id}/dossier` (`OP-13`)
- **Seguridad:** Exclusivo `CURATOR`.
- **Propósito:** Actualizar `taxon_dossier` de forma versionada, archivando la versión previa en `taxon_dossier_versions`, validando concurrencia optimista (`expected_version`) y actualizando control en `taxon` + `audit_log`.
- **Entrada (`UpdateTaxonDossierRequestSchema`):** `summary_description`, `summary_source_refs[]`, `summary_locators[]`, `sections`, `claims[]`, `media[]`, `change_reason`, `expected_version`, `dataset_tag`.
- **Salida:** `UpdateTaxonDossierResponseSchema` (`taxon_id`, `previous_version`, `archived_version_id`, `dossier`, `dossier_sync_status`, `sync_warning`).
- **Códigos:** `200`, `401`, `403`, `404` (`taxon` o `source`), `409` (`RD-02` sin fuentes citadas, `RD-15` conflicto optimista), `422`, `503`.
- **Bases involucradas:** PostgreSQL + MongoDB (`taxon_dossier`, `taxon_dossier_versions`).
- **Solicitud (`UpdateTaxonDossierRequestSchema`):**
```json
{
  "summary_description": "Ficha cientifica actualizada con evidencia dietaria de Montes Azules.",
  "summary_source_refs": ["BAT2007"],
  "summary_locators": ["Olea-Wagner et al. (2007), pp. 195-197"],
  "sections": { "ecology": { "diet": ["Frugivoria documentada en excretas"] } },
  "claims": [
    {
      "claim_id": "CLM_01",
      "field": "ecology.feeding_guild",
      "value": "frugivore",
      "source_id": "BAT2007",
      "source_locator": "p. 196, Table 2"
    }
  ],
  "media": [],
  "change_reason": "Incorporacion de sintesis bibliografica verificada",
  "expected_version": 1,
  "dataset_tag": "CURATED_BIOLINK"
}
```
- **Respuesta `200` (`UpdateTaxonDossierResponseSchema`):**
```json
{
  "taxon_id": "TAX_AN_001",
  "previous_version": 1,
  "archived_version_id": "TDV_TAX_AN_001_V1",
  "dossier": { "taxon_id": "TAX_AN_001", "schema_version": 1, "document_version": 2 },
  "dossier_sync_status": "SYNCED",
  "sync_warning": null
}
```

### 25. `GET /api/v1/admin/provenance/{entity_type}/{entity_id}` (`OP-14`)
- **Seguridad:** `CURATOR`, `REVIEWER` o `ADMIN`.
- **Propósito:** Reconstruir la cronología completa de fuentes, versiones de descarga, lotes, registros normalizados, evidencias, eventos de revisión, outbox, auditoría y (para `taxon`) historial de versiones documentales.
- **Parámetros Path:** `entity_type` (`assertion | taxon | import_batch | import_record`), `entity_id`.
- **Salida:** `ProvenanceHistoryResponseSchema`.
- **Códigos:** `200`, `401`, `403`, `404`, `422`, `503`.
- **Bases involucradas:** PostgreSQL (+ MongoDB `taxon_dossier_versions` cuando `entity_type == "taxon"`).

### 26. `POST /api/v1/admin/reconcile` (Reconciliación Multi-Modelo)
- **Seguridad:** `REVIEWER` o `ADMIN`.
- **Propósito:** Reencolar eventos `FAILED`/`DEAD_LETTER`/`PROCESSING`, drenar lotes Outbox, reconciliar nodos/aristas `PUBLISHED` de PostgreSQL hacia Neo4j retirando huérfanas, y alinear `taxon.dossier_version` contra MongoDB.
- **Entrada:** Ninguna.
- **Salida:** `ReconciliationResponseSchema`.
- **Códigos:** `200`, `401`, `403`, `409`, `503`.
- **Bases involucradas:** PostgreSQL + Neo4j + MongoDB.
```json
{
  "outbox_processed_count": 1,
  "outbox_failed_count": 0,
  "graph_expected_published_count": 22,
  "graph_projected_or_verified_count": 22,
  "graph_removed_stale_count": 0,
  "dossier_checked_taxa_count": 32,
  "dossier_reconciled_count": 0,
  "reconciled_taxon_ids": []
}
```

---

## 6. Diferenciación de Cobertura respecto al Catálogo `OP-01`–`OP-15`

- **Implementadas íntegramente en `/api/v1`:** `OP-01`, `OP-02`, `OP-03`, `OP-04`, `OP-05`, `OP-06`, `OP-07`, `OP-09`, `OP-10`, `OP-11`, `OP-12`, `OP-13`, `OP-14`, `OP-15`, más `Health`, `Auth` y `/admin/reconcile`.
- **Cubiertas parcialmente en exploración global:**
  - `OP-08` implementa consulta detallada por identificador (`GET /api/v1/sources/{source_id}`), pero **no existe** endpoint paginado `GET /api/v1/sources` para listar todas las fuentes del catálogo.
  - No existe endpoint relacional directo `GET /api/v1/interactions` para listar afirmaciones fuera del filtro de subgrafo en Neo4j (`GET /api/v1/network/subgraph`) o por taxón (`GET /api/v1/taxa/{taxon_id}/interactions`).
- **Pendiente de evolución futura (fuera de V1):** registro o consulta pública con cuentas externas, exportación masiva o soporte a `DISPERSES_SEEDS_OF` (bloqueado deliberadamente en `rules.py`).
