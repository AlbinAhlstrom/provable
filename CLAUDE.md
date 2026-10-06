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
- Backend tests (fast, ~20s): `python -m pytest backend/tests/` — hermetic: `conftest.py` points the session at a throwaway workspace and database, so tests never touch the live app's `workspace/` or state (guarded by `test_test_isolation.py`). Safe to run while the app is up.
- Frontend build/typecheck: `cd frontend && npm run build`
- Pre-flight (build + tests + purity lint + live checks): `python scripts/agent_preflight_check.py`.
  Runs without an LLM key (tests mock the LLM). Phases 1-5 work standalone; Phase 6 (UI screenshot) is only
  captured if PM Studio is running on :5173, otherwise it is reported as SKIPPED, which means no visual verification.
- **The agent owns the running app.** In cloud sessions a SessionStart hook starts the full stack (backend :8000, Studio :5173, preview :5174, via `run.py`) if it isn't already up. Before testing anything, check it with `bash .claude/hooks/ensure_app_running.sh` (idempotent); use `--restart` after backend changes that need a clean boot and `--stop` to stop it. Logs: `logs/run.log`; step traces: `logs/trace` (see below). Never launch `run.py` by hand.
- Every pipeline step's input/output is traced to `logs/trace` while the app runs (the launcher sets `PROVABLE_TRACE_DIR`); clear it with `rm -rf logs/trace` before a fresh experiment, then run `python scripts/trace_report.py logs/trace` (`--full N` shows one step). Implemented in `backend/pipeline_trace.py`; API keys are redacted.
- Real LLM calls need `GEMINI_API_KEY` (or `LLM_API_KEY` / `OPENAI_API_KEY`), plus optionally `OPENAI_BASE_URL`, `LLM_MODEL` and `LLM_REASONING_EFFORT` (default `low`; the provider default is ~50x slower and costlier). Locally copy `.env.example` to `.env`; in cloud sessions set them as environment variables in the cloud environment's settings (never paste keys into chat or commit them). Without a key the app still starts, but generation fails loudly.

## Hard invariants (details in the rule files)
- **`workspace/` is read-only for you** (it is an embedded git repo of generated output). Fix the generator in
  `backend/onboarding/` (`skeleton_builder.py`, `templates/workspace_scaffold.py`) or `backend/prompts/` instead.
- Ports: engine API :8000, PM Studio :5173, generated app API :8001, generated preview :5174, Allure :5050.
- DDD layering: pure domain (no FastAPI/Pydantic/DB) -> repositories -> service layer/UoW -> routers.
  Routers never import `db.store`.
- TDD loop: RED -> GREEN -> WIRE -> VERIFY, done directly in the main context (subagents only for read-only research/review). Don't weaken tests to get green;
  if the architecture evolved, rewrite or delete the obsolete test.
- Retries mask errors: at most ONE retry, only when a verifying step rejects a generator's output and its verdict is fed back; never retry provider/parse/infra errors (rule 03 §4).
- Frontend is domain-agnostic: no hardcoded domain terms (Pallet, Pizza, Order...) and no mock UI. Fail loudly.
- Run the full test suite before every commit and the pre-flight check before declaring work done.
  (`.claude/hooks/guard.py` enforces the test run on `git commit`, and blocks `workspace/` edits and starting the stack.)

## Environment notes
- Vercel deployment: `vercel.json` (services `backend` + `frontend`), serverless mode when `VERCEL=1`; see `vault/04-Decisions/ADR-005 Vercel Multi-Service Deployment.md`. Frontend code must use relative `/api/...` URLs, never `http://localhost:8000`.
- Developed on Windows (PowerShell, Docker Desktop) and works on Linux/WSL; keep paths relative and cross-platform.
  Don't commit absolute machine paths (e.g. in `backend/config/integrations.yaml`, vault links).
- `backend/` modules import each other as top-level packages (`from domain import ...`); `pytest.ini` sets the path.

## Skills
`/acceptance` (6-step TDD/acceptance protocol) and `/take_ui_screenshot` live in `.claude/skills/`.
For UI changes, review the generated `logs/latest_ui_render.png` before finishing.

## Generator principles (from the pipeline's design)
- **Root cause only.** If a stage emits bad output, fix the upstream schema, prompt or contract. No post-hoc regex filters or "MUST NOT" prompt patches; if you are tempted, stop and flag it to the user.
- **Typed contracts** between pipeline stages (dataclasses, not loose dicts); **surgical deltas** through `delta_compiler.py` / `cst_isolator.py`; **zero-question kickstart** (the user is the CEO: the pipeline makes opinionated assumptions and never interviews them).
- Pipeline map: COO `prompt_expander.py` -> intent `onboarding/intent.py` -> Analyst `router_engine.py`, `domain_ontology.py` -> Architect `skeleton_builder.py` -> Product Manager `service_layer/services.py` (Living Rule Deck) -> TDD `service_layer/tdd_machine.py` -> Backend `domain_engine_synthesizer.py` -> Frontend `presentation_projection_synthesizer.py`, `frontend_planning_engine.py` -> Styling `styling_synthesizer.py` -> QA `qa_auditor.py`, `qa_gate.py` (bounded rework, `max_rework_attempts=2`).
- Live-LLM "boss fight" tests only on request (`RUN_BOSS_FIGHTS=1` or `-m boss_fight`); the standard suite is offline.
