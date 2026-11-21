from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle

GENERATOR_VERSION = "1.0.0"
SYNTHETIC_TAG = "SYNTHETIC_BENCHMARK"
ALLOWED_VOLUMES = (1000, 10000, 50000)

INTERACTION_TYPES = [
    {
        "interaction_type_id": "IT_CONSUMES_FRUIT",
        "code": "CONSUMES_FRUIT_OF",
        "label": "Consume fruto de",
        "definition": "La fuente documenta consumo de fruto.",
        "actor_role": "ANIMAL",
        "target_role": "PLANT",
        "is_active": True,
    },
    {
        "interaction_type_id": "IT_REMOVES_FRUIT",
        "code": "REMOVES_FRUIT_OF",
        "label": "Remueve fruto de",
        "definition": "La fuente distingue la remoción del consumo.",
        "actor_role": "ANIMAL",
        "target_role": "PLANT",
        "is_active": True,
    },
    {
        "interaction_type_id": "IT_CONSUMES_OR_REMOVES",
        "code": "CONSUMES_OR_REMOVES_FRUIT_OF",
        "label": "Consume o remueve fruto de",
        "definition": "La fuente presenta ambas conductas combinadas o no permite separarlas.",
        "actor_role": "ANIMAL",
        "target_role": "PLANT",
        "is_active": True,
    },
]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_synthetic_bundle(
    target_assertions: int = 1000,
    seed: int = 20261120,
    timestamp_iso: str | None = None,
) -> DatasetBundle:
    """Generador determinista de entidades BioLink etiquetadas SYNTHETIC_BENCHMARK."""
    if target_assertions < 10:
        raise ValueError("target_assertions debe ser al menos 10")

    rng = random.Random(seed)
    ts = timestamp_iso or "2026-11-20T00:00:00Z"
    dataset_id = f"synthetic_{target_assertions}_seed_{seed}"

    num_animals = max(10, min(500, target_assertions // 10))
    num_plants = max(15, min(800, target_assertions // 8))
    num_sources = max(4, min(40, target_assertions // 250 + 3))
    num_localities = 6

    localities = [
        {
            "locality_id": "SYN_LOC_001",
            "name": "SYNTHETIC_BENCHMARK Sector Core A",
            "locality_type": "STUDY_AREA",
            "parent_locality_id": None,
            "protected_status": "PROTECTED_ANP",
            "spatial_validation_status": "INSIDE_ANP",
            "geometry_reference": None,
            "coordinate_precision": "SYNTHETIC_SECTOR",
            "source_id": "SYN_SRC_001",
            "dataset_tag": SYNTHETIC_TAG,
        },
        {
            "locality_id": "SYN_LOC_002",
            "name": "SYNTHETIC_BENCHMARK Sector Core B",
            "locality_type": "STUDY_AREA",
            "parent_locality_id": "SYN_LOC_001",
            "protected_status": "PROTECTED_ANP",
            "spatial_validation_status": "INSIDE_ANP",
            "geometry_reference": None,
            "coordinate_precision": "SYNTHETIC_SECTOR",
            "source_id": "SYN_SRC_001",
            "dataset_tag": SYNTHETIC_TAG,
        },
        {
            "locality_id": "SYN_LOC_003",
            "name": "SYNTHETIC_BENCHMARK External Zone A",
            "locality_type": "EJIDO",
            "parent_locality_id": None,
            "protected_status": "EXTERNAL_ZONE",
            "spatial_validation_status": "OUTSIDE_ANP",
            "geometry_reference": None,
            "coordinate_precision": "SYNTHETIC_LOCALITY",
            "source_id": "SYN_SRC_002",
            "dataset_tag": SYNTHETIC_TAG,
        },
        {
            "locality_id": "SYN_LOC_004",
            "name": "SYNTHETIC_BENCHMARK External Zone B",
            "locality_type": "EJIDO",
            "parent_locality_id": None,
            "protected_status": "EXTERNAL_ZONE",
            "spatial_validation_status": "OUTSIDE_ANP",
            "geometry_reference": None,
            "coordinate_precision": "SYNTHETIC_LOCALITY",
            "source_id": "SYN_SRC_002",
            "dataset_tag": SYNTHETIC_TAG,
        },
        {
            "locality_id": "SYN_LOC_005",
            "name": "SYNTHETIC_BENCHMARK Adjacent Buffer",
            "locality_type": "STUDY_SITE",
            "parent_locality_id": None,
            "protected_status": "ADJACENT_ZONE",
            "spatial_validation_status": "ADJACENT",
            "geometry_reference": None,
            "coordinate_precision": "SYNTHETIC_SITE",
            "source_id": "SYN_SRC_003",
            "dataset_tag": SYNTHETIC_TAG,
        },
        {
            "locality_id": "SYN_LOC_006",
            "name": "SYNTHETIC_BENCHMARK Undetermined Area",
            "locality_type": "OTHER",
            "parent_locality_id": None,
            "protected_status": "UNDETERMINED",
            "spatial_validation_status": "UNDETERMINED",
            "geometry_reference": None,
            "coordinate_precision": "UNKNOWN",
            "source_id": "SYN_SRC_003",
            "dataset_tag": SYNTHETIC_TAG,
        },
    ][:num_localities]

    sources: list[dict[str, Any]] = []
    source_versions: list[dict[str, Any]] = []
    study_dossiers: list[dict[str, Any]] = []
    methods_pool = ["FECAL_SEED_IDENTIFICATION", "CAMERA_TRAP", "FIELD_OBSERVATION", "DATASET_RECORD"]

    for i in range(1, num_sources + 1):
        src_id = f"SYN_SRC_{i:03d}"
        year = 2005 + (i % 20)
        method = methods_pool[i % len(methods_pool)]
        sources.append(
            {
                "source_id": src_id,
                "source_type": "PUBLICATION" if i % 2 else "DATASET",
                "title": f"SYNTHETIC_BENCHMARK Ecological Study {i:03d}",
                "authors": f"SynthAuthor_{i:03d} et al.",
                "publication_year": year,
                "doi": f"10.99999/syn.{seed}.{i:03d}",
                "uri": f"https://synthetic.biolink.local/sources/{src_id}",
                "publisher": "SYNTHETIC_BENCHMARK",
                "citation_text": f"SynthAuthor_{i:03d} ({year}) [SYNTHETIC_BENCHMARK]",
                "license_id": "CC-BY-4.0-SYNTHETIC",
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        source_versions.append(
            {
                "source_version_id": f"SYN_SV_{i:03d}_V1",
                "source_id": src_id,
                "provider_version": f"syn-v{GENERATOR_VERSION}",
                "release_date": f"{year}-06-01",
                "endpoint_or_file": f"synthetic://seed-{seed}/{src_id}.jsonl",
                "query_parameters": json.dumps({"seed": seed, "volume": target_assertions}),
                "filters": json.dumps({"dataset_tag": SYNTHETIC_TAG}),
                "license_id": "CC-BY-4.0-SYNTHETIC",
                "checksum": hashlib.sha256(f"{seed}:{src_id}".encode("utf-8")).hexdigest(),
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        study_dossiers.append(
            {
                "_id": src_id,
                "source_id": src_id,
                "document_type": "study_dossier",
                "schema_version": 1,
                "dataset_tag": SYNTHETIC_TAG,
                "title": f"SYNTHETIC_BENCHMARK Study Dossier {i:03d}",
                "methods": [method],
                "localities": [localities[i % len(localities)]["locality_id"]],
                "limitations": "Datos sintéticos generados exclusivamente para benchmark de rendimiento.",
            }
        )

    taxa: list[dict[str, Any]] = []
    taxon_names: list[dict[str, Any]] = []
    taxon_identifiers: list[dict[str, Any]] = []
    taxon_dossiers: list[dict[str, Any]] = []
    animal_ids: list[str] = []
    plant_ids: list[str] = []

    habitats = ["SYN_HABITAT_SELVA_ALTA", "SYN_HABITAT_ACAHUAL", "SYN_HABITAT_RIBERA"]
    diets = ["SYN_DIET_FRUGIVORE", "SYN_DIET_MIXED_FRUIT"]

    def _register_taxon(idx: int, group: str) -> str:
        prefix = "AN" if group == "ANIMAL" else "PL"
        taxon_id = f"SYN_TAX_{prefix}_{idx:05d}"
        canonical = (
            f"Synthetica animalis_{idx:05d}" if group == "ANIMAL" else f"Botanica synthetica_{idx:05d}"
        )
        src = sources[idx % len(sources)]["source_id"]
        rank = "GENUS" if idx % 17 == 0 else "SPECIES"
        if rank == "GENUS":
            canonical = f"SynGenus_{prefix}_{idx:05d} sp."

        taxa.append(
            {
                "taxon_id": taxon_id,
                "accepted_name": canonical,
                "scientific_authorship": f"SynAuth, {2000 + (idx % 25)}",
                "taxonomic_rank": rank,
                "organism_group": group,
                "taxonomic_status": "ACCEPTED" if rank == "SPECIES" else "UNRESOLVED_TO_SPECIES",
                "created_at": ts,
                "updated_at": ts,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        taxon_names.append(
            {
                "taxon_name_id": f"SYN_TN_{prefix}_{idx:05d}_ACC",
                "taxon_id": taxon_id,
                "name": canonical,
                "name_usage": "ACCEPTED",
                "language": "la",
                "source_id": src,
                "is_preferred": True,
                "verbatim_name": canonical,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        synonym_name = f"SynAlias_{prefix}_{idx:05d}_old"
        taxon_names.append(
            {
                "taxon_name_id": f"SYN_TN_{prefix}_{idx:05d}_SYN",
                "taxon_id": taxon_id,
                "name": synonym_name,
                "name_usage": "SYNONYM",
                "language": "la",
                "source_id": src,
                "is_preferred": False,
                "verbatim_name": synonym_name,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        taxon_identifiers.append(
            {
                "taxon_identifier_id": f"SYN_TID_{prefix}_{idx:05d}",
                "taxon_id": taxon_id,
                "scheme": "SYNTHETIC_CATALOG",
                "external_id": f"SYN-EXT-{prefix}-{seed}-{idx:05d}",
                "retrieved_at": ts,
                "source_id": src,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        loc_ref = localities[idx % len(localities)]["locality_id"]
        habitat_val = habitats[idx % len(habitats)]
        diet_val = diets[idx % len(diets)] if group == "ANIMAL" else "SYN_PRODUCER"
        taxon_dossiers.append(
            {
                "_id": taxon_id,
                "taxon_id": taxon_id,
                "document_type": "taxon_dossier",
                "schema_version": 1,
                "dataset_tag": SYNTHETIC_TAG,
                "accepted_name": canonical,
                "taxonomic_rank": rank,
                "organism_group": group,
                "summary": {
                    "description": {
                        "value": f"SYNTHETIC_BENCHMARK dossier for {canonical}",
                        "source_refs": [src],
                        "locators": [f"Table S{(idx % 5) + 1}"],
                    }
                },
                "sections": {
                    "morphology": [f"SYN_MORPH_TRAIT_{idx % 7}"],
                    "ecology": {
                        "habitats": [habitat_val],
                        "diet": [diet_val],
                        "activity_patterns": ["NOCTURNAL" if idx % 2 == 0 else "DIURNAL"],
                        "notes": [f"Generated deterministically with seed={seed}"],
                    },
                    "conservation": [{"category": f"SYN_STATUS_{idx % 4}"}],
                    "distribution": [{"locality_ref": loc_ref}],
                },
                "claims": [
                    {
                        "claim_id": f"SYN_CLM_{prefix}_{idx:05d}_1",
                        "field": "ecology.diet",
                        "value": diet_val,
                        "source_id": src,
                        "source_locator": f"p. {10 + (idx % 90)}",
                    },
                    {
                        "claim_id": f"SYN_CLM_{prefix}_{idx:05d}_2",
                        "field": "ecology.habitats",
                        "value": habitat_val,
                        "source_id": src,
                        "source_locator": f"p. {10 + (idx % 90)}",
                    },
                ],
                "media": [],
                "document_version": 1,
                "updated_at": ts,
            }
        )
        return taxon_id

    for i in range(1, num_animals + 1):
        animal_ids.append(_register_taxon(i, "ANIMAL"))
    for i in range(1, num_plants + 1):
        plant_ids.append(_register_taxon(i, "PLANT"))

    seasons = [
        ("2020-01", "2020-03", "Dry season, Jan-Mar 2020"),
        ("2020-05", "2020-07", "Rainy season, May-Jul 2020"),
        ("2022-01", "2022-03", "Dry season, Jan-Mar 2022"),
        ("2022-05", "2022-07", "Rainy season, May-Jul 2022"),
    ]
    statuses = ["PUBLISHED"] * 17 + ["IN_REVIEW", "DRAFT", "WITHDRAWN"]

    evidences: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    assertion_evidences: list[dict[str, Any]] = []
    review_events: list[dict[str, Any]] = []
    import_batches: list[dict[str, Any]] = []
    import_records: list[dict[str, Any]] = []
    raw_source_records: list[dict[str, Any]] = []

    batch_size = max(100, target_assertions // 10)
    num_batches = (target_assertions + batch_size - 1) // batch_size
    for b in range(1, num_batches + 1):
        src = sources[(b - 1) % len(sources)]
        start_idx = (b - 1) * batch_size + 1
        end_idx = min(target_assertions, b * batch_size)
        count = end_idx - start_idx + 1
        import_batches.append(
            {
                "import_batch_id": f"SYN_IB_{b:04d}",
                "source_id": src["source_id"],
                "source_version_id": f"SYN_SV_{((b - 1) % len(sources)) + 1:03d}_V1",
                "started_by": "USR_BENCH_CURATOR",
                "started_at": ts,
                "finished_at": ts,
                "query_parameters": json.dumps({"seed": seed, "batch": b}),
                "filters": json.dumps({"dataset_tag": SYNTHETIC_TAG}),
                "status": "COMPLETED",
                "received_count": count,
                "accepted_count": count,
                "rejected_count": 0,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )

    for idx in range(1, target_assertions + 1):
        actor_id = rng.choice(animal_ids)
        target_id = rng.choice(plant_ids)
        it = INTERACTION_TYPES[rng.randrange(len(INTERACTION_TYPES))]
        loc = localities[rng.randrange(len(localities))]
        src_idx = rng.randrange(len(sources))
        src = sources[src_idx]
        sv_id = source_versions[src_idx]["source_version_id"]
        p_start, p_end, season_label = seasons[rng.randrange(len(seasons))]
        method = methods_pool[rng.randrange(len(methods_pool))]
        status = statuses[rng.randrange(len(statuses))]

        ev_id = f"SYN_EVID_{idx:06d}"
        ast_id = f"SYN_AST_{idx:06d}"
        batch_num = ((idx - 1) // batch_size) + 1
        batch_id = f"SYN_IB_{batch_num:04d}"
        raw_doc_id = f"SYN_RAW_{idx:06d}"

        evidences.append(
            {
                "evidence_id": ev_id,
                "source_id": src["source_id"],
                "source_version_id": sv_id,
                "source_locator": f"Table {(idx % 6) + 1}, row {idx}",
                "evidence_kind": "SYNTHETIC_RECORD",
                "method_code": method,
                "reported_term": it["code"],
                "summary": f"SYNTHETIC_BENCHMARK evidence {ev_id}",
                "interpretation_limit": "SYNTHETIC_BENCHMARK synthetic limit",
                "period_start": p_start,
                "period_end": p_end,
                "license_id": "CC-BY-4.0-SYNTHETIC",
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        assertions.append(
            {
                "assertion_id": ast_id,
                "actor_taxon_id": actor_id,
                "target_taxon_id": target_id,
                "interaction_type_id": it["interaction_type_id"],
                "interaction_type_code": it["code"],
                "locality_id": loc["locality_id"],
                "period_start": p_start,
                "period_end": p_end,
                "season_label": season_label,
                "method_code": method,
                "assertion_scope": "SYNTHETIC_AGGREGATE",
                "status": status,
                "created_by": "USR_BENCH_CURATOR",
                "created_at": ts,
                "reviewed_by": "USR_BENCH_REVIEWER" if status in ("PUBLISHED", "WITHDRAWN") else None,
                "reviewed_at": ts if status in ("PUBLISHED", "WITHDRAWN") else None,
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        assertion_evidences.append(
            {
                "assertion_id": ast_id,
                "evidence_id": ev_id,
                "evidence_role": "PRIMARY",
                "review_note": "SYNTHETIC_BENCHMARK",
            }
        )
        if status in ("PUBLISHED", "WITHDRAWN"):
            review_events.append(
                {
                    "review_event_id": f"SYN_REV_{idx:06d}",
                    "assertion_id": ast_id,
                    "user_id": "USR_BENCH_REVIEWER",
                    "previous_status": "IN_REVIEW",
                    "new_status": status,
                    "reason": "SYNTHETIC_BENCHMARK transition",
                    "created_at": ts,
                }
            )

        import_records.append(
            {
                "import_record_id": f"SYN_IR_{idx:06d}",
                "import_batch_id": batch_id,
                "external_record_id": ast_id,
                "raw_document_id": raw_doc_id,
                "validation_status": "ACCEPTED" if status != "DRAFT" else "PENDING",
                "canonical_taxon_id": actor_id,
                "validation_notes": "SYNTHETIC_BENCHMARK record",
                "dataset_tag": SYNTHETIC_TAG,
            }
        )
        raw_source_records.append(
            {
                "_id": raw_doc_id,
                "raw_document_id": raw_doc_id,
                "document_type": "raw_source_record",
                "schema_version": 1,
                "dataset_tag": SYNTHETIC_TAG,
                "provider": src["source_id"],
                "external_record_id": ast_id,
                "import_batch_id": batch_id,
                "import_record_id": f"SYN_IR_{idx:06d}",
                "validation_status": "ACCEPTED" if status != "DRAFT" else "PENDING",
                "checksum": hashlib.sha256(f"{seed}:{ast_id}".encode("utf-8")).hexdigest(),
                "payload": {
                    "actor_taxon_id": actor_id,
                    "target_taxon_id": target_id,
                    "interaction_type": it["code"],
                    "locality_id": loc["locality_id"],
                    "season_label": season_label,
                    "method_code": method,
                    "dataset_tag": SYNTHETIC_TAG,
                },
                "retrieved_at": ts,
            }
        )

    return DatasetBundle(
        dataset_id=dataset_id,
        dataset_tag=SYNTHETIC_TAG,
        seed=seed,
        taxa=taxa,
        taxon_names=taxon_names,
        taxon_identifiers=taxon_identifiers,
        localities=localities,
        sources=sources,
        source_versions=source_versions,
        interaction_types=INTERACTION_TYPES,
        evidences=evidences,
        assertions=assertions,
        assertion_evidences=assertion_evidences,
        import_batches=import_batches,
        import_records=import_records,
        review_events=review_events,
        taxon_dossiers=taxon_dossiers,
        study_dossiers=study_dossiers,
        raw_source_records=raw_source_records,
    )


def export_synthetic_dataset(
    output_root: Path,
    manifest_dir: Path,
    target_assertions: int = 1000,
    seed: int = 20261120,
) -> tuple[DatasetBundle, Path]:
    """Escribe archivos JSONL deterministas y el manifiesto con SHA256."""
    bundle = build_synthetic_bundle(target_assertions=target_assertions, seed=seed)
    dataset_dir = output_root / bundle.dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    collections: dict[str, list[dict[str, Any]]] = {
        "taxa": bundle.taxa,
        "taxon_names": bundle.taxon_names,
        "taxon_identifiers": bundle.taxon_identifiers,
        "localities": bundle.localities,
        "sources": bundle.sources,
        "source_versions": bundle.source_versions,
        "interaction_types": bundle.interaction_types,
        "evidences": bundle.evidences,
        "assertions": bundle.assertions,
        "assertion_evidences": bundle.assertion_evidences,
        "import_batches": bundle.import_batches,
        "import_records": bundle.import_records,
        "review_events": bundle.review_events,
        "taxon_dossiers": bundle.taxon_dossiers,
        "study_dossiers": bundle.study_dossiers,
        "raw_source_records": bundle.raw_source_records,
    }

    files_meta: dict[str, dict[str, Any]] = {}
    for name, rows in collections.items():
        file_path = dataset_dir / f"{name}.jsonl"
        with file_path.open("w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        files_meta[f"{name}.jsonl"] = {
            "count": len(rows),
            "size_bytes": file_path.stat().st_size,
            "sha256": _sha256_file(file_path),
        }

    manifest = {
        "dataset_id": bundle.dataset_id,
        "dataset_tag": SYNTHETIC_TAG,
        "generator_version": GENERATOR_VERSION,
        "seed": seed,
        "target_assertions": target_assertions,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameters": {
            "seed": seed,
            "target_assertions": target_assertions,
            "non_overlapping_scientific_names": True,
        },
        "entity_counts": bundle.entity_counts(),
        "files": files_meta,
    }
    manifest_path = manifest_dir / f"{bundle.dataset_id}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return bundle, manifest_path


def load_synthetic_dataset(dataset_dir: Path, manifest_path: Path) -> DatasetBundle:
    """Carga y verifica checksums de un dataset sintético generado previamente."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files_meta: dict[str, dict[str, Any]] = manifest["files"]

    loaded: dict[str, list[dict[str, Any]]] = {}
    for filename, meta in files_meta.items():
        path = dataset_dir / filename
        actual_sha = _sha256_file(path)
        if actual_sha != meta["sha256"]:
            raise ValueError(f"Checksum inválido en {path}: esperado {meta['sha256']}, actual {actual_sha}")
        key = filename.removesuffix(".jsonl")
        with path.open("r", encoding="utf-8") as fh:
            loaded[key] = [json.loads(line) for line in fh if line.strip()]

    return DatasetBundle(
        dataset_id=manifest["dataset_id"],
        dataset_tag=manifest["dataset_tag"],
        seed=manifest["seed"],
        **loaded,
    )
