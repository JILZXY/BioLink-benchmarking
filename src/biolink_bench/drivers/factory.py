from __future__ import annotations

from biolink_bench.config import EngineConfig
from biolink_bench.drivers.base import BaseEngineAdapter
from biolink_bench.drivers.document.couchdb_adapter import CouchDBAdapter
from biolink_bench.drivers.document.mongodb_adapter import MongoDBAdapter
from biolink_bench.drivers.graph.memgraph_adapter import MemgraphAdapter
from biolink_bench.drivers.graph.neo4j_adapter import Neo4jAdapter
from biolink_bench.drivers.relational.mysql_adapter import MySQLAdapter
from biolink_bench.drivers.relational.postgresql_adapter import PostgreSQLAdapter

ADAPTER_CLASSES: dict[str, type[BaseEngineAdapter]] = {
    "mysql": MySQLAdapter,
    "postgresql": PostgreSQLAdapter,
    "mongodb": MongoDBAdapter,
    "couchdb": CouchDBAdapter,
    "neo4j": Neo4jAdapter,
    "memgraph": MemgraphAdapter,
}


def create_adapter(engine_config: EngineConfig) -> BaseEngineAdapter:
    cls = ADAPTER_CLASSES.get(engine_config.name)
    if cls is None:
        raise ValueError(f"No existe adaptador para el motor {engine_config.name!r}")
    return cls(engine_config)
