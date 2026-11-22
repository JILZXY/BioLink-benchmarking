from __future__ import annotations

import pytest

from biolink_bench.config import ENGINE_MODELS, load_config
from biolink_bench.runners.smoke_runner import run_smoke_for_engine


@pytest.mark.live
@pytest.mark.parametrize("engine", list(ENGINE_MODELS.keys()))
def test_live_engine_connectivity_and_smoke(engine: str, target_engine: str) -> None:
    if target_engine != "all" and target_engine != engine:
        pytest.skip(f"Omitido porque --engine={target_engine}")

    cfg = load_config()
    metrics, _ = run_smoke_for_engine(cfg, engine, manage_docker=False)
    assert not metrics.errors, f"Errores en smoke de {engine}: {metrics.errors}"
    summary = metrics.operation_summaries()["SMOKE_CRUD"]
    assert summary["correctness_rate_pct"] == 100.0
