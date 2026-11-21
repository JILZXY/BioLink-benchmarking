# BioLink Benchmarking (`biolink-benchmarking`)

Entorno independiente y reproducible para evaluar empíricamente el rendimiento, la corrección funcional y el consumo de recursos de seis motores de bases de datos candidatos para **BioLink** mediante conexiones directas con sus controladores o protocolos nativos.

---

## A. Descripción

### Propósito del proyecto
BioLink requiere integrar tres paradigmas de persistencia complementarios (relacional, documental y grafo). El propósito de `biolink-benchmarking` es comparar los candidatos dentro de cada paradigma antes de cerrar la selección tecnológica de `biolink-backend`:

| Modelo | Candidato A | Candidato B | Driver / protocolo directo |
|---|---|---|---|
| **Relacional** | MySQL 8.4 LTS (`mysql:8.4.13`) | PostgreSQL 18.7 (`postgres:18.7`) | `mysql-connector-python` / `psycopg` |
| **Documental** | MongoDB Community 8.0 (`mongo:8.0.38`) | Apache CouchDB 3.5.3 (`couchdb:3.5.3`) | `pymongo` / HTTP nativo de CouchDB (`httpx`) |
| **Grafo** | Neo4j Community (`neo4j:2026.10.2-community`) | Memgraph Community (`memgraph/memgraph:3.14.0`) | `neo4j` (Bolt) / cliente Bolt compatible |

> **Nota sobre MySQL 8.4 LTS:** La documentación de Etapa 3 citaba como referencia `8.4.12`; al validar contra Docker Hub, `mysql:8.4.12` no existe como tag publicado (`not found`), encontrándose disponibles `8.4.11` y `8.4.13`. Se fijó explícitamente **`mysql:8.4.13`** y se documentó esta desviación en [`docs/engine_matrix.md`](./docs/engine_matrix.md).

### Diferencia entre benchmark directo y pruebas de API
- **Benchmark directo (`biolink-benchmarking`):** se conecta directamente desde Python a cada base de datos usando su driver o protocolo nativo para medir el comportamiento real del motor (latencia de consulta, carga, índices, transacciones, memoria y almacenamiento).
- **Pruebas de API (`biolink-backend`):** miden el servicio HTTP/REST completo (serialización JSON, validación Pydantic, autenticación, reglas de negocio y orquestación).

### Arquitectura independiente
`biolink-benchmarking` es un **repositorio autónomo** dentro de la arquitectura SOA de tres repositorios (`biolink-frontend`, `biolink-backend`, `biolink-benchmarking`):
- No utiliza FastAPI ni endpoints REST de BioLink.
- No importa modelos, servicios, repositorios ni ORM (`SQLAlchemy`) desde `biolink-backend`.
- No depende de `biolink-frontend` ni comparte archivo `compose.yaml` con la aplicación.
- Mantiene su propio `pyproject.toml`, sus propios scripts, su propio `.env.example` y sus propios volúmenes Docker.

---

## B. Requisitos de hardware

Los valores siguientes se justifican a partir de los límites fijados en `docker/compose.yaml`, las imágenes descargadas y las mediciones de memoria observadas durante la validación en vivo (`results/summaries/`):

| Recurso | Mínimo indispensable | Recomendado | Justificación técnica |
|---|---|---|---|
| **RAM total del equipo** | **8 GB** | **16 GB** | El entorno de contenedores tiene un techo experimental de **4 GB (4,096 MB)** y Docker Desktop (WSL2 en Windows) + sistema operativo + Python requieren al menos ~3–4 GB adicionales para evitar swapping que distorsione latencias. |
| **RAM libre dedicada al entorno de prueba** | **4.5 GB disponibles** | **6 GB+ disponibles** | Garantiza los **4,096 MB** del presupuesto experimental sin compresión ni paginación. En ejecución secuencial, el motor más pesado observado en arranque/humo (`neo4j`) alcanzó **710.4 MiB** bajo su límite de `1,024 MiB`. |
| **Espacio en disco libre** | **12 GB** | **25 GB (SSD)** | Las 6 imágenes base ocupan varios GB en caché de Docker, más volúmenes temporales por motor, datasets sintéticos de hasta `50,000` afirmaciones en JSONL y resultados CSV/JSON/logs. Se recomienda SSD para medir E/S real de carga e índices. |
| **Procesador** | **4 núcleos / 4 hilos (x86_64)** | **6+ núcleos / 8+ hilos** | Cada contenedor acota `cpus: "2.0"`, mientras el cliente Python (`biolink-bench`) y el muestreador `docker stats` se ejecutan en paralelo en el host. |
| **Sistema operativo** | Windows 10/11 64-bit con WSL2, Linux x86_64 o macOS | Windows 11 (validado en `10.0.26300`), Ubuntu 22.04/24.04 | Compatible con contenedores `linux/amd64` y Docker Compose V2. |

