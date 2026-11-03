#!/bin/bash
# Container entrypoint: engine API on :8000, generated-app preview on :5174, generated domain API on :8001.
# Starts as root only to give the data volume to the unprivileged user. Generated code then runs without any secret
# in its environment, and the engine seals its own at startup (llm_credentials.py).
set -euo pipefail
cd /app
WS=/data/ws-root
RUN_AS=(setpriv --reuid=provable --regid=provable --init-groups)
# Generated code gets only these settings, never the container's secrets.
BARE_ENV=(env -i "PATH=$PATH" HOME=/home/provable "PROVABLE_WORKSPACE=$WS" PYTHONPATH=/app/backend PYTHONUNBUFFERED=1
          PLAYWRIGHT_BROWSERS_PATH=/ms-playwright)

mkdir -p "$WS"
[ "$(stat -c %U /data)" = provable ] || chown -R provable:provable /data
export PROVABLE_WORKSPACE="$WS"
export PROVABLE_KEYS_DB=/data/keys/provable-keys.db

if [ ! -f "$WS/package.json" ] || [ ! -f "$WS/src/App.tsx" ] || [ ! -f "$WS/src/app.py" ]; then
  (cd backend && "${RUN_AS[@]}" "${BARE_ENV[@]}" python -c "import os; from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold as c; c(os.environ['PROVABLE_WORKSPACE'])")
fi
# The generated domain API, which the preview reaches through Vite's /api proxy; it reloads as the engine rewrites it.
(
  cd "$WS"
  exec "${RUN_AS[@]}" "${BARE_ENV[@]}" python /app/backend/run_server.py src.app:app --reload --reload-dir "$WS/src" --host 0.0.0.0 --port 8001
) &
# The preview installs and starts in the background so the API answers at once.
(
  cd "$WS"
  exec "${RUN_AS[@]}" "${BARE_ENV[@]}" bash -c '[ -d node_modules/vite ] || npm install --no-audit --no-fund; exec npm run dev -- --host 0.0.0.0 --port 5174'
) &
cd backend
exec "${RUN_AS[@]}" env HOME=/home/provable python run_server.py main:app --host 0.0.0.0 --port 8000
