#!/bin/bash
# Container entrypoint: engine API on :8000, generated-app preview on :5174, generated domain API on :8001.
set -euo pipefail
cd /app
WS=/data/ws-root
mkdir -p "$WS"
export PROVABLE_WORKSPACE="$WS"

if [ ! -f "$WS/package.json" ] || [ ! -f "$WS/src/App.tsx" ] || [ ! -f "$WS/src/app.py" ]; then
  (cd backend && python -c "import os; from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold as c; c(os.environ['PROVABLE_WORKSPACE'])")
fi
# The generated domain API, which the preview reaches through Vite's /api proxy; it reloads as the engine rewrites it.
(
  cd "$WS"
  exec python /app/backend/run_server.py src.app:app --reload --reload-dir "$WS/src" --host 0.0.0.0 --port 8001
) &
# The preview installs and starts in the background so the API answers at once.
(
  cd "$WS"
  [ -d node_modules/vite ] || npm install --no-audit --no-fund
  exec npm run dev -- --host 0.0.0.0 --port 5174
) &
cd backend
exec python run_server.py main:app --host 0.0.0.0 --port 8000
