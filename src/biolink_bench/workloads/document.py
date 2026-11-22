from __future__ import annotations

import hashlib
from typing import Any

from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.workloads.base import WorkloadCase, WorkloadDefinition


def _build_d1_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    dossiers = bundle.taxon_dossiers
    cases: list[WorkloadCase] = []
    for i in range(count):
        doc = dossiers[(i * 5) % len(dossiers)]
        tid = doc["taxon_id"]
        min_claims = len(doc.get("claims", []))

        def _validate(res: Any, exp_tid: str = tid, exp_claims: int = min_claims) -> tuple[bool, str]:
            if not isinstance(res, dict):
                return False, "No se encontró el taxon_dossier esperado"
            if res.get("taxon_id") != exp_tid or res.get("claims_count", 0) < exp_claims:
                return False, f"Documento inconsistente para {exp_tid}: {res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="D1_read_taxon_dossier",
                params={"taxon_id": tid},
                validator=_validate,
            )
        )
    return cases


def _build_d2_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    # Extrae pares reales (claim_field, claim_value) sobre ecology.diet
    diet_values = sorted(
        {
            c["value"]
            for doc in bundle.taxon_dossiers
            for c in doc.get("claims", [])
            if c.get("field") == "ecology.diet"
        }
    )
    if not diet_values:
        diet_values = [bundle.taxon_dossiers[0]["claims"][0]["value"]]
    field_name = "ecology.diet" if any(
        c.get("field") == "ecology.diet" for d in bundle.taxon_dossiers for c in d.get("claims", [])
    ) else bundle.taxon_dossiers[0]["claims"][0]["field"]

    limit = 50
    cases: list[WorkloadCase] = []
    for i in range(count):
        val = diet_values[i % len(diet_values)]
        expected = sorted(
            [
                doc["taxon_id"]
                for doc in bundle.taxon_dossiers
                if doc["dataset_tag"] == bundle.dataset_tag
                and any(c.get("field") == field_name and c.get("value") == val for c in doc.get("claims", []))
            ]
        )[:limit]

        def _validate(res: Any, exp: list[str] = expected) -> tuple[bool, str]:
            if not isinstance(res, list):
                return False, "Se esperaba lista de documentos coincidentes"
            got = [d["taxon_id"] for d in res]
            if got != exp:
                return False, f"Se esperaban {len(exp)} taxones y se obtuvieron {len(got)}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="D2_nested_attribute_query",
                params={
                    "dataset_tag": bundle.dataset_tag,
                    "claim_field": field_name,
                    "claim_value": val,
                    "limit": limit,
                },
                validator=_validate,
            )
        )
    return cases


def _build_d3_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    dossiers = bundle.taxon_dossiers
    src = bundle.sources[0]["source_id"]
    cases: list[WorkloadCase] = []
    for i in range(count):
        doc = dossiers[i % len(dossiers)]
        tid = doc["taxon_id"]
        params = {
            "taxon_id": tid,
            "update_seq": f"{run_prefix}_{i:05d}",
            "claim_id": f"WL_{run_prefix}_CLM_{i:05d}",
            "note_value": f"Versioned update note {i}",
            "source_id": src,
            "source_locator": f"Workload D3 #{i}",
            "timestamp": "2026-11-20T12:00:00Z",
        }

        def _validate(res: Any, exp_tid: str = tid) -> tuple[bool, str]:
            if not isinstance(res, dict):
                return False, "Respuesta D3 inválida"
            if res.get("taxon_id") != exp_tid or res.get("new_version") != res.get("previous_version", 0) + 1:
                return False, f"Versión no incrementada correctamente: {res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="D3_versioned_dossier_update",
                params=params,
                validator=_validate,
            )
        )
    return cases


def _build_d4_cases(bundle: DatasetBundle, count: int, run_prefix: str) -> list[WorkloadCase]:
    src = bundle.sources[0]["source_id"]
    batch_size = 50
    cases: list[WorkloadCase] = []
    for i in range(count):
        docs = [
            {
                "_id": f"WL_{run_prefix}_D4_RAW_{i:05d}_{j:03d}",
                "raw_document_id": f"WL_{run_prefix}_D4_RAW_{i:05d}_{j:03d}",
                "document_type": "raw_source_record",
                "schema_version": 1,
                "dataset_tag": bundle.dataset_tag,
                "provider": src,
                "external_record_id": f"EXT_D4_{i:05d}_{j:03d}",
                "import_batch_id": f"WL_{run_prefix}_D4_IB_{i:05d}",
                "import_record_id": f"WL_{run_prefix}_D4_IR_{i:05d}_{j:03d}",
                "validation_status": "PENDING",
                "checksum": hashlib.sha256(f"{run_prefix}:{i}:{j}".encode("utf-8")).hexdigest(),
                "payload": {"raw_index": j, "dataset_tag": bundle.dataset_tag},
                "retrieved_at": "2026-11-20T12:00:00Z",
            }
            for j in range(batch_size)
        ]

        def _validate(res: Any, exp_count: int = batch_size) -> tuple[bool, str]:
            if not isinstance(res, dict) or res.get("inserted_count") != exp_count:
                return False, f"Se esperaba insertar {exp_count}, obtenido {res}"
            return True, "ok"

        cases.append(
            WorkloadCase(
                op_name="D4_bulk_raw_source_insert",
                params={"docs": docs},
                validator=_validate,
            )
        )
    return cases


DOCUMENT_WORKLOADS: list[WorkloadDefinition] = [
    WorkloadDefinition(
        op_name="D1_read_taxon_dossier",
        model="document",
        biolink_ops=("OP-02",),
        description="Lectura de taxon_dossier por taxon_id",
        is_write=False,
        build_cases=_build_d1_cases,
    ),
    WorkloadDefinition(
        op_name="D2_nested_attribute_query",
        model="document",
        biolink_ops=("OP-02", "OP-13"),
        description="Consulta por atributos anidados en claims",
        is_write=False,
        build_cases=_build_d2_cases,
    ),
    WorkloadDefinition(
        op_name="D3_versioned_dossier_update",
        model="document",
        biolink_ops=("OP-13",),
        description="Escritura de nueva versión de ficha conservando versión previa",
        is_write=True,
        build_cases=_build_d3_cases,
    ),
    WorkloadDefinition(
        op_name="D4_bulk_raw_source_insert",
        model="document",
        biolink_ops=("OP-09", "OP-10"),
        description="Inserción masiva de registros originales raw_source_record",
        is_write=True,
        build_cases=_build_d4_cases,
    ),
]
