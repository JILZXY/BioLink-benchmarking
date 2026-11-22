# BioLink — Estructura y Responsabilidades de los Tres Repositorios

**Versión:** 1.0  
**Fecha:** 20 de noviembre de 2026  
**Estado:** Estructura oficial definida; implementación de `biolink-backend` y `biolink-frontend` pendiente; `biolink-benchmarking` en preparación independiente.

---

## 1. Adopción de tres repositorios y retiro de la estructura anterior

BioLink se compone exclusivamente de **tres repositorios independientes**:

1. **`biolink-frontend`**: cliente de usuario conectado exclusivamente por HTTP/REST.
2. **`biolink-backend`**: servicio único que integra API REST, lógica de negocio, repositorios, persistencia, auditoría y workers de sincronización.
3. **`biolink-benchmarking`**: entorno autónomo para evaluar y comparar los motores de base de datos candidatos mediante conexiones directas.

### Estructura declarada obsoleta

Queda **obsoleta** cualquier organización previa que incluyera:
- Directorios `backend/`, `api/` y `frontend/` coexistiendo como subproyectos separados dentro de un único repositorio `BioLink/`.
- Un directorio o proyecto independiente para `api/` separado del backend.
- Un `docker-compose.yml` único en la raíz del proyecto compartido entre la aplicación y el benchmark.

> **Nota sobre estado real:** En el espacio de trabajo actual (`BioLink/`) únicamente reside la carpeta documental `docs/`. No se ha iniciado todavía la creación de los repositorios `biolink-backend` ni `biolink-frontend`. Cualquier trabajo paralelo en curso del benchmark debe respetar la separación hacia `biolink-benchmarking` sin modificar sus configuraciones funcionales actuales.

---

## 2. Repositorio `biolink-frontend`

**Estado:** Pendiente de inicialización y desarrollo (Etapa 8).

### Responsabilidades
- Presentar vistas de búsqueda taxonómica, fichas de taxones, exploración de redes de interacción, detalle de evidencia/fuentes y comparación Montes Azules vs. Playón de la Gloria.
- Capturar filtros, formularios de curaduría/revisión y mostrar advertencias interpretativas (`RNF-09`, `RD-01`–`RD-16`).
- Consumir exclusivamente los endpoints HTTP/REST del contrato OpenAPI publicado por `biolink-backend`.

### Restricciones
- Sin drivers de MySQL, PostgreSQL, MongoDB, CouchDB, Neo4j ni Memgraph.
- Sin acceso a variables de entorno o secretos de bases de datos.
- El framework concreto de UI se definirá antes de iniciar la Etapa 8; la estructura interna es orientativa.

### Estructura orientativa

```text
biolink-frontend/
├── src/
│   ├── api-client/          # Cliente HTTP tipado generado o alineado al contrato OpenAPI
│   ├── features/
│   │   ├── taxonomy/        # Búsqueda y fichas de taxones (OP-01, OP-02)
│   │   ├── interactions/    # Listado, evidencias y filtros (OP-03, OP-04, OP-05)
│   │   ├── network-graph/   # Visualización de subredes y conectividad (OP-05, OP-06, OP-07)
│   │   ├── localities/      # Comparación Montes Azules vs. Playón de la Gloria (OP-06)
│   │   ├── sources/         # Consulta de estudios y licencias (OP-08)
│   │   └── curation/        # Flujos autenticados de ingestión y revisión (OP-09..OP-14)
│   ├── components/          # Componentes visuales y advertencias metodológicas
│   └── config/              # Configuración de URL base de API (BIOLINK_API_BASE_URL)
├── tests/
│   ├── unit/
│   └── e2e/                 # Pruebas contra contratos HTTP/REST de biolink-backend
├── docs/
│   └── ui-notes.md
├── .env.example
├── Dockerfile               # Opcional para servir cliente en despliegue independiente
└── README.md
```

---

## 3. Repositorio `biolink-backend`

**Estado:** Pendiente de inicialización hasta cerrar la selección de motores en `biolink-benchmarking` y el diseño físico (Etapas 4–7).

