from __future__ import annotations

import json
import re
import subprocess
import threading
import time
from typing import Any


def parse_memory_to_mib(raw: str) -> float:
    """Convierte cadenas de `docker stats` como '142.5MiB / 768MiB' o '1.02GiB' a MiB."""
    head = raw.split("/")[0].strip()
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]+)", head)
    if not match:
        return 0.0
    val = float(match.group(1))
    unit = match.group(2).lower()
    factors = {
        "b": 1.0 / (1024 * 1024),
        "kb": 1000.0 / (1024 * 1024),
        "kib": 1.0 / 1024.0,
        "mb": (1000.0**2) / (1024.0**2),
        "mib": 1.0,
        "gb": (1000.0**3) / (1024.0**2),
        "gib": 1024.0,
    }
    return round(val * factors.get(unit, 1.0), 2)


def inspect_container(container_name: str) -> dict[str, Any]:
    """Obtiene metadatos exactos de imagen, digest, límites y salud del contenedor."""
    try:
        proc = subprocess.run(
            ["docker", "inspect", container_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return {"available": False, "error": proc.stderr.strip() or "Contenedor no encontrado"}
        payload = json.loads(proc.stdout)[0]
        img_id = payload.get("Image", "")
        img_name = payload.get("Config", {}).get("Image", "")

        repo_digests: list[str] = []
        if img_id:
            iproc = subprocess.run(
                ["docker", "image", "inspect", img_id, "--format", "{{json .RepoDigests}}"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if iproc.returncode == 0 and iproc.stdout.strip():
                try:
                    repo_digests = json.loads(iproc.stdout.strip()) or []
                except json.JSONDecodeError:
                    repo_digests = []

        state = payload.get("State", {})
        health = state.get("Health", {})
        host_cfg = payload.get("HostConfig", {})
        mem_bytes = int(host_cfg.get("Memory", 0))
        return {
            "available": True,
            "container_name": container_name,
            "image": img_name,
            "image_id": img_id,
            "repo_digests": repo_digests,
            "status": state.get("Status"),
            "health_status": health.get("Status"),
            "oom_killed": bool(state.get("OOMKilled", False)),
            "mem_limit_bytes": mem_bytes,
            "mem_limit_mb": round(mem_bytes / (1024 * 1024), 2) if mem_bytes else None,
            "nano_cpus": host_cfg.get("NanoCpus"),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


class DockerResourceMonitor:
    """Muestreador en segundo plano de memoria y CPU mediante `docker stats`."""

    def __init__(self, container_name: str, interval_seconds: float = 0.5) -> None:
        self.container_name = container_name
        self.interval_seconds = max(0.2, interval_seconds)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.mem_samples_mib: list[float] = []
        self.cpu_samples_pct: list[float] = []
        self.errors: list[str] = []

    def _sample_once(self) -> None:
        proc = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{.MemUsage}}|{{.CPUPerc}}",
                self.container_name,
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode != 0:
            return
        line = proc.stdout.strip()
        if "|" not in line:
            return
        mem_raw, cpu_raw = line.split("|", 1)
        self.mem_samples_mib.append(parse_memory_to_mib(mem_raw))
        try:
            self.cpu_samples_pct.append(float(cpu_raw.strip().rstrip("%")))
        except ValueError:
            pass

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._sample_once()
            except Exception as exc:
                self.errors.append(str(exc))
            self._stop_event.wait(self.interval_seconds)

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        try:
            self._sample_once()
        except Exception:
            pass
        post_inspect = inspect_container(self.container_name)
        return {
            "samples_count": len(self.mem_samples_mib),
            "peak_memory_mib": max(self.mem_samples_mib) if self.mem_samples_mib else None,
            "avg_memory_mib": round(sum(self.mem_samples_mib) / len(self.mem_samples_mib), 2)
            if self.mem_samples_mib
            else None,
            "peak_cpu_pct": max(self.cpu_samples_pct) if self.cpu_samples_pct else None,
            "avg_cpu_pct": round(sum(self.cpu_samples_pct) / len(self.cpu_samples_pct), 2)
            if self.cpu_samples_pct
            else None,
            "oom_killed": post_inspect.get("oom_killed", False),
        }
