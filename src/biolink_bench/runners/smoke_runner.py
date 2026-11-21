from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from biolink_bench.config import BenchmarkConfig, validate_config
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


def run_smoke_for_engine(
    cfg: BenchmarkConfig,
    engine_name: str,
    *,
    manage_docker: bool = False,
    remove_volumes: bool = False,
) -> tuple[RunMetricsBundle, dict[str, Path]]:
    """Ejecuta validación de conexión directa, CRUD de humo, verificación y limpieza."""
    errors = validate_config(cfg, require_env_file=True, target_engines=[engine_name])
    if errors:
        raise ValueError("Configuración inválida:\n- " + "\n- ".join(errors))

    run_id = make_run_id("smoke", engine_name)
    eng = cfg.engines[engine_name]
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_lines = [f"[{started_at}] Iniciando smoke test para {engine_name} ({eng.image})"]

    metrics = RunMetricsBundle(
        run_id=run_id,
        mode="smoke",
        engine=engine_name,
        model=eng.model,
        dataset_id="smoke_test",
        seed=None,
        started_at_utc=started_at,
        host_info=capture_host_info(),
    )

    if manage_docker:
        log_lines.append(f"Levantando perfil Compose '{eng.profile}'...")
        compose_up_engine(cfg, engine_name)
    else:
        ensure_exclusive_engine(cfg, engine_name)

    metrics.docker_info = inspect_container(eng.container_name)
    monitor = DockerResourceMonitor(eng.container_name, interval_seconds=cfg.stats_interval_seconds)
    adapter = create_adapter(eng)

    try:
        monitor.start()
        t0 = time.perf_counter_ns()
        adapter.connect()
        metrics.connection_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        log_lines.append(f"Conexión directa establecida en {metrics.connection_ms:.3f} ms")

        health_ok, health_msg = adapter.health_check()
        metrics.engine_info = adapter.get_engine_info()
        log_lines.append(f"Health check: ok={health_ok} ({health_msg})")

        t1 = time.perf_counter_ns()
        smoke = adapter.run_smoke_crud()
        smoke_ms = (time.perf_counter_ns() - t1) / 1_000_000.0
        valid = bool(smoke.connected and smoke.health_ok and smoke.query_ok and smoke.cleanup_ok)
        metrics.measurements.append(
            OperationMeasurement(
                run_id=run_id,
                engine=engine_name,
                model=eng.model,
                operation="SMOKE_CRUD",
                iteration=1,
                is_warmup=False,
                latency_ms=smoke_ms,
                ok=valid,
                valid=valid,
                rows_returned=smoke.details.get("matched_rows", 0),
                error="" if valid else f"Smoke falló: {smoke}",
            )
        )
        if not valid:
            metrics.errors.append(f"Validación de humo fallida: {smoke}")
        metrics.storage_bytes = adapter.get_storage_bytes()
        log_lines.append(
            f"Smoke CRUD completado en {smoke_ms:.3f} ms | query_ok={smoke.query_ok} | cleanup_ok={smoke.cleanup_ok}"
        )
    except Exception as exc:
        metrics.errors.append(f"{type(exc).__name__}: {exc}")
        log_lines.append(f"ERROR en smoke test: {type(exc).__name__}: {exc}")
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
                log_lines.append(f"Contenedor {eng.container_name} detenido (remove_volumes={remove_volumes})")
            except Exception as exc:
                metrics.errors.append(f"Error al detener contenedor: {exc}")

    artifacts = export_run_artifacts(metrics, cfg.results_dir, cfg.reports_dir, log_lines)
    return metrics, artifacts
