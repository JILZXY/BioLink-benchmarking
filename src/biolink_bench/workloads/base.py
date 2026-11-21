from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from biolink_bench.datasets.bundle import DatasetBundle


@dataclass(frozen=True)
class WorkloadCase:
    op_name: str
    params: dict[str, Any]
    validator: Callable[[Any], tuple[bool, str]]


@dataclass(frozen=True)
class WorkloadDefinition:
    op_name: str
    model: str
    biolink_ops: tuple[str, ...]
    description: str
    is_write: bool
    build_cases: Callable[[DatasetBundle, int, str], list[WorkloadCase]]
