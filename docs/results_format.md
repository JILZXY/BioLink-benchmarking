# Formato y Organización de Resultados (`biolink-benchmarking`)

Cada ejecución (`smoke`, `run-engine`, `run-pair`, `run-campaign`) genera un identificador único con formato:

```text
<YYYYMMDDTHHMMSSZ>_<modo>_<objetivo>_<6hex>
```

Ejemplo real generado: `20261121T013817Z_bench_mysql_3609b6`.  
Ninguna corrida sobrescribe archivos de corridas anteriores.

---

## 1. Ubicación de artefactos generados

| Directorio | Archivo generado | Propósito |
|---|---|---|
| `results/raw/` | `<run_id>.csv` | Mediciones individuales de cada iteración (calentamiento y medición). |
| `results/summaries/` | `<run_id>.json` | Metadatos completos de reproducibilidad, tiempos separados, resumen estadístico y recursos Docker. |
| `results/logs/` | `<run_id>.log` | Bitácora cronológica de arranque, salud, carga, workloads, errores y limpieza. |
| `reports/` | `<run_id>_summary.md` o `compare_<modelo>.md` | Reportes legibles en Markdown para inspección rápida o comparación entre pareja. |

---

## 2. Esquema del CSV individual (`results/raw/<run_id>.csv`)

Columnas:

1. `run_id`: identificador único de la corrida.
2. `engine`: motor evaluado (`mysql`, `postgresql`, `mongodb`, `couchdb`, `neo4j`, `memgraph`).
3. `model`: paradigma (`relational`, `document`, `graph`).
4. `operation`: nombre de operación (`SMOKE_CRUD`, `R1_taxon_search`, ..., `G4_idempotent_assertion_upsert`).
5. `iteration`: número de iteración dentro de la fase (`1..warmup` o `1..measure`).
6. `is_warmup`: `True` si pertenece a calentamiento (excluida de p50/p95/máx), `False` si es medición oficial.
7. `latency_ms`: latencia individual de esa operación en milisegundos (sin tiempo de conexión).
8. `ok`: `True` si completó sin excepción ni timeout.
9. `valid`: `True` si el resultado pasó la validación exacta contra el dataset.
10. `timed_out`: `True` si superó `BENCH_TIMEOUT_SECONDS`.
11. `rows_returned`: cantidad de filas/documentos/aristas devueltos o insertados.
12. `error`: detalle del error en caso de fallo o validación incorrecta.

### Ejemplo real de CSV generado (`results/raw/20261121T013817Z_bench_mysql_3609b6.csv`)
```csv
run_id,engine,model,operation,iteration,is_warmup,latency_ms,ok,valid,timed_out,rows_returned,error
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R1_taxon_search,1,False,2.4614,True,True,False,1,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R2_filtered_assertions,1,False,2.8366,True,True,False,18,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R3_transactional_assertion_outbox,1,False,19.1385,True,True,False,1,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R4_batch_import_insert,1,False,17.0037,True,True,False,50,
```

---

## 3. Esquema del JSON de metadatos y resumen (`results/summaries/<run_id>.json`)

Contiene los bloques:
- Identificación: `run_id`, `mode`, `engine`, `model`, `dataset_id`, `seed`, `started_at_utc`, `finished_at_utc`.
- Tiempos separados (`timings_ms`): `connection_ms`, `schema_ms`, `load_ms`, `index_ms`, `cleanup_ms`.
- Almacenamiento (`storage_bytes`): espacio reportado por el motor tras la ejecución (nota: en Neo4j Community, al carecer de procedimiento Cypher directo de tamaño en bytes del almacén sin plugins, `get_storage_bytes()` reporta conteo de nodos actuales hasta incorporar inspección de volumen en disco si se requiere).
- Entorno y reproducibilidad: `engine_info`, `docker_info` (incluyendo `repo_digests`), `docker_resources`, `host_info`.
- `operations`: diccionario por operación con `count`, `warmup_count`, `ok_count`, `valid_count`, `error_count`, `timeout_count`, `correctness_rate_pct`, `p50_ms`, `p95_ms`, `max_ms`, `min_ms`, `mean_ms`, `ops_per_sec`.
- `errors` y `artifacts`.

### Ejemplo real de JSON generado (`results/summaries/20261121T013817Z_bench_mysql_3609b6.json`, extracto)
```json
{
  "run_id": "20261121T013817Z_bench_mysql_3609b6",
  "mode": "benchmark",
  "engine": "mysql",
  "model": "relational",
  "dataset_id": "scientific_fixture_v1",
  "timings_ms": {
    "connection_ms": 27.5553,
    "schema_ms": 88.6534,
    "load_ms": 40.4931,
    "index_ms": 320.4262,
    "cleanup_ms": 27.3134
  },
  "storage_bytes": 589824,
  "docker_info": {
    "image": "mysql:8.4.13",
    "repo_digests": [
      "mysql@sha256:a81d043930e51745522bd5c430961cf8286f0a23f0a9a2a6e0108f7ea71b0902"
    ],
    "mem_limit_mb": 768.0
  },
  "docker_resources": {
    "peak_memory_mib": 451.2,
    "oom_killed": false
  }
}
```

---

## 4. Política de gestión de errores y timeouts

- Si una operación excede `BENCH_TIMEOUT_SECONDS`, se marca `timed_out=True`, `ok=False`, `valid=False` y se registra en el resumen sin detener la exportación de evidencia.
- Si el contenedor sufre OOM (`oom_killed=True`), queda documentado explícitamente en `docker_resources` y `docker_info`, y la falla se reporta como hallazgo experimental sin subir `mem_limit`.
