# Provable Project Wiki

Welcome to the Provable Project Obsidian Vault! This is the centralized knowledge base for Provable, an agentic software engineering simulation platform where PMs orchestrate autonomous developer agents using a strict, Requirements-Driven TDD workflow.

## 🗺️ Vault Map

### 1. 🏗️ System Architecture
- [[System Architecture]]: Overview of the React PM Studio frontend, FastAPI backend, SQLite DataStore, and LangGraph orchestrator.
- [[Database Schema]]: Comprehensive documentation of SQLite tables (`requirements`, `test_cases`, `agent_runs`), schema triggers, JSON columns, and DataStore sync mechanisms.
- [[Frontend Components]]: Breakdown of React components (`App`, `KanbanBoard`, `RequirementsList`, `CodeReview`, `CoverageHub`, `AgentTray`, `DiffViewer`, `ProjectSelector`), state hooks, and CSS design system.
- [[Backend REST API]]: Detailed REST API endpoint specifications, request/response models, background tasks, and CORS configuration.
- [[Integrations]]: Sync clients for Jira (`jira_client.py`), StrictDoc (`strictdoc_client.py`), and containerized Allure reporting (`allure_client.py`).
- [[LLM Abstraction and Prompts]]: Model configuration (`config/models.yaml`), OpenAI SDK wrapping, and externalized prompt template markdown files.

### 2. 🔄 Agent Workflows & Operations
- [[Shift-Left TDD Workflow]]: Unified pre-review testing execution, requirement-driven failing test spec generation, and Allure coverage mapping.
- [[Agent Execution Loop]]: LangGraph state machine breakdown (`prepare_branch`, `code_generation`, `test_runner`, `visual_qa`, `finalize`), retry loops, Vision gate, and git rollback mechanics.
- [[Helper Scripts]]: Single cross-platform application launcher (`run.py`), PowerShell/Bash wrappers, and developer debugging utility scripts (`reset_ticket.py`, `update_json.py`, `tail_logs.sh`).
- [[Onboarding and Discovery Workflow]]: Target project discovery, Vite dev server port auto-detection, build command discovery, and workspace setup.

### 3. 🧪 Testing & Quality Assurance
- [[Testing Strategy]]: 5-tier test architecture (`tests/unit`, `tests/api`, `tests/integration`, `tests/system`, `tests/e2e`), BDD docstrings (`Given`/`When`/`Then`), `@allure` metadata tags, and test coverage checklists.

### 4. ⚖️ Architectural Decisions (ADRs)
- [[ADR-001 Host vs Containerized Execution]]: Decision record on executing Vite dev servers and Pytest on the host machine vs sandboxed Docker container.
- [[ADR-002 SQLite and StrictDoc Bidirectional Sync]]: Decision record on bridging specifications with a performant relational SQLite database.
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]: Decision record on prompt externalization and model-agnostic routing.
- [[ADR-004 Allure Reporting Server Docker Integration]]: Decision record on utilizing a containerized Allure service for automated visual test reports.

### 5. 📜 Agent Rules & Governance
- [[Agent Customizations]]: Workspace restriction rules (`workspace/` off-limits for direct edits), headless Chrome/Selenium flags (`--disable-gpu`, `--remote-debugging-port=9222`), and safety guidelines.

---
*Updated by Antigravity on 2026-07-23.*