---

## C. Requisitos de software

| Software | Versión compatible / probada | Clasificación | Propósito |
|---|---|---|---|
| **Docker Desktop** o **Docker Engine** | Docker Engine **29.7.2** (probado en Windows Docker Desktop) | **Obligatorio** | Ejecutar cada motor candidato en contenedor aislado con `mem_limit` y volúmenes separados. |
| **Docker Compose V2** | **`v5.4.0`** (compatible `>= v2.20`) | **Obligatorio** | Orquestar perfiles independientes (`--profile`) y health checks (`--wait`). |
| **Python** | **`>=3.11,<3.16`** (probado en **Python `3.14.7`**) | **Obligatorio** | Ejecutar `biolink-bench`, generador sintético, drivers nativos y exportación de métricas. |
| **`pip`** + **`venv`** | `pip >= 24` (probado en `26.2.1`) | **Obligatorio** | Crear el entorno virtual aislado e instalar dependencias desde `pyproject.toml`. |
| **Git** | `>= 2.35` (probado en `2.56.1`) | **Obligatorio** | Clonar el repositorio y controlar cambios sin incluir `.env`, `.venv/` ni resultados locales. |
| **PowerShell 5.1+ / 7+** o **Bash** | PowerShell (Windows) / Bash (Linux/macOS) | **Obligatorio** | Ejecutar los comandos de preparación y scripts en `scripts/`. |
| **`pytest`** | `>= 8.3.0` (instalado con `.[dev]`, probado `9.2.0`) | **Opcional (recomendado)** | Correr pruebas unitarias de invariantes y pruebas `@pytest.mark.live`. |
| **Cliente SQL/GUI externo** (DBeaver, Compass, etc.) | Cualquiera | **Opcional** | Inspección manual ocasional en `127.0.0.1`; nunca necesario para ejecutar pruebas. |

---

## D. Preparación del entorno

### 1. Clonar el repositorio e ingresar al directorio

**Windows PowerShell:**
```powershell
git clone <URL_DEL_REPOSITORIO_BIOLINK_BENCHMARKING> biolink-benchmarking
Set-Location biolink-benchmarking
```

**Linux / macOS (Bash):**
```bash
git clone <URL_DEL_REPOSITORIO_BIOLINK_BENCHMARKING> biolink-benchmarking
cd biolink-benchmarking
```

### 2. Crear el entorno virtual de Python

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Si existen varias versiones instaladas en Windows, selecciona explícitamente una versión compatible, por ejemplo `py -3.14 -m venv .venv`.)*

**Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias independientes

**Windows PowerShell y Linux/macOS:**
```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Dependencias instaladas (sin FastAPI, sin SQLAlchemy, sin paquetes de backend):
- `mysql-connector-python` (MySQL nativo)
- `psycopg[binary]` (PostgreSQL v3 nativo)
- `pymongo` (MongoDB nativo)
- `httpx` (cliente HTTP directo para interfaz HTTP nativa de CouchDB)
- `neo4j` (driver Bolt oficial para Neo4j y compatible para Memgraph)
- `python-dotenv` y `pytest` (opcional de desarrollo)

### 4. Configurar el archivo `.env`

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

Edita `.env` y **reemplaza todos los valores `CHANGE_ME_*`** por contraseñas locales de prueba (por ejemplo, alfanuméricas de al menos 12 caracteres; **Neo4j exige mínimo 8 caracteres**). Nunca subas `.env` a Git.

### 5. Verificar configuración, fixture y sintaxis Compose

**Windows PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m biolink_bench check-config --require-env
.\.venv\Scripts\python.exe -m biolink_bench verify-fixture
.\.venv\Scripts\pytest.exe -m "not live" -v
.\scripts\validate_config.ps1 -RequireEnv
```

**Linux / macOS:**
```bash
python -m biolink_bench check-config --require-env
python -m biolink_bench verify-fixture
pytest -m "not live" -v
```

