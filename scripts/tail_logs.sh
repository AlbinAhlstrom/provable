#!/bin/bash
# tail_logs.sh — Stream OpenHands container buildx logs to backend ticket log

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TICKET_ID="${1:-REQ-001}"
LOG_FILE="$ROOT/backend/logs/${TICKET_ID}.log"

mkdir -p "$ROOT/backend/logs"
container_id=$(docker ps -q -f ancestor=ghcr.io/all-hands-ai/openhands:main)

if [ -n "$container_id" ]; then
    echo "Tailing container $container_id to $LOG_FILE..."
    docker exec $container_id bash -c "tail -n 100 -f /proc/\$(pgrep -f docker-buildx)/fd/2" >> "$LOG_FILE" &
else
    echo "No running OpenHands container found."
fi
