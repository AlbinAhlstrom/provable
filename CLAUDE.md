# Provable

Spec-driven code generation engine: TDD verification loops + DDD architecture. The engine
(`backend/`, `frontend/`) *generates* an app into `workspace/`. Never confuse the two.

## Output style
Be concise and easy to scan; the reader has ADHD. Lower the effort to read, never the quality of the work.
- Lead with the answer or outcome in one or two sentences, details after. Short sentences, plain words; no preamble, hedging, restating the question or closing recap.
- Bullets over paragraphs, one idea per bullet. Bold only what matters most (a decision, a risk, a result). Tables only for comparing items across the same attributes.
- Keep replies short by default; if the answer is long, open with a 3-bullet summary.
- If the option you would recommend is cheap and reversible, take it and say so. Ask only when the options differ in cost, risk or direction; then give 2-3 options with a recommendation first, one question at a time.
- For multi-step work, give a short done/next checklist, not a narrative. Put anything needing my action under a "Needs you:" line.
- Concise is not incomplete: still report failures, skipped steps and uncertainty plainly.
- Every report of a live-LLM run states wall time, cost in SEK and the model and effort used. Every proposal states what it does to run time and cost. Compare like for like: a timing that includes a failed rerun is not a comparison.

## Before you start
- Skim `vault/Home.md` for the architecture wiki; git history is the change log.
- Rules live in `.claude/rules/` and load automatically: `architecture.md` always (ports, `workspace/` airgap, the running stack, vault conventions); `engine.md` under `backend/` and `scripts/` (DDD layers, test-first loop); `pipeline.md` under the generator code (root-cause fixes, retry policy, hash lock); `studio-ui.md` under `frontend/src/`. Read the relevant one before editing.