### 6. Descargar previamente las imágenes Docker (opcional antes de medir)

Para separar el tiempo de descarga de los tiempos experimentales:

**Windows PowerShell:**
```powershell
foreach ($p in @("mysql","postgresql","mongodb","couchdb","neo4j","memgraph")) {
    docker compose --env-file .env -f docker/compose.yaml --profile $p pull
}
```

**Linux / macOS:**
```bash
for p in mysql postgresql mongodb couchdb neo4j memgraph; do
    docker compose --env-file .env -f docker/compose.yaml --profile "$p" pull
done
```

---

## E. Ejecución de motores (uno a la vez)

**Regla estricta:** los seis motores **nunca se levantan simultáneamente**. Detén el candidato activo antes de iniciar el siguiente. Todos publican puertos únicamente en `127.0.0.1`.

### 1. Iniciar MySQL 8.4 LTS (`mysql:8.4.13`, `127.0.0.1:3307`, límite `768m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile mysql up -d --wait
```

### 2. Iniciar PostgreSQL 18.7 (`postgres:18.7`, `127.0.0.1:5433`, límite `768m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile postgresql up -d --wait
```

### 3. Iniciar MongoDB Community 8.0 (`mongo:8.0.38`, `127.0.0.1:27018`, límite `768m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile mongodb up -d --wait
```

### 4. Iniciar Apache CouchDB 3.5.3 (`couchdb:3.5.3`, `127.0.0.1:5985`, límite `768m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile couchdb up -d --wait
```

### 5. Iniciar Neo4j Community (`neo4j:2026.10.2-community`, `127.0.0.1:7688` Bolt / `7475` HTTP, límite `1024m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile neo4j up -d --wait
```

### 6. Iniciar Memgraph Community (`memgraph/memgraph:3.14.0`, `127.0.0.1:7689`, límite `1024m`)
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile memgraph up -d --wait
```

*(También puedes usar `.\scripts\engine_control.ps1 -Engine <motor> -Action up` en Windows o `./scripts/engine_control.sh <motor> up` en Linux/macOS, que además bloquean el arranque si detectan otro contenedor del benchmark activo.)*

---

## F. Ejecución de pruebas

### Estado de validación de comandos

| Funcionalidad | Estado en esta entrega |
|---|---|
| Validación de configuración (`check-config`), fixture (`verify-fixture`) y tests unitarios (`pytest -m "not live"`) | **Implementado y validado** |
| Pruebas de conexión, salud, inserción/consulta/limpieza de humo (`smoke`) para los 6 motores | **Implementado y validado en los 6 motores** |
| Carga del fixture científico y ejecución de comprobación (`run-engine --dataset fixture --warmup 0 --iterations 1`) | **Implementado y validado en los 6 motores (100% corrección)** |
| Generación reproducible de volúmenes `1,000` / `10,000` / `50,000` (`generate-data`) | **Implementado y probado unitariamente en muestra pequeña; campaña masiva aún no ejecutada** |
| Comparación por pareja (`run-pair`) y campaña completa hasta 120 min (`run-campaign`) | **Implementado; campaña completa pendiente de ejecución autorizada** |

### 1. Pruebas de conexión y humo (por motor)
Con el motor correspondiente levantado (o usando `--manage-docker` para que `biolink-bench` lo levante y detenga automáticamente):
```powershell
.\.venv\Scripts\python.exe -m biolink_bench smoke --engine mysql
.\.venv\Scripts\python.exe -m pytest -m live --engine mysql -v
```
*(Sustituir `mysql` por `postgresql`, `mongodb`, `couchdb`, `neo4j` o `memgraph` tras detener el anterior.)*

### 2. Generación reproducible de datasets sintéticos
```powershell
# Volúmenes previstos: 1000, 10000 o 50000 afirmaciones SYNTHETIC_BENCHMARK
.\.venv\Scripts\python.exe -m biolink_bench generate-data --volume 1000 --seed 20261120
.\.venv\Scripts\python.exe -m biolink_bench generate-data --volume 10000 --seed 20261120
.\.venv\Scripts\python.exe -m biolink_bench generate-data --volume 50000 --seed 20261120
```

### 3. Carga de datos directa en un motor activo
```powershell
.\.venv\Scripts\python.exe -m biolink_bench load-data --engine postgresql --dataset fixture
# O con dataset sintético:
.\.venv\Scripts\python.exe -m biolink_bench load-data --engine postgresql --dataset synthetic --volume 1000 --seed 20261120
```

