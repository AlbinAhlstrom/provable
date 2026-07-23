#!/bin/bash
# run.sh — Bash convenience wrapper to run python run.py
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
python3 run.py || python run.py
