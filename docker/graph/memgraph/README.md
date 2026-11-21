# Memgraph Community (Docker)

- Imagen fijada: `memgraph/memgraph:3.14.0` (límite de contenedor: `1024m`).
- Límite interno del motor configurado mediante `--memory-limit=800` (MiB) para operar dentro del contenedor de 1,024 MB.
- Volumen separado: `memgraph_bench_data:/var/lib/memgraph`.
- Nota experimental: la documentación del proveedor recomienda 16 GB en producción y 1 GB mínimo; cualquier fallo de memoria con datasets grandes dentro de 1,024 MB debe registrarse sin aumentar el límite.
