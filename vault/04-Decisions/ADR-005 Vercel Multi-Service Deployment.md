# ADR-005: Vercel Multi-Service Deployment

## Context
The repository holds two deployable programs: the engine API (`backend/`, FastAPI) and PM Studio (`frontend/`, Vite/React). Locally `run.py` starts both, plus the *generated* workspace app (API :8001, preview :5174) and an optional Allure container. In development the Studio reaches the API through Vite's `/api` proxy.

## Decision
Deploy as one Vercel project with two services (`vercel.json`):

| Service | Root | Framework | Public path |
| :--- | :--- | :--- | :--- |
| `backend` | `backend/` | FastAPI | `/api/*` |
| `frontend` | `frontend/` | Vite | everything else (`/*`) |

- Same-origin routing replaces the dev proxy: the browser calls relative `/api/...` URLs (no hardcoded `localhost:8000`), and a top-level rewrite sends `/api/(.*)` to `backend`, the catch-all to `frontend`. The backend's routes already start with `/api`, so the path is forwarded unchanged.
- No service bindings: neither service calls the other server-side. The frontend is a static bundle whose browser requests go through the rewrite.
- `backend/requirements.txt` lists runtime dependencies only; the root `requirements.txt` includes it and adds launcher, test and screenshot tools.
- `.vercelignore` keeps `workspace/` (generated output, embedded repo), `logs/`, `.env`, the wiki and tests out of the upload.

## Serverless mode (`VERCEL=1`)
Vercel functions have a read-only checkout and cannot keep background processes, so `config_loader.is_serverless()` makes the engine:
- use an ephemeral scratch workspace in the temp directory (`provable-workspace`) instead of `workspace/`;
- skip starting the workspace dev servers and the Allure project bootstrap at startup.

## Consequences (what a deployment can and cannot do)
- Works: the Studio UI, all read endpoints, LLM calls and domain decomposition, writing the generated skeleton into the scratch workspace (verified in a read-only simulation).
- State is **ephemeral and per function instance**: the SQLite database lives in the scratch workspace, so saved specs and kickstart state can vanish between requests or cold starts. Real persistence needs an external database (not done).
- The generated app cannot be previewed: the workspace API (:8001) and preview (:5174) are local-only processes, so the Studio's Preview and API (Swagger) tabs have nothing to show. The `AppPreview` iframes still point at `localhost`.
- Anything that shells out (pytest runs, git, npm) will not work in functions.
- Long LLM calls (~20 s for the router decomposition) must fit the function's maximum duration.

## Status
Accepted (initial configuration; verify path forwarding and limits on the first preview deployment).
