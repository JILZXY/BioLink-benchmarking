# PostgreSQL 18.7 (Docker)

- Imagen fijada: `postgres:18.7` (límite de contenedor: `768m`).
- Volumen nombrado `postgresql_bench_data` montado en `/var/lib/postgresql` conforme al diseño oficial de directorios de PostgreSQL 18+.
- Parámetros aplicados desde `docker/compose.yaml` para operar dentro de 768 MB:
  - `shared_buffers=192MB`
  - `work_mem=8MB`
  - `maintenance_work_mem=64MB`
  - `effective_cache_size=384MB`
  - `max_connections=50`
