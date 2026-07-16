# Agent Customizations

This page documents the behavioral constraints, style guidelines, and rules configured for Provable's development assistants (stored in `.agents/AGENTS.md`).

## 1. Safety & Workspace Restraints
To preserve the integrity of the agentic simulation, development agents modifying Provable itself must never interfere with the sandbox:
*   **Target Directory**: The directory `workspace/` contains the target application modified *only* by sandbox agents.
*   **Off-Limits**: Under no circumstances should backend developer agents read, edit, compile, or commit files directly inside `workspace/`.
*   **Permitted Inspects**: Agents may run `git status`, `git diff`, and read file contents inside `workspace/` only to inspect errors.

## 2. Web Automation & Selenium args
For visual checks running within containerized environments or WSL headless hosts:
*   Always include `--disable-gpu` and `--remote-debugging-port=9222` to prevent headless chrome initialization errors.
