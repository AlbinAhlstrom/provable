# 01 - Architecture & Meta Isolation Rules

## 1. The "Meta" Isolation Invariant (Provable Engine vs. Workspace App)
Provable operates on a strict multi-service architectural split. You MUST NOT confuse the Provable Engine with the Generated Workspace Application.

| Service | Role | Ports | Location | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Provable Backend API** | Engine Backend | `http://localhost:8000` | `backend/` | Fast, pure DDD service layer, API orchestrators, SQLite `provable.db`. |
| **PM Studio Frontend** | Engine Presentation | `http://localhost:5173` | `frontend/` | React 18 / Vite PM Studio, aggregate inspector, BDD spec inbox. |
| **Workspace Domain API** | Generated App Backend | `http://localhost:8001` | `workspace/src/app.py` | Generated FastAPI app exposing domain OpenAPI `/openapi.json` & `/docs`. |
| **Workspace Preview** | Generated App Preview | `http://localhost:5174` | `workspace/` | Generated React sandbox or Vite application preview. |
| **Allure Test Dashboard** | CI/Test Dashboard | `http://localhost:5050` | Containerized | Allure Docker reporting service for test execution analytics. |

### Strict Isolation Invariants:
1. **API Port 8000 vs Port 8001**:
   - `http://localhost:8000` is Provable's internal orchestration engine API (e.g. `/api/onboarding/*`, `/api/specs/*`, `/api/components/*`).
   - `http://localhost:8001` is the synthesized workspace FastAPI application exposing domain entity CRUD and OpenAPI Swagger documentation (`/docs`).
   - The Swagger iframe in PM Studio strictly targets `http://localhost:8001/docs`.
2. **Frontend Port 5173 vs Port 5174**:
   - `http://localhost:5173` is PM Studio.
   - `http://localhost:5174` is the live sandbox preview.

---

## 2. `workspace/` is Strictly Off-Limits (No Bandages Invariant)
The `workspace/` directory contains the application produced by the automated generation pipeline.
**NEVER directly write, edit, patch, or commit files inside `workspace/`.**

Any structural, template, or configuration change meant for `workspace/` MUST be implemented in the authoritative backend generator code (`backend/onboarding/skeleton_builder.py`, `backend/onboarding/templates/workspace_scaffold.py`, `backend/prompts/ui_generation.md`).

### Permitted Actions:
- Read `workspace/` files to **diagnose** runtime/build errors or inspect generated output.
- Run `git log`, `git status`, `git diff` inside `workspace/` for inspection only.

### Forbidden Actions:
- Edit or create any files directly inside `workspace/` (always edit generator templates in `backend/` instead).
- Run `git add`, `git commit`, `git revert`, or `git reset` inside `workspace/`.

---

## 3. Starting & Managing the Application Stack
- **Ensure Docker Desktop is running** on the Windows host.
- **Start the Allure Dashboard container**:
  ```powershell
  docker compose -f docker-compose.allure.yaml up -d
  ```
- **Application Stack Execution Invariant**:
  **NEVER execute `python run.py` via `run_command` in background tasks.**
  Executing `python run.py` spawns long-lived WatchFiles reloader processes that trigger system restarts, interrupting the agent's turn and breaking the chat session. The user manages `python run.py` in their own terminal session, while Uvicorn and Vite handle hot-module-reloading (HMR) automatically.

---

## 4. Obsidian Vault Documentation & Handover Continuity
Maintain a well-structured Obsidian vault under `vault/`:
- **Cross-Chat Handover Invariant**: At the start of EVERY chat session or task, read `vault/HANDOVER.md` to restore full architectural state, active context, and planned unexecuted work items.
- **Session Wrap-Up Invariant**: At the conclusion of any task where architectural decisions or roadmap items are planned/modified, update `vault/HANDOVER.md` so future agents and chats pick up seamlessly.
- Keep `vault/Home.md` index file up-to-date.
- Document architectural changes under `vault/01-Architecture/`.
- Document new agent behaviors or workflow changes under `vault/02-Workflows/`.
- Use standard double-bracket internal links (e.g. `[[System Architecture]]`) to link related concepts.
