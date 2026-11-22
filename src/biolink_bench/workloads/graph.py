from __future__ import annotations

from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.workloads.base import WorkloadCase, WorkloadDefinition


def _build_g1_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    published = bundle.published_assertions
    participating = sorted({a["actor_taxon_id"] for a in published} | {a["target_taxon_id"] for a in published})
    expected_by_taxon: dict[str, set[tuple[str, str]]] = {t: set() for t in participating}
    for a in published:
        expected_by_taxon[a["actor_taxon_id"]].add((a["assertion_id"], a["target_taxon_id"]))
        expected_by_taxon[a["target_taxon_id"]].add((a["assertion_id"], a["actor_taxon_id"]))

    cases: list[WorkloadCase] = []
    for i in range(count):
        tid = participating[i % len(participating)]
        exp = expected_by_taxon[tid]

        def _validate(res: Any, expected: set[tuple[str, str]] = exp) -> tuple[bool, str]:
            if not isinstance(res, list):
                return False, "Se esperaba lista de vecinos"
            got = {(r["assertion_id"], r["partner_taxon_id"]) for r in res}
            if got != expected:
                return False, f"Vecinos esperados={len(expected)}, obtenidos={len(got)}"
            return True, "ok"

        cases.append(WorkloadCase(op_name="G1_taxon_neighbors", params={"taxon_id": tid}, validator=_validate))
    return cases


def _build_g2_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    published = bundle.published_assertions
    combos = sorted({(a["locality_id"], a["interaction_type_code"], a["period_start"]) for a in published})
    limit = 100
    cases: list[WorkloadCase] = []
    for i in range(count):
        loc_id, it_code, p_start = combos[i % len(combos)]
        expected = sorted(
            [
                a["assertion_id"]
                for a in published
                if a["locality_id"] == loc_id
                and a["interaction_type_code"] == it_code
                and a["period_start"] >= p_start
            ]
        )[:limit]

        def _validate(res: Any, exp: list[str] = expected, expected_loc: str = loc_id) -> tuple[bool, str]:
            if not isinstance(res, list):
                return False, "Se esperaba subgrafo de afirmaciones"
            got = [r["assertion_id"] for r in res]
            if got != exp:
                return False, f"Subgrafo esperado={len(exp)} afirmaciones, obtenido={len(got)}"
            if any(r["locality_id"] != expected_loc for r in res):
                return False, "Se mezclaron localidades en subgrafo"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="G2_filtered_subgraph",
                params={
                    "locality_id": loc_id,
                    "interaction_type_code": it_code,
                    "period_start": p_start,
                    "limit": limit,
                },
                validator=_validate,
            )
        )
    return cases


def _build_g3_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    published = bundle.published_assertions
    participating = sorted({a["actor_taxon_id"] for a in published} | {a["target_taxon_id"] for a in published})
    partners_by_taxon: dict[str, set[str]] = {t: set() for t in participating}
    assertions_by_taxon: dict[str, set[str]] = {t: set() for t in participating}
    for a in published:
        partners_by_taxon[a["actor_taxon_id"]].add(a["target_taxon_id"])
        partners_by_taxon[a["target_taxon_id"]].add(a["actor_taxon_id"])
        assertions_by_taxon[a["actor_taxon_id"]].add(a["assertion_id"])
        assertions_by_taxon[a["target_taxon_id"]].add(a["assertion_id"])

    cases: list[WorkloadCase] = []
    for i in range(count):
        tid = participating[i % len(participating)]
        exp_partners = len(partners_by_taxon[tid])
        exp_assertions = len(assertions_by_taxon[tid])

        def _validate(res: Any, ep: int = exp_partners, ea: int = exp_assertions) -> tuple[bool, str]:
            if not isinstance(res, dict):
                return False, "Se esperaba diccionario de conteo G3"
            if res.get("distinct_partner_count") != ep or res.get("assertion_count") != ea:
                return False, f"Esperado partners={ep}, assertions={ea}; obtenido={res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="G3_distinct_partner_count",
                params={"taxon_id": tid, "locality_id": None},
                validator=_validate,
            )
        )
    return cases


def _build_g4_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    animals = [t["taxon_id"] for t in bundle.taxa if t["organism_group"] == "ANIMAL"]
    plants = [t["taxon_id"] for t in bundle.taxa if t["organism_group"] == "PLANT"]
    loc = bundle.localities[0]["locality_id"]
    src = bundle.sources[0]
    it_code = bundle.interaction_types[0]["code"]

    cases: list[WorkloadCase] = []
    for i in range(count):
        # La mitad repite assertion_id previo para validar idempotencia real de MERGE
        unique_idx = i // 2
        ast_id = f"WL_{run_prefix}_G4_AST_{unique_idx:05d}"
        params = {
            "assertion_id": ast_id,
            "actor_taxon_id": animals[unique_idx % len(animals)],
            "target_taxon_id": plants[unique_idx % len(plants)],
            "locality_id": loc,
            "source_id": src["source_id"],
            "source_title": src["title"],
            "evidence_id": f"WL_{run_prefix}_G4_EVID_{unique_idx:05d}",
            "source_locator": f"Projection G4 #{unique_idx}",
            "interaction_type_code": it_code,
            "period_start": "2026-01",
            "period_end": "2026-03",
            "season_label": "Dry season 2026",
            "method_code": "DATASET_RECORD",
            "dataset_tag": bundle.dataset_tag,
        }

        def _validate(res: Any, exp_id: str = ast_id) -> tuple[bool, str]:
            if not isinstance(res, dict):
                return False, "Respuesta G4 inválida"
            if res.get("assertion_id") != exp_id or res.get("status") != "PUBLISHED":
                return False, f"Upsert G4 inesperado: {res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="G4_idempotent_assertion_upsert",
                params=params,
                validator=_validate,
            )
        )
    return cases


GRAPH_WORKLOADS: list[WorkloadDefinition] = [
    WorkloadDefinition(
        op_name="G1_taxon_neighbors",
        model="graph",
        biolink_ops=("OP-03",),
        description="Consulta de vecinos de un taxón sobre afirmaciones PUBLISHED",
        is_write=False,
        build_cases=_build_g1_cases,
    ),
    WorkloadDefinition(
        op_name="G2_filtered_subgraph",
        model="graph",
        biolink_ops=("OP-05",),
        description="Subgrafo filtrado por localidad, tipo de interacción y periodo",
        is_write=False,
        build_cases=_build_g2_cases,
    ),
    WorkloadDefinition(
        op_name="G3_distinct_partner_count",
        model="graph",
        biolink_ops=("OP-07",),
        description="Conteo de taxones contraparte distintos",
        is_write=False,
        build_cases=_build_g3_cases,
    ),
    WorkloadDefinition(
        op_name="G4_idempotent_assertion_upsert",
        model="graph",
        biolink_ops=("OP-12",),
        description="Upsert idempotente de una afirmación publicada",
        is_write=True,
        build_cases=_build_g4_cases,
    ),
]