### 4. Ejecución de workloads en un motor individual
```powershell
# Validación breve con fixture científico (ya validada en los 6 motores):
.\.venv\Scripts\python.exe -m biolink_bench run-engine --engine mysql --dataset fixture --warmup 0 --iterations 1

# Corrida con dataset sintético (pendiente de ejecución en campaña):
.\.venv\Scripts\python.exe -m biolink_bench run-engine --engine mysql --dataset synthetic --volume 1000 --warmup 5 --iterations 30 --manage-docker --remove-volumes
```

### 5. Ejecución comparativa secuencial por pareja *(pendiente de campaña)*
```powershell
.\.venv\Scripts\python.exe -m biolink_bench run-pair --model relational --dataset synthetic --volume 10000 --seed 20261120
.\.venv\Scripts\python.exe -m biolink_bench run-pair --model document   --dataset synthetic --volume 10000 --seed 20261120
.\.venv\Scripts\python.exe -m biolink_bench run-pair --model graph      --dataset synthetic --volume 10000 --seed 20261120
```

### 6. Campaña completa secuencial (máximo 120 minutos) *(NO ejecutada todavía)*
```powershell
.\.venv\Scripts\python.exe -m biolink_bench run-campaign --volume 10000 --seed 20261120
```

---

## G. Resultados

### Ubicación de archivos generados
- **Mediciones individuales CSV:** `results/raw/<run_id>.csv`
- **Metadatos, entorno y resúmenes estadísticos JSON:** `results/summaries/<run_id>.json`
- **Bitácoras de ejecución y errores:** `results/logs/<run_id>.log`
- **Reportes Markdown individuales y comparativos:** `reports/<run_id>_summary.md` y `reports/<run_id>.md`
- **Errores y timeouts:** registrados en la columna `error` del CSV, en el arreglo `"errors"` del JSON y detallados en `results/logs/<run_id>.log`.

### Ejemplo real generado en la validación (`20261121T013817Z_bench_mysql_3609b6`)

Estructura producida por una corrida:
```text
results/
├── raw/
│   └── 20261121T013817Z_bench_mysql_3609b6.csv
├── summaries/
│   └── 20261121T013817Z_bench_mysql_3609b6.json
└── logs/
    └── 20261121T013817Z_bench_mysql_3609b6.log
reports/
└── 20261121T013817Z_bench_mysql_3609b6_summary.md
```

Fragmento real de `results/raw/20261121T013817Z_bench_mysql_3609b6.csv`:
```csv
run_id,engine,model,operation,iteration,is_warmup,latency_ms,ok,valid,timed_out,rows_returned,error
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R1_taxon_search,1,False,2.4614,True,True,False,1,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R2_filtered_assertions,1,False,2.8366,True,True,False,18,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R3_transactional_assertion_outbox,1,False,19.1385,True,True,False,1,
20261121T013817Z_bench_mysql_3609b6,mysql,relational,R4_batch_import_insert,1,False,17.0037,True,True,False,50,
```

Especificación completa en [`docs/results_format.md`](./docs/results_format.md).

---

## H. Limpieza

### 1. Limpiar solo registros de prueba dentro de un motor activo (conserva el contenedor)
```powershell
.\.venv\Scripts\python.exe -m biolink_bench clean-data --engine mysql
```
*(Con `--all` reinicia todas las tablas/colecciones/nodos de prueba en ese motor.)*

### 2. Detener un contenedor conservando su volumen
```powershell
docker compose --env-file .env -f docker/compose.yaml --profile mysql down
```

### 3. Detener un motor y **ELIMINAR SU VOLUMEN DE DATOS** (destructivo)
> **ADVERTENCIA:** La bandera `-v` borra permanentemente todos los datos almacenados en el volumen del candidato seleccionado (sin afectar los volúmenes de los otros cinco motores).

```powershell
docker compose --env-file .env -f docker/compose.yaml --profile mysql down -v
```

### 4. Limpieza global de todos los perfiles y resultados temporales (destructivo)
```powershell
# Detener todos los perfiles sin borrar datos ni resultados:
.\scripts\cleanup_all.ps1

# ADVERTENCIA: elimina TODOS los volúmenes de prueba de los 6 motores y/o los resultados exportados:
.\scripts\cleanup_all.ps1 -RemoveVolumes
.\scripts\cleanup_all.ps1 -RemoveVolumes -RemoveResults
```

