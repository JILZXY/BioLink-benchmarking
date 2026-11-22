from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OperationMeasurement:
    run_id: str
    engine: str
    model: str
    operation: str
    iteration: int
    is_warmup: bool
    latency_ms: float
    ok: bool
    valid: bool
    timed_out: bool = False
    rows_returned: int = 0
    error: str = ""


def percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = (len(sorted_vals) - 1) * (pct / 100.0)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_vals[low]
    frac = rank - low
    return sorted_vals[low] * (1.0 - frac) + sorted_vals[high] * frac


def summarize_operation(records: list[OperationMeasurement]) -> dict[str, Any]:
    measured = [r for r in records if not r.is_warmup]
    ok_latencies = sorted(r.latency_ms for r in measured if r.ok)
    total = len(measured)
    ok_count = sum(1 for r in measured if r.ok)
    valid_count = sum(1 for r in measured if r.ok and r.valid)
    error_count = sum(1 for r in measured if not r.ok and not r.timed_out)
    timeout_count = sum(1 for r in measured if r.timed_out)

    total_time_sec = sum(ok_latencies) / 1000.0
    ops_per_sec = (ok_count / total_time_sec) if total_time_sec > 0 else 0.0

    return {
        "count": total,
        "warmup_count": sum(1 for r in records if r.is_warmup),
        "ok_count": ok_count,
        "valid_count": valid_count,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "correctness_rate_pct": round((valid_count / total) * 100.0, 2) if total else 0.0,
        "p50_ms": round(percentile(ok_latencies, 50.0), 4),
        "p95_ms": round(percentile(ok_latencies, 95.0), 4),
        "max_ms": round(max(ok_latencies), 4) if ok_latencies else 0.0,
        "min_ms": round(min(ok_latencies), 4) if ok_latencies else 0.0,
        "mean_ms": round(sum(ok_latencies) / len(ok_latencies), 4) if ok_latencies else 0.0,
        "ops_per_sec": round(ops_per_sec, 2),
    }


@dataclass
class RunMetricsBundle:
    run_id: str
    mode: str
    engine: str
    model: str
    dataset_id: str
    seed: int | None
    started_at_utc: str
    finished_at_utc: str = ""
    connection_ms: float = 0.0
    schema_ms: float = 0.0
    load_ms: float = 0.0
    index_ms: float = 0.0
    cleanup_ms: float = 0.0
    storage_bytes: int | None = None
    engine_info: dict[str, Any] = field(default_factory=dict)
    docker_info: dict[str, Any] = field(default_factory=dict)
    docker_resources: dict[str, Any] = field(default_factory=dict)
    host_info: dict[str, Any] = field(default_factory=dict)
    measurements: list[OperationMeasurement] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def operation_summaries(self) -> dict[str, dict[str, Any]]:
        grouped: dict[str, list[OperationMeasurement]] = {}
        for m in self.measurements:
            grouped.setdefault(m.operation, []).append(m)
        return {op: summarize_operation(items) for op, items in grouped.items()}
