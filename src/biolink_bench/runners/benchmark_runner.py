from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biolink_bench.config import MODEL_PAIRS, BenchmarkConfig, validate_config
from biolink_bench.datasets.bundle import DatasetBundle
from biolink_bench.datasets.synthetic_generator import build_synthetic_bundle
from biolink_bench.drivers.factory import create_adapter
from biolink_bench.metrics.collector import OperationMeasurement, RunMetricsBundle
from biolink_bench.metrics.docker_monitor import DockerResourceMonitor, inspect_container
from biolink_bench.metrics.exporter import export_run_artifacts, make_run_id
from biolink_bench.runners.lifecycle import (
    capture_host_info,
    compose_down_engine,
    compose_up_engine,
    ensure_exclusive_engine,
)
from biolink_bench.workloads import WORKLOADS_BY_MODEL

CAMPAIGN_BLOCK_LIMITS_SECONDS = {
    "relational": 15 * 60,
    "document": 12 * 60,
    "graph": 17 * 60,
}


def _count_rows(result: Any) -> int:
    if isinstance(result, list):
        return len(result)
    if isinstance(result, dict):
        if "inserted_records" in result:
            return int(result["inserted_records"])
        if "inserted_count" in result:
            return int(result["inserted_count"])
        return 1
    return 0


def run_engine_benchmark(
    cfg: BenchmarkConfig,
    engine_name: str,
    bundle: DatasetBundle,
    *,
    warmup: int | None = None,
    iterations: int | None = None,
    timeout_seconds: int | None = None,
    manage_docker: bool = False,
    remove_volumes: bool = False,
    cleanup_after: bool = True,
) -> tuple[RunMetricsBundle, dict[str, Path]]:
    """Ejecuta carga, creación de índices, calentamiento, workloads medidos y exportación."""
    errors = validate_config(cfg, require_env_file=True, target_engines=[engine_name])
    if errors:
        raise ValueError("Configuración inválida:\n- " + "\n- ".join(errors))

    warmup_n = cfg.warmup_iterations if warmup is None else warmup
    measure_n = cfg.measure_iterations if iterations is None else iterations
    op_timeout = cfg.timeout_seconds if timeout_seconds is None else timeout_seconds

    eng = cfg.engines[engine_name]
    run_id = make_run_id("bench", engine_name)
    run_prefix = run_id.rsplit("_", 1)[-1]
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_lines = [
        f"[{started_at}] Iniciando benchmark para {engine_name} | dataset={bundle.dataset_id} | warmup={warmup_n} | iters={measure_n}"
    ]

    metrics = RunMetricsBundle(
        run_id=run_id,
        mode="benchmark",
        engine=engine_name,
        model=eng.model,
        dataset_id=bundle.dataset_id,
        seed=bundle.seed,
        started_at_utc=started_at,
        host_info=capture_host_info(),
    )

    if manage_docker:
        compose_up_engine(cfg, engine_name)
    else:
        ensure_exclusive_engine(cfg, engine_name)

    metrics.docker_info = inspect_container(eng.container_name)
    monitor = DockerResourceMonitor(eng.container_name, interval_seconds=cfg.stats_interval_seconds)
    adapter = create_adapter(eng)

    try:
        monitor.start()

        # 1. Conexión directa separada del cronómetro de consultas
        t0 = time.perf_counter_ns()
        adapter.connect()
        metrics.connection_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        metrics.engine_info = adapter.get_engine_info()
        log_lines.append(f"Conexión: {metrics.connection_ms:.3f} ms | versión: {metrics.engine_info.get('server_version')}")

        # 2. Preparación de estructura
        t1 = time.perf_counter_ns()
        adapter.prepare_schema()
        metrics.schema_ms = (time.perf_counter_ns() - t1) / 1_000_000.0

        # 3. Carga inicial separada
        t2 = time.perf_counter_ns()
        loaded = adapter.load_dataset(bundle)
        metrics.load_ms = (time.perf_counter_ns() - t2) / 1_000_000.0
        log_lines.append(f"Carga inicial: {metrics.load_ms:.3f} ms | conteos: {loaded}")

        # 4. Creación de índices separada
        t3 = time.perf_counter_ns()
        adapter.create_indexes()
        metrics.index_ms = (time.perf_counter_ns() - t3) / 1_000_000.0
        log_lines.append(f"Índices creados en: {metrics.index_ms:.3f} ms")

        # 5. Ejecución separada de cada workload (lecturas antes que escrituras)
        workloads = WORKLOADS_BY_MODEL[eng.model]
        total_cases_per_op = warmup_n + measure_n
        for wl in workloads:
            cases = wl.build_cases(bundle, total_cases_per_op, run_prefix)
            for idx, case in enumerate(cases):
                is_warmup = idx < warmup_n
                iter_num = (idx + 1) if is_warmup else (idx - warmup_n + 1)
                t_start = time.perf_counter_ns()
                ok = False
                valid = False
                timed_out = False
                rows_returned = 0
                err_msg = ""
                try:
                    res = adapter.execute_operation(case.op_name, case.params)
                    elapsed_ms = (time.perf_counter_ns() - t_start) / 1_000_000.0
                    if elapsed_ms > op_timeout * 1000.0:
                        timed_out = True
                        err_msg = f"Excedió timeout de {op_timeout}s ({elapsed_ms:.1f} ms)"
                    else:
                        ok = True
                        rows_returned = _count_rows(res)
                        valid, val_msg = case.validator(res)
                        if not valid:
                            err_msg = f"Validación fallida: {val_msg}"
                except Exception as exc:
                    elapsed_ms = (time.perf_counter_ns() - t_start) / 1_000_000.0
                    err_msg = f"{type(exc).__name__}: {exc}"

                metrics.measurements.append(
                    OperationMeasurement(
                        run_id=run_id,
                        engine=engine_name,
                        model=eng.model,
                        operation=wl.op_name,
                        iteration=iter_num,
                        is_warmup=is_warmup,
                        latency_ms=elapsed_ms,
                        ok=ok,
                        valid=valid,
                        timed_out=timed_out,
                        rows_returned=rows_returned,
                        error=err_msg,
                    )
                )
            op_summary = metrics.operation_summaries()[wl.op_name]
            log_lines.append(
                f"Workload {wl.op_name}: p50={op_summary['p50_ms']} ms, p95={op_summary['p95_ms']} ms, "
                f"correctness={op_summary['correctness_rate_pct']}%"
            )

        metrics.storage_bytes = adapter.get_storage_bytes()

        if cleanup_after:
            tc = time.perf_counter_ns()
            adapter.cleanup_test_data(bundle.dataset_tag)
            metrics.cleanup_ms = (time.perf_counter_ns() - tc) / 1_000_000.0

    except Exception as exc:
        metrics.errors.append(f"{type(exc).__name__}: {exc}")
        log_lines.append(f"ERROR fatal durante benchmark: {type(exc).__name__}: {exc}")
    finally:
        try:
            adapter.disconnect()
        except Exception:
            pass
        metrics.docker_resources = monitor.stop()
        metrics.finished_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if manage_docker:
            try:
                compose_down_engine(cfg, engine_name, remove_volumes=remove_volumes)
            except Exception as exc:
                metrics.errors.append(f"Error al detener contenedor: {exc}")

    artifacts = export_run_artifacts(metrics, cfg.results_dir, cfg.reports_dir, log_lines)
    return metrics, artifacts


