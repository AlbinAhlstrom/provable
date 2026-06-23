#!/bin/bash
# dev.sh — Start all Provable services for local development
#
# Services:
#   :8000  FastAPI backend
#   :5173  Main Vite app (Provable UI)
#   :5174  Workspace live preview

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Cleanup handler — kill all child processes on exit (Ctrl+C etc.)
cleanup() {
  echo ""
  echo "Shutting down all services..."
  kill 0
}
trap cleanup EXIT INT TERM

# Color codes for labeled output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Provable dev environment...${NC}"
echo "  Backend API  → http://localhost:8000"
echo "  Main app     → http://localhost:5173"
echo "  Preview app  → http://localhost:5174"
echo ""

# 1. FastAPI backend
(
  cd "$ROOT/backend"
  source venv/bin/activate
  exec uvicorn main:app --reload --host 0.0.0.0 --port 8000
) 2>&1 | sed "s/^/${RED}[backend] ${NC}/" &

# 2. Main Vite app
(
  cd "$ROOT"
  exec npm run dev
) 2>&1 | sed "s/^/${GREEN}[app]     ${NC}/" &

# 3. Workspace live preview
(
  cd "$ROOT/workspace"
  exec npm run dev
) 2>&1 | sed "s/^/${BLUE}[preview] ${NC}/" &

# Wait for all background jobs
wait
