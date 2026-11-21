from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from biolink_bench.config import EngineConfig
from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.drivers.base import BaseEngineAdapter, SmokeResult
from biolink_bench.drivers.relational._common import (
    BENCH_USERS,
    chunked,
    prepare_relational_rows,
    serialize_outbox_payload,
)

PG_DDL = [
    """
    CREATE TABLE IF NOT EXISTS app_user (
        user_id VARCHAR(64) PRIMARY KEY,
        display_name VARCHAR(128) NOT NULL,
        email VARCHAR(160) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at VARCHAR(32) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source (
        source_id VARCHAR(64) PRIMARY KEY,
        source_type VARCHAR(32) NOT NULL,
        title VARCHAR(512) NOT NULL,
        authors VARCHAR(512) NOT NULL,
        publication_year INTEGER NOT NULL,
        doi VARCHAR(128),
        uri VARCHAR(255),
        publisher VARCHAR(160),
        citation_text VARCHAR(512),
        license_id VARCHAR(64) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS source_version (
        source_version_id VARCHAR(64) PRIMARY KEY,
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        provider_version VARCHAR(64) NOT NULL,
        release_date VARCHAR(32) NOT NULL,
        endpoint_or_file VARCHAR(255) NOT NULL,
        query_parameters TEXT NOT NULL,
        filters TEXT NOT NULL,
        license_id VARCHAR(64) NOT NULL,
        checksum VARCHAR(128) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS locality (
        locality_id VARCHAR(64) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        locality_type VARCHAR(64) NOT NULL,
        parent_locality_id VARCHAR(64),
        protected_status VARCHAR(64) NOT NULL,
        spatial_validation_status VARCHAR(64) NOT NULL,
        coordinate_precision VARCHAR(64),
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS taxon (
        taxon_id VARCHAR(64) PRIMARY KEY,
        accepted_name VARCHAR(255) NOT NULL,
        scientific_authorship VARCHAR(160) NOT NULL,
        taxonomic_rank VARCHAR(32) NOT NULL,
        organism_group VARCHAR(32) NOT NULL,
        taxonomic_status VARCHAR(64) NOT NULL,
        created_at VARCHAR(32) NOT NULL,
        updated_at VARCHAR(32) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS taxon_name (
        taxon_name_id VARCHAR(64) PRIMARY KEY,
        taxon_id VARCHAR(64) NOT NULL REFERENCES taxon(taxon_id),
        name VARCHAR(255) NOT NULL,
        name_usage VARCHAR(32) NOT NULL,
        language VARCHAR(16) NOT NULL,
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        is_preferred BOOLEAN NOT NULL,
        verbatim_name VARCHAR(255) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS taxon_identifier (
        taxon_identifier_id VARCHAR(64) PRIMARY KEY,
        taxon_id VARCHAR(64) NOT NULL REFERENCES taxon(taxon_id),
        scheme VARCHAR(64) NOT NULL,
        external_id VARCHAR(128) NOT NULL,
        retrieved_at VARCHAR(32) NOT NULL,
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        dataset_tag VARCHAR(64) NOT NULL,
        CONSTRAINT uq_pg_taxon_ident UNIQUE (scheme, external_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS interaction_type (
        interaction_type_id VARCHAR(64) PRIMARY KEY,
        code VARCHAR(64) NOT NULL UNIQUE,
        label VARCHAR(128) NOT NULL,
        definition VARCHAR(512) NOT NULL,
        actor_role VARCHAR(32) NOT NULL,
        target_role VARCHAR(32) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id VARCHAR(64) PRIMARY KEY,
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        source_version_id VARCHAR(64) NOT NULL REFERENCES source_version(source_version_id),
        source_locator VARCHAR(255) NOT NULL,
        evidence_kind VARCHAR(64) NOT NULL,
        method_code VARCHAR(64) NOT NULL,
        reported_term VARCHAR(128) NOT NULL,
        summary TEXT NOT NULL,
        interpretation_limit TEXT NOT NULL,
        period_start VARCHAR(32) NOT NULL,
        period_end VARCHAR(32) NOT NULL,
        license_id VARCHAR(64) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS interaction_assertion (
        assertion_id VARCHAR(64) PRIMARY KEY,
        actor_taxon_id VARCHAR(64) NOT NULL REFERENCES taxon(taxon_id),
        target_taxon_id VARCHAR(64) NOT NULL REFERENCES taxon(taxon_id),
        interaction_type_id VARCHAR(64) NOT NULL REFERENCES interaction_type(interaction_type_id),
        locality_id VARCHAR(64) NOT NULL REFERENCES locality(locality_id),
        period_start VARCHAR(32) NOT NULL,
        period_end VARCHAR(32) NOT NULL,
        season_label VARCHAR(128) NOT NULL,
        method_code VARCHAR(64) NOT NULL,
        assertion_scope VARCHAR(64) NOT NULL,
        status VARCHAR(32) NOT NULL,
        created_by VARCHAR(64) NOT NULL REFERENCES app_user(user_id),
        created_at VARCHAR(32) NOT NULL,
        reviewed_by VARCHAR(64),
        reviewed_at VARCHAR(32),
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS assertion_evidence (
        assertion_id VARCHAR(64) NOT NULL REFERENCES interaction_assertion(assertion_id),
        evidence_id VARCHAR(64) NOT NULL REFERENCES evidence(evidence_id),
        evidence_role VARCHAR(32) NOT NULL,
        review_note VARCHAR(512) NOT NULL,
        PRIMARY KEY (assertion_id, evidence_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS import_batch (
        import_batch_id VARCHAR(64) PRIMARY KEY,
        source_id VARCHAR(64) NOT NULL REFERENCES source(source_id),
        source_version_id VARCHAR(64) NOT NULL,
        started_by VARCHAR(64) NOT NULL REFERENCES app_user(user_id),
        started_at VARCHAR(32) NOT NULL,
        finished_at VARCHAR(32) NOT NULL,
        query_parameters TEXT NOT NULL,
        filters TEXT NOT NULL,
        status VARCHAR(32) NOT NULL,
        received_count INTEGER NOT NULL,
        accepted_count INTEGER NOT NULL,
        rejected_count INTEGER NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS import_record (
        import_record_id VARCHAR(64) PRIMARY KEY,
        import_batch_id VARCHAR(64) NOT NULL REFERENCES import_batch(import_batch_id),
        external_record_id VARCHAR(64) NOT NULL,
        raw_document_id VARCHAR(64) NOT NULL,
        validation_status VARCHAR(32) NOT NULL,
        canonical_taxon_id VARCHAR(64),
        validation_notes VARCHAR(255) NOT NULL,
        dataset_tag VARCHAR(64) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS review_event (
        review_event_id VARCHAR(64) PRIMARY KEY,
        assertion_id VARCHAR(64) NOT NULL REFERENCES interaction_assertion(assertion_id),
        user_id VARCHAR(64) NOT NULL REFERENCES app_user(user_id),
        previous_status VARCHAR(32) NOT NULL,
        new_status VARCHAR(32) NOT NULL,
        reason VARCHAR(255) NOT NULL,
        created_at VARCHAR(32) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS outbox_event (
        outbox_event_id VARCHAR(64) PRIMARY KEY,
        aggregate_type VARCHAR(64) NOT NULL,
        aggregate_id VARCHAR(64) NOT NULL,
        event_type VARCHAR(64) NOT NULL,
        payload_json JSONB NOT NULL,
        status VARCHAR(32) NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        created_at VARCHAR(32) NOT NULL
    )
    """,
]

