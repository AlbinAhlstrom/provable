#!/bin/bash
set -e

# Stop any existing container
docker stop openhands-app || true
docker rm openhands-app || true

WORKSPACE_BASE=$(pwd)/workspace

echo "Starting OpenHands on port 3000..."
docker run -d --pull=always \
    -e SANDBOX_USER_ID=$(id -u) \
    -e WORKSPACE_MOUNT_PATH=$WORKSPACE_BASE \
    -e LLM_API_KEY="${LLM_API_KEY}" \
    -e LLM_MODEL="gemini/gemini-1.5-pro-latest" \
    -v $WORKSPACE_BASE:/opt/workspace_base \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    ghcr.io/all-hands-ai/openhands:main

echo "OpenHands container started in background."
