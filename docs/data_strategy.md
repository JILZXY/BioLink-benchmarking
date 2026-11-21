# Estrategia de Datos de Prueba (`biolink-benchmarking`)

Los datos utilizados por `biolink-benchmarking` se dividen en **dos grupos estrictamente separados** para preservar la integridad científica del dominio y medir la escalabilidad del rendimiento.

---

## 1. Fixture Científico de Referencia (`SCIENTIFIC_FIXTURE`)

Ubicación: `datasets/scientific_fixture/biolink_scientific_fixture.json` y `datasets/scientific_fixture/manifest.json`.

### Origen y trazabilidad
Derivado exclusivamente de las evidencias primarias documentadas en la Etapa 1 del proyecto BioLink:
- **Olea-Wagner et al. (2007)** (`BAT2007`, DOI: `10.22201/ib.20078706e.2007.001.393`): semillas identificadas en excretas (`FECAL_SEED_IDENTIFICATION`) de tres murciélagos frugívoros en el sector sur de Montes Azules y en el Ejido Playón de la Gloria.
- **Camargo-Sanabria y Mendoza (2016)** (`MAMMAL2016`, DOI: `10.1016/j.actao.2016.02.005`): cámaras trampa (`CAMERA_TRAP`) en *Licania platypus* y *Pouteria sapota* dentro de la Reserva de la Biosfera Montes Azules.

### Invariantes verificadas automáticamente (`tests/test_scientific_fixture.py`)
1. **Conservación literal de procedencia:** todas las afirmaciones conservan `source_id`, `source_locator`, `method_code`, `period_start`/`period_end`, `season_label` e `interpretation_limit`.
2. **Separación espacial estricta:** `LOC_RBMA_SOUTH` (`INSIDE_ANP`) y `LOC_PDLG` (`OUTSIDE_ANP`) se mantienen separadas; nunca se mezclan registros de Playón de la Gloria dentro de Montes Azules.
3. **Preservación taxonómica honesta:** taxones reportados a nivel género o morfoespecie (`Ficus sp.`, `Clidemia sp.`, `Piper sp. (morfoespecie 2)`, `Piper sp. (morfoespecie 3)`) y grafías de fuente (`Ficus lundelli`, `Solanum rudepanum`, `Solanum ochraceo-frrugineum`) se conservan sin inventar epítetos ni crear interacciones no documentadas.
4. **Presencia != interacción:** los taxones vegetales mencionados en el cuadro del estudio que no tienen afirmación en la matriz de evidencias permanecen únicamente como nodos/registros taxonómicos sin aristas inventadas.
5. **Conteos verificados:** 2 fuentes, 2 localidades, 32 taxones (11 animales + 21 plantas) y **21 afirmaciones publicadas** (7 derivadas de `BAT2007` desdoblando los registros separados por localidad de *Artibeus lituratus*, más 14 de `MAMMAL2016`).

---

## 2. Dataset Sintético Reproducible (`SYNTHETIC_BENCHMARK`)

Implementado en `src/biolink_bench/datasets/synthetic_generator.py` (`GENERATOR_VERSION = "1.0.0"`).

### Características obligatorias
- **Determinismo por semilla:** utiliza exclusivamente `random.Random(seed)` (valor por defecto `BENCH_SEED=20261120`). Dos ejecuciones con la misma semilla y volumen generan exactamente las mismas entidades, identificadores y relaciones.
- **Volúmenes soportados:** `1,000`, `10,000` y `50,000` afirmaciones sintéticas (también admite volúmenes menores en pruebas unitarias).
- **Identificación explícita:** todas las entidades incluyen `dataset_tag = "SYNTHETIC_BENCHMARK"` y prefijos `SYN_`.
- **Cero reutilización de nombres científicos reales:** utiliza nombres ficticios (`Synthetica animalis_XXXXX`, `Botanica synthetica_XXXXX`, `SynGenus_... sp.`, `SynAlias_..._old`).
- **Coherencia referencial entre modelos:**
  - **Relacional:** genera `source`, `source_version`, `locality`, `taxon`, `taxon_name` (nombre aceptado + sinónimo), `taxon_identifier`, `evidence`, `interaction_type`, `interaction_assertion` (con mezcla realista de estados: ~85% `PUBLISHED` y ~15% `IN_REVIEW`/`DRAFT`/`WITHDRAWN`), `assertion_evidence`, `import_batch`, `import_record` y `review_event`.
  - **Documental:** genera `taxon_dossiers`, `study_dossiers` y `raw_source_records` con el mismo `taxon_id`, `source_id` e `import_batch_id`.
  - **Grafo:** proyecta **únicamente afirmaciones con estado `PUBLISHED`** (`bundle.published_assertions`), manteniendo fuera del grafo los borradores, revisiones pendientes y registros retirados.

### Manifiesto y checksums
Al ejecutar `biolink-bench generate-data --volume <N> --seed <S>`, se escriben archivos `.jsonl` en `datasets/synthetic/<dataset_id>/` y un manifiesto en `datasets/manifests/<dataset_id>_manifest.json` que registra:
- `dataset_id`, `dataset_tag`, `generator_version`
- `seed`, `target_assertions`, `generated_at_utc`
- `parameters`
- `entity_counts` (conteo exacto por cada entidad)
- `files` (tamaño en bytes y `sha256` por archivo para verificar integridad al recargar).
