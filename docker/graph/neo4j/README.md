# Neo4j Community (Docker)

- Imagen fijada: `neo4j:2026.10.2-community` (límite de contenedor: `1024m`).
- Memoria JVM y caché configuradas dentro del límite de 1,024 MB:
  - `NEO4J_server_memory_heap_initial__size=256m`
  - `NEO4J_server_memory_heap_max__size=384m`
  - `NEO4J_server_memory_pagecache_size=256m`
- Healthcheck por HTTP (`http://127.0.0.1:7474`) para no lanzar procesos `cypher-shell` adicionales que dupliquen memoria JVM.
- Volumen separado: `neo4j_bench_data:/data`.