### Responsabilidades
- Alojar la **API REST** (FastAPI + Pydantic + OpenAPI versionado) y el **backend de aplicación** dentro del mismo repositorio.
- Implementar entidades y reglas del dominio (`RD-01`–`RD-16`) sin dependencias hacia drivers específicos desde la capa de dominio.
- Coordinar casos de uso (`OP-01`–`OP-15`) a través de servicios de aplicación.
- Encapsular el acceso a los tres motores definitivos en repositorios separados (relacional, documental y grafo).
- Gestionar importaciones, preservación de registros originales, auditoría (`review_event`), autenticación/autorización y sincronización mediante tabla outbox y workers internos.
- Definir y versionar los scripts físicos (`DDL`, colecciones/validadores, constraints/índices Cypher) una vez concluido el benchmark.

### Restricciones
- No mezcla archivos ni scripts de `biolink-benchmarking`.
- No expone directamente puertos de bases de datos hacia `biolink-frontend`.

### Estructura orientativa

```text
biolink-backend/
├── src/
│   ├── api/                 # API REST integrada (FastAPI, routers v1, schemas, auth, OpenAPI)
│   ├── domain/              # Entidades, vocabularios controlados y reglas RD-01..RD-16
│   ├── application/         # Servicios y casos de uso (taxonomy, interactions, curation, ingestion, projection)
│   ├── ports/               # Interfaces/contratos hacia repositorios y sincronización
│   ├── repositories/        # Adaptadores concretos hacia los 3 motores seleccionados
│   │   ├── relational/
│   │   ├── document/
│   │   └── graph/
│   └── workers/             # Worker de ingestión y worker de proyección outbox -> grafo
├── database/                # Diseño físico (Etapa 4-5) separado por modelo
│   ├── relational/          # DDL, migraciones, semillas controladas y consultas
│   ├── document/            # Validadores JSON Schema, índices y semillas
│   └── graph/               # Constraints, índices y scripts Cypher de proyección
├── contracts/
│   └── openapi-v1.json      # Contrato OpenAPI exportado/versionado para biolink-frontend
├── infra/
│   └── docker-compose.yaml  # Orquestación independiente del backend + 3 bases seleccionadas
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── acceptance/
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 4. Repositorio `biolink-benchmarking`

**Estado:** En desarrollo independiente; estructura, drivers, workloads y límites preservados sin alteraciones por esta revisión documental.

### Responsabilidades
- Conectarse directamente a los seis motores candidatos mediante controladores o protocolos nativos.
- Generar datasets sintéticos reproducibles (`SYNTHETIC_BENCHMARK`) y cargar el fixture científico de referencia.
- Ejecutar workloads equivalentes dentro de cada paradigma y medir latencia, throughput, uso de memoria/CPU y almacenamiento.
- Validar corrección de respuestas y exportar metadatos (JSON), métricas individuales (CSV) y reportes.

### Restricciones
- Dependencias Python (`pyproject.toml`) y configuración Docker (`docker/compose.yaml`) totalmente independientes de `biolink-backend` y `biolink-frontend`.
- Prohibido importar modelos, servicios, repositorios, ORM o endpoints de `biolink-backend`.

### Estructura de referencia

```text
biolink-benchmarking/
├── docker/
│   ├── compose.yaml         # Perfiles secuenciales aislados (1 candidato activo a la vez)
│   ├── relational/
│   ├── document/
│   └── graph/
├── datasets/
│   ├── scientific_fixture/  # Derivado trazable de 01_matriz_evidencias_biolink.csv
│   ├── synthetic/           # Volúmenes 1,000 / 10,000 / 50,000 (SYNTHETIC_BENCHMARK)
│   └── manifests/           # Semilla, conteos, versión del generador y checksums
├── drivers/                 # Adaptadores nativos directos (sin ORM de aplicación)
│   ├── relational/
│   │   ├── mysql/           # Conector nativo de Python
│   │   └── postgresql/      # psycopg
│   ├── document/
│   │   ├── mongodb/         # pymongo
│   │   └── couchdb/         # Interfaz HTTP nativa de CouchDB
│   └── graph/
│       ├── neo4j/           # Driver oficial de Python (Bolt)
│       └── memgraph/        # Cliente Bolt compatible
├── workloads/
│   ├── relational/
│   ├── document/
│   └── graph/
├── runners/
├── scripts/
├── tests/
├── results/
│   ├── raw/
│   ├── logs/
│   ├── summaries/
│   └── README.md
├── reports/
├── docs/                    # Documentación técnica propia del entorno de benchmark
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 5. Artefactos compartidos y gobierno documental

Al operar como tres repositorios independientes, la coordinación entre proyectos se limita a artefactos versionados sin acoplamiento de código:

