# Documentación de BioLink

**Proyecto:** BioLink — Explorador de biodiversidad e interacciones ecológicas  
**Arquitectura oficial:** Arquitectura orientada a servicios (SOA) en **tres repositorios independientes**  
**Fecha de actualización documental:** 20 de noviembre de 2026  
**Estado actual:** Documentación de dominio, requisitos y arquitectura actualizada a tres repositorios; diseño físico, desarrollo de `biolink-backend` y `biolink-frontend`, y ejecución completa del benchmark pendientes.

---

## 1. Visión general de la arquitectura

BioLink adopta una **arquitectura oficial de tres repositorios independientes** orientada a servicios:

| Repositorio | Responsabilidad principal | Comunicación / conectividad |
|---|---|---|
| `biolink-frontend` | Interfaz de usuario, visualización de taxones, interacciones y grafos, formularios y filtros. | Se comunica **únicamente** con `biolink-backend` mediante HTTP/REST. Nunca se conecta directamente a las bases de datos. |
| `biolink-backend` | API REST (FastAPI), controladores/endpoints, servicios y reglas de negocio, repositorios, auditoría, sincronización del grafo (outbox/workers) y autenticación/autorización. | Expone contratos HTTP/REST + OpenAPI versionados hacia `biolink-frontend` y accede a los tres motores mediante drivers nativos o capas de persistencia propias. **La API forma parte de este repositorio y no es un proyecto separado.** |
| `biolink-benchmarking` | Entorno independiente para comparar motores candidatos mediante datasets científicos y sintéticos, workloads, medición de recursos y validación de resultados. | Se conecta **directamente** a cada motor candidato mediante drivers o protocolos nativos. Prohibido depender de `biolink-backend`, FastAPI o servicios/ORM de la aplicación. |

> **Nota sobre cambios arquitectónicos:** La organización previa contemplada en documentos anteriores (`BioLink/` con carpetas `backend/`, `api/`, `frontend/` y `benchmarking/` en un mismo repositorio, o la API como proyecto separado) queda **obsoleta** y ha sido reemplazada por esta arquitectura de tres repositorios independientes. El contenido de dominio, las reglas ecológicas (`RD-01` a `RD-16`), los requisitos (`RF-01` a `RF-16`), el catálogo de operaciones (`OP-01` a `OP-15`), los modelos lógicos y los límites de recursos del benchmark permanecen intactos.

---

## 2. Índice de documentación

### 2.1 Documentación arquitectónica y operativa vigente

| Documento | Propósito | Alcance principal |
|---|---|---|
| [architecture.md](./architecture.md) | Arquitectura oficial global de BioLink | Definición SOA de los tres repositorios, esquema de comunicación, contratos HTTP/REST y OpenAPI, límites de dependencia, fuente de verdad, ADRs y estrategia de pruebas. |
| [repository_structure.md](./repository_structure.md) | Estructura y gobierno de repositorios | Responsabilidades detalladas, árboles orientativos de carpetas de `biolink-frontend`, `biolink-backend` y `biolink-benchmarking`, artefactos compartidos e inconsistencias pendientes. |
| [deployment.md](./deployment.md) | Despliegue independiente e integración | Reglas de Docker Compose separado por repositorio, límites de memoria (4 GB totales), puertos en loopback, variables de entorno y comunicación entre proyectos. |
| [benchmarking.md](./benchmarking.md) | Especificación del entorno de benchmarking | Independencia total respecto al backend/API, seis motores candidatos, drivers nativos, fixture científico, generador sintético, workloads derivados de `OP-01`–`OP-15` y protocolo de medición. |

### 2.2 Documentos de etapas previas, catálogos y guía académica

