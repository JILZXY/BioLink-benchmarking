from __future__ import annotations

import csv
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biolink_bench.metrics.collector import RunMetricsBundle


def make_run_id(mode: str, engine: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = secrets.token_hex(3)
    return f"{ts}_{mode}_{engine}_{suffix}"


def export_run_artifacts(
    bundle: RunMetricsBundle,
    results_dir: Path,
    reports_dir: Path,
    log_lines: list[str],
) -> dict[str, Path]:
    """Exporta CSV individual, JSON de metadatos, log y resumen Markdown sin sobrescribir."""
    raw_dir = results_dir / "raw"
    summaries_dir = results_dir / "summaries"
    logs_dir = results_dir / "logs"
    for d in (raw_dir, summaries_dir, logs_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)

    csv_path = raw_dir / f"{bundle.run_id}.csv"
    json_path = summaries_dir / f"{bundle.run_id}.json"
    log_path = logs_dir / f"{bundle.run_id}.log"
    report_path = reports_dir / f"{bundle.run_id}_summary.md"

    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "run_id",
                "engine",
                "model",
                "operation",
                "iteration",
                "is_warmup",
                "latency_ms",
                "ok",
                "valid",
                "timed_out",
                "rows_returned",
                "error",
            ]
        )
        for m in bundle.measurements:
            writer.writerow(
                [
                    m.run_id,
                    m.engine,
                    m.model,
                    m.operation,
                    m.iteration,
                    m.is_warmup,
                    f"{m.latency_ms:.4f}",
                    m.ok,
                    m.valid,
                    m.timed_out,
                    m.rows_returned,
                    m.error,
                ]
            )

    summaries = bundle.operation_summaries()
    summary_payload: dict[str, Any] = {
        "run_id": bundle.run_id,
        "mode": bundle.mode,
        "engine": bundle.engine,
        "model": bundle.model,
        "dataset_id": bundle.dataset_id,
        "seed": bundle.seed,
        "started_at_utc": bundle.started_at_utc,
        "finished_at_utc": bundle.finished_at_utc,
        "timings_ms": {
            "connection_ms": round(bundle.connection_ms, 4),
            "schema_ms": round(bundle.schema_ms, 4),
            "load_ms": round(bundle.load_ms, 4),
            "index_ms": round(bundle.index_ms, 4),
            "cleanup_ms": round(bundle.cleanup_ms, 4),
        },
        "storage_bytes": bundle.storage_bytes,
        "engine_info": bundle.engine_info,
        "docker_info": bundle.docker_info,
        "docker_resources": bundle.docker_resources,
        "host_info": bundle.host_info,
        "operations": summaries,
        "errors": bundle.errors,
        "artifacts": {
            "raw_csv": str(csv_path.relative_to(results_dir.parent)),
            "summary_json": str(json_path.relative_to(results_dir.parent)),
            "log_file": str(log_path.relative_to(results_dir.parent)),
        },
    }
    json_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    md_lines = [
        f"# Resumen de ejecución: `{bundle.run_id}`",
        "",
        f"- **Modo:** `{bundle.mode}`",
        f"- **Motor:** `{bundle.engine}` ({bundle.model})",
        f"- **Dataset:** `{bundle.dataset_id}` (semilla: `{bundle.seed}`)",
        f"- **Inicio UTC:** `{bundle.started_at_utc}`",
        f"- **Fin UTC:** `{bundle.finished_at_utc}`",
        f"- **Conexión (ms):** `{bundle.connection_ms:.3f}` | **Esquema (ms):** `{bundle.schema_ms:.3f}` | **Carga (ms):** `{bundle.load_ms:.3f}` | **Índices (ms):** `{bundle.index_ms:.3f}`",
        f"- **Almacenamiento reportado (bytes):** `{bundle.storage_bytes}`",
        f"- **Pico memoria Docker (MiB):** `{bundle.docker_resources.get('peak_memory_mib')}` | **OOMKilled:** `{bundle.docker_resources.get('oom_killed')}`",
        "",
        "## Métricas por operación",
        "",
        "| Operación | Mediciones | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for op, stats in summaries.items():
        md_lines.append(
            f"| `{op}` | {stats['count']} | {stats['p50_ms']:.3f} | {stats['p95_ms']:.3f} | {stats['max_ms']:.3f} | {stats['ops_per_sec']:.2f} | {stats['correctness_rate_pct']:.2f}% | {stats['error_count'] + stats['timeout_count']} |"
        )
    if bundle.errors:
        md_lines.extend(["", "## Errores registrados", ""] + [f"- {e}" for e in bundle.errors])
    report_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    return {
        "csv": csv_path,
        "json": json_path,
        "log": log_path,
        "report": report_path,
    }
