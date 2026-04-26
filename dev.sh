#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_DIR="$ROOT_DIR/ui"
ENV_FILE="$ROOT_DIR/.env.local-dev"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
VENV_BIN_DIR="$ROOT_DIR/.venv/bin"
COMPOSE_FILE="$ROOT_DIR/docker-compose.dev.yml"

START_INFRA=1
WITH_CELERY=0
SERVICES=()
PIDS=()
NAMES=()

usage() {
  cat <<'EOF'
Usage: ./dev.sh [backend] [admin] [chat] [--skip-infra] [--with-celery]

Starts the local development stack from one command.

Examples:
  ./dev.sh
  ./dev.sh backend admin
  ./dev.sh backend admin --with-celery
  ./dev.sh chat --skip-infra

Defaults:
  - services: backend admin chat
  - infra: start PostgreSQL and Redis via docker-compose.dev.yml
  - celery: off (use --with-celery to start alongside backend)
EOF
}

ensure_file() {
  local path="$1"
  local message="$2"
  if [[ ! -e "$path" ]]; then
    printf 'Error: %s\n' "$message" >&2
    exit 1
  fi
}

ensure_command() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    printf 'Error: required command not found: %s\n' "$name" >&2
    exit 1
  fi
}

start_process() {
  local name="$1"
  shift

  printf '[%s] starting\n' "$name"
  setsid "$@" &

  PIDS+=("$!")
  NAMES+=("$name")
}

cleanup() {
  local exit_code="${1:-0}"

  if ((${#PIDS[@]} > 0)); then
    printf '\nStopping local app processes...\n'
    for pid in "${PIDS[@]}"; do
      kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    done
    wait "${PIDS[@]}" 2>/dev/null || true
  fi

  exit "$exit_code"
}

trap 'cleanup 0' INT TERM

while (($# > 0)); do
  case "$1" in
    backend|admin|chat)
      SERVICES+=("$1")
      ;;
    --skip-infra)
      START_INFRA=0
      ;;
    --with-celery)
      WITH_CELERY=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Error: unknown argument: %s\n\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if ((${#SERVICES[@]} == 0)); then
  SERVICES=(backend admin chat)
fi

ensure_file "$ENV_FILE" "missing .env.local-dev. Copy .env.local-dev.example first."
ensure_file "$PYTHON_BIN" "missing .venv/bin/python. Create the local uv environment first."
ensure_file "$UI_DIR/node_modules" "missing ui/node_modules. Run npm install in ui/."
ensure_command npm
ensure_command setsid

if ((START_INFRA)); then
  ensure_command docker
  printf 'Starting PostgreSQL and Redis...\n'
  docker compose -f "$COMPOSE_FILE" up -d
fi

set -a
source "$ENV_FILE"
set +a
export PATH="$VENV_BIN_DIR:$PATH"

BACKEND_HOST="${MAXKB_DEV_HOST:-127.0.0.1}"
BACKEND_PORT="${MAXKB_DEV_PORT:-3080}"
BACKEND_DISPLAY_HOST="$BACKEND_HOST"
BACKEND_TARGET="http://127.0.0.1:${BACKEND_PORT}"
if [[ "$BACKEND_DISPLAY_HOST" == "0.0.0.0" ]]; then
  BACKEND_DISPLAY_HOST="127.0.0.1"
fi

for service in "${SERVICES[@]}"; do
  case "$service" in
    backend)
      start_process backend "$PYTHON_BIN" "$ROOT_DIR/main.py" dev web
      if ((WITH_CELERY)); then
        start_process celery "$PYTHON_BIN" "$ROOT_DIR/main.py" dev celery
      fi
      ;;
    admin)
      start_process admin bash -lc "cd '$UI_DIR' && export VITE_API_TARGET='$BACKEND_TARGET' && exec npm run dev -- --host 0.0.0.0 --port 3000"
      ;;
    chat)
      start_process chat bash -lc "cd '$UI_DIR' && export VITE_API_TARGET='$BACKEND_TARGET' && exec npm run chat -- --host 0.0.0.0 --port 3001"
      ;;
  esac
done

printf '\nLocal development services:\n'
printf '  Backend API: http://%s:%s\n' "$BACKEND_DISPLAY_HOST" "$BACKEND_PORT"
if ((WITH_CELERY)); then
  printf '  Celery:      enabled\n'
fi

for service in "${SERVICES[@]}"; do
  case "$service" in
    admin)
      printf '  Admin UI:    http://127.0.0.1:3000/admin\n'
      ;;
    chat)
      printf '  Chat UI:     http://127.0.0.1:3001/chat\n'
      ;;
  esac
done

printf '\nPress Ctrl+C to stop local app processes. Docker infra stays running.\n\n'

wait -n "${PIDS[@]}"
status=$?
printf '\nA dev process exited with status %s. Stopping the rest.\n' "$status" >&2
cleanup "$status"
