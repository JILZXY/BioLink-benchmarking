from __future__ import annotations

import hashlib
from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.workloads.base import WorkloadCase, WorkloadDefinition


def _build_r1_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    # Mezcla nombres aceptados y sinónimos presentes en taxon_names
    pool = [tn["name"] for tn in bundle.taxon_names]
    names_by_query: dict[str, set[str]] = {}
    for tn in bundle.taxon_names:
        names_by_query.setdefault(tn["name"], set()).add(tn["taxon_id"])

    cases: list[WorkloadCase] = []
    for i in range(count):
        q = pool[(i * 7) % len(pool)]
        expected_ids = names_by_query[q]

        def _validate(res: Any, exp: set[str] = expected_ids) -> tuple[bool, str]:
            if not isinstance(res, list):
                return False, "Se esperaba lista de resultados"
            got_ids = {r["taxon_id"] for r in res}
            if got_ids != exp:
                return False, f"taxon_ids esperados={sorted(exp)}, obtenidos={sorted(got_ids)}"
            return True, "ok"

        cases.append(WorkloadCase(op_name="R1_taxon_search", params={"query_name": q}, validator=_validate))
    return cases


def _build_r2_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    loc_ids = [loc["locality_id"] for loc in bundle.localities]
    periods = sorted({a["period_start"] for a in bundle.assertions})
    limit = 50
    cases: list[WorkloadCase] = []
    for i in range(count):
        loc_id = loc_ids[i % len(loc_ids)]
        p_start = periods[i % len(periods)]
        expected = sorted(
            [
                a["assertion_id"]
                for a in bundle.assertions
                if a["locality_id"] == loc_id and a["period_start"] >= p_start and a["status"] == "PUBLISHED"
            ]
        )[:limit]

        def _validate(res: Any, exp: list[str] = expected) -> tuple[bool, str]:
            if not isinstance(res, list):
                return False, "Se esperaba lista de afirmaciones"
            got = [r["assertion_id"] for r in res]
            if got != exp:
                return False, f"Se esperaban {len(exp)} IDs y se obtuvieron {len(got)}"
            if any(r["status"] != "PUBLISHED" for r in res):
                return False, "Se filtraron afirmaciones no PUBLISHED"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="R2_filtered_assertions",
                params={"locality_id": loc_id, "period_start": p_start, "status": "PUBLISHED", "limit": limit},
                validator=_validate,
            )
        )
    return cases


def _build_r3_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    animals = [t["taxon_id"] for t in bundle.taxa if t["organism_group"] == "ANIMAL"]
    plants = [t["taxon_id"] for t in bundle.taxa if t["organism_group"] == "PLANT"]
    loc = bundle.localities[0]["locality_id"]
    src = bundle.sources[0]["source_id"]
    sv = bundle.source_versions[0]["source_version_id"]
    it = bundle.interaction_types[0]

    cases: list[WorkloadCase] = []
    for i in range(count):
        ast_id = f"WL_{run_prefix}_R3_AST_{i:05d}"
        ev_id = f"WL_{run_prefix}_R3_EVID_{i:05d}"
        rev_id = f"WL_{run_prefix}_R3_REV_{i:05d}"
        out_id = f"WL_{run_prefix}_R3_OUT_{i:05d}"
        params = {
            "assertion_id": ast_id,
            "evidence_id": ev_id,
            "review_event_id": rev_id,
            "outbox_event_id": out_id,
            "actor_taxon_id": animals[i % len(animals)],
            "target_taxon_id": plants[i % len(plants)],
            "interaction_type_id": it["interaction_type_id"],
            "interaction_type_code": it["code"],
            "locality_id": loc,
            "source_id": src,
            "source_version_id": sv,
            "source_locator": f"Workload R3 op {i}",
            "method_code": "DATASET_RECORD",
            "period_start": "2026-01",
            "period_end": "2026-03",
            "season_label": "Dry season 2026",
            "timestamp": "2026-11-20T12:00:00Z",
            "dataset_tag": bundle.dataset_tag,
        }

        def _validate(res: Any, expected_id: str = ast_id) -> tuple[bool, str]:
            if not isinstance(res, dict) or not res.get("committed"):
                return False, "Transacción R3 no confirmada"
            if res.get("assertion_id") != expected_id:
                return False, f"assertion_id inesperado: {res.get('assertion_id')}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="R3_transactional_assertion_outbox",
                params=params,
                validator=_validate,
            )
        )
    return cases


def _build_r4_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    src = bundle.sources[0]["source_id"]
    sv = bundle.source_versions[0]["source_version_id"]
    taxa_ids = [t["taxon_id"] for t in bundle.taxa]
    batch_size = 50
    cases: list[WorkloadCase] = []
    for i in range(count):
        batch_id = f"WL_{run_prefix}_R4_IB_{i:05d}"
        records = [
            {
                "import_record_id": f"WL_{run_prefix}_R4_IR_{i:05d}_{j:03d}",
                "external_record_id": f"EXT_R4_{i:05d}_{j:03d}",
                "raw_document_id": f"RAW_R4_{i:05d}_{j:03d}",
                "canonical_taxon_id": taxa_ids[(i + j) % len(taxa_ids)],
            }
            for j in range(batch_size)
        ]

        def _validate(res: Any, exp_len: int = batch_size, exp_bid: str = batch_id) -> tuple[bool, str]:
            if not isinstance(res, dict):
                return False, "Se esperaba diccionario de resultado R4"
            if res.get("import_batch_id") != exp_bid or res.get("inserted_records") != exp_len:
                return False, f"Conteo o batch_id incorrecto: {res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="R4_batch_import_insert",
                params={
                    "import_batch_id": batch_id,
                    "source_id": src,
                    "source_version_id": sv,
                    "timestamp": "2026-11-20T12:00:00Z",
                    "dataset_tag": bundle.dataset_tag,
                    "records": records,
                    "checksum": hashlib.sha256(batch_id.encode("utf-8")).hexdigest(),
                },
                validator=_validate,
            )
        )
    return cases


RELATIONAL_WORKLOADS: list[WorkloadDefinition] = [
    WorkloadDefinition(
        op_name="R1_taxon_search",
        model="relational",
        biolink_ops=("OP-01",),
        description="Búsqueda taxonómica por nombre aceptado o sinónimo",
        is_write=False,
        build_cases=_build_r1_cases,
    ),
    WorkloadDefinition(
        op_name="R2_filtered_assertions",
        model="relational",
        biolink_ops=("OP-03", "OP-05"),
        description="Consulta filtrada de afirmaciones por localidad, periodo y estado PUBLISHED",
        is_write=False,
        build_cases=_build_r2_cases,
    ),
    WorkloadDefinition(
        op_name="R3_transactional_assertion_outbox",
        model="relational",
        biolink_ops=("OP-11", "OP-12"),
        description="Inserción transaccional de afirmación con evidencia, auditoría y evento outbox",
        is_write=True,
        build_cases=_build_r3_cases,
    ),
    WorkloadDefinition(
        op_name="R4_batch_import_insert",
        model="relational",
        biolink_ops=("OP-09", "OP-10"),
        description="Inserción por lotes de lote y registros de importación",
        is_write=True,
        build_cases=_build_r4_cases,
    ),
]
