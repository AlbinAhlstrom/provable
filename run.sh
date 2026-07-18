#!/bin/bash
# run.sh — One-step script to start Allure container and start the Provable development stack

# 1. Start Allure Dashboard container
echo "Starting Allure Dashboard container..."
docker compose -f docker-compose.allure.yaml up -d

# 2. Start the Development stack
echo "Starting the development stack..."
bash dev.sh
