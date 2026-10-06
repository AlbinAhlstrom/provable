# Provable

Provable turns a CEO-style pitch into a verified full-stack app through a pipeline of "departments".
This repo is the **engine** plus a **meta-codebase**: `workspace/` holds the app the engine generated.
Reading `workspace/` and comparing it with the ideal output is how we find upstream bugs.

## Hard rules

1. **Airgap.** `workspace/` is written only by the engine (`backend/onboarding/`, `backend/service_layer/`).
   NEVER edit, create, delete, commit or `npm install` inside it. Fix the generator, templates or prompts, then regenerate.
   Reading is encouraged. Enforced by `.claude/settings.json` + `scripts/claude_hooks/workspace_guard.py`; a blocked call halts the run.
2. **Root cause only.** If a stage emits bad output, fix the upstream schema, prompt or contract.
   No post-hoc regex filters, no "MUST NOT" prompt patches. If you are tempted, stop and flag it to the user.
3. **Pure DDD** in generated domain code (`workspace/src/domain/`): plain dataclasses, no `fastapi`/`pydantic`/`sqlalchemy` imports,
   mutation only through domain methods. Non-default fields precede default fields.
4. **Typed contracts** between departments (dataclasses, not loose dicts).
5. **Surgical deltas.** Spec edits go through `delta_compiler.py` / `cst_isolator.py`; never rewrite unrelated code.
6. **Zero-question kickstart.** The user is the CEO; the pipeline makes opinionated assumptions and never interviews them.
7. **PM Studio (`frontend/src/`) is a domain-agnostic projection** of the OpenAPI schema: no hard-coded domain terms, fail loudly
   (empty state or red ErrorBoundary), never fake the UI to turn a test green.

## Commands

- Stack: the user runs `python run.py` in their own terminal (it installs dependencies itself). Never start it from a session:
  its reloaders restart services mid-turn. Ports: engine 8000/5173, generated app 8001/5174.
- Fast tests: `python -m pytest backend/tests/unit` (hermetic, offline, LLM mocked in `backend/tests/conftest.py`).
- Full suite: `python -m pytest backend/tests/`. Live-LLM "boss fights" only on request: `RUN_BOSS_FIGHTS=1` or `-m boss_fight`.
- Layer-leak check (must print nothing): `grep -rn "import db.store" backend/entrypoints/routers backend/service_layer/services.py`
- Frontend changes: `npm run build` in `frontend/`, then review the rendered UI.

## Workflow

- Engine changes are test-first: failing test in `backend/tests/unit/test_<target>.py` (use `FakeUnitOfWork`), implement, wire the router,
  then the full suite. Never weaken assertions to get green. If the architecture moved on, rewrite or delete the obsolete test.
- **Commits (standing instruction):** when a task is finished and the tests are confirmed green, commit it without being asked.
  Stage only the files that task touched (the tree usually holds unrelated uncommitted work, so never `git add -A`) and use a
  conventional subject (`feat|fix|test|docs|chore(scope): ...`). A later fix on the same subject goes into that commit with
  `git commit --amend`, but only while it is the latest commit, carries a `Claude-Session` trailer, and is unpushed;
  otherwise make a new commit. Never push, never amend someone else's commit. Run the full suite first; cloud sessions cannot,
  so they commit after the user confirms green.
- The pipeline's own build loop is test-first too: generated code goes RED -> GREEN against hash-locked tests
  (`service_layer/tdd_machine.py`: `compute_test_file_hash`, `verify_test_file_integrity`). Never weaken tests during GREEN.
- `scripts/agent_preflight_check.py` Phase 4 now runs against a throwaway workspace + DB with the LLM off (it used to POST
  `/api/onboarding/reset` at the real ones). Until the user confirms one clean run, do not run preflight yourself.
- The engine DB lives at `<workspace>/requirements/provable.db`, so wiping or resetting `workspace/` also resets engine state.
- Current state and open decisions (kept short; the long history is `vault/HANDOVER-archive.md`, read it only when needed).
  Update it at wrap-up when architectural decisions or roadmap items changed:

@vault/HANDOVER.md

## Pipeline map (engine files)

COO `prompt_expander.py` -> Analyst `router_engine.py`, `domain_ontology.py` -> Architect `skeleton_builder.py` ->
Product Manager `service_layer/services.py` (Living Rule Deck) -> Delta Compiler `delta_compiler.py`, `cst_isolator.py` ->
Backend `domain_engine_synthesizer.py` -> Frontend `presentation_projection_synthesizer.py`, `frontend_planning_engine.py` ->
Styling `styling_synthesizer.py` -> QA `qa_auditor.py`, `qa_gate.py` (bounded rework, `max_rework_attempts=2`).
Each department decides only its own concern (the Analyst never decides file layout, the Architect never decides business rules, etc.).

More detail: `vault/Home.md` (index), `vault/01-Architecture/`, `.agents/domain_ontology.yaml`.
Specialised rules load from `.claude/rules/` when matching files are touched. Review with the `architecture-verifier` and
`code-smell-verifier` subagents, inspect generated output with `workspace-inspector`, and use the skills `acceptance`,
`fix-pipeline-bug` and `commit-task`. Install this configuration with `python scripts/claude_setup/install.py`.

## Working agreement

- Flag suspected anti-patterns when you see them (post-hoc regex patching, negative-prompt patches, duplicated helpers,
  swallowed exceptions, oversized files, hard-coded domain heuristics) and let the user decide how to handle them.
- Suggest automating any flow we repeat (skill, slash command, hook, or subagent) as soon as the second repetition happens.
- Record lessons from fixed bug classes as one-line additions to this file, proposed to the user first.
- End every response with `[🛡️ Clanker Active]` (checked by the Stop hook).
