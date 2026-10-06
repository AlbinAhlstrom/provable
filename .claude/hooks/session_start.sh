#!/bin/bash
# Installs Python and Node dependencies in Claude Code cloud sessions.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"
pip install -q -r requirements.txt
(cd frontend && npm ci --silent)
