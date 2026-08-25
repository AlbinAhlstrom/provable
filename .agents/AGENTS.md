# Project Rules

## workspace/ is strictly off-limits (No Bandages Invariant)

The `workspace/` directory contains the application produced by the automated generation pipeline.
**NEVER directly write, edit, patch, or commit files inside `workspace/`.**

Any structural, template, or configuration change meant for `workspace/` MUST be implemented in the authoritative backend generator code (`backend/onboarding/skeleton_builder.py`, `backend/main.py`, `backend/prompts/ui_generation.md`). Editing `workspace/` files directly is an unacceptable band-aid that will immediately be overwritten when the pipeline runs.

You may:
- Read `workspace/` files to **diagnose** runtime/build errors or inspect generated output.
- Run `git log`, `git status`, `git diff` inside `workspace/` for inspection only.

You must NOT:
- Edit or create any files directly inside `workspace/` (always edit generator templates in `backend/` instead).
- Run `git add`, `git commit`, `git revert`, or `git reset` inside `workspace/`.

## Headless Chrome & Selenium
When executing headless Chrome or Selenium automation in containerized remote environments or headless hosts:
- Always include the `--disable-gpu` and `--remote-debugging-port=9222` options in the webdriver initialization arguments to prevent `DevToolsActivePort` initialization failures.

## Obsidian Vault Documentation & Handover Continuity
Maintain a well-structured Obsidian vault under the `vault/` directory in the root of the project. Whenever adding, modifying, or deleting features, update the corresponding documentation:
- Keep the `vault/Home.md` index file up-to-date.
- Read relevant files in `vault/` during the research phase of a task to understand system context and existing architecture.
- **Cross-Chat Handover Invariant**: At the start of EVERY chat session or task, read `vault/HANDOVER.md` to restore full architectural state, active context, and planned unexecuted work items.
- **Session Wrap-Up Invariant**: At the conclusion of any task where architectural decisions or roadmap items are planned/modified, update `vault/HANDOVER.md` so future agents and chats pick up seamlessly.
- Document architectural changes under `vault/01-Architecture/`.
- Document new agent behaviors or workflow changes under `vault/02-Workflows/`.
- Use standard double-bracket internal links (e.g. `[[System Architecture]]`) to link related concepts.

## Starting the Application Stack
When initializing the workspace services for coding, testing, or review tasks:
1. **Ensure Docker Desktop is running** on the Windows host.
2. **Start the Allure Dashboard container**:
   ```powershell
   docker compose -f docker-compose.allure.yaml up -d
   ```

## Application Stack Execution Invariant
**NEVER execute `python run.py` via `run_command` in background tasks.**
Executing `python run.py` spawns long-lived WatchFiles reloader processes that trigger system restarts, interrupting the agent's turn and breaking the chat session. The user manages `python run.py` in their own terminal session, while Uvicorn and Vite handle hot-module-reloading (HMR) automatically whenever code edits are made.

### Requirements-Driven TDD Architecture
When modifying the application codebase or writing developer agent iterations:
1. **SQLite DataStore**: Always read and update requirements, test cases, and runs via `backend/db/store.py` (which wraps SQLite `provable.db`) rather than legacy JSON files.
2. **StrictDoc Sync**: Requirements are version-controlled inside the git repository under `workspace/requirements/requirements.sdoc`. Updates to requirements database models must trigger the bidirectional sync hook `export_sdoc()` to keep spec files aligned.
3. **TDD Flow Execution**: Every feature task must begin by generating a failing BDD test case (`workspace/tests/test_{req_id}.py`) containing `@allure` metadata and BDD step docstrings (`Given/When/Then`).
4. **Allure Matrix**: All test results must be published to the containerized Allure service on port `5050` (`frankescobar/allure-docker-service`) to update the coverage metrics seen in the frontend.
5. **OpenAI SDK & Templates**: All LLM queries must route through the OpenAI Python client using configurations inside `backend/config/models.yaml` and load system prompts dynamically from `backend/prompts/` Markdown templates.
6. **Agent Log Inspection**: When debugging why a developer agent loop failed or is stuck, inspect the logs under `backend/logs/{ticket_id}.log`. The full LangGraph orchestration execution log, LLM request/response prompts, visual QA screenshot status, and pytest command stderr output are all written here.
7. **DDD Architecture Enforcement & Mandatory 4-Step TDD Workflow (No Subagents)**:
   - **No Developer Subagent Invariant**: DO NOT invoke developer subagents (like `tdd-developer` or `self`) for code edits. Perform all coding, testing, and debugging directly in the main conversation context.
   - **Layer Boundaries**: `Domain Model` (`backend/domain/`) $ightarrow$ `Repository Pattern` (`backend/adapters/`) $ightarrow$ `Service Layer / Unit of Work` (`backend/service_layer/`) $ightarrow$ `Presentation Routers` (`backend/entrypoints/routers/`).
   - **Entrypoint Isolation**: API Route handlers (`backend/entrypoints/routers/*.py`) MUST NEVER import `db.store` directly. Every route handler MUST delegate to `services.<use_case>(uow=SqliteUnitOfWork())`.
   - **Pure Domain**: Domain dataclasses (`backend/domain/model.py`) MUST have ZERO FastAPI, Pydantic, or DB dependencies.
   - **Mandatory 4-Step TDD Execution Workflow**:
     1. **RED**: Write unit test in `backend/tests/unit/test_<target>.py` using `FakeUnitOfWork` and `FakeWorkspaceAdapter`. Run ONLY `python -m pytest backend/tests/unit/test_<target>.py` and verify failure.
     2. **GREEN**: Implement `domain/model.py`, `service_layer/services.py`, and `messagebus.py`. Run targeted unit pytest, verify pass in `<0.5s`.
     3. **WIRE**: Implement concrete repositories/UoW and update target `routers/<router>.py`.
     4. **VERIFY**: Run full test suite `python -m pytest backend/tests/` and verify ZERO `import db.store` matches across BOTH routers and service layer (`grep -rn "import db.store" backend/entrypoints/routers/ backend/service_layer/services.py`).

