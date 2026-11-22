from __future__ import annotations

import platform
import subprocess
import sys
from typing import Any

from biolink_bench.config import BenchmarkConfig


def capture_host_info() -> dict[str, Any]:
    docker_ver = "unknown"
    try:
        proc = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode == 0:
            docker_ver = proc.stdout.strip()
    except Exception:
        pass

    return {
        "os": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "docker": docker_ver,
    }


def list_running_bench_containers() -> list[tuple[str, str]]:
    try:
        proc = subprocess.run(
            ["docker", "ps", "--filter", "name=biolink-bench-", "--format", "{{.Names}}|{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode != 0:
            return []
        items: list[tuple[str, str]] = []
        for line in proc.stdout.splitlines():
            if "|" in line:
                name, status = line.split("|", 1)
                items.append((name.strip(), status.strip()))
        return items
    except Exception:
        return []


def ensure_exclusive_engine(cfg: BenchmarkConfig, engine_name: str) -> None:
    expected = cfg.engines[engine_name].container_name
    running = list_running_bench_containers()
    others = [name for name, _ in running if name != expected]
    if others:
        raise RuntimeError(
            "Regla de ejecución secuencial violada: hay otros motores activos "
            f"({', '.join(others)}). Deténgalos antes de probar {engine_name}."
        )


def compose_up_engine(cfg: BenchmarkConfig, engine_name: str) -> None:
    ensure_exclusive_engine(cfg, engine_name)
    profile = cfg.engines[engine_name].profile
    cmd = [
        "docker",
        "compose",
        "--env-file",
        str(cfg.env_file),
        "-f",
        str(cfg.compose_file),
        "--profile",
        profile,
        "up",
        "-d",
        "--wait",
    ]
    proc = subprocess.run(cmd, cwd=str(cfg.project_root), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Fallo al levantar {engine_name}: {proc.stderr.strip() or proc.stdout.strip()}"
        )


def compose_down_engine(cfg: BenchmarkConfig, engine_name: str, *, remove_volumes: bool = False) -> None:
    profile = cfg.engines[engine_name].profile
    cmd = [
        "docker",
        "compose",
        "--env-file",
        str(cfg.env_file),
        "-f",
        str(cfg.compose_file),
        "--profile",
        profile,
        "down",
    ]
    if remove_volumes:
        cmd.append("-v")
    proc = subprocess.run(cmd, cwd=str(cfg.project_root), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Fallo al detener {engine_name}: {proc.stderr.strip() or proc.stdout.strip()}"
        )
