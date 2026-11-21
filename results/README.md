# Resultados de Benchmarking (`results/`)

Este directorio almacena las salidas generadas por `biolink-bench`:

- `raw/`: archivos CSV con cada medición individual (latencia por iteración, estado `ok`/`valid`, calentamiento separado).
- `summaries/`: archivos JSON con metadatos de entorno, versiones exactas, digests Docker, tiempos separados (`connection_ms`, `schema_ms`, `load_ms`, `index_ms`) y estadísticas (`p50`, `p95`, `max`, `ops_per_sec`, `correctness_rate_pct`).
- `logs/`: bitácoras completas por corrida.

Los archivos generados se ignoran en Git (salvo `.gitkeep` y este `README.md`) para no contaminar el repositorio con artefactos temporales locales. Consulta la especificación completa en [`../docs/results_format.md`](../docs/results_format.md).
