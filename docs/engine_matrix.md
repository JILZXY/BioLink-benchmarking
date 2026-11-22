# Matriz de Motores Candidatos, Versiones y Conectividad Directa

Este documento registra los seis motores evaluados por `biolink-benchmarking`, sus tags fijados (prohibido `:latest`), las versiones exactas reportadas por los servidores, los digests SHA256 verificados al descargar las imágenes y la configuración aplicada.

---

## 1. Matriz de candidatos y versiones verificadas

| Modelo | Candidato | Imagen Docker fijada | Versión exacta reportada | Digest SHA256 (`RepoDigests`) | Driver / interfaz directa | Puerto `127.0.0.1` | Límite Docker | Validación en vivo |
|---|---|---|---|---|---|---:|---:|---|
| **Relacional** | MySQL 8.4 LTS | `mysql:8.4.13` | `8.4.13` (`MySQL Community Server - GPL`) | `mysql@sha256:a81d043930e51745522bd5c430961cf8286f0a23f0a9a2a6e0108f7ea71b0902` | `mysql-connector-python 26.10.0` | `3307` | `768 MB` | Smoke + fixture (`100%`) |
| **Relacional** | PostgreSQL 18.7 | `postgres:18.7` | `18.7 (Debian 18.7-1.pgdg13+5)` | `postgres@sha256:eb63372c1e05c755f55fa30cbd07aecc443676fc6c0fa90b9002d01537841e1a` | `psycopg 3.3.9` | `5433` | `768 MB` | Smoke + fixture (`100%`) |
| **Documental** | MongoDB Community 8.0 | `mongo:8.0.38` | `8.0.38` | `mongo@sha256:479e85ced54ffb8a40dade1dcde2da2a9ae858515b9415e9cc54bfb8f0575d01` | `pymongo 4.20.1` | `27018` | `768 MB` | Smoke + fixture (`100%`) |
| **Documental** | Apache CouchDB 3.5.3 | `couchdb:3.5.3` | `3.5.3` | `couchdb@sha256:907eab5b7e55ab7cfd241d39b90b2a335ea40bef82acee5a37388c08bf201dda` | `httpx 0.28.1` (HTTP nativo CouchDB) | `5985` | `768 MB` | Smoke + fixture (`100%`) |
| **Grafo** | Neo4j Community | `neo4j:2026.10.2-community` | `2026.10.2` (Community) | `neo4j@sha256:88458a76de0704f543bab66b7df1984b36ac3f24de3c2e2d74c8fa1972ebb8cf` | `neo4j 6.4.1` (Bolt) | `7688` / `7475` | `1,024 MB` | Smoke + fixture (`100%`) |
| **Grafo** | Memgraph Community | `memgraph/memgraph:3.14.0` | `3.14.0` | `memgraph/memgraph@sha256:a732421217951066e42f5749111bc3d0c7b51b12c756be04850d4dafa84cc05e` | `neo4j 6.4.1` (cliente Bolt compatible) | `7689` | `1,024 MB` | Smoke + fixture (`100%`) |

---

## 2. Desviaciones de versión e incompatibilidades documentadas

1. **MySQL `8.4.12` -> `mysql:8.4.13` (desviación explícita de tag Docker):**
   - **Causa:** La matriz comparativa de la Etapa 3 citaba `8.4.12` como referencia documental, pero al intentar `docker pull` / `up` se recibió `docker.io/library/mysql:8.4.12: not found`. Al consultar el registro oficial de Docker Hub (`library/mysql/tags`), los tags publicados de la rama 8.4 LTS eran `8.4.11` y `8.4.13`.
   - **Decisión:** Se fijó **`mysql:8.4.13`** (parche estable vigente de MySQL 8.4 LTS) en `.env.example`, `docker/compose.yaml` y `config.py`.
2. **Apache CouchDB `3.5.3` y montajes `:ro` en Windows Docker Desktop:**
   - **Causa:** El script `/docker-entrypoint.sh` de `couchdb:3.5.3` ejecuta `set -e` y `find /opt/couchdb/etc -type f ! -perm 0644 -exec chmod -f 0644 '{}' +`. En Windows, montar `local.ini` en modo `:ro` dentro de `/opt/couchdb/etc/local.d/` provoca que `chmod` falle sobre el sistema de archivos de solo lectura y el contenedor salga con código `1`.
   - **Decisión:** `docker/compose.yaml` genera `/opt/couchdb/etc/local.d/10-biolink.ini` dentro de la capa escribible del contenedor antes de ejecutar `/docker-entrypoint.sh`, usando `require_valid_user_except_for_up = true` para permitir el health check `/_up` manteniendo autenticación obligatoria en el resto de rutas.
3. **PostgreSQL `18.7` y cambio de ruta de volumen:**
   - **Causa:** A partir de PostgreSQL 18, la imagen oficial almacena el clúster bajo `/var/lib/postgresql/18/docker`.
   - **Decisión:** El volumen `postgresql_bench_data` se monta en `/var/lib/postgresql`.

---

## 3. Parámetros específicos por motor

### MySQL 8.4 LTS (`mysql:8.4.13`)
- Archivo de referencia `docker/relational/mysql/my.cnf`: `innodb_buffer_pool_size=256M`, `innodb_log_buffer_size=16M`, `max_connections=50`, `performance_schema=OFF`, `character-set-server=utf8mb4`.
- **Observación en vivo:** En la ejecución sobre Windows Docker Desktop (`20261121T013817Z_bench_mysql_3609b6`), MySQL reportó `innodb_buffer_pool_size_bytes = 134217728` (128 MiB por defecto) porque MySQL ignora archivos `.cnf` montados desde host Windows si presentan permisos `world-writable`. Esto mantuvo la memoria dentro de `451.2 MiB / 768 MiB` sin errores; si en campañas de 50,000 filas en Linux/Windows se requiere forzar 256M, se recomienda pasar `--innodb-buffer-pool-size=256M` vía `command` o asegurar permisos `0644`.

### PostgreSQL 18.7 (`postgres:18.7`)
- Parámetros vía `command`: `shared_buffers=192MB`, `work_mem=8MB`, `maintenance_work_mem=64MB`, `effective_cache_size=384MB`, `max_connections=50`.
- `outbox_event.payload_json` utiliza `JSONB`.

### MongoDB Community Server 8.0 (`mongo:8.0.38`)
- Caché WiredTiger limitada con `--wiredTigerCacheSizeGB 0.25`.
- Validador `$jsonSchema` configurado en `taxon_dossiers`.
- Observación de licencia de Etapa 3 preservada: SSPL (source-available, no aprobada por OSI).

### Apache CouchDB 3.5.3 (`couchdb:3.5.3`)
- Modo `single_node = true`, índices Mango (`_index`), validación `_design/biolink_validation` (`validate_doc_update`), carga masiva vía `_bulk_docs` y versionado con control `_rev`.
- Licencia: Apache 2.0.

### Neo4j Community (`neo4j:2026.10.2-community`)
- Heap inicial `256m`, heap máximo `384m`, pagecache `256m`.
- Health check por HTTP (`http://127.0.0.1:7474`) para no lanzar una JVM adicional con `cypher-shell`.
- Licencia: GPLv3 (Community Edition).

### Memgraph Community (`memgraph/memgraph:3.14.0`)
- Límite interno `--memory-limit=800` (MiB) para mantenerse dentro de `1,024 MB`.
- Consultas de introspección adaptadas a las columnas reales de Memgraph 3.14 (`SHOW VERSION;` y `SHOW STORAGE INFO;` con columna `'storage info'`).
