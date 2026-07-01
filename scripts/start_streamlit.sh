#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-5000}"
export PYTHONUSERBASE="${PYTHONUSERBASE:-$HOME/.local}"
export PATH="$HOME/.local/bin:$ROOT/.venv/bin:$PATH"

# region agent log
_log() {
  local hypothesis="$1"
  local message="$2"
  local data="$3"
  echo "{\"sessionId\":\"75e047\",\"hypothesisId\":\"${hypothesis}\",\"location\":\"scripts/start_streamlit.sh\",\"message\":\"${message}\",\"data\":${data}}" >&2
}
# endregion

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
  _log "H2" "python_selected" "{\"source\":\"venv\",\"python\":\"${PYTHON}\"}"
else
  PYTHON="python3"
  _log "H2" "python_selected" "{\"source\":\"system\",\"pythonuserbase\":\"${PYTHONUSERBASE}\"}"
fi

if ! "$PYTHON" -c "import streamlit" 2> /tmp/wcp_streamlit_import.err; then
  _log "H3" "streamlit_import_failed" "{\"error\":$(python3 -c 'import json; print(json.dumps(open("/tmp/wcp_streamlit_import.err").read()))')}"
  exit 1
fi

_log "H1" "streamlit_start" "{\"port\":\"${PORT}\",\"cwd\":\"${ROOT}\"}"

exec "$PYTHON" -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableWebsocketCompression false