| Artefacto | Origen autorizado | Consumidor | Mecanismo |
|---|---|---|---|
| Especificación OpenAPI (`openapi-v1.json`) | `biolink-backend` | `biolink-frontend` | Publicación/exportación desde `biolink-backend` por versión (`/api/v1`). |
| Matriz de evidencias (`01_matriz_evidencias_biolink.csv`) y catálogo (`02_catalogo_operaciones_biolink.csv`) | Documentación de diseño | `biolink-backend` y `biolink-benchmarking` | Referencia documental o copia versionada con checksum verificable; `biolink-benchmarking` no importa código del backend. |
| Reportes de resultados del benchmark | `biolink-benchmarking` | Documentación / decisión de Etapa 3–4 | Evidencia empírica para confirmar o ajustar la selección de motores en `biolink-backend`. |

---

## 6. Correspondencia con la guía académica del proyecto

La sección 10 de [Guia_Proyecto_Final_Bases_Datos.pdf](./Guia_Proyecto_Final_Bases_Datos.pdf) propone una estructura orientativa adaptable al stack elegido. La tabla siguiente muestra cómo los entregables de la guía se mapean sin pérdida sobre la arquitectura oficial de tres repositorios:

| Elemento de la guía académica | Ubicación en la arquitectura oficial de BioLink |
|---|---|
| `docs/` (propuesta, modelos, arquitectura, decisiones, API, pruebas) | Documentación transversal en `docs/` (y documentación específica en cada repositorio). |
| `database/` (esquemas, validadores, datos, consultas de las 3 bases) | Dentro de `biolink-backend/database/` (y su contraparte de evaluación comparativa en `biolink-benchmarking/`). |
| `backend/` (`controllers`, `services`, `repositories`) + API | Unificados dentro de `biolink-backend/src/` (`api/`, `domain/`, `application/`, `repositories/`, `workers/`). |
| `frontend/` | Repositorio independiente `biolink-frontend`. |
| `tests/` (`unit`, `integration`, `e2e`) | Distribuidos según responsabilidad en cada repositorio (`biolink-backend/tests/`, `biolink-frontend/tests/`, `biolink-benchmarking/tests/`). |
| `.env.example`, `docker-compose`, `README.md` | Independientes en cada uno de los tres repositorios. |

---

## 7. Inconsistencias pendientes y correcciones propuestas (sin aplicar automáticamente)

De acuerdo con el principio de no alterar configuraciones ni código en desarrollo del benchmark y no inventar código inexistente, se registran las siguientes observaciones abiertas para revisión del equipo:

1. **Estado del espacio de trabajo actual (`BioLink/`):** en el directorio raíz inspeccionado solo existe actualmente `docs/`. Si el entorno de benchmarking se está desarrollando en paralelo fuera de esta carpeta o bajo un subdirectorio `benchmarking/` heredado de la arquitectura previa, **no se ha tocado**.
   - **Corrección propuesta:** al consolidar el repositorio independiente `biolink-benchmarking`, promover el contenido de `benchmarking/` al directorio raíz de ese repositorio (conservando intactos `drivers/`, `workloads/`, `datasets/`, `docker/`, `runners/`, `scripts/`, `results/` y sus límites de memoria), sin crear ni arrastrar carpetas `backend/`, `api/` o `frontend/` dentro de él.
2. **Alojamiento definitivo de `docs/` transversal:** cuando existan los tres repositorios Git separados (`biolink-frontend`, `biolink-backend`, `biolink-benchmarking`), deberá decidirse si `docs/` permanece en un repositorio paraguas/documental de BioLink o si su núcleo de arquitectura reside en `biolink-backend` con enlaces explícitos desde los otros dos repositorios.
3. **Ubicación de la documentación propia de `biolink-benchmarking`:** el diseño de `biolink-benchmarking` contempla manuales operativos locales (`README.md` de ejecución/limpieza y `docs/` internos de protocolo, límites y workloads). Debe mantenerse sincronizada la referencia hacia [benchmarking.md](./benchmarking.md) sin duplicar definiciones contradictorias sobre límites de memoria o versiones de imagen.
4. **Cierre de selección de motores:** la carpeta `database/` y los adaptadores de `biolink-backend` solo deben concretarse después de ejecutar la campaña en `biolink-benchmarking` y cerrar la decisión de los tres motores ganadores.
