# Agent Customizations & Operating Rules

This document outlines workspace boundary rules, headless browser execution flags, and safety guidelines enforced for all autonomous and pair-programming agents working on Provable.

---

## 🚫 Workspace Boundary Rules (`workspace/` off-limits)

The `workspace/` directory contains the target application being built by autonomous developer agents:
- **Direct Editing Forbidden**: Never directly write, edit, delete, or commit files inside `workspace/` during manual development turns.
- **Automated Pipeline Only**: All edits inside `workspace/` must be performed exclusively by the automated developer agent pipeline (`agent_orchestrator.py`), which runs LLM code generation, executes tests, and commits on target ticket branches.
- **Allowed Actions**: Reading `workspace/` files for inspection/diagnosis and running `git log`, `git status`, or `git diff` inside `workspace/` is permitted.

---

## 🖥️ Headless Chrome & Selenium Execution Flags

When running headless Chrome or Selenium automation in containerized remote environments or WSL:
- Always include `--disable-gpu` and `--remote-debugging-port=9222` in Webdriver initialization arguments to prevent `DevToolsActivePort` initialization failures.
- Recommended argument list:
  ```python
  options = webdriver.ChromeOptions()
  options.add_argument("--headless=new")
  options.add_argument("--disable-gpu")
  options.add_argument("--remote-debugging-port=9222")
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  ```

---

## 📁 Obsidian Vault Documentation Maintenance

Maintain a well-structured Obsidian vault under `vault/`:
- Keep `vault/Home.md` up-to-date whenever adding or deleting pages.
- Use standard double-bracket internal links (e.g. `[[System Architecture]]`) to link related concepts.
- Document architectural changes under `vault/01-Architecture/`.
- Document new workflows under `vault/02-Workflows/`.
- Document testing policies under `vault/03-Testing/`.