PG_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_taxon_name_lookup ON taxon_name (name, taxon_id)",
    "CREATE INDEX IF NOT EXISTS idx_taxon_accepted ON taxon (accepted_name)",
    "CREATE INDEX IF NOT EXISTS idx_assertion_filter ON interaction_assertion (status, locality_id, period_start, period_end)",
    "CREATE INDEX IF NOT EXISTS idx_assertion_actor ON interaction_assertion (actor_taxon_id)",
    "CREATE INDEX IF NOT EXISTS idx_assertion_target ON interaction_assertion (target_taxon_id)",
    "CREATE INDEX IF NOT EXISTS idx_import_record_batch ON import_record (import_batch_id)",
]


class PostgreSQLAdapter(BaseEngineAdapter):
    """Adaptador directo nativo para PostgreSQL 18.7 usando psycopg 3."""

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._conn: psycopg.Connection[Any] | None = None

    def _require_conn(self) -> psycopg.Connection[Any]:
        if self._conn is None or self._conn.closed:
            raise RuntimeError("Conexión PostgreSQL no establecida; llame a connect() primero")
        return self._conn

    def connect(self) -> None:
        self._conn = psycopg.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            dbname=self.config.database,
            connect_timeout=10,
            autocommit=False,
        )

    def disconnect(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None

    def health_check(self) -> tuple[bool, str]:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute("SHOW server_version")
            row = cur.fetchone()
            return True, f"PostgreSQL {row[0]}" if row else "PostgreSQL OK"

    def get_engine_info(self) -> dict[str, Any]:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT version(), current_setting('server_version'), current_setting('shared_buffers')")
            full_ver, short_ver, shared_buf = cur.fetchone()
            return {
                "engine": "postgresql",
                "server_version": short_ver,
                "version_detail": full_ver,
                "shared_buffers": shared_buf,
                "driver": f"psycopg {psycopg.__version__}",
            }

    def prepare_schema(self) -> None:
        conn = self._require_conn()
        with conn.transaction():
            with conn.cursor() as cur:
                for ddl in PG_DDL:
                    cur.execute(ddl)
                cur.executemany(
                    """
                    INSERT INTO app_user (user_id, display_name, email, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    BENCH_USERS,
                )

    def load_dataset(self, bundle: DatasetBundle) -> dict[str, int]:
        conn = self._require_conn()
        self.cleanup_test_data(bundle.dataset_tag)
        rows = prepare_relational_rows(bundle)
        inserts = [
            ("source", "INSERT INTO source VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("source_version", "INSERT INTO source_version VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("locality", "INSERT INTO locality VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("taxon", "INSERT INTO taxon VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("taxon_name", "INSERT INTO taxon_name VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("taxon_identifier", "INSERT INTO taxon_identifier VALUES (%s,%s,%s,%s,%s,%s,%s)"),
            (
                "interaction_type",
                "INSERT INTO interaction_type VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (interaction_type_id) DO NOTHING",
            ),
            ("evidence", "INSERT INTO evidence VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            (
                "interaction_assertion",
                "INSERT INTO interaction_assertion VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            ),
            ("assertion_evidence", "INSERT INTO assertion_evidence VALUES (%s,%s,%s,%s)"),
            ("import_batch", "INSERT INTO import_batch VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("import_record", "INSERT INTO import_record VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"),
            ("review_event", "INSERT INTO review_event VALUES (%s,%s,%s,%s,%s,%s,%s)"),
        ]

        counts: dict[str, int] = {}
        with conn.transaction():
            with conn.cursor() as cur:
                for table, sql in inserts:
                    table_rows = rows[table]
                    for batch in chunked(table_rows, 500):
                        cur.executemany(sql, batch)
                    counts[table] = len(table_rows)
        return counts

    def create_indexes(self) -> None:
        conn = self._require_conn()
        with conn.transaction():
            with conn.cursor() as cur:
                for sql in PG_INDEXES:
                    cur.execute(sql)

    def execute_operation(self, op_name: str, params: dict[str, Any]) -> Any:
        conn = self._require_conn()
        if op_name == "R1_taxon_search":
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT DISTINCT
                        t.taxon_id,
                        t.accepted_name,
                        t.taxonomic_rank,
                        t.organism_group,
                        tn.name AS matched_name,
                        tn.name_usage
                    FROM taxon_name tn
                    JOIN taxon t ON t.taxon_id = tn.taxon_id
                    WHERE tn.name = %s
                    ORDER BY t.taxon_id
                    """,
                    (params["query_name"],),
                )
                return cur.fetchall()

        if op_name == "R2_filtered_assertions":
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT
                        ia.assertion_id,
                        ia.actor_taxon_id,
                        ia.target_taxon_id,
                        it.code AS interaction_type_code,
                        ia.locality_id,
                        ia.period_start,
                        ia.period_end,
                        ia.status
                    FROM interaction_assertion ia
                    JOIN interaction_type it ON it.interaction_type_id = ia.interaction_type_id
                    WHERE ia.locality_id = %s
                      AND ia.period_start >= %s
                      AND ia.status = %s
                    ORDER BY ia.assertion_id
                    LIMIT %s
                    """,
                    (
                        params["locality_id"],
                        params["period_start"],
                        params.get("status", "PUBLISHED"),
                        int(params.get("limit", 100)),
                    ),
                )
                return cur.fetchall()

        if op_name == "R3_transactional_assertion_outbox":
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO evidence (
                            evidence_id, source_id, source_version_id, source_locator,
                            evidence_kind, method_code, reported_term, summary,
                            interpretation_limit, period_start, period_end, license_id, dataset_tag
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            params["evidence_id"],
                            params["source_id"],
                            params["source_version_id"],
                            params["source_locator"],
                            "WORKLOAD_TRANSACTION",
                            params["method_code"],
                            params["interaction_type_code"],
                            "Workload R3 transactional assertion",
                            "SYNTHETIC_BENCHMARK transactional check",
                            params["period_start"],
                            params["period_end"],
                            "CC-BY-4.0-SYNTHETIC",
                            params["dataset_tag"],
                        ),
                    )
                    cur.execute(
                        """
                        INSERT INTO interaction_assertion (
                            assertion_id, actor_taxon_id, target_taxon_id, interaction_type_id,
                            locality_id, period_start, period_end, season_label, method_code,
                            assertion_scope, status, created_by, created_at, reviewed_by, reviewed_at, dataset_tag
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            params["assertion_id"],
                            params["actor_taxon_id"],
                            params["target_taxon_id"],
                            params["interaction_type_id"],
                            params["locality_id"],
                            params["period_start"],
                            params["period_end"],
                            params["season_label"],
                            params["method_code"],
                            "WORKLOAD_R3",
                            "PUBLISHED",
                            "USR_BENCH_CURATOR",
                            params["timestamp"],
                            "USR_BENCH_REVIEWER",
                            params["timestamp"],
                            params["dataset_tag"],
                        ),
                    )
                    cur.execute(
                        """
                        INSERT INTO assertion_evidence (assertion_id, evidence_id, evidence_role, review_note)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (params["assertion_id"], params["evidence_id"], "PRIMARY", "R3 transactional"),
                    )
                    cur.execute(
                        """
                        INSERT INTO review_event (
                            review_event_id, assertion_id, user_id, previous_status, new_status, reason, created_at
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            params["review_event_id"],
                            params["assertion_id"],
                            "USR_BENCH_REVIEWER",
                            "IN_REVIEW",
                            "PUBLISHED",
                            "Workload R3 approval",
                            params["timestamp"],
                        ),
                    )
                    cur.execute(
                        """
                        INSERT INTO outbox_event (
                            outbox_event_id, aggregate_type, aggregate_id, event_type,
                            payload_json, status, attempts, created_at
                        ) VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s)
                        """,
                        (
                            params["outbox_event_id"],
                            "InteractionAssertion",
                            params["assertion_id"],
                            "ASSERTION_PUBLISHED",
                            serialize_outbox_payload(params),
                            "PENDING",
                            0,
                            params["timestamp"],
                        ),
                    )
            return {
                "assertion_id": params["assertion_id"],
                "evidence_id": params["evidence_id"],
                "review_event_id": params["review_event_id"],
                "outbox_event_id": params["outbox_event_id"],
                "committed": True,
            }

        if op_name == "R4_batch_import_insert":
            records = params["records"]
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO import_batch (
                            import_batch_id, source_id, source_version_id, started_by,
                            started_at, finished_at, query_parameters, filters,
                            status, received_count, accepted_count, rejected_count, dataset_tag
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            params["import_batch_id"],
                            params["source_id"],
                            params["source_version_id"],
                            "USR_BENCH_INGESTION",
                            params["timestamp"],
                            params["timestamp"],
                            '{"workload": "R4"}',
                            '{"dataset_tag": "SYNTHETIC_BENCHMARK"}',
                            "COMPLETED",
                            len(records),
                            len(records),
                            0,
                            params["dataset_tag"],
                        ),
                    )
                    cur.executemany(
                        """
                        INSERT INTO import_record (
                            import_record_id, import_batch_id, external_record_id, raw_document_id,
                            validation_status, canonical_taxon_id, validation_notes, dataset_tag
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        [
                            (
                                r["import_record_id"],
                                params["import_batch_id"],
                                r["external_record_id"],
                                r["raw_document_id"],
                                "ACCEPTED",
                                r["canonical_taxon_id"],
                                "Workload R4 batch",
                                params["dataset_tag"],
                            )
                            for r in records
                        ],
                    )
            return {
                "import_batch_id": params["import_batch_id"],
                "inserted_records": len(records),
            }

        raise ValueError(f"Operación relacional no soportada: {op_name}")

    def cleanup_test_data(self, dataset_tag: str) -> int:
        conn = self._require_conn()
        deleted = 0
        statements = [
            (
                "DELETE FROM outbox_event WHERE aggregate_id IN "
                "(SELECT assertion_id FROM interaction_assertion WHERE dataset_tag = %s)"
            ),
            (
                "DELETE FROM review_event WHERE assertion_id IN "
                "(SELECT assertion_id FROM interaction_assertion WHERE dataset_tag = %s)"
            ),
            (
                "DELETE FROM assertion_evidence WHERE assertion_id IN "
                "(SELECT assertion_id FROM interaction_assertion WHERE dataset_tag = %s)"
            ),
            "DELETE FROM interaction_assertion WHERE dataset_tag = %s",
            "DELETE FROM evidence WHERE dataset_tag = %s",
            "DELETE FROM import_record WHERE dataset_tag = %s",
            "DELETE FROM import_batch WHERE dataset_tag = %s",
            "DELETE FROM taxon_identifier WHERE dataset_tag = %s",
            "DELETE FROM taxon_name WHERE dataset_tag = %s",
            "DELETE FROM taxon WHERE dataset_tag = %s",
            "DELETE FROM locality WHERE dataset_tag = %s",
            "DELETE FROM source_version WHERE dataset_tag = %s",
            "DELETE FROM source WHERE dataset_tag = %s",
        ]
        with conn.transaction():
            with conn.cursor() as cur:
                for sql in statements:
                    cur.execute(sql, (dataset_tag,))
                    deleted += cur.rowcount
        return deleted

    def reset_all_data(self) -> None:
        conn = self._require_conn()
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    TRUNCATE TABLE
                        outbox_event,
                        review_event,
                        assertion_evidence,
                        interaction_assertion,
                        import_record,
                        import_batch,
                        evidence,
                        taxon_identifier,
                        taxon_name,
                        taxon,
                        locality,
                        source_version,
                        source
                    CASCADE
                    """
                )

    def get_storage_bytes(self) -> int | None:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT pg_database_size(current_database())")
            (size_bytes,) = cur.fetchone()
            return int(size_bytes)

    def run_smoke_crud(self) -> SmokeResult:
        self.prepare_schema()
        smoke_tag = "SMOKE_TEST_PG"
        self.cleanup_test_data(smoke_tag)
        conn = self._require_conn()
        info = self.get_engine_info()
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO source VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        "SMOKE_SRC_001",
                        "PUBLICATION",
                        "Smoke Test Study",
                        "Smoke Author",
                        2026,
                        None,
                        None,
                        "BioLink Smoke",
                        "Smoke test",
                        "CC-BY-4.0",
                        smoke_tag,
                    ),
                )
                cur.executemany(
                    "INSERT INTO taxon VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [
                        (
                            "SMOKE_TAX_AN",
                            "Smoke Animalis",
                            "",
                            "SPECIES",
                            "ANIMAL",
                            "ACCEPTED",
                            "2026-11-20T00:00:00Z",
                            "2026-11-20T00:00:00Z",
                            smoke_tag,
                        ),
                        (
                            "SMOKE_TAX_PL",
                            "Smoke Planta",
                            "",
                            "SPECIES",
                            "PLANT",
                            "ACCEPTED",
                            "2026-11-20T00:00:00Z",
                            "2026-11-20T00:00:00Z",
                            smoke_tag,
                        ),
                    ],
                )
                cur.execute(
                    "INSERT INTO taxon_name VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        "SMOKE_TN_1",
                        "SMOKE_TAX_AN",
                        "Smoke Animalis",
                        "ACCEPTED",
                        "la",
                        "SMOKE_SRC_001",
                        True,
                        "Smoke Animalis",
                        smoke_tag,
                    ),
                )

        rows = self.execute_operation("R1_taxon_search", {"query_name": "Smoke Animalis"})
        query_ok = len(rows) == 1 and rows[0]["taxon_id"] == "SMOKE_TAX_AN"

        self.cleanup_test_data(smoke_tag)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM taxon WHERE dataset_tag = %s", (smoke_tag,))
            cleanup_ok = cur.fetchone()[0] == 0

        return SmokeResult(
            engine=self.engine_name,
            model=self.model_name,
            connected=True,
            health_ok=True,
            server_version=info["server_version"],
            inserted_records=2,
            query_ok=query_ok,
            cleanup_ok=cleanup_ok,
            details={"driver": info["driver"], "matched_rows": len(rows)},
        )
