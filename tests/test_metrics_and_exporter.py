from __future__ import annotations

import csv
import json
from pathlib import Path

from biolink_bench.metrics.collector import OperationMeasurement, RunMetricsBundle, summarize_operation
from biolink_bench.metrics.exporter import export_run_artifacts


def test_metrics_summary_and_correctness() -> None:
    records = [
        OperationMeasurement("r1", "mysql", "relational", "R1", 1, True, 99.0, True, True),
        OperationMeasurement("r1", "mysql", "relational", "R1", 1, False, 10.0, True, True),
        OperationMeasurement("r1", "mysql", "relational", "R1", 2, False, 20.0, True, True),
        OperationMeasurement("r1", "mysql", "relational", "R1", 3, False, 30.0, True, False, error="mismatch"),
        OperationMeasurement("r1", "mysql", "relational", "R1", 4, False, 40.0, True, True),
    ]
    summary = summarize_operation(records)
    assert summary["count"] == 4
    assert summary["warmup_count"] == 1
    assert summary["p50_ms"] == 25.0
    assert summary["max_ms"] == 40.0
    assert summary["correctness_rate_pct"] == 75.0


def test_exporter_writes_csv_json_log_and_report(tmp_path: Path) -> None:
    results_dir = tmp_path / "results"
    reports_dir = tmp_path / "reports"
    bundle = RunMetricsBundle(
        run_id="20261120T000000Z_smoke_mysql_abc123",
        mode="smoke",
        engine="mysql",
        model="relational",
        dataset_id="smoke_test",
        seed=None,
        started_at_utc="2026-11-20T00:00:00Z",
        finished_at_utc="2026-11-20T00:00:01Z",
        connection_ms=5.12,
        measurements=[
            OperationMeasurement(
                "20261120T000000Z_smoke_mysql_abc123",
                "mysql",
                "relational",
                "SMOKE_CRUD",
                1,
                False,
                3.45,
                True,
                True,
                rows_returned=1,
            )
        ],
    )
    artifacts = export_run_artifacts(bundle, results_dir, reports_dir, ["line 1"])
    assert artifacts["csv"].exists()
    assert artifacts["json"].exists()
    assert artifacts["log"].exists()
    assert artifacts["report"].exists()

    with artifacts["csv"].open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["operation"] == "SMOKE_CRUD"

    data = json.loads(artifacts["json"].read_text(encoding="utf-8"))
    assert data["timings_ms"]["connection_ms"] == 5.12
    assert data["operations"]["SMOKE_CRUD"]["correctness_rate_pct"] == 100.0
