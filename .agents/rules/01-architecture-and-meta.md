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

Any structural, template, or configuration change meant for `workspace/` MUST be implemented in the authoritative backend generator code (`backend/onboarding/skeleton_builder.py`, `backend/onboarding/templates/workspace_scaffold.py`, the LLM prompts in `backend/prompts/` (notably `app_assembly.md`), and the fallback template `backend/onboarding/templates/fallback_app.tsx.tmpl`).

The fallback template is deliberately domain-neutral (it renders only blueprint data and the `catalog` fixture collection). Never add domain-specific templates or keyword-triggered branches (pizza, warehouse, booking...) to the generator; domain behavior must come from the LLM-planned blueprint.

### Permitted Actions:
- Read `workspace/` files to **diagnose** runtime/build errors or inspect generated output.
- Run `git log`, `git status`, `git diff` inside `workspace/` for inspection only.

### Forbidden Actions:
- Edit or create any files directly inside `workspace/` (always edit generator templates in `backend/` instead).
- Run `git add`, `git commit`, `git revert`, or `git reset` inside `workspace/`.

---

## 3. Starting & Managing the Application Stack
- **Docker must be running** (Docker Desktop on Windows/macOS) for the optional Allure dashboard.
- **Start the Allure Dashboard container**:
  ```bash
  docker compose -f docker-compose.allure.yaml up -d
  ```
- **Application Stack Execution Invariant**:
  **In Claude Code cloud sessions the agent owns the running app**: a SessionStart hook starts it, and `bash .claude/hooks/ensure_app_running.sh [--restart|--stop]` is the only way the agent starts, restarts or stops it (idempotent, detached, logs to `logs/run.log`). Do not launch `run.py` by hand (the guard hook blocks it). On a developer's own machine the developer runs `python run.py` in their terminal.
  `run.py` spawns long-lived reloader processes; uvicorn and Vite hot-reload code edits automatically, so a restart is only needed for changes that require a clean boot (new dependencies, startup code, env vars). Port conflicts are cleared by the script.

---

## 4. Obsidian Vault Documentation
`vault/` is the project wiki (architecture, workflows, ADRs). It is documentation, not a task log: git history is the record of what changed.
- When you make an architectural decision, document it under `vault/01-Architecture/` or as an ADR in `vault/04-Decisions/`.
- Document new agent behaviors or workflow changes under `vault/02-Workflows/`.
- Keep `vault/Home.md` index up-to-date when adding or deleting pages.
- Use standard double-bracket internal links (e.g. `[[System Architecture]]`) to link related concepts.
- Do not link to files that no longer exist; describe removed things in plain text.
