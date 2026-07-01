#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5000}"
# region agent log
echo "{\"sessionId\":\"75e047\",\"hypothesisId\":\"H1\",\"location\":\"scripts/start_streamlit.sh\",\"message\":\"streamlit_start\",\"data\":{\"port\":\"${PORT}\"}}" >&2
# endregion

exec python3 -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}" \
  --server.headless true \
  --server.enableCORS false \
  --server.enableWebsocketCompression false
