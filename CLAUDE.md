# Provable

Spec-driven code generation engine: TDD verification loops + DDD architecture. The engine
(`backend/`, `frontend/`) *generates* an app into `workspace/`. Never confuse the two.

## Output style
Be concise and easy to scan; the reader has ADHD. Lower the effort to read, never the quality of the work.
- Lead with the answer or outcome in one or two sentences, details after. Short sentences, plain words; no preamble, hedging, restating the question or closing recap.
- Bullets over paragraphs, one idea per bullet. Bold only what matters most (a decision, a risk, a result). Tables only for comparing items across the same attributes.
- Keep replies short by default; if the answer is long, open with a 3-bullet summary.
- When asking me to decide, give 2-3 options with a recommendation first, and ask one question at a time.
- For multi-step work, give a short done/next checklist, not a narrative. Put anything needing my action under a "Needs you:" line.
- Concise is not incomplete: still report failures, skipped steps and uncertainty plainly.

## Before you start
- Skim `vault/Home.md` for the architecture wiki; git history is the change log.
- Rules live in `.claude/rules/` and load automatically: `architecture.md` always (ports, `workspace/` airgap, the running stack, vault conventions); `engine.md` under `backend/` and `scripts/` (DDD layers, test-first loop); `pipeline.md` under the generator code (root-cause fixes, retry policy, hash lock); `studio-ui.md` under `frontend/src/`. Read the relevant one before editing.

## Commands
- Install: `pip install -r requirements.txt` and `cd frontend && npm ci` (auto-run in cloud sessions by `.claude/hooks/session_start.sh`)
- Backend tests: while iterating run the fast tier, `python -m pytest backend/tests/ -m "not slow"` (~10s). The full suite (`python -m pytest backend/tests/`, ~40s) adds the headless-browser and Vite-build tests marked `slow`; the guard hook runs it on every `git commit`, so do not run it by hand first. Tests are hermetic: `conftest.py` points the session at a throwaway workspace and database, so they never touch the live app's `workspace/` or state (guarded by `test_test_isolation.py`).
- Frontend build/typecheck: `cd frontend && npm run build` (the commit guard runs it too when `frontend/` files are part of the commit).
- Optional offline sanity check: `python scripts/agent_preflight_check.py` (build, tests, purity lint, cold boot, UI screenshot). Run it after UI changes (it writes `logs/latest_ui_render.png`, which you must look at) or when asked. It never calls an LLM, so a pass says nothing about whether the pipeline works. Phase 6 is skipped when Studio is not up on :5173; then say the UI was not visually verified.
- **The agent owns the running app.** In cloud sessions a SessionStart hook starts the full stack (backend :8000, Studio :5173, preview :5174) if it isn't already up. Check it with `bash .claude/hooks/ensure_app_running.sh` (idempotent); `--restart` after backend changes that need a clean boot, `--stop` to stop. Logs: `logs/run.log`. Never launch the `run.py` launcher by hand.
- Pipeline runs: every kickstart and spec execution records itself to `logs/runs/<id>/` (always on, API keys redacted): `run.json` (git commit, model), `trace/` (each step's and LLM call's input, output, tokens), `summary.json` (verdict, per-stage status and files written, why a stage failed) and a copy of the generated `src/`. `python scripts/trace_report.py` reports on the latest run (`--list`, `--compare A B`, `--full N`). Details: `vault/02-Workflows/Run Recorder.md`.
- Real LLM calls need `GEMINI_API_KEY` (or `LLM_API_KEY` / `OPENAI_API_KEY`), optionally `OPENAI_BASE_URL`, `LLM_MODEL` and `LLM_REASONING_EFFORT` (default `low`; the provider default is ~50x slower and costlier). Locally copy `.env.example` to `.env`; in cloud sessions set them as environment variables in the environment's settings (never paste keys into chat or commit them). Without a key the app still starts, but generation fails loudly.

## Commits
- When a task is done, commit it yourself (the `commit-task` skill): scoped staging (never `git add -A`), conventional subject. Do not leave finished work uncommitted, and do not batch tasks into one large commit.
- A follow-up that fixes or finishes the latest commit's own subject is folded into it with `git commit --amend`, but only while that commit is unpushed and from this session. Once pushed, never rewrite history: record the follow-up as `git commit --fixup=<sha>` and let the PR squash. If unsure it is the same subject, make a new commit.
- Every commit is gated by `.claude/hooks/guard.py`: the full backend suite, plus the frontend build when `frontend/` is staged. The guard also blocks `workspace/` writes and hand-launching the stack.

