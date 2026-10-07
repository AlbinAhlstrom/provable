#!/bin/bash
# Ensures the Provable stack (backend :8000, PM Studio :5173, workspace preview :5174) is running.
# Idempotent: does nothing if the app already answers. The agent owns the running app.
#
#   bash .claude/hooks/ensure_app_running.sh            start if not running
#   bash .claude/hooks/ensure_app_running.sh --restart  stop and start again (e.g. after backend edits that need a clean boot)
#   bash .claude/hooks/ensure_app_running.sh --stop     stop the stack
#
# Output goes to logs/run.log; every pipeline run records itself to logs/runs/<id> (see backend/run_recorder.py).
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

up() { curl -s -o /dev/null --max-time 2 "http://localhost:$1"; }

stop_stack() {
  # run.py handles SIGINT by shutting down its child services.
  pkill -INT -f '^python3? run\.py$' 2>/dev/null || true
  for _ in $(seq 1 15); do
    up 8000 || up 5173 || return 0
    sleep 1
  done
  # Anything still holding the ports (orphaned Vite/uvicorn) is stopped explicitly.
  for port in 8000 5173 5174 8001; do
    pid=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    [ -n "$pid" ] && kill $pid 2>/dev/null || true
  done
}

case "${1:-}" in
  --stop) stop_stack; echo "[app] stopped"; exit 0 ;;
  --restart) stop_stack ;;
esac

if up 8000 && up 5173; then
  echo "[app] already running (backend :8000, Studio :5173)"
  exit 0
fi

if [ -z "${GEMINI_API_KEY:-}${LLM_API_KEY:-}${OPENAI_API_KEY:-}" ] && ! grep -qE '^(GEMINI_API_KEY|LLM_API_KEY|OPENAI_API_KEY)=.+' .env 2>/dev/null; then
  echo "[app] WARNING: no LLM API key (env vars or .env). The app will start, but generation will fail loudly."
fi

mkdir -p logs
# setsid detaches the stack from this shell so it outlives the hook / tool call.
setsid nohup python3 run.py > logs/run.log 2>&1 < /dev/null &
echo "[app] starting (log: logs/run.log, pipeline runs: logs/runs)"

for _ in $(seq 1 90); do
  if up 8000 && up 5173; then
    echo "[app] ready: backend :8000, Studio :5173, preview :5174"
    exit 0
  fi
  sleep 2
done
echo "[app] NOT ready after 180s; see logs/run.log"
exit 1
