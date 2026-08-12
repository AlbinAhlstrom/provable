# Project Rules

## workspace/ is strictly off-limits (No Bandages Invariant)

The `workspace/` directory contains the application produced by the automated generation pipeline.
**NEVER directly write, edit, patch, or commit files inside `workspace/`.**

Any structural, template, or configuration change meant for `workspace/` MUST be implemented in the authoritative backend generator code (`backend/onboarding/dynamic_domain_generator.py`, `backend/main.py`, `backend/prompts/ui_generation.md`). Editing `workspace/` files directly is an unacceptable band-aid that will immediately be overwritten when the pipeline runs.

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

## Requirements-Driven TDD Architecture
When modifying the application codebase or writing developer agent iterations:
1. **SQLite DataStore**: Always read and update requirements, test cases, and runs via `backend/db/store.py` (which wraps SQLite `provable.db`) rather than legacy JSON files.
2. **StrictDoc Sync**: Requirements are version-controlled inside the git repository under `workspace/requirements/requirements.sdoc`. Updates to requirements database models must trigger the bidirectional sync hook `export_sdoc()` to keep spec files aligned.
3. **TDD Flow Execution**: Every feature task must begin by generating a failing BDD test case (`workspace/tests/test_{req_id}.py`) containing `@allure` metadata and BDD step docstrings (`Given/When/Then`).
4. **Allure Matrix**: All test results must be published to the containerized Allure service on port `5050` (`frankescobar/allure-docker-service`) to update the coverage metrics seen in the frontend.
5. **OpenAI SDK & Templates**: All LLM queries must route through the OpenAI Python client using configurations inside `backend/config/models.yaml` and load system prompts dynamically from `backend/prompts/` Markdown templates.
6. **Agent Log Inspection**: When debugging why a developer agent loop failed or is stuck, inspect the logs under `backend/logs/{ticket_id}.log`. The full LangGraph orchestration execution log, LLM request/response prompts, visual QA screenshot status, and pytest command stderr output are all written here.
7. **DDD Architecture Enforcement & TDD Subagent Rules**:
   - **Layer Boundaries**: `Domain Model` (`backend/domain/`) $\rightarrow$ `Repository Pattern` (`backend/adapters/`) $\rightarrow$ `Service Layer / Unit of Work` (`backend/service_layer/`) $\rightarrow$ `Presentation Routers` (`backend/entrypoints/routers/`).
   - **Entrypoint Isolation**: API Route handlers (`backend/entrypoints/routers/*.py`) MUST NEVER import `db.store` directly. Every route handler MUST delegate to `services.<use_case>(uow=SqliteUnitOfWork())`.
   - **Pure Domain**: Domain dataclasses (`backend/domain/model.py`) MUST have ZERO FastAPI, Pydantic, or DB dependencies.
   - **Concurrency Limit**: Launch at most 2–3 subagents in parallel to prevent API quota rate-limit exhaustion.
   - **4-Step Execution Workflow**:
     1. **RED**: Write unit test in `backend/tests/unit/test_<target>.py` using `FakeUnitOfWork` and `FakeWorkspaceAdapter`. Run ONLY `python -m pytest backend/tests/unit/test_<target>.py` and verify failure.
     2. **GREEN**: Implement `domain/model.py`, `service_layer/services.py`, and `messagebus.py`. Run targeted unit pytest, verify pass in `<0.5s`.
     3. **WIRE**: Implement concrete repositories/UoW and update target `routers/<router>.py`.
     4. **VERIFY**: Run full test suite `python -m pytest backend/tests/` and verify ZERO `import db.store` matches across BOTH routers and service layer (`grep -rn "import db.store" backend/entrypoints/routers/ backend/service_layer/services.py`).

## Task Completion & Git Commit Invariant
- **Completion Commitment**: Every developer task or milestone MUST end with a clean git commit capturing the completed work.
- **Commit Amending Rule**: If an immediate follow-up fix or adjustment is made for work that was just committed, ALWAYS append/amend the changes to the same commit (`git commit --amend --no-edit` or `git commit --amend -m "..."`) so the commit log remains clean without fragmented fix commits.

## Strict Zero-Hardcoding & Universal Dynamic Synthesis Invariant

**NEVER hardcode domain-specific strings, mock items, or pitch-conditional branches in backend generator code.**
- The core purpose of Provable is 100% dynamic, prompt-agnostic generation for any arbitrary user prompt (e.g. quantum physics labs, pizza shops, pet grooming, drone logistics, or space stations).
- **Prohibited**: Checking for specific pitch keywords (e.g., `if "pizza" in pitch: ...` or `if "bakery" in pitch: ...`) or inserting hardcoded mock product items (e.g., `"Margherita Speciale"`) inside compiler or generator templates.
- **Enforced Strategy**: All entity attributes, catalog offerings, headers, mock items, and components MUST be synthesized dynamically via the LLM pipeline (`call_gemini` / schema extractors) or constructed using prompt-agnostic AST metadata transformers (`manifest.intent.domain_name`, `manifest.business_pitch`).

