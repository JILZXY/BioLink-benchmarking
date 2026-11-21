# Comparativa secuencial — Modelo document (`20261121T044042Z_compare_document_d98c9a`)

- **Dataset:** `synthetic_1000_seed_20261120` (semilla `20261120`)
- **Candidatos:** `mongodb` vs. `couchdb`

| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |
|---|---|---:|---:|---:|---:|---|---:|
| `mongodb` | `8.0.38` | 27.52 | 23.90 | 41.83 | 407.0 | False | 122880 |
| `couchdb` | `3.5.3` | 127.26 | 339.51 | 26.23 | 169.4 | False | 2067380 |

## Detalle por operación

| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---|---:|---:|---:|---:|---:|---:|
| `mongodb` | `D1_read_taxon_dossier` | 0.604 | 0.900 | 1.072 | 1561.96 | 100.00% | 0 |
| `mongodb` | `D2_nested_attribute_query` | 0.981 | 1.389 | 1.457 | 984.58 | 100.00% | 0 |
| `mongodb` | `D3_versioned_dossier_update` | 2.135 | 2.634 | 2.747 | 453.22 | 100.00% | 0 |
| `mongodb` | `D4_bulk_raw_source_insert` | 1.315 | 2.211 | 3.718 | 674.23 | 100.00% | 0 |
| `couchdb` | `D1_read_taxon_dossier` | 2.032 | 2.829 | 3.525 | 457.59 | 100.00% | 0 |
| `couchdb` | `D2_nested_attribute_query` | 15.697 | 16.946 | 17.170 | 67.79 | 100.00% | 0 |
| `couchdb` | `D3_versioned_dossier_update` | 13.075 | 14.090 | 14.719 | 76.68 | 100.00% | 0 |
| `couchdb` | `D4_bulk_raw_source_insert` | 9.018 | 10.270 | 10.571 | 108.85 | 100.00% | 0 |
