#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLATFORM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$PLATFORM_DIR/.." && pwd)"
VENV="$REPO_ROOT/.venv"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

pip install --upgrade pip hatchling
pip install -r "$PLATFORM_DIR/requirements.txt"
pip install -e "$REPO_ROOT[web]"

if [[ ! -f "$PLATFORM_DIR/.env" ]]; then
  echo "Tip: copy platform/.env.example to platform/.env for Kaggle URL uploads"
fi

cd "$PLATFORM_DIR"
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
