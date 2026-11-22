#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Uso: $0 <mysql|postgresql|mongodb|couchdb|neo4j|memgraph> <up|down|clean|status|smoke>" >&2
  exit 1
fi

ENGINE="$1"
ACTION="$2"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE="$ROOT/docker/compose.yaml"
ENV_FILE="$ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Falta $ENV_FILE. Copie .env.example a .env." >&2
  exit 1
fi

EXPECTED="biolink-bench-$ENGINE"

case "$ACTION" in
  up)
    OTHERS="$(docker ps --filter 'name=biolink-bench-' --format '{{.Names}}' | grep -v "^${EXPECTED}$" || true)"
    if [[ -n "$OTHERS" ]]; then
      echo "Error: hay otros motores activos ($OTHERS). Deténgalos antes de iniciar $ENGINE." >&2
      exit 1
    fi
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE" --profile "$ENGINE" up -d --wait
    ;;
  down)
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE" --profile "$ENGINE" down
    ;;
  clean)
    echo "ADVERTENCIA: eliminando contenedor y volumen de datos de $ENGINE"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE" --profile "$ENGINE" down -v
    ;;
  status)
    docker ps -a --filter "name=$EXPECTED"
    ;;
  smoke)
    PY="$ROOT/.venv/bin/python"
    [[ -x "$PY" ]] || PY="python3"
    "$PY" -m biolink_bench smoke --engine "$ENGINE"
    ;;
  *)
    echo "Acción desconocida: $ACTION" >&2
    exit 1
    ;;
esac
