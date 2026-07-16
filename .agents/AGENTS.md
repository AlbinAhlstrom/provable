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

## Headless Chrome & Selenium in WSL
When executing headless Chrome or Selenium automation inside WSL or containerized remote environments:
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
   wsl -e bash dev.sh
   ```
   *Note: `dev.sh` runs Vite on port 5173 and the FastAPI backend on port 8000. Under-the-hood, the backend startup routine will automatically register and configure the Allure project settings on port 5050.*

