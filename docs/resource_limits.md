# Límites de Recursos y Reglas de Docker (`biolink-benchmarking`)

## 1. Presupuesto experimental acordado

Las restricciones de recursos forman parte integral del experimento de BioLink:

| Categoría / elemento | Límite fijado | Regla operativa |
|---|---:|---|
| Techo global del entorno | **4,096 MB (4 GB)** | Ninguna corrida debe exceder 4 GB de contenedores activos. |
| Relacional (`mysql`, `postgresql`) | **768 MB** por contenedor | Solo uno levantado a la vez. |
| Documental (`mongodb`, `couchdb`) | **768 MB** por contenedor | Solo uno levantado a la vez. |
| Grafo (`neo4j`, `memgraph`) | **1,024 MB** por contenedor | Solo uno levantado a la vez. |
| Duración máxima de campaña completa | **120 minutos** | Ejecución secuencial con topes por bloque. |
| Puertos en host | Solo `127.0.0.1` | Prohibido exponer `0.0.0.0` o interfaces externas. |

---

## 2. Reglas de aislamiento y política ante fallos

1. **Ejecución estrictamente secuencial:** tanto `docker/compose.yaml` (mediante `profiles`) como `runners/lifecycle.py` (`ensure_exclusive_engine`) impiden levantar un motor mientras exista otro contenedor `biolink-bench-*` corriendo.
2. **Volúmenes independientes:** cada motor usa su propio volumen nombrado (`mysql_bench_data`, `postgresql_bench_data`, `mongodb_bench_data`, `couchdb_bench_data`, `neo4j_bench_data`, `memgraph_bench_data`).
3. **Sin aumento automático de memoria:** si un motor falla al iniciar, sufre `OOMKilled` o agota la memoria durante carga o consultas bajo `768m` / `1024m`, **el límite no se aumenta automáticamente**; el evento se registra como resultado experimental válido.
4. **Puertos locales desplazados:** se asignan puertos en `127.0.0.1` (`3307`, `5433`, `27018`, `5985`, `7688`/`7475`, `7689`) para evitar conflictos con instancias locales estándar (`3306`, `5432`, `27017`, `5984`, `7687`).

---

## 3. Observaciones medidas durante la validación técnica secuencial

Mediciones obtenidas en `Windows 11` (`Docker Desktop 29.7.2`, `WSL2`, `7.615 GiB` asignados a Docker) durante `smoke` y la comprobación ligera con el fixture científico (`21` afirmaciones):

| Motor | Límite (`mem_limit`) | Pico RAM en `smoke` (MiB) | Pico RAM en fixture (MiB) | `OOMKilled` | Estado observado |
|---|---:|---:|---:|---|---|
| `mysql` (`8.4.13`) | `768 MB` | `445.90` | `451.20` | `False` | Saludable; consumo estable (~59% del límite). |
| `postgresql` (`18.7`) | `768 MB` | `57.98` | `58.94` | `False` | Saludable; huella base muy baja (<8% del límite). |
| `mongodb` (`8.0.38`) | `768 MB` | `299.00` | `206.50` | `False` | Saludable con `--wiredTigerCacheSizeGB 0.25`. |
| `couchdb` (`3.5.3`) | `768 MB` | `154.10` | `163.90` | `False` | Saludable tras corregir la generación interna de `10-biolink.ini`. |
| `neo4j` (`2026.10.2-community`) | `1,024 MB` | `663.60` | `710.40` | `False` | Saludable; mayor consumo base (~69% del límite) por JVM + page cache. |
| `memgraph` (`3.14.0`) | `1,024 MB` | `62.96` | `72.10` | `False` | Saludable en arranque y fixture con `--memory-limit=800`; falta evaluar presión bajo 50,000 afirmaciones. |

> **Nota para la futura campaña completa:** Neo4j ya ocupa ~`700 MiB` de `1,024 MiB` con el fixture pequeño y Memgraph almacena el grafo completo en RAM; ambos deberán vigilarse estrechamente al cargar el volumen de `50,000` afirmaciones en la campaña oficial.