---

## I. Solución de problemas

| Problema | Causa probable | Solución recomendada |
|---|---|---|
| **Puerto ocupado** | Ya existe otra instancia local de MySQL (`3306`), PostgreSQL (`5432`), MongoDB (`27017`), CouchDB (`5984`) o Neo4j/Memgraph (`7687`) o un proceso ocupando los puertos del benchmark (`3307`, `5433`, `27018`, `5985`, `7688`, `7689`). | Verifica con `netstat -ano` (Windows) o `ss -tulpn` (Linux), detén el otro servicio o ajusta el puerto correspondiente en `.env` (manteniendo `BENCH_BIND_HOST=127.0.0.1`). |
| **Contenedor sin memoria (`OOMKilled: true`)** | El motor superó su límite experimental (`768m` o `1024m`), frecuente si se excede el caché interno o en grafos in-memory con 50,000 afirmaciones. | **No aumentes `mem_limit`.** Registra el fallo como hallazgo experimental (`docker inspect <contenedor>`), limpia el volumen (`down -v`) y documenta en el reporte de campaña. |
| **Error de autenticación** | Contraseña en `.env` modificada después de haber creado el volumen del contenedor, o contraseña de Neo4j menor a 8 caracteres. | Verifica `.env` (Neo4j exige >= 8 caracteres), ejecuta `docker compose ... --profile <motor> down -v` para regenerar el volumen con las credenciales actuales y vuelve a levantar. |
| **Driver no instalado (`ModuleNotFoundError`)** | No activaste `.venv` o instalaste paquetes en el Python global en lugar del entorno virtual. | Ejecuta `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"` y ejecuta siempre mediante `.\.venv\Scripts\python.exe -m biolink_bench ...`. |
| **Motor no disponible / conexión rechazada** | El contenedor aún no termina su `start_period`, está detenido o intentas levantar un segundo motor cuando otro sigue corriendo. | Usa `docker ps` para confirmar que solo el motor esperado esté `healthy`; levanta con `up -d --wait`. |
| **Timeout en carga o consulta** | La operación excedió `BENCH_TIMEOUT_SECONDS` (por defecto `60 s`) debido a volumen alto o contención de memoria/E/S. | Revisa `results/logs/<run_id>.log` y `docker_resources.peak_memory_mib`; confirma que no haya procesos pesados en el host o ajusta solo si el protocolo de campaña lo justifica explícitamente. |
| **Espacio insuficiente en disco** | Múltiples imágenes Docker y volúmenes acumulados sin limpiar en el disco virtual de Docker Desktop. | Limpia volúmenes previos con `.\scripts\cleanup_all.ps1 -RemoveVolumes` y libera caché huérfana de Docker con `docker system prune` (sin borrar las imágenes ya descargadas si no agregas `-a`). |
| **Error de compatibilidad** | Cambios de imágenes o comportamiento del sistema anfitrión (p. ej. `mysql:8.4.12` no existe en Docker Hub → usar `mysql:8.4.13`; montajes `:ro` en CouchDB en Windows fallan `chmod` en entrypoint → `compose.yaml` genera `10-biolink.ini` dentro del contenedor; PostgreSQL 18+ requiere montar `/var/lib/postgresql`). | Usa siempre las definiciones fijadas en `docker/compose.yaml` y `.env.example`, y consulta [`docs/engine_matrix.md`](./docs/engine_matrix.md) para incidencias documentadas. |

---

## Documentación técnica adicional

- [`docs/benchmark_protocol.md`](./docs/benchmark_protocol.md): fases de medición, calentamiento y reglas de equidad.
- [`docs/engine_matrix.md`](./docs/engine_matrix.md): versiones fijadas, digests SHA256 y parámetros por motor.
- [`docs/data_strategy.md`](./docs/data_strategy.md): fixture científico de Etapa 1 y generador sintético.
- [`docs/workloads.md`](./docs/workloads.md): mapeo de `R1`–`R4`, `D1`–`D4`, `G1`–`G4` con `OP-01`–`OP-15`.
- [`docs/resource_limits.md`](./docs/resource_limits.md): presupuesto Docker (4 GB) y observaciones reales de memoria.
- [`docs/results_format.md`](./docs/results_format.md): estructura de CSV, JSON y reportes con ejemplo real.
# BioLink-benchmarking
