from __future__ import annotations

import json
from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle

BENCH_USERS = [
    ("USR_BENCH_CURATOR", "Curador Benchmark", "curator@benchmark.local", True, "2026-11-20T00:00:00Z"),
    ("USR_BENCH_REVIEWER", "Revisor Benchmark", "reviewer@benchmark.local", True, "2026-11-20T00:00:00Z"),
    ("USR_BENCH_INGESTION", "Servicio Ingestión", "ingestion@benchmark.local", True, "2026-11-20T00:00:00Z"),
]


def chunked(rows: list[Any], size: int = 500) -> list[list[Any]]:
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def prepare_relational_rows(bundle: DatasetBundle) -> dict[str, list[tuple[Any, ...]]]:
    """Convierte el bundle lógico en tuplas ordenadas por tabla respetando FKs."""
    return {
        "source": [
            (
                s["source_id"],
                s["source_type"],
                s["title"],
                s["authors"],
                s["publication_year"],
                s.get("doi"),
                s.get("uri"),
                s.get("publisher"),
                s.get("citation_text"),
                s["license_id"],
                s["dataset_tag"],
            )
            for s in bundle.sources
        ],
        "source_version": [
            (
                sv["source_version_id"],
                sv["source_id"],
                sv["provider_version"],
                sv["release_date"],
                sv["endpoint_or_file"],
                sv["query_parameters"],
                sv["filters"],
                sv["license_id"],
                sv["checksum"],
                sv["dataset_tag"],
            )
            for sv in bundle.source_versions
        ],
        "locality": [
            (
                loc["locality_id"],
                loc["name"],
                loc["locality_type"],
                loc.get("parent_locality_id"),
                loc["protected_status"],
                loc["spatial_validation_status"],
                loc.get("coordinate_precision"),
                loc["source_id"],
                loc["dataset_tag"],
            )
            for loc in bundle.localities
        ],
        "taxon": [
            (
                t["taxon_id"],
                t["accepted_name"],
                t.get("scientific_authorship", ""),
                t["taxonomic_rank"],
                t["organism_group"],
                t["taxonomic_status"],
                t["created_at"],
                t["updated_at"],
                t["dataset_tag"],
            )
            for t in bundle.taxa
        ],
        "taxon_name": [
            (
                tn["taxon_name_id"],
                tn["taxon_id"],
                tn["name"],
                tn["name_usage"],
                tn.get("language", "la"),
                tn["source_id"],
                bool(tn["is_preferred"]),
                tn["verbatim_name"],
                tn["dataset_tag"],
            )
            for tn in bundle.taxon_names
        ],
        "taxon_identifier": [
            (
                ti["taxon_identifier_id"],
                ti["taxon_id"],
                ti["scheme"],
                ti["external_id"],
                ti["retrieved_at"],
                ti["source_id"],
                ti["dataset_tag"],
            )
            for ti in bundle.taxon_identifiers
        ],
        "interaction_type": [
            (
                it["interaction_type_id"],
                it["code"],
                it["label"],
                it["definition"],
                it["actor_role"],
                it["target_role"],
                bool(it["is_active"]),
            )
            for it in bundle.interaction_types
        ],
        "evidence": [
            (
                ev["evidence_id"],
                ev["source_id"],
                ev["source_version_id"],
                ev["source_locator"],
                ev["evidence_kind"],
                ev["method_code"],
                ev["reported_term"],
                ev["summary"],
                ev.get("interpretation_limit", ""),
                ev["period_start"],
                ev["period_end"],
                ev["license_id"],
                ev["dataset_tag"],
            )
            for ev in bundle.evidences
        ],
        "interaction_assertion": [
            (
                a["assertion_id"],
                a["actor_taxon_id"],
                a["target_taxon_id"],
                a["interaction_type_id"],
                a["locality_id"],
                a["period_start"],
                a["period_end"],
                a["season_label"],
                a["method_code"],
                a["assertion_scope"],
                a["status"],
                a["created_by"],
                a["created_at"],
                a.get("reviewed_by"),
                a.get("reviewed_at"),
                a["dataset_tag"],
            )
            for a in bundle.assertions
        ],
        "assertion_evidence": [
            (
                ae["assertion_id"],
                ae["evidence_id"],
                ae["evidence_role"],
                ae["review_note"],
            )
            for ae in bundle.assertion_evidences
        ],
        "import_batch": [
            (
                ib["import_batch_id"],
                ib["source_id"],
                ib["source_version_id"],
                ib["started_by"],
                ib["started_at"],
                ib["finished_at"],
                ib["query_parameters"],
                ib["filters"],
                ib["status"],
                ib["received_count"],
                ib["accepted_count"],
                ib["rejected_count"],
                ib["dataset_tag"],
            )
            for ib in bundle.import_batches
        ],
        "import_record": [
            (
                ir["import_record_id"],
                ir["import_batch_id"],
                ir["external_record_id"],
                ir["raw_document_id"],
                ir["validation_status"],
                ir.get("canonical_taxon_id"),
                ir.get("validation_notes", ""),
                ir["dataset_tag"],
            )
            for ir in bundle.import_records
        ],
        "review_event": [
            (
                re["review_event_id"],
                re["assertion_id"],
                re["user_id"],
                re["previous_status"],
                re["new_status"],
                re["reason"],
                re["created_at"],
            )
            for re in bundle.review_events
        ],
    }


def serialize_outbox_payload(params: dict[str, Any]) -> str:
    return json.dumps(
        {
            "assertion_id": params["assertion_id"],
            "actor_taxon_id": params["actor_taxon_id"],
            "target_taxon_id": params["target_taxon_id"],
            "interaction_type_id": params["interaction_type_id"],
            "locality_id": params["locality_id"],
            "status": "PUBLISHED",
        },
        sort_keys=True,
    )
