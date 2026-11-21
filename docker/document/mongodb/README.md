# MongoDB Community Server 8.0 (Docker)

- Imagen fijada: `mongo:8.0.38` (límite de contenedor: `768m`).
- Caché WiredTiger acotada explícitamente mediante `--wiredTigerCacheSizeGB 0.25` para dejar margen suficiente al sistema operativo del contenedor y evitar OOM dentro de 768 MB.
- Volumen separado: `mongodb_bench_data:/data/db`.
