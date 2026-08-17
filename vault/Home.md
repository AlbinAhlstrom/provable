# Provable Project Wiki

Welcome to the Provable Project Obsidian Vault! This is the centralized knowledge base for Provable, an agentic software engineering simulation platform where PMs orchestrate dynamic Domain-Driven Design (DDD) domain synthesis and autonomous developer agents using a strict, Requirements-Driven TDD workflow.

---

## 🗺️ Vault Map

### 1. 🏗️ System Architecture
- [[System Architecture]]: Overview of the React PM Studio frontend (Explorer, Domain Canvas, Live App Preview, Code Review, Coverage Hub), FastAPI backend engine, SQLite DataStore, and OpenHands orchestrator.
- [[PM-Studio-UX-Architecture-And-Direction]]: Breakdown of PM Studio 3-Pillar UX Architecture (Pages Bar, Executable Test Specs, Domain Entity CRUD) and Mobile-First responsive design system invariants.
- [[Universal-Dynamic-Domain-AST-Generator]]: Universal dynamic domain generator synthesizing contract-first 6-part DDD backend modules and React 18 frontend stacks for ANY domain pitch without template leakage.
- [[Database Schema]]: Comprehensive documentation of SQLite tables (`requirements`, `test_cases`, `agent_runs`), schema triggers, JSON columns, and DataStore sync mechanisms.
- [[Frontend Components]]: Breakdown of React components (`App`, `DomainModeling`, `AppPreview`, `RequirementsList`, `CodeReview`, `CoverageHub`, `AgentTray`, `DiffViewer`), state hooks, and CSS design system.
- [[Backend REST API]]: Detailed REST API endpoint specifications, request/response models, background tasks, and CORS configuration.
- [[Integrations]]: Sync clients for Jira (`jira_client.py`), StrictDoc (`strictdoc_client.py`), and containerized Allure reporting (`allure_client.py`).
- [[LLM Abstraction and Prompts]]: Model configuration (`config/models.yaml`), OpenAI SDK wrapping, and externalized prompt template markdown files (`domain_discovery.md`).
- [[05-DDD-TDD-Architecture-Guidelines|DDD & TDD Architecture Guidelines]]: Architectural layer rules (Domain Model, Repository, Service Layer, Unit of Work, Events) adapted from *Architecture Patterns with Python*.


### 2. 🔄 Agent Workflows & Operations
- [[Onboarding and Discovery Workflow]]: Business pitch discovery, dynamic schema derivation, contract-first domain synthesis, and clean workspace scaffold invariants.
- [[Shift-Left TDD Workflow]]: Unified pre-review testing execution, requirement-driven failing test spec generation, and Allure coverage mapping.
- [[Agent Execution Loop]]: LangGraph state machine breakdown (`prepare_branch`, `code_generation`, `test_runner`, `visual_qa`, `finalize`), retry loops, Vision gate, and git rollback mechanics.
- [[DDD_TDD_Developer_Workflow]]: Pure DDD layer boundaries, subagent execution contract, 4-step execution loop, and anti-leakage verification gate.
- [[Future Enhancements Roadmap]]: Detailed blueprints for the Live Agent Execution Graph Visualizer and Self-Healing TDD Feedback Loop.

- [[Helper Scripts]]: Single cross-platform application launcher (`run.py`), PowerShell/Bash wrappers, and developer debugging utility scripts (`reset_ticket.py`, `update_json.py`, `tail_logs.sh`).


### 3. 🧪 Testing & Quality Assurance
- [[Automated-Verification-And-Self-Healing-Pipeline]]: 3-stage automated verification pipeline featuring Vocabulary Audit Gate (`audit_domain_vocabulary`), Web App Preview Health Gate (`verify_preview_health`), and Pytest Execution Gate.
- [[Testing Strategy]]: 5-tier test architecture (`tests/unit`, `tests/api`, `tests/integration`, `tests/system`, `tests/e2e`), BDD docstrings (`Given`/`When`/`Then`), `@allure` metadata tags, and test coverage checklists.


### 4. ⚖️ Architectural Decisions (ADRs)
- [[ADR-001 Host vs Containerized Execution]]: Decision record on executing Vite dev servers and Pytest on the host machine vs sandboxed Docker container.
- [[ADR-002 SQLite and StrictDoc Bidirectional Sync]]: Decision record on bridging specifications with a performant relational SQLite database.
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]: Decision record on prompt externalization and model-agnostic routing.
- [[ADR-004 Allure Reporting Server Docker Integration]]: Decision record on utilizing a containerized Allure service for automated visual test reports.


### 5. 📜 Agent Rules & Governance
- [[Agent Customizations]]: Workspace restriction rules (`workspace/` off-limits for direct edits), headless Chrome/Selenium flags (`--disable-gpu`, `--remote-debugging-port=9222`), and safety guidelines.


### 6. 🌌 Cosmic Python Journey
- [[Chapter-01-Domain-Model|Chapter 1: Domain Modeling]]: Pure Python domain entities, value objects, low-gear TDD, and 4 extracted universal agent rules.
- [[Chapter-07-Aggregates-and-Optimistic-Concurrency|Chapter 7: Aggregates & Optimistic Concurrency]]: Aggregate consistency boundaries, `version_number` tracking, and SQLAlchemy `version_id_col` optimistic locks.
- [[Chapter-13-Dependency-Injection-and-Bootstrap|Chapter 13: DI & Bootstrap Container]]: Dependency Injection container (`bootstrap.py`), `inspect.signature` injection, and decoupled message bus.

---
*Updated by Antigravity on 2026-08-05.*
