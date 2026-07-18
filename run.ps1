# run.ps1 — One-step script to start Allure container and start the Provable development stack

# 1. Start Allure Dashboard container on the Windows host
Write-Host "Starting Allure Dashboard container..." -ForegroundColor Green
docker compose -f docker-compose.allure.yaml up -d

# 2. Start the Development stack (FastAPI backend + Vite frontend) inside WSL
Write-Host "Starting the development stack inside WSL..." -ForegroundColor Green
wsl -e bash dev.sh
