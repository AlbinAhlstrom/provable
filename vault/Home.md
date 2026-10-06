# Provable Project Wiki

Welcome to the Provable Project Obsidian Vault! This is the centralized knowledge base for Provable, an enterprise-grade, deterministic Domain-Driven Design (DDD) and Test-Driven Development (TDD) AppGen Engine.

---

## 🗺️ Vault Map

### 1. 🏗️ System Architecture
- [[Enterprise-AppGen-TDD-Engine-Architecture]]: Core Enterprise AppGen engine architecture: Schema-Driven UI (Dumb Projection), Programmatic Red-Gate TDD Validation, LibCST Code Isolation, and SHA-256 5-Line Hash Lock.
- [[System Architecture]]: Overview of PM Studio frontend (`KickstartStudio`, `BehaviorInboxPanel`, `RequirementControlPanel`, `AppPreview`), FastAPI backend engine, SQLite DataStore, and TDD state machine.
- [[Full-LLM-Free-Form-Orchestration-Graph]]: Full-LLM synthesis pipeline featuring Domain Storming, Backend DDD/TDD, Skeleton Builder, and Verification Gates.
- [[PM-Studio-UX-Architecture-And-Direction]]: Breakdown of PM Studio 3-Pillar UX Architecture (Pages Bar, Executable Test Specs / Behavior Inbox, Domain Entities Inspector) and Mobile-First responsive design system invariants.
- [[Universal-Dynamic-Domain-AST-Generator]]: Dynamic domain generator scaffolding pure DDD domain aggregates (`Pallet`, `Zone`, `Operator`), Pydantic DTOs, Unit of Work, and FastAPI routers.
- [[Database Schema]]: Comprehensive documentation of SQLite tables (`requirements`, `test_cases`, `agent_runs`, `kickstart_state`, `projects`), schema triggers, JSON columns, and DataStore sync mechanisms.
- [[Frontend Components]]: Breakdown of React components (`App`, `KickstartStudio`, `AppPreview`, `BehaviorInboxPanel`, `RequirementControlPanel`, `DomainEntitiesPanel`, `CoverageHub`), state hooks, and CSS design system.
- [[Backend REST API]]: Detailed REST API endpoint specifications (`/api/specs/inbox`, `/api/onboarding/kickstart`, `/api/onboarding/reset`, `/api/requirements`, `/api/coverage`), request/response models, and CORS configuration.
- [[Integrations]]: Sync clients for StrictDoc (`strictdoc_client.py`) and containerized Allure reporting (`allure_client.py`).
- [[LLM Abstraction and Prompts]]: Env-var model configuration, the OpenAI-SDK `call_gemini` wrapper, and where each prompt lives (file-based vs inline).
- [[05-DDD-TDD-Architecture-Guidelines|DDD & TDD Architecture Guidelines]]: Architectural layer rules (Domain Model, Repository, Service Layer, Unit of Work, Events) adapted from *Architecture Patterns with Python*.


### 2. 🔄 Agent Workflows & Operations
- [[Clanker-Protocol]]: The Clanker Protocol operational paradigm: Principal Architect persona, The Three Laws, "The Fatal Flaw" pushback mechanism, and UX Dual-Track routing (Track A vs Track B).
- [[Onboarding and Discovery Workflow]]: Bounded context discovery, router engine decomposition (`router_engine.py`), skeleton scaffolding (`skeleton_builder.py`), and clean workspace scaffold invariants.
- [[Shift-Left TDD Workflow]]: Unified pre-implementation testing execution, requirement-driven failing test spec generation, and Allure coverage mapping.
- [[Agent Execution Loop]]: TDD execution loop (`tdd_machine.py`) enforcing RED phase, LibCST class extraction, SHA-256 test integrity check, and the single-feedback-retry dead-end policy.
- [[DDD_TDD_Developer_Workflow]]: Pure DDD layer boundaries, 4-step execution loop (RED-GREEN-WIRE-VERIFY), and anti-leakage verification gate.
- [[Future Enhancements Roadmap]]: Detailed blueprints for Schema-Driven Dynamic Forms, LLM LibCST repair loops, and Multi-Domain Stress Testing.
- [[Bug-Reproduction-and-Testing-Policy]]: Strict policy and automated regression test workflow for bug reproduction, tri-service stack startup (:8000, :5173, :5174), and zero-regression guarantees.
- [[Helper Scripts]]: Single cross-platform application launcher (`run.py`) and PowerShell/Bash wrappers.


### 3. 🧪 Testing & Quality Assurance
- [[Automated-Verification-And-Self-Healing-Pipeline]]: Automated verification pipeline featuring The Gibberish Strategy (`test_ui_dynamic_projection.py`), Frontend Domain Purity Gate (`test_frontend_domain_purity.py`), and Pytest Execution Gate.
- [[Testing Strategy]]: 3-tier DDD test architecture (`backend/tests/unit`, `backend/tests/integration`, `backend/tests/e2e`), BDD docstrings (`Given`/`When`/`Then`), `@allure` metadata tags, and 5-line hash lock verification.


### 4. ⚖️ Architectural Decisions (ADRs)
- [[ADR-001 Host vs Containerized Execution]]: Decision record on executing Vite dev servers and Pytest on the host machine vs sandboxed Docker container.
- [[ADR-002 SQLite and StrictDoc Bidirectional Sync]]: Decision record on bridging specifications with a performant relational SQLite database.
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]: Decision record on prompt externalization and model-agnostic routing via OpenAI SDK.
- [[ADR-004 Allure Reporting Server Docker Integration]]: Decision record on utilizing a containerized Allure service for automated visual test reports.
- [[ADR-005 Vercel Multi-Service Deployment]]: Decision record on deploying the engine API and Studio as Vercel services, the serverless mode, and what a deployment cannot do (ephemeral state, no generated-app preview).
- [[ADR-006 Spec-Derived RED Tests and Fragment GREEN]]: Decision record on LLM-written behavioral RED tests, the stricter RED gate, module-fragment GREEN, rollback and the evidence behind them.
- [[ADR-007 Product Intent Step]]: Decision record on classifying what kind of product a pitch asks for before designing the domain model.
- [[ADR-008 Aggregate Ownership and Audience-Scoped UI]]: The TDD loop owns the aggregate, the intent reaches every stage, and the UI serves only the product's audience; lists the known remaining gaps.


### 5. 📜 Agent Rules & Governance
- [[Agent Customizations]]: Workspace restriction rules (`workspace/` off-limits for direct edits), headless Chrome/Selenium flags (`--disable-gpu`, `--remote-debugging-port=9222`), and safety guidelines.


### 6. 🌌 Cosmic Python Journey
- [[Chapter-01-Domain-Model|Chapter 1: Domain Modeling]]: Pure Python domain entities, value objects, low-gear TDD, and 4 extracted universal agent rules.
- [[Chapter-07-Aggregates-and-Optimistic-Concurrency|Chapter 7: Aggregates & Optimistic Concurrency]]: Aggregate consistency boundaries, `version_number` tracking, and SQLAlchemy `version_id_col` optimistic locks.
- [[Chapter-13-Dependency-Injection-and-Bootstrap|Chapter 13: DI & Bootstrap Container]]: Dependency Injection container (`bootstrap.py`), `inspect.signature` injection, and decoupled message bus.

---

