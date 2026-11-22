from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from biolink_bench.config import ENGINE_MODELS, MODEL_PAIRS, load_config, validate_config
from biolink_bench.datasets.scientific_fixture import load_scientific_fixture
from biolink_bench.datasets.synthetic_generator import build_synthetic_bundle, export_synthetic_dataset
from biolink_bench.drivers.factory import create_adapter
from biolink_bench.runners.benchmark_runner import run_engine_benchmark, run_full_campaign, run_pair_comparison
from biolink_bench.runners.lifecycle import compose_down_engine, compose_up_engine
from biolink_bench.runners.smoke_runner import run_smoke_for_engine


def _load_bundle_for_args(args: argparse.Namespace, cfg) -> object:
    if args.dataset == "fixture":
        bundle, _ = load_scientific_fixture(cfg.datasets_dir / "scientific_fixture")
        return bundle
    seed = cfg.seed if args.seed is None else args.seed
    return build_synthetic_bundle(target_assertions=args.volume, seed=seed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="biolink-bench",
        description="CLI independiente de benchmarking directo para los 6 motores candidatos de BioLink.",
    )
    parser.add_argument("--env-file", type=Path, default=None, help="Ruta opcional al archivo .env")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check-config", help="Valida reglas de configuración, tags y límites")
    p_check.add_argument("--require-env", action="store_true", help="Exige archivo .env con credenciales locales")

    sub.add_parser("verify-fixture", help="Verifica integridad y reglas del fixture científico")

    p_gen = sub.add_parser("generate-data", help="Genera dataset sintético determinista y manifiesto")
    p_gen.add_argument("--volume", type=int, default=1000, help="Número de afirmaciones sintéticas (ej. 1000, 10000, 50000)")
    p_gen.add_argument("--seed", type=int, default=None, help="Semilla determinista")

    p_smoke = sub.add_parser("smoke", help="Ejecuta prueba de conectividad, inserción, consulta y limpieza")
    p_smoke.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))
    p_smoke.add_argument("--manage-docker", action="store_true", help="Levanta y detiene el contenedor automáticamente")
    p_smoke.add_argument("--remove-volumes", action="store_true", help="Elimina el volumen al detener (con --manage-docker)")

    p_load = sub.add_parser("load-data", help="Prepara esquema, carga dataset y crea índices en un motor activo")
    p_load.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))
    p_load.add_argument("--dataset", choices=["fixture", "synthetic"], default="fixture")
    p_load.add_argument("--volume", type=int, default=1000)
    p_load.add_argument("--seed", type=int, default=None)

    p_run = sub.add_parser("run-engine", help="Ejecuta los workloads medidos de un motor individual")
    p_run.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))
    p_run.add_argument("--dataset", choices=["fixture", "synthetic"], default="synthetic")
    p_run.add_argument("--volume", type=int, default=1000)
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--warmup", type=int, default=None)
    p_run.add_argument("--iterations", type=int, default=None)
    p_run.add_argument("--manage-docker", action="store_true")
    p_run.add_argument("--remove-volumes", action="store_true")

    p_pair = sub.add_parser("run-pair", help="Compara secuencialmente la pareja de un modelo (con Docker aislado)")
    p_pair.add_argument("--model", required=True, choices=list(MODEL_PAIRS.keys()))
    p_pair.add_argument("--dataset", choices=["fixture", "synthetic"], default="synthetic")
    p_pair.add_argument("--volume", type=int, default=1000)
    p_pair.add_argument("--seed", type=int, default=None)
    p_pair.add_argument("--warmup", type=int, default=None)
    p_pair.add_argument("--iterations", type=int, default=None)

    p_camp = sub.add_parser("run-campaign", help="Ejecuta la campaña completa secuencial (máx. 120 min)")
    p_camp.add_argument("--volume", type=int, default=10000)
    p_camp.add_argument("--seed", type=int, default=None)
    p_camp.add_argument("--warmup", type=int, default=None)
    p_camp.add_argument("--iterations", type=int, default=None)

    p_clean = sub.add_parser("clean-data", help="Limpia registros de prueba en un motor activo")
    p_clean.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))
    p_clean.add_argument("--all", action="store_true", help="Elimina todas las estructuras de prueba del motor")

    p_up = sub.add_parser("up", help="Levanta únicamente el perfil Docker del motor indicado")
    p_up.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))

    p_down = sub.add_parser("down", help="Detiene el perfil Docker del motor indicado")
    p_down.add_argument("--engine", required=True, choices=list(ENGINE_MODELS.keys()))
    p_down.add_argument("--remove-volumes", action="store_true")

    args = parser.parse_args(argv)
    cfg = load_config(args.env_file)

    if args.command == "check-config":
        errs = validate_config(cfg, require_env_file=args.require_env)
        if errs:
            print("ERRORES DE CONFIGURACIÓN:")
            for e in errs:
                print(f"  - {e}")
            return 1
        print(
            json.dumps(
                {
                    "status": "ok",
                    "bind_host": cfg.bind_host,
                    "max_total_mem_mb": cfg.max_total_mem_mb,
                    "engines": {
                        k: {"image": v.image, "port": v.port, "mem_limit": v.mem_limit}
                        for k, v in cfg.engines.items()
                    },
                },
                indent=2,
            )
        )
        return 0

    if args.command == "verify-fixture":
        bundle, manifest = load_scientific_fixture(cfg.datasets_dir / "scientific_fixture")
        print(
            json.dumps(
                {
                    "status": "ok",
                    "dataset_id": bundle.dataset_id,
                    "counts": bundle.entity_counts(),
                    "manifest_sha256": manifest.get("sha256"),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "generate-data":
        used_seed = cfg.seed if args.seed is None else args.seed
        bundle, manifest_path = export_synthetic_dataset(
            cfg.datasets_dir / "synthetic",
            cfg.datasets_dir / "manifests",
            target_assertions=args.volume,
            seed=used_seed,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "dataset_id": bundle.dataset_id,
                    "manifest": str(manifest_path),
                    "counts": bundle.entity_counts(),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "up":
        compose_up_engine(cfg, args.engine)
        print(f"Motor {args.engine} iniciado y saludable.")
        return 0

    if args.command == "down":
        compose_down_engine(cfg, args.engine, remove_volumes=args.remove_volumes)
        print(f"Motor {args.engine} detenido (remove_volumes={args.remove_volumes}).")
        return 0

    if args.command == "smoke":
        metrics, artifacts = run_smoke_for_engine(
            cfg,
            args.engine,
            manage_docker=args.manage_docker,
            remove_volumes=args.remove_volumes,
        )
        print(
            json.dumps(
                {
                    "run_id": metrics.run_id,
                    "engine": metrics.engine,
                    "server_version": metrics.engine_info.get("server_version"),
                    "connection_ms": round(metrics.connection_ms, 3),
                    "operations": metrics.operation_summaries(),
                    "docker_resources": metrics.docker_resources,
                    "errors": metrics.errors,
                    "artifacts": {k: str(v) for k, v in artifacts.items()},
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1 if metrics.errors else 0

    if args.command == "load-data":
        bundle = _load_bundle_for_args(args, cfg)
        adapter = create_adapter(cfg.engines[args.engine])
        adapter.connect()
        try:
            adapter.prepare_schema()
            counts = adapter.load_dataset(bundle)
            adapter.create_indexes()
            print(json.dumps({"status": "ok", "engine": args.engine, "loaded": counts}, indent=2))
        finally:
            adapter.disconnect()
        return 0

    if args.command == "clean-data":
        adapter = create_adapter(cfg.engines[args.engine])
        adapter.connect()
        try:
            if args.all:
                adapter.reset_all_data()
                print(f"Se reiniciaron todos los datos en {args.engine}.")
            else:
                removed = (
                    adapter.cleanup_test_data("SYNTHETIC_BENCHMARK")
                    + adapter.cleanup_test_data("SCIENTIFIC_FIXTURE")
                )
                print(f"Registros de prueba eliminados en {args.engine}: {removed}")
        finally:
            adapter.disconnect()
        return 0

    if args.command == "run-engine":
        bundle = _load_bundle_for_args(args, cfg)
        metrics, artifacts = run_engine_benchmark(
            cfg,
            args.engine,
            bundle,
            warmup=args.warmup,
            iterations=args.iterations,
            manage_docker=args.manage_docker,
            remove_volumes=args.remove_volumes,
        )
        print(
            json.dumps(
                {
                    "run_id": metrics.run_id,
                    "engine": metrics.engine,
                    "operations": metrics.operation_summaries(),
                    "errors": metrics.errors,
                    "artifacts": {k: str(v) for k, v in artifacts.items()},
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1 if metrics.errors else 0

    if args.command == "run-pair":
        bundle = _load_bundle_for_args(args, cfg)
        results, report = run_pair_comparison(
            cfg, args.model, bundle, warmup=args.warmup, iterations=args.iterations
        )
        print(
            json.dumps(
                {
                    "model": args.model,
                    "report": str(report),
                    "runs": [
                        {"engine": r.engine, "run_id": r.run_id, "errors": r.errors} for r in results
                    ],
                },
                indent=2,
            )
        )
        return 1 if any(r.errors for r in results) else 0

    if args.command == "run-campaign":
        report = run_full_campaign(
            cfg,
            volume=args.volume,
            seed=args.seed,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        print(json.dumps({"status": "ok", "campaign_report": str(report)}, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
