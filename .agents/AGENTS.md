# Project Rules

## workspace/ is off-limits

The `workspace/` directory contains the application being built by the developer agents.
**Never directly read, write, edit, or commit files inside `workspace/`.**

All changes to `workspace/` must be made exclusively by the automated developer agent (the `run_openhands_loop` pipeline), which generates code via Gemini, runs tests, and commits on the appropriate ticket branch.

You may:
- Read `workspace/` files to **diagnose** agent failures
- Run `git log`, `git status`, `git diff` inside `workspace/` for inspection only

You must NOT:
- Edit any files inside `workspace/`
- Run `git add`, `git commit`, `git revert`, or `git reset` inside `workspace/`

## Headless Chrome & Selenium
When executing headless Chrome or Selenium automation in containerized remote environments or headless hosts:
- Always include the `--disable-gpu` and `--remote-debugging-port=9222` options in the webdriver initialization arguments to prevent `DevToolsActivePort` initialization failures.

## Obsidian Vault Documentation
Maintain a well-structured Obsidian vault under the `vault/` directory in the root of the project. Whenever adding, modifying, or deleting features, update the corresponding documentation:
- Keep the `vault/Home.md` index file up-to-date.
- Read relevant files in `vault/` during the research phase of a task to understand system context and existing architecture.
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
3. **Start the Development stack (FastAPI backend + Vite frontend)**:
   ```bash
   python run.py
   ```
   *Note: `run.py` runs Vite on port 5173 and the FastAPI backend on port 8000. Under-the-hood, the backend startup routine will automatically register and configure the Allure project settings on port 5050.*

## Requirements-Driven TDD Architecture
When modifying the application codebase or writing developer agent iterations:
1. **SQLite DataStore**: Always read and update requirements, test cases, and runs via `backend/db/store.py` (which wraps SQLite `provable.db`) rather than legacy JSON files.
2. **StrictDoc Sync**: Requirements are version-controlled inside the git repository under `workspace/requirements/requirements.sdoc`. Updates to requirements database models must trigger the bidirectional sync hook `export_sdoc()` to keep spec files aligned.
3. **TDD Flow Execution**: Every feature task must begin by generating a failing BDD test case (`workspace/tests/test_{req_id}.py`) containing `@allure` metadata and BDD step docstrings (`Given/When/Then`).
4. **Allure Matrix**: All test results must be published to the containerized Allure service on port `5050` (`frankescobar/allure-docker-service`) to update the coverage metrics seen in the frontend.
5. **OpenAI SDK & Templates**: All LLM queries must route through the OpenAI Python client using configurations inside `backend/config/models.yaml` and load system prompts dynamically from `backend/prompts/` Markdown templates.
6. **Agent Log Inspection**: When debugging why a developer agent loop failed or is stuck, inspect the logs under `backend/logs/{ticket_id}.log`. The full LangGraph orchestration execution log, LLM request/response prompts, visual QA screenshot status, and pytest command stderr output are all written here.



