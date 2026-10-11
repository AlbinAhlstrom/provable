#!/bin/bash
# Container entrypoint: engine API on :8000, generated-app preview on :5174.
set -euo pipefail
cd /app
WS=/data/ws-root
mkdir -p "$WS"
export PROVABLE_WORKSPACE="$WS"

if [ ! -f "$WS/package.json" ] || [ ! -f "$WS/src/App.tsx" ]; then
  (cd backend && python -c "import os; from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold as c; c(os.environ['PROVABLE_WORKSPACE'])")
fi
if [ ! -d "$WS/node_modules/vite" ]; then
  (cd "$WS" && npm install --no-audit --no-fund)
fi

(cd "$WS" && exec npm run dev -- --host 0.0.0.0 --port 5174) &
cd backend
exec python run_server.py main:app --host 0.0.0.0 --port 8000