def run_pair_comparison(
    cfg: BenchmarkConfig,
    model: str,
    bundle: DatasetBundle,
    *,
    warmup: int | None = None,
    iterations: int | None = None,
) -> tuple[list[RunMetricsBundle], Path]:
    """Ejecuta secuencialmente la pareja de motores de un mismo paradigma y genera reporte comparativo."""
    if model not in MODEL_PAIRS:
        raise ValueError(f"Modelo inválido: {model}. Opciones: {list(MODEL_PAIRS.keys())}")
    pair = MODEL_PAIRS[model]
    results: list[RunMetricsBundle] = []

    for engine_name in pair:
        metrics, _ = run_engine_benchmark(
            cfg,
            engine_name,
            bundle,
            warmup=warmup,
            iterations=iterations,
            manage_docker=True,
            remove_volumes=True,
            cleanup_after=True,
        )
        results.append(metrics)

    cmp_id = make_run_id("compare", model)
    report_path = cfg.reports_dir / f"{cmp_id}.md"
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Comparativa secuencial — Modelo {model} (`{cmp_id}`)",
        "",
        f"- **Dataset:** `{bundle.dataset_id}` (semilla `{bundle.seed}`)",
        f"- **Candidatos:** `{pair[0]}` vs. `{pair[1]}`",
        "",
        "| Motor | Versión | Conexión (ms) | Carga (ms) | Índices (ms) | Pico RAM (MiB) | OOMKilled | Almacenamiento (bytes) |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for r in results:
        lines.append(
            f"| `{r.engine}` | `{r.engine_info.get('server_version', 'N/A')}` | {r.connection_ms:.2f} | "
            f"{r.load_ms:.2f} | {r.index_ms:.2f} | {r.docker_resources.get('peak_memory_mib')} | "
            f"{r.docker_resources.get('oom_killed')} | {r.storage_bytes} |"
        )
    lines.extend(["", "## Detalle por operación", ""])
    lines.append("| Motor | Operación | p50 (ms) | p95 (ms) | Máx (ms) | ops/s | Corrección (%) | Errores |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in results:
        for op, st in r.operation_summaries().items():
            lines.append(
                f"| `{r.engine}` | `{op}` | {st['p50_ms']:.3f} | {st['p95_ms']:.3f} | {st['max_ms']:.3f} | "
                f"{st['ops_per_sec']:.2f} | {st['correctness_rate_pct']:.2f}% | {st['error_count'] + st['timeout_count']} |"
            )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results, report_path


def run_full_campaign(
    cfg: BenchmarkConfig,
    volume: int = 10000,
    seed: int | None = None,
    *,
    warmup: int | None = None,
    iterations: int | None = None,
) -> Path:
    """Ejecuta la campaña secuencial completa (máximo 120 min) sobre los 3 modelos."""
    used_seed = cfg.seed if seed is None else seed
    bundle = build_synthetic_bundle(target_assertions=volume, seed=used_seed)
    campaign_start = time.monotonic()
    max_campaign_seconds = 120 * 60

    all_reports: list[Path] = []
    for model in ("relational", "document", "graph"):
        elapsed = time.monotonic() - campaign_start
        if elapsed >= max_campaign_seconds:
            break
        _, rep = run_pair_comparison(cfg, model, bundle, warmup=warmup, iterations=iterations)
        all_reports.append(rep)

    campaign_id = make_run_id("campaign", f"{volume}")
    summary_path = cfg.reports_dir / f"{campaign_id}.md"
    lines = [
        f"# Campaña completa BioLink (`{campaign_id}`)",
        "",
        f"- **Volumen objetivo:** `{volume}` afirmaciones | **Semilla:** `{used_seed}`",
        f"- **Duración total:** `{(time.monotonic() - campaign_start):.1f} s` (límite: 7200 s)",
        "",
        "## Reportes por categoría",
        "",
    ] + [f"- `{p.name}`" for p in all_reports]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary_path
