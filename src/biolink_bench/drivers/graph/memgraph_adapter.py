from __future__ import annotations

from typing import Any

import neo4j
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import ClientError

from biolink_bench.config import EngineConfig
from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.drivers.base import BaseEngineAdapter, SmokeResult

MEMGRAPH_CONSTRAINTS = [
    "CREATE CONSTRAINT ON (t:Taxon) ASSERT t.taxon_id IS UNIQUE;",
    "CREATE CONSTRAINT ON (a:InteractionAssertion) ASSERT a.assertion_id IS UNIQUE;",
    "CREATE CONSTRAINT ON (l:Locality) ASSERT l.locality_id IS UNIQUE;",
    "CREATE CONSTRAINT ON (e:Evidence) ASSERT e.evidence_id IS UNIQUE;",
    "CREATE CONSTRAINT ON (s:Source) ASSERT s.source_id IS UNIQUE;",
]

MEMGRAPH_INDEXES = [
    "CREATE INDEX ON :Taxon(taxon_id);",
    "CREATE INDEX ON :Taxon(organism_group);",
    "CREATE INDEX ON :InteractionAssertion(assertion_id);",
    "CREATE INDEX ON :InteractionAssertion(status);",
    "CREATE INDEX ON :Locality(locality_id);",
]


class MemgraphAdapter(BaseEngineAdapter):
    """Adaptador directo nativo para Memgraph Community usando el protocolo Bolt."""

    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config)
        self._driver: Driver | None = None

    def _require_driver(self) -> Driver:
        if self._driver is None:
            raise RuntimeError("Cliente Bolt Memgraph no conectado; llame a connect() primero")
        return self._driver

    def connect(self) -> None:
        uri = f"bolt://{self.config.host}:{self.config.port}"
        auth = (self.config.user, self.config.password) if self.config.user else None
        self._driver = GraphDatabase.driver(
            uri,
            auth=auth,
            connection_timeout=10.0,
        )
        self._driver.verify_connectivity()

    def disconnect(self) -> None:
        if self._driver is not None:
            self._driver.close()
        self._driver = None

    def health_check(self) -> tuple[bool, str]:
        driver = self._require_driver()
        with driver.session() as session:
            val = session.run("RETURN 1 AS ok").single()["ok"]
            info = self.get_engine_info()
            return val == 1, f"Memgraph {info['server_version']}"

    def get_engine_info(self) -> dict[str, Any]:
        driver = self._require_driver()
        with driver.session() as session:
            rows = [dict(r) for r in session.run("SHOW VERSION;")]
            version = str(rows[0].get("version", "unknown")) if rows else "unknown"
            return {
                "engine": "memgraph",
                "server_version": version,
                "driver": f"neo4j {neo4j.__version__} (Bolt client for Memgraph)",
            }

    def prepare_schema(self) -> None:
        driver = self._require_driver()
        with driver.session() as session:
            for cypher in MEMGRAPH_CONSTRAINTS:
                try:
                    session.run(cypher).consume()
                except ClientError as exc:
                    if "already exists" not in str(exc).lower():
                        raise

    def load_dataset(self, bundle: DatasetBundle) -> dict[str, int]:
        driver = self._require_driver()
        self.cleanup_test_data(bundle.dataset_tag)
        published = bundle.published_assertions
        pub_ids = {a["assertion_id"] for a in published}
        ev_by_id = {e["evidence_id"]: e for e in bundle.evidences}
        ae_links = [ae for ae in bundle.assertion_evidences if ae["assertion_id"] in pub_ids]

        with driver.session() as session:
            for i in range(0, len(bundle.taxa), 500):
                session.run(
                    """
                    UNWIND $rows AS r
                    MERGE (t:Taxon {taxon_id: r.taxon_id})
                    SET t.accepted_name = r.accepted_name,
                        t.taxonomic_rank = r.taxonomic_rank,
                        t.organism_group = r.organism_group,
                        t.taxonomic_status = r.taxonomic_status,
                        t.dataset_tag = r.dataset_tag
                    """,
                    rows=bundle.taxa[i : i + 500],
                ).consume()

            session.run(
                """
                UNWIND $rows AS r
                MERGE (l:Locality {locality_id: r.locality_id})
                SET l.name = r.name,
                    l.locality_type = r.locality_type,
                    l.protected_status = r.protected_status,
                    l.spatial_validation_status = r.spatial_validation_status,
                    l.dataset_tag = r.dataset_tag
                """,
                rows=bundle.localities,
            ).consume()

            session.run(
                """
                UNWIND $rows AS r
                MERGE (s:Source {source_id: r.source_id})
                SET s.source_type = r.source_type,
                    s.title = r.title,
                    s.publication_year = r.publication_year,
                    s.doi_or_uri = coalesce(r.doi, r.uri),
                    s.dataset_tag = r.dataset_tag
                """,
                rows=bundle.sources,
            ).consume()

            ev_rows = [ev_by_id[ae["evidence_id"]] for ae in ae_links if ae["evidence_id"] in ev_by_id]
            for i in range(0, len(ev_rows), 500):
                session.run(
                    """
                    UNWIND $rows AS r
                    MERGE (e:Evidence {evidence_id: r.evidence_id})
                    SET e.evidence_kind = r.evidence_kind,
                        e.method_code = r.method_code,
                        e.source_locator = r.source_locator,
                        e.dataset_tag = r.dataset_tag
                    WITH e, r
                    MATCH (s:Source {source_id: r.source_id})
                    MERGE (e)-[:CITED_FROM]->(s)
                    """,
                    rows=ev_rows[i : i + 500],
                ).consume()

            for i in range(0, len(published), 500):
                session.run(
                    """
                    UNWIND $rows AS r
                    MATCH (actor:Taxon {taxon_id: r.actor_taxon_id})
                    MATCH (target:Taxon {taxon_id: r.target_taxon_id})
                    MATCH (loc:Locality {locality_id: r.locality_id})
                    MERGE (a:InteractionAssertion {assertion_id: r.assertion_id})
                    SET a.interaction_type_code = r.interaction_type_code,
                        a.period_start = r.period_start,
                        a.period_end = r.period_end,
                        a.season_label = r.season_label,
                        a.method_code = r.method_code,
                        a.status = r.status,
                        a.assertion_scope = r.assertion_scope,
                        a.dataset_tag = r.dataset_tag
                    MERGE (actor)-[:ACTOR_IN]->(a)
                    MERGE (a)-[:TARGETS]->(target)
                    MERGE (a)-[:OBSERVED_AT]->(loc)
                    """,
                    rows=published[i : i + 500],
                ).consume()

            for i in range(0, len(ae_links), 500):
                session.run(
                    """
                    UNWIND $rows AS r
                    MATCH (a:InteractionAssertion {assertion_id: r.assertion_id})
                    MATCH (e:Evidence {evidence_id: r.evidence_id})
                    MERGE (a)-[:SUPPORTED_BY]->(e)
                    """,
                    rows=ae_links[i : i + 500],
                ).consume()

        return {
            "taxa": len(bundle.taxa),
            "localities": len(bundle.localities),
            "sources": len(bundle.sources),
            "evidences": len(ev_rows),
            "published_assertions": len(published),
        }

    def create_indexes(self) -> None:
        driver = self._require_driver()
        with driver.session() as session:
            for cypher in MEMGRAPH_INDEXES:
                try:
                    session.run(cypher).consume()
                except ClientError as exc:
                    if "already exists" not in str(exc).lower():
                        raise

    def execute_operation(self, op_name: str, params: dict[str, Any]) -> Any:
        driver = self._require_driver()
        with driver.session() as session:
            if op_name == "G1_taxon_neighbors":
                result = session.run(
                    """
                    MATCH (actor:Taxon)-[:ACTOR_IN]->(a:InteractionAssertion)-[:TARGETS]->(target:Taxon)
                    MATCH (a)-[:OBSERVED_AT]->(l:Locality)
                    WHERE a.status = 'PUBLISHED' AND (actor.taxon_id = $taxon_id OR target.taxon_id = $taxon_id)
                    RETURN a.assertion_id AS assertion_id,
                           CASE WHEN actor.taxon_id = $taxon_id THEN target.taxon_id ELSE actor.taxon_id END AS partner_taxon_id,
                           CASE WHEN actor.taxon_id = $taxon_id THEN target.accepted_name ELSE actor.accepted_name END AS partner_name,
                           a.interaction_type_code AS interaction_type_code,
                           l.locality_id AS locality_id,
                           a.period_start AS period_start
                    ORDER BY a.assertion_id
                    """,
                    taxon_id=params["taxon_id"],
                )
                return [dict(r) for r in result]

            if op_name == "G2_filtered_subgraph":
                result = session.run(
                    """
                    MATCH (actor:Taxon)-[:ACTOR_IN]->(a:InteractionAssertion)-[:TARGETS]->(target:Taxon)
                    MATCH (a)-[:OBSERVED_AT]->(l:Locality)
                    WHERE a.status = 'PUBLISHED'
                      AND l.locality_id = $locality_id
                      AND a.interaction_type_code = $interaction_type_code
                      AND a.period_start >= $period_start
                    RETURN a.assertion_id AS assertion_id,
                           actor.taxon_id AS actor_taxon_id,
                           target.taxon_id AS target_taxon_id,
                           l.locality_id AS locality_id,
                           l.spatial_validation_status AS spatial_validation_status,
                           a.period_start AS period_start
                    ORDER BY a.assertion_id
                    LIMIT $limit
                    """,
                    locality_id=params["locality_id"],
                    interaction_type_code=params["interaction_type_code"],
                    period_start=params["period_start"],
                    limit=int(params.get("limit", 100)),
                )
                return [dict(r) for r in result]

            if op_name == "G3_distinct_partner_count":
                rec = session.run(
                    """
                    MATCH (actor:Taxon)-[:ACTOR_IN]->(a:InteractionAssertion)-[:TARGETS]->(target:Taxon)
                    MATCH (a)-[:OBSERVED_AT]->(l:Locality)
                    WHERE a.status = 'PUBLISHED'
                      AND (actor.taxon_id = $taxon_id OR target.taxon_id = $taxon_id)
                      AND ($locality_id IS NULL OR l.locality_id = $locality_id)
                    WITH CASE WHEN actor.taxon_id = $taxon_id THEN target.taxon_id ELSE actor.taxon_id END AS partner_id,
                         a.assertion_id AS assertion_id
                    RETURN count(DISTINCT partner_id) AS distinct_partner_count,
                           count(DISTINCT assertion_id) AS assertion_count
                    """,
                    taxon_id=params["taxon_id"],
                    locality_id=params.get("locality_id"),
                ).single()
                return {
                    "taxon_id": params["taxon_id"],
                    "distinct_partner_count": int(rec["distinct_partner_count"]) if rec else 0,
                    "assertion_count": int(rec["assertion_count"]) if rec else 0,
                }

            if op_name == "G4_idempotent_assertion_upsert":
                rec = session.run(
                    """
                    MATCH (actor:Taxon {taxon_id: $actor_taxon_id})
                    MATCH (target:Taxon {taxon_id: $target_taxon_id})
                    MATCH (loc:Locality {locality_id: $locality_id})
                    MERGE (src:Source {source_id: $source_id})
                      ON CREATE SET src.title = $source_title, src.dataset_tag = $dataset_tag
                    MERGE (ev:Evidence {evidence_id: $evidence_id})
                      ON CREATE SET ev.evidence_kind = 'WORKLOAD_PROJECTION',
                                    ev.method_code = $method_code,
                                    ev.source_locator = $source_locator,
                                    ev.dataset_tag = $dataset_tag
                    MERGE (ev)-[:CITED_FROM]->(src)
                    MERGE (a:InteractionAssertion {assertion_id: $assertion_id})
                      ON CREATE SET a.interaction_type_code = $interaction_type_code,
                                    a.period_start = $period_start,
                                    a.period_end = $period_end,
                                    a.season_label = $season_label,
                                    a.method_code = $method_code,
                                    a.status = 'PUBLISHED',
                                    a.assertion_scope = 'PROJECTION_EVENT',
                                    a.dataset_tag = $dataset_tag
                      ON MATCH SET  a.interaction_type_code = $interaction_type_code,
                                    a.period_start = $period_start,
                                    a.period_end = $period_end,
                                    a.season_label = $season_label,
                                    a.method_code = $method_code,
                                    a.status = 'PUBLISHED',
                                    a.dataset_tag = $dataset_tag
                    MERGE (actor)-[:ACTOR_IN]->(a)
                    MERGE (a)-[:TARGETS]->(target)
                    MERGE (a)-[:OBSERVED_AT]->(loc)
                    MERGE (a)-[:SUPPORTED_BY]->(ev)
                    RETURN a.assertion_id AS assertion_id, a.status AS status
                    """,
                    **params,
                ).single()
                if rec is None:
                    raise RuntimeError("G4 upsert no encontró nodos Taxon/Locality referenciados")
                return dict(rec)

            raise ValueError(f"Operación de grafo no soportada: {op_name}")

    def cleanup_test_data(self, dataset_tag: str) -> int:
        driver = self._require_driver()
        total_deleted = 0
        with driver.session() as session:
            while True:
                rec = session.run(
                    """
                    MATCH (n {dataset_tag: $tag})
                    WITH n LIMIT 2000
                    DETACH DELETE n
                    RETURN count(n) AS deleted
                    """,
                    tag=dataset_tag,
                ).single()
                count = int(rec["deleted"]) if rec else 0
                total_deleted += count
                if count == 0:
                    break
        return total_deleted

    def reset_all_data(self) -> None:
        driver = self._require_driver()
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n").consume()

    def get_storage_bytes(self) -> int | None:
        driver = self._require_driver()
        with driver.session() as session:
            rows = {}
            for rec in session.run("SHOW STORAGE INFO;"):
                d = dict(rec)
                key = d.get("storage info") or d.get("name")
                if key is not None:
                    rows[str(key)] = d.get("value")
            mem_usage = rows.get("memory_tracked") or rows.get("memory_res") or rows.get("disk_usage")
            if isinstance(mem_usage, (int, float)):
                return int(mem_usage)
            if isinstance(mem_usage, str):
                m = __import__("re").match(r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)", mem_usage.strip())
                if m:
                    val = float(m.group(1))
                    unit = m.group(2).lower()
                    scale = {
                        "b": 1,
                        "kb": 1000,
                        "kib": 1024,
                        "mb": 1000**2,
                        "mib": 1024**2,
                        "gb": 1000**3,
                        "gib": 1024**3,
                    }.get(unit, 1)
                    return int(val * scale)
            return None

    def run_smoke_crud(self) -> SmokeResult:
        self.prepare_schema()
        smoke_tag = "SMOKE_TEST_MEMGRAPH"
        self.cleanup_test_data(smoke_tag)
        driver = self._require_driver()
        info = self.get_engine_info()
        with driver.session() as session:
            session.run(
                """
                CREATE (a:Taxon {taxon_id: 'SMOKE_MG_AN', accepted_name: 'Smoke Bat', organism_group: 'ANIMAL', dataset_tag: $tag})
                CREATE (p:Taxon {taxon_id: 'SMOKE_MG_PL', accepted_name: 'Smoke Tree', organism_group: 'PLANT', dataset_tag: $tag})
                CREATE (l:Locality {locality_id: 'SMOKE_MG_LOC', name: 'Smoke Sector', spatial_validation_status: 'INSIDE_ANP', dataset_tag: $tag})
                CREATE (i:InteractionAssertion {assertion_id: 'SMOKE_MG_AST', interaction_type_code: 'CONSUMES_FRUIT_OF', period_start: '2026-01', status: 'PUBLISHED', dataset_tag: $tag})
                CREATE (a)-[:ACTOR_IN]->(i)
                CREATE (i)-[:TARGETS]->(p)
                CREATE (i)-[:OBSERVED_AT]->(l)
                """,
                tag=smoke_tag,
            ).consume()

        neighbors = self.execute_operation("G1_taxon_neighbors", {"taxon_id": "SMOKE_MG_AN"})
        query_ok = len(neighbors) == 1 and neighbors[0]["partner_taxon_id"] == "SMOKE_MG_PL"

        self.cleanup_test_data(smoke_tag)
        with driver.session() as session:
            cnt = session.run("MATCH (n {dataset_tag: $tag}) RETURN count(n) AS cnt", tag=smoke_tag).single()["cnt"]

        return SmokeResult(
            engine=self.engine_name,
            model=self.model_name,
            connected=True,
            health_ok=True,
            server_version=info["server_version"],
            inserted_records=2,
            query_ok=query_ok,
            cleanup_ok=cnt == 0,
            details={"driver": info["driver"], "matched_rows": len(neighbors)},
        )
