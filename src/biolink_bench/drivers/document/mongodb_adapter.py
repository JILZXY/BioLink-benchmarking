from __future__ import annotations

from copy import deepcopy
from typing import Any

import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import CollectionInvalid

from biolink_bench.config import EngineConfig
from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.drivers.base import BaseEngineAdapter, SmokeResult

TAXON_DOSSIER_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "taxon_id", "document_type", "schema_version", "claims", "document_version", "dataset_tag"],
        "properties": {
            "_id": {"bsonType": "string"},
            "taxon_id": {"bsonType": "string"},
            "document_type": {"enum": ["taxon_dossier"]},
            "schema_version": {"bsonType": "int", "minimum": 1},
            "document_version": {"bsonType": "int", "minimum": 1},
            "dataset_tag": {"bsonType": "string"},
            "claims": {"bsonType": "array"},
        },
    }
}


class MongoDBAdapter(BaseEngineAdapter):
    """Adaptador directo nativo para MongoDB Community 8.0 usando pymongo."""

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._client: MongoClient[dict[str, Any]] | None = None
        self._db: Database[dict[str, Any]] | None = None

    def _require_db(self) -> Database[dict[str, Any]]:
        if self._client is None or self._db is None:
            raise RuntimeError("Conexión MongoDB no establecida; llame a connect() primero")
        return self._db

    def connect(self) -> None:
        self._client = MongoClient(
            host=self.config.host,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
            authSource="admin",
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        self._db = self._client[self.config.database]
        self._client.admin.command("ping")

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None

    def health_check(self) -> tuple[bool, str]:
        db = self._require_db()
        res = db.client.admin.command("buildInfo")
        return True, f"MongoDB {res['version']}"

    def get_engine_info(self) -> dict[str, Any]:
        db = self._require_db()
        build = db.client.admin.command("buildInfo")
        return {
            "engine": "mongodb",
            "server_version": build["version"],
            "driver": f"pymongo {pymongo.__version__}",
        }

    def prepare_schema(self) -> None:
        db = self._require_db()
        existing = set(db.list_collection_names())
        if "taxon_dossiers" not in existing:
            try:
                db.create_collection("taxon_dossiers", validator=TAXON_DOSSIER_VALIDATOR)
            except CollectionInvalid:
                pass
        for col in ("taxon_dossier_versions", "study_dossiers", "raw_source_records"):
            if col not in existing:
                try:
                    db.create_collection(col)
                except CollectionInvalid:
                    pass

    def load_dataset(self, bundle: DatasetBundle) -> dict[str, int]:
        db = self._require_db()
        self.cleanup_test_data(bundle.dataset_tag)
        counts: dict[str, int] = {}
        mapping = [
            ("taxon_dossiers", bundle.taxon_dossiers),
            ("study_dossiers", bundle.study_dossiers),
            ("raw_source_records", bundle.raw_source_records),
        ]
        for col_name, docs in mapping:
            if docs:
                for i in range(0, len(docs), 1000):
                    db[col_name].insert_many(deepcopy(docs[i : i + 1000]), ordered=True)
            counts[col_name] = len(docs)
        return counts

    def create_indexes(self) -> None:
        db = self._require_db()
        db["taxon_dossiers"].create_index([("taxon_id", 1)], name="idx_taxon_id")
        db["taxon_dossiers"].create_index(
            [("dataset_tag", 1), ("claims.field", 1), ("claims.value", 1)],
            name="idx_claims_nested",
        )
        db["taxon_dossiers"].create_index(
            [("dataset_tag", 1), ("organism_group", 1)],
            name="idx_tag_group",
        )
        db["taxon_dossier_versions"].create_index(
            [("taxon_id", 1), ("document_version", 1)],
            name="idx_version_history",
        )
        db["raw_source_records"].create_index(
            [("dataset_tag", 1), ("import_batch_id", 1)],
            name="idx_raw_batch",
        )

    def execute_operation(self, op_name: str, params: dict[str, Any]) -> Any:
        db = self._require_db()
        if op_name == "D1_read_taxon_dossier":
            doc = db["taxon_dossiers"].find_one({"_id": params["taxon_id"]})
            if doc is None:
                return None
            return {
                "taxon_id": doc["taxon_id"],
                "accepted_name": doc.get("accepted_name"),
                "document_version": doc["document_version"],
                "claims_count": len(doc.get("claims", [])),
            }

        if op_name == "D2_nested_attribute_query":
            cursor = (
                db["taxon_dossiers"]
                .find(
                    {
                        "dataset_tag": params["dataset_tag"],
                        "claims": {
                            "$elemMatch": {
                                "field": params["claim_field"],
                                "value": params["claim_value"],
                            }
                        },
                    },
                    {"_id": 1, "taxon_id": 1, "accepted_name": 1, "document_version": 1},
                )
                .sort("taxon_id", 1)
                .limit(int(params.get("limit", 50)))
            )
            return list(cursor)

        if op_name == "D3_versioned_dossier_update":
            taxon_id = params["taxon_id"]
            current = db["taxon_dossiers"].find_one({"_id": taxon_id})
            if current is None:
                raise KeyError(f"No existe taxon_dossier para {taxon_id}")
            old_version = int(current["document_version"])
            new_version = old_version + 1
            snapshot = deepcopy(current)
            snapshot["_id"] = f"{taxon_id}::v{old_version}::{params['update_seq']}"
            snapshot["archived_from_id"] = taxon_id
            db["taxon_dossier_versions"].insert_one(snapshot)

            db["taxon_dossiers"].update_one(
                {"_id": taxon_id},
                {
                    "$set": {
                        "document_version": new_version,
                        "updated_at": params["timestamp"],
                    },
                    "$push": {
                        "claims": {
                            "claim_id": params["claim_id"],
                            "field": "ecology.notes",
                            "value": params["note_value"],
                            "source_id": params["source_id"],
                            "source_locator": params["source_locator"],
                        }
                    },
                },
            )
            return {
                "taxon_id": taxon_id,
                "previous_version": old_version,
                "new_version": new_version,
            }

        if op_name == "D4_bulk_raw_source_insert":
            docs = deepcopy(params["docs"])
            res = db["raw_source_records"].insert_many(docs, ordered=True)
            return {"inserted_count": len(res.inserted_ids)}

        raise ValueError(f"Operación documental no soportada: {op_name}")

    def cleanup_test_data(self, dataset_tag: str) -> int:
        db = self._require_db()
        deleted = 0
        for col in ("taxon_dossiers", "taxon_dossier_versions", "study_dossiers", "raw_source_records"):
            res = db[col].delete_many({"dataset_tag": dataset_tag})
            deleted += res.deleted_count
        return deleted

    def reset_all_data(self) -> None:
        db = self._require_db()
        for col in ("taxon_dossiers", "taxon_dossier_versions", "study_dossiers", "raw_source_records"):
            db[col].delete_many({})

    def get_storage_bytes(self) -> int | None:
        db = self._require_db()
        stats = db.command("dbStats")
        return int(stats.get("storageSize", 0) + stats.get("indexSize", 0))

    def run_smoke_crud(self) -> SmokeResult:
        self.prepare_schema()
        smoke_tag = "SMOKE_TEST_MONGODB"
        self.cleanup_test_data(smoke_tag)
        db = self._require_db()
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
        db["taxon_dossiers"].insert_many(docs, ordered=True)
        matched = self.execute_operation(
            "D2_nested_attribute_query",
            {"dataset_tag": smoke_tag, "claim_field": "ecology.diet", "claim_value": "SMOKE_FRUGIVORE"},
        )
        query_ok = len(matched) == 1 and matched[0]["taxon_id"] == "SMOKE_DOC_1"

        self.cleanup_test_data(smoke_tag)
        remaining = db["taxon_dossiers"].count_documents({"dataset_tag": smoke_tag})
        return SmokeResult(
            engine=self.engine_name,
            model=self.model_name,
            connected=True,
            health_ok=True,
            server_version=info["server_version"],
            inserted_records=2,
            query_ok=query_ok,
            cleanup_ok=remaining == 0,
            details={"driver": info["driver"], "matched_rows": len(matched)},
        )
