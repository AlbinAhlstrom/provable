# Provable

Spec-driven code generation engine: TDD verification loops + DDD architecture. The engine
(`backend/`, `frontend/`) *generates* an app into `workspace/`. Never confuse the two.

## Before you start
- Skim `vault/Home.md` for the architecture wiki; git history is the change log.
- Read the rule file(s) for your task before editing (full index: `.agents/AGENTS.md`):
  - Architecture, ports, workspace isolation: @.agents/rules/01-architecture-and-meta.md
  - React / PM Studio UI: @.agents/rules/02-frontend-and-ui.md
  - Backend features, tests, DDD layers: @.agents/rules/03-tdd-engine.md
- Document architectural decisions in `vault/` (architecture page or ADR) and keep `vault/Home.md` current.

## Commands
- Install: `pip install -r requirements.txt` and `cd frontend && npm ci` (auto-run in cloud sessions by `.claude/hooks/session_start.sh`)
- Backend tests (fast, ~15s): `python -m pytest backend/tests/`
- Frontend build/typecheck: `cd frontend && npm run build`
- Pre-flight (build + tests + purity lint + live checks): `python scripts/agent_preflight_check.py`.
  Runs without an LLM key (tests mock the LLM). Phases 1-5 work standalone; Phase 6 (UI screenshot) is only
  captured if PM Studio is running on :5173, otherwise it is reported as SKIPPED, which means no visual verification.
- **The agent owns the running app.** In cloud sessions a SessionStart hook starts the full stack (backend :8000, Studio :5173, preview :5174, via `run.py`) if it isn't already up. Before testing anything, check it with `bash .claude/hooks/ensure_app_running.sh` (idempotent); use `--restart` after backend changes that need a clean boot and `--stop` to stop it. Logs: `logs/run.log`; step traces: `logs/trace` (see below). Never launch `run.py` by hand.
- Every pipeline step's input/output is traced to `logs/trace` while the app runs (the launcher sets `PROVABLE_TRACE_DIR`); clear it with `rm -rf logs/trace` before a fresh experiment, then run `python scripts/trace_report.py logs/trace` (`--full N` shows one step). Implemented in `backend/pipeline_trace.py`; API keys are redacted.
- Real LLM calls need `GEMINI_API_KEY` (or `LLM_API_KEY` / `OPENAI_API_KEY`), plus optionally `OPENAI_BASE_URL` and `LLM_MODEL`. Locally copy `.env.example` to `.env`; in cloud sessions set them as environment variables in the cloud environment's settings (never paste keys into chat or commit them). Without a key the app still starts, but generation fails loudly.

## Hard invariants (details in the rule files)
- **`workspace/` is read-only for you** (it is an embedded git repo of generated output). Fix the generator in
  `backend/onboarding/` (`skeleton_builder.py`, `templates/workspace_scaffold.py`) or `backend/prompts/` instead.
- Ports: engine API :8000, PM Studio :5173, generated app API :8001, generated preview :5174, Allure :5050.
- DDD layering: pure domain (no FastAPI/Pydantic/DB) -> repositories -> service layer/UoW -> routers.
  Routers never import `db.store`.
- TDD loop: RED -> GREEN -> WIRE -> VERIFY, done directly in the main context (subagents only for read-only research/review). Don't weaken tests to get green;
  if the architecture evolved, rewrite or delete the obsolete test.
- Frontend is domain-agnostic: no hardcoded domain terms (Pallet, Pizza, Order...) and no mock UI. Fail loudly.
- Run the full test suite before every commit and the pre-flight check before declaring work done.
  (`.claude/hooks/guard.py` enforces the test run on `git commit`, and blocks `workspace/` edits and starting the stack.)

## Environment notes
- Developed on Windows (PowerShell, Docker Desktop) and works on Linux/WSL; keep paths relative and cross-platform.
  Don't commit absolute machine paths (e.g. in `backend/config/integrations.yaml`, vault links).
- `backend/` modules import each other as top-level packages (`from domain import ...`); `pytest.ini` sets the path.

## Skills
`/acceptance` (6-step TDD/acceptance protocol) and `/take_ui_screenshot` live in `.claude/skills/`.
For UI changes, review the generated `logs/latest_ui_render.png` before finishing.
