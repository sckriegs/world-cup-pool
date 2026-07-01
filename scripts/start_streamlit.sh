#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-5000}"
export PYTHONUSERBASE="${PYTHONUSERBASE:-$HOME/.local}"
export PATH="$HOME/.local/bin:$ROOT/.venv/bin:$PATH"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

if ! "$PYTHON" -c "import streamlit"; then
  echo "streamlit not installed; run deployment build or pip install -r requirements.txt" >&2
  exit 1
fi

exec "$PYTHON" -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableWebsocketCompression false