| Documento | Etapa / tipo | Estado y observaciones |
|---|---|---|
| [01_etapa_1_biolink.md](./01_etapa_1_biolink.md) | Etapa 1: Definición e investigación del dominio | Completada y preservada sin modificaciones. Delimita Montes Azules vs. Playón de la Gloria, frugivoría y evidencia primaria. |
| [01_matriz_evidencias_biolink.csv](./01_matriz_evidencias_biolink.csv) | Anexo Etapa 1: Matriz de evidencias | Fuente de referencia para el fixture científico del dominio (Olea-Wagner et al., 2007; Camargo-Sanabria & Mendoza, 2016). Preservado sin cambios. |
| [02_etapa_2_modelado_y_requisitos_biolink.md](./02_etapa_2_modelado_y_requisitos_biolink.md) | Etapa 2: Modelado lógico y requisitos | Preservada en su modelado lógico, reglas `RD-01`–`RD-16` y requisitos; incluye nota de alineación hacia los tres repositorios independientes. |
| [02_catalogo_operaciones_biolink.csv](./02_catalogo_operaciones_biolink.csv) | Anexo Etapa 2: Catálogo de operaciones | Especifica `OP-01` a `OP-15`, entradas, validaciones, modelos participantes y criterios de aceptación. Preservado sin cambios. |
| [03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md](./03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md) | Etapa 3: Arquitectura y selección tecnológica (v1.1) | Actualizada a v1.1 para reflejar los tres repositorios independientes y la API unificada en `biolink-backend`, conservando comparativas de motores, presupuestos de recursos y protocolo de benchmark. |
| [03_matriz_comparativa_motores_biolink.csv](./03_matriz_comparativa_motores_biolink.csv) | Anexo Etapa 3: Comparativa de motores | Evaluación documental previa de MySQL 8.4 LTS, PostgreSQL 18.7, MongoDB 8.0, CouchDB 3.5.3, Neo4j Community y Memgraph Community. Preservado sin cambios. |
| [Guia_Proyecto_Final_Bases_Datos.pdf](./Guia_Proyecto_Final_Bases_Datos.pdf) | Guía institucional del proyecto | Material de orientación académica de la Universidad Politécnica de Chiapas (2026). |

---

## 3. Guía de lectura recomendada

### Para revisión académica o evaluación general
1. Leer [01_etapa_1_biolink.md](./01_etapa_1_biolink.md) y [02_etapa_2_modelado_y_requisitos_biolink.md](./02_etapa_2_modelado_y_requisitos_biolink.md) para comprender el dominio ecológico, las reglas y los tres modelos lógicos.
2. Leer [architecture.md](./architecture.md) y [repository_structure.md](./repository_structure.md) para revisar la arquitectura oficial en tres repositorios independientes.
3. Consultar [03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md](./03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md) y [deployment.md](./deployment.md) para la preselección tecnológica, la estrategia de consistencia y las restricciones operativas.

### Para el desarrollo y ejecución de `biolink-benchmarking`
1. Revisar [benchmarking.md](./benchmarking.md) y la sección 9 de [03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md](./03_etapa_3_arquitectura_y_seleccion_tecnologica_biolink.md).
2. Consultar [01_matriz_evidencias_biolink.csv](./01_matriz_evidencias_biolink.csv) para el fixture científico y [02_catalogo_operaciones_biolink.csv](./02_catalogo_operaciones_biolink.csv) para la semántica de los workloads.
3. Verificar límites de memoria y reglas de Docker en [deployment.md](./deployment.md).

### Para la futura implementación de `biolink-backend`
1. Revisar las responsabilidades y límites en [architecture.md](./architecture.md) y la organización interna en [repository_structure.md](./repository_structure.md).
2. Confirmar los modelos lógicos, reglas `RD-01`–`RD-16`, políticas de outbox y catálogo `OP-01`–`OP-15` en [02_etapa_2_modelado_y_requisitos_biolink.md](./02_etapa_2_modelado_y_requisitos_biolink.md) y [02_catalogo_operaciones_biolink.csv](./02_catalogo_operaciones_biolink.csv).
3. Esperar el cierre del benchmark empírico antes de iniciar la Etapa 4 (diseño físico) y la programación de persistencia/API.

### Para la futura implementación de `biolink-frontend`
1. Revisar [architecture.md](./architecture.md) (sección de contratos HTTP/REST y OpenAPI) y [deployment.md](./deployment.md).
2. Consultar los flujos de usuario y restricciones de claridad científica (`RNF-09`, `RD-01`–`RD-16`) en [02_etapa_2_modelado_y_requisitos_biolink.md](./02_etapa_2_modelado_y_requisitos_biolink.md).

---

## 4. Estado actual del proyecto y pendientes

- **Documentación de etapas 1 a 3 y arquitectura SOA:** elaborada y alineada en este directorio (`docs/`).
- **Entorno `biolink-benchmarking`:** arquitectura y protocolo documentados; la implementación en repositorio independiente está en desarrollo por separado y la campaña completa de hasta 120 minutos aún no se ejecuta (no existen resultados empíricos ni ganador definitivo por paradigma). En este espacio de trabajo (`BioLink/`) no se encuentra actualmente código fuente de los repositorios ejecutables.
- **Repositorios `biolink-backend` y `biolink-frontend`:** diseño físico, programación de API REST, servicios, repositorios e interfaz de usuario **pendientes** hasta completar la validación empírica de los motores.
