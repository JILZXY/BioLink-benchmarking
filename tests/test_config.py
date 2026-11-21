from __future__ import annotations

from dataclasses import replace

from biolink_bench.config import PROJECT_ROOT, load_config, validate_config


def test_default_config_rules() -> None:
    cfg = load_config(PROJECT_ROOT / ".env.example")
    errors = validate_config(cfg, require_env_file=False)
    assert errors == [], f"Errores inesperados: {errors}"
    assert cfg.bind_host == "127.0.0.1"
    assert cfg.max_total_mem_mb <= 4096
    assert set(cfg.engines.keys()) == {
        "mysql",
        "postgresql",
        "mongodb",
        "couchdb",
        "neo4j",
        "memgraph",
    }


def test_rejects_latest_tag() -> None:
    cfg = load_config(PROJECT_ROOT / ".env.example")
    bad_mysql = replace(cfg.engines["mysql"], image="mysql:latest")
    bad_cfg = replace(cfg, engines={**cfg.engines, "mysql": bad_mysql})
    errors = validate_config(bad_cfg, require_env_file=False)
    assert any("latest" in e for e in errors)


def test_rejects_non_loopback_bind() -> None:
    cfg = load_config(PROJECT_ROOT / ".env.example")
    bad_cfg = replace(cfg, bind_host="0.0.0.0")
    errors = validate_config(bad_cfg, require_env_file=False)
    assert any("127.0.0.1" in e for e in errors)


def test_rejects_excessive_memory_limit() -> None:
    cfg = load_config(PROJECT_ROOT / ".env.example")
    bad_pg = replace(cfg.engines["postgresql"], mem_limit="1024m")
    bad_cfg = replace(cfg, engines={**cfg.engines, "postgresql": bad_pg})
    errors = validate_config(bad_cfg, require_env_file=False)
    assert any("768" in e for e in errors)