## Task Completion & Git Commit Invariant
- **Pre-Commit Full Test Suite Invariant**: **NEVER execute `git commit` or `git commit --amend` without running the full test suite (`python -m pytest backend/tests/`) first.** Every commit MUST be preceded by empirical runtime verification showing 100% PASS across both unit (`backend/tests/unit/`) and E2E (`backend/tests/e2e/`) test suites to strictly prevent regressions.
- **Completion Commitment**: Every developer task or milestone MUST end with a clean git commit capturing the completed work.
- **Commit Amending Rule**: If an immediate follow-up fix or adjustment is made for work that was just committed, ALWAYS append/amend the changes to the same commit (`git commit --amend --no-edit` or `git commit --amend -m "..."`) so the commit log remains clean without fragmented fix commits.

## Bug Reproduction & Tri-Service Stack Invariant
- **Automated Regression Test Invariant**: Whenever any runtime bug, startup issue, compilation error, or preview connectivity failure is encountered, agents MUST write or update an automated integration test (e.g. `backend/tests/integration/test_app_startup_and_preview_connectivity.py`) ensuring full test coverage and preventing regressions.
- **Tri-Service Live Stack Invariant**: All three core application stack services MUST remain fully scaffolded, configured, and compilable:
  1. `FastAPI Backend API` (`:8000`): Pure DDD service layer and REST endpoints.
  2. `PM Studio Frontend` (`:5173`): React 18 / Vite interface in `frontend/`.
  3. `Workspace Live Preview` (`:5174`): React 18 / Vite sandbox application in `workspace/` with complete `package.json`, `tsconfig.json`, and `vite.config.ts`.
- **Automated Dependency & Scaffold Guarantee**: `run.py` and workspace scaffold generators MUST verify that `workspace/node_modules/vite` and required TypeScript configs are present on disk before launching dev servers to prevent connection refused errors.
- **E2E Dynamic Projection & Directory Isolation Invariant**: All E2E tests strictly reside under `backend/tests/e2e/` (e.g., `backend/tests/e2e/test_ui_dynamic_projection.py` testing The Gibberish Strategy), while `backend/tests/unit/` strictly contains fast (<0.5s) unit tests using `FakeUnitOfWork`.

## STRICT INVARIANTS & ANTI-REGRESSION
- **FRONTEND PURITY**: The frontend is domain-agnostic. You are strictly forbidden from hardcoding specific domain entities (like Pallet, Zone, Pizza, User, Order) into React components. All domain data MUST flow dynamically from the OpenAPI schema or API responses.
- **ZERO-MOCK TOLERANCE**: You are strictly forbidden from hardcoding static UI elements (e.g., product cards, carts, specific domain data) to bypass rendering issues. Real LLM calls route to OpenAI/Gemini SDK.
- **FAIL LOUDLY**: If a dynamic schema (OpenAPI/JSON) fails to render in the frontend, you must render an empty state or a red `<ErrorBoundary>` with the technical error. You must never resurrect legacy code or fake the UI to make a test pass visually.
- **TEST EVOLUTION OVER REGRESSION**: If a test fails because the fundamental architecture or Bounded Context has evolved (e.g., moving from static UI to schema-driven UI), you must DELETE OR REWRITE THE TEST. You are strictly forbidden from reverting architectural progress or hardcoding data just to turn a failing legacy test green.
- **5-LINE HASH LOCK**: Test integrity during TDD GREEN phase is enforced via SHA-256 cryptographic hashing (`compute_test_file_hash` / `verify_test_file_integrity`).
