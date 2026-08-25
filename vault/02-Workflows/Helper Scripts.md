# Helper & Utility Scripts

This document details the single cross-platform application launcher and developer inspection scripts.

---

## 🚀 Single Application Launcher (`run.py`)

`run.py` located at the project root is the master launcher for the entire Provable application stack:

### Execution Flow
1. **OS & Environment Detection**: Detects whether running on Windows host, WSL (Windows Subsystem for Linux), or native Linux.
2. **Dependency Resolution**: Checks Python virtualenv packages (`requirements.txt`) and Node modules (`package.json`), auto-installing missing packages.
3. **Containerized Allure Service**: Verifies Docker Desktop status and launches the Allure container (`docker-compose.allure.yaml` on port `5050`).
4. **FastAPI Backend Server**: Spawns the FastAPI application (`backend/app.py`) on `http://localhost:8000`.
5. **Vite PM Studio Frontend**: Spawns the Vite dev server on `http://localhost:5173`.

### Wrappers
- **`run.ps1`**: PowerShell wrapper for Windows host execution of `python run.py`.
- **`run.sh`**: Bash wrapper for Linux / WSL execution of `python3 run.py`.

---

## 🛠️ Developer Diagnostic Scripts (`backend/scripts/`)

### 1. `backend/scripts/deep_heuristic_scan.py`
- **Purpose**: Scans python codebase for lingering hardcoded domain keywords and heuristic switchboards.
- **Usage**: `python backend/scripts/deep_heuristic_scan.py`

### 2. `backend/scripts/inspect_ast_pipeline.py`
- **Purpose**: Inspects AST compilation stages and LibCST code splicing transformations.
- **Usage**: `python backend/scripts/inspect_ast_pipeline.py`

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original helper scripts included live log tailing utilities (tail_logs.sh). While streaming logs are available via backend stdout and pytest JSON reports, a dedicated CLI log tailing script for TDD execution state is helpful for developer ergonomics.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Bug-Reproduction-and-Testing-Policy]]

