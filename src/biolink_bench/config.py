from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_LIMITS_MB: dict[str, int] = {
    "relational": 768,
    "document": 768,
    "graph": 1024,
}

ENGINE_MODELS: dict[str, str] = {
    "mysql": "relational",
    "postgresql": "relational",
    "mongodb": "document",
    "couchdb": "document",
    "neo4j": "graph",
    "memgraph": "graph",
}

MODEL_PAIRS: dict[str, tuple[str, str]] = {
    "relational": ("mysql", "postgresql"),
    "document": ("mongodb", "couchdb"),
    "graph": ("neo4j", "memgraph"),
}


def parse_mem_limit_mb(limit_str: str) -> int:
    match = re.fullmatch(r"\s*(\d+)\s*([kmgKMG])?\s*", limit_str)
    if not match:
        raise ValueError(f"Formato de límite de memoria inválido: {limit_str!r}")
    value = int(match.group(1))
    unit = (match.group(2) or "m").lower()
    if unit == "k":
        return max(1, value // 1024)
    if unit == "m":
        return value
    if unit == "g":
        return value * 1024
    raise ValueError(f"Unidad de memoria no soportada: {unit}")


@dataclass(frozen=True)
class EngineConfig:
    name: str
    model: str
    profile: str
    container_name: str
    image: str
    host: str
    port: int
    http_port: int | None
    database: str
    user: str
    password: str
    root_password: str
    mem_limit: str
    cpus: str
    volume_name: str


@dataclass(frozen=True)
class BenchmarkConfig:
    project_root: Path
    env_file: Path
    compose_file: Path
    datasets_dir: Path
    results_dir: Path
    reports_dir: Path
    bind_host: str
    project_name: str
    seed: int
    warmup_iterations: int
    measure_iterations: int
    timeout_seconds: int
    stats_interval_seconds: float
    max_total_mem_mb: int
    engines: dict[str, EngineConfig]


def load_config(env_file: Path | None = None) -> BenchmarkConfig:
    env_path = env_file or (PROJECT_ROOT / ".env")
    file_vals: dict[str, str] = {}
    if env_path.exists():
        raw_vals = dotenv_values(env_path)
        file_vals = {k: v for k, v in raw_vals.items() if v is not None}

    def get(key: str, default: str = "") -> str:
        if key in os.environ and os.environ[key] != "":
            return os.environ[key]
        return file_vals.get(key, default)

    bind_host = get("BENCH_BIND_HOST", "127.0.0.1")
    project_name = get("BENCH_PROJECT_NAME", "biolink-benchmarking")

    engines = {
        "mysql": EngineConfig(
            name="mysql",
            model="relational",
            profile="mysql",
            container_name="biolink-bench-mysql",
            image=get("MYSQL_IMAGE", "mysql:8.4.13"),
            host=bind_host,
            port=int(get("MYSQL_PORT", "3307")),
            http_port=None,
            database=get("MYSQL_DATABASE", "biolink_bench"),
            user=get("MYSQL_USER", "biolink_bench"),
            password=get("MYSQL_PASSWORD", ""),
            root_password=get("MYSQL_ROOT_PASSWORD", ""),
            mem_limit=get("MYSQL_MEM_LIMIT", "768m"),
            cpus=get("MYSQL_CPUS", "2.0"),
            volume_name=f"{project_name}_mysql_bench_data",
        ),
        "postgresql": EngineConfig(
            name="postgresql",
            model="relational",
            profile="postgresql",
            container_name="biolink-bench-postgresql",
            image=get("POSTGRES_IMAGE", "postgres:18.7"),
            host=bind_host,
            port=int(get("POSTGRES_PORT", "5433")),
            http_port=None,
            database=get("POSTGRES_DB", "biolink_bench"),
            user=get("POSTGRES_USER", "biolink_bench"),
            password=get("POSTGRES_PASSWORD", ""),
            root_password="",
            mem_limit=get("POSTGRES_MEM_LIMIT", "768m"),
            cpus=get("POSTGRES_CPUS", "2.0"),
            volume_name=f"{project_name}_postgresql_bench_data",
        ),
        "mongodb": EngineConfig(
            name="mongodb",
            model="document",
            profile="mongodb",
            container_name="biolink-bench-mongodb",
            image=get("MONGODB_IMAGE", "mongo:8.0.38"),
            host=bind_host,
            port=int(get("MONGODB_PORT", "27018")),
            http_port=None,
            database=get("MONGODB_DB", "biolink_bench"),
            user=get("MONGODB_USER", "biolink_bench"),
            password=get("MONGODB_PASSWORD", ""),
            root_password="",
            mem_limit=get("MONGODB_MEM_LIMIT", "768m"),
            cpus=get("MONGODB_CPUS", "2.0"),
            volume_name=f"{project_name}_mongodb_bench_data",
        ),
        "couchdb": EngineConfig(
            name="couchdb",
            model="document",
            profile="couchdb",
            container_name="biolink-bench-couchdb",
            image=get("COUCHDB_IMAGE", "couchdb:3.5.3"),
            host=bind_host,
            port=int(get("COUCHDB_PORT", "5985")),
            http_port=int(get("COUCHDB_PORT", "5985")),
            database=get("COUCHDB_DB_PREFIX", "biolink_bench"),
            user=get("COUCHDB_USER", "biolink_bench"),
            password=get("COUCHDB_PASSWORD", ""),
            root_password="",
            mem_limit=get("COUCHDB_MEM_LIMIT", "768m"),
            cpus=get("COUCHDB_CPUS", "2.0"),
            volume_name=f"{project_name}_couchdb_bench_data",
        ),
        "neo4j": EngineConfig(
            name="neo4j",
            model="graph",
            profile="neo4j",
            container_name="biolink-bench-neo4j",
            image=get("NEO4J_IMAGE", "neo4j:2026.10.2-community"),
            host=bind_host,
            port=int(get("NEO4J_BOLT_PORT", "7688")),
            http_port=int(get("NEO4J_HTTP_PORT", "7475")),
            database="neo4j",
            user=get("NEO4J_USER", "neo4j"),
            password=get("NEO4J_PASSWORD", ""),
            root_password="",
            mem_limit=get("NEO4J_MEM_LIMIT", "1024m"),
            cpus=get("NEO4J_CPUS", "2.0"),
            volume_name=f"{project_name}_neo4j_bench_data",
        ),
        "memgraph": EngineConfig(
            name="memgraph",
            model="graph",
            profile="memgraph",
            container_name="biolink-bench-memgraph",
            image=get("MEMGRAPH_IMAGE", "memgraph/memgraph:3.14.0"),
            host=bind_host,
            port=int(get("MEMGRAPH_BOLT_PORT", "7689")),
            http_port=None,
            database="memgraph",
            user=get("MEMGRAPH_USER", ""),
            password=get("MEMGRAPH_PASSWORD", ""),
            root_password="",
            mem_limit=get("MEMGRAPH_MEM_LIMIT", "1024m"),
            cpus=get("MEMGRAPH_CPUS", "2.0"),
            volume_name=f"{project_name}_memgraph_bench_data",
        ),
    }

    return BenchmarkConfig(
        project_root=PROJECT_ROOT,
        env_file=env_path,
        compose_file=PROJECT_ROOT / "docker" / "compose.yaml",
        datasets_dir=PROJECT_ROOT / "datasets",
        results_dir=PROJECT_ROOT / "results",
        reports_dir=PROJECT_ROOT / "reports",
        bind_host=bind_host,
        project_name=project_name,
        seed=int(get("BENCH_SEED", "20261120")),
        warmup_iterations=int(get("BENCH_WARMUP_ITERATIONS", "5")),
        measure_iterations=int(get("BENCH_MEASURE_ITERATIONS", "30")),
        timeout_seconds=int(get("BENCH_TIMEOUT_SECONDS", "60")),
        stats_interval_seconds=float(get("BENCH_STATS_INTERVAL_SECONDS", "0.5")),
        max_total_mem_mb=int(get("BENCH_MAX_TOTAL_MEM_MB", "4096")),
        engines=engines,
    )


def validate_config(
    cfg: BenchmarkConfig,
    *,
    require_env_file: bool = False,
    target_engines: list[str] | None = None,
) -> list[str]:
    """Valida reglas obligatorias de seguridad, versiones y presupuesto Docker."""
    errors: list[str] = []

    if not cfg.compose_file.exists():
        errors.append(f"No se encontró compose.yaml en {cfg.compose_file}")

    if require_env_file and not cfg.env_file.exists():
        errors.append(
            f"Falta archivo .env en {cfg.env_file}. Copie .env.example a .env y configure contraseñas locales."
        )

    if cfg.bind_host != "127.0.0.1":
        errors.append(
            f"BENCH_BIND_HOST debe ser 127.0.0.1 para evitar exposición externa (actual: {cfg.bind_host!r})"
        )

    if cfg.max_total_mem_mb > 4096:
        errors.append(
            f"BENCH_MAX_TOTAL_MEM_MB excede el techo experimental de 4096 MB (actual: {cfg.max_total_mem_mb})"
        )

    if cfg.seed < 0:
        errors.append("BENCH_SEED debe ser un entero no negativo")

    selected = target_engines or list(cfg.engines.keys())
    for name in selected:
        if name not in cfg.engines:
            errors.append(f"Motor desconocido: {name}")
            continue
        eng = cfg.engines[name]
        if ":" not in eng.image or eng.image.strip().endswith(":latest"):
            errors.append(f"Imagen inválida para {name}: {eng.image!r} (prohibido usar :latest o sin tag)")

        try:
            mem_mb = parse_mem_limit_mb(eng.mem_limit)
            max_allowed = MODEL_LIMITS_MB[eng.model]
            if mem_mb > max_allowed:
                errors.append(
                    f"Límite de memoria de {name} ({mem_mb} MB) excede el límite acordado de {max_allowed} MB"
                )
        except ValueError as exc:
            errors.append(str(exc))

        if require_env_file and name != "memgraph":
            if not eng.password or eng.password.startswith("CHANGE_ME_"):
                errors.append(
                    f"La contraseña de {name} en .env está vacía o conserva el placeholder CHANGE_ME_*"
                )
            if name == "mysql" and (not eng.root_password or eng.root_password.startswith("CHANGE_ME_")):
                errors.append("MYSQL_ROOT_PASSWORD en .env está vacío o conserva el placeholder CHANGE_ME_*")
            if name == "neo4j" and eng.password and len(eng.password) < 8:
                errors.append("NEO4J_PASSWORD debe tener al menos 8 caracteres para Neo4j Community")

    return errors
