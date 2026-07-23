# Helper & Utility Scripts

This document details the single cross-platform application launcher and utility scripts in `scripts/`.

---

## 🚀 Single Application Launcher (`run.py`)

`run.py` located at the project root is the master launcher for the entire Provable application stack:

### Execution Flow
1. **OS & Environment Detection**: Detects whether running on Windows host, WSL (Windows Subsystem for Linux), or native Linux.
2. **Dependency Resolution**: Checks Python virtualenv packages (`requirements.txt`) and Node modules (`package.json`), auto-installing missing packages.
3. **Containerized Allure Service**: Verifies Docker Desktop status and launches the Allure container (`docker-compose.allure.yaml` on port `5050`).
4. **FastAPI Backend Server**: Spawns the FastAPI application (`backend/main.py`) on `http://localhost:8000`.
5. **Vite PM Studio Frontend**: Spawns the Vite dev server on `http://localhost:5173`.

---

## 🛠️ Utility Scripts (`scripts/`)

### 1. `scripts/reset_ticket.py`
- **Purpose**: Resets a requirement ticket's status back to `Backlog` in SQLite DataStore.
- **Usage**: `python scripts/reset_ticket.py REQ-1002`

### 2. `scripts/update_json.py`
- **Purpose**: Fetches the `git diff` between `main` and a target ticket branch (`ticket/REQ-XXX`) inside `workspace/`, updates the requirement status to `Review`, and attaches the proposed code diff to SQLite DataStore.
- **Usage**: `python scripts/update_json.py REQ-1002`

### 3. `scripts/tail_logs.sh`
- **Purpose**: Streams real-time agent execution logs from `backend/logs/<TICKET_ID>.log` for developer debugging.
- **Usage**: `bash scripts/tail_logs.sh REQ-1002`

### 4. `scripts/run.ps1`
- **Purpose**: PowerShell wrapper for Windows host execution of `python run.py`.
- **Usage**: `.\scripts\run.ps1`

### 5. `scripts/run.sh`
- **Purpose**: Bash wrapper for Linux / WSL execution of `python3 run.py`.
- **Usage**: `./scripts/run.sh`
