# Comparativa secuencial — Modelo document (`20261121T043542Z_compare_document_1a32e9`)

- **Dataset:** `synthetic_10000_seed_20261120` (semilla `20261120`)
- **Candidatos:** `mongodb` vs. `couchdb`

| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |
|---|---|---:|---:|---:|---:|---|---:|
| `mongodb` | `8.0.38` | 29.41 | 186.34 | 162.66 | 418.2 | False | 229376 |
| `couchdb` | `3.5.3` | 113.14 | 1596.89 | 25.72 | 184.2 | False | 9976076 |

## Detalle por operación

| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---|---:|---:|---:|---:|---:|---:|
| `mongodb` | `D1_read_taxon_dossier` | 0.658 | 1.287 | 2.070 | 1282.93 | 100.00% | 0 |
| `mongodb` | `D2_nested_attribute_query` | 0.985 | 1.293 | 1.303 | 962.01 | 100.00% | 0 |
| `mongodb` | `D3_versioned_dossier_update` | 2.098 | 3.082 | 3.523 | 447.11 | 100.00% | 0 |
| `mongodb` | `D4_bulk_raw_source_insert` | 1.291 | 1.929 | 3.523 | 709.57 | 100.00% | 0 |
| `couchdb` | `D1_read_taxon_dossier` | 3.345 | 5.293 | 9.395 | 286.41 | 100.00% | 0 |
| `couchdb` | `D2_nested_attribute_query` | 12.411 | 60.228 | 66.243 | 38.64 | 100.00% | 0 |
| `couchdb` | `D3_versioned_dossier_update` | 14.017 | 16.711 | 17.238 | 70.68 | 100.00% | 0 |
| `couchdb` | `D4_bulk_raw_source_insert` | 9.348 | 10.558 | 11.230 | 106.74 | 100.00% | 0 |