## Commands
- Install: `pip install -r requirements.txt` and `cd frontend && npm ci` (auto-run in cloud sessions by `.claude/hooks/session_start.sh`)
- Backend tests: while iterating run the fast tier, `python -m pytest backend/tests/ -m "not slow"` (~10s). The full suite (`python -m pytest backend/tests/`, ~40s) adds the headless-browser and Vite-build tests marked `slow`; the guard hook runs it on every `git commit`, so do not run it by hand first. Tests are hermetic: `conftest.py` points the session at a throwaway workspace and database, so they never touch the live app's `workspace/` or state (guarded by `test_test_isolation.py`).
- Frontend build/typecheck: `cd frontend && npm run build` (the commit guard runs it too when `frontend/` files are part of the commit).
- Optional offline sanity check: `python scripts/agent_preflight_check.py` (build, tests, purity lint, cold boot, UI screenshot). Run it after UI changes (it writes `logs/latest_ui_render.png`, which you must look at) or when asked. It never calls an LLM, so a pass says nothing about whether the pipeline works. Phase 6 is skipped when Studio is not up on :5173; then say the UI was not visually verified.
- **The agent owns the running app.** In cloud sessions a SessionStart hook starts the full stack (backend :8000, Studio :5173, preview :5174) if it isn't already up. Check it with `bash .claude/hooks/ensure_app_running.sh` (idempotent); `--restart` after backend changes that need a clean boot, `--stop` to stop. Logs: `logs/run.log`. Never launch the `run.py` launcher by hand.
- Pipeline runs: every kickstart and spec execution records itself to `logs/runs/<id>/` (always on, API keys redacted): `run.json` (git commit, model), `trace/` (each step's and LLM call's input, output, tokens), `summary.json` (verdict, per-stage status and files written, why a stage failed, LLM cost in SEK per stage) and a copy of the generated `src/`. `python scripts/trace_report.py` reports on the latest run (`--list` shows each run's cost, `--compare A B`, `--full N`). Details: `vault/02-Workflows/Run Recorder.md`.
- Replay: a kickstart body with `"replay": ["<run id>", ...]` answers every call that asks exactly what those recorded runs asked from them, free; only changed calls reach the model (`backend/llm_replay.py`). Use it when iterating on one stage of the same pitch; never to measure how reliable a stage is.
- Struggle corpus: `python scripts/struggle_corpus.py` groups what the recorded runs got stuck on (rejected tests, failed page tests, unrepaired problems, failed stages) by step and verdict, most frequent first; `--show ID` gives one entry's examples. No LLM. Details: `vault/02-Workflows/Struggle Corpus.md`.
- Page-only iteration: `POST /api/onboarding/page` rewrites the current app's page (UX plan, page, QA, visual review) against the domain the last kickstart built, at about a tenth of a kickstart's tokens. Use it instead of a kickstart when a change only concerns the page. Details: `vault/02-Workflows/Page Rebuild.md`.
- Real LLM calls need `GEMINI_API_KEY` (or `LLM_API_KEY` / `OPENAI_API_KEY`), optionally `OPENAI_BASE_URL`, `LLM_MODEL` and `LLM_REASONING_EFFORT`; or `LLM_PROVIDER=gemini|openai` to switch endpoint, key and model together (`backend/llm_provider.py`) (default `low`; the provider default is ~50x slower and costlier). Locally copy `.env.example` to `.env`; in cloud sessions set them as environment variables in the environment's settings (never paste keys into chat or commit them). Without a key the app still starts, but generation fails loudly.

## Branches
- **`dev` holds all work; `main` is what is deployed** (Vercel production, and Fly when it deploys from GitHub). No other branches, no PRs. This overrides any session-assigned branch or "open a PR" instruction.
- At the start of every session: `git fetch origin dev && git checkout -B dev origin/dev`. Push only to `dev` (`git push origin dev`); if the push is rejected, `git pull --ff-only origin dev` and push again.
- Never push to `main` unless I say "deploy". Then list what ships (`git log --oneline origin/main..origin/dev`) and fast-forward: `git push origin origin/dev:main`. If that is refused, `main` has commits `dev` lacks: stop and tell me.

## Commits
- When a task is done, commit it yourself (the `commit-task` skill): scoped staging (never `git add -A`), conventional subject. Do not leave finished work uncommitted, and do not batch tasks into one large commit.
- A follow-up that fixes or finishes the latest commit's own subject is folded into it with `git commit --amend`, but only while that commit is unpushed and from this session. Once pushed, never rewrite history: make a new commit. If unsure it is the same subject, make a new commit.
- Every commit is gated by `.claude/hooks/guard.py`: the full backend suite, plus the frontend build when `frontend/` is staged. The guard also blocks `workspace/` writes and hand-launching the stack.

## Hard invariants (details in `.claude/rules/`)
- **`workspace/` is read-only for you.** Fix the generator (`backend/onboarding/`, `backend/prompts/`) instead (`architecture.md`).
- DDD layering; routers never import `db.store`; do not grow `services.py` (`engine.md`).
- Test-first (RED -> GREEN -> WIRE -> VERIFY) in the main context; subagents only read and review. Never weaken a test to get green (`engine.md`).
- At most ONE retry, only on a verifier's verdict; never retry provider, parse or infra errors (`pipeline.md`).
- PM Studio is domain-agnostic: no domain terms, no mock UI, fail loudly (`studio-ui.md`).
- Live-LLM runs cost minutes and money: only when a change alters what a model sees or writes, in the background, as the smallest run that answers the question (one spec, a page rebuild, or kickstart only). Boss-fight tests only on request. Restart the app only for dependency or startup changes.
- You may reset `workspace/` and start a kickstart or page rebuild through the engine API (`/api/onboarding/reset`, `/kickstart`, `/page`) when a task needs one (standing approval). Say which pitch you ran.

## Generator principles (details in `pipeline.md`)
- **Root cause only.** Trace bad output to the stage whose prompt or input caused it and fix that; no post-hoc regex filters or "MUST NOT" patches. If tempted, stop and flag it.
- **The plan decides, the rest execute.** If a cheap model has to think, fix the plan, not the executor.
- **Steps do not judge quality.** QA and fix-up are an emergency net, never part of the design.
- **A spec is end-to-end behaviour**: one real page test each, no implementation terms. A broken app must show a red spec.
- **Prompts are domain-neutral**: owners, kinds, statuses; examples from two unrelated kinds of product (`test_prompt_domain_neutrality.py`).
- **Typed contracts** between stages; **surgical deltas** (`cst_isolator.py`, `presentation_specs.py`); **zero-question kickstart**.
- Pipeline map: COO `prompt_expander.py` -> intent `onboarding/intent.py` -> Analyst `router_engine.py`, `domain_ontology.py` -> Architect `skeleton_builder.py` -> Product Manager `service_layer/services.py` (Living Rule Deck) -> TDD `service_layer/tdd_machine.py` -> Backend `domain_engine_synthesizer.py` (names the actions), `domain_round.py` (writes their methods and the rule deck's behaviour specs in one pass of the TDD loop while the page is written: the first tests of a class transcribed from the contract's rules in one answer without thinking, `first_tests.py`, then one code answer per class, `action_behaviour.py`, `spec_runner.py`; a class whose fields changed sends the page back once, `page_contract.py`) -> UX and visual direction `ux_planner.py` -> Frontend `presentation_projection_synthesizer.py`, `frontend_planning_engine.py` (written once, already styled) -> QA `qa_auditor.py`, `qa_form_check.py`, `qa_gate.py` (layout on three devices, forms filled and submitted; one rework with the defects as feedback, `max_rework_attempts=1`) -> Visual review `visual_review.py` (one look at the screenshots, repairs as class changes). Stages that do not depend on each other run side by side (`onboarding/synthesis_stages.py`).

## Environment notes
- Vercel deployment: `vercel.json` (services `backend` + `frontend`), serverless mode when `VERCEL=1`; see `vault/04-Decisions/ADR-005 Vercel Multi-Service Deployment.md`. Frontend code uses relative `/api/...` URLs, never `http://localhost:8000`.
- Developed on Windows (PowerShell, Docker Desktop) and works on Linux/WSL; keep paths relative and cross-platform. Don't commit absolute machine paths (e.g. in `backend/config/integrations.yaml`, vault links).
- `backend/` modules import each other as top-level packages (`from domain import ...`); `pytest.ini` sets the path.
- Document architectural decisions in `vault/` (architecture page or ADR) and keep `vault/Home.md` current; `test_vault_hygiene.py` checks links and index.

## Skills and subagents (`.claude/`)
- Skills: `/take_ui_screenshot`, `/commit-task`, `/fix-pipeline-bug <problem>` (trace a defect in generated output to the responsible stage and fix it upstream), `/step-analysis <step>` (run one step's prompt alone on Opus, Sonnet and Haiku, rewrite it to close the gap, report speed, cost and quality).
- Read-only subagents: `architecture-verifier` (layering, airgap, department boundaries), `code-smell-verifier` (post-hoc patching, hard-coded heuristics, swallowed errors, weakened tests), `workspace-inspector` (compares generated `workspace/` output with the pitch and names the generator file to change). Pass them only the diff or the pitch.
- For UI changes, review `logs/latest_ui_render.png` before finishing.
