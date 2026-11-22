# Resumen de ejecución: `20261121T044402Z_bench_mongodb_cddcb0`

- **Modo:** `benchmark`
- **Motor:** `mongodb` (document)
- **Dataset:** `synthetic_50000_seed_20261120` (semilla: `20261120`)
- **Inicio UTC:** `2026-11-21T04:44:02Z`
- **Fin UTC:** `2026-11-21T04:44:11Z`
- **Conexión (ms):** `13.200` | **Esquema (ms):** `35.876` | **Carga (ms):** `773.564` | **Índices (ms):** `102.916`
- **Almacenamiento reportado (bytes):** `8060928`
- **Pico memoria Docker (MiB):** `269.9` | **OOMKilled:** `False`

## Métricas por operación

| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |
|---|---:|---:|---:|---:|---:|---:|---:|
| `D1_read_taxon_dossier` | 30 | 0.562 | 0.629 | 0.912 | 1757.46 | 100.00% | 0 |
| `D2_nested_attribute_query` | 30 | 0.864 | 1.220 | 1.692 | 1056.08 | 100.00% | 0 |
| `D3_versioned_dossier_update` | 30 | 1.831 | 2.320 | 2.712 | 527.96 | 100.00% | 0 |
| `D4_bulk_raw_source_insert` | 30 | 1.121 | 1.372 | 2.688 | 838.79 | 100.00% | 0 |
