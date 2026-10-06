# Provable

Spec-driven code generation engine: TDD verification loops + DDD architecture. The engine
(`backend/`, `frontend/`) *generates* an app into `workspace/`. Never confuse the two.

## Before you start
- Read `vault/HANDOVER.md` for current architectural state and planned work.
- Read the rule file(s) for your task before editing (full index: `.agents/AGENTS.md`):
  - Architecture, ports, workspace isolation: @.agents/rules/01-architecture-and-meta.md
  - React / PM Studio UI: @.agents/rules/02-frontend-and-ui.md
  - Backend features, tests, DDD layers: @.agents/rules/03-tdd-engine.md
- When you change architecture or the roadmap, update `vault/HANDOVER.md` (and `vault/Home.md` if the index changes).

## Commands
- Install: `pip install -r requirements.txt` and `cd frontend && npm ci` (auto-run in cloud sessions by `.claude/hooks/session_start.sh`)
- Backend tests (fast, ~15s): `python -m pytest backend/tests/`
- Frontend build/typecheck: `cd frontend && npm run build`
- Pre-flight (build + tests + purity lint + live checks): `python scripts/agent_preflight_check.py`.
  Phases 4-6 need the full stack running on :8000/:8001/:5173; phases 1-3 work standalone.
- Run the stack: `python run.py` — the **user** runs this in their own terminal; never start it from the agent.
- Copy `.env.example` to `.env` and set `GEMINI_API_KEY` (or `OPENAI_API_KEY`) for real LLM calls.

## Hard invariants (details in the rule files)
- **`workspace/` is read-only for you** (it is an embedded git repo of generated output). Fix the generator in
  `backend/onboarding/` (`skeleton_builder.py`, `templates/workspace_scaffold.py`) or `backend/prompts/` instead.
- Ports: engine API :8000, PM Studio :5173, generated app API :8001, generated preview :5174, Allure :5050.
- DDD layering: pure domain (no FastAPI/Pydantic/DB) -> repositories -> service layer/UoW -> routers.
  Routers never import `db.store`.
- TDD loop: RED -> GREEN -> WIRE -> VERIFY, done directly (no developer subagents). Don't weaken tests to get green;
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
