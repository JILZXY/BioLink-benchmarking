# Protocolo Técnico de Benchmarking Directo (`biolink-benchmarking`)

## 1. Propósito y alcance

Este protocolo rige las pruebas empíricas comparativas entre los seis motores candidatos de BioLink dentro de `biolink-benchmarking`:

- **Relacional:** MySQL 8.4 LTS vs. PostgreSQL 18.7
- **Documental:** MongoDB Community Server 8.0 vs. Apache CouchDB 3.5.3
- **Grafo:** Neo4j Community vs. Memgraph Community

Cada motor se evalúa **exclusivamente mediante su driver o protocolo nativo** (`mysql-connector-python`, `psycopg`, `pymongo`, interfaz HTTP nativa de CouchDB vía `httpx`, y protocolo Bolt vía `neo4j`), sin pasar por FastAPI, endpoints de `biolink-backend` ni ORM de aplicación.

---

## 2. Fases de una ejecución medida

Para garantizar comparabilidad justa y evitar mezclar preparación con rendimiento de consulta, `benchmark_runner.py` separa cada corrida en fases explícitas e independientes:

1. **Validación previa (`validate_config`):** verifica tags fijados sin `:latest`, puertos en `127.0.0.1`, límites de memoria por categoría y credenciales locales en `.env`.
2. **Aislamiento de contenedor:** verifica mediante `docker ps` que ningún otro contenedor `biolink-bench-*` esté activo antes de iniciar el candidato.
3. **Inspección y monitoreo:** captura imagen, digest SHA256, límite de memoria (`docker inspect`) e inicia un hilo secundario de muestreo de recursos (`docker stats --no-stream` cada `0.5 s`).
4. **Conexión directa (`connection_ms`):** abre la conexión nativa y valida disponibilidad antes de cronometrar consultas.
5. **Preparación de esquema (`schema_ms`):** crea tablas/colecciones/constraints sin poblar datos.
6. **Carga inicial (`load_ms`):** inserta el conjunto lógico (`SCIENTIFIC_FIXTURE` o `SYNTHETIC_BENCHMARK`) correspondiente al paradigma del motor.
7. **Creación de índices (`index_ms`):** construye índices secundarios después de la carga inicial.
8. **Calentamiento (`warmup`):** ejecuta `BENCH_WARMUP_ITERATIONS` (por defecto `5`) por cada operación; estas iteraciones se registran en el CSV con `is_warmup=True` y se excluyen del resumen estadístico.
9. **Medición por operación:** ejecuta cada workload por separado (lecturas antes que escrituras para preservar el ground truth del conjunto cargado), midiendo cada invocación con `time.perf_counter_ns()` y validando la exactitud del resultado contra el dataset en memoria.
10. **Almacenamiento, limpieza y exportación:** consulta el espacio reportado por el motor, elimina los registros de prueba (`cleanup_test_data`), detiene el monitoreo, exporta CSV/JSON/LOG/reporte Markdown y apaga el contenedor con `-v` al comparar parejas.

---

## 3. Reglas de medición y equidad

- **No mezclas arbitrarias 80/20:** cada operación (`R1`–`R4`, `D1`–`D4`, `G1`–`G4`) se mide y reporta por separado.
- **Mismo conjunto lógico y mismos parámetros:** `build_cases` genera exactamente la misma secuencia determinista de consultas y validaciones para ambos candidatos de una misma categoría.
- **Validación obligatoria de corrección:** una ejecución más rápida con resultado incorrecto reduce `correctness_rate_pct` y no puede declararse ganadora.
- **Sin comparación entre paradigmas:** nunca se comparan tiempos absolutos de SQL contra documental o grafo.
- **No sobrescribir corridas:** cada ejecución genera un `run_id` único (`YYYYMMDDTHHMMSSZ_<modo>_<motor>_<hex>`).

---

## 4. Ventana máxima de campaña (120 minutos)

| Bloque | Presupuesto máximo | Actividad |
|---|---:|---|
| Preparación | 10 min | Verificar imágenes previamente descargadas, salud, límites y datasets. |
| Relacional | 30 min | MySQL 8.4 LTS y PostgreSQL 18.7 secuenciales (~15 min c/u). |
| Documental | 25 min | MongoDB 8.0 y CouchDB 3.5.3 secuenciales (~12 min c/u). |
| Grafo | 35 min | Neo4j Community y Memgraph Community secuenciales (~17 min c/u). |
| Validación y cierre | 20 min | Consolidar resúmenes, verificar corrección y exportar reportes. |
| **Total máximo** | **120 min** | Techo experimental de campaña completa (`run-campaign`). |

---

## 5. Criterio de decisión (post-benchmark)

Conforme a la Etapa 3 de BioLink, la selección del ganador dentro de cada paradigma seguirá este orden de prioridad:

1. Cumplimiento funcional y 100% de corrección de resultados.
2. Integridad, trazabilidad y capacidad de reconstrucción.
3. Capacidad para completar los volúmenes objetivo (1,000; 10,000; 50,000).
4. Estabilidad y pico de memoria bajo el límite asignado y el presupuesto global de 4 GB.
5. Latencias `p50`/`p95`, tiempo de carga y creación de índices.
6. Facilidad operativa, calidad de drivers y términos de licencia.
