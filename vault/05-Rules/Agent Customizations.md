# Agent Customizations & Operating Rules

This document outlines workspace boundary rules, headless browser execution flags, and safety guidelines enforced for all autonomous and pair-programming agents working on Provable.

---

## 🚫 Workspace Boundary Rules (`workspace/` off-limits)

The `workspace/` directory contains the target application being built by autonomous developer agents:
The authoritative rule is `.agents/rules/01-architecture-and-meta.md` (section 2, "No Bandages"): never edit or commit inside `workspace/`; fix the generator in `backend/` instead. Reading `workspace/` and running `git log/status/diff` there is fine. The `PreToolUse` hook `.claude/hooks/guard.py` enforces this for Claude Code.

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

See rule 01 section 4. In short:
- Keep `vault/Home.md` up-to-date whenever adding or deleting pages.
- Use standard double-bracket internal links (e.g. `[[System Architecture]]`) to link related concepts.
- Document architectural changes under `vault/01-Architecture/`.
- Document new workflows under `vault/02-Workflows/`.
- Document testing policies under `vault/03-Testing/`.