## Hard invariants (details in `.claude/rules/`)
- **`workspace/` is read-only for you** (an embedded git repo of generated output). Fix the generator in `backend/onboarding/` (`skeleton_builder.py`, `templates/workspace_scaffold.py`) or `backend/prompts/` instead.
- DDD layering: pure domain -> repositories -> service layer/UoW -> routers. Routers never import `db.store`. Do not grow `services.py`; new pipeline logic goes in `backend/onboarding/`.
- Test-first (RED -> GREEN -> WIRE -> VERIFY), done directly in the main context; subagents only for read-only research and review. Don't weaken tests to get green; if the architecture evolved, rewrite or delete the obsolete test.
- Retries mask errors: at most ONE retry, only when a verifying step rejects a generator's output and its verdict is fed back; never retry provider, parse or infra errors (`pipeline.md`).
- Frontend (PM Studio) is domain-agnostic: no hardcoded domain terms and no mock UI. Fail loudly.
- Live-LLM runs (kickstart, spec execution) take minutes and cost money: do them only when a change alters what a model sees or writes, in the background, and as the smallest run that answers the question (one spec, or kickstart only), never the whole pipeline by reflex. Live-LLM "boss fight" tests only on request (`RUN_BOSS_FIGHTS=1` or `-m boss_fight`); the standard suite is offline. Restart the app only for dependency or startup changes; hot reload covers the rest.

## Generator principles
- **Root cause only.** If a stage emits bad output, fix the upstream schema, prompt or contract. No post-hoc regex filters or "MUST NOT" prompt patches; if you are tempted, stop and flag it to the user.
- **Typed contracts** between pipeline stages (dataclasses, not loose dicts); **surgical deltas** through `cst_isolator.py` (behaviour specs) and `presentation_specs.py` (presentation specs: one view, proved by a build); **zero-question kickstart** (the user is the CEO: the pipeline makes opinionated assumptions and never interviews them).
- Pipeline map: COO `prompt_expander.py` -> intent `onboarding/intent.py` -> Analyst `router_engine.py`, `domain_ontology.py` -> Architect `skeleton_builder.py` -> Product Manager `service_layer/services.py` (Living Rule Deck) -> TDD `service_layer/tdd_machine.py` -> Backend `domain_engine_synthesizer.py` (names the actions), `action_behaviour.py` (writes their methods through the TDD loop before the page is written) -> UX and visual direction `ux_planner.py` -> Frontend `presentation_projection_synthesizer.py`, `frontend_planning_engine.py` (written once, already styled) -> QA `qa_auditor.py`, `qa_form_check.py`, `qa_gate.py` (layout on three devices, forms filled and submitted; one rework with the defects as feedback, `max_rework_attempts=1`) -> Visual review `visual_review.py` (one look at the screenshots, repairs as class changes). Stages that do not depend on each other run side by side (`onboarding/synthesis_stages.py`).

## Environment notes
- Vercel deployment: `vercel.json` (services `backend` + `frontend`), serverless mode when `VERCEL=1`; see `vault/04-Decisions/ADR-005 Vercel Multi-Service Deployment.md`. Frontend code uses relative `/api/...` URLs, never `http://localhost:8000`.
- Developed on Windows (PowerShell, Docker Desktop) and works on Linux/WSL; keep paths relative and cross-platform. Don't commit absolute machine paths (e.g. in `backend/config/integrations.yaml`, vault links).
- `backend/` modules import each other as top-level packages (`from domain import ...`); `pytest.ini` sets the path.
- Document architectural decisions in `vault/` (architecture page or ADR) and keep `vault/Home.md` current; `test_vault_hygiene.py` checks links and index.

## Skills and subagents (`.claude/`)
- Skills: `/acceptance` (6-step acceptance protocol), `/take_ui_screenshot`, `/commit-task`, `/fix-pipeline-bug <problem>` (trace a defect in generated output to the responsible stage and fix it upstream).
- Read-only subagents: `architecture-verifier` (layering, airgap, department boundaries), `code-smell-verifier` (post-hoc patching, hard-coded heuristics, swallowed errors, weakened tests), `workspace-inspector` (compares generated `workspace/` output with the pitch and names the generator file to change). Pass them only the diff or the pitch.
- For UI changes, review `logs/latest_ui_render.png` before finishing.
