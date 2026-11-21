from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle

FIXTURE_TAG = "SCIENTIFIC_FIXTURE"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_scientific_fixture(
    fixture_dir: Path, verify_manifest: bool = True
) -> tuple[DatasetBundle, dict[str, Any]]:
    """Carga el fixture científico de Etapa 1 y valida sus invariantes de dominio."""
    fixture_path = fixture_dir / "biolink_scientific_fixture.json"
    manifest_path = fixture_dir / "manifest.json"
    if not fixture_path.exists():
        raise FileNotFoundError(f"No existe el fixture científico en {fixture_path}")

    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if verify_manifest:
            expected_sha = manifest.get("sha256")
            actual_sha = compute_sha256(fixture_path)
            if expected_sha and expected_sha != actual_sha:
                raise ValueError(
                    f"Checksum inválido en {fixture_path}: esperado {expected_sha}, actual {actual_sha}"
                )

    taxa_by_id = {t["taxon_id"]: t for t in raw["taxa"]}
    locs_by_id = {loc["locality_id"]: loc for loc in raw["localities"]}
    it_by_code = {it["code"]: it for it in raw["interaction_types"]}
    sources_by_id = {s["source_id"]: s for s in raw["sources"]}

    if "LOC_RBMA_SOUTH" not in locs_by_id or "LOC_PDLG" not in locs_by_id:
        raise ValueError("El fixture debe mantener LOC_RBMA_SOUTH y LOC_PDLG separados")
    if locs_by_id["LOC_RBMA_SOUTH"]["spatial_validation_status"] != "INSIDE_ANP":
        raise ValueError("LOC_RBMA_SOUTH debe ser INSIDE_ANP")
    if locs_by_id["LOC_PDLG"]["spatial_validation_status"] != "OUTSIDE_ANP":
        raise ValueError("LOC_PDLG debe ser OUTSIDE_ANP")

    taxa: list[dict[str, Any]] = []
    taxon_names: list[dict[str, Any]] = []
    taxon_identifiers: list[dict[str, Any]] = []
    taxon_dossiers: list[dict[str, Any]] = []

    for t in raw["taxa"]:
        row = {
            "taxon_id": t["taxon_id"],
            "accepted_name": t["accepted_name"],
            "scientific_authorship": t.get("scientific_authorship", ""),
            "taxonomic_rank": t["taxonomic_rank"],
            "organism_group": t["organism_group"],
            "taxonomic_status": t["taxonomic_status"],
            "created_at": "2026-11-20T00:00:00Z",
            "updated_at": "2026-11-20T00:00:00Z",
            "dataset_tag": FIXTURE_TAG,
        }
        taxa.append(row)
        taxon_names.append(
            {
                "taxon_name_id": f"TN_{t['taxon_id']}",
                "taxon_id": t["taxon_id"],
                "name": t["accepted_name"],
                "name_usage": "ACCEPTED" if t["taxonomic_status"] == "ACCEPTED" else "VERBATIM_SOURCE",
                "language": "la",
                "source_id": t["source_id"],
                "is_preferred": True,
                "verbatim_name": t["accepted_name"],
                "dataset_tag": FIXTURE_TAG,
            }
        )
        taxon_identifiers.append(
            {
                "taxon_identifier_id": f"TID_{t['taxon_id']}",
                "taxon_id": t["taxon_id"],
                "scheme": "BIOLINK_FIXTURE",
                "external_id": t["taxon_id"],
                "retrieved_at": "2026-11-20T00:00:00Z",
                "source_id": t["source_id"],
                "dataset_tag": FIXTURE_TAG,
            }
        )
        taxon_dossiers.append(
            {
                "_id": t["taxon_id"],
                "taxon_id": t["taxon_id"],
                "document_type": "taxon_dossier",
                "schema_version": 1,
                "dataset_tag": FIXTURE_TAG,
                "accepted_name": t["accepted_name"],
                "taxonomic_rank": t["taxonomic_rank"],
                "organism_group": t["organism_group"],
                "summary": {
                    "description": {
                        "value": f"Taxón documentado en fuente {t['source_id']}",
                        "source_refs": [t["source_id"]],
                        "locators": ["Stage 1 documented taxon"],
                    }
                },
                "sections": {
                    "morphology": [],
                    "ecology": {
                        "habitats": ["Selva alta perennifolia"] if t["source_id"] == "MAMMAL2016" else ["Selva Lacandona"],
                        "diet": ["Frugivoría documentada"] if t["organism_group"] == "ANIMAL" else [],
                        "activity_patterns": [],
                        "notes": [],
                    },
                    "conservation": [],
                    "distribution": [{"locality_ref": "LOC_RBMA_SOUTH"}],
                },
                "claims": [
                    {
                        "claim_id": f"CLM_{t['taxon_id']}_1",
                        "field": "taxonomy.verbatim",
                        "value": t["accepted_name"],
                        "source_id": t["source_id"],
                        "source_locator": "Etapa 1 — sección 4",
                    }
                ],
                "media": [],
                "document_version": 1,
                "updated_at": "2026-11-20T00:00:00Z",
            }
        )

    sources = [{**s, "publisher": "Academic Journal", "dataset_tag": FIXTURE_TAG} for s in raw["sources"]]
    source_versions = [
        {
            "source_version_id": f"SV_{s['source_id']}_V1",
            "source_id": s["source_id"],
            "provider_version": "stage1-2026-11-20",
            "release_date": "2026-11-20",
            "endpoint_or_file": "docs/01_matriz_evidencias_biolink.csv",
            "query_parameters": "{}",
            "filters": "{}",
            "license_id": s["license_id"],
            "checksum": compute_sha256(fixture_path),
            "dataset_tag": FIXTURE_TAG,
        }
        for s in raw["sources"]
    ]

    localities = [{**loc, "geometry_reference": None, "dataset_tag": FIXTURE_TAG} for loc in raw["localities"]]

    evidences: list[dict[str, Any]] = []
    assertions: list[dict[str, Any]] = []
    assertion_evidences: list[dict[str, Any]] = []
    review_events: list[dict[str, Any]] = []
    raw_source_records: list[dict[str, Any]] = []

    import_batches = [
        {
            "import_batch_id": "IB_SCI_001",
            "source_id": "BAT2007",
            "source_version_id": "SV_BAT2007_V1",
            "started_by": "USR_BENCH_CURATOR",
            "started_at": "2026-11-20T00:00:00Z",
            "finished_at": "2026-11-20T00:01:00Z",
            "query_parameters": '{"source": "01_matriz_evidencias_biolink.csv"}',
            "filters": '{"dataset_tag": "SCIENTIFIC_FIXTURE"}',
            "status": "COMPLETED",
            "received_count": len(raw["assertions"]),
            "accepted_count": len(raw["assertions"]),
            "rejected_count": 0,
            "dataset_tag": FIXTURE_TAG,
        }
    ]
    import_records: list[dict[str, Any]] = []

    for idx, item in enumerate(raw["assertions"], start=1):
        actor = taxa_by_id[item["actor_taxon_id"]]
        target = taxa_by_id[item["target_taxon_id"]]
        if actor["organism_group"] != "ANIMAL" or target["organism_group"] != "PLANT":
            raise ValueError(f"Violación RD-03 en {item['assertion_id']}")
        if item["locality_id"] not in locs_by_id:
            raise ValueError(f"Localidad desconocida en {item['assertion_id']}")
        if item["source_id"] not in sources_by_id:
            raise ValueError(f"Fuente desconocida en {item['assertion_id']}")
        it = it_by_code[item["interaction_type_code"]]

        ev_id = f"EVID_SCI_{idx:03d}"
        evidences.append(
            {
                "evidence_id": ev_id,
                "source_id": item["source_id"],
                "source_version_id": f"SV_{item['source_id']}_V1",
                "source_locator": item["source_locator"],
                "evidence_kind": "SCIENTIFIC_LITERATURE",
                "method_code": item["method_code"],
                "reported_term": item["interaction_type_code"],
                "summary": item["reported_detail"],
                "interpretation_limit": item["interpretation_limit"],
                "period_start": item["period_start"],
                "period_end": item["period_end"],
                "license_id": "ACADEMIC_CITATION_ONLY",
                "dataset_tag": FIXTURE_TAG,
            }
        )
        assertions.append(
            {
                "assertion_id": item["assertion_id"],
                "actor_taxon_id": item["actor_taxon_id"],
                "target_taxon_id": item["target_taxon_id"],
                "interaction_type_id": it["interaction_type_id"],
                "interaction_type_code": it["code"],
                "locality_id": item["locality_id"],
                "period_start": item["period_start"],
                "period_end": item["period_end"],
                "season_label": item["season_label"],
                "method_code": item["method_code"],
                "assertion_scope": "STUDY_REPORTED",
                "status": "PUBLISHED",
                "created_by": "USR_BENCH_CURATOR",
                "created_at": "2026-11-20T00:00:00Z",
                "reviewed_by": "USR_BENCH_REVIEWER",
                "reviewed_at": "2026-11-20T00:00:00Z",
                "dataset_tag": FIXTURE_TAG,
            }
        )
        assertion_evidences.append(
            {
                "assertion_id": item["assertion_id"],
                "evidence_id": ev_id,
                "evidence_role": "PRIMARY",
                "review_note": item["interpretation_limit"],
            }
        )
        review_events.append(
            {
                "review_event_id": f"REV_SCI_{idx:03d}",
                "assertion_id": item["assertion_id"],
                "user_id": "USR_BENCH_REVIEWER",
                "previous_status": "IN_REVIEW",
                "new_status": "PUBLISHED",
                "reason": "Verified from Stage 1 matrix",
                "created_at": "2026-11-20T00:00:00Z",
            }
        )
        raw_doc_id = f"RAW_SCI_{idx:03d}"
        import_records.append(
            {
                "import_record_id": f"IR_SCI_{idx:03d}",
                "import_batch_id": "IB_SCI_001",
                "external_record_id": item["assertion_id"],
                "raw_document_id": raw_doc_id,
                "validation_status": "ACCEPTED",
                "canonical_taxon_id": item["actor_taxon_id"],
                "validation_notes": "Scientific fixture record",
                "dataset_tag": FIXTURE_TAG,
            }
        )
        raw_source_records.append(
            {
                "_id": raw_doc_id,
                "raw_document_id": raw_doc_id,
                "document_type": "raw_source_record",
                "schema_version": 1,
                "dataset_tag": FIXTURE_TAG,
                "provider": item["source_id"],
                "external_record_id": item["assertion_id"],
                "import_batch_id": "IB_SCI_001",
                "import_record_id": f"IR_SCI_{idx:03d}",
                "validation_status": "ACCEPTED",
                "checksum": hashlib.sha256(item["assertion_id"].encode("utf-8")).hexdigest(),
                "payload": item,
                "retrieved_at": "2026-11-20T00:00:00Z",
            }
        )

    study_dossiers = [
        {
            "_id": s["source_id"],
            "source_id": s["source_id"],
            "document_type": "study_dossier",
            "schema_version": 1,
            "dataset_tag": FIXTURE_TAG,
            "title": s["title"],
            "authors": s["authors"],
            "publication_year": s["publication_year"],
            "methods": ["FECAL_SEED_IDENTIFICATION"] if s["source_id"] == "BAT2007" else ["CAMERA_TRAP"],
            "localities": ["LOC_RBMA_SOUTH", "LOC_PDLG"] if s["source_id"] == "BAT2007" else ["LOC_RBMA_SOUTH"],
            "limitations": "Conserva resolución taxonómica y distinción espacial estricta de Etapa 1.",
        }
        for s in raw["sources"]
    ]

    bundle = DatasetBundle(
        dataset_id=raw["dataset_id"],
        dataset_tag=FIXTURE_TAG,
        seed=None,
        taxa=taxa,
        taxon_names=taxon_names,
        taxon_identifiers=taxon_identifiers,
        localities=localities,
        sources=sources,
        source_versions=source_versions,
        interaction_types=raw["interaction_types"],
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
    return bundle, manifest
