from __future__ import annotations

from copy import deepcopy
from typing import Any

import httpx

from biolink_bench.config import EngineConfig
from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.drivers.base import BaseEngineAdapter, SmokeResult

COUCH_VALIDATE_DESIGN_DOC = {
    "_id": "_design/biolink_validation",
    "language": "javascript",
    "validate_doc_update": (
        "function(newDoc, oldDoc, userCtx) {"
        "  if (newDoc._deleted) return;"
        "  if (!newDoc.document_type || !newDoc.schema_version || !newDoc.dataset_tag) {"
        "    throw({forbidden: 'Document must declare document_type, schema_version, and dataset_tag'});"
        "  }"
        "}"
    ),
}


class CouchDBAdapter(BaseEngineAdapter):
    """Adaptador directo a la interfaz HTTP nativa de Apache CouchDB 3.5.3."""

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._client: httpx.Client | None = None
        prefix = config.database
        self._dbs = {
            "taxon_dossiers": f"{prefix}_taxon_dossiers",
            "taxon_dossier_versions": f"{prefix}_taxon_dossier_versions",
            "study_dossiers": f"{prefix}_study_dossiers",
            "raw_source_records": f"{prefix}_raw_source_records",
        }

    def _require_client(self) -> httpx.Client:
        if self._client is None:
            raise RuntimeError("Cliente HTTP de CouchDB no conectado; llame a connect() primero")
        return self._client

    def connect(self) -> None:
        base_url = f"http://{self.config.host}:{self.config.port}"
        self._client = httpx.Client(
            base_url=base_url,
            auth=(self.config.user, self.config.password),
            timeout=15.0,
        )
        resp = self._client.get("/_up")
        resp.raise_for_status()

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None

    def health_check(self) -> tuple[bool, str]:
        client = self._require_client()
        resp = client.get("/")
        resp.raise_for_status()
        data = resp.json()
        return True, f"CouchDB {data.get('version', 'unknown')}"

    def get_engine_info(self) -> dict[str, Any]:
        client = self._require_client()
        resp = client.get("/")
        resp.raise_for_status()
        data = resp.json()
        return {
            "engine": "couchdb",
            "server_version": data.get("version", "unknown"),
            "vendor": data.get("vendor", {}).get("name", "Apache"),
            "driver": f"httpx {httpx.__version__} (CouchDB native HTTP API)",
        }

    def prepare_schema(self) -> None:
        client = self._require_client()
        for db_name in self._dbs.values():
            resp = client.put(f"/{db_name}")
            if resp.status_code not in (200, 201, 202, 412):
                resp.raise_for_status()

        td_db = self._dbs["taxon_dossiers"]
        existing = client.get(f"/{td_db}/_design/biolink_validation")
        if existing.status_code == 404:
            put_resp = client.put(f"/{td_db}/_design/biolink_validation", json=COUCH_VALIDATE_DESIGN_DOC)
            put_resp.raise_for_status()

    def _bulk_insert(self, db_name: str, docs: list[dict[str, Any]]) -> None:
        client = self._require_client()
        for i in range(0, len(docs), 500):
            batch = deepcopy(docs[i : i + 500])
            resp = client.post(f"/{db_name}/_bulk_docs", json={"docs": batch})
            resp.raise_for_status()
            errors = [r for r in resp.json() if not r.get("ok")]
            if errors:
                raise RuntimeError(f"Errores en _bulk_docs de {db_name}: {errors[:3]}")

    def load_dataset(self, bundle: DatasetBundle) -> dict[str, int]:
        self.cleanup_test_data(bundle.dataset_tag)
        counts: dict[str, int] = {}
        mapping = [
            ("taxon_dossiers", bundle.taxon_dossiers),
            ("study_dossiers", bundle.study_dossiers),
            ("raw_source_records", bundle.raw_source_records),
        ]
        for key, docs in mapping:
            if docs:
                self._bulk_insert(self._dbs[key], docs)
            counts[key] = len(docs)
        return counts

    def create_indexes(self) -> None:
        client = self._require_client()
        indexes = [
            (self._dbs["taxon_dossiers"], "idx_taxon_id", ["taxon_id"]),
            (self._dbs["taxon_dossiers"], "idx_tag_group", ["dataset_tag", "organism_group"]),
            (self._dbs["taxon_dossier_versions"], "idx_version_history", ["taxon_id", "document_version"]),
            (self._dbs["raw_source_records"], "idx_raw_batch", ["dataset_tag", "import_batch_id"]),
        ]
        for db_name, idx_name, fields in indexes:
            resp = client.post(
                f"/{db_name}/_index",
                json={"index": {"fields": fields}, "name": idx_name, "type": "json"},
            )
            resp.raise_for_status()

    def execute_operation(self, op_name: str, params: dict[str, Any]) -> Any:
        client = self._require_client()
        if op_name == "D1_read_taxon_dossier":
            resp = client.get(f"/{self._dbs['taxon_dossiers']}/{params['taxon_id']}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            doc = resp.json()
            return {
                "taxon_id": doc["taxon_id"],
                "accepted_name": doc.get("accepted_name"),
                "document_version": doc["document_version"],
                "claims_count": len(doc.get("claims", [])),
            }

        if op_name == "D2_nested_attribute_query":
            resp = client.post(
                f"/{self._dbs['taxon_dossiers']}/_find",
                json={
                    "selector": {
                        "dataset_tag": params["dataset_tag"],
                        "claims": {
                            "$elemMatch": {
                                "field": params["claim_field"],
                                "value": params["claim_value"],
                            }
                        },
                    },
                    "fields": ["_id", "taxon_id", "accepted_name", "document_version"],
                    "limit": int(params.get("limit", 50)),
                },
            )
            resp.raise_for_status()
            docs = resp.json().get("docs", [])
            return sorted(docs, key=lambda d: d["taxon_id"])

        if op_name == "D3_versioned_dossier_update":
            taxon_id = params["taxon_id"]
            td_db = self._dbs["taxon_dossiers"]
            ver_db = self._dbs["taxon_dossier_versions"]

            resp = client.get(f"/{td_db}/{taxon_id}")
            resp.raise_for_status()
            current = resp.json()
            old_version = int(current["document_version"])
            new_version = old_version + 1

            snapshot = deepcopy(current)
            snapshot.pop("_rev", None)
            snapshot_id = f"{taxon_id}::v{old_version}::{params['update_seq']}"
            snapshot["_id"] = snapshot_id
            snapshot["archived_from_id"] = taxon_id
            put_ver = client.put(f"/{ver_db}/{snapshot_id}", json=snapshot)
            put_ver.raise_for_status()

            updated = deepcopy(current)
            updated["document_version"] = new_version
            updated["updated_at"] = params["timestamp"]
            updated.setdefault("claims", []).append(
                {
                    "claim_id": params["claim_id"],
                    "field": "ecology.notes",
                    "value": params["note_value"],
                    "source_id": params["source_id"],
                    "source_locator": params["source_locator"],
                }
            )
            put_doc = client.put(f"/{td_db}/{taxon_id}", json=updated)
            put_doc.raise_for_status()
            return {
                "taxon_id": taxon_id,
                "previous_version": old_version,
                "new_version": new_version,
            }

        if op_name == "D4_bulk_raw_source_insert":
            docs = deepcopy(params["docs"])
            self._bulk_insert(self._dbs["raw_source_records"], docs)
            return {"inserted_count": len(docs)}

        raise ValueError(f"Operación documental no soportada: {op_name}")

    def cleanup_test_data(self, dataset_tag: str) -> int:
        client = self._require_client()
        deleted = 0
        for db_name in self._dbs.values():
            check = client.get(f"/{db_name}")
            if check.status_code == 404:
                continue
            while True:
                resp = client.post(
                    f"/{db_name}/_find",
                    json={
                        "selector": {"dataset_tag": dataset_tag},
                        "fields": ["_id", "_rev"],
                        "limit": 500,
                    },
                )
                resp.raise_for_status()
                docs = resp.json().get("docs", [])
                if not docs:
                    break
                tombstones = [{"_id": d["_id"], "_rev": d["_rev"], "_deleted": True} for d in docs]
                del_resp = client.post(f"/{db_name}/_bulk_docs", json={"docs": tombstones})
                del_resp.raise_for_status()
                deleted += len(tombstones)
        return deleted

    def reset_all_data(self) -> None:
        client = self._require_client()
        for db_name in self._dbs.values():
            resp = client.delete(f"/{db_name}")
            if resp.status_code not in (200, 202, 404):
                resp.raise_for_status()
        self.prepare_schema()

    def get_storage_bytes(self) -> int | None:
        client = self._require_client()
        total = 0
        for db_name in self._dbs.values():
            resp = client.get(f"/{db_name}")
            if resp.status_code == 200:
                sizes = resp.json().get("sizes", {})
                total += int(sizes.get("active", sizes.get("file", 0)))
        return total

    def run_smoke_crud(self) -> SmokeResult:
        self.prepare_schema()
        smoke_tag = "SMOKE_TEST_COUCHDB"
        self.cleanup_test_data(smoke_tag)
        client = self._require_client()
        info = self.get_engine_info()

        docs = [
            {
                "_id": "SMOKE_DOC_1",
                "taxon_id": "SMOKE_DOC_1",
                "document_type": "taxon_dossier",
                "schema_version": 1,
                "dataset_tag": smoke_tag,
                "accepted_name": "Smoke Doc One",
                "organism_group": "ANIMAL",
                "claims": [{"claim_id": "C1", "field": "ecology.diet", "value": "SMOKE_FRUGIVORE", "source_id": "S1", "source_locator": "p.1"}],
                "document_version": 1,
                "updated_at": "2026-11-20T00:00:00Z",
            },
            {
                "_id": "SMOKE_DOC_2",
                "taxon_id": "SMOKE_DOC_2",
                "document_type": "taxon_dossier",
                "schema_version": 1,
                "dataset_tag": smoke_tag,
                "accepted_name": "Smoke Doc Two",
                "organism_group": "PLANT",
                "claims": [{"claim_id": "C2", "field": "ecology.diet", "value": "SMOKE_PRODUCER", "source_id": "S1", "source_locator": "p.2"}],
                "document_version": 1,
                "updated_at": "2026-11-20T00:00:00Z",
            },
        ]
        self._bulk_insert(self._dbs["taxon_dossiers"], docs)
        matched = self.execute_operation(
            "D2_nested_attribute_query",
            {"dataset_tag": smoke_tag, "claim_field": "ecology.diet", "claim_value": "SMOKE_FRUGIVORE"},
        )
        query_ok = len(matched) == 1 and matched[0]["taxon_id"] == "SMOKE_DOC_1"

        self.cleanup_test_data(smoke_tag)
        verify = client.post(
            f"/{self._dbs['taxon_dossiers']}/_find",
            json={"selector": {"dataset_tag": smoke_tag}, "fields": ["_id"], "limit": 10},
        )
        verify.raise_for_status()
        cleanup_ok = len(verify.json().get("docs", [])) == 0
        return SmokeResult(
            engine=self.engine_name,
            model=self.model_name,
            connected=True,
            health_ok=True,
            server_version=info["server_version"],
            inserted_records=2,
            query_ok=query_ok,
            cleanup_ok=cleanup_ok,
            details={"driver": info["driver"], "matched_rows": len(matched)},
        )
