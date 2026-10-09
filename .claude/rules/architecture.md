# Architecture and meta isolation

## Engine vs generated app

Provable is a multi-service split. Never confuse the engine with the app it generates.

| Service | Role | Port | Location |
| --- | --- | --- | --- |
| Provable Backend API | engine orchestration (`/api/onboarding/*`, `/api/specs/*`, `/api/components/*`), SQLite `provable.db` | :8000 | `backend/` |
| PM Studio | engine UI (React 18 / Vite) | :5173 | `frontend/` |
| Workspace Domain API | generated FastAPI app, OpenAPI at `/openapi.json` and `/docs` | :8001 | `workspace/src/app.py` |
| Workspace Preview | generated app preview | :5174 | `workspace/` |
| Allure dashboard | optional test reporting container | :5050 | `docker-compose.allure.yaml` |

The Swagger iframe in PM Studio targets `http://localhost:8001/docs`, never :8000.

## `workspace/` is off-limits

`workspace/` is an embedded git repo of generated output. Do not write, edit, patch, delete or commit anything in it, by any tool (Edit, Write, shell redirects, `sed -i`, `git` inside it). `.claude/hooks/guard.py` blocks the common routes; the rule holds regardless.

- Allowed: reading files to diagnose build or runtime errors, and `git log` / `status` / `diff` inside it.
- Any structural, template or configuration change meant for `workspace/` goes into the generator: `backend/onboarding/skeleton_builder.py`, `presentation_projection_synthesizer.py`, `templates/workspace_scaffold.py`, `backend/prompts/` (notably `app_assembly.md`), and the fallback template `templates/fallback_app.tsx.tmpl`.
- The fallback template is deliberately domain-neutral (it renders only blueprint data and the `catalog` fixture collection). Never add domain-specific templates or keyword-triggered branches (pizza, warehouse, booking, ...). Domain behaviour comes from the LLM-planned blueprint.

## The running stack

In cloud sessions the agent owns the app: a SessionStart hook starts it, and `bash .claude/hooks/ensure_app_running.sh [--restart|--stop]` is the only way to start, restart or stop it. Never launch the `run.py` launcher by hand (the guard blocks it). On a developer machine the developer runs it in their own terminal. uvicorn and Vite hot-reload code edits; restart only for new dependencies, startup code or env vars.

Allure is optional: `docker compose -f docker-compose.allure.yaml up -d` (needs Docker).

## Vault documentation

`vault/` is the project wiki (architecture, workflows, ADRs), not a task log: git history is the record of what changed.

- Architectural decision: `vault/01-Architecture/` or an ADR in `vault/04-Decisions/`. Workflow or agent-behaviour change: `vault/02-Workflows/`.
- Keep `vault/Home.md` listing every page. Link with `[[Page Name]]`. Never link to a page or file that no longer exists; describe removed things in plain text.
- `backend/tests/unit/test_vault_hygiene.py` enforces broken links, Home coverage and references to missing source files.
