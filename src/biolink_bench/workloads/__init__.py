from biolink_bench.workloads.base import WorkloadCase, WorkloadDefinition
from biolink_bench.workloads.document import DOCUMENT_WORKLOADS
from biolink_bench.workloads.graph import GRAPH_WORKLOADS
from biolink_bench.workloads.relational import RELATIONAL_WORKLOADS

WORKLOADS_BY_MODEL: dict[str, list[WorkloadDefinition]] = {
    "relational": RELATIONAL_WORKLOADS,
    "document": DOCUMENT_WORKLOADS,
    "graph": GRAPH_WORKLOADS,
}

__all__ = [
    "DOCUMENT_WORKLOADS",
    "GRAPH_WORKLOADS",
    "RELATIONAL_WORKLOADS",
    "WORKLOADS_BY_MODEL",
    "WorkloadCase",
    "WorkloadDefinition",
]
