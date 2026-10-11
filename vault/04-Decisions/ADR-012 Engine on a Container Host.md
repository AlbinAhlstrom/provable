# ADR-012: Engine on a Container Host

## Context
A kickstart on Vercel fails with "npm is not installed". Vercel functions have no Node, no writable checkout and no background processes, but the engine runs `npm`, builds, pytest and a headless browser (see [[ADR-005 Vercel Multi-Service Deployment]]).

## Decision
- The engine runs in a container on Fly.io (`Dockerfile`, `fly.toml`, `deploy/start.sh`): Python, Node 20, Chromium and Playwright. It serves the API on :8000 and the generated app's preview on :5174.
- Generated output and the database live on a volume mounted at `/data` (`PROVABLE_WORKSPACE`), so they survive restarts.
- PM Studio stays on Vercel as a static bundle (`vercel.json` has only the `frontend` service).
- The Studio reaches the engine through `VITE_ENGINE_URL` (calls to `/api/...` are prefixed in `frontend/src/engine.ts`) and shows the preview from `VITE_PREVIEW_URL`. Both are unset in development, where the Vite proxy and `localhost:5174` apply.
- Generated Vite configs set `allowedHosts: true` so the preview answers on the hosted hostname.

## Consequences
- Deploy: `fly volumes create provable_data --size 3`, `fly secrets set GEMINI_API_KEY=...`, `fly deploy`; then set the two `VITE_` variables in Vercel.
- The engine API is public and unauthenticated (CORS is open); add auth before sharing the URL.
- The Swagger tab still points at the workspace API on :8001, which is not exposed.
- The generated app's fixtures fallback still calls `localhost:8000`.
- The image was not built when this was written; expect small fixes on the first build.

## Status
Accepted; supersedes the Vercel backend service of ADR-005.
