# Provable: Complete Project & Architecture Documentation

> **Consolidated Master Document**
> This single-file documentation bundle contains the complete specifications, architectural designs, agent invariants, workflows, testing policies, ADRs, Cosmic Python foundations, and backend system prompts across the entire Provable repository (including the full Obsidian Vault).

---

## 📑 Table of Contents

1. [README.md](#file-1-readmemd)
2. [.agents/AGENTS.md](#file-2-agents-agentsmd)
3. [.agents/skills/acceptance/SKILL.md](#file-3-agents-skills-acceptance-skillmd)
4. [.agents/skills/take_ui_screenshot/SKILL.md](#file-4-agents-skills-take-ui-screenshot-skillmd)
5. [vault/Home.md](#file-5-vault-homemd)
6. [vault/HANDOVER.md](#file-6-vault-handovermd)
7. [vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md](#file-7-vault-01-architecture-enterprise-appgen-tdd-engine-architecturemd)
8. [vault/01-Architecture/System Architecture.md](#file-8-vault-01-architecture-system-architecturemd)
9. [vault/01-Architecture/Universal-Dynamic-Domain-AST-Generator.md](#file-9-vault-01-architecture-universal-dynamic-domain-ast-generatormd)
10. [vault/01-Architecture/Frontend Components.md](#file-10-vault-01-architecture-frontend-componentsmd)
11. [vault/01-Architecture/Backend REST API.md](#file-11-vault-01-architecture-backend-rest-apimd)
12. [vault/01-Architecture/Database Schema.md](#file-12-vault-01-architecture-database-schemamd)
13. [vault/01-Architecture/Integrations.md](#file-13-vault-01-architecture-integrationsmd)
14. [vault/01-Architecture/LLM Abstraction and Prompts.md](#file-14-vault-01-architecture-llm-abstraction-and-promptsmd)
15. [vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md](#file-15-vault-01-architecture-pm-studio-ux-architecture-and-directionmd)
16. [vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md](#file-16-vault-01-architecture-full-llm-free-form-orchestration-graphmd)
17. [vault/01-Architecture/05-DDD-TDD-Architecture-Guidelines.md](#file-17-vault-01-architecture-05-ddd-tdd-architecture-guidelinesmd)
18. [vault/02-Workflows/Onboarding and Discovery Workflow.md](#file-18-vault-02-workflows-onboarding-and-discovery-workflowmd)
19. [vault/02-Workflows/Shift-Left TDD Workflow.md](#file-19-vault-02-workflows-shift-left-tdd-workflowmd)
20. [vault/02-Workflows/Agent Execution Loop.md](#file-20-vault-02-workflows-agent-execution-loopmd)
21. [vault/02-Workflows/DDD_TDD_Developer_Workflow.md](#file-21-vault-02-workflows-ddd-tdd-developer-workflowmd)
22. [vault/02-Workflows/Future Enhancements Roadmap.md](#file-22-vault-02-workflows-future-enhancements-roadmapmd)
23. [vault/02-Workflows/Bug-Reproduction-and-Testing-Policy.md](#file-23-vault-02-workflows-bug-reproduction-and-testing-policymd)
24. [vault/02-Workflows/Helper Scripts.md](#file-24-vault-02-workflows-helper-scriptsmd)
25. [vault/03-Testing/Testing Strategy.md](#file-25-vault-03-testing-testing-strategymd)
26. [vault/03-Testing/Automated-Verification-And-Self-Healing-Pipeline.md](#file-26-vault-03-testing-automated-verification-and-self-healing-pipelinemd)
27. [vault/04-Decisions/ADR-001 Host vs Containerized Execution.md](#file-27-vault-04-decisions-adr-001-host-vs-containerized-executionmd)
28. [vault/04-Decisions/ADR-002 SQLite and StrictDoc Bidirectional Sync.md](#file-28-vault-04-decisions-adr-002-sqlite-and-strictdoc-bidirectional-syncmd)
29. [vault/04-Decisions/ADR-003 LLM Abstraction Layer and Prompt Externalization.md](#file-29-vault-04-decisions-adr-003-llm-abstraction-layer-and-prompt-externalizationmd)
30. [vault/04-Decisions/ADR-004 Allure Reporting Server Docker Integration.md](#file-30-vault-04-decisions-adr-004-allure-reporting-server-docker-integrationmd)
31. [vault/05-Rules/Agent Customizations.md](#file-31-vault-05-rules-agent-customizationsmd)
32. [vault/06-Cosmic-Python-Journey/Chapter-01-Domain-Model.md](#file-32-vault-06-cosmic-python-journey-chapter-01-domain-modelmd)
33. [vault/06-Cosmic-Python-Journey/Chapter-07-Aggregates-and-Optimistic-Concurrency.md](#file-33-vault-06-cosmic-python-journey-chapter-07-aggregates-and-optimistic-concurrencymd)
34. [vault/06-Cosmic-Python-Journey/Chapter-13-Dependency-Injection-and-Bootstrap.md](#file-34-vault-06-cosmic-python-journey-chapter-13-dependency-injection-and-bootstrapmd)
35. [vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_condensed.md](#file-35-vault-06-cosmic-python-journey-references-architecture-patterns-with-python-condensedmd)
36. [vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_dump.md](#file-36-vault-06-cosmic-python-journey-references-architecture-patterns-with-python-dumpmd)
37. [vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python.md](#file-37-vault-06-cosmic-python-journey-references-architecture-patterns-with-pythonmd)
38. [backend/prompts/router_decomposition.md](#file-38-backend-prompts-router-decompositionmd)
39. [backend/prompts/domain_discovery.md](#file-39-backend-prompts-domain-discoverymd)
40. [backend/prompts/test_case_generation.md](#file-40-backend-prompts-test-case-generationmd)
41. [backend/prompts/code_generation.md](#file-41-backend-prompts-code-generationmd)
42. [backend/prompts/ui_generation.md](#file-42-backend-prompts-ui-generationmd)
43. [backend/prompts/visual_qa.md](#file-43-backend-prompts-visual-qamd)
44. [backend/prompts/visual_audit.md](#file-44-backend-prompts-visual-auditmd)
45. [backend/prompts/task_decomposition.md](#file-45-backend-prompts-task-decompositionmd)
46. [backend/prompts/requirement_audit.md](#file-46-backend-prompts-requirement-auditmd)
47. [backend/prompts/merge_resolution.md](#file-47-backend-prompts-merge-resolutionmd)
48. [backend/prompts/ddd_guidelines_template.md](#file-48-backend-prompts-ddd-guidelines-templatemd)
49. [backend/prompts/green_class_repair.md](#file-49-backend-prompts-green-class-repairmd)

---

---

## File 1: `README.md`

<!-- START_FILE: README.md -->

<div align="center">

# 🛡️ Provable

**Deterministic Domain-Driven Design (DDD) & Test-Driven Development (TDD) AppGen Engine**

*Enterprise-grade, specification-driven application generator transforming industrial business requirements into verified DDD Python backends and schema-projected interfaces.*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Architecture](#-system-architecture) •
[Quick Start](#-quick-start) •
[Services & Ports](#-services--live-endpoints) •
[Key Features](#-key-features) •
[Project Structure](#-project-structure)

</div>

---

## 📖 Overview

**Provable** is a deterministic, enterprise-grade software generation platform. It eliminates LLM hallucinations, context drift, and brittle synthetic code by enforcing a strict **Test-Driven Development (RED-GREEN-COMMIT)** state machine and **Domain-Driven Design (DDD)** bounded context architecture.

Industrial business domains (e.g. Warehouse Management Systems, Logistics, Supply Chain) are decomposed into formal Aggregate Roots (`Pallet`, `Zone`, `Operator`) and atomic BDD behavior specifications (`GIVEN / WHEN / THEN`). Solutions are surgically spliced via **LibCST**, verified against programmatic Red-Gate and Green-Gate pytest suites, locked via **SHA-256 5-line anti-cheat hash locks**, and projected onto domain-agnostic user interfaces.

---

## ✨ Key Features

- ⚡ **Deterministic RED-GREEN-COMMIT TDD Loop**: Programmatic pytest execution gate evaluating exit codes, tautologies (rejecting exit code 0 during RED), crash reports, and 5-second hard timeouts.
- 🔒 **SHA-256 5-Line Hash Lock Anti-Cheat**: Cryptographic hashing of test specifications before and after implementation phases to mathematically prevent AI test tampering without OS-level locks.
- 🧬 **Pure DDD Aggregate Core**: Business logic strictly anchored in isolated dataclass aggregate roots with zero database or framework dependencies.
- 📐 **Surgical LibCST Code Splicing**: Meta `libcst` context extraction and class splicing preserving 100% of formatting, indentation, and docstrings.
- 🌐 **Schema-Driven Dumb UI Projection**: Dynamic frontend projection driven by backend schema contracts, eliminating hardcoded domain assumptions (verified via The Gibberish Strategy).
- 📊 **Containerized Allure Dashboard**: Live test execution matrices and coverage analytics rendered via an embedded Allure Docker service.
- 🚀 **Single-Command Launch**: Zero-friction cross-platform runner (`run.py`) managing dependencies, Docker services, and dev servers.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph Intake [1. Natural Language Bounded Context]
        Pitch[Industrial Domain Pitch] --> Router[router_engine.py]
        Router --> Struct[DomainStructureSchema: Aggregate Roots]
        Router --> Inbox[DomainBehaviorInboxSchema: BDD Specs]
    end

    subgraph Skeleton [2. Instant Full-Stack Skeleton]
        Struct --> SkeletonBuilder[skeleton_builder.py]
        SkeletonBuilder --> Domain[src/domain/: Pure Dataclasses]
        SkeletonBuilder --> Adapters[src/adapters/: Repositories & Fakes]
        SkeletonBuilder --> UoW[src/service_layer/: Unit of Work]
        SkeletonBuilder --> Routers[src/entrypoints/routers/: FastAPI Routers]
        Routers --> OpenAPI[/openapi.json Contract from Second 0/]
    end

    subgraph TDD [3. Hardened Red-Gate TDD State Machine]
        Inbox --> PopSpec[Next BDD Spec]
        PopSpec --> RedGen[RED_GEN: Generate Unit Test]
        RedGen --> RedGate{RED GATE: pytest Exit 1 + AssertionError}
        RedGate -- Approved RED --> HashLock[SHA-256 Test File Hash Snapshot]
        HashLock --> GreenGen[GREEN_GEN: LibCST Surgical Class Splicing]
        GreenGen --> GreenGate{GREEN GATE: pytest Exit 0 + Hash Intact}
        GreenGate -- PASS --> Commit[Git Commit: feat/spec]
        GreenGate -- FAIL (Tries == 3) --> DeadEnd[Git Rollback: REQUIRES_HUMAN_INTERVENTION]
    end

    subgraph Presentation [4. Domain-Agnostic UI Projection]
        OpenAPI --> UI[React PM Studio :5173 / Live Preview :5174]
        Routers --> Swagger[FastAPI Swagger UI :8000/docs]
    end
```

---

## 🚀 Quick Start

### 📋 Prerequisites

Before running Provable, ensure the host machine has the following tools installed:

1. **Python 3.11+** (Added to system `PATH`)
2. **Node.js 18+** & **npm** (Added to system `PATH`)
3. **Docker Desktop** (Running, for containerized Allure reporting)

### ⚡ Launching the Application (Single Command)

Provable features a unified, cross-platform runner script (`run.py`) that auto-detects your environment, installs/upgrades all Python and Node dependencies, starts the Docker container, and launches all background development servers.

Run the launcher for your environment:

#### Windows (PowerShell / Command Prompt)
```powershell
python run.py
```

#### Linux / WSL / macOS
```bash
python3 run.py
```

---

## 🌐 Services & Live Endpoints

Once launched, the following services will be available:

| Service | Endpoint | Description |
| :--- | :--- | :--- |
| **PM Studio Frontend** | [`http://localhost:5173`](http://localhost:5173) | Domain Bounded Context & Behavior Inbox Studio |
| **FastAPI Backend API** | [`http://localhost:8000`](http://localhost:8000) | REST API engine, DDD services & orchestration |
| **Interactive API Docs** | [`http://localhost:8000/docs`](http://localhost:8000/docs) | Generated OpenAPI Swagger documentation |
| **Allure Test Dashboard** | [`http://localhost:5050`](http://localhost:5050) | Containerized test results & BDD matrix dashboard |
| **Workspace Live Preview** | [`http://localhost:5174`](http://localhost:5174) | Sandbox live preview server for the target app |

---

## 📂 Project Structure

```
provable/
├── backend/                  # FastAPI backend engine & DDD orchestrator
│   ├── adapters/             # Repository Pattern & Workspace adapters
│   ├── config/               # Model routing (models.yaml) & configuration
│   ├── db/                   # SQLite DataStore wrapper & schema migrations (store.py)
│   ├── domain/               # Core domain entities & business exceptions
│   ├── entrypoints/          # REST API routers (specs, kickstart, onboarding, requirements)
│   ├── onboarding/           # Domain router engine, skeleton builder, LibCST isolator
│   ├── prompts/              # System prompt templates for LLM agents
│   ├── service_layer/        # Unit of Work, message bus, and TDD state machine
│   └── tests/                # Unit, integration, and E2E test suites (124+ tests)
├── frontend/                 # PM Studio React 18 + Vite frontend
│   ├── src/                  # React TypeScript source
│   │   ├── components/       # KickstartStudio, BehaviorInboxPanel, RequirementControlPanel, AppPreview
│   │   └── App.tsx           # Main application shell
├── vault/                    # Comprehensive Obsidian knowledge base & architectural records
│   ├── 01-Architecture/      # System architecture, DDD patterns, schema-driven UI
│   ├── 02-Workflows/         # TDD workflows, verification pipelines, roadmap
│   ├── 04-Decisions/         # Architectural Decision Records (ADRs)
│   ├── HANDOVER.md           # Cross-chat continuity & active system state
│   └── Home.md               # Vault sitemap & wiki index
├── docker-compose.allure.yaml# Docker Compose manifest for Allure reporting service
├── run.py                    # Unified single cross-platform launcher script
├── run.ps1                   # Windows PowerShell launcher wrapper
└── run.sh                    # Linux/WSL shell launcher wrapper
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<!-- END_FILE: README.md -->

---

## File 2: `.agents/AGENTS.md`

<!-- START_FILE: .agents/AGENTS.md -->

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
   - **Layer Boundaries**: `Domain Model` (`backend/domain/`) $
ightarrow$ `Repository Pattern` (`backend/adapters/`) $
ightarrow$ `Service Layer / Unit of Work` (`backend/service_layer/`) $
ightarrow$ `Presentation Routers` (`backend/entrypoints/routers/`).
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

<!-- END_FILE: .agents/AGENTS.md -->

---

## File 3: `.agents/skills/acceptance/SKILL.md`

<!-- START_FILE: .agents/skills/acceptance/SKILL.md -->

---
name: acceptance
description: Rigorous 6-step TDD, self-critique, acceptance criteria formulation, and verification workflow for code changes.
---

# Acceptance Protocol Skill

This skill defines the standard 6-step Quality & Acceptance Protocol for Antigravity agents executing complex code modifications, refactorings, or new features.

---

## 📋 The 6-Step Acceptance Workflow

### Step 1: Self-Critique & Plan Refinement
Before modifying source code, perform a critical review of the proposed plan:
- **Edge Cases & Failure Modes**: What boundary conditions or unexpected inputs could break this logic?
- **Performance & Latency**: Does this approach introduce synchronous network bottlenecks or heavy loops?
- **Architectural Integrity**: Does this introduce hardcoded string hacks or special-casing? If so, replace with contract-driven abstractions.
- **Accessibility & UX**: Does this violate WCAG contrast ratios, typography rules, or visual layout boundaries?

### Step 2: Define Acceptance Criteria
Formulate clear, unambiguous criteria divided into two categories:

#### 🧪 Testable Acceptance Criteria (Automated)
- Quantitative invariants (e.g., zero hardcoded keyword cascades, zero pizza string leakage, WCAG contrast ratio $\ge 4.5:1$).
- Specific API response schemas and database state contracts.
- 100% pass rate across automated test suites.

#### 🖐️ Manual Verification Criteria (User Verification)
- Visual styling, color harmony, and layout proportions.
- Interactive UX responsiveness and canvas controls.
- End-to-end user flows in the live browser preview (`http://localhost:5174`).

### Step 3: Test-Driven Development (TDD) First
- Author automated tests **BEFORE** modifying implementation code (`backend/tests/test_<feature>.py`).
- Include edge case assertions and contract invariants.
- Execute the test suite to verify initial expected failure (Red state).

### Step 4: Implement Solution
- Implement source code changes adhering to Domain-Driven Design (DDD) layer boundaries.
- Ensure all business logic relies on contracts/schemas rather than hardcoded string checks.

### Step 5: Automated Verification Loop
- Run automated tests (`pytest backend/tests`).
- If any assertion fails, inspect the error traceback silently, fix the underlying root cause, and re-run.
- Repeat until 100% of testable criteria pass (Green state).

### Step 6: Handover & Manual Verification Report
- Summarize work accomplished and automated test results.
- Explicitly list the manual verification steps for the user to perform in the live preview.
- Update documentation sitemap and handover records (`vault/HANDOVER.md`).

---

## 🛠️ Usage Example

When instructed to apply the `acceptance` workflow:

```bash
# 1. Run TDD tests (expecting failure)
pytest backend/tests/test_feature.py

# 2. Implement changes in backend/

# 3. Verify clean pass
pytest backend/tests

# 4. Re-sync application shell if needed
python -c "import sys; sys.path.insert(0, 'backend'); from main import sync_workspace_app_shell; sync_workspace_app_shell()"
```

<!-- END_FILE: .agents/skills/acceptance/SKILL.md -->

---

## File 4: `.agents/skills/take_ui_screenshot/SKILL.md`

<!-- START_FILE: .agents/skills/take_ui_screenshot/SKILL.md -->

---
name: take_ui_screenshot
description: Takes a screenshot of a specific URL/view of the web application using headless Selenium.
---
# Take UI Screenshot

This skill navigates to the application, selects a specific view, and captures a high-resolution screenshot.

## Instructions

Run the Python helper script to take a screenshot:
```bash
python3 .agents/skills/take_ui_screenshot/scripts/take_screenshot.py --url http://localhost:5173 --view Tests --output /path/to/screenshot.png
```

Parameters:
- `--url`: The base URL of the application (default: `http://localhost:5173`).
- `--view`: The name of the tab/view to click (e.g., `Tests`, `Kanban`, `Requirements`, `Review`).
- `--output`: File path to save the screenshot (default: `screenshot.png`).
- `--viewport`: Viewport resolution, e.g., `1280x800` (default) or `375x812`.

<!-- END_FILE: .agents/skills/take_ui_screenshot/SKILL.md -->

---

## File 5: `vault/Home.md`

<!-- START_FILE: vault/Home.md -->

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
- [[LLM Abstraction and Prompts]]: Model configuration (`config/models.yaml`), OpenAI Python SDK client routing (`gemini-2.5-flash`), and externalized prompt template markdown files (`router_decomposition.md`, `domain_discovery.md`).
- [[05-DDD-TDD-Architecture-Guidelines|DDD & TDD Architecture Guidelines]]: Architectural layer rules (Domain Model, Repository, Service Layer, Unit of Work, Events) adapted from *Architecture Patterns with Python*.


### 2. 🔄 Agent Workflows & Operations
- [[Onboarding and Discovery Workflow]]: Bounded context discovery, router engine decomposition (`router_engine.py`), skeleton scaffolding (`skeleton_builder.py`), and clean workspace scaffold invariants.
- [[Shift-Left TDD Workflow]]: Unified pre-implementation testing execution, requirement-driven failing test spec generation, and Allure coverage mapping.
- [[Agent Execution Loop]]: TDD execution loop (`tdd_machine.py`) enforcing RED phase, LibCST class extraction, SHA-256 test integrity check, and 3-strike dead-end rollback handling.
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


### 5. 📜 Agent Rules & Governance
- [[Agent Customizations]]: Workspace restriction rules (`workspace/` off-limits for direct edits), headless Chrome/Selenium flags (`--disable-gpu`, `--remote-debugging-port=9222`), and safety guidelines.


### 6. 🌌 Cosmic Python Journey
- [[Chapter-01-Domain-Model|Chapter 1: Domain Modeling]]: Pure Python domain entities, value objects, low-gear TDD, and 4 extracted universal agent rules.
- [[Chapter-07-Aggregates-and-Optimistic-Concurrency|Chapter 7: Aggregates & Optimistic Concurrency]]: Aggregate consistency boundaries, `version_number` tracking, and SQLAlchemy `version_id_col` optimistic locks.
- [[Chapter-13-Dependency-Injection-and-Bootstrap|Chapter 13: DI & Bootstrap Container]]: Dependency Injection container (`bootstrap.py`), `inspect.signature` injection, and decoupled message bus.

---
*Updated by Antigravity on 2026-08-25.*

<!-- END_FILE: vault/Home.md -->

---

## File 6: `vault/HANDOVER.md`

<!-- START_FILE: vault/HANDOVER.md -->

# Provable Project Handover & Cross-Chat Continuity Record

This living record ensures 100% seamless continuity between chat sessions. Any agent or human developer resuming work must read this document at the start of a session.

---

## 📌 Current Active System State

- **Active Workspace Base**: `workspace/` (repo-relative)
- **Application Stack Status**:
  - FastAPI Backend Engine: Running on `http://localhost:8000/`
  - Vite PM Studio Frontend: Running on `http://localhost:5173/`
  - Workspace App Preview: Running on `http://localhost:5174/`
  - Containerized Allure Service: Running on `http://localhost:5050/`
- **Active Backend Architecture**: Clean Layered DDD/TDD Architecture (Domain Model, Repository, Unit of Work, Service Layer, Routers).
- **Verified Build Status**: `100% PASS` (0 Vite JSX/TypeScript compilation errors, 102/102 backend pytest suite passed in 42.90s).

---

## 🏛️ Completed Architectural Achievements

1. **Comprehensive Codebase Purge (2,818 lines of dead code removed)**:
   - **Purged Backend Routers**: Deleted [`backend/entrypoints/routers/reviews.py`](backend/entrypoints/routers/reviews.py) and [`backend/entrypoints/routers/agents.py`](backend/entrypoints/routers/agents.py) and unmounted them from [`backend/app.py`](backend/app.py).
   - **Purged Jira/Kanban Integration**: Deleted [`backend/integrations/jira_client.py`](backend/integrations/jira_client.py), `jira` section from `integrations.yaml`, startup sync hook in `app.py`, and `jira_key` fields across `store.py`, `schema.sql`, `model.py`, and `repository.py`.
   - **Purged Orphaned UI Components**: Deleted [`AgentTray.tsx`](src/components/AgentTray.tsx), [`CodeReview.tsx`](src/components/CodeReview.tsx), [`DiffViewer.tsx`](src/components/DiffViewer.tsx), and [`DomainModeling.tsx`](src/components/DomainModeling.tsx), and cleaned up dead polling loops/state in [`src/App.tsx`](src/App.tsx).
   - **Purged Legacy Onboarding Modules & Obsolete Scripts**: Deleted [`onboard.py`](backend/onboarding/onboard.py), [`requirements_generator.py`](backend/onboarding/requirements_generator.py), [`requirements_synthesizer.py`](backend/onboarding/requirements_synthesizer.py), [`workspace_discovery_agent.py`](backend/onboarding/workspace_discovery_agent.py), [`reset_task.py`](backend/reset_task.py), [`src/requirements.json`](src/requirements.json), [`reset_ticket.py`](scripts/reset_ticket.py), and [`update_json.py`](scripts/update_json.py).
   - **Purged Legacy Onboarding Modules & Obsolete Scripts**: Deleted [`onboard.py`](backend/onboarding/onboard.py), [`requirements_generator.py`](backend/onboarding/requirements_generator.py), [`requirements_synthesizer.py`](backend/onboarding/requirements_synthesizer.py), [`workspace_discovery_agent.py`](backend/onboarding/workspace_discovery_agent.py), [`reset_task.py`](reset_task.py), [`src/requirements.json`](src/requirements.json), [`reset_ticket.py`](scripts/reset_ticket.py), and [`update_json.py`](scripts/update_json.py).
   - **Verified Clean Build**: Zero TypeScript compilation errors (`cmd /c npx tsc --noEmit` code 0) and 100% passing backend test suite.

2. **3-Layer Requirements-Driven Engine & PM Studio UI Pivot**:
   - **Purged Legacy AST Pipeline Short-Circuit**: Removed legacy `if True:` block in `dynamic_domain_generator.py` and unhooked `site_ast_compiler.py` string-template fallbacks, routing all synthesis directly to `generate_llm_ui` in `ui_generator.py`.
   - **SQLite & Schema 3-Layer Upgrade**: Added `layer` column (`PRESENTATION`, `LOGIC`, `INFRASTRUCTURE`) to `schema.sql` and `store.py` SQLite DataStore.
   - **Synthesizer & Requirement Generator Refactor**: Refactored `requirement_generator.py` and `ui_generator.py` to synthesize 3-layer ISO 29148 requirements and full-stack React + FastAPI apps with `// Implements REQ-UI-*` traceability tags and Functional Sandbox Mocks. Added rich domain entity profiles for pizza, bakery, sitting, and e-commerce domains.
   - **PM Studio 3-Layer UI & Presentation Sidebar**: Updated `RequirementsList.tsx` with a 3-Layer Explorer filter bar (`All`, `🎨 UI`, `⚡ Logic`, `💾 API`) and filtered `RequirementControlPanel.tsx` sidebar to ONLY render Presentation layer components (`layer == 'PRESENTATION'`).
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 100% backend unit test pass).

3. **Event-Driven BDD State Machine Requirements & Function-First UI Synthesis**:
   - **Unified BDD Requirements**: Refactored `requirement_generator.py` to synthesize Feature-level requirements with embedded BDD Acceptance Criteria (`Given / When / Then`) and explicit Event/State transition contracts (`User Action ➔ Event ➔ State Transition`).
   - **Function-First, Zero-Fluff Rule**: Removed decorative `__PITCH__` card boxes from `frontend_planning_engine.py` fallback templates and prohibited printing raw prompt text in white decorative hero cards.
   - **Interactive Cart & Checkout Modal Wiring**: Mandated that any Cart component included in synthesis MUST provide state management (`isCartOpen`, `cartItems`), Cart Button toggle handlers, and a complete `CheckoutDrawer` / `CheckoutModal` rendering item lists, item deletion, subtotal calculations, and simulated payment triggers (`[ ⚡ Sandbox Mode ]`).
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 41/41 unit pytest suite passed in 13.58s).

4. **Active Components Collapsible Tree & Sub-Requirement CRUD**:
   - **Collapsible Component Tree View**: Upgraded `RequirementControlPanel.tsx` with a collapsible node hierarchy (`▶ / ▼` toggles) displaying active components, icon badges, component descriptions, and nested child sub-requirements.
   - **Inline Sub-Requirement CRUD**: Added inline creation input forms (`➕ Add Sub-Req`) calling `POST /api/components/sub-requirements/add` and trash bin buttons (`🗑️`) calling `POST /api/components/sub-requirements/delete` to allow dynamically adding/deleting sub-requirements directly from the PM Studio sidebar.
   - **Verified Build Status**: `100% PASS` (0 TypeScript compilation errors via `npx tsc --noEmit`, 41/41 unit pytest suite passed in 13.58s).

5. **Component ID Harmonization, Ghost Component Elimination & Sub-Requirement Tree Linkage**:
   - **ID Harmonization**: Standardized Presentation component IDs across `model.py`, `services.py`, and `requirement_generator.py` to canonical `REQ-UI-{CANONICAL_KEY}` format (e.g. `REQ-UI-CATALOG`, `REQ-UI-CART`, `REQ-UI-TRACKING`).
   - **Ghost Component Elimination**: Purged hardcoded creation of orphan fallback components (`REQ-UI-WORKFLOW` / `REQ-UI-STATUS`) in `_link_logic_reqs_to_ui_components`, ensuring sidebars display strictly active synthesized components.
   - **SQLite Service Layer Linkage Fix**: Fixed `synthesize_kickstart_stack` in `backend/service_layer/services.py` to preserve `parent_id` and `layer` attributes on requirement domain objects when seeding `provable.db`, ensuring sub-requirements appear cleanly under parent component tree nodes.
   - **Verified Build Status**: `100% PASS` (102/102 backend pytest suite passed in 42.90s).

6. **Test Pyramid Streamlining & Heavy E2E Consolidation**:
   - **Single E2E Invariant**: Consolidated all heavy Selenium browser tests into **EXCLUSIVELY 1 E2E test** (`backend/tests/test_e2e_pizza_prompt_sanity.py`).
   - **Unit/Integration Migration**: Moved all non-browser AST compilation, schema synthesis, and domain isolation tests into `backend/tests/unit/`, eliminating redundant Selenium browser startup loops and disk write delays.
   - **Execution Time Optimization**: Reduced full test suite execution time from 80s+ to 42s while maintaining 100% test coverage across 102 tests.
   - **Verified Build Status**: `100% PASS` (102/102 tests passed cleanly).

7. **3-Pillar PM Studio UX Architecture Pivot**:
   - **Page Selector Top Nav**: Implemented [`PageSelectorBar.tsx`](src/components/PageSelectorBar.tsx) for switching active Pages/Views (`/`, `/checkout`, `/tracking`) and creating custom page routes.
   - **Executable Test Spec Cards**: Upgraded [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx) to render Executable Test Spec cards with `🟢 PASS` / `🔴 FAIL` badges and formatted `GIVEN / WHEN / THEN` assertion steps.
   - **DDD Domain Entities Explorer**: Added [`DomainEntitiesPanel.tsx`](src/components/DomainEntitiesPanel.tsx) for managing domain models (`MenuItem`, `Order`, `CartItem`) and editing seed data tables.
   - **Verified Build Status**: `100% PASS` (0 TypeScript errors via `npx tsc --noEmit`, 102/102 backend pytest suite passed in 42.59s).

8. **Responsive Mobile-First PM Studio Layout & JSX Compilation Integrity Test**:
   - **Mobile-First Default Preview**: Changed default `deviceMode` in [`AppPreview.tsx`](src/components/AppPreview.tsx) to `'mobile'` (`375px`), allowing maximum horizontal space for the PM Studio component inspector.
   - **Frame Container Flex Sizing**: Tightened mobile/tablet iframe container flex wrapper (`0 0 375px`), eliminating dark side black bars and allowing the `COMPONENTS` sidebar to expand to fill all remaining horizontal screen space.
   - **Zero Horizontal Scrollbar**: Configured `overflow-x: hidden`, `min-width: 0`, and `flex: 1` on [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx) to guarantee zero horizontal scrollbars.
   - **JSX Compilation Integrity Test Suite**: Created [`backend/tests/unit/test_jsx_compilation_integrity.py`](backend/tests/unit/test_jsx_compilation_integrity.py) to automatically verify `npx tsc --noEmit` and generated AST React code with zero syntax error overlays.
   - **Verified Build & Visual Status**: `100% PASS` (104/104 backend pytest suite passed, 0 TypeScript errors via `npx tsc --noEmit`, verified clean in browser).

9. **Mobile-First Responsive Generator Architecture & Dual-Viewport Visual Auditor**:
   - **Dual-Viewport Visual Auditor**: Refactored [`visual_auditor.py`](backend/onboarding/visual_auditor.py) to capture both `preview_desktop.png` (`1280x800`) and `preview_mobile.png` (`375x812`), auditing both viewports against [`visual_qa.md`](backend/prompts/visual_qa.md) for horizontal overflow, text clipping, and responsive button wrapping.
   - **Mobile-First CSS Resets & Fluid Drawers**: Enforced global CSS resets (`box-sizing: border-box`, `overflow-x: hidden`, `max-width: 100%`) and replaced fixed drawer widths (`width: '380px'`) with fluid bounds (`width: '100%', maxWidth: '380px'`) across all generator templates in [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py) and [`ui_generation.md`](backend/prompts/ui_generation.md).
   - **Verified Build Status**: `100% PASS` (105/105 backend pytest suite passed, 0 TypeScript compilation errors via `npx tsc --noEmit`).

10. **Pizza Ordering Prompt Perfect Output Blueprint & Gap Analysis**:
    - **Diagnostic Gap Analysis**: Identified 5 key areas missing in current synthesis outputs: missing size/crust dynamic pricing multipliers, absence of interactive pizza customizer modal, flat order lists without live status tracking & KDS, lack of 3-layer ISO 29148 trace links (`REQ-UI-*` -> `REQ-SVC-*` -> `REQ-API-*`), and static desktop-only drawer bounds.
    - **Perfect Output Blueprint**: Formulated complete 4-pillar reference specification (`pizza_app_perfect_output_spec.md`), including formal ISO 29148 requirement JSONs, DDD Aggregate (`PizzaOrder`) state machine, pytest BDD test suite, and mobile-first React UI with live price previews, promo engine (`PIZZA20`), and Kitchen Display System (`/kds`).

11. **PM Studio Live Data Fixture Synchronization & Default Order Cleanup**:
    - **Default Order Cleanup**: Fixed initial app generation state in [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py) and [`AppPreview.tsx`](src/components/AppPreview.tsx) so generated pizzeria apps initialize `cart: []` and `orders: []` empty by default.
    - **Data Fixtures API & Service Layer**: Added `GET /api/components/fixtures` and `POST /api/components/fixtures/update` in [`components.py`](backend/entrypoints/routers/components.py) and [`services.py`](backend/service_layer/services.py) to persist fixture CRUD in SQLite (`provable.db`) and regenerate `workspace/src/App.tsx` live.
    - **PM Studio Live HMR**: Wired [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx) `📦 Data Fixtures` tab to backend API, ensuring adding, editing, or deleting items updates `App.tsx` live and reloads the preview iframe via HMR.

12. **Bidirectional Real-Time Data Fixture Sync & E2E Live Project Protection**:
    - **Bidirectional Data Fixtures Sync**: Implemented full two-way real-time data sync between PM Studio and live App preview. PM Studio edits write to SQLite `provable.db` and regenerate `workspace/src/App.tsx` shell live. Live App preview actions (adding to cart, placing orders) sync back via `fetch('/api/components/fixtures/update')` and `window.parent.postMessage({ type: 'FIXTURES_UPDATED', ... })`, updating PM Studio's `dataFixturesByComponent` state live.
    - **Backend Generator Support**: Updated [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py) and [`ui_generator.py`](backend/onboarding/ui_generator.py) to accept `custom_fixtures` and embed bidirectional sync event handlers in synthesized `App.tsx` templates.
    - **Single E2E Test Invariant & Live Project Protection**: Updated [`test_e2e_pizza_prompt_sanity.py`](backend/tests/test_e2e_pizza_prompt_sanity.py) to check for existing live project files in `workspace/src/App.tsx` and skip code generation when a live project exists.
    14. **Full-Stack SQLite Persistence & Menu Addition Live Preview Sync**:
        - **DataStore Column Migration & Model Mapping**: Fixed `backend/db/store.py` (`get_kickstart_state` and `save_kickstart_state`), `backend/domain/model.py` (`KickstartState`), and `backend/adapters/repository.py` (`SqliteKickstartRepository.get`) to persist and retrieve `custom_fixtures` in SQLite `provable.db` under `custom_fixtures_json`.
        - **Cross-Port API Endpoint Resolution**: Added `getApiUrl` helper and updated fallback templates in `backend/onboarding/frontend_planning_engine.py` so preview app running on Vite port `5174` targets `http://localhost:8000/api/components/fixtures` and `http://localhost:8000/api/components/fixtures/update` directly, avoiding 404 proxy errors.
        - **Menu Item Addition Rendering E2E Test**: Added `test_add_new_menu_item_fixture_renders_in_live_preview` to [`test_e2e_pizza_prompt_sanity.py`](backend/tests/e2e/test_e2e_pizza_prompt_sanity.py), verifying that adding new menu items in backend SQLite renders live pizza cards in the browser preview.
        - **Verified 100% Test Pass**: 106/106 unit tests passed and 6/6 heavy E2E Selenium tests passed cleanly.

    15. **Default 4-Step TDD Direct Execution & Order Snapshot Contract Enforcement**:
        - **Subagent Removal & Direct TDD Rule**: Updated `.agents/AGENTS.md` and `vault/HANDOVER.md` to mandate the strict 4-step RED-GREEN-WIRE-VERIFY TDD workflow directly in the primary agent turn without calling subagents.
        - **Domain State & Order Snapshot Contracts**: Updated `backend/prompts/ui_generation.md` with explicit LLM system prompt invariants for catalog-driven cart management and decoupled immutable order tracking snapshots.
        - **Unit Test Suite Verification**: Added [`backend/tests/unit/test_order_snapshot_integrity.py`](backend/tests/unit/test_order_snapshot_integrity.py) to assert prompt contracts and fallback template decoupled order snapshots.
        - **Verified 100% PASS**: 108/108 unit tests passed in 29.65s with zero `import db.store` leaks across routers and service layer.

    16. **Pre-Commit Full Test Suite Invariant Enforcement**:
        - **Mandatory Pre-Commit Test Run Invariant**: Updated `.agents/AGENTS.md` and `vault/HANDOVER.md` to strictly require running the full test suite (`python -m pytest backend/tests/`) before every `git commit` or `git commit --amend` to guarantee zero regressions.

    18. **Standard Benchmark QA Prompt & Universal Domain Entity Architecture**:
        - **Standard Benchmark Prompt**: Codified `"An app to order pizzas"` as the official standard QA benchmark prompt for all testing, synthetic app generation, and quality assurance.
        - **Terminology Pivot (Fixtures ➔ Domain Entities)**: Deprecated legacy "Data Fixtures" terminology across PM Studio in favor of "Domain Entities" / "Entities".
        - **Universal Entity Graph & Linking Invariant**:
          - Primary/Master Catalog components (`catalog`, `menu`, `services`) own root domain entities (`name`, `price`/`rate`, `description`).
          - Universal across all domains (pizzeria, tutor booking, bakery, e-commerce) via automatic master entity role discovery.

    19. **Test Suite Categorization & Directory Isolation (Unit / Integration / E2E)**:
        - **Folder Separation**:
          - `backend/tests/unit/` (102 tests, 28.48s): Strictly fast in-memory unit tests using `FakeUnitOfWork` and isolated domain algorithms.
    20. **Unit Test Speed Optimization (14x Speedup: 28.5s ➔ 2.05s)**:
        - **Bottleneck Resolution**:
          - Refactored `test_chess_game_kickstart_isolation` to use in-memory `FakeUnitOfWork` and domain services rather than heavy on-disk FastAPI/SQLite synthesis (14.08s $\rightarrow$ 0.01s).
          - Created [`backend/tests/unit/conftest.py`](backend/tests/unit/conftest.py) to mock external network requests (`requests.post`/`requests.get`) to Allure Docker container, eliminating 4-second socket connection timeouts in `test_switch_project_service`, `test_switch_project_uses_workspace_adapter`, and `test_generate_allure_report_service`.
    21. **Single Pizza Prompt Benchmark Test Suite Focus & Multi-Domain Test Purge**:
        - **Purged Incompatible Tests**: Deleted `test_flappy_bird_prompt_isolation.py`, `test_multi_domain_synthesis.py`, and chess/flappy test functions from `test_generic_domain_synthesis.py`, `test_prompt_synthesis_flow.py`, and `test_visual_verification_suite.py`.
        - **Single Code Gen Execution**: Synthesized a fresh reference pizza ordering stack in `workspace/` for `"An app to order pizzas"`, verifying 100% Native Domain Terminology, Vite bundle health, and Visual Inspection score (95/100).
        - **Empirical Test Results**: Clean 93/93 test pass (100% PASS) across unit, integration, and e2e suites with minimal LLM token consumption.

    24. **Exhaustive Hardcoding Purge (Zero Remaining Across Backend, Prompts, & Frontend)**:
        - **Dynamic Domain Generator Cleanup**: Replaced 1,673-line monolith in [`dynamic_domain_generator.py`](backend/onboarding/dynamic_domain_generator.py) (containing `PizzaOrder`, `OvenStation`, `BakingStarted`, and 400 lines of Flappy/Pizza UI) with clean, generic, parameter-driven `Order`, `OrderItem`, and `domain_orders` backend templates.
        - **Site AST Compiler Decoupling**: Purged 150-line Flappy Bird/Chess 2D Canvas engine in [`site_ast_compiler.py`](backend/onboarding/site_ast_compiler.py) and replaced with generic `__CUSTOM_CONTAINER_JSX__` rendering any novel AST component node.
        - **Service Layer & Ontology Direct Mapping**: Replaced lingering keyword checks in `get_component_entity_schemas` in [`services.py`](backend/service_layer/services.py) with direct mapping of `ontology.master_entity.attributes`.
        - **Prompt & Template Generality**: Purged hardcoded domain examples from [`domain_discovery.md`](backend/prompts/domain_discovery.md) and [`ui_generation.md`](backend/prompts/ui_generation.md).
        - **Frontend PM Studio Generality**: Purged hardcoded `'Pizza'` fallbacks and initial state entities in [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx), [`AppPreview.tsx`](src/components/AppPreview.tsx), and [`KickstartStudio.tsx`](src/components/KickstartStudio.tsx).
        - **Intent-Based Classification & Registry**: Refactored [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py), [`domain_ontology.py`](backend/onboarding/domain_ontology.py), and [`block_catalog.py`](backend/onboarding/block_catalog.py) to classify interactions via structural verbs and intent (`e_commerce`, `service_booking`, `operations_dashboard`) with zero keyword switchboards.
        - **Empirical Verification**: 100% test pass (103/103 tests in 29.89s), 0 TypeScript errors, 0 `import db.store` leaks, and 0 domain-specific terms across production code, prompts, and frontend UI.

    26. **Full-LLM Free-Form Software Synthesis Architecture Implementation**:
        - **Decommissioned Component Registry**: Deleted [`backend/onboarding/component_registry.py`](backend/onboarding/component_registry.py) (191 lines of pre-baked React snippets) and unhooked `reused_registry_blocks` from planning engines.
        - **Bespoke Domain Deconstruction**: Refactored `_run_component_planning_agent` in [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py) to directly decompose pitch requirements into domain-native bespoke components from ontology contracts.
        - **Domain-Native Spatial Controls Prompting**: Enhanced [`ui_generation.md`](backend/prompts/ui_generation.md) with explicit rules for domain-native spatial and interactive controls (quantum wire canvases, frequency waterfall spectrograms, drone radar HUDs, customizers) avoiding generic grid traps.
        - **Orchestration Graph Documentation**: Authored [`vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md`](vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md) with complete 4-loop Mermaid workflow diagrams.
        - **Empirical Verification**: 100% test pass (91/91 unit tests in 1.85s, 0 TypeScript compilation errors, 0 `import db.store` leaks).

    27. **Total Decommissioning of Block & Category Lego Subsystems**:
        - **Deleted `block_catalog.py` & `category_layouts.py`**: Permanently deleted [`backend/onboarding/block_catalog.py`](backend/onboarding/block_catalog.py) and [`backend/onboarding/category_layouts.py`](backend/onboarding/category_layouts.py).
        - **Dynamic `DomainCapabilitySpec` Engine**: Replaced static 8-block catalog and category slot layouts with pure dynamic `DomainCapabilitySpec` generated from first-principles domain ontology in [`domain_ontology.py`](backend/onboarding/domain_ontology.py).
        - **Purged `CANONICAL_FEATURE_MAP`**: Eradicated static 7-item feature map from [`backend/domain/model.py`](backend/domain/model.py) in favor of dynamic slugification.
        - **Entity Attribute `display_mode` Metadata**: Added typed `display_mode` (`tag_chips`, `badge`, `subtitle`, `visible`, `hidden`) to `EntityAttribute` in backend and frontend schema editors, eliminating unsightly stats blobs and providing clean separation between UI presentation pills and internal data fields.
        - **Ghost Component Purge**: Auxiliary capabilities (`auth`, `reviews`) are strictly pitch-driven and never auto-injected for standard ordering/booking workflows.
        - **Empirical Verification**: 100% test pass across full test suite (103/103 tests in 30.53s) and 0 TypeScript errors.

    28. **Total Eradication of Keyword Heuristics & Hermetic LLM Gateway Isolation**:
        - **Zero Heuristic Invariant in Production**: Eradicated all fallback token-slicers, `stop_words` arrays, and keyword `if` cascades from `storm_domain_ontology` in [`backend/onboarding/domain_ontology.py`](backend/onboarding/domain_ontology.py) and `frontend_planning_engine.py`. Production code directly calls `call_gemini` and parses structured DDD JSON.
        - **Gateway Mock Pattern in `agent_orchestrator.py`**: Updated `call_gemini` network gateway to return contract-valid mock schema responses across all stages (`domain_ontology`, `category_planning`, `component_planning`, `aesthetic_planning`, `pitch_component_analysis`, `ui_generation`) when running without an active API key (`api_key == "mock-key"`), eliminating JSON parse crashes and unhandled 500 errors.
        - **Hermetic Test Harness (`backend/tests/conftest.py`)**: Centralized LLM mock test fixtures into the root `backend/tests/conftest.py` so all unit, integration, and E2E suites execute hermetically without external network dependencies.
        - **Empirical Verification**: 100% test pass (103/103 tests in 30.11s), 0 TypeScript compilation errors, live `analyze_kickstart_pitch` and `synthesize_kickstart_stack` execution verified.

    29. **100% Unlocked Entity Schemas & Dynamic Display Mode Controls**:
        - **Zero Locked Schema Invariant**: Completely eradicated all lock icons and delete restrictions (`isBase = attr.name === 'name' || ...`) in [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx). Every attribute can be renamed, changed in type, assigned custom `display_mode` metadata, or removed.
        - **Inline Schema Attribute Modifiers**: Provided inline Type (`string`, `currency`, `number`, `tags`, `boolean`) and Display Mode (`tag_chips` [Pills], `badge` [Ribbon], `subtitle` [Text], `visible` [Field], `hidden` [Internal State]) dropdown selectors for every attribute.
        - **Schema-Driven Data Fixtures CRUD**: Updated PM Studio Data Fixtures panel to dynamically render form inputs and card presentations matching `entitySchemas[canonicalKey].attributes` instead of hardcoded fields.
        - **Template Display Mode Rendering**: Upgraded catalog card rendering in [`frontend_planning_engine.py`](backend/onboarding/frontend_planning_engine.py) and `App.tsx` templates to render badges at card top-right, subtitles under title, tag pills for tags/specs, and omit hidden fields.
        - **Empirical Verification**: 100% test pass (103/103 tests in 30.06s) and 0 TypeScript compilation errors.

    30. **Dynamic Multi-Attribute Entity Fixture Editor & Multi-Target PostMessage Sync**:
        - **Dynamic Multi-Attribute Inline Editor**: Replaced the 3-input inline edit box with a dynamic multi-attribute editor grid in [`RequirementControlPanel.tsx`](src/components/RequirementControlPanel.tsx). Clicking ✏️ on an entity now opens a grid containing inputs for EVERY attribute defined in that entity's schema (`tags`, `currency`, `number`, `boolean`, `string`, `badge`, `subtitle`), populated with the entity's current values.
        - **Dynamic Entity Creation Form**: The "Add Entity" form at the bottom of the data fixtures panel dynamically generates input controls matching all attributes in `schema.attributes`.
        - **Multi-Target PostMessage Sync**: Saving a schema or editing a fixture now broadcasts `FIXTURES_UPDATED` directly to `window.parent` and all `<iframe>` child windows (`iframe.contentWindow?.postMessage`), enabling immediate live preview reflection without requiring manual browser refreshes.
        - **Empirical Verification**: 100% test pass (103/103 tests in 27.89s) and 0 TypeScript compilation errors.

    31. **Enterprise AppGen TDD Engine Architectural Specification (7 Binding Directives)**:
        - **1. Runtime Schema-Driven UI**: 100% dynamic UI at runtime using `@rjsf/core` (React JSON Schema Form) driven by FastAPI `/openapi.json`. Zero static React scaffolding or LLM frontend generation.
        - **2. Pytest-First & Parameterized**: Standard `@pytest.mark.parametrize` default; `hypothesis` opt-in strictly when flagged for mathematical/range boundary rules.
        - **3. LibCST Code Isolation (`cst_isolator.py`)**: Meta `libcst` preserves formatting, comments, and docstrings during Aggregate Root class extraction and splicing.
        - **4. Test File Write-Locking**: `test_<spec_id>.py` is write-locked during GREEN phase to prevent LLM test tampering.
        - **5. Pytest Execution Hard Timeout**: 5-second hard timeout (`pytest-timeout`) to kill hanging executions / infinite loops.
        - **6. Instant Full-Stack Skeleton (`skeleton_builder.py`)**: Generates domain models, Pydantic DTOs, and FastAPI routers immediately so `openapi.json` exists from second zero.
        - **7. 3-Strike Dead-End Handling**: If GREEN fails 3 times, performs `git reset --hard` to pre-RED state, marks spec `REQUIRES_HUMAN_INTERVENTION` in SQLite, and advances to next spec.
        - **Documentation**: Updated [`vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md`](vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md).

    32. **Enterprise AppGen Core TDD/DDD Engine Implementation Complete (119/119 Tests PASS)**:
        - **Router Engine (`router_engine.py`)**: Implemented structured output decomposing arbitrary business pitches into `DomainStructureSchema` (Entities/Value Objects) and `DomainBehaviorInboxSchema` (Ordered Specs with Given/When/Then and boundary flags).
        - **Instant Skeleton Builder (`skeleton_builder.py`)**: Implemented full-stack code generator scaffolding pure DDD domain models (`domain/<entity>.py`), Abstract/Fake Repositories, Unit of Work, Pydantic DTOs, and FastAPI routers exporting `/openapi.json` from second zero.
        - **LibCST Context Isolator (`cst_isolator.py`)**: Built with Meta `libcst` to extract and splice Aggregate Root classes with 100% preservation of comments, docstrings, formatting, and surrounding code.
        - **Hardened Red-Gate TDD Machine (`tdd_machine.py`)**: Built state machine with programmatic Pytest JSON report evaluation, tautology rejection (Exit Code 0 in RED), syntax/timeout rejection (Exit Code 2), OS-level test file write-locking in GREEN phase, and 3-strike dead-end rollback handling (`git reset --hard` + `REQUIRES_HUMAN_INTERVENTION`).
        - **Behavior Inbox & Spec-CRUD API (`specs.py` & `BehaviorInboxPanel.tsx`)**: Created backend endpoints (`GET /api/specs/inbox`, `POST /api/specs/inbox/add`, `POST /api/specs/inbox/{id}/status`) and PM Studio frontend panel for structured spec creation without free-text prompt drift.
        - **Dual-Track Benchmark Suite (`test_dual_track_benchmarks.py`)**: Fully verified against both **Track A (B2C Pizzeria Ordering)** and **Track B (Industrial FIFO Warehouse Management)** with 100% PASS.
    36. **PM Studio Frontend DDD Refactoring & 3-View Workspace System**:
        - **Global Navigation Simplification (`App.tsx`)**: Removed detached "Requirements" and "Tests" top tabs, integrating all BDD specification and verification workflows directly into the active Domain Aggregate Inspector.
        - **3-View Workspace System (`AppPreview.tsx`)**: Implemented 3 dedicated Workspace views:
          1. `Preview`: Live RJSF / React sandboxed application preview (`:5174`).
          2. `API (Swagger)`: Embedded FastAPI OpenAPI Swagger interface (`:8000/docs`).
          3. `Domain`: Abstract JSON-driven schema visualizer presenting Python Aggregate dataclasses (`Pallet`, `Zone`, `Operator`), attributes, types, invariants, and method signatures without client-side AST parsing.
        - **Industrial Bounded Context Kickstart (`KickstartStudio.tsx`)**: Removed legacy e-commerce example cards and updated copy to "Define Bounded Context" with WMS industrial prompt placeholder and "⚡ Synthesize Architecture".
        - **Engine Room Pivot (`RequirementControlPanel.tsx`)**: Renamed section to "🧬 DOMAIN AGGREGATES", replaced UI component accordions with Domain Aggregate roots (`Pallet`, `Zone`, `Operator`), mapped BDD executable spec payloads (`GIVEN / WHEN / THEN / UNLESS`) directly to `target_aggregate` via `/api/specs/inbox/add`, added live TDD state badges (`🟢 FULFILLED`, `⚡ TDD RUNNING`, `🔴 NEEDS REVIEW`, `⏳ PENDING`), and removed the free-text component addition box.
        - **Empirical Verification**: 100% PASS across TypeScript frontend build (`npm run build` $\rightarrow$ 0 errors) and full Pytest suite (124/124 PASS).

    44. **Documentation & Architectural Synchronization Pass (Vault & Codebase Alignment)**:
        - **Comprehensive Documentation Rewrite**: Updated `README.md`, `.agents/AGENTS.md`, `vault/Home.md`, and all architecture & workflow records across `vault/` to accurately reflect the pivot to the enterprise DDD/TDD AppGen Engine.
        - **Master Consolidated Documentation**: Compiled all 48 documentation files across the vault and `.agents/` into root `FULL_PROJECT_DOCUMENTATION.md` for seamless context ingestion.
        - **Empirical Verification**: 100% PASS across full backend Pytest suite.

    45. **Category A Architectural Alignment Execution (Tasks 1–4 Complete)**:
        - **Nuclear Purge of Legacy Generators (A4)**: Deleted `backend/onboarding/dynamic_domain_generator.py`, `backend/onboarding/site_ast_compiler.py`, and obsolete AST compiler tests. All domain generation strictly routes through `skeleton_builder.py` and `cst_isolator.py`.
        - **Wire Real LLM for GREEN Phase (A1)**: Replaced heuristic stubs in `backend/service_layer/tdd_machine.py` with `synthesize_green_class_implementation` powered by `gemini-2.5-flash` via `agent_orchestrator.py`. Supplies LibCST micro-context and failing pytest AssertionError to synthesize corrected `@dataclass` definitions with Google-style docstrings, zero inline comments, and SHA-256 hash lock anti-cheat validation.
        - **Pure Schema-Driven UI Dynamic Projection (A2)**: Created `frontend/src/components/SchemaDrivenAppPreview.tsx` powered by `@rjsf/core` and `@rjsf/validator-ajv8`, eliminating the secondary Vite dev server iframe (`:5174`) in favor of dynamic schema forms and live entity data tables directly driven by backend OpenAPI / aggregate schemas.
        - **Database Architecture Realignment (A3)**: Reversed database normalization discrepancy in `vault/01-Architecture/Database Schema.md` to formally document dynamic JSON blob storage in SQLite for rapid Bounded Context evolution with ACID guarantees.
        - **Empirical Verification**: 100% PASS across frontend TypeScript build (`npm run build` $\rightarrow$ 0 errors) and full backend Pytest suite.

---

*Updated by Antigravity AI on 2026-08-25 (Category A Discrepancies 100% Resolved; Tasks 1–4 Complete).*

<!-- END_FILE: vault/HANDOVER.md -->

---

## File 7: `vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md`

<!-- START_FILE: vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md -->

# Enterprise AppGen TDD & DDD Engine Architecture

## 1. Executive Summary & Core Invariant
Enterprise AppGen eliminates AI hallucination, context drift, and technical debt by replacing unstructured free-text iterative prompting with a deterministic **TDD (Test-Driven Development) & DDD (Domain-Driven Design)** state machine.

---

## 2. The 7 Core Architectural & Safety Directives

### 1. Runtime Schema-Driven UI (Zero Static React Scaffolding)
- **100% Runtime Dynamic UI**: No static React component code is generated during build time or iterative loops.
- **OpenAPI / JSON Schema Form**: The UI is dynamically rendered at runtime via `@rjsf/core` (React JSON Schema Form) or dynamic schema tables driven directly by FastAPI’s `/openapi.json`.
- **Zero Frontend LLM Involvement**: LLM focus is 100% reserved for pure Python domain logic and architecture.

### 2. Pytest-First with Parameterized Tests
- **Standard Pytest Default**: Test generation defaults to standard `pytest` functions, utilizing `@pytest.mark.parametrize` for table-driven scenarios.
- **Opt-In Hypothesis**: `hypothesis` property-based testing is strictly opt-in, triggered only when the Router-LLM flags a rule as a mathematical, arithmetic, or cryptographic boundary invariant.

### 3. LibCST Code Isolation (`cst_isolator.py`)
- **Meta LibCST**: Built-in `ast` is discarded in favor of `libcst`.
- **Preserved Formatting**: Extracts and splices Aggregate Root classes while strictly preserving whitespace, comments, indentation, and docstrings.

### 4. The 5-Line Hash Lock Anti-Cheat (`tdd_machine.py`)
- **Anti-Tampering Invariant**: During the `GREEN_GEN` phase, a SHA-256 cryptographic hash of `test_<spec_id>.py` is snapshotted (`compute_test_file_hash`).
- After code generation / splicing, the hash is re-verified (`verify_test_file_integrity`). If the hash changed, a `TestTamperingError` is raised immediately.
- Eliminates brittle OS-level filesystem locks (`chmod`) across platforms.

### 5. Pytest Execution Hard Timeout
- **Hanging Protection**: Pytest executions enforce a hard 5-second timeout (`pytest-timeout`).
- Timeouts or infinite loops (e.g. `while True:`) are treated as Exit Code 2 execution errors, triggering immediate rejection and rollback.

### 6. Full-Stack Skeleton from Second Zero
- **Instant OpenAPI Contract**: `skeleton_builder.py` immediately scaffolds domain classes, Pydantic DTOs (`schemas.py`), and basic FastAPI routers (`entrypoints/routers/`).
- `/openapi.json` is available from iteration 1 to immediately power the runtime UI.

### 7. 3-Strike Dead-End Handling & Rollback
- **Safety Fallback**: If the GREEN phase fails after 3 consecutive repair attempts:
  1. Automatic Git rollback (`git reset --hard`) to the state immediately preceding the RED phase.
  2. The specification in SQLite is flagged with status `REQUIRES_HUMAN_INTERVENTION`.
  3. The error is logged and the engine automatically pops the next specification (`POP_SPEC`).

---

## 3. Active Architecture Implementation

> [!NOTE]
> **LLM-Driven LibCST Splicing (GREEN Phase)**: The GREEN phase uses `synthesize_green_class_implementation` powered by `gemini-2.5-flash` to synthesize domain class modifications directly against the LibCST micro-context and failing pytest `AssertionError` with strict SHA-256 hash lock verification.

> [!NOTE]
> **Runtime Schema-Driven UI Dynamic Projection**: Runtime Schema-Driven UI via FastAPI `/openapi.json` and `@rjsf/core` in `SchemaDrivenAppPreview.tsx` completely eliminates frontend LLM hallucinations and secondary Vite dev server dependencies, projecting reactive forms and live entity data directly from backend contracts.


---

## 4. Pillar Breakdown & Workflow Diagram

```mermaid
flowchart TD
    subgraph Intake ["1. Intake & Routing"]
        Pitch["Natural Language Pitch"] --> RouterEngine["router_engine.py"]
        RouterEngine --> Struct["DomainStructureSchema"]
        RouterEngine --> Inbox["DomainBehaviorInboxSchema"]
    end

    subgraph Skeleton ["2. Full-Stack Skeleton Builder"]
        Struct --> SkeletonGen["skeleton_builder.py"]
        SkeletonGen --> Domain["domain/<entity>.py (Dataclasses)"]
        SkeletonGen --> DTO["entrypoints/schemas.py (Pydantic DTOs)"]
        SkeletonGen --> Routers["entrypoints/routers/<entity>.py (FastAPI)"]
        SkeletonGen --> InitialCommit["Git Commit: 'feat: initial domain skeleton & openapi'"]
    end

    subgraph TDDStateMachine ["3. TDD State Machine (LibCST & Red-Gate)"]
        Inbox --> PopSpec["POP_SPEC: Next Rule"]
        PopSpec --> RedGen["RED_GEN: Generate test_<spec_id>.py"]
        RedGen --> RedRun{"RED_GATE: pytest (Exit 1 & AssertionError, 5s timeout)"}
        RedRun -- Pass/SyntaxErr --> RejectRed["Reject & Retry Test"]
        RedRun -- Approved RED --> HashLock["5-Line Hash Lock: Snapshot SHA-256"]
        
        HashLock --> GreenGen["GREEN_GEN: LibCST Micro-Context Slice -> Generate Domain Logic"]
        GreenGen --> GreenRun{"GREEN_GATE: pytest (Exit 0, 5s timeout, Hash Verified)"}
        GreenRun -- Pass --> CommitSpec["Git Commit: 'feat(spec): REQ-xxx'"]
        GreenRun -- Fail (Tries < 3) --> RetryGreen["Retry Domain Logic"]
        GreenRun -- Fail (Tries == 3) --> DeadEnd["Git Rollback -> Mark REQUIRES_HUMAN_INTERVENTION"]
        DeadEnd --> PopSpec
        CommitSpec --> PopSpec
    end

    subgraph UIProjection ["4. Runtime Schema-Driven UI"]
        Routers --> OpenAPI["FastAPI /openapi.json"]
        OpenAPI --> RJSF["Dynamic Schema UI & Table Renderer"]
        RJSF --> AppView["Live Responsive Web Interface"]
    end
```

---

## 5. Cross-References
- [[System Architecture]]
- [[Shift-Left TDD Workflow]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]

<!-- END_FILE: vault/01-Architecture/Enterprise-AppGen-TDD-Engine-Architecture.md -->

---

## File 8: `vault/01-Architecture/System Architecture.md`

<!-- START_FILE: vault/01-Architecture/System Architecture.md -->

# System Architecture

Provable is an enterprise-grade, deterministic Domain-Driven Design (DDD) and Test-Driven Development (TDD) AppGen Engine. It features a React-based PM Studio frontend and a FastAPI backend orchestrating a deterministic TDD state machine (`tdd_machine.py`), router engine (`router_engine.py`), instant full-stack skeleton builder (`skeleton_builder.py`), and LibCST surgical code splicing (`cst_isolator.py`).

```mermaid
graph TD
    subgraph Frontend [PM Studio Frontend - React / Vite]
        App[App.tsx Entrypoint] --> ProjectSelector[components/ProjectSelector.tsx]
        App --> Kickstart[components/KickstartStudio.tsx Bounded Context Studio]
        App --> AppPreview[components/AppPreview.tsx 3-View System: Preview / Swagger / Domain]
        App --> BehaviorInbox[components/BehaviorInboxPanel.tsx BDD Spec CRUD]
        App --> ReqControl[components/RequirementControlPanel.tsx Domain Aggregates]
        App --> DomainEntities[components/DomainEntitiesPanel.tsx Dynamic Entity Data]
        App --> CoverageHub[components/CoverageHub.tsx Allure Matrix]
    end

    subgraph Backend [FastAPI Backend Engine]
        API[main.py REST API] --> Store[db/store.py DataStore API]
        API --> RouterEngine[onboarding/router_engine.py Domain Decomposition]
        API --> SkeletonBuilder[onboarding/skeleton_builder.py Instant Full-Stack Skeleton]
        API --> CSTIsolator[onboarding/cst_isolator.py Meta LibCST Splicer]
        API --> TDDMachine[service_layer/tdd_machine.py Red-Gate & Hash-Lock Engine]
        API --> ServiceLayer[service_layer/services.py Use Cases]
        ServiceLayer --> UoW[service_layer/unit_of_work.py Sqlite/Fake UoW]
    end

    subgraph DB [Persistence Layer]
        Store --> SQLite[SQLite provable.db Database]
        Store <-->|Bidirectional Sync| SDoc[requirements/requirements.sdoc]
    end

    subgraph Workspace [Target Project Sandbox]
        SkeletonBuilder --> TargetCode[workspace/src/domain/ Aggregate Roots]
        SkeletonBuilder --> TargetAdapters[workspace/src/adapters/ Repositories]
        SkeletonBuilder --> TargetRouters[workspace/src/entrypoints/routers/ FastAPI Routers]
        TargetRouters --> TargetOpenAPI[FastAPI /openapi.json Contract]
        TargetCode <-->|TDD Machine & Pytest| WorkspaceTests[workspace/tests/unit/]
    end

    subgraph Docker [Allure Reporting Container]
        ServiceLayer --> AllureContainer[Allure Docker Service :5050]
        CoverageHub --> AllureContainer
    end

    App <-->|REST API / JSON| API
```

---

## Subsystem Breakdown

### PM Studio Frontend (`frontend/src/`)
Built with React, TypeScript, Vite, and custom CSS styling across modular views:
- **`App.tsx`**: Top-level layout manager, project banner, and global navigation.
- **`components/KickstartStudio.tsx`**: Bounded context intake studio accepting industrial domain pitches, triggering decomposition and skeleton synthesis, and managing workspace resets (`/api/onboarding/reset`).
- **`components/AppPreview.tsx`**: 3-View Workspace System hosting:
  1. `Preview`: Live sandboxed web preview (`http://localhost:5174/`).
  2. `API (Swagger)`: Embedded FastAPI OpenAPI Swagger interface (`http://localhost:8000/docs`).
  3. `Domain`: Abstract JSON-driven schema visualizer presenting Python Aggregate dataclasses (`Pallet`, `Zone`, `Operator`), attributes, types, invariants, and method signatures.
- **`components/BehaviorInboxPanel.tsx`**: Structured BDD specification inbox for atomic business rules (`GIVEN / WHEN / THEN`), target aggregate binding, and mathematical/boundary flags (triggering Hypothesis).
- **`components/RequirementControlPanel.tsx`**: Domain aggregate tree view with inline BDD test specs, live TDD state badges (`🟢 FULFILLED`, `⚡ TDD RUNNING`, `🔴 NEEDS REVIEW`, `⏳ PENDING`), and dynamic attribute controls.
- **`components/DomainEntitiesPanel.tsx`**: Dynamic entity data fixture viewer and editor bound directly to active schema attributes.
- **`components/CoverageHub.tsx`**: Aggregates requirement-to-test mapping matrices and embeds the live Allure Docker portal (`:5050`).

### FastAPI Backend Engine (`backend/`)
- **`main.py` / `app.py`**: FastAPI application mounting routers for specs, kickstart, onboarding, requirements, components, projects, and testing.
- **`onboarding/router_engine.py`**: Decomposes natural language pitches into `DomainStructureSchema` (Entities/Value Objects) and `DomainBehaviorInboxSchema` (Atomic BDD specs).
- **`onboarding/skeleton_builder.py`**: Scaffolds pure DDD domain models, Abstract/Fake Repositories, Unit of Work, Pydantic DTOs, and FastAPI routers exporting `/openapi.json` from second zero.
- **`onboarding/cst_isolator.py`**: Uses Meta `libcst` to extract and splice Aggregate Root classes with 100% preservation of comments, docstrings, formatting, and surrounding code.
- **`service_layer/tdd_machine.py`**: Red-Gate TDD state machine with programmatic Pytest evaluation, tautology rejection (Exit 0 in RED), syntax/timeout rejection (Exit 2), SHA-256 5-line test integrity hash locking, and 3-strike dead-end rollback handling.
- **`db/store.py`**: SQLite database wrapper (`provable.db`) managing relational data for requirements, test cases, projects, and kickstart states.

---

## 🏛️ Discrepancies & Architectural Evolution

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original doc specified an LLM-driven micro-context repair prompt via LibCST slicing during GREEN_GEN, whereas the current code in tdd_machine.py relies on hardcoded string-matching heuristic stubs (e.g. inject validate_invariants or weight: float). The LLM-driven LibCST repair is architecturally superior and generalizable.]

> [!NOTE]
> [DISCREPANCY: Doc approach better - Pure Runtime Schema-Driven UI via OpenAPI dynamic form generation eliminates frontend LLM hallucinations and maintenance overhead, whereas the codebase still maintains legacy TSX generators.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[Universal-Dynamic-Domain-AST-Generator]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]
- [[05-DDD-TDD-Architecture-Guidelines]]
- [[Frontend Components]]
- [[Backend REST API]]

<!-- END_FILE: vault/01-Architecture/System Architecture.md -->

---

## File 9: `vault/01-Architecture/Universal-Dynamic-Domain-AST-Generator.md`

<!-- START_FILE: vault/01-Architecture/Universal-Dynamic-Domain-AST-Generator.md -->

# Universal Dynamic Domain AST Generator & Skeleton Engine

The **Universal Dynamic Domain Generator** comprises the **Router Engine** ([`backend/onboarding/router_engine.py`](backend/onboarding/router_engine.py)), **Skeleton Builder** ([`backend/onboarding/skeleton_builder.py`](backend/onboarding/skeleton_builder.py)), and **LibCST Isolator** ([`backend/onboarding/cst_isolator.py`](backend/onboarding/cst_isolator.py)). It transforms arbitrary natural language business pitches into 100% contract-first, clean Domain-Driven Design (DDD) backend modules and OpenAPI schemas.

```mermaid
graph TD
    Pitch["User Business Pitch (e.g. Industrial WMS)"] --> Router["1. Router Engine (router_engine.py)"]
    Router --> Struct["DomainStructureSchema: Entities & Value Objects"]
    Router --> Inbox["DomainBehaviorInboxSchema: Atomic BDD Specs"]
    
    subgraph SKELETON_BUILDER ["Instant Full-Stack Skeleton Builder"]
        Struct --> VO["Value Objects -> Dataclasses"]
        Struct --> AGG["Aggregate Roots -> Python Classes"]
        Struct --> REPO["Abstract & Fake Repositories"]
        Struct --> UOW["Unit of Work (Sqlite/Fake)"]
        Struct --> DTO["Pydantic DTO Schemas"]
        Struct --> ROUTERS["FastAPI Presentation Routers"]
        ROUTERS --> OPENAPI["FastAPI /openapi.json from Second 0"]
    end

    subgraph TDD_LIBCST ["LibCST Surgical Splicing & Red-Gate TDD"]
        Inbox --> TDD["Red-Gate TDD State Machine (tdd_machine.py)"]
        TDD --> CST["LibCST Class Extraction & Splicing (cst_isolator.py)"]
        TDD --> HashLock["5-Line SHA-256 Anti-Cheat Hash Lock"]
    end

    SKELETON_BUILDER --> Verified["2. Instant Verified OpenAPI Stack"]
    TDD_LIBCST --> Verified
```

---

## 🏛️ Key Architectural Features

### 1. Pure DDD Layer Isolation
- **Domain Layer (`workspace/src/domain/`)**: Pure dataclasses with 0 framework or ORM dependencies.
- **Adapters Layer (`workspace/src/adapters/`)**: Abstract repository definitions and in-memory test doubles (`FakeRepository`).
- **Service Layer (`workspace/src/service_layer/`)**: `AbstractUnitOfWork` and `FakeUnitOfWork` for transaction management.
- **Entrypoints (`workspace/src/entrypoints/`)**: FastAPI routers and Pydantic schemas.

### 2. Surgical LibCST Class Splicing (`cst_isolator.py`)
- Replaces legacy whole-file AST string regeneration with surgical class extraction (`extract_class_cst`) and splicing (`splice_class_cst`) using Meta `libcst`.
- Preserves 100% of formatting, comments, and Google-style docstrings.

---

## 🛡️ Active Generator Architecture

> [!NOTE]
> **Pure LibCST & Skeleton Generator Pipeline**: Legacy monolithic string-template generators (`dynamic_domain_generator.py` and `site_ast_compiler.py`) have been entirely purged. All domain synthesis routes through `skeleton_builder.py` and Meta `cst_isolator.py`.


---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[05-DDD-TDD-Architecture-Guidelines]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]
- [[Onboarding and Discovery Workflow]]

<!-- END_FILE: vault/01-Architecture/Universal-Dynamic-Domain-AST-Generator.md -->

---

## File 10: `vault/01-Architecture/Frontend Components.md`

<!-- START_FILE: vault/01-Architecture/Frontend Components.md -->

# Frontend Components

The PM Studio frontend ([`frontend/src/`](frontend/src)) is a modern React 18 application built with TypeScript, Vite, and custom CSS design system tokens.

---

## 🧩 Component Sitemap

```mermaid
graph TD
    App["App.tsx Shell"] --> Header["Header Nav & Project Selector"]
    Header --> ProjectSelector["components/ProjectSelector.tsx"]
    
    App --> KickstartStudio["components/KickstartStudio.tsx Intake Studio"]
    KickstartStudio --> AppPreview["components/AppPreview.tsx 3-View System"]
    
    AppPreview --> PageSelectorBar["components/PageSelectorBar.tsx Top Page Selector"]
    AppPreview --> ReqControl["components/RequirementControlPanel.tsx Domain Aggregates Panel"]
    AppPreview --> DomainInspector["Domain Visualizer Inspector (@dataclass Class Projection)"]
    
    ReqControl --> BehaviorInbox["components/BehaviorInboxPanel.tsx BDD Spec CRUD"]
    ReqControl --> DomainEntities["components/DomainEntitiesPanel.tsx Dynamic Entity Fixtures"]
    
    App --> CoverageHub["components/CoverageHub.tsx Allure Matrix"]
```

---

## 📦 Component Descriptions

### 1. `frontend/src/App.tsx` (Application Shell)
- **Responsibility**: Top-level layout manager, project banner, and global view state router (`Domain`, `Requirements`, `Tests`).

### 2. `frontend/src/components/KickstartStudio.tsx` (Bounded Context Studio)
- **Responsibility**: Intake form accepting industrial bounded context descriptions, triggering synthesis via `POST /api/onboarding/kickstart`, and initiating physical workspace resets (`POST /api/onboarding/reset`).

### 3. `frontend/src/components/AppPreview.tsx` (3-View Workspace System)
- **Responsibility**: 3-in-1 workspace system providing:
  1. `Preview`: Live Vite sandbox iframe (`http://localhost:5174/`).
  2. `API (Swagger)`: Embedded FastAPI OpenAPI Swagger UI (`http://localhost:8000/docs`).
  3. `Domain`: Abstract JSON-driven schema visualizer presenting Python Aggregate dataclasses (`Pallet`, `Zone`, `Operator`), attributes, types, invariants, and method signatures without client-side AST parsing.

### 4. `frontend/src/components/BehaviorInboxPanel.tsx` (BDD Specification Inbox)
- **Responsibility**: Structured specification inbox for managing atomic business rules (`GIVEN / WHEN / THEN`), target aggregate binding, mathematical boundary flags, and execution status (`PENDING`, `IN_PROGRESS`, `FULFILLED`, `REQUIRES_HUMAN_INTERVENTION`).

### 5. `frontend/src/components/RequirementControlPanel.tsx` (Domain Aggregates Panel)
- **Responsibility**: Collapsible tree inspector for active domain aggregates, inline BDD spec creation forms, and attribute schema controls.

### 6. `frontend/src/components/DomainEntitiesPanel.tsx` (Dynamic Entity Fixtures)
- **Responsibility**: Dynamic CRUD panel for entity data instances bound directly to schema attribute metadata.

### 7. `frontend/src/components/CoverageHub.tsx` (Coverage Matrix)
- **Responsibility**: Embeds the containerized Allure reporting dashboard (`http://localhost:5050/allure-docker-service/projects/default/reports/latest/index.html`).

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original PM Studio architecture envisioned a 100% dumb schema-driven UI using `@rjsf/core` directly rendering forms from `/openapi.json` with zero custom hardcoded DOM structures. While the active React frontend has been cleaned of domain keywords, it currently uses a hybrid iframe (:5174) and custom table visualizer rather than a pure `@rjsf/core` schema form runner.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[PM-Studio-UX-Architecture-And-Direction]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]

<!-- END_FILE: vault/01-Architecture/Frontend Components.md -->

---

## File 11: `vault/01-Architecture/Backend REST API.md`

<!-- START_FILE: vault/01-Architecture/Backend REST API.md -->

# Backend REST API Specification & Data Contracts

The FastAPI backend application (`backend/app.py` / `backend/main.py`) serves as the primary REST API and DDD service layer engine for PM Studio, database persistence, and TDD execution control.

- **Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## 🏛️ Active Router Specifications

### 1. Behavior Inbox & BDD Specs Router (`backend/entrypoints/routers/specs.py`)

- **`GET /api/specs/inbox`**: Returns `List[BusinessSpecItem]` of atomic BDD specifications.
- **`POST /api/specs/inbox/add`**: Adds a new atomic BDD specification item.
  - **Body**:
    ```json
    {
      "title": "Enforce Pallet Weight Limit",
      "description": "Reject placement if total weight exceeds capacity",
      "given_when_then": "Given a Zone with 1000kg max When Pallet of 1200kg placed Then raise CapacityExceeded",
      "target_aggregate": "Zone",
      "is_mathematical_boundary": true,
      "priority": "High"
    }
    ```
- **`POST /api/specs/inbox/{spec_id}/status`**: Updates spec execution status (`PENDING`, `IN_PROGRESS`, `FULFILLED`, `REQUIRES_HUMAN_INTERVENTION`).

---

### 2. Onboarding & Kickstart Router (`backend/entrypoints/routers/onboarding.py` & `kickstart.py`)

- **`POST /api/onboarding/kickstart`**: Ingests natural language business pitch, derives domain structure, scaffolds initial DDD skeleton, and saves state.
  - **Body**: `{"pitch": "An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators."}`
- **`GET /api/onboarding/aggregates`**: Returns list of discovered DDD Aggregate Roots, attributes, types, and invariant rules for dynamic UI projection.
- **`POST /api/onboarding/reset`**: **Physical Workspace Nuke & DB Purge**. Deletes all generated files in `workspace/src/` and `workspace/tests/`, wipes database records across all tables, and restores blank scaffold.
- **`GET /api/kickstart/state`**: Returns current synthesis status, pitch, and entity schemas.

---

### 3. Components & Entity Fixtures Router (`backend/entrypoints/routers/components.py`)

- **`GET /api/components/entities`**: Returns domain entity schemas and active fixtures data.
- **`GET /api/components/fixtures`**: Returns data fixtures mapped by component.
- **`POST /api/components/fixtures/update`**: Updates fixture items for a given entity key and regenerates live preview.
- **`POST /api/components/sub-requirements/add`**: Adds an inline sub-requirement node.
- **`POST /api/components/sub-requirements/delete`**: Removes a sub-requirement node.

---

### 4. Requirements & Testing Routers (`backend/entrypoints/routers/requirements.py` & `testing.py`)

- **`GET /api/requirements`**: Returns hierarchical requirements tree for Explorer view.
- **`POST /api/requirements`**: Creates a requirement and exports `.sdoc`.
- **`PUT /api/requirements/{req_id}`**: Updates requirement metadata.
- **`DELETE /api/requirements/{req_id}`**: Deletes a requirement node.
- **`POST /api/requirements/{req_id}/generate-test`**: Generates a failing BDD test spec.
- **`POST /api/requirements/{req_id}/run-test`**: Executes pytest on the target test file.
- **`GET /api/coverage`**: Returns coverage percentage and test execution matrices.
- **`POST /api/coverage/generate-report`**: Triggers Allure Docker report generation.

---

### 5. Projects Management Router (`backend/entrypoints/routers/projects.py`)

- **`GET /api/projects`**: Lists available workspaces.
- **`GET /api/projects/active`**: Returns active workspace path and configuration.
- **`POST /api/projects/switch`**: Switches active workspace directory.
- **`POST /api/projects/reset-all`**: Clears active database tables.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original REST API specification documented explicit code review queue endpoints (`/api/review-queue`, `/api/requirements/{id}/merge`, `/api/requirements/{id}/reject`) with branch diff inspections. While the project evolved toward deterministic local RED-GREEN-COMMIT TDD loops without git branch PR queues, an explicit audit log endpoint for TDD state transitions and rollback records provides superior enterprise visibility.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Database Schema]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]

<!-- END_FILE: vault/01-Architecture/Backend REST API.md -->

---

## File 12: `vault/01-Architecture/Database Schema.md`

<!-- START_FILE: vault/01-Architecture/Database Schema.md -->

# Database Schema & DataStore API

Provable manages its application state using an SQLite database located dynamically per-project under `workspace/requirements/provable.db`. All database interactions are encapsulated by `backend/db/store.py` and initialized using SQL definitions in `backend/db/schema.sql`.

```mermaid
erDiagram
    requirements ||--o{ test_cases : "has"
    requirements ||--o{ agent_runs : "triggers"
    requirements {
        text id PK
        text title
        text description
        text type "Folder|Requirement|Task|Bug"
        text layer "PRESENTATION|LOGIC|INFRASTRUCTURE"
        text priority "High|Med|Low"
        text status "Backlog|In Progress|Review|Conflict|Done"
        text parent_id FK
        text component_type
        text component_meta
        text dependencies "JSON array"
        text assigned_agents "JSON array"
        text proposed_code
        text feedback
        timestamp created_at
        timestamp updated_at
    }
    test_cases {
        text id PK
        text requirement_id FK
        text title
        text given_text
        text when_text
        text then_text
        text file_path
        text last_result "pass|fail|skip|pending|never_run"
        text allure_id
        text failure_message
        timestamp created_at
    }
    agent_runs {
        text id PK
        text ticket_id
        text requirement_id
        text status "running|success|failed|cancelled"
        timestamp started_at
        timestamp completed_at
        integer attempts
        text stages_json "JSON array"
    }
```

---

## Verbatim Database DDL (`backend/db/schema.sql`)

```sql
-- Provable data schema
CREATE TABLE IF NOT EXISTS requirements (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    type        TEXT CHECK(type IN ('Folder','Requirement','Task','Bug')),
    layer       TEXT CHECK(layer IN ('PRESENTATION','LOGIC','INFRASTRUCTURE')) DEFAULT 'LOGIC',
    priority    TEXT DEFAULT 'Med',
    status      TEXT DEFAULT 'Backlog',
    parent_id   TEXT REFERENCES requirements(id),
    component_type TEXT DEFAULT 'custom',
    component_meta TEXT DEFAULT '{}',
    jira_key    TEXT,
    sdoc_uid    TEXT,
    dependencies TEXT DEFAULT '[]',   -- JSON array of requirement IDs
    assigned_agents TEXT DEFAULT '[]',-- JSON array of agent roles
    proposed_code TEXT,
    feedback    TEXT DEFAULT '',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_cases (
    id              TEXT PRIMARY KEY,
    requirement_id  TEXT REFERENCES requirements(id),
    title           TEXT NOT NULL,
    given_text      TEXT DEFAULT '',
    when_text       TEXT DEFAULT '',
    then_text       TEXT DEFAULT '',
    file_path       TEXT,
    last_result     TEXT CHECK(last_result IN ('pass','fail','skip','pending','never_run')) DEFAULT 'never_run',
    allure_id       TEXT,
    failure_message TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id              TEXT PRIMARY KEY,
    ticket_id       TEXT,
    jira_key        TEXT,
    requirement_id  TEXT,
    status          TEXT CHECK(status IN ('running','success','failed','cancelled')) DEFAULT 'running',
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    attempts        INTEGER DEFAULT 0,
    stages_json     TEXT DEFAULT '[]'
);

-- Trigger to auto-update updated_at on requirements
CREATE TRIGGER IF NOT EXISTS requirements_updated_at
    AFTER UPDATE ON requirements
    FOR EACH ROW
    BEGIN
        UPDATE requirements SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
```

---

## DataStore API Specification (`backend/db/store.py`)

The `store.py` module manages SQLite operations and triggers bidirectional sync:

- **`get_all_requirements()` / `get_requirement(req_id)` / `create_requirement(data)` / `update_requirement(req_id, updates)` / `delete_requirement(req_id)`**
- **`get_test_cases_for_requirement(req_id)` / `create_test_case(data)` / `update_test_case_result(test_id, result, failure_msg)`**
- **`save_kickstart_state(pitch, domain_model, synthesized, entity_schemas, custom_fixtures)` / `get_kickstart_state()`**
- **`save_active_project(name, path, settings)` / `list_projects()` / `wipe_database()`**

---

## 🏛️ Architectural Invariants & Dynamic Schema Storage

> [!NOTE]
> **Dynamic Bounded Context JSON Storage**: To support rapidly evolving, dynamic Bounded Contexts, we strictly utilize JSON blob columns in SQLite rather than normalized relational EAV (Entity-Attribute-Value) tables. This provides NoSQL-like flexibility with SQLite's ACID guarantees.


---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Backend REST API]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]

<!-- END_FILE: vault/01-Architecture/Database Schema.md -->

---

## File 13: `vault/01-Architecture/Integrations.md`

<!-- START_FILE: vault/01-Architecture/Integrations.md -->

# Integrations Engine & Data Formats

Provable supports external tool syncing through integrations located in `backend/integrations/`. These clients bridge Provable's local SQLite database with StrictDoc and containerized Allure reporting.

---

## 1. StrictDoc Client (`strictdoc_client.py`)

[StrictDoc](https://github.com/strictdoc-project/strictdoc) uses text-based `.sdoc` specification files.

### Standard `.sdoc` Block Syntax
```
[DOCUMENT]
TITLE: Document Title

[SECTION]
TITLE: Section Title

[REQUIREMENT]
UID: REQ-PM-001
TITLE: Simplified Specification Explorer View
STATEMENT: Requirement description text...
REQ_TYPE: Requirement
PRIORITY: High
STATUS: Backlog

[/SECTION]
```

### Sync Functions
- `sync_sdoc_to_db(sdoc_path: str = "requirements/requirements.sdoc") -> None`: Reads `.sdoc` file on startup and populates SQLite `requirements` table.
- `export_sdoc(sdoc_path: str = "requirements/requirements.sdoc") -> None`: Writes SQLite requirements back out to `.sdoc` plain text.

---

## 2. Allure Client (`allure_client.py`)

Allure Docker Service API client for containerized visual test reporting.
- **Base URL**: `http://localhost:5050`
- **Endpoints**:
  - `POST /projects`: Registers project ID `provable`.
  - `POST /send-results?project_id=provable`: Uploads pytest JSON results from `workspace/allure-results/`.
  - `GET /generate-report?project_id=provable`: Triggers HTML report rendering.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original integrations design included bi-directional syncing with enterprise issue trackers (Jira/Linear). While Jira was intentionally purged to simplify the deterministic local AppGen engine, an outbound webhook or event publisher for CI/CD integration remains valuable for production deployments.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Database Schema]]
- [[Shift-Left TDD Workflow]]

<!-- END_FILE: vault/01-Architecture/Integrations.md -->

---

## File 14: `vault/01-Architecture/LLM Abstraction and Prompts.md`

<!-- START_FILE: vault/01-Architecture/LLM Abstraction and Prompts.md -->

# LLM Abstraction Layer & System Prompt Catalog

Provable routes all LLM calls through a model-agnostic abstraction layer defined in `backend/config_loader.py` and `backend/agent_orchestrator.py`. Prompts are externalized into dedicated markdown files in `backend/prompts/`.

---

## 1. Model Configuration (`backend/config/models.yaml`)

Models and provider settings are configured centrally in YAML:

```yaml
default:
  model: gemini-2.5-flash
  base_url: https://generativelanguage.googleapis.com/v1beta/openai/
  api_key_env: LLM_API_KEY

stages:
  code_generation:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  visual_qa:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  task_decomposition:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  merge_resolution:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  requirement_audit:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  test_case_generation:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY
```

---

## 2. Prompt Template Catalog & Format Rules

All prompt files reside in `backend/prompts/`. They dictate system persona, context placeholders, and output schemas:

### 1. `router_decomposition.md`
- **Purpose**: Decomposes raw natural language business pitches into structured `DomainStructureSchema` (Entities/Value Objects/Aggregate Roots) and `DomainBehaviorInboxSchema` (Atomic BDD Given/When/Then specs with mathematical boundary flags).
- **Placeholders**: `{business_pitch}`.

### 2. `domain_discovery.md`
- **Purpose**: Extracts ubiquitous language, core domain nouns, entity attributes, commands, and domain invariants from raw business pitches.
- **Placeholders**: `{business_pitch}`.

### 3. `test_case_generation.md`
- **Purpose**: Generates failing pytest BDD test cases (`workspace/tests/test_<REQ_ID>.py`) establishing the initial TDD Red state with BDD Given/When/Then docstrings.
- **Placeholders**: `{req_id}`, `{title}`, `{description}`, `{test_case_id}`.

### 4. `code_generation.md`
- **Purpose**: Generates drop-in source code files and accompanying pytest test files.
- **Placeholders**: `{current_workspace_context}`, `{task_desc}`, `{feedback_note_attempt}`, `{test_context}`, `{test_file_path}`, `{parent_id}`.

### 5. `visual_qa.md` & `visual_audit.md`
- **Purpose**: Multi-modal vision analysis evaluating mobile (`375x812`) and desktop (`1280x800`) screenshots against layout defect rubrics.
- **Placeholders**: `{proposed_code}`, `{screen_type}`.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - Externalizing all prompt templates into backend/prompts/*.md enables independent prompt iteration without touching Python code. However, ui_generation.md still contains references to legacy e-commerce cart and pizza order snapshot patterns, which should be sanitized to pure industrial domain standards.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]

<!-- END_FILE: vault/01-Architecture/LLM Abstraction and Prompts.md -->

---

## File 15: `vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md`

<!-- START_FILE: vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md -->

# PM Studio UX Architecture, Design Guidelines & Strategic Direction

This document captures the UX philosophy, component layout hierarchy, design invariants, and strategic product direction for **Provable PM Studio**.

---

## 🏛️ 1. Core UX Philosophy: 3-Pillar Architecture

PM Studio moves away from cluttered dashboard overlays and text-heavy sub-requirements, organizing the application management workflow into **3 clear pillars**:

### Pillar 1: Top Pages & Views Selector Bar (`PageSelectorBar.tsx`)
- **Location**: Top section of the application preview canvas.
- **Function**: Displays all active views/routes in the synthesized application (`🏠 Home Page (/)`, `💳 Checkout Page (/checkout)`, `📦 Order Tracking View (/tracking)`).
- **Interactions**:
  - Click any page chip to switch active preview view.
  - Click `➕ Add Page` to define a new custom page route inline (`Page Name` + `Route`).
  - Click `✕` to delete custom non-home pages.

### Pillar 2: Executable Test Spec Cards (`RequirementControlPanel.tsx` ➔ `Tab 1: 🧪 Executable Tests`)
- **Location**: Tab 1 inside each expanded component card in the right/bottom sidebar.
- **Function**: Replaces plain-text sub-requirements with **Executable Test Specs**.
- **Visual Spec Cards**:
  - `🟢 PASS` / `🔴 FAIL` status badges.
  - Interactive BDD Builder Action Chips (`+ GIVEN`, `+ WHEN`, `+ THEN`) pre-filling assertion prefixes with 1 click.
  - Context-aware behavioral example placeholders (e.g., `e.g. When item added, update subtotal & badge count...`).
  - Explicit `➕ Add Test` action button.
  - Trash bin `🗑️` button to delete test specs.

### Pillar 3: Domain Entities CRUD & Universal Entity Graph (`RequirementControlPanel.tsx` ➔ `Tab 2: 🧬 Entities`)
- **Location**: Tab 2 inside each expanded component card.
- **Function**: Directly binds Domain Entities (e.g. `MenuItem`, `CartItem`, `Order`) to the component cards they belong to, avoiding separate messy floating overlays.
- **Terminology**: Migrated from legacy "Data Fixtures" to **Domain Entities**.
- **Universal Entity Graph & Linking Invariant**:
  - **Master Catalog Components** (`catalog`, `menu`, `services`, `tutors`): Define root items (`Name` + `Price/Rate` + `Description`).
  - **Selection/Basket Components** (`cart`, `basket`): Do NOT use arbitrary freeform string inputs. Instead, they provide a **Dropdown Selector of Master Catalog Entities** + Quantity input (`[ Dropdown: Select Catalog Item ▼ ] [ Qty: 1 ] [ ➕ Add to Cart ]`).
  - **Transaction/Tracking Components** (`tracking`, `orders`, `bookings`): Provide a **Dropdown Selector of Master Catalog Entities** + Status enum (`[ Dropdown: Select Item ▼ ] [ Status: Received ▼ ] [ ➕ Create Test Order ]`).
- **Full Inline CRUD**:
  - **Create**: Add new entity items via role-aware forms (text fields for catalog roots, dropdown selectors for dependent carts/orders).
  - **Read**: Display seed items bound to the component with price/status formatting.
  - **Update**: Click `✏️ Edit` to modify entity name/price/status inline.
  - **Delete**: Click `🗑️` to remove entity items from the active dataset.


---

## 📱 2. Mobile-First Responsive Design Invariants

All PM Studio features and backend UI generators MUST adhere to the following mobile-first layout invariants:

1. **Mobile Default Preview**:
   - `AppPreview.tsx` defaults `deviceMode` to `'mobile'` (`375px`).
   - Keeps preview focused on touch/mobile layout and maximizes horizontal space for the component inspector.

2. **Tight Frame Container Flex**:
   - In mobile mode, the preview frame flex wrapper collapses to `0 0 375px` (`width: 375px`).
   - **Zero Black Side Bars**: Eliminates dark empty padding around the mobile canvas.

3. **Responsive Vertical Stacking (`@media (max-width: 960px)`)**:
   - On screens `< 960px` (or mobile viewports), `.app-preview-split` stacks vertically (`flex-direction: column`):
     - Mobile preview frame on top (`height: 500px`).
     - Component Inspector below (`width: 100%`, `flex: 1`).
   - On desktop screens (`>= 961px`), side-by-side split row layout is rendered.

4. **Zero Horizontal Scrollbar Invariant**:
   - `RequirementControlPanel` and cards MUST use `flex: 1`, `minWidth: 0`, and `overflowX: 'hidden'`.
   - Text, badges, and input forms wrap fluidly (`wordBreak: 'break-word'`, `flexWrap: 'wrap'`) so the component inspector NEVER requires a horizontal scrollbar.

---

## 🧪 3. Test Pyramid Invariant & The Gibberish Strategy

- **Industrial WMS Domain Benchmark**: The official QA benchmark is an industrial domain context (e.g. Warehouse Management System tracking `Pallet`, `Zone`, and `Operator`).
- **The Gibberish Strategy (`backend/tests/e2e/test_ui_dynamic_projection.py`)**: UI dynamic purity is mathematically verified by feeding synthetic nonsense schemas (`TestFlorg` / `Zorp`) and asserting that the presentation layer projects them dynamically without fallback to hardcoded words.
- **Fast Unit Tests**: All skeleton generation, router derivation, and LibCST splicing tests reside in `backend/tests/unit/`, running in `< 1.0s`.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original document outlined a 3-pillar UX connecting domain entities through universal entity graphs (Master -> Selection -> Tracking). While the frontend has been updated to render domain aggregate trees, full dynamic form auto-generation from OpenAPI schema definitions directly in PM Studio remains a key roadmap item.]

---

## 💾 4. Persistence & Memory Channels

To ensure these decisions persist across future agent chat sessions:
1. **`vault/HANDOVER.md`**: Updated at the end of every turn to pass live architectural state to the next session.
2. **`.agents/AGENTS.md`**: Codifies mandatory rules and layout invariants into the agent's system prompt.

<!-- END_FILE: vault/01-Architecture/PM-Studio-UX-Architecture-And-Direction.md -->

---

## File 16: `vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md`

<!-- START_FILE: vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md -->

# Full-LLM Free-Form Software Synthesis & Orchestration Graph

## 1. Overview & Architectural Shift

Provable operates as a **Pure Full-LLM Free-Form Software Synthesizer**. Unlike traditional low-code generators that force business concepts into pre-baked "lego-block" components (such as rigid catalogs, shopping carts, or generic data tables), Provable synthesizes 100% bespoke, domain-native React 18 frontend interfaces and DDD backend stacks directly from domain mechanics and ubiquitous language.

---

## 2. The Multi-Loop Orchestration Graph

The software generation pipeline is structured as a **4-Loop Connected Graph**:

```mermaid
flowchart TD
    Pitch["User Business Pitch (Arbitrary Natural Language)"] --> Loop1["Loop 1: Domain Discovery & Ontology Storming"]

    subgraph Loop1Graph["Loop 1: Domain Storming (domain_ontology.py)"]
        Loop1 --> OntSpec["DomainOntologySpec<br/>• Ubiquitous Language<br/>• Master & Secondary Entities<br/>• Domain Commands & Events<br/>• Business Invariants"]
    end

    OntSpec --> Loop2["Loop 2: Backend DDD & TDD Engine (run_domain_loop)"]
    
    subgraph Loop2Graph["Loop 2: Backend DDD & TDD Engine"]
        Loop2 --> PureDomain["Pure Domain Model (0 DB dependencies)"]
        PureDomain --> CQRS["Commands & Events (PlaceOrder, OrderPlaced)"]
        CQRS --> Repos["Repositories & Unit of Work (SqliteUnitOfWork)"]
        Repos --> FastAPIRouters["FastAPI Presentation Routers"]
        FastAPIRouters --> StrictDocReqs["ISO 29148 Requirements & BDD Tests"]
    end

    OntSpec --> Loop3["Loop 3: Full-LLM Free-Form UI Synthesizer (run_ui_loop)"]

    subgraph Loop3Graph["Loop 3: Full-LLM Free-Form UI Synthesizer"]
        Loop3 --> BespokeDecomp["Bespoke Component Deconstruction (No Lego Bricks)"]
        BespokeDecomp --> FreeFormJSX["100% Bespoke React 18 TSX<br/>• Domain-Native Spatial Controls (Spectrogram, Radar, Matrix)<br/>• CSS Variable Theming (:root resets)<br/>• Optimistic State Management"]
    end

    Loop2Graph --> Loop4["Loop 4: Review, Self-Healing & Verification Gates"]
    Loop3Graph --> Loop4

    subgraph Loop4Graph["Loop 4: Verification Gates (verification.py)"]
        Loop4 --> ASTGate["AST Syntax & Babel Verification (verify_tsx_syntax)"]
        ASTGate --> VocabGate["Vocabulary Isolation Audit (audit_domain_vocabulary)"]
        VocabGate --> FixtureSync["Bidirectional Fixture Sync Injection (inject_data_fixtures_sync_to_tsx)"]
        FixtureSync --> ViteCheck["Vite Bundle & TypeScript Compilation Gate"]
    end

    Loop4 --> DeployedStack["Live Synthesized Application Stack (workspace/)"]
```

---

## 3. The 4 Loops in Detail

### Loop 1: Domain Discovery & Ontology Storming (`storm_domain_ontology`)
- Ingests the user's natural language pitch.
- Extracts the ubiquitous language noun, domain category (`catalog_cart`, `calendar_service`, `pipeline_tracker`, `dashboard_metrics`, `interactive_tool`), visual theme archetype, master entity attributes, and business invariants.
- Emits a structured `DomainOntologySpec` with zero hardcoded domain keywords.

### Loop 2: Backend Domain & TDD Engine (`run_domain_loop`)
- **01 Research**: Ingests the domain ontology schema and master entity attributes.
- **02 Red**: Generates dynamic ISO 29148 requirements and failing test case specifications with BDD `Given / When / Then` docstrings.
- **03 Build**: Synthesizes pure Python DDD models, domain commands, events, repositories, Unit of Work, and FastAPI routers.
- **04 Review**: Verifies layer boundaries (zero DB imports in pure domain, zero `db.store` in routers).
- **05 Verify**: Persists verified requirements to SQLite `provable.db` and exports StrictDoc `.sdoc`.

### Loop 3: Full-LLM Free-Form UI Synthesizer (`run_ui_loop`)
- **01 Deconstruct**: Decomposes the pitch into bespoke domain-native React components.
- **02 Synthesize**: Prompts the LLM with the full domain ontology to generate complete `App.tsx` code from first principles.
- **03 Avoid the Square-Hole Trap**: Gives the LLM full freedom to invent domain-tailored interactive tools (quantum circuit wire diagrams, acoustic frequency waterfalls, drone radar HUDs, custom crust builders) rather than forcing everything into generic spreadsheets.
- **04 Enforce Mobile-First Invariant**: Enforces fluid CSS resets (`* { box-sizing: border-box; } body { margin: 0; overflow-x: hidden; }`), `flex-wrap: wrap` header navigation, and fluid `maxWidth: '380px'` drawers.

### Loop 4: Review, Self-Healing & Verification Gates (`verification.py`)
- **AST Syntax Gate**: Validates TypeScript/JSX syntax using `verify_tsx_syntax` and executes AST self-healing if parse errors occur.
- **Vocabulary Isolation Gate**: Audits generated code to ensure zero leftover retail/batch terms pollute custom domain applications.
- **Fixture Synchronization Gate**: Injects bidirectional postMessage listener and state setter (`inject_data_fixtures_sync_to_tsx`) so PM Studio data fixtures synchronize in real time.
- **Vite Health Gate**: Verifies `npx vite build` and HTTP 200 OK.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The vision of pure full-stack schema projection replaces Loop 3 (Free-Form React code generation) with 100% dynamic schema rendering directly from OpenAPI contracts. This completely eliminates frontend LLM hallucinations and brittle TypeScript compilation errors.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[System Architecture]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]

<!-- END_FILE: vault/01-Architecture/Full-LLM-Free-Form-Orchestration-Graph.md -->

---

## File 17: `vault/01-Architecture/05-DDD-TDD-Architecture-Guidelines.md`

<!-- START_FILE: vault/01-Architecture/05-DDD-TDD-Architecture-Guidelines.md -->

# DDD & TDD Architecture Guidelines

This document defines the standardized Domain-Driven Design (DDD) and Test-Driven Development (TDD) architectural guidelines for applications built and maintained within Provable, based on patterns from *Architecture Patterns with Python* (Cosmic Python).

```mermaid
graph TD
    subgraph Entrypoints [Layer 4: Presentation & Entrypoints]
        API[FastAPI / Web Routes] --> ServiceLayer
        CLI[CLI Commands / Events] --> ServiceLayer
    end

    subgraph ServiceLayer [Layer 3: Application Service Layer & Unit of Work]
        UoW[Unit of Work (UoW)] --> Repo[Repository Protocol]
        UoW --> DomainModel[Domain Model]
        Handlers[Service Functions / Command Handlers] --> UoW
    end

    subgraph Adapters [Layer 2: Infrastructure & Adapters]
        Repo --> SQLAlchemy[ORM / SQLite Datastore]
        Repo --> ExternalAPIs[External API Clients]
    end

    subgraph Domain [Layer 1: Core Domain Model]
        DomainModel --> Entities[Entities & Value Objects]
        DomainModel --> DomainEvents[Domain Events]
    end
```

---

## 🏛️ Architectural Principles

Applications created or modified by Provable autonomous developer agents must adhere to the 4 concentric architectural layers:

### 1. Pure Domain Model (`domain/`)
- **Isolation**: Must not import ORMs, database frameworks (SQLAlchemy, Django), HTTP clients, or IO libraries.
- **Components**:
  - **Entities**: Objects with persistent identity (e.g. `Order`, `Batch`).
  - **Value Objects**: Immutable data structures defined purely by attributes (e.g. `Money`, `Sku`, `Quantity`).
  - **Domain Services**: Pure business logic operations involving multiple domain entities.
- **Testing**: Tested exclusively via **Low Gear TDD** (fast, pure-Python unit tests with zero IO).

### 2. Repository Abstraction (`adapters/`)
- **Purpose**: Decouple domain models from persistence mechanisms.
- **Protocol**: Expose explicit abstract base classes or protocols (`AbstractRepository`) with standard methods like `.add(entity)` and `.get(id)`.
- **Implementations**:
  - `SqlAlchemyRepository` for production SQL storage.
  - `FakeRepository` in-memory implementation for high-gear testing without database dependencies.

### 3. Application Service Layer & Unit of Work (`service_layer/`)
- **Use Case Orchestration**: Accepts primitive types (strings, ints, dicts), fetches entities via Repository, invokes domain methods, and commits changes.
- **Unit of Work (UoW)**:
  - Manages atomic transactions and context boundaries (`with uow:`).
  - Owns instances of repositories for the duration of a transaction.
- **Testing**: Tested via **High Gear TDD** (end-to-end use case tests using `FakeUnitOfWork`).

### 4. Entrypoints & Presentation (`entrypoints/`)
- **Role**: Thin wrappers mapping HTTP requests, CLI commands, or message events into call signatures for the Service Layer.
- **Strict Boundary**: API route handlers must **NEVER** contain SQL queries, ORM session manipulation, or direct business rules.

---

## 🧪 Shift-Left TDD Execution Pipeline

Provable enforces a requirement-driven TDD pipeline across all feature branches:

1. **Requirement Mapping**: Every StrictDoc requirement (`workspace/requirements/requirements.sdoc`) maps directly to a BDD Pytest scenario in `workspace/tests/`.
2. **Low Gear vs High Gear Strategy**:
   - **Low Gear**: Pure unit tests verifying business invariants on `domain/` objects.
   - **High Gear**: Integration tests verifying use case workflows in `service_layer/` with `FakeUnitOfWork`.
   - **End-to-End**: API contract tests verifying `entrypoints/` using Pytest WebTest / TestClient.
3. **Allure Matrix Mapping**: All tests must include `@allure.epic`, `@allure.feature`, and `@allure.story` annotations matching requirement IDs.

---

## 📚 Chapter Pattern Reference (Cosmic Python)

| Chapter / Pattern | Architectural Responsibility | Provable Implementation Guidance |
| :--- | :--- | :--- |
| **Ch 1: Domain Model** | Enforce business rules in pure Python objects | Store in `workspace/src/domain/` without ORM annotations |
| **Ch 2: Repository Pattern** | Abstract storage behind clean interface | Define `AbstractRepository` in `workspace/src/adapters/repository.py` |
| **Ch 3 & 5: High vs Low Gear TDD** | Balance test speed with coverage | Write domain unit tests first (Low Gear), service tests second (High Gear) |
| **Ch 4: Service Layer** | Orchestrate use cases & primitive parameters | Define use case functions in `workspace/src/service_layer/services.py` |
| **Ch 6: Unit of Work** | Provide atomic transaction boundaries | Implement `AbstractUnitOfWork` in `workspace/src/service_layer/unit_of_work.py` |
| **Ch 7: Aggregates** | Define consistency boundaries for data mutations | Wrap related domain entities under a single Aggregate root |
| **Ch 8-11: Events & Message Bus** | Decouple side-effects and microservice integrations | Use in-memory `MessageBus` for domain events and command handlers |
| **Ch 12: CQRS** | Separate read queries from write commands | Provide dedicated optimized read queries bypassing full domain models |

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Shift-Left TDD Workflow]]
- [[Testing Strategy]]
- [[Agent Execution Loop]]

<!-- END_FILE: vault/01-Architecture/05-DDD-TDD-Architecture-Guidelines.md -->

---

## File 18: `vault/02-Workflows/Onboarding and Discovery Workflow.md`

<!-- START_FILE: vault/02-Workflows/Onboarding and Discovery Workflow.md -->

# Onboarding & Workspace Discovery Workflow

When Provable is initialized against a new target repository (or when the active workspace is changed), the discovery subsystem inspects project structure, configuration files, and build manifests to auto-configure agent execution parameters.

```mermaid
flowchart TD
    Select[User selects target repository workspace] --> Scan[Discovery Agent scans workspace files]
    Scan --> DetectFramework{Detect App Framework}
    DetectFramework -->|package.json / vite| Vite[Configure Vite preview dev server port :5174]
    DetectFramework -->|pyproject.toml / pytest| Pytest[Configure Pytest runner & allure-results]
    Scan --> SyncSpecs[Scan workspace for existing requirements / sdoc specs]
    Vite --> Config[Synthesize project configuration]
    Pytest --> Config
    SyncSpecs --> Config
    Config --> Store[Save project settings to SQLite DataStore]
```

## Discovery Steps

### 1. Framework & Dev Server Auto-Detection
- Scans `package.json` for frontend framework markers (Vite, Next.js, React).
- Auto-configures preview server launch commands (e.g. `npm run dev -- --port 5174`).

### 2. Test Runner Discovery
- Checks for `pytest.ini`, `conftest.py`, or `pyproject.toml`.
- Configures default test command: `pytest -v --alluredir=allure-results`.

### 3. Specification Discovery
- Checks for `.sdoc` specification files or `requirements.json`.
- Automatically executes `sync_sdoc_to_db()` to import requirement hierarchies into SQLite.

<!-- END_FILE: vault/02-Workflows/Onboarding and Discovery Workflow.md -->

---

## File 19: `vault/02-Workflows/Shift-Left TDD Workflow.md`

<!-- START_FILE: vault/02-Workflows/Shift-Left TDD Workflow.md -->

# Shift-Left TDD Workflow

Provable enforces a strict Shift-Left Test-Driven Development (TDD) lifecycle. Instead of writing verification tests after feature implementation, failing pytest test specs are auto-generated before any source code is modified.

```mermaid
sequenceDiagram
    participant PM as PM Studio (UI)
    participant ReqList as Requirements Explorer
    participant AllureHub as Coverage Hub (Allure)
    participant Agent as LangGraph Agent Loop
    participant Workspace as Git Sandbox / Tests

    PM->>ReqList: 1. Create New Requirement (REQ-XXX)
    PM->>ReqList: 2. Click "Create Test Case"
    ReqList->>Workspace: Write failing test_REQ_XXX.py (TDD Red)
    Workspace-->>AllureHub: Publish failing result to Allure container (:5050)
    AllureHub-->>PM: Display ✗ failing test in Coverage Table
    PM->>AllureHub: 3. Click "Fix Failing Test"
    AllureHub->>Agent: Dispatch autonomous coding agent
    activate Agent
    Agent->>Workspace: Write source edits to satisfy test_REQ_XXX.py
    Agent->>Workspace: Run tests (Verify target test passes)
    Workspace-->>AllureHub: Publish passing result to Allure
    Agent-->>PM: Transition ticket to "Review" status (Code Review)
    deactivate Agent
    PM->>PM: 4. Approve & Merge code changes to main
```

## Detailed TDD Lifecycle Steps

### 1. Specification Creation
- A Project Manager creates a requirement, task, or bug in the **Requirements Explorer**.
- The item is created in `Backlog` status with **no linked test cases** (indicated by a white circle icon `○`).

### 2. Failing Test Case Generation (TDD Red)
- The PM clicks **"Create Test Case"** on the requirement detail panel.
- The backend loads `prompts/test_case_generation.md` and calls the LLM to write a BDD-structured pytest file (`workspace/tests/test_<REQ_ID>.py`).
- The backend immediately executes the new test file to verify that it **fails**. This establishes the verified **TDD Red** baseline (represented by a red cross icon `✗`).

### 3. Coverage Matrix & Allure Sync
- The **Coverage Hub** aggregates all requirements and their linked test status.
- Test execution results are uploaded to the containerized Allure Docker Service (`:5050`) and displayed in the embedded iframe.

### 4. Developer Agent Execution (TDD Green)
- The PM clicks **"Fix Failing Test"** next to the failing item in the Coverage Hub or Requirements Explorer.
- The backend dispatches the LangGraph developer agent loop.
- The agent modifies source code files inside `workspace/` until the target pytest spec passes without breaking existing tests.

### 5. Review & Merge Approval
- Upon test pass (TDD Green), the agent submits the branch to the **Code Review Queue**.
- The PM inspects the git diff in **Code Review** and clicks **Approve**.
- The backend merges `ticket/<TICKET_ID>` into `main` and updates requirement status to `Done`.

<!-- END_FILE: vault/02-Workflows/Shift-Left TDD Workflow.md -->

---

## File 20: `vault/02-Workflows/Agent Execution Loop.md`

<!-- START_FILE: vault/02-Workflows/Agent Execution Loop.md -->

# Deterministic TDD Agent Execution Pipeline

Provable utilizes a **Deterministic TDD State Machine** ([`backend/service_layer/tdd_machine.py`](backend/service_layer/tdd_machine.py)) enforcing programmatic Red-Gate evaluation, Meta LibCST code isolation, and SHA-256 test integrity hash locking.

```mermaid
sequenceDiagram
    participant Inbox as Behavior Inbox (Specs)
    participant TDD as TDD State Machine (tdd_machine.py)
    participant LibCST as LibCST Isolator (cst_isolator.py)
    participant Pytest as Pytest Runner (5s Timeout)
    participant Git as Git Version Control

    Inbox->>TDD: 1. Pop Next Business Spec (SPEC-XXX)
    activate TDD
    TDD->>TDD: 2. RED_GEN: Generate BDD unit test (test_spec.py)
    TDD->>Pytest: 3. Execute Pytest on test_spec.py
    Pytest-->>TDD: Evaluate Exit Code 1 & AssertionError (Approved RED)
    
    TDD->>TDD: 4. 5-Line Hash Lock: Compute SHA-256 hash of test_spec.py
    TDD->>LibCST: 5. Extract Aggregate Root CST from domain model
    LibCST-->>TDD: Target Class Definition CST
    TDD->>LibCST: 6. Splice implemented class back into module
    
    TDD->>TDD: 7. Re-verify test_spec.py SHA-256 hash (Anti-Cheat)
    TDD->>Pytest: 8. Execute Pytest on test_spec.py (5s Timeout)
    
    alt Green Phase Passed (Exit Code 0)
        Pytest-->>TDD: 0 Errors / All Assertions Pass
        TDD->>Git: Auto-commit spec feature branch / main
        TDD->>Inbox: Update Spec Status to "FULFILLED" 🟢
    else Green Phase Failed (Attempts < 3)
        Pytest-->>TDD: AssertionError in Green
        TDD->>TDD: Retry LibCST repair loop
    else Green Phase Dead-End (Attempts == 3)
        TDD->>Git: git reset --hard to pre-RED state
        TDD->>Inbox: Update Spec Status to "REQUIRES_HUMAN_INTERVENTION" 🔴
    end
    deactivate TDD
```

---

## Detailed Execution Steps

### 1. Spec Intake & RED Gate
- Ingests atomic `BusinessSpec` from Behavior Inbox.
- Generates BDD pytest test file (`workspace/tests/unit/test_<spec_id>.py`).
- Executes Pytest with `--timeout=5` and `--json-report`.
- **Programmatic Red-Gate Evaluation (`evaluate_red_gate_result`)**:
  - Exit Code 0 (Pass without code) $\rightarrow$ **REJECTED_TAUTOLOGY**.
  - Exit Code 2 / SyntaxError / Timeout $\rightarrow$ **REJECTED_SYNTAX_OR_EXEC**.
  - Exit Code 1 with `AssertionError` $\rightarrow$ **APPROVED_RED**.

### 2. 5-Line SHA-256 Hash Lock Anti-Cheat
- Computes SHA-256 hash snapshot of `test_<spec_id>.py`.
- Enforces that no test assertion or file content is tampered with during code generation.

### 3. LibCST Surgical Class Splicing (`cst_isolator.py`)
- Extracts the exact class CST node from the domain module.
- Generates or updates domain methods and invariants.
- Splices updated class back into the module preserving 100% of formatting, comments, and docstrings.

### 4. GREEN Gate & Commit / Rollback
- Re-verifies test file SHA-256 hash (`verify_test_file_integrity`).
- Executes Pytest. If Exit Code 0: marks spec `FULFILLED` and commits.
- If failed after 3 attempts: executes `git reset --hard` to pre-RED state and flags `REQUIRES_HUMAN_INTERVENTION`.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original execution loop specification was designed for autonomous LLM code generation iterating over full repo branches. While tdd_machine.py successfully isolates the RED-GREEN-COMMIT loop, the GREEN implementation currently relies on stub mutations rather than live LLM-driven LibCST prompts. Connecting the LLM to the LibCST micro-context is architecturally superior.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[System Architecture]]
- [[DDD_TDD_Developer_Workflow]]

<!-- END_FILE: vault/02-Workflows/Agent Execution Loop.md -->

---

## File 21: `vault/02-Workflows/DDD_TDD_Developer_Workflow.md`

<!-- START_FILE: vault/02-Workflows/DDD_TDD_Developer_Workflow.md -->

# DDD/TDD Developer Subagent Workflow & Layer Rules

This document outlines the strict execution protocol for the `ddd_tdd_developer` subagent and human developers refactoring or adding backend features in Provable.

---

## 🏛️ Architectural Layer Boundaries

1. **Domain Model Layer** ([`backend/domain/`](backend/domain)):
   - Contains pure Python dataclasses (`Requirement`, `Component`, `Project`, `AgentRun`) and custom business domain exceptions (`InvalidStatusTransition`).
   - **Rule**: ZERO imports from FastAPI, Pydantic, SQLAlchemy, or SQLite.
2. **Adapter Layer** ([`backend/adapters/`](backend/adapters)):
   - Defines `AbstractRepository` interfaces with concrete implementations (`SqliteRepository`) and fast in-memory fakes (`FakeRepository`).
3. **Service Layer & Unit of Work** ([`backend/service_layer/`](backend/service_layer)):
   - Defines `AbstractUnitOfWork`, `SqliteUnitOfWork`, and `FakeUnitOfWork` context managers managing transaction atomicity (`commit()`, `rollback()`).
   - Houses stateless use-case workflows (`create_requirement`, `list_requirements`, `get_requirement`).
4. **Presentation Entrypoints** ([`backend/entrypoints/routers/`](backend/entrypoints/routers)):
   - Modular FastAPI routers.
   - **Rule**: MUST NEVER import `db.store` directly. Every POST/GET handler delegates to `services.<use_case>(uow=SqliteUnitOfWork())`.

---

## 🔄 Mandatory 4-Step TDD Execution Loop

```mermaid
sequenceDiagram
    participant Agent as Developer Subagent
    participant Test as Unit Test Suite
    participant Domain as Domain & Service Layer
    participant Router as Entrypoint Router
    
    Agent->>Test: 1. Write Red Unit Test (FakeUnitOfWork)
    Test-->>Agent: Fail (Red Phase)
    Agent->>Domain: 2. Implement Pure Model & Service Handler
    Agent->>Test: Run Unit Pytest (<0.5s)
    Test-->>Agent: Pass (Green Phase)
    Agent->>Router: 3. Wire SqliteUnitOfWork in Router
    Agent->>Test: 4. Run Full Pytest & Anti-Leakage Gate (grep)
    Test-->>Agent: 100% Pass & Zero db.store Leakage
```

---

## 🛡️ Anti-Leakage Verification Gate

At the conclusion of any router or service layer refactoring task, run:
```powershell
grep -rn "import db.store" backend/entrypoints/routers/ backend/service_layer/services.py
```
**Required Result**: `0 matches`.

<!-- END_FILE: vault/02-Workflows/DDD_TDD_Developer_Workflow.md -->

---

## File 22: `vault/02-Workflows/Future Enhancements Roadmap.md`

<!-- START_FILE: vault/02-Workflows/Future Enhancements Roadmap.md -->

# Future Enhancements & Prototype Roadmap

This document captures all planned, scoped, but unexecuted architectural enhancements to advance Provable towards a production-grade enterprise platform.

---

## 1. ⚡ Live Agent Execution Graph Visualizer

### Overview
Enhance the bottom collapsible `AgentTray.tsx` component with an interactive, animated step graph representing the 5 LangGraph orchestrator nodes:
```
[ prepare_branch ] ➔ [ code_generation ] ➔ [ test_runner ] ➔ [ visual_qa ] ➔ [ finalize ]
```

### Technical Blueprint
- **Data Source**: Poll `/api/agent-status` or connect via Server-Sent Events (SSE).
- **UI Component**: React Flow or custom SVG node graph in [`src/components/AgentTray.tsx`](src/components/AgentTray.tsx).
- **Node Log Filtering**: Clicking a node filters the log viewer specifically to that node's execution phase.

---

## 2. 🔄 Self-Healing TDD Feedback Loop

### Overview
When a Project Manager rejects an agent submission in `CodeReview.tsx` with feedback (e.g., *"The export button must be disabled when no rows are selected"*), the system automatically updates the underlying BDD test specification before re-dispatching the developer agent.

```mermaid
sequenceDiagram
    participant PM as PM Studio (UI)
    participant Backend as FastAPI Backend
    participant LLM as OpenAI SDK
    participant TestSpec as workspace/tests/test_REQ.py
    participant Agent as LangGraph Agent Loop

    PM->>Backend: 1. Reject Submission with Feedback Text
    Backend->>LLM: 2. Load prompts/test_spec_update.md + inject feedback
    LLM-->>Backend: 3. Return updated BDD test_REQ.py assertions
    Backend->>TestSpec: 4. Write updated test spec to workspace/
    Backend->>TestSpec: 5. Execute pytest (Verify test spec now FAILS - Red)
    Backend->>Agent: 6. Dispatch LangGraph agent with failing traceback
    Agent->>Agent: 7. Modify source code to make test PASS (Green)
    Agent-->>PM: 8. Re-submit updated branch to Code Review Queue
```

---

## 3. 🧪 Multi-Domain Synthesis Benchmark Suite & Stress Tester

### Overview
An automated testing framework (`backend/tests/benchmark_domain_stormer.py`) that runs stress tests across 10 diverse business domain pitches to ensure 100% domain vocabulary isolation and zero Vite build errors.

### Target Domains for Benchmark Suite:
1. **Medical Clinic**: `Appointment`, `Doctor`, `Patient`, `TimeSlot`
2. **Laundromat Service**: `WasherMachine`, `LaundryOrder`, `Cycle`, `Detergent`
3. **Barber Shop**: `Barber`, `HaircutBooking`, `ServiceMenu`
4. **Car Rental Fleet**: `RentalVehicle`, `CustomerBooking`, `ReturnInspection`
5. **SaaS Billing**: `SubscriptionPlan`, `CustomerAccount`, `Invoice`
6. **Construction Logistics**: `HeavyEquipment`, `SiteDispatch`, `Maintenance`
7. **Hotel Reservation**: `GuestRoom`, `Reservation`, `CheckIn`
8. **Gym Membership**: `MemberCard`, `AccessGate`, `ClassBooking`
9. **Restaurant Kitchen**: `KitchenOrder`, `ChefStation`, `TableReservation`
10. **E-Commerce Fulfillment**: `FulfillmentOrder`, `PackingStation`, `Courier`

### Automated Checks Performed by Benchmark Suite:
- **Vocabulary Isolation Audit**: Verifies 0 occurrences of `sku`, `batch`, `_purchased_quantity`, or `OrderLine` in non-retail code output.
- **Syntactic AST Correctness**: Executes `python -m py_compile` on all generated `.py` files.
- **Frontend Build Gate**: Executes `npx vite build` to guarantee zero JSX/TypeScript errors.

---

## 4. 🎨 Interactive Bounded Context & Subdomain Canvas

### Overview
Extend [`src/components/DomainModeling.tsx`](src/components/DomainModeling.tsx) with a visual Bounded Context Map visualizer.

### Key Features
- **Bounded Context Boundaries**: Visualizes strategic DDD context boundaries (e.g. `Ordering Context` $\leftrightarrow$ `Kitchen Dispatch Context` $\leftrightarrow$ `Delivery Context`).
- **Context Maps**: Displays upstream/downstream relationship patterns (Customer/Supplier, Shared Kernel, Anti-Corruption Layer).
- **Subdomain Classification**: Categorizes domain components into Core Subdomains, Supporting Subdomains, and Generic Subdomains.

---

## 5. 📄 StrictDoc Bidirectional Webhook Synchronization

### Overview
Automate bidirectional synchronization between SQLite `provable.db` database records and Git version-controlled `.sdoc` specification files (`workspace/requirements/requirements.sdoc`).

### Key Features
- **Automatic Export Hook**: Any REST API call modifying requirements or test cases automatically triggers `strictdoc_client.export_sdoc()`.
- **File Watcher Import Hook**: Modifying `requirements.sdoc` directly in VS Code automatically triggers `strictdoc_client.import_sdoc()` to update SQLite DataStore tables.

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Universal-Dynamic-Domain-AST-Generator]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]

<!-- END_FILE: vault/02-Workflows/Future Enhancements Roadmap.md -->

---

## File 23: `vault/02-Workflows/Bug-Reproduction-and-Testing-Policy.md`

<!-- START_FILE: vault/02-Workflows/Bug-Reproduction-and-Testing-Policy.md -->

﻿# Bug Reproduction & Live Stack Testing Policy

## Översikt & Syfte
För att säkerställa hög tillförlitlighet, förhindra regressionsfel och eliminera runtime-överraskningar (såsom utebliven serveranslutning på `localhost:5174` eller brutna build-scripts), gäller en strikt policy för alla AI-agenter och utvecklare: **Varje fel som identifieras ska omedelbart förses med ett automatiserat regressionstest som reproducerar och verifierar lösningen.**

---

## De 3 Gyllene Reglerna för Felhantering

### 1. Reproduktion via Automatiserat Integrationstest
När en bugg upptäcks (t.ex. en felande endpoint, saknad CLI-beroende, trasig TypeScript-typning eller timeout vid dev-serverstart):
1. Skriv **alltid** ett automatiserat test först i `backend/tests/integration/` eller `backend/tests/unit/`.
2. Kör testet och bekräfta att det fångar problemet.
3. Genomför fixen i backend-källkoden / generatorerna (aldrig direkt i `workspace/`).
4. Verifiera att testet blir 100% grönt (`PASS`).

### 2. Tri-Service Live Stack Invariant
AppGen-plattformen består av tre sammankopplade tjänster som alltid ska vara verifierade:
- **Port 8000 (FastAPI Backend Engine)**: REST-endpoints, DDD-servicelager och OpenAPI-schema (`/openapi.json`).
- **Port 5173 (PM Studio Frontend)**: React 18 / TypeScript / Vite-användargränssnittet (`frontend/`).
- **Port 5174 (Workspace Live Preview)**: Sandlådemiljön som kör den genererade koden (`workspace/`).

### 3. Noll "Phantom Node Modules" & Fullständig Scaffolding
- `workspace/` måste alltid innehålla giltig `package.json`, `tsconfig.json` och `vite.config.ts`.
- `run.py` och testsviter verifierar att både `frontend/node_modules/vite` och `workspace/node_modules/vite` är installerade och redo.
- Start-processen väntar in och bekräftar att alla tre portar (`8000`, `5173`, `5174`) lyssnar innan sessionen lämnas över till användaren.

---

## Relevanta Testfiler
- `backend/tests/integration/test_app_startup_and_preview_connectivity.py`: Verifierar komplett scaffolding, TypeScript-konfiguration och felfri Vite-kompilering för både PM Studio och Workspace Preview.
- `backend/tests/integration/test_jsx_compilation_integrity.py`: Verifierar AST- och JSX-kompileringsintegritet för genererade React-komponenter.

<!-- END_FILE: vault/02-Workflows/Bug-Reproduction-and-Testing-Policy.md -->

---

## File 24: `vault/02-Workflows/Helper Scripts.md`

<!-- START_FILE: vault/02-Workflows/Helper Scripts.md -->

# Helper & Utility Scripts

This document details the single cross-platform application launcher and developer inspection scripts.

---

## 🚀 Single Application Launcher (`run.py`)

`run.py` located at the project root is the master launcher for the entire Provable application stack:

### Execution Flow
1. **OS & Environment Detection**: Detects whether running on Windows host, WSL (Windows Subsystem for Linux), or native Linux.
2. **Dependency Resolution**: Checks Python virtualenv packages (`requirements.txt`) and Node modules (`package.json`), auto-installing missing packages.
3. **Containerized Allure Service**: Verifies Docker Desktop status and launches the Allure container (`docker-compose.allure.yaml` on port `5050`).
4. **FastAPI Backend Server**: Spawns the FastAPI application (`backend/app.py`) on `http://localhost:8000`.
5. **Vite PM Studio Frontend**: Spawns the Vite dev server on `http://localhost:5173`.

### Wrappers
- **`run.ps1`**: PowerShell wrapper for Windows host execution of `python run.py`.
- **`run.sh`**: Bash wrapper for Linux / WSL execution of `python3 run.py`.

---

## 🛠️ Developer Diagnostic Scripts (`backend/scripts/`)

### 1. `backend/scripts/deep_heuristic_scan.py`
- **Purpose**: Scans python codebase for lingering hardcoded domain keywords and heuristic switchboards.
- **Usage**: `python backend/scripts/deep_heuristic_scan.py`

### 2. `backend/scripts/inspect_ast_pipeline.py`
- **Purpose**: Inspects AST compilation stages and LibCST code splicing transformations.
- **Usage**: `python backend/scripts/inspect_ast_pipeline.py`

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original helper scripts included live log tailing utilities (tail_logs.sh). While streaming logs are available via backend stdout and pytest JSON reports, a dedicated CLI log tailing script for TDD execution state is helpful for developer ergonomics.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Bug-Reproduction-and-Testing-Policy]]

<!-- END_FILE: vault/02-Workflows/Helper Scripts.md -->

---

## File 25: `vault/03-Testing/Testing Strategy.md`

<!-- START_FILE: vault/03-Testing/Testing Strategy.md -->

# Testing Strategy & Quality Assurance Architecture

Provable enforces a 3-tier Domain-Driven Design (DDD) test architecture combined with deterministic Test-Driven Development (TDD). Every business rule is backed by automated BDD test specs before implementation code is written.

---

## 3-Tier DDD Test Architecture (`backend/tests/`)

```
backend/tests/
├── unit/         # Fast (<0.5s) in-memory unit tests using FakeUnitOfWork and pure domain logic
├── integration/  # Multi-component integration tests (router engine, startup, purity)
└── e2e/          # Dynamic UI projection verification via The Gibberish Strategy
```

### Tier 1: Unit Tests (`backend/tests/unit/`)
- Fast in-memory unit tests exercising pure domain models (`domain/model.py`), Unit of Work (`FakeUnitOfWork`), service handlers, and LibCST class isolators.
- **Execution Speed**: 100+ tests execute in `< 1.5s`.

### Tier 2: Integration Tests (`backend/tests/integration/`)
- Verifies multi-stage domain synthesis pipelines (`test_dual_track_benchmarks.py`), tri-service startup connectivity, and strict frontend domain vocabulary purity (`test_frontend_domain_purity.py`).

### Tier 3: E2E Tests (`backend/tests/e2e/`)
- **The Gibberish Strategy (`test_ui_dynamic_projection.py`)**: Feeds synthetic nonsense schemas (`TestFlorg` / `Zorp`) to mathematically prove the UI is a 100% domain-agnostic projection with zero hardcoded legacy components.

---

## BDD Test Docstring & Allure Metadata Tagging

All generated pytest specs (`workspace/tests/unit/test_*.py`) must include BDD Given-When-Then docstrings:

```python
import pytest

def test_pallet_capacity_limit():
    """
    BDD Specification: Enforce Maximum Weight Limit
    Given a storage Zone with 1000kg maximum capacity
    When a Pallet weighing 1200kg is allocated to the Zone
    Then raise CapacityExceededError
    """
    ...
```

---

## 5-Line Hash Lock Anti-Cheat Verification

```python
initial_hash = compute_test_file_hash(test_file_path)
# Execute GREEN Phase Code Generation
verify_test_file_integrity(test_file_path, initial_hash)
```

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original testing strategy envisioned full browser-driven Selenium E2E tests validating visual renders on every ticket run. While browser automation is valuable, consolidating visual QA to lightweight API contracts and The Gibberish Strategy reduced test execution time from 80s+ to 2s.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]
- [[Bug-Reproduction-and-Testing-Policy]]

<!-- END_FILE: vault/03-Testing/Testing Strategy.md -->

---

## File 26: `vault/03-Testing/Automated-Verification-And-Self-Healing-Pipeline.md`

<!-- START_FILE: vault/03-Testing/Automated-Verification-And-Self-Healing-Pipeline.md -->

# Automated Verification & Self-Healing Pipeline

The **Automated Verification Pipeline** enforces strict domain purity, schema contract projection, and TDD invariants across Provable.

```mermaid
graph LR
    Synthesis["Code Generation / Skeleton Build"] --> Gate1["Gate 1: Frontend Domain Purity Gate"]
    Gate1 -- PASS --> Gate2["Gate 2: The Gibberish Strategy (E2E)"]
    Gate2 -- PASS --> Gate3["Gate 3: Pytest Red-Green Execution Gate"]
    Gate3 -- PASS --> Success["Verified DDD Stack & Active Projection"]

    Gate1 -- FAIL --> ReSynthesize["Reject & Alert"]
    Gate2 -- FAIL --> ReSynthesize
    Gate3 -- FAIL --> ReSynthesize
```

---

## 🛡️ Verification Gates Breakdown

### 1. Frontend Domain Purity Gate (`test_frontend_domain_purity.py`)
- **Objective**: Ensure the frontend remains 100% domain-agnostic and free of hardcoded domain words (`pizza`, `cart`, `checkout`, `pallet`, `zone`).
- **Mechanism**: Dynamically extracts active backend aggregate roots and attributes via static AST parsing and scans `frontend/src/` to guarantee zero domain term leakage.

### 2. The Gibberish Strategy E2E Gate (`test_ui_dynamic_projection.py`)
- **Objective**: Mathematically prove that the UI is a pure dumb projection of backend schemas.
- **Mechanism**: Feeds the presentation layer a synthetic nonsense schema (`TestFlorg` / `Zorp`) and asserts that the UI dynamically renders `TestFlorg` and `Zorp` without fallback to static mock components.

### 3. Pytest Execution Gate & 5-Line Hash Lock (`tdd_machine.py`)
- **Objective**: Programmatically enforce RED (Exit Code 1 + `AssertionError`), GREEN (Exit Code 0), and anti-tampering SHA-256 test file integrity.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original pipeline specified an automated self-healing re-synthesis loop triggered whenever verification gates fail. While tdd_machine.py provides 3-strike repair loops for backend domain classes, an automated end-to-end self-healing orchestrator for the entire stack remains a vital enterprise feature.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[Testing Strategy]]
- [[Bug-Reproduction-and-Testing-Policy]]

<!-- END_FILE: vault/03-Testing/Automated-Verification-And-Self-Healing-Pipeline.md -->

---

## File 27: `vault/04-Decisions/ADR-001 Host vs Containerized Execution.md`

<!-- START_FILE: vault/04-Decisions/ADR-001 Host vs Containerized Execution.md -->

# ADR-001: Host vs Containerized Execution

## Context
Provable needs to run Vite web development/preview servers and execute pytest test suites for the code generated inside the `workspace/` directory. We must decide whether to run these processes directly on the developer's host machine or isolate them inside Docker containers.

## Decision
For the initial prototype, we will run Vite servers and pytests **directly on the host machine**. We defer full containerization of the target workspace for a later production design iteration.

## Alternatives Considered

### Option A: Host Execution (Selected)
Execute `npm run dev` and `pytest` using the host's runtime environment and the Python virtual environment located at `backend/venv`.
- **Pros**:
  - Extremely fast start times (Vite dev server launches in milliseconds).
  - Simpler networking (localhost is shared, avoiding port mapping issues).
  - Lower prototype complexity (no need to manage Docker containers programmatically).
- **Cons**:
  - No security sandbox: the LLM-generated code runs with the developer's user permissions (risk of executing malicious shell scripts).
  - Host pollution: requires Node, Python, Chrome, and ChromeDriver to be installed on the host machine.

### Option B: Sandboxed Docker Containerization (Deferred)
Launch a Docker container for each ticket branch, mounting `workspace/` and executing tests inside the isolated container.
- **Pros**:
  - Secure sandboxing: agents cannot access host files or execute commands outside the container.
  - Consistent environments: dependencies are locked in the container image.
- **Cons**:
  - Virtualization startup overhead (seconds vs. milliseconds).
  - Complex network routing to bridge the PM Studio interface to nested containers.
  - File permission issues with bind mounts between the host filesystem and Docker.

## Status
**Accepted (Prototype)** - Deferred full containerization to production design stage.

<!-- END_FILE: vault/04-Decisions/ADR-001 Host vs Containerized Execution.md -->

---

## File 28: `vault/04-Decisions/ADR-002 SQLite and StrictDoc Bidirectional Sync.md`

<!-- START_FILE: vault/04-Decisions/ADR-002 SQLite and StrictDoc Bidirectional Sync.md -->

# ADR-002: SQLite and StrictDoc Bidirectional Sync

## Context
Provable requires a robust, structured way to model software requirements, parent-child relations, and test linking. We need to bridge the gap between human-readable requirements specification formats (like StrictDoc's `.sdoc` specifications) and the high-performance database queries needed by the React-based PM Studio frontend.

## Decision
We implement a hybrid, bidirectional synchronization system between an SQLite database (`backend/provable.db`) and StrictDoc text specification files (`workspace/requirements/requirements.sdoc`).

1. **SQLite DataStore**: Serves as the primary runtime storage for API endpoints. It stores requirements, test cases, and agent runs, allowing fast reads, parent-child tree queries, and transactional updates.
2. **StrictDoc `.sdoc` File**: Serves as the persistent local requirements file inside the codebase. It represents the "specs" in the "specs-to-code" loop.
3. **Synchronization Logic (`strictdoc_client.py`)**:
   - **Import (`sync_sdoc_to_db`)**: Parses the `.sdoc` spec file on backend startup and imports/syncs its sections and requirement UIDs into the SQLite database.
   - **Export (`export_sdoc`)**: Rewrites the `.sdoc` file dynamically whenever a requirement or task is modified, added, or deleted via the frontend PM Studio interface.

## Alternatives Considered
- **StrictDoc Only**: Direct parsing of `.sdoc` files for every API request. Dismissed due to file-IO performance bottleneck and complex relational queries.
- **SQLite Only**: Storing requirements only in database tables. Dismissed because it lacks a localized, text-based specification format that simulated developer agents can easily read and write inside the repository.

## Status
**Accepted**

<!-- END_FILE: vault/04-Decisions/ADR-002 SQLite and StrictDoc Bidirectional Sync.md -->

---

## File 29: `vault/04-Decisions/ADR-003 LLM Abstraction Layer and Prompt Externalization.md`

<!-- START_FILE: vault/04-Decisions/ADR-003 LLM Abstraction Layer and Prompt Externalization.md -->

# ADR-003: LLM Abstraction Layer and Prompt Externalization

## Context
In early Provable prototypes, LLM API calls were hardcoded to Gemini models, and system prompts were embedded directly in Python strings inside `backend/agent_orchestrator.py`. This made it difficult to swap LLM providers (e.g. to OpenAI, Anthropic, or local Ollama models) or modify developer agent prompts without modifying backend code.

## Decision
We abstract all LLM interactions and externalize prompt templates:

1. **LLM Abstraction Layer**: Built using the OpenAI Python SDK to allow a standardized, API-compatible interface. LLM routing is configured in `backend/config/models.yaml`, mapping custom identifiers (e.g., `gemini-2.5-flash`) to specific API models and parameters.
2. **Prompt Externalization**: Removed all system prompts and templates from Python files. They are stored as structured markdown files under `backend/prompts/` (e.g., `write_code.md`, `run_tests.md`) and loaded dynamically at runtime.
3. **Environment Setup**: The API key and LLM provider endpoint are configured via standard `.env` variables (`LLM_API_KEY`, etc.).

## Alternatives Considered
- **Direct Gemini SDK Integration**: Kept LLM calls restricted to Google Gemini. Dismissed because it limits the ability to test alternative models (e.g. GPT-4o, Claude) or local models (Ollama).
- **Embedded Python Prompt Strings**: Kept prompts inside code. Dismissed because prompt engineering is a primary workflow for refining agent developer behaviors, necessitating independent modification.

## Status
**Accepted**

<!-- END_FILE: vault/04-Decisions/ADR-003 LLM Abstraction Layer and Prompt Externalization.md -->

---

## File 30: `vault/04-Decisions/ADR-004 Allure Reporting Server Docker Integration.md`

<!-- START_FILE: vault/04-Decisions/ADR-004 Allure Reporting Server Docker Integration.md -->

# ADR-004: Allure Reporting Server Docker Integration

## Context
Provable requires a test reporting dashboard showing detailed metrics, history, and requirement coverage. Generating static HTML reports for every run is resource-intensive and does not support dynamic visual updates.

## Decision
We integrate the Allure Docker Service to host and serve visual test reports.

1. **Docker Container**: A containerized Allure service (`frankescobar/allure-docker-service`) is executed on port `5050` (mapped via `docker-compose.allure.yaml` or run command).
2. **Startup Initialization Hook**: On backend startup, the FastAPI app performs an HTTP POST request to register the project ID (`provable`):
   ```python
   requests.post("http://localhost:5050/projects", json={"id": "provable"})
   ```
   This ensures that the project is registered inside the Allure container memory, resolving any `project_id not found` issues when the Allure iframe is embedded in the frontend.
3. **Report Generation**: The pytest runner in the workspace outputs results to `workspace/allure-results/` using `--alluredir=allure-results`. The Allure service monitors this folder and auto-generates reports.

## Alternatives Considered
- **Static Allure HTML Generation**: Generating reports locally and rendering them. Dismissed because static HTML generation is slow, and linking coverage metrics back to requirement IDs is highly complex without a database dashboard.

## Status
**Accepted**

<!-- END_FILE: vault/04-Decisions/ADR-004 Allure Reporting Server Docker Integration.md -->

---

## File 31: `vault/05-Rules/Agent Customizations.md`

<!-- START_FILE: vault/05-Rules/Agent Customizations.md -->

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

<!-- END_FILE: vault/05-Rules/Agent Customizations.md -->

---

## File 32: `vault/06-Cosmic-Python-Journey/Chapter-01-Domain-Model.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/Chapter-01-Domain-Model.md -->

# Chapter 1: Domain Modeling (Cosmic Python Journey)

Welcome to Chapter 1 of our dual-track exploration! Here we examine how to build a pure Python domain model driven by unit tests (Low Gear TDD) and extract universal guidelines for Provable's automated app generation workflow.

---

## 🎯 Track A: Concrete Domain Implementation (Allocation & Inventory)

### Problem Statement
The allocation system must match customer `OrderLine`s to available stock `Batch`es according to business rules:
- **OrderLine**: Represents a request for a specific product SKU and quantity.
- **Batch**: Represents a shipment or stock allotment of a SKU with a fixed initial quantity and optional ETA date.
- **Business Invariant 1**: Allocating an `OrderLine` to a `Batch` reduces the batch's available quantity by `line.qty`.
- **Business Invariant 2**: A batch can only allocate an order line if `batch.sku == line.sku` and `batch.available_quantity >= line.qty`.
- **Business Invariant 3**: Allocation is idempotent (allocating an already allocated line has no additional effect).
- **Business Invariant 4**: Batches with earlier ETAs should be allocated first.

```mermaid
classDiagram
    class OrderLine {
        +str orderid
        +str sku
        +int qty
    }
    class Batch {
        +str reference
        +str sku
        +int initial_allocation
        +date eta
        +set _allocations
        +allocate(OrderLine)
        +deallocate(OrderLine)
        +available_quantity int
        +allocated_quantity int
    }
    Batch "1" o-- "*" OrderLine : _allocations
```

### Pure Python Domain Code (`domain/model.py`)
```python
from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

@dataclass(frozen=True)
class OrderLine:
    """Value Object: Immutable data structure defined purely by its attributes."""
    orderid: str
    sku: str
    qty: int

class Batch:
    """Entity: Object with persistent identity defined by `reference`."""
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = ref
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations: Set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __gt__(self, other: "Batch") -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
```

### Low Gear TDD Unit Tests (`tests/unit/test_batches.py`)
```python
from datetime import date
import pytest
from domain.model import Batch, OrderLine

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False

def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFY-CHAIR", 100)
    line = OrderLine("order-123", "EXPENSIVE-FOOTSTOOL", 10)
    assert batch.can_allocate(line) is False

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGEL-STATUE", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def make_batch_and_line(sku: str, batch_qty: int, line_qty: int):
    return Batch("batch-001", sku, batch_qty, eta=date.today()), OrderLine("order-123", sku, line_qty)
```

---

## 🌐 Track B: Universal Agent Workflow Guidelines (Extracted Rules)

Based on Chapter 1, we extract 4 universal guidelines that Provable will use when instructing developer agents to build domain logic for *any* application:

### Guideline 1: Pure Domain Isolation ("No Framework Leaks")
> **Rule**: Domain models must be written in pure Python standard library types (`dataclass`, `typing`, `enum`, `datetime`).
> **Enforcement**: Developer agents are prohibited from importing ORM decorators (`@declarative_mixin`, `Column`, `relationship`), web decorators (`@app.get`), or IO modules inside `domain/`.

### Guideline 2: Explicit Identity Distinction (Value Objects vs Entities)
> **Rule**: Agents must distinguish between immutable Value Objects and stateful Entities:
> - **Value Objects**: Use `@dataclass(frozen=True)` with equality based on values (e.g. `Money`, `Address`, `OrderLine`).
> - **Entities**: Use standard classes with identity defined strictly by a unique reference/ID (`__eq__` and `__hash__` based solely on `id`).

### Guideline 3: Low Gear TDD First ("Test Invariants, Not Frameworks")
> **Rule**: When building a new feature domain:
> 1. Agent must first write unit tests that verify domain invariants directly on domain objects (zero database, zero HTTP mocks).
> 2. Domain tests must execute in < 0.1s.

### Guideline 4: Encapsulate State Transitions Inside Domain Methods
> **Rule**: External callers (service layers or APIs) must NEVER mutate an entity's internal collections or private variables directly (e.g., `batch._allocations.add(line)` is forbidden). All state changes must occur through explicit domain methods (e.g. `batch.allocate(line)`).

---

*Documented in Obsidian Vault under `vault/06-Cosmic-Python-Journey/Chapter-01-Domain-Model.md`.*

<!-- END_FILE: vault/06-Cosmic-Python-Journey/Chapter-01-Domain-Model.md -->

---

## File 33: `vault/06-Cosmic-Python-Journey/Chapter-07-Aggregates-and-Optimistic-Concurrency.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/Chapter-07-Aggregates-and-Optimistic-Concurrency.md -->

# Chapter 7: Aggregates & Optimistic Concurrency Controls

Chapter 7 of *Architecture Patterns with Python* introduces **Aggregates** (consistency boundaries) and **DB-Enforced Optimistic Concurrency Controls**.

```mermaid
graph TD
    Client1["Thread 1: Concurrent Request"] --> Service["Service Layer"]
    Client2["Thread 2: Concurrent Request"] --> Service
    
    Service --> Aggregate["Aggregate Root (version_number)"]
    Aggregate --> ORM["SQLAlchemy ORM (version_id_col)"]
    
    ORM --> DB["SQLite / PostgreSQL DB"]
    
    DB -- "Thread 1 Commits (Version 1 -> 2)" --> Success["Transaction 1 Succeeded"]
    DB -- "Thread 2 Stale Version (Version 1)" --> ConcurrencyError["StaleDataError / Optimistic Lock Failure"]
```

---

## 🏛️ Architectural Implementation

In Provable, all synthesized domain models enforce Aggregate consistency boundaries and DB-enforced optimistic concurrency:

### 1. Aggregate Root `version_number` Tracking
Every Aggregate Root class (`Product`, `PizzaOrder`, `Appointment`) includes an explicit `version_number` attribute initialized to `0` or loaded from persistence:

```python
class PizzaOrder:
    def __init__(self, order_number: str, customer_name: str, items: List[OrderItem], version_number: int = 0):
        self.order_number = order_number
        self.customer_name = customer_name
        self.items = items
        self.version_number = version_number
        self.events: List[events.Event] = []

    def start_baking(self, oven_id: str) -> None:
        self.status = OrderStatus.BAKING
        self.version_number += 1  # Increment version on aggregate mutation
```

### 2. SQLAlchemy ORM `version_id_col` Mapping
In [`src/adapters/orm.py`](workspace/src/adapters/orm.py), the SQLAlchemy imperative mapper links `version_id_col` directly to the aggregate's database column:

```python
pizza_orders = Table(
    "pizza_orders",
    metadata,
    Column("order_number", String(255), primary_key=True),
    Column("customer_name", String(255), nullable=False),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

def start_mappers():
    mapper_registry.map_imperatively(
        PizzaOrder,
        pizza_orders,
        version_id_col=pizza_orders.c.version_number
    )
```

### 3. Concurrency Protection Invariant
If two concurrent worker threads attempt to modify the same Aggregate Root simultaneously, SQLAlchemy emits `sqlalchemy.orm.exc.StaleDataError`, rolling back the stale transaction and preserving data consistency.

---

## 🔗 Related Documentation
- [[05-DDD-TDD-Architecture-Guidelines]]
- [[Universal-Dynamic-Domain-AST-Generator]]
- [[Chapter-01-Domain-Model]]

<!-- END_FILE: vault/06-Cosmic-Python-Journey/Chapter-07-Aggregates-and-Optimistic-Concurrency.md -->

---

## File 34: `vault/06-Cosmic-Python-Journey/Chapter-13-Dependency-Injection-and-Bootstrap.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/Chapter-13-Dependency-Injection-and-Bootstrap.md -->

# Chapter 13: Dependency Injection & Bootstrap Container

Chapter 13 of *Architecture Patterns with Python* introduces the **Bootstrap Container** pattern to decouple initialization logic and dependencies from application entrypoints.

```mermaid
graph TD
    Entrypoint["FastAPI App / CLI Entrypoint"] --> Bootstrap["bootstrap.bootstrap() Container"]
    
    subgraph BOOTSTRAP_CONTAINER ["Bootstrap Container"]
        Bootstrap --> ORM["1. start_mappers()"]
        Bootstrap --> UoW["2. SqlAlchemyUnitOfWork()"]
        Bootstrap --> Bus["3. MessageBus(uow, event_handlers, command_handlers)"]
    end

    Bootstrap --> MessageBus["Active MessageBus Instance"]
    Entrypoint --> MessageBus
```

---

## 🏛️ Architectural Implementation

In Provable, all synthesized application stacks expose a `bootstrap.py` module ([`src/bootstrap.py`](workspace/src/bootstrap.py)) that wires application dependencies:

```python
import inspect
from typing import Callable, Dict, Type
from src.adapters import orm
from src.domain import commands, events
from src.service_layer import messagebus, unit_of_work

def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    publish: Callable = None,
) -> messagebus.MessageBus:
    """Dependency Injection Container and MessageBus Initializer."""
    if start_orm:
        orm.start_mappers()

    if uow is None:
        uow = unit_of_work.SqlAlchemyUnitOfWork()

    if publish is None:
        publish = lambda event: print(f"📡 EVENT PUBLISHED: {event}")

    # Inject dependencies dynamically using inspect.signature
    injected_command_handlers = {
        # Command handlers wired to UoW and publish dependencies
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers={},
        command_handlers=injected_command_handlers
    )
```

---

## 🔑 Key Benefits
1. **Testing Flexibility**: Tests can invoke `bootstrap(start_orm=False, uow=FakeUnitOfWork())` to inject fake repositories and test doubles without touching SQLite databases.
2. **Decoupled Entrypoints**: FastAPI API routes (`src/entrypoints/app.py`) do not manage ORM initialization or session factories; they simply call `bus.handle(command)`.

---

## 🔗 Related Documentation
- [[05-DDD-TDD-Architecture-Guidelines]]
- [[Universal-Dynamic-Domain-AST-Generator]]
- [[Chapter-07-Aggregates-and-Optimistic-Concurrency]]

<!-- END_FILE: vault/06-Cosmic-Python-Journey/Chapter-13-Dependency-Injection-and-Bootstrap.md -->

---

## File 35: `vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_condensed.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_condensed.md -->

# Architectural Law: Patterns with Python

This document serves as the **authoritative architectural reference** for AI agents and human developers working on this project. It condenses the principles of *Architecture Patterns with Python* into actionable, stack-aware guidelines. The core stack includes **Python, FastAPI, SQLAlchemy, SQLite, and React**.

This guide is designed to be self-contained, detailed, and directly applicable. It dictates how to organize code, manage state, and build scalable event-driven systems.

---

## Part 0: Philosophy & Mindset

### Why Designs Go Wrong (The Big Ball of Mud)
Software systems naturally tend toward chaos. Without deliberate architectural effort, a well-ordered codebase collapses into a "Big Ball of Mud"—a state characterized by high coupling, low cohesion, and a sameness of function where everything depends on everything else. In such systems, a small change in one place causes unpredictable side effects in completely unrelated areas, destroying development velocity.

### Encapsulation, Abstractions, Layering
Encapsulation is about simplifying behavior and hiding data. By identifying a task and assigning it to a well-defined object or function (an abstraction), we protect the rest of the system from its internal complexities. Abstracting away details helps make code expressive, testable, and easier to maintain. 
Layering ensures that different concerns are separated. The business rules should live in a pure layer, isolated from the messy details of web frameworks and databases.

### The Dependency Inversion Principle (DIP)
The Dependency Inversion Principle is a core tenet of our architecture:
1. High-level modules (business rules) should not depend on low-level modules (infrastructure, databases). Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

We insert abstractions between the high-level domain model and the low-level infrastructure (like SQLAlchemy) so they can evolve independently.

### TDD as a Design Practice
Test-Driven Development (TDD) is not just about testing; it is fundamentally a **design practice**. Writing the test first forces you to think about the interface and the behavior from the client's perspective before getting bogged down in the implementation details. 

### Fakes over Mocks Philosophy
Our testing philosophy strongly prefers **Fakes over Mocks**:
- **Mocks (London-school):** Verify *how* something is used. This tightly couples tests to implementation details, making refactoring a nightmare.
- **Fakes (Classic-school):** Working implementations designed for tests (e.g., an in-memory `FakeRepository`). They allow assertions about the end state of a system, keeping tests robust and decoupling them from internal mechanics.

### High Gear vs Low Gear TDD
- **High Gear:** Testing at the boundaries (e.g., Service Layer or API). This provides maximum coverage and safety for refactoring the underlying domain model.
- **Low Gear:** Testing individual domain objects (Entities, Value Objects). Use this when the logic is particularly complex and needs targeted verification. Most tests should be high gear.

---

## Part I: Building Architecture to Support Domain Modeling

### Domain Model (Entities, Value Objects, Domain Services, Domain Exceptions)

#### What it is
The Domain Model is the mental map of the business. It contains Entities, Value Objects, Domain Services, and Domain Exceptions. 
- **Value Object**: Uniquely identified by its data (e.g., `Money(amount, currency)`). Immutable.
- **Entity**: Has a long-lived identity (e.g., `User(id)`). Attributes may change, but it's the same entity.
- **Domain Service**: Stateless functions for operations that don't fit inside a single entity.
- **Domain Exception**: Custom exceptions expressing business rules (e.g., `OutOfStock`).

#### Why it matters
It isolates business logic from infrastructure, ensuring that the most valuable part of the codebase is purely focused on solving business problems without being polluted by database ORMs or HTTP routing.

#### Code Example
```python
from dataclasses import dataclass
from typing import List, Optional

class OutOfStock(Exception):
    pass

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref: str, sku: str, qty: int):
        self.reference = ref
        self.sku = sku
        self._purchased_quantity = qty
        self._allocations = set()  # type: set[OrderLine]

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Highly testable without databases. | Requires translating domain models to persistence models. |
| Pure representation of business rules. | Can feel overly complex for simple CRUD applications. |

#### Key Rules/Invariants
- No dependencies on ORMs (SQLAlchemy), web frameworks (FastAPI), or external APIs.
- Must be fully testable with pure unit tests (no mocking required).

---

### Repository Pattern

#### What it is
The Repository pattern is an abstraction over persistent storage. It provides an illusion of an in-memory collection of objects. Instead of the domain model inheriting from SQLAlchemy's `Base`, the ORM depends on the domain model via classical mappers or explicit translation functions.

#### Why it matters
It decouples the domain from the database. It allows us to easily swap out a real database for a `FakeRepository` in tests, drastically speeding up the test suite and preventing tests from touching the filesystem or network.

#### Code Example
```python
import abc
from typing import Set
# Domain model imports
from domain import model

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> model.Batch:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        self.session.add(batch)

    def get(self, reference: str) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).first()

class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> model.Batch:
        return next((b for b in self._batches if b.reference == reference), None)
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Simple interface between storage and domain model. | Maintaining ORM mappings or translation requires extra work. |
| Easy to make a `FakeRepository` for blazingly fast unit testing. | Extra indirection can frustrate those used to Active Record. |

#### Key Rules/Invariants
- Repositories must only return and accept domain objects, never ORM-specific models or rows.
- Repositories do not call `commit()`; that is the responsibility of the Unit of Work.

---

### Service Layer & Unit of Work

#### What it is
The Service Layer (or Use Case layer) orchestrates workflows: fetching data via Repositories, invoking domain logic, and saving changes. 
The Unit of Work (UoW) abstracts atomic operations, acting as a single entrypoint to repositories and ensuring that all changes are committed together or rolled back.

#### Why it matters
The Service Layer keeps domain logic pure by handling infrastructure coordination. The UoW ensures consistency, protecting the system from partial updates and corrupt states.

#### Code Example
```python
import abc
from sqlalchemy.orm import sessionmaker

class AbstractUnitOfWork(abc.ABC):
    batches: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

# Service Layer function
def allocate(line: model.OrderLine, uow: AbstractUnitOfWork) -> str:
    with uow:
        batch = uow.batches.get(line.sku)
        if batch is None:
            raise model.InvalidSku(f'Invalid sku {line.sku}')
        batch.allocate(line)
        uow.commit()
        return batch.reference
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| UoW makes transaction boundaries explicit. | Reinvents the wheel slightly if using an ORM that has its own UoW. |
| Service Layer explicitly documents application use cases. | Adds layers of boilerplate for simple apps. |

#### Key Rules/Invariants
- All state-altering operations must be wrapped in a UoW context manager.
- Endpoints (FastAPI) should only call Service Layer functions, never Repositories directly.

---

### Aggregates & Consistency Boundaries

#### What it is
An Aggregate is a cluster of associated objects treated as a unit for data changes. It acts as a consistency boundary, ensuring that all invariants are satisfied when state changes.

#### Why it matters
It resolves the tension between protecting invariants and allowing concurrency. Modifying multiple objects in complex graphs causes database lock contention. An Aggregate ensures you only ever modify a single root object per transaction.

#### Code Example
```python
class Product:
    # Product is the Aggregate Root. Batches cannot be modified directly.
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = [] # type: List[Event]

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            self.events.append(OutOfStock(line.sku))
            return None
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Defines explicit consistency boundaries, avoiding ORM performance problems. | Forces a rigid rule of "one aggregate per transaction." |
| Makes the system much easier to reason about. | Managing eventual consistency between aggregates is hard. |

#### Key Rules/Invariants
- Repositories should only return Aggregate Roots.
- A single transaction (UoW) must only update a single Aggregate.

---

## Part II: Event-Driven Architecture

### Domain Events & Message Bus

#### What it is
Domain Events are facts about things that happened (e.g., `OutOfStock`). 
The Message Bus is a publish-subscribe system that routes events to appropriate handlers.

#### Why it matters
It enables decoupling. Primary use cases can happen quickly, while side effects (like sending emails or updating read models) happen asynchronously or in separate, decoupled handlers.

#### Code Example
```python
from dataclasses import dataclass
from typing import List, Callable, Dict, Type

class Event:
    pass

@dataclass
class OutOfStock(Event):
    sku: str

def send_out_of_stock_notification(event: OutOfStock):
    print(f"Notification: Out of stock for {event.sku}")

HANDLERS: Dict[Type[Event], List[Callable]] = {
    OutOfStock: [send_out_of_stock_notification],
}

def handle(event: Event):
    for handler in HANDLERS.get(type(event), []):
        handler(event)
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Decouples primary logic from secondary side effects. | Control flow is implicit and harder to trace. |
| Perfectly models real-world business processes. | Requires disciplined logging to debug. |

#### Key Rules/Invariants
- Events must be named in the past tense (e.g., `OrderAllocated`).
- The Unit of Work should collect events from aggregates and dispatch them via the Message Bus.

---

### Commands vs Events

#### What it is
- **Commands:** Capture intent. Imperative verbs (e.g., `AllocateStock`). Directed to a single handler. Must fail noisily if unsuccessful.
- **Events:** Capture facts. Past tense (e.g., `StockAllocated`). Broadcast to many handlers. Sender doesn't care if a handler fails.

#### Why it matters
Differentiating them allows us to isolate failures. A Command modifies state and must succeed. An Event triggers side effects, which can fail independently without rolling back the primary Command.

#### Code Example
```python
class Command:
    pass

@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int

Message = Command | Event

def handle(message: Message, uow: AbstractUnitOfWork):
    queue = [message]
    while queue:
        msg = queue.pop(0)
        if isinstance(msg, Event):
            for handler in EVENT_HANDLERS[type(msg)]:
                try:
                    handler(msg, uow=uow)
                    queue.extend(uow.collect_new_events())
                except Exception:
                    continue # Events fail independently
        elif isinstance(msg, Command):
            handler = COMMAND_HANDLERS[type(msg)]
            handler(msg, uow=uow) # Commands fail noisily
            queue.extend(uow.collect_new_events())
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Clear understanding of what must succeed vs what can be retried. | The semantic difference can be subtle, leading to debate. |

#### Key Rules/Invariants
- Commands must be handled by exactly ONE handler.
- Events can be handled by ZERO OR MORE handlers.

---

### CQRS (Command-Query Responsibility Segregation)

#### What it is
CQRS dictates that Reads (Queries) and Writes (Commands) are fundamentally different operations and should have different models. Commands use the complex Domain Model and Repositories. Queries can bypass the domain entirely and use raw SQL or specialized view models.

#### Why it matters
Writes require strict consistency and business rules (Aggregates). Reads require high performance, cacheability, and often complex joins. Forcing both through the same ORM models leads to performance bottlenecks and compromised designs.

#### Code Example
```python
# A read-only query bypassing the domain model
def get_allocations(orderid: str, uow: SqlAlchemyUnitOfWork):
    with uow:
        # Use raw SQL or lightweight ORM queries for performance
        result = uow.session.execute(
            'SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid',
            {'orderid': orderid}
        )
        return [dict(r) for r in result]
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Massive performance improvements for reads. | Data in read models may be eventually consistent (stale). |
| Simplifies the write domain model by removing read-specific quirks. | Requires managing separate read models/tables. |

#### Key Rules/Invariants
- Queries must never modify state.
- Commands must not return data (other than maybe an identifier or success status).

---

## Part III: Infrastructure & Bootstrapping

### Dependency Injection (Composition Root)

#### What it is
The Composition Root is a bootstrap script executed at application startup. It wires up dependencies (like Repositories and UoW) and injects them into the Message Bus or Service Layer.

#### Why it matters
It concentrates all knowledge of infrastructure into one place. This makes it trivial to swap out a SQL database for an in-memory dictionary during testing, without touching the application code.

#### Code Example
```python
import inspect

def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)

def bootstrap(
    uow: AbstractUnitOfWork = None,
    notifications: AbstractNotifications = None,
    publish: Callable = None,
) -> MessageBus:
    if uow is None:
        uow = SqlAlchemyUnitOfWork()
    
    dependencies = {'uow': uow, 'notifications': notifications, 'publish': publish}
    
    injected_event_handlers = {
        event_type: [inject_dependencies(handler, dependencies) for handler in event_handlers]
        for event_type, event_handlers in EVENT_HANDLERS.items()
    }
    # ... wire up command handlers similarly
    return MessageBus(injected_event_handlers, injected_command_handlers)
```

#### Trade-offs Table
| Pros | Cons |
| --- | --- |
| Centralizes configuration. | Boilerplate setup required. |
| Pure functions/classes without framework magic. | |

#### Key Rules/Invariants
- Never instantiate infrastructure dependencies (like DB sessions) deep inside business logic.
- Always inject dependencies from the outside.

---

### Project Structure Template

```text
â”œâ”€â”€ src
â”‚   â”œâ”€â”€ myapp
â”‚   â”‚   â”œâ”€â”€ adapters      # Repositories, ORM mappers, External API clients
â”‚   â”‚   â”œâ”€â”€ domain        # Entities, Value Objects, Domain Exceptions
â”‚   â”‚   â”œâ”€â”€ entrypoints   # FastAPI routers, CLI commands, Event consumers
â”‚   â”‚   â””â”€â”€ service_layer # Use cases, UoW, Message Bus, Handlers
â””â”€â”€ tests
    â”œâ”€â”€ e2e             # Tests targeting FastAPI endpoints
    â”œâ”€â”€ integration     # Tests targeting Repositories/DB
    â””â”€â”€ unit            # Tests targeting Service Layer with Fakes
```

---

### Validation (Syntactic, Semantic, Pragmatic)

1. **Syntactic:** Is the data well-formed? (e.g., "quantity is an integer"). Validate at the **entrypoints** (e.g., using Pydantic in FastAPI). Be a tolerant reader.
2. **Semantic:** Does the data make sense? (e.g., "SKU exists in the system"). Validate in the **Service Layer** before executing commands.
3. **Pragmatic:** Business rules in context (e.g., "Do we have enough stock?"). Validate inside the **Domain Model**.

---

## Part IV: Practical Guidance

### Getting There from Legacy Code (Strangler Fig)
To migrate a Big Ball of Mud:
1. Carve out a Service Layer for specific use cases.
2. Stop ORM leakage by introducing Repositories.
3. For moving to Microservices, use the **Strangler Fig Pattern**: intercept events from the legacy system, build the new system to consume those events, and gradually strangle the old system.

### Identifying Aggregates
Highly connected object graphs kill performance. Break direct object references (e.g., `user.workspaces[0].docs`) and replace them with IDs (e.g., `Workspace(owner_id=user.id)`). An aggregate represents a true transactional consistency boundary.

### Footguns and Pitfalls
- **Reliable messaging is hard:** Redis pub/sub drops messages. Use reliable brokers (Kafka, RabbitMQ) for external events, or use the Outbox Pattern.
- **Eventual Consistency:** UI/React clients must be designed to handle eventual consistency (e.g., optimistic UI updates or polling/WebSockets) because read models may lag behind writes.
- **Idempotency:** All event handlers must be idempotent. Processing the same event twice must not corrupt state.

### The Complete Pattern Architecture Diagram

```mermaid
graph TD
    Client[Web/React Client] -->|HTTP POST| Web[FastAPI Entrypoint]
    Web -->|Command| Bus[Message Bus]
    Bus -->|Routes to| Handler[Service Layer Handler]
    
    Handler -->|1. Gets| UoW[Unit of Work]
    UoW -->|2. Provides| Repo[Repository]
    Repo -->|3. Loads| Agg[Aggregate Root]
    
    Handler -->|4. Mutates| Agg
    Handler -->|5. Commits| UoW
    
    UoW -->|6. Flushes| DB[(SQLite/Postgres)]
    UoW -->|7. Emits| Events[Domain Events]
    Events -->|8. Back to| Bus
```

This guide encapsulates the rules for maintaining a robust, scalable, and decoupled architecture. Follow these patterns rigorously.

<!-- END_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_condensed.md -->

---

## File 36: `vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_dump.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_dump.md -->

﻿# Architecture Patterns with Python - Part 1

## Introduction: Why Do Our Designs Go Wrong?
Software systems tend toward chaos. Without deliberate effort, a well-ordered architecture collapses into a "Big Ball of Mud", characterized by a sameness of function where everything is coupled to everything else.

### Encapsulation and Abstractions
Encapsulation covers simplifying behavior and hiding data. We encapsulate behavior by identifying a task and giving it to a well-defined object or function, called an abstraction. Abstracting away details helps make code expressive, testable, and easier to maintain. 

### The Dependency Inversion Principle (DIP)
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

High-level modules deal with real-world business concepts, while low-level modules deal with technical infrastructure (network, filesystem, databases). We insert an abstraction layer between them so they can change independently. 

---

## Chapter 1: Domain Modeling
The domain model is the mental map business owners have of their business. It is the part of your code that is closest to the business, most likely to change, and where you deliver the most value.

### Entities vs Value Objects
- **Value Object**: Any domain object uniquely identified by the data it holds (e.g., an OrderLine or Money). Usually immutable. If you change an attribute, it becomes a different object.
- **Entity**: A domain object with long-lived identity (e.g., a Person or a Batch). Its attributes may change over time, but it remains the same entity. Usually implements equality (`__eq__`) based on a unique reference.

### Domain Service
Not everything has to be an object. If an operation doesn't naturally fit inside a stateful entity or value object, it can be a stateless function (e.g., `allocate(line, batches)`).

### Domain Exceptions
Exceptions can express domain concepts (e.g., `OutOfStock` when trying to allocate beyond available quantity).

---

## Chapter 2: Repository Pattern
The Repository pattern is an abstraction over persistent storage. It hides the details of data access by giving the illusion of a collection of in-memory objects.

### Inverting the Dependency
Instead of the model depending on the ORM (e.g., inheriting from SQLAlchemy's `Base`), the ORM should depend on the model. Using SQLAlchemy's classical mapper (`mapper(model.OrderLine, order_lines)`) keeps the domain pure and unaware of the database.

### Abstract Repository
```python
class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError
```

### Trade-offs: Repository Pattern
| Pros | Cons |
| --- | --- |
| Simple interface between storage and domain model. | Maintaining ORM mappings by hand requires extra work. |
| Easy to make a `FakeRepository` for unit testing. | Extra layer of indirection increases maintenance costs. |
| Keeps focus on business logic rather than DB schemas. | Can be confusing for programmers unfamiliar with the pattern. |

---

## Chapter 3: Coupling and Abstractions
When we are unable to change component A for fear of breaking component B, we say they are coupled. We can reduce coupling by introducing a simpler abstraction between them.

### Functional Core, Imperative Shell (FCIS)
Isolate the stateful, I/O-heavy parts of the application from the business logic. Let the business logic (Functional Core) take simple data structures and return simple data structures representing actions to be taken, which the Imperative Shell then executes.

### Testing Philosophy: Fakes over Mocks
- **Mocks** (London-school TDD): Verify *how* something gets used (e.g., `assert_called_once_with`). Lead to tests tightly coupled to implementation.
- **Fakes** (Classic-style TDD): Working implementations of dependencies designed for tests (e.g., an in-memory FakeRepository). Allow assertions about the end state of a system.
- TDD is a design practice first. Over-mocked tests get overwhelmed with setup code and hinder refactoring.

---

## Chapter 4: Service Layer
The Service Layer (or Orchestration Layer) orchestrates workflows and defines the use cases of the system. 

### Responsibilities of a Service Layer
1. Fetch objects from the repository.
2. Validate input against current state.
3. Call a domain service.
4. Persist any changes.

By keeping orchestration logic in the service layer, the domain logic stays pure, and the web entrypoints (e.g., Flask APIs) remain thin.

### Service Layer Implementation
```python
def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
```

### Trade-offs: Service Layer
| Pros | Cons |
| --- | --- |
| Single place capturing all application use cases. | Can seem like boilerplate for purely CRUD web apps. |
| Defines a clear API, allowing independent refactoring. | Requires passing around stateful components. |
| Enables fast "high gear" unit testing with fakes. | |
# Architecture Patterns with Python - Part 2 Extract

## Chapter 6: Unit of Work Pattern

### Pattern Definition and Explanation
The Unit of Work (UoW) pattern is an abstraction over the idea of atomic operations. It allows decoupling the service layer from the data layer. The UoW acts as a single entrypoint to persistent storage and keeps track of what objects were loaded and of the latest state. This provides:
1. A stable snapshot of the database to work with.
2. A way to persist all changes at once, so if something goes wrong, the system doesn't end up in an inconsistent state.
3. A simple API to persistence concerns and a handy place to get a repository.

### Code Example
```python
class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
```

### Wrap-Up / Recap
- **The Unit of Work pattern is an abstraction around data integrity**: It helps enforce consistency of the domain model and improves performance by letting us perform a single flush operation at the end of an operation.
- **It works closely with the Repository and Service Layer patterns**: The UoW completes abstractions over data access by representing atomic updates.
- **This is a lovely case for a context manager**: Context managers are an idiomatic way of defining scope in Python.
- **SQLAlchemy already implements this pattern**: We introduce an even simpler abstraction over the SQLAlchemy Session object in order to "narrow" the interface between the ORM and our code.

### Trade-offs
| Pros | Cons |
|------|------|
| We have a nice abstraction over atomic operations, and the context manager makes it easy to see what blocks of code are grouped atomically. | Your ORM probably already has some perfectly good abstractions around atomicity (like SQLAlchemy context managers). |
| Explicit control over when a transaction starts and finishes; application fails in a way that is safe by default. | You have to think quite carefully about things like rollbacks, multithreading, and nested transactions. |
| It's a nice place to put all your repositories so client code can access them. | |
| Atomicity isn't only about transactions; it can help us work with events and the message bus. | |

## Chapter 7: Aggregates and Consistency Boundaries

### Pattern Definition and Explanation
An **Aggregate** is a cluster of associated objects that we treat as a unit for the purpose of data changes. It helps to resolve the tension between protecting invariants and allowing for concurrency. The aggregate acts as a boundary where every operation ends in a consistent state.

### Code Example
```python
class Product:
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = [] # type: List[events.Event]

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(
                b for b in sorted(self.batches) if b.can_allocate(line)
            )
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None
```

### Wrap-Up / Recap
- **Aggregates are your entrypoints into the domain model**: By restricting the number of ways that things can be changed, we make the system easier to reason about.
- **Aggregates are in charge of a consistency boundary**: An aggregate's job is to manage business rules about invariants as they apply to a group of related objects.
- **Aggregates and concurrency issues go together**: Choosing the right aggregate is about performance as well as conceptual organization.

### Trade-offs
| Pros | Cons |
|------|------|
| Choosing aggregates lets you decide which domain classes are public and which aren't. | Yet another new concept for developers to take on. |
| Modeling operations around explicit consistency boundaries helps avoid ORM performance problems. | Sticking rigidly to the rule of modifying only one aggregate at a time is a big mental shift. |
| Putting the aggregate in sole charge of state changes makes the system easier to reason about. | Dealing with eventual consistency between aggregates can be complex. |

## Part II: Event-Driven Architecture (Intro)

### Philosophical Statement
> "I'm sorry that I long ago coined the term 'objects' for this topic because it gets many people to focus on the lesser idea. The big idea is 'messaging.'...The key in making great and growable systems is much more to design how its modules communicate rather than what their internal properties and behaviors should be." â€” Alan Kay

## Chapter 8: Events and the Message Bus

### Pattern Definition and Explanation
- **Domain Events**: Trigger workflows that cross consistency boundaries. Events are facts about things that have happened.
- **Message Bus**: Provides a unified way of invoking use cases from any endpoint. It acts as a publish-subscribe system mapping events to their handlers.

### Code Example
```python
@dataclass
class OutOfStock(Event):
    sku: str

def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
}
```

### Wrap-Up / Recap
- **Events can help with the single responsibility principle**: Events help keep things tidy by separating primary use cases from secondary ones.
- **A message bus routes messages to handlers**: It's a piece of dumb infrastructure for getting messages around the system.
- **Options for publishing events**:
  1. Service layer raises events and passes them to message bus.
  2. Domain model raises events, service layer passes them to message bus.
  3. UoW collects events from aggregates and passes them to message bus (recommended).

### Trade-offs
| Pros | Cons |
|------|------|
| A message bus separates responsibilities when taking multiple actions per request. | An additional concept to learn; UoW magically raising events might obscure flow. |
| Event handlers are decoupled from core application logic. | Hidden event-handling code executes synchronously by default. |
| Domain events model the real world and align with business language. | Event-driven workflows can make it harder to trace the lifecycle of a request. |

## Chapter 9: Going to Town on the Message Bus

### Pattern Definition and Explanation
Transforming the application fundamentally into a message processor. External API calls and internal side effects all map to events (e.g., `AllocationRequired`, `BatchQuantityChanged`) which are routed through the message bus to handlers. This eliminates the distinction between internal and external event handlers.

### Code Example
```python
def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
        queue.extend(uow.collect_new_events())
    return results
```
# Architecture Patterns with Python - Part 3 Extract (Chapters 10-13, Epilogue)

## Chapter 10: Commands and Command Handler

### Pattern Definitions: Commands vs Events
*   **Commands:** Capture intent. They express our wish for the system to do something. They are sent by one actor to another specific actor with the expectation that a particular thing will happen. They are named with imperative mood verb phrases like "allocate stock". When they fail, the sender needs to receive error information.
*   **Events:** Capture facts about things that happened in the past. They are broadcast by an actor to all interested listeners. Senders should not care whether the receivers succeeded or failed. They are named with past-tense verb phrases like "order allocated".

### Trade-off Table: Events vs Commands

| Feature | Event | Command |
| :--- | :--- | :--- |
| Named | Past tense | Imperative mood |
| Error handling | Fail independently | Fail noisily |
| Sent to | All listeners | One recipient |

### Error Handling Philosophy
By separating messages into commands and events, we make it possible for things to fail in isolation, improving overall reliability. A command should modify a single aggregate and succeed or fail in totality. Any other bookkeeping, cleanup, and notification happen via events. Event handlers don't need to succeed for the command to be successful. We invite failure but handle it by making failures smaller and more isolated.

### Code Example: Dispatching Events vs Commands differently

```python
Message = Union[commands.Command, events.Event]

def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} was not an Event or Command')
    return results

def handle_event(event: events.Event, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception('Exception handling event %s', event)
            continue

def handle_command(command: commands.Command, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork):
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception('Exception handling command %s', command)
        raise
```

### Wrap-Up / Trade-offs Table

| Pros | Cons |
| :--- | :--- |
| Treating commands and events differently helps us understand which things have to succeed and which things we can tidy up later. | The semantic differences between commands and events can be subtle. Expect bikeshedding arguments. |
| Explicit names like `CreateBatch` convey user intent clearly. | We're expressly inviting failure, choosing to make failures smaller and isolated. This can make the system harder to reason about and requires better monitoring. |


## Chapter 11: Event-Driven Architecture (Microservices Integration)

### Temporal Decoupling and Microservices
A naive approach to microservices splits systems by nouns (e.g., Batches, Orders), linking them with synchronous HTTP calls. This creates a "Distributed Ball of Mud" with temporal coupling: every part of the system has to work at the same time for any part of it to work. 

Instead, think in verbs (e.g., ordering, allocating). Like aggregates, microservices should be consistency boundaries. Between two services, accept eventual consistency using asynchronous messaging (events). This reduces the strength of coupling (Connascence of Name instead of Connascence of Execution/Timing) and allows services to fail independently.

### Trade-off Table: Event-Based Integration

| Pros | Cons |
| :--- | :--- |
| Avoids the distributed big ball of mud. | The overall flows of information are harder to see. |
| Services are decoupled: it's easier to change individual services and add new ones. | Eventual consistency is a new concept to deal with. |
| | Message reliability and delivery guarantees need thinking through. |


## Chapter 12: Command-Query Responsibility Segregation (CQRS)

### Pattern Definition: CQRS
Reads (queries) and writes (commands) are different and should be treated differently. Domain models apply complex business rules and consistency boundaries (aggregates) during writes. Reads often require different data shapes, can tolerate stale (eventually consistent) data, and need high cacheability and performance. Command-Query Separation (CQS) states that functions should either modify state or answer questions, but never both.

### Trade-off Table: Read vs Write

| | Read side | Write side |
| :--- | :--- | :--- |
| Behavior | Simple read | Complex business logic |
| Cacheability | Highly cacheable | Uncacheable |
| Consistency | Can be stale | Must be transactionally consistent |

### Code Example: Updating a Read Model Table via Event Handler

```python
def add_allocation_to_read_model(
    event: events.Allocated, uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            'INSERT INTO allocations_view (orderid, sku, batchref)'
            ' VALUES (:orderid, :sku, :batchref)',
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
        )
        uow.commit()
```

### Trade-off Table: View Model Options

| Option | Pros | Cons |
| :--- | :--- | :--- |
| Just use repositories | Simple, consistent approach. | Expect performance issues with complex query patterns. |
| Use custom queries with ORM | Allows reuse of DB config and models. | Adds another query language with quirks. |
| Use hand-rolled SQL | Fine control over performance, standard syntax. | DB schema changes affect hand-rolled queries and ORM. |
| Separate read stores with events | Read-only copies scale easily; views can be customized for queries. | Complex technique; suspicious motives. |


## Chapter 13: Dependency Injection and Bootstrapping

### Pattern Definition: Composition Root (Bootstrap)
We use explicit dependencies (Dependency Inversion Principle) to avoid heavy monkeypatching and coupling to implementations. The Composition Root (bootstrap script) is a single place where dependencies are configured, instantiated, and injected into handlers, initializing the message bus at runtime.

### Code Example: Manual DI with Closures/Partials

```python
def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
```

### Wrap-Up
Setting up Dependency Injection (DI) is part of the one-time initialization done at app startup in a bootstrap script. The script provides sensible defaults for adapters and is a single place to override those adapters with fakes for testing. For complex dependency chains, a DI framework might be useful, but manual DI via functions/classes is often sufficient.


## Epilogue: Getting There from Here

### Extracting Use Cases from a Ball of Mud
To break apart a legacy system, start by separating responsibilities into a Service Layer. Identify use cases with imperative names (e.g., "Apply Billing Charges"). Each use case orchestrates work: starts a transaction, fetches data, updates the domain model, and persists changes. Move data-access and orchestration out of the domain model and into the use cases.

### Identifying Aggregates
Highly connected object graphs (where `user.account.workspaces[0].documents` is possible) kill performance. Break direct links and bidirectional relationships by replacing object references with identifiers. An aggregate is a consistency boundary; each use case should update a single aggregate at a time to remain eventually consistent.

### The Strangler Fig Pattern
To move to microservices, use "event interception":
1. Raise events for changes in the old system.
2. Build a new system that consumes those events for its domain model.
3. Replace the older system with the new one.
# Architecture Patterns with Python - Part 4

## Footguns

Before attempting to implement these patterns in a production system, consider the following caveats:

### Reliable messaging is hard
Redis pub/sub is not reliable and shouldn't be used as a general-purpose messaging tool. Consider using tools like Event Store, RabbitMQ, or Amazon EventBridge. Understanding trade-offs in distributed messaging is essential (e.g., exactly-once delivery is a myth).

### We explicitly choose small, focused transactions that can fail independently
In our models, updating an aggregate and related aggregates often happen in separate units of work. You will need monitoring to know when these transactions fail, and tooling to replay events. Using a transaction log as your message broker (e.g., Kafka or EventStore) or the Outbox pattern can help.

### We don't discuss idempotency
Handlers should ideally be idempotent so that calling them repeatedly with the same message will not make repeated changes to state. This enables safely retrying events when they fail.

### Your events will need to change their schema over time
You'll need a way of documenting your events and sharing schemas with consumers (e.g., JSON schema). Versioning event-sourced systems is a complex topic.

## Appendix A: Summary Diagram and Table

### Components of our architecture

| Layer | Component | Description |
|-------|-----------|-------------|
| **Domain** | Entity | A domain object whose attributes may change but that has a recognizable identity over time. |
| | Value object | An immutable domain object whose attributes entirely define it. Fungible with identical objects. |
| | Aggregate | Cluster of associated objects treated as a unit for data changes. Defines a consistency boundary. |
| | Event | Represents something that happened. |
| | Command | Represents a job the system should perform. |
| **Service Layer** | Handler | Receives a command or event and performs what needs to happen. |
| | Unit of work | Abstraction around data integrity. Represents an atomic update. Tracks new events on retrieved aggregates. |
| | Message bus (internal) | Routes commands and events to the appropriate handler. |
| **Adapters** | Repository | Abstraction around persistent storage. Each aggregate has its own repository. |
| | Event publisher | Pushes events onto the external message bus. |
| **Entrypoints** | Web | Receives web requests and translates them into commands for the internal message bus. |
| | Event consumer | Reads events from the external message bus and translates them into commands for the internal message bus. |
| **External** | External message bus | Infrastructure that different services use to intercommunicate via events. |

## Appendix B: A Template Project Structure

The basic folder structure for a well-organized project:

```
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ Makefile
â”œâ”€â”€ README.md
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ mypy.ini
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ src
â”‚   â”œâ”€â”€ allocation
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ adapters
â”‚   â”‚   â”‚   â”œâ”€â”€ orm.py
â”‚   â”‚   â”‚   â””â”€â”€ repository.py
â”‚   â”‚   â”œâ”€â”€ config.py
â”‚   â”‚   â”œâ”€â”€ domain
â”‚   â”‚   â”‚   â””â”€â”€ model.py
â”‚   â”‚   â”œâ”€â”€ entrypoints
â”‚   â”‚   â”‚   â””â”€â”€ flask_app.py
â”‚   â”‚   â””â”€â”€ service_layer
â”‚   â”‚       â””â”€â”€ services.py
â”‚   â””â”€â”€ setup.py
â””â”€â”€ tests
    â”œâ”€â”€ conftest.py
    â”œâ”€â”€ e2e
    â”œâ”€â”€ integration
    â”œâ”€â”€ pytest.ini
    â””â”€â”€ unit
```

- **`config.py`**: Centralized configuration management using environment variables.
- **`docker-compose.yml`**: Defines the different services (containers) needed. 
- **`setup.py`**: Makes the `src` folder pip-installable for easy imports.

## Appendix C: Swapping Out the Infrastructure

The benefits of the Repository, Unit of Work, and Service Layer patterns become clear when swapping out infrastructure, such as moving from a database to CSV files. Because infrastructure concerns are decoupled from the domain model and service layer, switching to CSVs only requires writing new Repository and UnitOfWork classes, allowing full reuse of domain logic.

## Appendix D: Repository and Unit of Work Patterns with Django

To use Django instead of SQLAlchemy:
- **Repository Pattern**: You can create a DjangoRepository that implements `add`, `get`, and `list`. Since Django's ORM couples models to the database, you'll need custom methods on your Django models to translate to and from your pure domain model (e.g., `update_from_domain` and `to_domain`).
- **Unit of Work Pattern**: Implement a DjangoUnitOfWork that sets `transaction.set_autocommit(False)` on entry and uses `transaction.commit()` or `transaction.rollback()`.
- **Views**: Django views act as adapters, functioning similarly to Flask endpoints, passing requests to the service layer.

**Caveat**: If your app is heavily read-oriented or a simple CRUD app, these patterns may add unnecessary boilerplate and fight against Django's strengths. 

## Appendix E: Validation

Validation is about testing inputs to ensure they match criteria before processing (preconditions). It's useful to categorize it into three subtypes:

### 1. Syntactic Validation
Validating the structure of incoming data (e.g., "Quantity must be a positive integer").
- **Where**: Validate syntax at the edge of the system (e.g., on the message class or API endpoint). Handlers should only receive well-formed messages.
- **Tolerant Reader Pattern**: Be strict in what you send, lenient in what you receive. Read only the fields you need, and don't overspecify their structure (e.g., treat a SKU as an opaque string rather than strictly validating its format, unless you own the format).

### 2. Semantic Validation
Validating the meaning of the data (e.g., "The product SKU exists").
- **Where**: Often handled at the service layer or message handler layer using preconditions (e.g., checking if an entity exists before processing).

### 3. Pragmatic Validation
Validating business rules in context (e.g., "Is there enough stock available to fulfill this order?").
- **Where**: Pragmatics belong in the domain model. This is the core business logic.

<!-- END_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python_dump.md -->

---

## File 37: `vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python.md`

<!-- START_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python.md -->

&#x20;PDF To Markdown Converter



&#x20;   Debug View

&#x20;   Result View



1.Preface

a.Managing Complexity, Solving Business

Problems

b.Why Python?

c.TDD, DDD, and Event-Driven Architecture

d.Who Should Read This Book

e.A Brief Overview of What You’ll Learn

i.Part I, Building an Architecture to

Support Domain Modeling

ii.Part II, Event-Driven Architecture

iii.Addtional Content

f.Example Code and Coding Along

g.License

h.Conventions Used in This Book

i.O’Reilly Online Learning

j.How to Contact O’Reilly

k.Acknowledgments

2.Introduction

a.Why Do Our Designs Go Wrong?

b.Encapsulation and Abstractions

c.Layering

d.The Dependency Inversion Principle

e.A Place for All Our Business Logic: The

Domain Model

3.I. Building an Architecture to Support Domain

Modeling

4.1. Domain Modeling

a.What Is a Domain Model?

b.Exploring the Domain Language

c.Unit Testing Domain Models

i.Dataclasses Are Great for Value

Objects

ii.Value Objects and Entities

d.Not Everything Has to Be an Object: A Domain

Service Function

i.Python’s Magic Methods Let Us Use

Our Models with Idiomatic Python

ii.Exceptions Can Express Domain

Concepts Too

5.2. Repository Pattern

a.Persisting Our Domain Model

b.Some Pseudocode: What Are We Going to

Need?

c.Applying the DIP to Data Access

d.Reminder: Our Model

i.The “Normal” ORM Way: Model

Depends on ORM

ii.Inverting the Dependency: ORM

Depends on Model

e.Introducing the Repository Pattern

i.The Repository in the Abstract

ii.What Is the Trade-Off?

f.Building a Fake Repository for Tests Is Now

Trivial!

g.What Is a Port and What Is an Adapter, in

Python?

h.Wrap-Up

6.3. A Brief Interlude: On Coupling and Abstractions

a.Abstracting State Aids Testability

b.Choosing the Right Abstraction(s)

c.Implementing Our Chosen Abstractions

i.Testing Edge to Edge with Fakes and

Dependency Injection

ii.Why Not Just Patch It Out?

d.Wrap-Up

7.4. Our First Use Case: Flask API and Service Layer

a.Connecting Our Application to the Real World

b.A First End-to-End Test

c.The Straightforward Implementation

d.Error Conditions That Require Database

Checks

e.Introducing a Service Layer, and Using

FakeRepository to Unit Test It

i.A Typical Service Function

f.Why Is Everything Called a Service?

g.Putting Things in Folders to See Where It All

Belongs

h.Wrap-Up

i.The DIP in Action

8.5. TDD in High Gear and Low Gear

a.How Is Our Test Pyramid Looking?

b.Should Domain Layer Tests Move to the

Service Layer?

c.On Deciding What Kind of Tests to Write

d.High and Low Gear

e.Fully Decoupling the Service-Layer Tests from

the Domain

i.Mitigation: Keep All Domain

Dependencies in Fixture Functions

ii.Adding a Missing Service

f.Carrying the Improvement Through to the E2E

Tests

g.Wrap-Up

9.6. Unit of Work Pattern

a.The Unit of Work Collaborates with the

Repository

b.Test-Driving a UoW with Integration Tests

c.Unit of Work and Its Context Manager

i.The Real Unit of Work Uses

SQLAlchemy Sessions

ii.Fake Unit of Work for Testing

d.Using the UoW in the Service Layer

e.Explicit Tests for Commit/Rollback Behavior

f.Explicit Versus Implicit Commits

g.Examples: Using UoW to Group Multiple

Operations into an Atomic Unit

i.Example 1: Reallocate

ii.Example 2: Change Batch Quantity

h.Tidying Up the Integration Tests

i.Wrap-Up

10.7. Aggregates and Consistency Boundaries

a.Why Not Just Run Everything in a

Spreadsheet?

b.Invariants, Constraints, and Consistency

i.Invariants, Concurrency, and Locks

c.What Is an Aggregate?

d.Choosing an Aggregate

e.One Aggregate = One Repository

f.What About Performance?

g.Optimistic Concurrency with Version Numbers

i.Implementation Options for Version

Numbers

h.Testing for Our Data Integrity Rules

i.Enforcing Concurrency Rules by Using

Database Transaction Isolation Levels

ii.Pessimistic Concurrency Control

Example: SELECT FOR UPDATE

i.Wrap-Up

j.Part I Recap

11.II. Event-Driven Architecture

12.8. Events and the Message Bus

a.Avoiding Making a Mess

i.First, Let’s Avoid Making a Mess of

Our Web Controllers

ii.And Let’s Not Make a Mess of Our

Model Either

iii.Or the Service Layer!

b.Single Responsibility Principle

c.All Aboard the Message Bus!

i.The Model Records Events

ii.Events Are Simple Dataclasses

iii.The Model Raises Events

iv.The Message Bus Maps Events to

Handlers

d.Option 1: The Service Layer Takes Events from

the Model and Puts Them on the Message Bus

e.Option 2: The Service Layer Raises Its Own

Events

f.Option 3: The UoW Publishes Events to the

Message Bus

g.Wrap-Up

13.9. Going to Town on the Message Bus

a.A New Requirement Leads Us to a New

Architecture

i.Imagining an Architecture Change:

Everything Will Be an Event Handler

b.Refactoring Service Functions to Message

Handlers

i.The Message Bus Now Collects Events

from the UoW

ii.Our Tests Are All Written in Terms of

Events Too

iii.A Temporary Ugly Hack: The Message

Bus Has to Return Results

iv.Modifying Our API to Work with

Events

c.Implementing Our New Requirement

i.Our New Event

d.Test-Driving a New Handler

i.Implementation

ii.A New Method on the Domain Model

e.Optionally: Unit Testing Event Handlers in

Isolation with a Fake Message Bus

f.Wrap-Up

i.What Have We Achieved?

ii.Why Have We Achieved?

14.10. Commands and Command Handler

a.Commands and Events

b.Differences in Exception Handling

c.Discussion: Events, Commands, and Error

Handling

d.Recovering from Errors Synchronously

e.Wrap-Up

15.11. Event-Driven Architecture: Using Events to

Integrate Microservices

a.Distributed Ball of Mud, and Thinking in

Nouns

b.Error Handling in Distributed Systems

c.The Alternative: Temporal Decoupling Using

Asynchronous Messaging

d.Using a Redis Pub/Sub Channel for

Integration

e.Test-Driving It All Using an End-to-End Test

i.Redis Is Another Thin Adapter Around

Our Message Bus

ii.Our New Outgoing Event

f.Internal Versus External Events

g.Wrap-Up

16.12. Command-Query Responsibility Segregation

(CQRS)

a.Domain Models Are for Writing

b.Most Users Aren’t Going to Buy Your

Furniture

c.Post/Redirect/Get and CQS

d.Hold On to Your Lunch, Folks

e.Testing CQRS Views

f.“Obvious” Alternative 1: Using the Existing

Repository

g.Your Domain Model Is Not Optimized for

Read Operations

h.“Obvious” Alternative 2: Using the ORM

i.SELECT N+1 and Other Performance

Considerations

j.Time to Completely Jump the Shark

i.Updating a Read Model Table Using an

Event Handler

k.Changing Our Read Model Implementation Is

Easy

l.Wrap-Up

17.13. Dependency Injection (and Bootstrapping)

a.Implicit Versus Explicit Dependencies

b.Aren’t Explicit Dependencies Totally Weird

and Java-y?

c.Preparing Handlers: Manual DI with Closures

and Partials

d.An Alternative Using Classes

e.A Bootstrap Script

f.Message Bus Is Given Handlers at Runtime

g.Using Bootstrap in Our Entrypoints

h.Initializing DI in Our Tests

i.Building an Adapter “Properly”: A Worked

Example

i.Define the Abstract and Concrete

Implementations

ii.Make a Fake Version for Your Tests

iii.Figure Out How to Integration Test the

Real Thing

j.Wrap-Up

18.Epilogue

a.What Now?

b.How Do I Get There from Here?

c.Separating Entangled Responsibilities

d.Identifying Aggregates and Bounded Contexts

e.An Event-Driven Approach to Go to

Microservices via Strangler Pattern

f.Convincing Your Stakeholders to Try

Something New

g.Questions Our Tech Reviewers Asked That We

Couldn’t Work into Prose

h.Footguns

i.More Required Reading

j.Wrap-Up

19.A. Summary Diagram and Table

20.B. A Template Project Structure

a.Env Vars, 12-Factor, and Config, Inside and

Outside Containers

b.Config.py

c.Docker-Compose and Containers Config

d.Installing Your Source as a Package

e.Dockerfile

f.Tests

g.Wrap-Up

21.C. Swapping Out the Infrastructure: Do Everything

with CSVs

a.Implementing a Repository and Unit of Work

for CSVs

22.D. Repository and Unit of Work Patterns with Django

a.Repository Pattern with Django

i.Custom Methods on Django ORM

Classes to Translate to/from Our

Domain Model

b.Unit of Work Pattern with Django

c.API: Django Views Are Adapters

d.Why Was This All So Hard?

e.What to Do If You Already Have Django

f.Steps Along the Way

23.E. Validation

a.What Is Validation, Anyway?

b.Validating Syntax

c.Postel’s Law and the Tolerant Reader Pattern

d.Validating at the Edge

e.Validating Semantics

f.Validating Pragmatics

24.Index

Architecture Patterns with

Python

Enabling Test-Driven Development, Domain-

Driven Design, and Event-Driven Microservices

Harry Percival and Bob Gregory

Architecture Patterns with Python

by Harry Percival and Bob Gregory

Copyright © 2020 Harry Percival and Bob Gregory. All rights

reserved.

Printed in the United States of America.

Published by O’Reilly Media, Inc., 1005 Gravenstein Highway North,

Sebastopol, CA 95472.

O’Reilly books may be purchased for educational, business, or sales

promotional use. Online editions are also available for most titles

(http://oreilly.com). For more information, contact our

corporate/institutional sales department: 800-998-9938 or

corporate@oreilly.com.

Acquisitions Editor: Ryan Shaw

Development Editor: Corbin Collins

Production Editor: Katherine Tozer

Copyeditor: Sharon Wilkey

Proofreader: Arthur Johnson

Indexer: Ellen Troutman-Zaig

Interior Designer: David Futato

Cover Designer: Karen Montgomery

Illustrator: Rebecca Demarest

March 2020: First Edition

Revision History for the First Edition

2020-03-05: First Release

Seehttp://oreilly.com/catalog/errata.csp?isbn=9781492052203for

release details.

The O’Reilly logo is a registered trademark of O’Reilly Media, Inc.

Architecture Patterns with Python , the cover image, and related trade

dress are trademarks of O’Reilly Media, Inc.

The views expressed in this work are those of the authors and do not

represent the publisher’s views. While the publisher and the authors

have used good faith efforts to ensure that the information and

instructions contained in this work are accurate, the publisher and the

authors disclaim all responsibility for errors or omissions, including

without limitation responsibility for damages resulting from the use of

or reliance on this work. Use of the information and instructions

contained in this work is at your own risk. If any code samples or other

technology this work contains or describes is subject to open source

licenses or the intellectual property rights of others, it is your

responsibility to ensure that your use thereof complies with such

licenses and/or rights.

978-1-492-05220-

\[LSI]

Preface

You may be wondering who we are and why we wrote this book.

At the end of Harry’s last book, Test-Driven Development with

Python (O’Reilly), he found himself asking a bunch of questions about

architecture, such as, What’s the best way of structuring your

application so that it’s easy to test? More specifically, so that your

core business logic is covered by unit tests, and so that you minimize

the number of integration and end-to-end tests you need? He made

vague references to “Hexagonal Architecture” and “Ports and

Adapters” and “Functional Core, Imperative Shell,” but if he was

honest, he’d have to admit that these weren’t things he really

understood or had done in practice.

And then he was lucky enough to run into Bob, who has the answers to

all these questions.

Bob ended up a software architect because nobody else on his team

was doing it. He turned out to be pretty bad at it, but he was lucky

enough to run into Ian Cooper, who taught him new ways of writing

and thinking about code.

Managing Complexity, Solving Business

Problems

We both work for MADE.com, a European ecommerce company that

sells furniture online; there, we apply the techniques in this book to

build distributed systems that model real-world business problems.

Our example domain is the first system Bob built for MADE, and this

book is an attempt to write down all the stuff we have to teach new

programmers when they join one of our teams.

MADE.com operates a global supply chain of freight partners and

manufacturers. To keep costs low, we try to optimize the delivery of

stock to our warehouses so that we don’t have unsold goods lying

around the place.

Ideally, the sofa that you want to buy will arrive in port on the very day

that you decide to buy it, and we’ll ship it straight to your house

without ever storing it. Getting the timing right is a tricky balancing act

when goods take three months to arrive by container ship. Along the

way, things get broken or water damaged, storms cause unexpected

delays, logistics partners mishandle goods, paperwork goes missing,

customers change their minds and amend their orders, and so on.

We solve those problems by building intelligent software representing

the kinds of operations taking place in the real world so that we can

automate as much of the business as possible.

Why Python?

If you’re reading this book, we probably don’t need to convince you

that Python is great, so the real question is “Why does the Python

community need a book like this?” The answer is about Python’s

popularity and maturity: although Python is probably the world’s

fastest-growing programming language and is nearing the top of the

absolute popularity tables, it’s only just starting to take on the kinds of

problems that the C# and Java world has been working on for years.

Startups become real businesses; web apps and scripted automations

are becoming (whisper it) enterprise software.

In the Python world, we often quote the Zen of Python: “There should

be one—and preferably only one—obvious way to do it.”

Unfortunately, as project size grows, the most obvious way of doing

things isn’t always the way that helps you manage complexity and

evolving requirements.

None of the techniques and patterns we discuss in this book are new,

but they are mostly new to the Python world. And this book isn’t a

replacement for the classics in the field such as Eric Evans’s Domain-

Driven Design or Martin Fowler’s Patterns of Enterprise

Application Architecture (both published by Addison-Wesley

Professional)—which we often refer to and encourage you to go and

read.

But all the classic code examples in the literature do tend to be written

in Java or C++/#, and if you’re a Python person and haven’t used

either of those languages in a long time (or indeed ever), those code

listings can be quite...trying. There’s a reason the latest edition of that

other classic text, Fowler’s Refactoring (Addison-Wesley

Professional), is in JavaScript.

1

TDD, DDD, and Event-Driven Architecture

In order of notoriety, we know of three tools for managing complexity:

1\. Test-driven development (TDD) helps us to build code that is

correct and enables us to refactor or add new features,

without fear of regression. But it can be hard to get the best

out of our tests: How do we make sure that they run as fast as

possible? That we get as much coverage and feedback from

fast, dependency-free unit tests and have the minimum number

of slower, flaky end-to-end tests?

2\. Domain-driven design (DDD) asks us to focus our efforts on

building a good model of the business domain, but how do we

make sure that our models aren’t encumbered with

infrastructure concerns and don’t become hard to change?

3\. Loosely coupled (micro)services integrated via messages

(sometimes called reactive microservices ) are a well-

established answer to managing complexity across multiple

applications or business domains. But it’s not always obvious

how to make them fit with the established tools of the Python

world—Flask, Django, Celery, and so on.

NOT E



Don’t be put off if you’re not working with (or interested in) microservices. The

vast majority of the patterns we discuss, including much of the event-driven

architecture material, is absolutely applicable in a monolithic architecture.



Our aim with this book is to introduce several classic architectural

patterns and show how they support TDD, DDD, and event-driven

services. We hope it will serve as a reference for implementing them

in a Pythonic way, and that people can use it as a first step toward

further research in this field.

Who Should Read This Book

Here are a few things we assume about you, dear reader:

You’ve been close to some reasonably complex Python

applications.

You’ve seen some of the pain that comes with trying to

manage that complexity.

You don’t necessarily know anything about DDD or any of the

classic application architecture patterns.

We structure our explorations of architectural patterns around an

example app, building it up chapter by chapter. We use TDD at work,

so we tend to show listings of tests first, followed by implementation.

If you’re not used to working test-first, it may feel a little strange at the

beginning, but we hope you’ll soon get used to seeing code “being

used” (i.e., from the outside) before you see how it’s built on the

inside.

We use some specific Python frameworks and technologies, including

Flask, SQLAlchemy, and pytest, as well as Docker and Redis. If

you’re already familiar with them, that won’t hurt, but we don’t think

it’s required. One of our main aims with this book is to build an

architecture for which specific technology choices become minor

implementation details.

A Brief Overview of What You’ll Learn

The book is divided into two parts; here’s a look at the topics we’ll

cover and the chapters they live in.

Part I, Building an Architecture to Support Domain

Modeling

Domain modeling and DDD (Chapters 1 and 7 )

At some level, everyone has learned the lesson that complex

business problems need to be reflected in code, in the form of a

model of the domain. But why does it always seem to be so hard to

do without getting tangled up with infrastructure concerns, our web

frameworks, or whatever else? In the first chapter we give a broad

overview of domain modeling and DDD, and we show how to get

started with a model that has no external dependencies, and fast

unit tests. Later we return to DDD patterns to discuss how to

choose the right aggregate, and how this choice relates to questions

of data integrity.

Repository, Service Layer, and Unit of Work patterns (Chapters 2 , 4 ,

and 5 )

In these three chapters we present three closely related and

mutually reinforcing patterns that support our ambition to keep the

model free of extraneous dependencies. We build a layer of

abstraction around persistent storage, and we build a service layer

to define the entrypoints to our system and capture the primary use

cases. We show how this layer makes it easy to build thin

entrypoints to our system, whether it’s a Flask API or a CLI.

Some thoughts on testing and abstractions (Chapters^3 and^6 )

After presenting the first abstraction (the Repository pattern), we

take the opportunity for a general discussion of how to choose

abstractions, and what their role is in choosing how our software

is coupled together. After we introduce the Service Layer pattern,

we talk a bit about achieving a test pyramid and writing unit tests

at the highest possible level of abstraction.

Part II, Event-Driven Architecture

Event-driven architecture (Chapters 8 – 11 )

We introduce three more mutually reinforcing patterns: the Domain

Events, Message Bus, and Handler patterns. Domain events are a

vehicle for capturing the idea that some interactions with a system

are triggers for others. We use a message bus to allow actions to

trigger events and call appropriate handlers. We move on to

discuss how events can be used as a pattern for integration

between services in a microservices architecture. Finally, we

distinguish between commands and events. Our application is now

fundamentally a message-processing system.

Command-query responsibility segregation (Chapter 12)

We present an example of command-query responsibility

segregation , with and without events.

Dependency injection (Chapter 13)

We tidy up our explicit and implicit dependencies and implement a

simple dependency injection framework.

Addtional Content

How do I get there from here? (Epilogue)

Implementing architectural patterns always looks easy when you

show a simple example, starting from scratch, but many of you will

probably be wondering how to apply these principles to existing

software. We’ll provide a few pointers in the epilogue and some

links to further reading.

Example Code and Coding Along

You’re reading a book, but you’ll probably agree with us when we say

that the best way to learn about code is to code. We learned most of

what we know from pairing with people, writing code with them, and

learning by doing, and we’d like to re-create that experience as much

as possible for you in this book.

As a result, we’ve structured the book around a single example project

(although we do sometimes throw in other examples). We’ll build up

this project as the chapters progress, as if you’ve paired with us and

we’re explaining what we’re doing and why at each step.

But to really get to grips with these patterns, you need to mess about

with the code and get a feel for how it works. You’ll find all the code

on GitHub; each chapter has its own branch. You can finda listof the

branches on GitHub as well.

Here are three ways you might code along with the book:

Start your own repo and try to build up the app as we do,

following the examples from listings in the book, and

occasionally looking to our repo for hints. A word of

warning, however: if you’ve read Harry’s previous book and

coded along with that, you’ll find that this book requires you

to figure out more on your own; you may need to lean pretty

heavily on the working versions on GitHub.

Try to apply each pattern, chapter by chapter, to your own

(preferably small/toy) project, and see if you can make it

work for your use case. This is high risk/high reward (and

high effort besides!). It may take quite some work to get things

working for the specifics of your project, but on the other

hand, you’re likely to learn the most.

For less effort, in each chapter we outline an “Exercise for

the Reader,” and point you to a GitHub location where you

can download some partially finished code for the chapter

with a few missing parts to write yourself.

Particularly if you’re intending to apply some of these patterns in your

own projects, working through a simple example is a great way to

safely practice.

T IP



At the very least, do a git checkout of the code from our repo as you read each

chapter. Being able to jump in and see the code in the context of an actual

working app will help answer a lot of questions as you go, and makes everything

more real. You’ll find instructions for how to do that at the beginning of each

chapter.



License

The code (and the online version of the book) is licensed under a

Creative Commons CC BY-NC-ND license, which means you are free

to copy and share it with anyone you like, for non-commercial

purposes, as long as you give attribution. If you want to re-use any of

the content from this book and you have any worries about the license,

contact O’Reilly at permissions@oreilly.com.

The print edition is licensed differently; please see the copyright page.

Conventions Used in This Book

The following typographical conventions are used in this book:

Italic

Indicates new terms, URLs, email addresses, filenames, and file

extensions.

Constant width

Used for program listings, as well as within paragraphs to refer to

program elements such as variable or function names, databases,

data types, environment variables, statements, and keywords.

Constant width bold

Shows commands or other text that should be typed literally by the

user.

Constant width italic

Shows text that should be replaced with user-supplied values or by

values determined by context.

T IP



This element signifies a tip or suggestion.



NOT E



This element signifies a general note.



WARNING



This element indicates a warning or caution.



O’Reilly Online Learning

NOT E



For more than 40 years, O’Reilly Media has provided technology and business

training, knowledge, and insight to help companies succeed.



Our unique network of experts and innovators share their knowledge

and expertise through books, articles, conferences, and our online

learning platform. O’Reilly’s online learning platform gives you on-

demand access to live training courses, in-depth learning paths,

interactive coding environments, and a vast collection of text and

video from O’Reilly and 200+ other publishers. For more information,

please visit http://oreilly.com.

How to Contact O’Reilly

Please address comments and questions concerning this book to the

publisher:

O’Reilly Media, Inc.

1005 Gravenstein Highway North

Sebastopol, CA 95472

800-998-9938 (in the United States or Canada)

707-829-0515 (international or local)

707-829-0104 (fax)

We have a web page for this book, where we list errata, examples, and

any additional information. You can access this page at

https://oreil.ly/architecture-patterns-python.

Email bookquestions@oreilly.com to comment or ask technical

questions about this book.

For more information about our books, courses, conferences, and

news, see our website at http://www.oreilly.com.

Find us on Facebook: http://facebook.com/oreilly

Follow us on Twitter: http://twitter.com/oreillymedia

Watch us on YouTube: http://www.youtube.com/oreillymedia

Acknowledgments

To our tech reviewers, David Seddon, Ed Jung, and Hynek Schlawack:

we absolutely do not deserve you. You are all incredibly dedicated,

conscientious, and rigorous. Each one of you is immensely smart, and

your different points of view were both useful and complementary to

each other. Thank you from the bottom of our hearts.

Gigantic thanks also to our Early Release readers for their comments

and suggestions: Ian Cooper, Abdullah Ariff, Jonathan Meier, Gil

Gonçalves, Matthieu Choplin, Ben Judson, James Gregory,Łukasz

Lechowicz, Clinton Roy, Vitorino Araújo, Susan Goodbody, Josh

Harwood, Daniel Butler, Liu Haibin, Jimmy Davies, Ignacio Vergara

Kausel, Gaia Canestrani, Renne Rocha, pedroabi, Ashia Zawaduk,

Jostein Leira, Brandon Rhodes, and many more; our apologies if we

missed you on this list.

Super-mega-thanks to our editor Corbin Collins for his gentle

chivvying, and for being a tireless advocate of the reader. Similarly-

superlative thanks to the production staff, Katherine Tozer, Sharon

Wilkey, Ellen Troutman-Zaig, and Rebecca Demarest, for your

dedication, professionalism, and attention to detail. This book is

immeasurably improved thanks to you.

Any errors remaining in the book are our own, naturally.



1 python -c "import this"



Introduction

Why Do Our Designs Go Wrong?

What comes to mind when you hear the word chaos? Perhaps you think

of a noisy stock exchange, or your kitchen in the morning—everything

confused and jumbled. When you think of the word order , perhaps you

think of an empty room, serene and calm. For scientists, though, chaos

is characterized by homogeneity (sameness), and order by complexity

(difference).

For example, a well-tended garden is a highly ordered system.

Gardeners define boundaries with paths and fences, and they mark out

flower beds or vegetable patches. Over time, the garden evolves,

growing richer and thicker; but without deliberate effort, the garden

will run wild. Weeds and grasses will choke out other plants, covering

over the paths, until eventually every part looks the same again—wild

and unmanaged.

Software systems, too, tend toward chaos. When we first start building

a new system, we have grand ideas that our code will be clean and

well ordered, but over time we find that it gathers cruft and edge cases

and ends up a confusing morass of manager classes and util modules.

We find that our sensibly layered architecture has collapsed into itself

like an oversoggy trifle. Chaotic software systems are characterized by

a sameness of function: API handlers that have domain knowledge and

send email and perform logging; “business logic” classes that perform

no calculations but do perform I/O; and everything coupled to

everything else so that changing any part of the system becomes fraught

with danger. This is so common that software engineers have their own

term for chaos: the Big Ball of Mud anti-pattern (Figure P-1).



Figure P-1. A real-life dependency diagram (source:“Enterprise Dependency: Big Ball

of Yarn”by Alex Papadimoulis)



T IP



A big ball of mud is the natural state of software in the same way that wilderness

is the natural state of your garden. It takes energy and direction to prevent the

collapse.



Fortunately, the techniques to avoid creating a big ball of mud aren’t

complex.

Encapsulation and Abstractions

Encapsulation and abstraction are tools that we all instinctively reach

for as programmers, even if we don’t all use these exact words. Allow

us to dwell on them for a moment, since they are a recurring

background theme of the book.

The term encapsulation covers two closely related ideas: simplifying

behavior and hiding data. In this discussion, we’re using the first

sense. We encapsulate behavior by identifying a task that needs to be

done in our code and giving that task to a well-defined object or

function. We call that object or function an abstraction.

Take a look at the following two snippets of Python code:

Do a search with urllib



importjson

fromurllib.requestimport urlopen

fromurllib.parseimport urlencode



params=dict(q='Sausages',format='json')



handle=urlopen('http://api.duckduckgo.com'+'?'+urlencode(params))

raw\_text=handle.read().decode('utf8')

parsed=json.loads(raw\_text)



results=parsed\['RelatedTopics']

for r in results:

if 'Text' in r:

print (r\['FirstURL']+' - '+r\['Text'])

Do a search with requests



importrequests



params=dict(q='Sausages',format='json')

parsed=requests.get('http://api.duckduckgo.com/',params=params).json()



results=parsed\['RelatedTopics']

for r in results:

if 'Text' in r:

print (r\['FirstURL']+' - '+r\['Text'])

Both code listings do the same thing: they submit form-encoded values

to a URL in order to use a search engine API. But the second is

simpler to read and understand because it operates at a higher level of

abstraction.

We can take this one step further still by identifying and naming the

task we want the code to perform for us and using an even higher-level

abstraction to make it explicit:

Do a search with the duckduckgo module



importduckduckgo

for r in duckduckgo.query('Sausages').results:

print (r.url+' - '+r.text)

Encapsulating behavior by using abstractions is a powerful tool for

making code more expressive, more testable, and easier to maintain.

NOT E



In the literature of the object-oriented (OO) world, one of the classic

characterizations of this approach is called responsibility-driven design ; it uses

the words roles and responsibilities rather than tasks. The main point is to think

about code in terms of behavior, rather than in terms of data or algorithms.



ABSTRACTIONS AND ABCS



In a traditional OO language like Java or C#, you might use an abstract base class (ABC) or an

interface to define an abstraction. In Python you can (and we sometimes do) use ABCs, but you

can also happily rely on duck typing.

The abstraction can just mean “the public API of the thing you’re using”—a function name plus

some arguments, for example.



Most of the patterns in this book involve choosing an abstraction, so

you’ll see plenty of examples in each chapter. In addition,Chapter 3

specifically discusses some general heuristics for choosing

abstractions.

Layering

Encapsulation and abstraction help us by hiding details and protecting

the consistency of our data, but we also need to pay attention to the

interactions between our objects and functions. When one function,

module, or object uses another, we say that the one depends on the

other. These dependencies form a kind of network or graph.



1



In a big ball of mud, the dependencies are out of control (as you saw in

Figure P-1). Changing one node of the graph becomes difficult because

it has the potential to affect many other parts of the system. Layered

architectures are one way of tackling this problem. In a layered

architecture, we divide our code into discrete categories or roles, and

we introduce rules about which categories of code can call each other.

One of the most common examples is the three-layered architecture

shown inFigure P-2.



Figure P-2. Layered architecture



Layered architecture is perhaps the most common pattern for building

business software. In this model we have user-interface components,

which could be a web page, an API, or a command line; these user-

interface components communicate with a business logic layer that

contains our business rules and our workflows; and finally, we have a

database layer that’s responsible for storing and retrieving data.

For the rest of this book, we’re going to be systematically turning this

model inside out by obeying one simple principle.

The Dependency Inversion Principle

You might be familiar with the dependency inversion principle (DIP)

already, because it’s the D in SOLID.

Unfortunately, we can’t illustrate the DIP by using three tiny code

listings as we did for encapsulation. However, the whole ofPart Iis

essentially a worked example of implementing the DIP throughout an

application, so you’ll get your fill of concrete examples.

In the meantime, we can talk about DIP’s formal definition:

1\. High-level modules should not depend on low-level modules.

Both should depend on abstractions.

2\. Abstractions should not depend on details. Instead, details

should depend on abstractions.

But what does this mean? Let’s take it bit by bit.

High-level modules are the code that your organization really cares

about. Perhaps you work for a pharmaceutical company, and your high-

level modules deal with patients and trials. Perhaps you work for a

2

bank, and your high-level modules manage trades and exchanges. The

high-level modules of a software system are the functions, classes, and

packages that deal with our real-world concepts.

By contrast, low-level modules are the code that your organization

doesn’t care about. It’s unlikely that your HR department gets excited

about filesystems or network sockets. It’s not often that you discuss

SMTP, HTTP, or AMQP with your finance team. For our nontechnical

stakeholders, these low-level concepts aren’t interesting or relevant.

All they care about is whether the high-level concepts work correctly.

If payroll runs on time, your business is unlikely to care whether that’s

a cron job or a transient function running on Kubernetes.

Depends on doesn’t mean imports or calls , necessarily, but rather a

more general idea that one module knows about or needs another

module.

And we’ve mentioned abstractions already: they’re simplified

interfaces that encapsulate behavior, in the way that our duckduckgo

module encapsulated a search engine’s API.

All problems in computer science can be solved by adding another

level of indirection.

—David Wheeler

So the first part of the DIP says that our business code shouldn’t

depend on technical details; instead, both should use abstractions.

Why? Broadly, because we want to be able to change them

independently of each other. High-level modules should be easy to

change in response to business needs. Low-level modules (details) are

often, in practice, harder to change: think about refactoring to change a

function name versus defining, testing, and deploying a database

migration to change a column name. We don’t want business logic

changes to slow down because they are closely coupled to low-level

infrastructure details. But, similarly, it is important to be able to

change your infrastructure details when you need to (think about

sharding a database, for example), without needing to make changes to

your business layer. Adding an abstraction between them (the famous

extra layer of indirection) allows the two to change (more)

independently of each other.

The second part is even more mysterious. “Abstractions should not

depend on details” seems clear enough, but “Details should depend on

abstractions” is hard to imagine. How can we have an abstraction that

doesn’t depend on the details it’s abstracting? By the time we get to

Chapter 4, we’ll have a concrete example that should make this all a

bit clearer.

A Place for All Our Business Logic: The

Domain Model

But before we can turn our three-layered architecture inside out, we

need to talk more about that middle layer: the high-level modules or

business logic. One of the most common reasons that our designs go

wrong is that business logic becomes spread throughout the layers of

our application, making it hard to identify, understand, and change.

Chapter 1shows how to build a business layer with a Domain Model

pattern. The rest of the patterns inPart Ishow how we can keep the

domain model easy to change and free of low-level concerns by

choosing the right abstractions and continuously applying the DIP.



1 If you’ve come across class-responsibility-collaborator (CRC) cards, they’re driving at

the same thing: thinking about responsibilities helps you decide how to split things up.



2 SOLID is an acronym for Robert C. Martin’s five principles of object-oriented design:

single responsibility, open for extension but closed for modification, Liskov substitution,

interface segregation, and dependency inversion. See“S.O.L.I.D: The First 5 Principles

of Object-Oriented Design”by Samuel Oloruntoba.



Part I. Building an

Architecture to Support

Domain Modeling

Most developers have never seen a domain model, only a data

model.

—Cyrille Martraire, DDD EU 2017

Most developers we talk to about architecture have a nagging sense

that things could be better. They are often trying to rescue a system that

has gone wrong somehow, and are trying to put some structure back

into a ball of mud. They know that their business logic shouldn’t be

spread all over the place, but they have no idea how to fix it.

We’ve found that many developers, when asked to design a new

system, will immediately start to build a database schema, with the

object model treated as an afterthought. This is where it all starts to go

wrong. Instead, behavior should come first and drive our storage

requirements. After all, our customers don’t care about the data model.

They care about what the system does ; otherwise they’d just use a

spreadsheet.

The first part of the book looks at how to build a rich object model

through TDD (inChapter 1), and then we’ll show how to keep that

model decoupled from technical concerns. We show how to build

persistence-ignorant code and how to create stable APIs around our

domain so that we can refactor aggressively.

To do that, we present four key design patterns:

TheRepository pattern, an abstraction over the idea of

persistent storage

TheService Layerpattern to clearly define where our use

cases begin and end

TheUnit of Work patternto provide atomic operations

TheAggregate patternto enforce the integrity of our data

If you’d like a picture of where we’re going, take a look atFigure I-1,

but don’t worry if none of it makes sense yet! We introduce each box in

the figure, one by one, throughout this part of the book.



Figure I-1. A component diagram for our app at the end ofPart I



We also take a little time out to talk aboutcoupling and abstractions,

illustrating it with a simple example that shows how and why we

choose our abstractions.

Three appendices are further explorations of the content from Part I:

Appendix Bis a write-up of the infrastructure for our example

code: how we build and run the Docker images, where we

manage configuration info, and how we run different types of

tests.

Appendix Cis a “proof is in the pudding” kind of content,

showing how easy it is to swap out our entire infrastructure—

the Flask API, the ORM, and Postgres—for a totally different

I/O model involving a CLI and CSVs.

Finally,Appendix Dmay be of interest if you’re wondering

how these patterns might look if using Django instead of Flask

and SQLAlchemy.

Chapter 1. Domain Modeling

This chapter looks into how we can model business processes with

code, in a way that’s highly compatible with TDD. We’ll discuss why

domain modeling matters, and we’ll look at a few key patterns for

modeling domains: Entity, Value Object, and Domain Service.

Figure 1-1is a simple visual placeholder for our Domain Model

pattern. We’ll fill in some details in this chapter, and as we move on to

other chapters, we’ll build things around the domain model, but you

should always be able to find these little shapes at the core.



Figure 1-1. A placeholder illustration of our domain model



What Is a Domain Model?

In theintroduction, we used the term business logic layer to describe

the central layer of a three-layered architecture. For the rest of the

book, we’re going to use the term domain model instead. This is a

term from the DDD community that does a better job of capturing our

intended meaning (see the next sidebar for more on DDD).

The domain is a fancy way of saying the problem you’re trying to

solve. Your authors currently work for an online retailer of furniture.

Depending on which system you’re talking about, the domain might be

purchasing and procurement, or product design, or logistics and

delivery. Most programmers spend their days trying to improve or

automate business processes; the domain is the set of activities that

those processes support.

A model is a map of a process or phenomenon that captures a useful

property. Humans are exceptionally good at producing models of

things in their heads. For example, when someone throws a ball

toward you, you’re able to predict its movement almost unconsciously,

because you have a model of the way objects move in space. Your

model isn’t perfect by any means. Humans have terrible intuitions

about how objects behave at near-light speeds or in a vacuum because

our model was never designed to cover those cases. That doesn’t mean

the model is wrong, but it does mean that some predictions fall outside

of its domain.

The domain model is the mental map that business owners have of

their businesses. All business people have these mental maps—they’re

how humans think about complex processes.

You can tell when they’re navigating these maps because they use

business speak. Jargon arises naturally among people who are

collaborating on complex systems.

Imagine that you, our unfortunate reader, were suddenly transported

light years away from Earth aboard an alien spaceship with your

friends and family and had to figure out, from first principles, how to

navigate home.

In your first few days, you might just push buttons randomly, but soon

you’d learn which buttons did what, so that you could give one another

instructions. “Press the red button near the flashing doohickey and then

throw that big lever over by the radar gizmo,” you might say.

Within a couple of weeks, you’d become more precise as you adopted

words to describe the ship’s functions: “Increase oxygen levels in

cargo bay three” or “turn on the little thrusters.” After a few months,

you’d have adopted language for entire complex processes: “Start

landing sequence” or “prepare for warp.” This process would happen

quite naturally, without any formal effort to build a shared glossary.

THIS IS NOT A DDD BOOK. YOU SHOULD READ A DDD BOOK.



Domain-driven design, or DDD, popularized the concept of domain modeling, and it’s been a

hugely successful movement in transforming the way people design software by focusing on the

core business domain. Many of the architecture patterns that we cover in this book—including

Entity, Aggregate, Value Object (seeChapter 7), and Repository (inthe next chapter)—come from

the DDD tradition.

In a nutshell, DDD says that the most important thing about software is that it provides a useful

model of a problem. If we get that model right, our software delivers value and makes new things

possible.

If we get the model wrong, it becomes an obstacle to be worked around. In this book, we can

show the basics of building a domain model, and building an architecture around it that leaves

the model as free as possible from external constraints, so that it’s easy to evolve and change.

But there’s a lot more to DDD and to the processes, tools, and techniques for developing a

domain model. We hope to give you a taste of it, though, and cannot encourage you enough to go

on and read a proper DDD book:

The original “blue book,” Dom ain-Driven Design by Eric Evans (Addison-Wesley

Professional)

The “red book,” Im plem enting Dom ain-Driven Design by Vaughn Vernon (Addison-

Wesley Professional)



So it is in the mundane world of business. The terminology used by

business stakeholders represents a distilled understanding of the

domain model, where complex ideas and processes are boiled down

to a single word or phrase.

When we hear our business stakeholders using unfamiliar words, or

using terms in a specific way, we should listen to understand the

deeper meaning and encode their hard-won experience into our

software.

We’re going to use a real-world domain model throughout this book,

specifically a model from our current employment. MADE.com is a



1



successful furniture retailer. We source our furniture from

manufacturers all over the world and sell it across Europe.

When you buy a sofa or a coffee table, we have to figure out how best

to get your goods from Poland or China or Vietnam and into your living

room.

At a high level, we have separate systems that are responsible for

buying stock, selling stock to customers, and shipping goods to

customers. A system in the middle needs to coordinate the process by

allocating stock to a customer’s orders; seeFigure 1-2.



Figure 1-2. Context diagram for the allocation service



For the purposes of this book, we’re imagining that the business

decides to implement an exciting new way of allocating stock. Until

now, the business has been presenting stock and lead times based on

what is physically available in the warehouse. If and when the

warehouse runs out, a product is listed as “out of stock” until the next

shipment arrives from the manufacturer.

Here’s the innovation: if we have a system that can keep track of all

our shipments and when they’re due to arrive, we can treat the goods

on those ships as real stock and part of our inventory, just with slightly

longer lead times. Fewer goods will appear to be out of stock, we’ll

sell more, and the business can save money by keeping lower

inventory in the domestic warehouse.

But allocating orders is no longer a trivial matter of decrementing a

single quantity in the warehouse system. We need a more complex

allocation mechanism. Time for some domain modeling.

Exploring the Domain Language

Understanding the domain model takes time, and patience, and Post-it

notes. We have an initial conversation with our business experts and

agree on a glossary and some rules for the first minimal version of the

domain model. Wherever possible, we ask for concrete examples to

illustrate each rule.

We make sure to express those rules in the business jargon (the

ubiquitous language in DDD terminology). We choose memorable

identifiers for our objects so that the examples are easier to talk about.

“Some Notes on Allocation”shows some notes we might have taken

while having a conversation with our domain experts about allocation.



SOME NOTES ON ALLOCATION

A product is identified by a SKU , pronounced “skew,” which is short for stock -k eeping unit.

Custom ers place orders. An order is identified by an order reference and comprises multiple

order lines , where each line has a SKU and a quantity. For example:

10 units of RED-CHAIR

1 unit of TASTELESS-LAMP

The purchasing department orders small b atches of stock. A b atch of stock has a unique ID

called a reference , a SKU , and a quantity.

We need to allocate order lines to b atches. When we’ve allocated an order line to a batch, we will

send stock from that specific batch to the customer’s delivery address. When we allocate x units

of stock to a batch, the availab le quantity is reduced by x. For example:

We have a batch of 20 SMALL-TABLE, and we allocate an order line for 2 SMALL-TABLE.

The batch should have 18 SMALL-TABLE remaining.

We can’t allocate to a batch if the available quantity is less than the quantity of the order line. For

example:

We have a batch of 1 BLUE-CUSHION, and an order line for 2 BLUE-CUSHION.

We should not be able to allocate the line to the batch.

We can’t allocate the same line twice. For example:

We have a batch of 10 BLUE-VASE, and we allocate an order line for 2 BLUE-VASE.

If we allocate the order line again to the same batch, the batch should still have an

available quantity of 8.

Batches have an ETA if they are currently shipping, or they may be in warehouse stock. We

allocate to warehouse stock in preference to shipment batches. We allocate to shipment batches

in order of which has the earliest ETA.



Unit Testing Domain Models

We’re not going to show you how TDD works in this book, but we

want to show you how we would construct a model from this business

conversation.

EXERCISE FOR THE READER



Why not have a go at solving this problem yourself? Write a few unit tests to see if you can

capture the essence of these business rules in nice, clean code.

You’ll find someplaceholder unit tests on GitHub, but you could just start from scratch, or

combine/rewrite them however you like.



Here’s what one of our first tests might look like:

A first test for allocation (test\_batches.py)



def test\_allocating\_to\_a\_batch\_reduces\_the\_available\_quantity():

batch=Batch("batch-001","SMALL-TABLE",qty= 20 ,eta=date.today())

line=OrderLine('order-ref',"SMALL-TABLE", 2 )



batch.allocate(line)



assert batch.available\_quantity== 18



The name of our unit test describes the behavior that we want to see

from the system, and the names of the classes and variables that we use

are taken from the business jargon. We could show this code to our

nontechnical coworkers, and they would agree that this correctly

describes the behavior of the system.

And here is a domain model that meets our requirements:

First cut of a domain model for batches (model.py)



@dataclass(frozen=True)

classOrderLine :

orderid:str

sku:str

qty:int



classBatch :

def init(

self,ref:str,sku:str,qty:int,eta:Optional\[date]

):

self.reference=ref

self.sku=sku

self.eta=eta

self.available\_quantity=qty



def allocate(self,line:OrderLine):

self.available\_quantity-=line.qty



OrderLine is an immutable dataclass with no behavior.

We’re not showing imports in most code listings, in an attempt to

keep them clean. We’re hoping you can guess that this came via

from dataclasses import dataclass; likewise,

typing.Optional and datetime.date. If you want to double-

check anything, you can see the full working code for each chapter

in its branch (e.g.,chapter\_01\_domain\_model).

Type hints are still a matter of controversy in the Python world.

For domain models, they can sometimes help to clarify or

document what the expected arguments are, and people with IDEs

are often grateful for them. You may decide the price paid in terms

of readability is too high.

Our implementation here is trivial: a Batch just wraps an integer

available\_quantity, and we decrement that value on allocation.

2

We’ve written quite a lot of code just to subtract one number from

another, but we think that modeling our domain precisely will pay off.

Let’s write some new failing tests:

Testing logic for what we can allocate (test\_batches.py)



def make\_batch\_and\_line(sku,batch\_qty,line\_qty):

return (

Batch("batch-001",sku,batch\_qty,eta=date.today()),

OrderLine("order-123",sku,line\_qty)

)



def test\_can\_allocate\_if\_available\_greater\_than\_required():

large\_batch,small\_line=make\_batch\_and\_line("ELEGANT-LAMP", 20 , 2 )

assert large\_batch.can\_allocate(small\_line)



def test\_cannot\_allocate\_if\_available\_smaller\_than\_required():

small\_batch,large\_line=make\_batch\_and\_line("ELEGANT-LAMP", 2 , 20 )

assert small\_batch.can\_allocate(large\_line) is False



def test\_can\_allocate\_if\_available\_equal\_to\_required():

batch,line =make\_batch\_and\_line("ELEGANT-LAMP", 2 , 2 )

assert batch.can\_allocate(line)



def test\_cannot\_allocate\_if\_skus\_do\_not\_match():

batch=Batch("batch-001","UNCOMFORTABLE-CHAIR", 100 ,eta=None)

different\_sku\_line=OrderLine("order-123","EXPENSIVE-TOASTER", 10 )

assert batch.can\_allocate(different\_sku\_line) is False

There’s nothing too unexpected here. We’ve refactored our test suite so

that we don’t keep repeating the same lines of code to create a batch

and a line for the same SKU; and we’ve written four simple tests for a

new method can\_allocate. Again, notice that the names we use

3

mirror the language of our domain experts, and the examples we

agreed upon are directly written into code.

We can implement this straightforwardly, too, by writing the

can\_allocate method of Batch:

A new method in the model (model.py)



def can\_allocate(self,line:OrderLine)->bool:

return self.sku==line.sku and self.available\_quantity>=line.qty



So far, we can manage the implementation by just incrementing and

decrementing Batch.available\_quantity, but as we get into

deallocate() tests, we’ll be forced into a more intelligent solution:

This test is going to require a smarter model (test\_batches.py)



def test\_can\_only\_deallocate\_allocated\_lines():

batch,unallocated\_line =make\_batch\_and\_line("DECORATIVE-TRINKET", 20 , 2 )

batch.deallocate(unallocated\_line)

assert batch.available\_quantity== 20

In this test, we’re asserting that deallocating a line from a batch has no

effect unless the batch previously allocated the line. For this to work,

our Batch needs to understand which lines have been allocated. Let’s

look at the implementation:

The domain model now tracks allocations (model.py)



classBatch :

def init(

self,ref:str,sku:str,qty:int,eta:Optional\[date]

):

self.reference=ref



self.sku=sku

self.eta=eta

self.\_purchased\_quantity=qty

self.\_allocations=set() # type: Set\[OrderLine]



def allocate(self,line:OrderLine):

if self.can\_allocate(line):

self.\_allocations.add(line)



def deallocate(self,line:OrderLine):

if line in self.\_allocations:

self.\_allocations.remove(line)



@property

def allocated\_quantity(self)->int:

return sum(line.qty for line in self.\_allocations)



@property

def available\_quantity(self)->int:

return self.\_purchased\_quantity-self.allocated\_quantity



def can\_allocate(self,line:OrderLine)->bool:

return self.sku==line.sku and self.available\_quantity>=line.qty



Figure 1-3shows the model in UML.



Figure 1-3. Our model in UML



Now we’re getting somewhere! A batch now keeps track of a set of

allocated OrderLine objects. When we allocate, if we have enough

available quantity, we just add to the set. Our available\_quantity is

now a calculated property: purchased quantity minus allocated

quantity.

Yes, there’s plenty more we could do. It’s a little disconcerting that

both allocate() and deallocate() can fail silently, but we have the

basics.

Incidentally, using a set for .\_allocations makes it simple for us to

handle the last test, because items in a set are unique:

Last batch test! (test\_batches.py)



def test\_allocation\_is\_idempotent():

batch,line =make\_batch\_and\_line("ANGULAR-DESK", 20 , 2 )

batch.allocate(line)

batch.allocate(line)

assert batch.available\_quantity== 18

At the moment, it’s probably a valid criticism to say that the domain

model is too trivial to bother with DDD (or even object orientation!).

In real life, any number of business rules and edge cases crop up:

customers can ask for delivery on specific future dates, which means

we might not want to allocate them to the earliest batch. Some SKUs

aren’t in batches, but ordered on demand directly from suppliers, so

they have different logic. Depending on the customer’s location, we

can allocate to only a subset of warehouses and shipments that are in

their region—except for some SKUs we’re happy to deliver from a

warehouse in a different region if we’re out of stock in the home

region. And so on. A real business in the real world knows how to pile

on complexity faster than we can show on the page!

But taking this simple domain model as a placeholder for something

more complex, we’re going to extend our simple domain model in the

rest of the book and plug it into the real world of APIs and databases

and spreadsheets. We’ll see how sticking rigidly to our principles of

encapsulation and careful layering will help us to avoid a ball of mud.

MORE TYPES FOR MORE TYPE HINTS



If you really want to go to town with type hints, you could go so far as wrapping primitive types by

using typing.NewType:

Just tak ing it way too far, Bob

fromdataclassesimport dataclass

fromtypingimport NewType

Quantity=NewType("Quantity",int)

Sku=NewType("Sku",str)

Reference=NewType("Reference",str)

...

classBatch :

def \_\_init\_\_(self,ref:Reference,sku:Sku,qty:Quantity):

self.sku=sku

self.reference=ref

self.\_purchased\_quantity=qty

That would allow our type checker to make sure that we don’t pass a Sku where a Reference is

expected, for example.

Whether you think this is wonderful or appalling is a matter of debate.



Dataclasses Are Great for Value Objects

We’ve used line liberally in the previous code listings, but what is a

line? In our business language, an order has multiple line items, where

each line has a SKU and a quantity. We can imagine that a simple

YAML file containing order information might look like this:

Order info as YAML



4



Order\_reference : 12345

Lines :



&#x20;   sku :RED-CHAIR

&#x20;   qty : 25

&#x20;   sku :BLU-CHAIR

&#x20;   qty : 25

&#x20;   sku :GRN-CHAIR

&#x20;   qty : 25



Notice that while an order has a reference that uniquely identifies it, a

line does not. (Even if we add the order reference to the OrderLine

class, it’s not something that uniquely identifies the line itself.)

Whenever we have a business concept that has data but no identity, we

often choose to represent it using the Value Object pattern. A value

object is any domain object that is uniquely identified by the data it

holds; we usually make them immutable:

OrderLine is a value object



@dataclass(frozen=True)

classOrderLine :

orderid:OrderReference

sku:ProductReference

qty:Quantity

One of the nice things that dataclasses (or namedtuples) give us is

value equality , which is the fancy way of saying, “Two lines with the

same orderid, sku, and qty are equal.”

More examples of value objects



fromdataclassesimport dataclass

fromtypingimport NamedTuple

fromcollectionsimport namedtuple



@dataclass(frozen=True)

className :

first\_name:str

surname:str



classMoney (NamedTuple):

currency:str

value:int



Line=namedtuple('Line', \['sku','qty'])



def test\_equality():

assert Money('gbp', 10 )==Money('gbp', 10 )

assert Name('Harry','Percival')!=Name('Bob','Gregory')

assert Line('RED-CHAIR', 5 )==Line('RED-CHAIR', 5 )

These value objects match our real-world intuition about how their

values work. It doesn’t matter which £10 note we’re talking about,

because they all have the same value. Likewise, two names are equal

if both the first and last names match; and two lines are equivalent if

they have the same customer order, product code, and quantity. We can

still have complex behavior on a value object, though. In fact, it’s

common to support operations on values; for example, mathematical

operators:

Math with value objects



fiver=Money('gbp', 5 )

tenner=Money('gbp', 10 )



def can\_add\_money\_values\_for\_the\_same\_currency():

assert fiver+fiver==tenner



def can\_subtract\_money\_values():

assert tenner-fiver==fiver



def adding\_different\_currencies\_fails():

with pytest.raises( ValueError ):

Money('usd', 10 )+Money('gbp', 10 )



def can\_multiply\_money\_by\_a\_number():

assert fiver\* 5 ==Money('gbp', 25 )



def multiplying\_two\_money\_values\_is\_an\_error():

with pytest.raises( TypeError ):

tenner\*fiver

Value Objects and Entities

An order line is uniquely identified by its order ID, SKU, and quantity;

if we change one of those values, we now have a new line. That’s the

definition of a value object: any object that is identified only by its

data and doesn’t have a long-lived identity. What about a batch,

though? That is identified by a reference.

We use the term entity to describe a domain object that has long-lived

identity. On the previous page, we introduced a Name class as a value

object. If we take the name Harry Percival and change one letter, we

have the new Name object Barry Percival.

It should be clear that Harry Percival is not equal to Barry Percival:

A name itself cannot change...



def test\_name\_equality():

assert Name("Harry","Percival")!=Name("Barry","Percival")

But what about Harry as a person? People do change their names, and

their marital status, and even their gender, but we continue to recognize

them as the same individual. That’s because humans, unlike names,

have a persistent identity :

But a person can!



classPerson :



def \_\_init\_\_(self,name:Name):

self.name=name



def test\_barry\_is\_harry():

harry=Person(Name("Harry","Percival"))

barry=harry



barry.name=Name("Barry","Percival")



assert harry is barry and barry is harry



Entities, unlike values, have identity equality. We can change their

values, and they are still recognizably the same thing. Batches, in our

example, are entities. We can allocate lines to a batch, or change the

date that we expect it to arrive, and it will still be the same entity.

We usually make this explicit in code by implementing equality

operators on entities:

Implementing equality operators (model.py)



classBatch :

...



def \_\_eq\_\_(self,other):

ifnot isinstance(other,Batch):

return False

return other.reference==self.reference



def \_\_hash\_\_(self):

return hash(self.reference)



Python’s eq magic method defines the behavior of the class for

the == operator.

For both entity and value objects, it’s also worth thinking through how

hash will work. It’s the magic method Python uses to control the

behavior of objects when you add them to sets or use them as dict

keys; you can find more infoin the Python docs.

For value objects, the hash should be based on all the value attributes,

and we should ensure that the objects are immutable. We get this for

free by specifying @frozen=True on the dataclass.

For entities, the simplest option is to say that the hash is None, meaning

that the object is not hashable and cannot, for example, be used in a

set. If for some reason you decide you really do want to use set or dict

operations with entities, the hash should be based on the attribute(s),

such as .reference, that defines the entity’s unique identity over time.

You should also try to somehow make that attribute read-only.

WARNING



This is tricky territory; you shouldn’t modify \_\_hash\_\_ without also modifying

\_\_eq\_\_. If you’re not sure what you’re doing, further reading is suggested.

“Python Hashes and Equality”by our tech reviewer Hynek Schlawack is a good

place to start.



5

Not Everything Has to Be an Object: A

Domain Service Function

We’ve made a model to represent batches, but what we actually need

to do is allocate order lines against a specific set of batches that

represent all our stock.

Sometimes, it just isn’t a thing.

—Eric Evans, Domain-Driven Design

Evans discusses the idea of Domain Service operations that don’t have

a natural home in an entity or value object. A thing that allocates an

order line, given a set of batches, sounds a lot like a function, and we

can take advantage of the fact that Python is a multiparadigm language

and just make it a function.

Let’s see how we might test-drive such a function:

Testing our domain service (test\_allocate.py)



def test\_prefers\_current\_stock\_batches\_to\_shipments():

in\_stock\_batch=Batch("in-stock-batch","RETRO-CLOCK", 100 ,eta=None)

shipment\_batch=Batch("shipment-batch","RETRO-CLOCK", 100 ,eta=tomorrow)

line=OrderLine("oref","RETRO-CLOCK", 10 )



allocate(line, \[in\_stock\_batch,shipment\_batch])



assert in\_stock\_batch.available\_quantity== 90

assert shipment\_batch.available\_quantity== 100



def test\_prefers\_earlier\_batches():

earliest=Batch("speedy-batch","MINIMALIST-SPOON", 100 ,eta=today)

medium=Batch("normal-batch","MINIMALIST-SPOON", 100 ,eta=tomorrow)

latest=Batch("slow-batch","MINIMALIST-SPOON", 100 ,eta=later)

6



line=OrderLine("order1","MINIMALIST-SPOON", 10 )



allocate(line, \[medium,earliest,latest])



assert earliest.available\_quantity== 90

assert medium.available\_quantity== 100

assert latest.available\_quantity== 100



def test\_returns\_allocated\_batch\_ref():

in\_stock\_batch=Batch("in-stock-batch-ref","HIGHBROW-POSTER", 100 ,

eta=None)

shipment\_batch=Batch("shipment-batch-ref","HIGHBROW-POSTER", 100 ,

eta=tomorrow)

line=OrderLine("oref","HIGHBROW-POSTER", 10 )

allocation=allocate(line, \[in\_stock\_batch,shipment\_batch])

assert allocation==in\_stock\_batch.reference

And our service might look like this:

A standalone function for our domain service (model.py)



def allocate(line:OrderLine,batches:List\[Batch])->str:

batch=next(

b for b in sorted(batches) if b.can\_allocate(line)

)

batch.allocate(line)

return batch.reference

Python’s Magic Methods Let Us Use Our Models

with Idiomatic Python

You may or may not like the use of next() in the preceding code, but

we’re pretty sure you’ll agree that being able to use sorted() on our

list of batches is nice, idiomatic Python.

To make it work, we implement gt on our domain model:

Magic methods can express domain semantics (model.py)



classBatch :

...



def \_\_gt\_\_(self,other):

if self.eta is None:

return False

if other.eta is None:

return True

return self.eta>other.eta



That’s lovely.

Exceptions Can Express Domain Concepts Too

We have one final concept to cover: exceptions can be used to express

domain concepts too. In our conversations with domain experts, we’ve

learned about the possibility that an order cannot be allocated because

we are out of stock , and we can capture that by using a domain

exception :

Testing out-of-stock exception (test\_allocate.py)



def test\_raises\_out\_of\_stock\_exception\_if\_cannot\_allocate():

batch=Batch('batch1','SMALL-FORK', 10 ,eta=today)

allocate(OrderLine('order1','SMALL-FORK', 10 ), \[batch])



with pytest.raises(OutOfStock,match='SMALL-FORK'):

allocate(OrderLine('order2','SMALL-FORK', 1 ), \[batch])



DOMAIN MODELING RECAP



Domain modeling

This is the part of your code that is closest to the business, the most likely to change, and the

place where you deliver the most value to the business. Make it easy to understand and

modify.



Distinguish entities from value objects

A value object is defined by its attributes. It’s usually best implemented as an immutable

type. If you change an attribute on a Value Object, it represents a different object. In contrast,

an entity has attributes that may vary over time and it will still be the same entity. It’s important

to define what does uniquely identify an entity (usually some sort of name or reference field).



Not everything has to be an object

Python is a multiparadigm language, so let the “verbs” in your code be functions. For every

FooManager, BarBuilder, or BazFactory, there’s often a more expressive and readable

manage\_foo(), build\_bar(), or get\_baz() waiting to happen.



This is the time to apply your best OO design principles

Revisit the SOLID principles and all the other good heuristics like “has a versus is-a,” “prefer

composition over inheritance,” and so on.



You’ll also want to think about consistency boundaries and aggregates

But that’s a topic forChapter 7.



We won’t bore you too much with the implementation, but the main

thing to note is that we take care in naming our exceptions in the

ubiquitous language, just as we do our entities, value objects, and

services:

Raising a domain exception (model.py)



classOutOfStock ( Exception ):

pass



def allocate(line:OrderLine,batches:List\[Batch])->str:

try :

batch=next(

...



exceptStopIteration :

raise OutOfStock(f'Out of stock for sku {line.sku}')



Figure 1-4is a visual representation of where we’ve ended up.



Figure 1-4. Our domain model at the end of the chapter



That’ll probably do for now! We have a domain service that we can

use for our first use case. But first we’ll need a database...



1 DDD did not originate domain modeling. Eric Evans refers to the 2002 book Object

Design by Rebecca Wirfs-Brock and Alan McKean (Addison-Wesley Professional),

which introduced responsibility-driven design, of which DDD is a special case dealing

with the domain. But even that is too late, and OO enthusiasts will tell you to look further

back to Ivar Jacobson and Grady Booch; the term has been around since the mid-1980s.



2 In previous Python versions, we might have used a namedtuple. You could also check out

Hynek Schlawack’s excellentattrs.



3 Or perhaps you think there’s not enough code? What about some sort of check that the

SKU in the OrderLine matches Batch.sku? We saved some thoughts on validation for

Appendix E.



4 It is appalling. Please, please don’t do this. —Harry



5 The \_\_eq\_\_ method is pronounced “dunder-EQ.” By some, at least.



6 Domain services are not the same thing as the services from theservice layer, although

they are often closely related. A domain service represents a business concept or

process, whereas a service-layer service represents a use case for your application.

Often the service layer will call a domain service.



Chapter 2. Repository Pattern

It’s time to make good on our promise to use the dependency inversion

principle as a way of decoupling our core logic from infrastructural

concerns.

We’ll introduce the Repository pattern, a simplifying abstraction over

data storage, allowing us to decouple our model layer from the data

layer. We’ll present a concrete example of how this simplifying

abstraction makes our system more testable by hiding the complexities

of the database.

Figure 2-1shows a little preview of what we’re going to build: a

Repository object that sits between our domain model and the

database.



Figure 2-1. Before and after the Repository pattern

T IP



The code for this chapter is in the chapter\_02\_repository branchon GitHub.



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_02\_repository

\# or to code along, checkout the previous chapter:

git checkout chapter\_01\_domain\_model



Persisting Our Domain Model

InChapter 1we built a simple domain model that can allocate orders

to batches of stock. It’s easy for us to write tests against this code

because there aren’t any dependencies or infrastructure to set up. If we

needed to run a database or an API and create test data, our tests

would be harder to write and maintain.

Sadly, at some point we’ll need to put our perfect little model in the

hands of users and contend with the real world of spreadsheets and

web browsers and race conditions. For the next few chapters we’re

going to look at how we can connect our idealized domain model to

external state.

We expect to be working in an agile manner, so our priority is to get to

a minimum viable product as quickly as possible. In our case, that’s

going to be a web API. In a real project, you might dive straight in

with some end-to-end tests and start plugging in a web framework,

test-driving things outside-in.

But we know that, no matter what, we’re going to need some form of

persistent storage, and this is a textbook, so we can allow ourselves a

tiny bit more bottom-up development and start to think about storage

and databases.

Some Pseudocode: What Are We Going

to Need?

When we build our first API endpoint, we know we’re going to have

some code that looks more or less like the following.

What our first API endpoint will look like



@flask.route.gubbins

def allocate\_endpoint():

\# extract order line from request

line=OrderLine(request.params,...)

\# load all batches from the DB

batches= ...

\# call our domain service

allocate(line,batches)

\# then save the allocation back to the database somehow

return 201

NOT E



We’ve used Flask because it’s lightweight, but you don’t need to be a Flask user

to understand this book. In fact, we’ll show you how to make your choice of

framework a minor detail.



We’ll need a way to retrieve batch info from the database and

instantiate our domain model objects from it, and we’ll also need a

way of saving them back to the database.

What? Oh, “gubbins” is a British word for “stuff.” You can just

ignore that. It’s pseudocode, OK?

Applying the DIP to Data Access

As mentioned in theintroduction, a layered architecture is a common

approach to structuring a system that has a UI, some logic, and a

database (seeFigure 2-2).



Figure 2-2. Layered architecture



Django’s Model-View-Template structure is closely related, as is

Model-View-Controller (MVC). In any case, the aim is to keep the

layers separate (which is a good thing), and to have each layer depend

only on the one below it.

But we want our domain model to have no dependencies whatsoever.

We don’t want infrastructure concerns bleeding over into our domain

model and slowing our unit tests or our ability to make changes.

Instead, as discussed in the introduction, we’ll think of our model as

being on the “inside,” and dependencies flowing inward to it; this is

what people sometimes call onion architecture (seeFigure 2-3).

1



Figure 2-3. Onion architecture



IS THIS PORTS AND ADAPTERS?



If you’ve been reading about architectural patterns, you may be asking yourself questions like

this:



Is this ports and adapters? Or is it hexagonal architecture? Is that the sam e as onion

architecture? What ab out the clean architecture? What’s a port, and what’s an adapter? Why

do you people have so m any words for the sam e thing?



Although some people like to nitpick over the differences, all these are pretty much names for the

same thing, and they all boil down to the dependency inversion principle: high-level modules (the

domain) should not depend on low-level ones (the infrastructure).



We’ll get into some of the nitty-gritty around “depending on abstractions,” and whether there is a

Pythonic equivalent of interfaces,later in the book. See also“What Is a Port and What Is an

Adapter, in Python?”.



2



Reminder: Our Model

Let’s remind ourselves of our domain model (seeFigure 2-4): an

allocation is the concept of linking an OrderLine to a Batch. We’re

storing the allocations as a collection on our Batch object.



Figure 2-4. Our model



Let’s see how we might translate this to a relational database.

The “Normal” ORM Way: Model Depends on ORM

These days, it’s unlikely that your team members are hand-rolling their

own SQL queries. Instead, you’re almost certainly using some kind of

framework to generate SQL for you based on your model objects.

These frameworks are called object-relational mappers (ORMs)

because they exist to bridge the conceptual gap between the world of

objects and domain modeling and the world of databases and

relational algebra.

The most important thing an ORM gives us is persistence ignorance :

the idea that our fancy domain model doesn’t need to know anything

about how data is loaded or persisted. This helps keep our domain

clean of direct dependencies on particular database technologies.

But if you follow the typical SQLAlchemy tutorial, you’ll end up with

something like this:

SQLAlchemy “declarative” syntax, model depends on ORM (orm.py)



fromsqlalchemyimport Column,ForeignKey,Integer,String

fromsqlalchemy.ext.declarativeimport declarative\_base

fromsqlalchemy.ormimport relationship



Base=declarative\_base()



classOrder (Base):

id=Column(Integer,primary\_key=True)



classOrderLine (Base):

id=Column(Integer,primary\_key=True)

sku=Column(String( 250 ))

qty=Integer(String( 250 ))

order\_id=Column(Integer,ForeignKey('order.id'))

order=relationship(Order)



classAllocation (Base):

...

You don’t need to understand SQLAlchemy to see that our pristine

model is now full of dependencies on the ORM and is starting to look

ugly as hell besides. Can we really say this model is ignorant of the

database? How can it be separate from storage concerns when our

model properties are directly coupled to database columns?

3

DJANGO’S ORM IS ESSENTIALLY THE SAME, BUT MORE

RESTRICTIVE



If you’re more used to Django, the preceding “declarative” SQLAlchemy snippet translates to

something like this:

Django ORM exam ple

classOrder (models.Model):

pass

classOrderLine (models.Model):

sku=models.CharField(max\_length= 255 )

qty=models.IntegerField()

order=models.ForeignKey(Order)

classAllocation (models.Model):

...

The point is the same—our model classes inherit directly from ORM classes, so our model

depends on the ORM. We want it to be the other way around.

Django doesn’t provide an equivalent for SQLAlchemy’s classical mapper, but seeAppendix D

for examples of how to apply dependency inversion and the Repository pattern to Django.



Inverting the Dependency: ORM Depends on

Model

Well, thankfully, that’s not the only way to use SQLAlchemy. The

alternative is to define your schema separately, and to define an

explicit mapper for how to convert between the schema and our

domain model, what SQLAlchemy calls aclassical mapping:

Explicit ORM mapping with SQLAlchemy Table objects (orm.py)



fromsqlalchemy.ormimport mapper,relationship



importmodel



metadata=MetaData()



order\_lines=Table(

'order\_lines',metadata,

Column('id',Integer,primary\_key=True,autoincrement=True),

Column('sku',String( 255 )),

Column('qty',Integer,nullable=False),

Column('orderid',String( 255 )),

)



...



def start\_mappers():

lines\_mapper=mapper(model.OrderLine,order\_lines)

The ORM imports (or “depends on” or “knows about”) the domain

model, and not the other way around.

We define our database tables and columns by using

SQLAlchemy’s abstractions.

When we call the mapper function, SQLAlchemy does its magic to

bind our domain model classes to the various tables we’ve

defined.

The end result will be that, if we call start\_mappers, we will be

able to easily load and save domain model instances from and to the

database. But if we never call that function, our domain model classes

stay blissfully unaware of the database.

This gives us all the benefits of SQLAlchemy, including the ability to

use alembic for migrations, and the ability to transparently query

using our domain classes, as we’ll see.

When you’re first trying to build your ORM config, it can be useful to

write tests for it, as in the following example:

4

Testing the ORM directly (throwaway tests) (test\_orm.py)



def test\_orderline\_mapper\_can\_load\_lines(session):

session.execute(

'INSERT INTO order\_lines (orderid, sku, qty) VALUES '

'("order1", "RED-CHAIR", 12),'

'("order1", "RED-TABLE", 13),'

'("order2", "BLUE-LIPSTICK", 14)'

)

expected=\[

model.OrderLine("order1","RED-CHAIR", 12 ),

model.OrderLine("order1","RED-TABLE", 13 ),

model.OrderLine("order2","BLUE-LIPSTICK", 14 ),

]

assert session.query(model.OrderLine).all()==expected



def test\_orderline\_mapper\_can\_save\_lines(session):

new\_line=model.OrderLine("order1","DECORATIVE-WIDGET", 12 )

session.add(new\_line)

session.commit()



rows=list(session.execute('SELECT orderid, sku, qty FROM "order\_lines"'))

assert rows ==\[("order1","DECORATIVE-WIDGET", 12 )]



If you haven’t used pytest, the session argument to this test needs

explaining. You don’t need to worry about the details of pytest or

its fixtures for the purposes of this book, but the short explanation

is that you can define common dependencies for your tests as

“fixtures,” and pytest will inject them to the tests that need them by

looking at their function arguments. In this case, it’s a SQLAlchemy

database session.

You probably wouldn’t keep these tests around—as you’ll see shortly,

once you’ve taken the step of inverting the dependency of ORM and

domain model, it’s only a small additional step to implement another

abstraction called the Repository pattern, which will be easier to write

tests against and will provide a simple interface for faking out later in

tests.

But we’ve already achieved our objective of inverting the traditional

dependency: the domain model stays “pure” and free from

infrastructure concerns. We could throw away SQLAlchemy and use a

different ORM, or a totally different persistence system, and the

domain model doesn’t need to change at all.

Depending on what you’re doing in your domain model, and especially

if you stray far from the OO paradigm, you may find it increasingly

hard to get the ORM to produce the exact behavior you need, and you

may need to modify your domain model. As so often happens with

architectural decisions, you’ll need to consider a trade-off. As the Zen

of Python says, “Practicality beats purity!”

At this point, though, our API endpoint might look something like the

following, and we could get it to work just fine:

Using SQLAlchemy directly in our API endpoint



@flask.route.gubbins

def allocate\_endpoint():

session=start\_session()



\# extract order line from request

line=OrderLine(

request.json\['orderid'],

request.json\['sku'],

request.json\['qty'],

)



\# load all batches from the DB



5



batches=session.query(Batch).all()



\# call our domain service

allocate(line,batches)



\# save the allocation back to the database

session.commit()



return 201



Introducing the Repository Pattern

The Repository pattern is an abstraction over persistent storage. It

hides the boring details of data access by pretending that all of our

data is in memory.

If we had infinite memory in our laptops, we’d have no need for

clumsy databases. Instead, we could just use our objects whenever we

liked. What would that look like?

You have to get your data from somewhere



importall\_my\_data



def create\_a\_batch():

batch=Batch(...)

all\_my\_data.batches.add(batch)



def modify\_a\_batch(batch\_id,new\_quantity):

batch=all\_my\_data.batches.get(batch\_id)

batch.change\_initial\_quantity(new\_quantity)

Even though our objects are in memory, we need to put them

somewhere so we can find them again. Our in-memory data would let

us add new objects, just like a list or a set. Because the objects are in

memory, we never need to call a .save() method; we just fetch the

object we care about and modify it in memory.

The Repository in the Abstract

The simplest repository has just two methods: add() to put a new item

in the repository, and get() to return a previously added item. We

stick rigidly to using these methods for data access in our domain and

our service layer. This self-imposed simplicity stops us from coupling

our domain model to the database.

Here’s what an abstract base class (ABC) for our repository would

look like:

The simplest possible repository (repository.py)



classAbstractRepository (abc.ABC):



@abc.abstractmethod

def add(self,batch:model.Batch):

raiseNotImplementedError



@abc.abstractmethod

def get(self,reference)->model.Batch:

raiseNotImplementedError



Python tip: @abc.abstractmethod is one of the only things that

makes ABCs actually “work” in Python. Python will refuse to let

you instantiate a class that does not implement all the

abstractmethods defined in its parent class.

raise NotImplementedError is nice, but it’s neither necessary

nor sufficient. In fact, your abstract methods can have real behavior

that subclasses can call out to, if you really want.

6

7

ABSTRACT BASE CLASSES, DUCK TYPING, AND PROTOCOLS



We’re using abstract base classes in this book for didactic reasons: we hope they help explain

what the interface of the repository abstraction is.

In real life, we’ve sometimes found ourselves deleting ABCs from our production code, because

Python makes it too easy to ignore them, and they end up unmaintained and, at worst,

misleading. In practice we often just rely on Python’s duck typing to enable abstractions. To a

Pythonista, a repository is any object that has add( thing ) and get( id ) methods.



An alternative to look into isPEP 544 protocols. These give you typing without the possibility of

inheritance, which “prefer composition over inheritance” fans will particularly like.



What Is the Trade-Off?

You know they say economists know the price of everything and

the value of nothing? Well, programmers know the benefits of

everything and the trade-offs of nothing.

—Rich Hickey

Whenever we introduce an architectural pattern in this book, we’ll

always ask, “What do we get for this? And what does it cost us?”

Usually, at the very least, we’ll be introducing an extra layer of

abstraction, and although we may hope it will reduce complexity

overall, it does add complexity locally, and it has a cost in terms of the

raw numbers of moving parts and ongoing maintenance.

The Repository pattern is probably one of the easiest choices in the

book, though, if you’re already heading down the DDD and

dependency inversion route. As far as our code is concerned, we’re

really just swapping the SQLAlchemy abstraction

(session.query(Batch)) for a different one (batches\_repo.get)

that we designed.

We will have to write a few lines of code in our repository class each

time we add a new domain object that we want to retrieve, but in

return we get a simple abstraction over our storage layer, which we

control. The Repository pattern would make it easy to make

fundamental changes to the way we store things (seeAppendix C), and

as we’ll see, it is easy to fake out for unit tests.

In addition, the Repository pattern is so common in the DDD world

that, if you do collaborate with programmers who have come to Python

from the Java and C# worlds, they’re likely to recognize it.Figure 2-5

illustrates the pattern.



Figure 2-5. Repository pattern



As always, we start with a test. This would probably be classified as

an integration test, since we’re checking that our code (the repository)

is correctly integrated with the database; hence, the tests tend to mix

raw SQL with calls and assertions on our own code.

T IP



Unlike the ORM tests from earlier, these tests are good candidates for staying

part of your codebase longer term, particularly if any parts of your domain model

mean the object-relational map is nontrivial.



Repository test for saving an object (test\_repository.py)



def test\_repository\_can\_save\_a\_batch(session):

batch=model.Batch("batch1","RUSTY-SOAPDISH", 100 ,eta=None)



repo=repository.SqlAlchemyRepository(session)

repo.add(batch)

session.commit()



rows=list(session.execute(

'SELECT reference, sku, \_purchased\_quantity, eta FROM "batches"'

))

assert rows ==\[("batch1","RUSTY-SOAPDISH", 100 ,None)]



repo.add() is the method under test here.

We keep the .commit() outside of the repository and make it the

responsibility of the caller. There are pros and cons for this; some

of our reasons will become clearer when we get toChapter 6.

We use the raw SQL to verify that the right data has been saved.

The next test involves retrieving batches and allocations, so it’s more

complex:

Repository test for retrieving a complex object (test\_repository.py)



def insert\_order\_line(session):

session.execute(

'INSERT INTO order\_lines (orderid, sku, qty)'

' VALUES ("order1", "GENERIC-SOFA", 12)'

)

\[\[orderline\_id]]=session.execute(

'SELECT id FROM order\_lines WHERE orderid=:orderid AND sku=:sku',

dict(orderid="order1",sku="GENERIC-SOFA")

)

return orderline\_id



def insert\_batch(session,batch\_id):

...



def test\_repository\_can\_retrieve\_a\_batch\_with\_allocations(session):

orderline\_id=insert\_order\_line(session)

batch1\_id=insert\_batch(session,"batch1")

insert\_batch(session,"batch2")

insert\_allocation(session,orderline\_id,batch1\_id)



repo=repository.SqlAlchemyRepository(session)

retrieved=repo.get("batch1")



expected=model.Batch("batch1","GENERIC-SOFA", 100 ,eta=None)

assert retrieved==expected # Batch.\_\_eq\_\_ only compares reference

assert retrieved.sku==expected.sku

assert retrieved.\_purchased\_quantity==expected.\_purchased\_quantity

assert retrieved.\_allocations=={

model.OrderLine("order1","GENERIC-SOFA", 12 ),

}



This tests the read side, so the raw SQL is preparing data to be

read by the repo.get().

We’ll spare you the details of insert\_batch and

insert\_allocation; the point is to create a couple of batches,

and, for the batch we’re interested in, to have one existing order

line allocated to it.

And that’s what we verify here. The first assert == checks that

the types match, and that the reference is the same (because, as you

remember, Batch is an entity, and we have a custom eq for it).

So we also explicitly check on its major attributes, including

.\_allocations, which is a Python set of OrderLine value

objects.

Whether or not you painstakingly write tests for every model is a

judgment call. Once you have one class tested for create/modify/save,

you might be happy to go on and do the others with a minimal round-

trip test, or even nothing at all, if they all follow a similar pattern. In

our case, the ORM config that sets up the .\_allocations set is a little

complex, so it merited a specific test.

You end up with something like this:

A typical repository (repository.py)



classSqlAlchemyRepository (AbstractRepository):



def \_\_init\_\_(self,session):

self.session=session



def add(self,batch):

self.session.add(batch)



def get(self,reference):

return

self.session.query(model.Batch).filter\_by(reference=reference).one()



def list(self):

return self.session.query(model.Batch).all()



And now our Flask endpoint might look something like the following:

Using our repository directly in our API endpoint



@flask.route.gubbins

def allocate\_endpoint():

batches=SqlAlchemyRepository.list()

lines=\[

OrderLine(l\['orderid'],l\['sku'],l\['qty'])

for l in request.params...

]

allocate(lines,batches)



session.commit()

return 201



EXERCISE FOR THE READER



We bumped into a friend at a DDD conference the other day who said, “I haven’t used an ORM in

10 years.” The Repository pattern and an ORM both act as abstractions in front of raw SQL, so

using one behind the other isn’t really necessary. Why not have a go at implementing our

repository without using the ORM? You’ll find the codeon GitHub.

We’ve left the repository tests, but figuring out what SQL to write is up to you. Perhaps it’ll be

harder than you think; perhaps it’ll be easier. But the nice thing is, the rest of your application just

doesn’t care.



Building a Fake Repository for Tests Is

Now Trivial!

Here’s one of the biggest benefits of the Repository pattern:

A simple fake repository using a set (repository.py)



classFakeRepository (AbstractRepository):



def \_\_init\_\_(self,batches):

self.\_batches=set(batches)



def add(self,batch):

self.\_batches.add(batch)



def get(self,reference):

return next(b for b in self.\_batches if b.reference==reference)



def list(self):

return list(self.\_batches)



Because it’s a simple wrapper around a set, all the methods are one-

liners.

Using a fake repo in tests is really easy, and we have a simple

abstraction that’s easy to use and reason about:

Example usage of fake repository (test\_api.py)



fake\_repo=FakeRepository(\[batch1,batch2,batch3])

You’ll see this fake in action in the next chapter.

T IP



Building fakes for your abstractions is an excellent way to get design feedback: if

it’s hard to fake, the abstraction is probably too complicated.



What Is a Port and What Is an Adapter, in

Python?

We don’t want to dwell on the terminology too much here because the

main thing we want to focus on is dependency inversion, and the

specifics of the technique you use don’t matter too much. Also, we’re

aware that different people use slightly different definitions.

Ports and adapters came out of the OO world, and the definition we

hold onto is that the port is the interface between our application and

whatever it is we wish to abstract away, and the adapter is the

implementation behind that interface or abstraction.

Now Python doesn’t have interfaces per se, so although it’s usually

easy to identify an adapter, defining the port can be harder. If you’re

using an abstract base class, that’s the port. If not, the port is just the

duck type that your adapters conform to and that your core application

expects—the function and method names in use, and their argument

names and types.

Concretely, in this chapter, AbstractRepository is the port, and

SqlAlchemyRepository and FakeRepository are the adapters.

Wrap-Up

Bearing the Rich Hickey quote in mind, in each chapter we summarize

the costs and benefits of each architectural pattern we introduce. We

want to be clear that we’re not saying every single application needs

to be built this way; only sometimes does the complexity of the app

and domain make it worth investing the time and effort in adding these

extra layers of indirection.

With that in mind,Table 2-1shows some of the pros and cons of the

Repository pattern and our persistence-ignorant model.

Table 2-1. Repository pattern and persistence ignorance: the

trade-offs



Pros Cons



Pros Cons



We have a simple interface

between persistent storage

and our domain model.



It’s easy to make a fake

version of the repository for

unit testing, or to

swap out different storage

solutions, because we’ve fully

decoupled the model

from infrastructure concerns.



Writing the domain model

before thinking about

persistence helps us focus on

the business problem at hand.

If we ever want to radically

change our approach,

we can do that in our model,

without needing to worry

about foreign keys

or migrations until later.



Our database schema is

really simple because we

have complete control over

how we map our objects to

tables.



An ORM already buys you some

decoupling. Changing foreign keys

might be hard,

but it should be pretty easy to

swap between MySQL and

Postgres if you

ever need to.



Maintaining ORM mappings by

hand requires extra work and

extra code.



Any extra layer of indirection

always increases maintenance

costs and

adds a “WTF factor” for Python

programmers who’ve never seen

the Repository pattern

before.



Figure 2-6shows the basic thesis: yes, for simple cases, a decoupled

domain model is harder work than a simple ORM/ActiveRecord

pattern.

T IP



If your app is just a simple CRUD (create-read-update-delete) wrapper around a

database, then you don’t need a domain model or a repository.



But the more complex the domain, the more an investment in freeing

yourself from infrastructure concerns will pay off in terms of the ease

of making changes.

8



Figure 2-6. Domain model trade-offs as a diagram



Our example code isn’t complex enough to give more than a hint of

what the right-hand side of the graph looks like, but the hints are there.

Imagine, for example, if we decide one day that we want to change

allocations to live on the OrderLine instead of on the Batch object: if

we were using Django, say, we’d have to define and think through the

database migration before we could run any tests. As it is, because our

model is just plain old Python objects, we can change a set() to being

a new attribute, without needing to think about the database until later.

REPOSITORY PATTERN RECAP



Apply dependency inversion to your ORM

Our domain model should be free of infrastructure concerns, so your ORM should import

your model, and not the other way around.



The Repository pattern is a simple abstraction around permanent storage

The repository gives you the illusion of a collection of in-memory objects. It makes it easy to

create a FakeRepository for testing and to swap fundamental details of your infrastructure

without disrupting your core application. SeeAppendix Cfor an example.



You’ll be wondering, how do we instantiate these repositories, fake or

real? What will our Flask app actually look like? You’ll find out in the

next exciting installment,the Service Layer pattern.

But first, a brief digression.



1 I suppose we mean “no stateful dependencies.” Depending on a helper library is fine;

depending on an ORM or a web framework is not.



2 Mark Seemann hasan excellent blog poston the topic.



3 In this sense, using an ORM is already an example of the DIP. Instead of depending on

hardcoded SQL, we depend on an abstraction, the ORM. But that’s not enough for us—

not in this book!



4 Even in projects where we don’t use an ORM, we often use SQLAlchemy alongside

Alembic to declaratively create schemas in Python and to manage migrations,

connections, and sessions.



5 Shout-out to the amazingly helpful SQLAlchemy maintainers, and to Mike Bayer in

particular.



6 You may be thinking, “What about list or delete or update?” However, in an ideal

world, we modify our model objects one at a time, and delete is usually handled as a soft-

delete—i.e., batch.cancel(). Finally, update is taken care of by the Unit of Work

pattern, as you’ll see inChapter 6.



7 To really reap the benefits of ABCs (such as they may be), be running helpers like

pylint and mypy.



8 Diagram inspired by a post called“Global Complexity, Local Simplicity”by Rob Vens.

Chapter 3. A Brief Interlude:

On Coupling and

Abstractions

Allow us a brief digression on the subject of abstractions, dear reader.

We’ve talked about abstractions quite a lot. The Repository pattern is

an abstraction over permanent storage, for example. But what makes a

good abstraction? What do we want from abstractions? And how do

they relate to testing?

T IP



The code for this chapter is in the chapter\_03\_abstractions branchon GitHub:



git clone https://github.com/cosmicpython/code.git

git checkout chapter\_03\_abstractions



A key theme in this book, hidden among the fancy patterns, is that we

can use simple abstractions to hide messy details. When we’re writing

code for fun, or in a kata, we get to play with ideas freely, hammering

things out and refactoring aggressively. In a large-scale system, though,

we become constrained by the decisions made elsewhere in the

system.

1

When we’re unable to change component A for fear of breaking

component B, we say that the components have become coupled.

Locally, coupling is a good thing: it’s a sign that our code is working

together, each component supporting the others, all of them fitting in

place like the gears of a watch. In jargon, we say this works when

there is high cohesion between the coupled elements.

Globally, coupling is a nuisance: it increases the risk and the cost of

changing our code, sometimes to the point where we feel unable to

make any changes at all. This is the problem with the Ball of Mud

pattern: as the application grows, if we’re unable to prevent coupling

between elements that have no cohesion, that coupling increases

superlinearly until we are no longer able to effectively change our

systems.

We can reduce the degree of coupling within a system (Figure 3-1) by

abstracting away the details (Figure 3-2).



Figure 3-1. Lots of coupling



Figure 3-2. Less coupling



In both diagrams, we have a pair of subsystems, with one dependent on

the other. InFigure 3-1, there is a high degree of coupling between the

two; the number of arrows indicates lots of kinds of dependencies

between the two. If we need to change system B, there’s a good chance

that the change will ripple through to system A.

InFigure 3-2, though, we have reduced the degree of coupling by

inserting a new, simpler abstraction. Because it is simpler, system A

has fewer kinds of dependencies on the abstraction. The abstraction

serves to protect us from change by hiding away the complex details of

whatever system B does—we can change the arrows on the right

without changing the ones on the left.

Abstracting State Aids Testability

Let’s see an example. Imagine we want to write code for synchronizing

two file directories, which we’ll call the source and the destination :

If a file exists in the source but not in the destination, copy the

file over.

If a file exists in the source, but it has a different name than in

the destination, rename the destination file to match.

If a file exists in the destination but not in the source, remove

it.

Our first and third requirements are simple enough: we can just

compare two lists of paths. Our second is trickier, though. To detect

renames, we’ll have to inspect the content of files. For this, we can use

a hashing function like MD5 or SHA-1. The code to generate a SHA-1

hash from a file is simple enough:

Hashing a file (sync.py)

BLOCKSIZE= 65536



def hash\_file(path):

hasher=hashlib.sha1()

with path.open("rb") as file:

buf=file.read(BLOCKSIZE)

while buf:

hasher.update(buf)

buf=file.read(BLOCKSIZE)

return hasher.hexdigest()

Now we need to write the bit that makes decisions about what to do—

the business logic, if you will.

When we have to tackle a problem from first principles, we usually try

to write a simple implementation and then refactor toward better

design. We’ll use this approach throughout the book, because it’s how

we write code in the real world: start with a solution to the smallest

part of the problem, and then iteratively make the solution richer and

better designed.

Our first hackish approach looks something like this:

Basic sync algorithm (sync.py)



importhashlib

importos

importshutil

frompathlibimport Path



def sync(source,dest):

\# Walk the source folder and build a dict of filenames and their hashes

source\_hashes={}

for folder,\_,files in os.walk(source):

for fn in files:

source\_hashes\[hash\_file(Path(folder)/fn)]=fn



seen=set() # Keep track of the files we've found in the target



\# Walk the target folder and get the filenames and hashes

for folder,\_,files in os.walk(dest):

for fn in files:

dest\_path=Path(folder)/fn

dest\_hash=hash\_file(dest\_path)

seen.add(dest\_hash)



\# if there's a file in target that's not in source, delete it

if dest\_hash not in source\_hashes:

dest\_path.remove()



\# if there's a file in target that has a different path in source,

\# move it to the correct path

elif dest\_hash in source\_hashes and fn!=source\_hashes\[dest\_hash]:

shutil.move(dest\_path,Path(folder)/source\_hashes\[dest\_hash])



\# for every file that appears in source but not target, copy the file to

\# the target

for src\_hash,fn in source\_hashes.items():

if src\_hash not in seen:

shutil.copy(Path(source)/fn,Path(dest)/fn)



Fantastic! We have some code and it looks OK, but before we run it on

our hard drive, maybe we should test it. How do we go about testing

this sort of thing?

Some end-to-end tests (test\_sync.py)



def test\_when\_a\_file\_exists\_in\_the\_source\_but\_not\_the\_destination():

try :

source=tempfile.mkdtemp()

dest=tempfile.mkdtemp()



content="I am a very useful file"

(Path(source)/'my-file').write\_text(content)



sync(source,dest)



expected\_path=Path(dest)/ 'my-file'

assert expected\_path.exists()

assert expected\_path.read\_text()==content



finally :

shutil.rmtree(source)

shutil.rmtree(dest)



def test\_when\_a\_file\_has\_been\_renamed\_in\_the\_source():

try :

source=tempfile.mkdtemp()

dest=tempfile.mkdtemp()



content="I am a file that was renamed"

source\_path=Path(source)/'source-filename'

old\_dest\_path=Path(dest)/'dest-filename'

expected\_dest\_path=Path(dest)/'source-filename'

source\_path.write\_text(content)

old\_dest\_path.write\_text(content)



sync(source,dest)



assert old\_dest\_path.exists() is False

assert expected\_dest\_path.read\_text()==content



finally :

shutil.rmtree(source)

shutil.rmtree(dest)



Wowsers, that’s a lot of setup for two simple cases! The problem is

that our domain logic, “figure out the difference between two

directories,” is tightly coupled to the I/O code. We can’t run our

difference algorithm without calling the pathlib, shutil, and

hashlib modules.

And the trouble is, even with our current requirements, we haven’t

written enough tests: the current implementation has several bugs (the

shutil.move() is wrong, for example). Getting decent coverage and

revealing these bugs means writing more tests, but if they’re all as

unwieldy as the preceding ones, that’s going to get real painful real

quickly.

On top of that, our code isn’t very extensible. Imagine trying to

implement a --dry-run flag that gets our code to just print out what

it’s going to do, rather than actually do it. Or what if we wanted to

sync to a remote server, or to cloud storage?

Our high-level code is coupled to low-level details, and it’s making

life hard. As the scenarios we consider get more complex, our tests

will get more unwieldy. We can definitely refactor these tests (some of

the cleanup could go into pytest fixtures, for example) but as long as

we’re doing filesystem operations, they’re going to stay slow and be

hard to read and write.

Choosing the Right Abstraction(s)

What could we do to rewrite our code to make it more testable?

First, we need to think about what our code needs from the filesystem.

Reading through the code, we can see that three distinct things are

happening. We can think of these as three distinct responsibilities that

the code has:

1\. We interrogate the filesystem by using os.walk and determine

hashes for a series of paths. This is similar in both the source

and the destination cases.

2\. We decide whether a file is new, renamed, or redundant.

3\. We copy, move, or delete files to match the source.

Remember that we want to find simplifying abstractions for each of

these responsibilities. That will let us hide the messy details so we can

focus on the interesting logic.

NOT E



In this chapter, we’re refactoring some gnarly code into a more testable structure

by identifying the separate tasks that need to be done and giving each task to a

clearly defined actor, along similar lines tothe duckduckgo example.



For steps 1 and 2, we’ve already intuitively started using an

abstraction, a dictionary of hashes to paths. You may already have

been thinking, “Why not build up a dictionary for the destination folder

as well as the source, and then we just compare two dicts?” That

seems like a nice way to abstract the current state of the filesystem:



source\_files = {'hash1': 'path1', 'hash2': 'path2'}

dest\_files = {'hash1': 'path1', 'hash2': 'pathX'}



What about moving from step 2 to step 3? How can we abstract out the

actual move/copy/delete filesystem interaction?

We’ll apply a trick here that we’ll employ on a grand scale later in the

book. We’re going to separate what we want to do from how to do it.

2

We’re going to make our program output a list of commands that look

like this:



("COPY", "sourcepath", "destpath"),

("MOVE", "old", "new"),



Now we could write tests that just use two filesystem dicts as inputs,

and we would expect lists of tuples of strings representing actions as

outputs.

Instead of saying, “Given this actual filesystem, when I run my

function, check what actions have happened,” we say, “Given this

abstraction of a filesystem, what abstraction of filesystem actions

will happen?”

Simplified inputs and outputs in our tests (test\_sync.py)



def test\_when\_a\_file\_exists\_in\_the\_source\_but\_not\_the\_destination():

src\_hashes={'hash1':'fn1'}

dst\_hashes={}

expected\_actions=\[('COPY','/src/fn1','/dst/fn1')]

...



def test\_when\_a\_file\_has\_been\_renamed\_in\_the\_source():

src\_hashes={'hash1':'fn1'}

dst\_hashes={'hash1':'fn2'}

expected\_actions==\[('MOVE','/dst/fn2','/dst/fn1')]

...



Implementing Our Chosen Abstractions

That’s all very well, but how do we actually write those new tests,

and how do we change our implementation to make it all work?

Our goal is to isolate the clever part of our system, and to be able to

test it thoroughly without needing to set up a real filesystem. We’ll

create a “core” of code that has no dependencies on external state and

then see how it responds when we give it input from the outside world

(this kind of approach was characterized by Gary Bernhardt as

Functional Core, Imperative Shell, or FCIS).

Let’s start off by splitting the code to separate the stateful parts from

the logic.

And our top-level function will contain almost no logic at all; it’s just

an imperative series of steps: gather inputs, call our logic, apply

outputs:

Split our code into three (sync.py)



def sync(source,dest):

\# imperative shell step 1, gather inputs

source\_hashes=read\_paths\_and\_hashes(source)

dest\_hashes=read\_paths\_and\_hashes(dest)



\# step 2: call functional core

actions=determine\_actions(source\_hashes,dest\_hashes,source,dest)



\# imperative shell step 3, apply outputs

for action,\*paths in actions:

if action=='copy':

shutil.copyfile(\*paths)

if action=='move':

shutil.move(\*paths)

if action=='delete':

os.remove(paths\[ 0 ])



Here’s the first function we factor out,

read\_paths\_and\_hashes(), which isolates the I/O part of our

application.

Here is where carve out the functional core, the business logic.

The code to build up the dictionary of paths and hashes is now trivially

easy to write:

A function that just does I/O (sync.py)



def read\_paths\_and\_hashes(root):

hashes={}

for folder,\_,files in os.walk(root):

for fn in files:

hashes\[hash\_file(Path(folder)/fn)]=fn

return hashes

The determine\_actions() function will be the core of our business

logic, which says, “Given these two sets of hashes and filenames, what

should we copy/move/delete?”. It takes simple data structures and

returns simple data structures:

A function that just does business logic (sync.py)



def determine\_actions(src\_hashes,dst\_hashes,src\_folder,dst\_folder):

for sha,filename in src\_hashes.items():

if sha not in dst\_hashes:

sourcepath=Path(src\_folder)/filename

destpath=Path(dst\_folder)/filename

yield 'copy',sourcepath,destpath



elif dst\_hashes\[sha]!=filename:

olddestpath=Path(dst\_folder)/dst\_hashes\[sha]

newdestpath=Path(dst\_folder)/filename

yield 'move',olddestpath,newdestpath



for sha,filename in dst\_hashes.items():

if sha not in src\_hashes:

yield 'delete',dst\_folder/filename



Our tests now act directly on the determine\_actions() function:

Nicer-looking tests (test\_sync.py)



def test\_when\_a\_file\_exists\_in\_the\_source\_but\_not\_the\_destination():

src\_hashes={'hash1':'fn1'}

dst\_hashes={}

actions=determine\_actions(src\_hashes,dst\_hashes,Path('/src'),

Path('/dst'))

assert list(actions)==\[('copy',Path('/src/fn1'),Path('/dst/fn1'))]

...



def test\_when\_a\_file\_has\_been\_renamed\_in\_the\_source():

src\_hashes={'hash1':'fn1'}

dst\_hashes={'hash1':'fn2'}

actions=determine\_actions(src\_hashes,dst\_hashes,Path('/src'),

Path('/dst'))

assert list(actions)==\[('move',Path('/dst/fn2'),Path('/dst/fn1'))]

Because we’ve disentangled the logic of our program—the code for

identifying changes—from the low-level details of I/O, we can easily

test the core of our code.

With this approach, we’ve switched from testing our main entrypoint

function, sync(), to testing a lower-level function,

determine\_actions(). You might decide that’s fine because sync()

is now so simple. Or you might decide to keep some

integration/acceptance tests to test that sync(). But there’s another

option, which is to modify the sync() function so it can be unit tested

and end-to-end tested; it’s an approach Bob calls edge-to-edge

testing.

Testing Edge to Edge with Fakes and Dependency

Injection

When we start writing a new system, we often focus on the core logic

first, driving it with direct unit tests. At some point, though, we want to

test bigger chunks of the system together.

We could return to our end-to-end tests, but those are still as tricky to

write and maintain as before. Instead, we often write tests that invoke

a whole system together but fake the I/O, sort of edge to edge :

Explicit dependencies (sync.py)



def sync(reader,filesystem,source\_root,dest\_root):



source\_hashes=reader(source\_root)

dest\_hashes=reader(dest\_root)



for sha,filename in src\_hashes.items():

if sha not in dest\_hashes:

sourcepath=source\_root/filename

destpath=dest\_root/filename

filesystem.copy(destpath,sourcepath)



elif dest\_hashes\[sha]!=filename:

olddestpath=dest\_root/dest\_hashes\[sha]

newdestpath=dest\_root/filename

filesystem.move(olddestpath,newdestpath)



for sha,filename in dst\_hashes.items():

if sha not in source\_hashes:

filesystem.delete(dest\_root/filename)



Our top-level function now exposes two new dependencies, a

reader and a filesystem.

We invoke the reader to produce our files dict.

We invoke the filesystem to apply the changes we detect.

T IP



Although we’re using dependency injection, there is no need to define an abstract

base class or any kind of explicit interface. In this book, we often show ABCs

because we hope they help you understand what the abstraction is, but they’re not

necessary. Python’s dynamic nature means we can always rely on duck typing.



Tests using DI



classFakeFileSystem (list):



def copy(self,src,dest):

self.append(('COPY',src,dest))



def move(self,src,dest):

self.append(('MOVE',src,dest))



def delete(self,dest):

self.append(('DELETE',src,dest))



def test\_when\_a\_file\_exists\_in\_the\_source\_but\_not\_the\_destination():

source={"sha1":"my-file"}

dest={}

filesystem=FakeFileSystem()



reader={"/source":source,"/dest":dest}

synchronise\_dirs(reader.pop,filesystem,"/source","/dest")



assert filesystem==\[("COPY","/source/my-file","/dest/my-file")]



def test\_when\_a\_file\_has\_been\_renamed\_in\_the\_source():

source={"sha1":"renamed-file"}

dest={"sha1":"original-file"}

filesystem=FakeFileSystem()



reader={"/source":source,"/dest":dest}

synchronise\_dirs(reader.pop,filesystem,"/source","/dest")



assert filesystem==\[("MOVE","/dest/original-file","/dest/renamed-file")]



Bob loves using lists to build simple test doubles, even though his

coworkers get mad. It means we can write tests like assert foo

not in database.

Each method in our FakeFileSystem just appends something to

the list so we can inspect it later. This is an example of a spy

object.

The advantage of this approach is that our tests act on the exact same

function that’s used by our production code. The disadvantage is that

we have to make our stateful components explicit and pass them

around. David Heinemeier Hansson, the creator of Ruby on Rails,

famously described this as “test-induced design damage.”

In either case, we can now work on fixing all the bugs in our

implementation; enumerating tests for all the edge cases is now much

easier.

Why Not Just Patch It Out?

At this point you may be scratching your head and thinking, “Why don’t

you just use mock.patch and save yourself the effort?"”

We avoid using mocks in this book and in our production code too.

We’re not going to enter into a Holy War, but our instinct is that

mocking frameworks, particularly monkeypatching, are a code smell.

Instead, we like to clearly identify the responsibilities in our

codebase, and to separate those responsibilities into small, focused

objects that are easy to replace with a test double.

NOT E



You can see an example inChapter 8, where we mock.patch() out an email-

sending module, but eventually we replace that with an explicit bit of dependency

injection inChapter 13.



We have three closely related reasons for our preference:

Patching out the dependency you’re using makes it possible to

unit test the code, but it does nothing to improve the design.

Using mock.patch won’t let your code work with a --dry-

run flag, nor will it help you run against an FTP server. For

that, you’ll need to introduce abstractions.

Tests that use mocks tend to be more coupled to the

implementation details of the codebase. That’s because mock

tests verify the interactions between things: did we call

shutil.copy with the right arguments? This coupling

between code and test tends to make tests more brittle, in our

experience.

Overuse of mocks leads to complicated test suites that fail to

explain the code.

NOT E



Designing for testability really means designing for extensibility. We trade off a

little more complexity for a cleaner design that admits novel use cases.



MOCKS VERSUS FAKES; CLASSIC-STYLE VERSUS LONDON-

SCHOOL TDD



Here’s a short and somewhat simplistic definition of the difference between mocks and fakes:

Mocks are used to verify how something gets used; they have methods like

assert\_called\_once\_with(). They’re associated with London-school TDD.

Fakes are working implementations of the thing they’re replacing, but they’re designed

for use only in tests. They wouldn’t work “in real life”; our in-memory repository is a

good example. But you can use them to make assertions about the end state of a

system rather than the behaviors along the way, so they’re associated with classic-style

TDD.

We’re slightly conflating mocks with spies and fakes with stubs here, and you can read the long,

correct answer in Martin Fowler’s classic essay on the subject called“Mocks Aren’t Stubs”.

It also probably doesn’t help that the MagicMock objects provided by unittest.mock aren’t, strictly

speaking, mocks; they’re spies, if anything. But they’re also often used as stubs or dummies.

There, we promise we’re done with the test double terminology nitpicks now.

What about London-school versus classic-style TDD? You can read more about those two in

Martin Fowler’s article that we just cited, as well as on theSoftware Engineering Stack Exchange

site, but in this book we’re pretty firmly in the classicist camp. We like to build our tests around

state both in setup and in assertions, and we like to work at the highest level of abstraction

possible rather than doing checks on the behavior of intermediary collaborators.

Read more on this in“On Deciding What Kind of Tests to Write”.



We view TDD as a design practice first and a testing practice second.

The tests act as a record of our design choices and serve to explain the

system to us when we return to the code after a long absence.

Tests that use too many mocks get overwhelmed with setup code that

hides the story we care about.



3



Steve Freeman has a great example of overmocked tests in his talk

“Test-Driven Development”. You should also check out this PyCon

talk,“Mocking and Patching Pitfalls”, by our esteemed tech reviewer,

Ed Jung, which also addresses mocking and its alternatives. And while

we’re recommending talks, don’t miss Brandon Rhodes talking about

“Hoisting Your I/O”, which really nicely covers the issues we’re

talking about, using another simple example.

T IP



In this chapter, we’ve spent a lot of time replacing end-to-end tests with unit tests.

That doesn’t mean we think you should never use E2E tests! In this book we’re

showing techniques to get you to a decent test pyramid with as many unit tests as

possible, and with the minimum number of E2E tests you need to feel confident.

Read on to“Recap: Rules of Thumb for Different Types of Test”for more

details.



SO WHICH DO WE USE IN THIS BOOK? FUNCTIONAL OR

OBJECT-ORIENTED COMPOSITION?



Both. Our domain model is entirely free of dependencies and side effects, so that’s our functional

core. The service layer that we build around it (inChapter 4) allows us to drive the system edge to

edge, and we use dependency injection to provide those services with stateful components, so

we can still unit test them.

SeeChapter 13for more exploration of making our dependency injection more explicit and

centralized.



Wrap-Up

We’ll see this idea come up again and again in the book: we can make

our systems easier to test and maintain by simplifying the interface

between our business logic and messy I/O. Finding the right

abstraction is tricky, but here are a few heuristics and questions to ask

yourself:

Can I choose a familiar Python data structure to represent the

state of the messy system and then try to imagine a single

function that can return that state?

Where can I draw a line between my systems, where can I

carve out aseamto stick that abstraction in?

What is a sensible way of dividing things into components

with different responsibilities? What implicit concepts can I

make explicit?

What are the dependencies, and what is the core business

logic?

Practice makes less imperfect! And now back to our regular

programming...



1 A code kata is a small, contained programming challenge often used to practice TDD.

See“Kata—The Only Way to Learn TDD”by Peter Provost.



2 If you’re used to thinking in terms of interfaces, that’s what we’re trying to define here.



3 Which is not to say that we think the London school people are wrong. Some insanely

smart people work that way. It’s just not what we’re used to.



Chapter 4. Our First Use

Case: Flask API and Service

Layer

Back to our allocations project!Figure 4-1shows the point we

reached at the end ofChapter 2, which covered the Repository pattern.



Figure 4-1. Before: we drive our app by talking to repositories and

the domain model

In this chapter, we discuss the differences between orchestration logic,

business logic, and interfacing code, and we introduce the Service

Layer pattern to take care of orchestrating our workflows and defining

the use cases of our system.

We’ll also discuss testing: by combining the Service Layer with our

repository abstraction over the database, we’re able to write fast tests,

not just of our domain model but of the entire workflow for a use case.

Figure 4-2shows what we’re aiming for: we’re going to add a Flask

API that will talk to the service layer, which will serve as the

entrypoint to our domain model. Because our service layer depends on

the AbstractRepository, we can unit test it by using

FakeRepository but run our production code using

SqlAlchemyRepository.



Figure 4-2. The service layer will become the main way into our app



In our diagrams, we are using the convention that new components are

highlighted with bold text/lines (and yellow/orange color, if you’re

reading a digital version).

T IP



The code for this chapter is in the chapter\_04\_service\_layer branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_04\_service\_layer

\# or to code along, checkout Chapter 2:

git checkout chapter\_02\_repository



Connecting Our Application to the Real

World

Like any good agile team, we’re hustling to try to get an MVP out and

in front of the users to start gathering feedback. We have the core of

our domain model and the domain service we need to allocate orders,

and we have the repository interface for permanent storage.

Let’s plug all the moving parts together as quickly as we can and then

refactor toward a cleaner architecture. Here’s our plan:

1\. Use Flask to put an API endpoint in front of our allocate

domain service. Wire up the database session and our

repository. Test it with an end-to-end test and some quick-

and-dirty SQL to prepare test data.

2\. Refactor out a service layer that can serve as an abstraction to

capture the use case and that will sit between Flask and our

domain model. Build some service-layer tests and show how

they can use FakeRepository.

3\. Experiment with different types of parameters for our service

layer functions; show that using primitive data types allows

the service layer’s clients (our tests and our Flask API) to be

decoupled from the model layer.

A First End-to-End Test

No one is interested in getting into a long terminology debate about

what counts as an end-to-end (E2E) test versus a functional test versus

an acceptance test versus an integration test versus a unit test. Different

projects need different combinations of tests, and we’ve seen perfectly

successful projects just split things into “fast tests” and “slow tests.”

For now, we want to write one or maybe two tests that are going to

exercise a “real” API endpoint (using HTTP) and talk to a real

database. Let’s call them end-to-end tests because it’s one of the most

self-explanatory names.

The following shows a first cut:

A first API test (test\_api.py)



@pytest.mark.usefixtures('restart\_api')

def test\_api\_returns\_allocation(add\_stock):

sku,othersku=random\_sku(),random\_sku('other')

earlybatch=random\_batchref( 1 )

laterbatch=random\_batchref( 2 )

otherbatch=random\_batchref( 3 )



add\_stock(\[

(laterbatch,sku, 100 ,'2011-01-02'),

(earlybatch,sku, 100 ,'2011-01-01'),

(otherbatch,othersku, 100 ,None),

])

data={'orderid':random\_orderid(),'sku':sku,'qty': 3 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 201

assert r.json()\['batchref']==earlybatch



random\_sku(), random\_batchref(), and so on are little helper

functions that generate randomized characters by using the uuid

module. Because we’re running against an actual database now,

this is one way to prevent various tests and runs from interfering

with each other.

add\_stock is a helper fixture that just hides away the details of

manually inserting rows into the database using SQL. We’ll show a

nicer way of doing this later in the chapter.

config.py is a module in which we keep configuration information.

Everyone solves these problems in different ways, but you’re going to

need some way of spinning up Flask, possibly in a container, and of

talking to a Postgres database. If you want to see how we did it, check

outAppendix B.

The Straightforward Implementation

Implementing things in the most obvious way, you might get something

like this:

First cut of Flask app (flask\_app.py)



fromflaskimport Flask,jsonify,request

fromsqlalchemyimport create\_engine

fromsqlalchemy.ormimport sessionmaker



importconfig

importmodel

importorm

importrepository



orm.start\_mappers()

get\_session=sessionmaker(bind=create\_engine(config.get\_postgres\_uri()))

app=Flask(name)



@app.route("/allocate",methods=\['POST'])

def allocate\_endpoint():

session=get\_session()

batches=repository.SqlAlchemyRepository(session).list()

line=model.OrderLine(

request.json\['orderid'],

request.json\['sku'],

request.json\['qty'],

)



batchref=model.allocate(line,batches)



return jsonify({'batchref':batchref}), 201



So far, so good. No need for too much more of your “architecture

astronaut” nonsense, Bob and Harry, you may be thinking.

But hang on a minute—there’s no commit. We’re not actually saving

our allocation to the database. Now we need a second test, either one

that will inspect the database state after (not very black-boxy), or

maybe one that checks that we can’t allocate a second line if a first

should have already depleted the batch:

Test allocations are persisted (test\_api.py)



@pytest.mark.usefixtures('restart\_api')

def test\_allocations\_are\_persisted(add\_stock):

sku=random\_sku()

batch1,batch2=random\_batchref( 1 ),random\_batchref( 2 )

order1,order2=random\_orderid( 1 ),random\_orderid( 2 )

add\_stock(\[

(batch1,sku, 10 ,'2011-01-01'),

(batch2,sku, 10 ,'2011-01-02'),

])

line1={'orderid':order1,'sku':sku,'qty': 10 }

line2={'orderid':order2,'sku':sku,'qty': 10 }

url=config.get\_api\_url()



\# first order uses up all stock in batch 1

r=requests.post(f'{url}/allocate',json=line1)

assert r.status\_code== 201

assert r.json()\['batchref']==batch1



\# second order should go to batch 2

r=requests.post(f'{url}/allocate',json=line2)

assert r.status\_code== 201

assert r.json()\['batchref']==batch2



Not quite so lovely, but that will force us to add the commit.

Error Conditions That Require Database

Checks

If we keep going like this, though, things are going to get uglier and

uglier.

Suppose we want to add a bit of error handling. What if the domain

raises an error, for a SKU that’s out of stock? Or what about a SKU

that doesn’t even exist? That’s not something the domain even knows

about, nor should it. It’s more of a sanity check that we should

implement at the database layer, before we even invoke the domain

service.

Now we’re looking at two more end-to-end tests:

Yet more tests at the E2E layer (test\_api.py)



@pytest.mark.usefixtures('restart\_api')

def test\_400\_message\_for\_out\_of\_stock(add\_stock):

sku,smalL\_batch,large\_order=random\_sku(),random\_batchref(),

random\_orderid()

add\_stock(\[

(smalL\_batch,sku, 10 ,'2011-01-01'),

])

data={'orderid':large\_order,'sku':sku,'qty': 20 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 400

assert r.json()\['message']==f'Out of stock for sku {sku}'



@pytest.mark.usefixtures('restart\_api')

def test\_400\_message\_for\_invalid\_sku():

unknown\_sku,orderid=random\_sku(),random\_orderid()

data={'orderid':orderid,'sku':unknown\_sku,'qty': 20 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 400

assert r.json()\['message']==f'Invalid sku {unknown\_sku}'

In the first test, we’re trying to allocate more units than we have in

stock.

In the second, the SKU just doesn’t exist (because we never called

add\_stock), so it’s invalid as far as our app is concerned.

And sure, we could implement it in the Flask app too:

Flask app starting to get crufty (flask\_app.py)



def is\_valid\_sku(sku,batches):

return sku in {b.sku for b in batches}



@app.route("/allocate",methods=\['POST'])

def allocate\_endpoint():

session=get\_session()

batches=repository.SqlAlchemyRepository(session).list()

line=model.OrderLine(

request.json\['orderid'],

request.json\['sku'],

request.json\['qty'],

)



ifnot is\_valid\_sku(line.sku,batches):

return jsonify({'message':f'Invalid sku {line.sku}'}), 400



try :

batchref=model.allocate(line,batches)

except model.OutOfStock as e:

return jsonify({'message':str(e)}), 400



session.commit()

return jsonify({'batchref':batchref}), 201



But our Flask app is starting to look a bit unwieldy. And our number of

E2E tests is starting to get out of control, and soon we’ll end up with

an inverted test pyramid (or “ice-cream cone model,” as Bob likes to

call it).

Introducing a Service Layer, and Using

FakeRepository to Unit Test It

If we look at what our Flask app is doing, there’s quite a lot of what

we might call orchestration —fetching stuff out of our repository,

validating our input against database state, handling errors, and

committing in the happy path. Most of these things don’t have anything

to do with having a web API endpoint (you’d need them if you were

building a CLI, for example; seeAppendix C), and they’re not really

things that need to be tested by end-to-end tests.

It often makes sense to split out a service layer, sometimes called an

orchestration layer or a use-case layer.

Do you remember the FakeRepository that we prepared in

Chapter 3?

Our fake repository, an in-memory collection of batches

(test\_services.py)



classFakeRepository (repository.AbstractRepository):



def \_\_init\_\_(self,batches):

self.\_batches=set(batches)



def add(self,batch):

self.\_batches.add(batch)



def get(self,reference):

return next(b for b in self.\_batches if b.reference==reference)



def list(self):

return list(self.\_batches)



Here’s where it will come in useful; it lets us test our service layer

with nice, fast unit tests:

Unit testing with fakes at the service layer (test\_services.py)



def test\_returns\_allocation():

line=model.OrderLine("o1","COMPLICATED-LAMP", 10 )

batch=model.Batch("b1","COMPLICATED-LAMP", 100 ,eta=None)

repo=FakeRepository(\[batch])



result=services.allocate(line,repo,FakeSession())

assert result=="b1"



def test\_error\_for\_invalid\_sku():

line=model.OrderLine("o1","NONEXISTENTSKU", 10 )

batch=model.Batch("b1","AREALSKU", 100 ,eta=None)

repo=FakeRepository(\[batch])



with pytest.raises(services.InvalidSku,match="Invalid sku NONEXISTENTSKU"):

services.allocate(line,repo,FakeSession())



FakeRepository holds the Batch objects that will be used by our

test.

Our services module ( services.py ) will define an allocate()

service-layer function. It will sit between our

allocate\_endpoint() function in the API layer and the

allocate() domain service function from our domain model.

We also need a FakeSession to fake out the database session, as

shown in the following code snippet.

A fake database session (test\_services.py)



classFakeSession ():

committed=False



def commit(self):

self.committed=True



This fake session is only a temporary solution. We’ll get rid of it and

make things even nicer soon, inChapter 6. But in the meantime the fake

1

.commit() lets us migrate a third test from the E2E layer:

A second test at the service layer (test\_services.py)



def test\_commits():

line=model.OrderLine('o1','OMINOUS-MIRROR', 10 )

batch=model.Batch('b1','OMINOUS-MIRROR', 100 ,eta=None)

repo=FakeRepository(\[batch])

session=FakeSession()



services.allocate(line,repo,session)

assert session.committed is True



A Typical Service Function

We’ll write a service function that looks something like this:

Basic allocation service (services.py)



classInvalidSku ( Exception ):

pass



def is\_valid\_sku(sku,batches):

return sku in {b.sku for b in batches}



def allocate(line:OrderLine,repo:AbstractRepository,session)->str:

batches=repo.list()

ifnot is\_valid\_sku(line.sku,batches):

raise InvalidSku(f'Invalid sku {line.sku}')

batchref=model.allocate(line,batches)

session.commit()

return batchref

Typical service-layer functions have similar steps:

We fetch some objects from the repository.

We make some checks or assertions about the request against the

current state of the world.

We call a domain service.

If all is well, we save/update any state we’ve changed.

That last step is a little unsatisfactory at the moment, as our service

layer is tightly coupled to our database layer. We’ll improve that in

Chapter 6with the Unit of Work pattern.

DEPEND ON ABSTRACTIONS



Notice one more thing about our service-layer function:



def allocate(line:OrderLine,repo:AbstractRepository,session)->str:



It depends on a repository. We’ve chosen to make the dependency explicit, and we’ve used the

type hint to say that we depend on AbstractRepository. This means it’ll work both when the tests

give it a FakeRepository and when the Flask app gives it a SqlAlchemyRepository.

If you remember“The Dependency Inversion Principle”, this is what we mean when we say we

should “depend on abstractions.” Our high-level m odule , the service layer, depends on the

repository abstraction.And the details of the implementation for our specific choice of persistent

storage also depend on that same abstraction. See Figures4-3and4-4.



See also inAppendix Ca worked example of swapping out the details of which persistent

storage system to use while leaving the abstractions intact.



But the essentials of the service layer are there, and our Flask app now

looks a lot cleaner:

Flask app delegating to service layer (flask\_app.py)



@app.route("/allocate",methods=\['POST'])

def allocate\_endpoint():

session=get\_session()

repo=repository.SqlAlchemyRepository(session)



line=model.OrderLine(

request.json\['orderid'],

request.json\['sku'],

request.json\['qty'],

)

try :

batchref=services.allocate(line,repo,session)

except (model.OutOfStock,services.InvalidSku) as e:

return jsonify({'message':str(e)}), 400



return jsonify({'batchref':batchref}), 201



We instantiate a database session and some repository objects.

We extract the user’s commands from the web request and pass

them to a domain service.

We return some JSON responses with the appropriate status codes.

The responsibilities of the Flask app are just standard web stuff: per-

request session management, parsing information out of POST

parameters, response status codes, and JSON. All the orchestration

logic is in the use case/service layer, and the domain logic stays in the

domain.

Finally, we can confidently strip down our E2E tests to just two, one

for the happy path and one for the unhappy path:

E2E tests only happy and unhappy paths (test\_api.py)



@pytest.mark.usefixtures('restart\_api')

def test\_happy\_path\_returns\_201\_and\_allocated\_batch(add\_stock):

sku,othersku=random\_sku(),random\_sku('other')

earlybatch=random\_batchref( 1 )

laterbatch=random\_batchref( 2 )

otherbatch=random\_batchref( 3 )



add\_stock(\[

(laterbatch,sku, 100 ,'2011-01-02'),

(earlybatch,sku, 100 ,'2011-01-01'),

(otherbatch,othersku, 100 ,None),

])

data={'orderid':random\_orderid(),'sku':sku,'qty': 3 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 201

assert r.json()\['batchref']==earlybatch



@pytest.mark.usefixtures('restart\_api')

def test\_unhappy\_path\_returns\_400\_and\_error\_message():

unknown\_sku,orderid=random\_sku(),random\_orderid()

data={'orderid':orderid,'sku':unknown\_sku,'qty': 20 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 400

assert r.json()\['message']==f'Invalid sku {unknown\_sku}'

We’ve successfully split our tests into two broad categories: tests

about web stuff, which we implement end to end; and tests about

orchestration stuff, which we can test against the service layer in

memory.

EXERCISE FOR THE READER



Now that we have an allocate service, why not build out a service for deallocate? We’ve addedan

E2E test and a few stub service-layer testsfor you to get started on GitHub.

If that’s not enough, continue into the E2E tests and flask \_app.py , and refactor the Flask adapter

to be more RESTful. Notice how doing so doesn’t require any change to our service layer or

domain layer!



TIP



If you decide you want to build a read-only endpoint for retrieving allocation info,

just do “the simplest thing that can possibly work,” which is repo.get() right in

the Flask handler. We’ll talk more about reads versus writes inChapter 12.



Why Is Everything Called a Service?

Some of you are probably scratching your heads at this point trying to

figure out exactly what the difference is between a domain service and

a service layer.

We’re sorry—we didn’t choose the names, or we’d have much cooler

and friendlier ways to talk about this stuff.

We’re using two things called a service in this chapter. The first is an

application service (our service layer). Its job is to handle requests

from the outside world and to orchestrate an operation. What we mean

is that the service layer drives the application by following a bunch of

simple steps:

Get some data from the database

Update the domain model

Persist any changes

This is the kind of boring work that has to happen for every operation

in your system, and keeping it separate from business logic helps to

keep things tidy.

The second type of service is a domain service. This is the name for a

piece of logic that belongs in the domain model but doesn’t sit

naturally inside a stateful entity or value object. For example, if you

were building a shopping cart application, you might choose to build

taxation rules as a domain service. Calculating tax is a separate job

from updating the cart, and it’s an important part of the model, but it

doesn’t seem right to have a persisted entity for the job. Instead a

stateless TaxCalculator class or a calculate\_tax function can do the

job.

Putting Things in Folders to See Where It

All Belongs

As our application gets bigger, we’ll need to keep tidying our

directory structure. The layout of our project gives us useful hints

about what kinds of object we’ll find in each file.

Here’s one way we could organize things:

Some subfolders

.



├── config.py

├── domain

│ ├── init.py

│ └── model.py



├── service\_layer

│ ├── init.py

│ └── services.py

├── adapters

│ ├── init.py

│ ├── orm.py

│ └── repository.py

├── entrypoints

│ ├── init.py

│ └── flask\_app.py

└── tests

├── init.py

├── conftest.py

├── unit

│ ├── test\_allocate.py

│ ├── test\_batches.py

│ └── test\_services.py

├── integration

│ ├── test\_orm.py

│ └── test\_repository.py

└── e2e

└── test\_api.py

Let’s have a folder for our domain model. Currently that’s just one

file, but for a more complex application, you might have one file

per class; you might have helper parent classes for Entity,

ValueObject, and Aggregate, and you might add an

exceptions.py for domain-layer exceptions and, as you’ll see in

Part II, commands.py and events.py.

We’ll distinguish the service layer. Currently that’s just one file

called services.py for our service-layer functions. You could add

service-layer exceptions here, and as you’ll see inChapter 5,

we’ll add unit\_of\_work.py.

Adapters is a nod to the ports and adapters terminology. This will

fill up with any other abstractions around external I/O (e.g., a

redis\_client.py ). Strictly speaking, you would call these secondary

adapters or driven adapters, or sometimes inward-facing adapters.

Entrypoints are the places we drive our application from. In the

official ports and adapters terminology, these are adapters too, and

are referred to as primary , driving , or outward-facing adapters.

What about ports? As you may remember, they are the abstract

interfaces that the adapters implement. We tend to keep them in the

same file as the adapters that implement them.

Wrap-Up

Adding the service layer has really bought us quite a lot:

Our Flask API endpoints become very thin and easy to write:

their only responsibility is doing “web stuff,” such as parsing

JSON and producing the right HTTP codes for happy or

unhappy cases.

We’ve defined a clear API for our domain, a set of use cases

or entrypoints that can be used by any adapter without needing

to know anything about our domain model classes—whether

that’s an API, a CLI (seeAppendix C), or the tests! They’re

an adapter for our domain too.

We can write tests in “high gear” by using the service layer,

leaving us free to refactor the domain model in any way we

see fit. As long as we can still deliver the same use cases, we

can experiment with new designs without needing to rewrite a

load of tests.

And our test pyramid is looking good—the bulk of our tests

are fast unit tests, with just the bare minimum of E2E and

integration tests.

The DIP in Action

Figure 4-3shows the dependencies of our service layer: the domain

model and AbstractRepository (the port, in ports and adapters

terminology).

When we run the tests,Figure 4-4shows how we implement the

abstract dependencies by using FakeRepository (the adapter).

And when we actually run our app, we swap in the “real” dependency

shown inFigure 4-5.



Figure 4-3. Abstract dependencies of the service layer



Figure 4-4. Tests provide an implementation of the abstract

dependency



Figure 4-5. Dependencies at runtime



Wonderful.

Let’s pause forTable 4-1, in which we consider the pros and cons of

having a service layer at all.

Table 4-1. Service layer: the trade-offs



Pros Cons



Pros Cons



We have a single place to

capture all the use cases for our

application.



We’ve placed our clever domain

logic behind an API, which

leaves us free to

refactor.



We have cleanly separated

“stuff that talks HTTP” from

“stuff that talks

allocation.”



When combined with the

Repository pattern and FakeRep

ository, we have

a nice way of writing tests at a

higher level than the domain

layer;

we can test more of our

workflow without needing to

use integration tests

(read on toChapter 5for more

elaboration on this).



If your app is purely a web

app, your controllers/view

functions can be

the single place to capture all

the use cases.



It’s yet another layer of

abstraction.



Putting too much logic into the

service layer can lead to the

Anemic Domain

anti-pattern. It’s better to

introduce this layer after you

spot orchestration

logic creeping into your

controllers.



You can get a lot of the benefits

that come from having rich

domain models

by simply pushing logic out of

your controllers and down to

the model layer,

without needing to add an extra

layer in between (aka “fat

models, thin

controllers”).



But there are still some bits of awkwardness to tidy up:

The service layer is still tightly coupled to the domain,

because its API is expressed in terms of OrderLine objects.

InChapter 5, we’ll fix that and talk about the way that the

service layer enables more productive TDD.

The service layer is tightly coupled to a session object. In

Chapter 6, we’ll introduce one more pattern that works

closely with the Repository and Service Layer patterns, the

Unit of Work pattern, and everything will be absolutely

lovely. You’ll see!



1 Service-layer services and domain services do have confusingly similar names. We

tackle this topic later in“Why Is Everything Called a Service?”.



Chapter 5. TDD in High Gear

and Low Gear

We’ve introduced the service layer to capture some of the additional

orchestration responsibilities we need from a working application.

The service layer helps us clearly define our use cases and the

workflow for each: what we need to get from our repositories, what

pre-checks and current state validation we should do, and what we

save at the end.

But currently, many of our unit tests operate at a lower level, acting

directly on the model. In this chapter we’ll discuss the trade-offs

involved in moving those tests up to the service-layer level, and some

more general testing guidelines.

HARRY SAYS: SEEING A TEST PYRAMID IN ACTION WAS A LIGHT-

BULB MOMENT



Here are a few words from Harry directly:

I was initially sk eptical of all Bob ’s architectural patterns, b ut seeing an actual test pyram id m ade

m e a convert.

Once you im plem ent dom ain m odeling and the service layer, you really actually can get to a

stage where unit tests outnum b er integration and end-to-end tests b y an order of m agnitude.

Having work ed in places where the E2E test b uild would tak e hours (“wait ‘til tom orrow,”

essentially), I can’t tell you what a difference it m ak es to b e ab le to run all your tests in m inutes or

seconds.

Read on for som e guidelines on how to decide what k inds of tests to write and at which level. The

high gear versus low gear way of think ing really changed m y testing life.



How Is Our Test Pyramid Looking?

Let’s see what this move to using a service layer, with its own service-

layer tests, does to our test pyramid:

Counting types of tests



$grep -c test\_ test\_\*.py

tests/unit/test\_allocate.py:4

tests/unit/test\_batches.py:8

tests/unit/test\_services.py:3



tests/integration/test\_orm.py:6

tests/integration/test\_repository.py:2



tests/e2e/test\_api.py:2

Not bad! We have 15 unit tests, 8 integration tests, and just 2 end-to-

end tests. That’s already a healthy-looking test pyramid.

Should Domain Layer Tests Move to the

Service Layer?

Let’s see what happens if we take this a step further. Since we can test

our software against the service layer, we don’t really need tests for

the domain model anymore. Instead, we could rewrite all of the

domain-level tests fromChapter 1in terms of the service layer:

Rewriting a domain test at the service layer

(tests/unit/test\_services.py)



\# domain-layer test:

def test\_prefers\_current\_stock\_batches\_to\_shipments():

in\_stock\_batch=Batch("in-stock-batch","RETRO-CLOCK", 100 ,eta=None)

shipment\_batch=Batch("shipment-batch","RETRO-CLOCK", 100 ,eta=tomorrow)



line=OrderLine("oref","RETRO-CLOCK", 10 )



allocate(line, \[in\_stock\_batch,shipment\_batch])



assert in\_stock\_batch.available\_quantity== 90

assert shipment\_batch.available\_quantity== 100



\# service-layer test:

def test\_prefers\_warehouse\_batches\_to\_shipments():

in\_stock\_batch=Batch("in-stock-batch","RETRO-CLOCK", 100 ,eta=None)

shipment\_batch=Batch("shipment-batch","RETRO-CLOCK", 100 ,eta=tomorrow)

repo=FakeRepository(\[in\_stock\_batch,shipment\_batch])

session=FakeSession()



line=OrderLine('oref',"RETRO-CLOCK", 10 )



services.allocate(line,repo,session)



assert in\_stock\_batch.available\_quantity== 90

assert shipment\_batch.available\_quantity== 100



Why would we want to do that?

Tests are supposed to help us change our system fearlessly, but often

we see teams writing too many tests against their domain model. This

causes problems when they come to change their codebase and find

that they need to update tens or even hundreds of unit tests.

This makes sense if you stop to think about the purpose of automated

tests. We use tests to enforce that a property of the system doesn’t

change while we’re working. We use tests to check that the API

continues to return 200, that the database session continues to commit,

and that orders are still being allocated.

If we accidentally change one of those behaviors, our tests will break.

The flip side, though, is that if we want to change the design of our

code, any tests relying directly on that code will also fail.

As we get further into the book, you’ll see how the service layer forms

an API for our system that we can drive in multiple ways. Testing

against this API reduces the amount of code that we need to change

when we refactor our domain model. If we restrict ourselves to testing

only against the service layer, we won’t have any tests that directly

interact with “private” methods or attributes on our model objects,

which leaves us freer to refactor them.

T IP



Every line of code that we put in a test is like a blob of glue, holding the system in

a particular shape. The more low-level tests we have, the harder it will be to

change things.



On Deciding What Kind of Tests to Write

You might be asking yourself, “Should I rewrite all my unit tests, then?

Is it wrong to write tests against the domain model?” To answer those

questions, it’s important to understand the trade-off between coupling

and design feedback (seeFigure 5-1).



Figure 5-1. The test spectrum



Extreme programming (XP) exhorts us to “listen to the code.” When

we’re writing tests, we might find that the code is hard to use or notice

a code smell. This is a trigger for us to refactor, and to reconsider our

design.

We only get that feedback, though, when we’re working closely with

the target code. A test for the HTTP API tells us nothing about the fine-

grained design of our objects, because it sits at a much higher level of

abstraction.

On the other hand, we can rewrite our entire application and, so long

as we don’t change the URLs or request formats, our HTTP tests will

continue to pass. This gives us confidence that large-scale changes,

like changing the database schema, haven’t broken our code.

At the other end of the spectrum, the tests we wrote inChapter 1

helped us to flesh out our understanding of the objects we need. The

tests guided us to a design that makes sense and reads in the domain

language. When our tests read in the domain language, we feel

comfortable that our code matches our intuition about the problem

we’re trying to solve.

Because the tests are written in the domain language, they act as living

documentation for our model. A new team member can read these tests

to quickly understand how the system works and how the core

concepts interrelate.

We often “sketch” new behaviors by writing tests at this level to see

how the code might look. When we want to improve the design of the

code, though, we will need to replace or delete these tests, because

they are tightly coupled to a particular implementation.

High and Low Gear

Most of the time, when we are adding a new feature or fixing a bug,

we don’t need to make extensive changes to the domain model. In these

cases, we prefer to write tests against services because of the lower

coupling and higher coverage.

For example, when writing an add\_stock function or a cancel\_order

feature, we can work more quickly and with less coupling by writing

tests against the service layer.

When starting a new project or when hitting a particularly gnarly

problem, we will drop back down to writing tests against the domain

model so we get better feedback and executable documentation of our

intent.

The metaphor we use is that of shifting gears. When starting a journey,

the bicycle needs to be in a low gear so that it can overcome inertia.

Once we’re off and running, we can go faster and more efficiently by

changing into a high gear; but if we suddenly encounter a steep hill or

are forced to slow down by a hazard, we again drop down to a low

gear until we can pick up speed again.

Fully Decoupling the Service-Layer Tests

from the Domain

We still have direct dependencies on the domain in our service-layer

tests, because we use domain objects to set up our test data and to

invoke our service-layer functions.

To have a service layer that’s fully decoupled from the domain, we

need to rewrite its API to work in terms of primitives.

Our service layer currently takes an OrderLine domain object:

Before: allocate takes a domain object (service\_layer/services.py)



def allocate(line:OrderLine,repo:AbstractRepository,session)->str:

How would it look if its parameters were all primitive types?

After: allocate takes strings and ints (service\_layer/services.py)



def allocate(

orderid:str,sku:str,qty:int,repo:AbstractRepository,session

)->str:

We rewrite the tests in those terms as well:

Tests now use primitives in function call (tests/unit/test\_services.py)



def test\_returns\_allocation():

batch=model.Batch("batch1","COMPLICATED-LAMP", 100 ,eta=None)

repo=FakeRepository(\[batch])



result=services.allocate("o1","COMPLICATED-LAMP", 10 ,repo,

FakeSession())

assert result=="batch1"

But our tests still depend on the domain, because we still manually

instantiate Batch objects. So, if one day we decide to massively

refactor how our Batch model works, we’ll have to change a bunch of

tests.

Mitigation: Keep All Domain Dependencies in

Fixture Functions

We could at least abstract that out to a helper function or a fixture in

our tests. Here’s one way you could do that, adding a factory function

on FakeRepository:

Factory functions for fixtures are one possibility

(tests/unit/test\_services.py)



classFakeRepository (set):



@staticmethod

def for\_batch(ref,sku,qty,eta=None):

return FakeRepository(\[

model.Batch(ref,sku,qty,eta),

])



...



def test\_returns\_allocation():

repo=FakeRepository.for\_batch("batch1","COMPLICATED-LAMP", 100 ,eta=None)

result=services.allocate("o1","COMPLICATED-LAMP", 10 ,repo,

FakeSession())

assert result=="batch1"

At least that would move all of our tests’ dependencies on the domain

into one place.

Adding a Missing Service

We could go one step further, though. If we had a service to add stock,

we could use that and make our service-layer tests fully expressed in

terms of the service layer’s official use cases, removing all

dependencies on the domain:

Test for new add\_batch service (tests/unit/test\_services.py)



def test\_add\_batch():

repo,session=FakeRepository(\[]),FakeSession()

services.add\_batch("b1","CRUNCHY-ARMCHAIR", 100 ,None,repo,session)

assert repo.get("b1") is not None

assert session.committed

T IP



In general, if you find yourself needing to do domain-layer stuff directly in your

service-layer tests, it may be an indication that your service layer is incomplete.



And the implementation is just two lines:

A new service for add\_batch (service\_layer/services.py)



def add\_batch(

ref:str,sku:str,qty:int,eta:Optional\[date],

repo:AbstractRepository,session,

):

repo.add(model.Batch(ref,sku,qty,eta))

session.commit()



def allocate(

orderid:str,sku:str,qty:int,repo:AbstractRepository,session

)->str:

...

NOT E



Should you write a new service just because it would help remove dependencies

from your tests? Probably not. But in this case, we almost definitely would need

an add\_batch service one day anyway.



That now allows us to rewrite all of our service-layer tests purely in

terms of the services themselves, using only primitives, and without

any dependencies on the model:

Services tests now use only services (tests/unit/test\_services.py)



def test\_allocate\_returns\_allocation():

repo,session=FakeRepository(\[]),FakeSession()

services.add\_batch("batch1","COMPLICATED-LAMP", 100 ,None,repo,session)

result=services.allocate("o1","COMPLICATED-LAMP", 10 ,repo,session)

assert result=="batch1"



def test\_allocate\_errors\_for\_invalid\_sku():



repo,session=FakeRepository(\[]),FakeSession()

services.add\_batch("b1","AREALSKU", 100 ,None,repo,session)



with pytest.raises(services.InvalidSku,match="Invalid sku NONEXISTENTSKU"):

services.allocate("o1","NONEXISTENTSKU", 10 ,repo,FakeSession())



This is a really nice place to be in. Our service-layer tests depend on

only the service layer itself, leaving us completely free to refactor the

model as we see fit.

Carrying the Improvement Through to the

E2E Tests

In the same way that adding add\_batch helped decouple our service-

layer tests from the model, adding an API endpoint to add a batch

would remove the need for the ugly add\_stock fixture, and our E2E

tests could be free of those hardcoded SQL queries and the direct

dependency on the database.

Thanks to our service function, adding the endpoint is easy, with just a

little JSON wrangling and a single function call required:

API for adding a batch (entrypoints/flask\_app.py)



@app.route("/add\_batch",methods=\['POST'])

def add\_batch():

session=get\_session()

repo=repository.SqlAlchemyRepository(session)

eta=request.json\['eta']

if eta is not None:

eta=datetime.fromisoformat(eta).date()

services.add\_batch(

request.json\['ref'],request.json\['sku'],request.json\['qty'],eta,



repo,session

)

return 'OK', 201



NOT E



Are you thinking to yourself, POST to /add\_batch? That’s not very RESTful!

You’re quite right. We’re being happily sloppy, but if you’d like to make it all more

RESTy, maybe a POST to /batches , then knock yourself out! Because Flask is a

thin adapter, it’ll be easy. Seethe next sidebar.



And our hardcoded SQL queries from conftest.py get replaced with

some API calls, meaning the API tests have no dependencies other than

the API, which is also nice:

API tests can now add their own batches (tests/e2e/test\_api.py)



def post\_to\_add\_batch(ref,sku,qty,eta):

url=config.get\_api\_url()

r=requests.post(

f'{url}/add\_batch',

json={'ref':ref,'sku':sku,'qty':qty,'eta':eta}

)

assert r.status\_code== 201



@pytest.mark.usefixtures('postgres\_db')

@pytest.mark.usefixtures('restart\_api')

def test\_happy\_path\_returns\_201\_and\_allocated\_batch():

sku,othersku=random\_sku(),random\_sku('other')

earlybatch=random\_batchref( 1 )

laterbatch=random\_batchref( 2 )

otherbatch=random\_batchref( 3 )

post\_to\_add\_batch(laterbatch,sku, 100 ,'2011-01-02')

post\_to\_add\_batch(earlybatch,sku, 100 ,'2011-01-01')



post\_to\_add\_batch(otherbatch,othersku, 100 ,None)

data={'orderid':random\_orderid(),'sku':sku,'qty': 3 }

url=config.get\_api\_url()

r=requests.post(f'{url}/allocate',json=data)

assert r.status\_code== 201

assert r.json()\['batchref']==earlybatch



Wrap-Up

Once you have a service layer in place, you really can move the

majority of your test coverage to unit tests and develop a healthy test

pyramid.

RECAP: RULES OF THUMB FOR DIFFERENT TYPES OF TEST



Aim for one end-to-end test per feature

This might be written against an HTTP API, for example. The objective is to demonstrate that

the feature works, and that all the moving parts are glued together correctly.



Write the bulk of your tests against the service layer

These edge-to-edge tests offer a good trade-off between coverage, runtime, and efficiency.

Each test tends to cover one code path of a feature and use fakes for I/O. This is the place to

exhaustively cover all the edge cases and the ins and outs of your business logic.



Maintain a small core of tests written against your domain model

These tests have highly focused coverage and are more brittle, but they have the highest

feedback. Don’t be afraid to delete these tests if the functionality is later covered by tests at

the service layer.



Error handling counts as a feature

Ideally, your application will be structured such that all errors that bubble up to your

entrypoints (e.g., Flask) are handled in the same way. This means you need to test only the

happy path for each feature, and to reserve one end-to-end test for all unhappy paths (and

many unhappy path unit tests, of course).



A few things will help along the way:



1



Express your service layer in terms of primitives rather than

domain objects.

In an ideal world, you’ll have all the services you need to be

able to test entirely against the service layer, rather than

hacking state via repositories or the database. This pays off in

your end-to-end tests as well.

Onto the next chapter!



1 A valid concern about writing tests at a higher level is that it can lead to combinatorial

explosion for more complex use cases. In these cases, dropping down to lower-level unit

tests of the various collaborating domain objects can be useful. But see alsoChapter 8

and“Optionally: Unit Testing Event Handlers in Isolation with a Fake Message Bus”.



Chapter 6. Unit of Work

Pattern

In this chapter we’ll introduce the final piece of the puzzle that ties

together the Repository and Service Layer patterns: the Unit of Work

pattern.

If the Repository pattern is our abstraction over the idea of persistent

storage, the Unit of Work (UoW) pattern is our abstraction over the

idea of atomic operations. It will allow us to finally and fully

decouple our service layer from the data layer.

Figure 6-1shows that, currently, a lot of communication occurs across

the layers of our infrastructure: the API talks directly to the database

layer to start a session, it talks to the repository layer to initialize

SQLAlchemyRepository, and it talks to the service layer to ask it to

allocate.

T IP



The code for this chapter is in the chapter\_06\_uow branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_06\_uow

\# or to code along, checkout Chapter 4:

git checkout chapter\_04\_service\_layer



Figure 6-1. Without UoW: API talks directly to three layers



Figure 6-2shows our target state. The Flask API now does only two

things: it initializes a unit of work, and it invokes a service. The

service collaborates with the UoW (we like to think of the UoW as

being part of the service layer), but neither the service function itself

nor Flask now needs to talk directly to the database.

And we’ll do it all using a lovely piece of Python syntax, a context

manager.



Figure 6-2. With UoW: UoW now manages database state



The Unit of Work Collaborates with the

Repository

Let’s see the unit of work (or UoW, which we pronounce “you-wow”)

in action. Here’s how the service layer will look when we’re finished:

Preview of unit of work in action

(src/allocation/service\_layer/services.py)



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

batches=uow.batches.list()

...

batchref=model.allocate(line,batches)

uow.commit()

We’ll start a UoW as a context manager.

uow.batches is the batches repo, so the UoW provides us access

to our permanent storage.

When we’re done, we commit or roll back our work, using the

UoW.

The UoW acts as a single entrypoint to our persistent storage, and it

keeps track of what objects were loaded and of the latest state.

This gives us three useful things:

1

A stable snapshot of the database to work with, so the objects

we use aren’t changing halfway through an operation

A way to persist all of our changes at once, so if something

goes wrong, we don’t end up in an inconsistent state

A simple API to our persistence concerns and a handy place

to get a repository

Test-Driving a UoW with Integration Tests

Here are our integration tests for the UOW:

A basic “round-trip” test for a UoW (tests/integration/test\_uow.py)



def test\_uow\_can\_retrieve\_a\_batch\_and\_allocate\_to\_it(session\_factory):

session=session\_factory()

insert\_batch(session,'batch1','HIPSTER-WORKBENCH', 100 ,None)

session.commit()



uow=unit\_of\_work.SqlAlchemyUnitOfWork(session\_factory)

with uow:

batch=uow.batches.get(reference='batch1')

line=model.OrderLine('o1','HIPSTER-WORKBENCH', 10 )

batch.allocate(line)

uow.commit()



batchref=get\_allocated\_batch\_ref(session,'o1','HIPSTER-WORKBENCH')

assert batchref =='batch1'



We initialize the UoW by using our custom session factory and get

back a uow object to use in our with block.

The UoW gives us access to the batches repository via

uow.batches.

We call commit() on it when we’re done.

For the curious, the insert\_batch and get\_allocated\_batch\_ref

helpers look like this:

Helpers for doing SQL stuff (tests/integration/test\_uow.py)



def insert\_batch(session,ref,sku,qty,eta):

session.execute(

'INSERT INTO batches (reference, sku, \_purchased\_quantity, eta)'

' VALUES (:ref, :sku, :qty, :eta)',

dict(ref=ref,sku=sku,qty=qty,eta=eta)

)



def get\_allocated\_batch\_ref(session,orderid,sku):

\[\[orderlineid]]=session.execute(

'SELECT id FROM order\_lines WHERE orderid=:orderid AND sku=:sku',

dict(orderid=orderid,sku=sku)

)

\[\[batchref]]=session.execute(

'SELECT b.reference FROM allocations JOIN batches AS b ON batch\_id =

b.id'

' WHERE orderline\_id=:orderlineid',

dict(orderlineid=orderlineid)

)

return batchref

Unit of Work and Its Context Manager

In our tests we’ve implicitly defined an interface for what a UoW

needs to do. Let’s make that explicit by using an abstract base class:

Abstract UoW context manager

(src/allocation/service\_layer/unit\_of\_work.py)



classAbstractUnitOfWork (abc.ABC):

batches:repository.AbstractRepository



def \_\_exit\_\_(self,\*args):

self.rollback()



@abc.abstractmethod

def commit(self):

raiseNotImplementedError



@abc.abstractmethod

def rollback(self):

raiseNotImplementedError



The UoW provides an attribute called .batches, which will give

us access to the batches repository.

If you’ve never seen a context manager, enter and exit

are the two magic methods that execute when we enter the with

block and when we exit it, respectively. They’re our setup and

teardown phases.

We’ll call this method to explicitly commit our work when we’re

ready.

If we don’t commit, or if we exit the context manager by raising an

error, we do a rollback. (The rollback has no effect if commit()

has been called. Read on for more discussion of this.)

The Real Unit of Work Uses SQLAlchemy

Sessions

The main thing that our concrete implementation adds is the database

session:

The real SQLAlchemy UoW

(src/allocation/service\_layer/unit\_of\_work.py)



DEFAULT\_SESSION\_FACTORY=sessionmaker(bind=create\_engine(

config.get\_postgres\_uri(),

))



classSqlAlchemyUnitOfWork (AbstractUnitOfWork):



def \_\_init\_\_(self,session\_factory=DEFAULT\_SESSION\_FACTORY):

self.session\_factory=session\_factory



def \_\_enter\_\_(self):

self.session=self.session\_factory() # type: Session

self.batches=repository.SqlAlchemyRepository(self.session)

return super().\_\_enter\_\_()



def \_\_exit\_\_(self,\*args):

super().\_\_exit\_\_(\*args)

self.session.close()



def commit(self):

self.session.commit()



def rollback(self):

self.session.rollback()



The module defines a default session factory that will connect to

Postgres, but we allow that to be overridden in our integration tests

so that we can use SQLite instead.

The enter method is responsible for starting a database

session and instantiating a real repository that can use that session.

We close the session on exit.

Finally, we provide concrete commit() and rollback() methods

that use our database session.

Fake Unit of Work for Testing

Here’s how we use a fake UoW in our service-layer tests:

Fake UoW (tests/unit/test\_services.py)



classFakeUnitOfWork (unit\_of\_work.AbstractUnitOfWork):



def \_\_init\_\_(self):

self.batches=FakeRepository(\[])

self.committed=False



def commit(self):

self.committed=True



def rollback(self):

pass



def test\_add\_batch():

uow=FakeUnitOfWork()

services.add\_batch("b1","CRUNCHY-ARMCHAIR", 100 ,None,uow)

assert uow.batches.get("b1") is not None

assert uow.committed



def test\_allocate\_returns\_allocation():

uow=FakeUnitOfWork()

services.add\_batch("batch1","COMPLICATED-LAMP", 100 ,None,uow)

result=services.allocate("o1","COMPLICATED-LAMP", 10 ,uow)

assert result=="batch1"

...

FakeUnitOfWork and FakeRepository are tightly coupled, just

like the real UnitofWork and Repository classes. That’s fine

because we recognize that the objects are collaborators.

Notice the similarity with the fake commit() function from

FakeSession (which we can now get rid of). But it’s a substantial

improvement because we’re now faking out code that we wrote

rather than third-party code. Some people say,“Don’t mock what

you don’t own”.

In our tests, we can instantiate a UoW and pass it to our service

layer, rather than passing a repository and a session. This is

considerably less cumbersome.

DON’T MOCK WHAT YOU DON’T OWN



Why do we feel more comfortable mocking the UoW than the session? Both of our fakes achieve

the same thing: they give us a way to swap out our persistence layer so we can run tests in

memory instead of needing to talk to a real database. The difference is in the resulting design.

If we cared only about writing tests that run quickly, we could create mocks that replace

SQLAlchemy and use those throughout our codebase. The problem is that Session is a complex

object that exposes lots of persistence-related functionality. It’s easy to use Session to make

arbitrary queries against the database, but that quickly leads to data access code being

sprinkled all over the codebase. To avoid that, we want to limit access to our persistence layer so

each component has exactly what it needs and nothing more.

By coupling to the Session interface, you’re choosing to couple to all the complexity of

SQLAlchemy. Instead, we want to choose a simpler abstraction and use that to clearly separate

responsibilities. Our UoW is much simpler than a session, and we feel comfortable with the

service layer being able to start and stop units of work.

“Don’t mock what you don’t own” is a rule of thumb that forces us to build these simple

abstractions over messy subsystems. This has the same performance benefit as mocking the

SQLAlchemy session but encourages us to think carefully about our designs.



Using the UoW in the Service Layer

Here’s what our new service layer looks like:

Service layer using UoW (src/allocation/service\_layer/services.py)



def add\_batch(

ref:str,sku:str,qty:int,eta:Optional\[date],

uow:unit\_of\_work.AbstractUnitOfWork

):

with uow:

uow.batches.add(model.Batch(ref,sku,qty,eta))

uow.commit()



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

batches=uow.batches.list()

ifnot is\_valid\_sku(line.sku,batches):

raise InvalidSku(f'Invalid sku {line.sku}')

batchref=model.allocate(line,batches)

uow.commit()

return batchref

Our service layer now has only the one dependency, once again on

an abstract UoW.

Explicit Tests for Commit/Rollback

Behavior

To convince ourselves that the commit/rollback behavior works, we

wrote a couple of tests:

Integration tests for rollback behavior

(tests/integration/test\_uow.py)



def test\_rolls\_back\_uncommitted\_work\_by\_default(session\_factory):

uow=unit\_of\_work.SqlAlchemyUnitOfWork(session\_factory)

with uow:

insert\_batch(uow.session,'batch1','MEDIUM-PLINTH', 100 ,None)



new\_session=session\_factory()

rows=list(new\_session.execute('SELECT \* FROM "batches"'))

assert rows ==\[]



def test\_rolls\_back\_on\_error(session\_factory):

classMyException ( Exception ):

pass



uow=unit\_of\_work.SqlAlchemyUnitOfWork(session\_factory)

with pytest.raises(MyException):

with uow:

insert\_batch(uow.session,'batch1','LARGE-FORK', 100 ,None)

raise MyException()



new\_session=session\_factory()

rows=list(new\_session.execute('SELECT \* FROM "batches"'))

assert rows ==\[]



T IP



We haven’t shown it here, but it can be worth testing some of the more “obscure”

database behavior, like transactions, against the “real” database—that is, the same

engine. For now, we’re getting away with using SQLite instead of Postgres, but in

Chapter 7, we’ll switch some of the tests to using the real database. It’s

convenient that our UoW class makes that easy!



Explicit Versus Implicit Commits

Now we briefly digress on different ways of implementing the UoW

pattern.

We could imagine a slightly different version of the UoW that commits

by default and rolls back only if it spots an exception:

A UoW with implicit commit... (src/allocation/unit\_of\_work.py)



classAbstractUnitOfWork (abc.ABC):



def \_\_enter\_\_(self):

return self



def \_\_exit\_\_(self,exn\_type,exn\_value,traceback):

if exn\_type is None:

self.commit()

else :

self.rollback()



Should we have an implicit commit in the happy path?

And roll back only on exception?

It would allow us to save a line of code and to remove the explicit

commit from our client code:

...would save us a line of code

(src/allocation/service\_layer/services.py)



def add\_batch(ref:str,sku:str,qty:int,eta:Optional\[date],uow):

with uow:

uow.batches.add(model.Batch(ref,sku,qty,eta))

\# uow.commit()

This is a judgment call, but we tend to prefer requiring the explicit

commit so that we have to choose when to flush state.

Although we use an extra line of code, this makes the software safe by

default. The default behavior is to not change anything. In turn, that

makes our code easier to reason about because there’s only one code

path that leads to changes in the system: total success and an explicit

commit. Any other code path, any exception, any early exit from the

UoW’s scope leads to a safe state.

Similarly, we prefer to roll back by default because it’s easier to

understand; this rolls back to the last commit, so either the user did

one, or we blow their changes away. Harsh but simple.

Examples: Using UoW to Group Multiple

Operations into an Atomic Unit

Here are a few examples showing the Unit of Work pattern in use. You

can see how it leads to simple reasoning about what blocks of code

happen together.

Example 1: Reallocate

Suppose we want to be able to deallocate and then reallocate orders:

Reallocate service function



def reallocate(line:OrderLine,uow:AbstractUnitOfWork)->str:

with uow:

batch=uow.batches.get(sku=line.sku)

if batch is None:

raise InvalidSku(f'Invalid sku {line.sku}')

batch.deallocate(line)

allocate(line)

uow.commit()

If deallocate() fails, we don’t want to call allocate(),

obviously.

If allocate() fails, we probably don’t want to actually commit

the deallocate() either.

Example 2: Change Batch Quantity

Our shipping company gives us a call to say that one of the container

doors opened, and half our sofas have fallen into the Indian Ocean.

Oops!

Change quantity



def change\_batch\_quantity(batchref:str,new\_qty:int,uow:AbstractUnitOfWork):

with uow:

batch=uow.batches.get(reference=batchref)

batch.change\_purchased\_quantity(new\_qty)

while batch.available\_quantity< 0 :

line=batch.deallocate\_one()

uow.commit()

Here we may need to deallocate any number of lines. If we get a

failure at any stage, we probably want to commit none of the

changes.

Tidying Up the Integration Tests

We now have three sets of tests, all essentially pointing at the

database: test\_orm.py , test\_repository.py , and test\_uow.py. Should

we throw any away?



└── tests

├── conftest.py

├── e2e

│ └── test\_api.py

├── integration

│ ├── test\_orm.py

│ ├── test\_repository.py

│ └── test\_uow.py

├── pytest.ini

└── unit

├── test\_allocate.py

├── test\_batches.py

└── test\_services.py

You should always feel free to throw away tests if you think they’re not

going to add value longer term. We’d say that test\_orm.py was

primarily a tool to help us learn SQLAlchemy, so we won’t need that

long term, especially if the main things it’s doing are covered in

test\_repository.py. That last test, you might keep around, but we could

certainly see an argument for just keeping everything at the highest

possible level of abstraction (just as we did for the unit tests).

EXERCISE FOR THE READER



For this chapter, probably the best thing to try is to implement a UoW from scratch. The code, as

always, ison GitHub. You could either follow the model we have quite closely, or perhaps

experiment with separating the UoW (whose responsibilities are commit(), rollback(), and

providing the .batches repository) from the context manager, whose job is to initialize things, and

then do the commit or rollback on exit. If you feel like going all-functional rather than messing

about with all these classes, you could use @contextmanager from contextlib.

We’ve stripped out both the actual UoW and the fakes, as well as paring back the abstract UoW.

Why not send us a link to your repo if you come up with something you’re particularly proud of?



T IP



This is another example of the lesson fromChapter 5: as we build better

abstractions, we can move our tests to run against them, which leaves us free to

change the underlying details.



Wrap-Up

Hopefully we’ve convinced you that the Unit of Work pattern is useful,

and that the context manager is a really nice Pythonic way of visually

grouping code into blocks that we want to happen atomically.

This pattern is so useful, in fact, that SQLAlchemy already uses a UoW

in the shape of the Session object. The Session object in

SQLAlchemy is the way that your application loads data from the

database.

Every time you load a new entity from the database, the session begins

to track changes to the entity, and when the session is flushed , all your

changes are persisted together. Why do we go to the effort of

abstracting away the SQLAlchemy session if it already implements the

pattern we want?

Table 6-1discusses some of the trade-offs.

Table 6-1. Unit of Work pattern: the trade-offs



Pros Cons



We have a nice abstraction

over the concept of atomic

operations, and the

context manager makes it easy

to see, visually, what blocks of

code are

grouped together atomically.



We have explicit control over

when a transaction starts and

finishes, and our

application fails in a way that is

safe by default. We never have

to worry

that an operation is partially

committed.



It’s a nice place to put all your

repositories so client code can

access them.



As you’ll see in later chapters,

atomicity isn’t only about

transactions; it

can help us work with events

and the message bus.



Your ORM probably already

has some perfectly good

abstractions around

atomicity. SQLAlchemy even

has context managers. You can

go a long way

just passing a session around.



We’ve made it look easy, but

you have to think quite carefully

about

things like rollbacks,

multithreading, and nested

transactions. Perhaps just

sticking to what Django or

Flask-SQLAlchemy gives you

will keep your life

simpler.



For one thing, the Session API is rich and supports operations that we

don’t want or need in our domain. Our UnitOfWork simplifies the

session to its essential core: it can be started, committed, or thrown

away.

For another, we’re using the UnitOfWork to access our Repository

objects. This is a neat bit of developer usability that we couldn’t do

with a plain SQLAlchemy Session.

UNIT OF WORK PATTERN RECAP



The Unit of Work pattern is an abstraction around data integrity

It helps to enforce the consistency of our domain model, and improves performance, by

letting us perform a single flush operation at the end of an operation.



It works closely with the Repository and Service Layer patterns

The Unit of Work pattern completes our abstractions over data access by representing

atomic updates. Each of our service-layer use cases runs in a single unit of work that

succeeds or fails as a block.



This is a lovely case for a context manager

Context managers are an idiomatic way of defining scope in Python. We can use a context

manager to automatically roll back our work at the end of a request, which means the system

is safe by default.



SQLAlchemy already implements this pattern

We introduce an even simpler abstraction over the SQLAlchemy Session object in order to

“narrow” the interface between the ORM and our code. This helps to keep us loosely

coupled.



Lastly, we’re motivated again by the dependency inversion principle:

our service layer depends on a thin abstraction, and we attach a

concrete implementation at the outside edge of the system. This lines

up nicely with SQLAlchemy’s ownrecommendations:

Keep the life cycle of the session (and usually the transaction)

separate and external. The most comprehensive approach,

recommended for more substantial applications, will try to keep

the details of session, transaction, and exception management as

far as possible from the details of the program doing its work.

—SQLALchemy “Session Basics” Documentation



1 You may have come across the use of the word collaborators to describe objects that

work together to achieve a goal. The unit of work and the repository are a great example

of collaborators in the object-modeling sense. In responsibility-driven design, clusters of

objects that collaborate in their roles are called object neighborhoods , which is, in our

professional opinion, totally adorable.



Chapter 7. Aggregates and

Consistency Boundaries

In this chapter, we’d like to revisit our domain model to talk about

invariants and constraints, and see how our domain objects can

maintain their own internal consistency, both conceptually and in

persistent storage. We’ll discuss the concept of a consistency

boundary and show how making it explicit can help us to build high-

performance software without compromising maintainability.

Figure 7-1shows a preview of where we’re headed: we’ll introduce a

new model object called Product to wrap multiple batches, and we’ll

make the old allocate() domain service available as a method on

Product instead.



Figure 7-1. Adding the Product aggregate



Why? Let’s find out.

T IP



The code for this chapter is in the appendix\_csvs branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout appendix\_csvs

\# or to code along, checkout the previous chapter:

git checkout chapter\_06\_uow



Why Not Just Run Everything in a

Spreadsheet?

What’s the point of a domain model, anyway? What’s the fundamental

problem we’re trying to address?

Couldn’t we just run everything in a spreadsheet? Many of our users

would be delighted by that. Business users like spreadsheets because

they’re simple, familiar, and yet enormously powerful.

In fact, an enormous number of business processes do operate by

manually sending spreadsheets back and forth over email. This “CSV

over SMTP” architecture has low initial complexity but tends not to

scale very well because it’s difficult to apply logic and maintain

consistency.

Who is allowed to view this particular field? Who’s allowed to update

it? What happens when we try to order –350 chairs, or 10,000,000

tables? Can an employee have a negative salary?

These are the constraints of a system. Much of the domain logic we

write exists to enforce these constraints in order to maintain the

invariants of the system. The invariants are the things that have to be

true whenever we finish an operation.

Invariants, Constraints, and Consistency

The two words are somewhat interchangeable, but a constraint is a

rule that restricts the possible states our model can get into, while an

invariant is defined a little more precisely as a condition that is

always true.

If we were writing a hotel-booking system, we might have the

constraint that double bookings are not allowed. This supports the

invariant that a room cannot have more than one booking for the same

night.

Of course, sometimes we might need to temporarily bend the rules.

Perhaps we need to shuffle the rooms around because of a VIP

booking. While we’re moving bookings around in memory, we might

be double booked, but our domain model should ensure that, when

we’re finished, we end up in a final consistent state, where the

invariants are met. If we can’t find a way to accommodate all our

guests, we should raise an error and refuse to complete the operation.

Let’s look at a couple of concrete examples from our business

requirements; we’ll start with this one:

An order line can be allocated to only one batch at a time.

—The business

This is a business rule that imposes an invariant. The invariant is that

an order line is allocated to either zero or one batch, but never more

than one. We need to make sure that our code never accidentally calls

Batch.allocate() on two different batches for the same line, and

currently, there’s nothing there to explicitly stop us from doing that.

Invariants, Concurrency, and Locks

Let’s look at another one of our business rules:

We can’t allocate to a batch if the available quantity is less than

the quantity of the order line.

—The business

Here the constraint is that we can’t allocate more stock than is

available to a batch, so we never oversell stock by allocating two

customers to the same physical cushion, for example. Every time we

update the state of the system, our code needs to ensure that we don’t

break the invariant, which is that the available quantity must be greater

than or equal to zero.

In a single-threaded, single-user application, it’s relatively easy for us

to maintain this invariant. We can just allocate stock one line at a time,

and raise an error if there’s no stock available.

This gets much harder when we introduce the idea of concurrency.

Suddenly we might be allocating stock for multiple order lines

simultaneously. We might even be allocating order lines at the same

time as processing changes to the batches themselves.

We usually solve this problem by applying locks to our database

tables. This prevents two operations from happening simultaneously on

the same row or same table.

As we start to think about scaling up our app, we realize that our

model of allocating lines against all available batches may not scale. If

we process tens of thousands of orders per hour, and hundreds of

thousands of order lines, we can’t hold a lock over the whole batches

table for every single one—we’ll get deadlocks or performance

problems at the very least.

What Is an Aggregate?

OK, so if we can’t lock the whole database every time we want to

allocate an order line, what should we do instead? We want to protect

the invariants of our system but allow for the greatest degree of

concurrency. Maintaining our invariants inevitably means preventing

concurrent writes; if multiple users can allocate DEADLY-SPOON at the

same time, we run the risk of overallocating.

On the other hand, there’s no reason we can’t allocate DEADLY-SPOON

at the same time as FLIMSY-DESK. It’s safe to allocate two products at

the same time because there’s no invariant that covers them both. We

don’t need them to be consistent with each other.

The Aggregate pattern is a design pattern from the DDD community

that helps us to resolve this tension. An aggregate is just a domain

object that contains other domain objects and lets us treat the whole

collection as a single unit.

The only way to modify the objects inside the aggregate is to load the

whole thing, and to call methods on the aggregate itself.

As a model gets more complex and grows more entity and value

objects, referencing each other in a tangled graph, it can be hard to

keep track of who can modify what. Especially when we have

collections in the model as we do (our batches are a collection), it’s a

good idea to nominate some entities to be the single entrypoint for

modifying their related objects. It makes the system conceptually

simpler and easy to reason about if you nominate some objects to be in

charge of consistency for the others.

For example, if we’re building a shopping site, the Cart might make a

good aggregate: it’s a collection of items that we can treat as a single

unit. Importantly, we want to load the entire basket as a single blob

from our data store. We don’t want two requests to modify the basket

at the same time, or we run the risk of weird concurrency errors.

Instead, we want each change to the basket to run in a single database

transaction.

We don’t want to modify multiple baskets in a transaction, because

there’s no use case for changing the baskets of several customers at the

same time. Each basket is a single consistency boundary responsible

for maintaining its own invariants.

An AGGREGATE is a cluster of associated objects that we treat as

a unit for the purpose of data changes.

—Eric Evans, Domain-Driven Design blue book

Per Evans, our aggregate has a root entity (the Cart) that encapsulates

access to items. Each item has its own identity, but other parts of the

system will always refer to the Cart only as an indivisible whole.

T IP



Just as we sometimes use \_leading\_underscores to mark methods or

functions as “private,” you can think of aggregates as being the “public” classes

of our model, and the rest of the entities and value objects as “private.”



Choosing an Aggregate

What aggregate should we use for our system? The choice is somewhat

arbitrary, but it’s important. The aggregate will be the boundary where

we make sure every operation ends in a consistent state. This helps us

to reason about our software and prevent weird race issues. We want

to draw a boundary around a small number of objects—the smaller, the

better, for performance—that have to be consistent with one another,

and we need to give this boundary a good name.

The object we’re manipulating under the covers is Batch. What do we

call a collection of batches? How should we divide all the batches in

the system into discrete islands of consistency?

We could use Shipment as our boundary. Each shipment contains

several batches, and they all travel to our warehouse at the same time.

Or perhaps we could use Warehouse as our boundary: each warehouse

contains many batches, and counting all the stock at the same time

could make sense.

Neither of these concepts really satisfies us, though. We should be able

to allocate DEADLY-SPOONs and FLIMSY-DESKs at the same time, even

if they’re in the same warehouse or the same shipment. These concepts

have the wrong granularity.

When we allocate an order line, we’re interested only in batches that

have the same SKU as the order line. Some sort of concept like

GlobalSkuStock could work: a collection of all the batches for a

given SKU.

It’s an unwieldy name, though, so after some bikeshedding via

SkuStock, Stock, ProductStock, and so on, we decided to simply

call it Product—after all, that was the first concept we came across in

our exploration of the domain language back inChapter 1.

So the plan is this: when we want to allocate an order line, instead of

Figure 7-2, where we look up all the Batch objects in the world and

pass them to the allocate() domain service...



Figure 7-2. Before: allocate against all batches using the domain service



...we’ll move to the world ofFigure 7-3, in which there is a new

Product object for the particular SKU of our order line, and it will be

in charge of all the batches for that SKU , and we can call a

.allocate() method on that instead.



Figure 7-3. After: ask Product to allocate against its batches

Let’s see how that looks in code form:

Our chosen aggregate, Product (src/allocation/domain/model.py)



classProduct :



def \_\_init\_\_(self,sku:str,batches:List\[Batch]):

self.sku=sku

self.batches=batches



def allocate(self,line:OrderLine)->str:

try :

batch=next(

b for b in sorted(self.batches) if b.can\_allocate(line)

)

batch.allocate(line)

return batch.reference

exceptStopIteration :

raise OutOfStock(f'Out of stock for sku {line.sku}')



Product’s main identifier is the sku.

Our Product class holds a reference to a collection of batches

for that SKU.

Finally, we can move the allocate() domain service to be a

method on the Product aggregate.

NOT E



This Product might not look like what you’d expect a Product model to look like.

No price, no description, no dimensions. Our allocation service doesn’t care about

any of those things. This is the power of bounded contexts; the concept of a

product in one app can be very different from another. See the following sidebar

for more discussion.



AGGREGATES, BOUNDED CONTEXTS, AND MICROSERVICES



One of the most important contributions from Evans and the DDD community is the concept of

b ounded contexts.

In essence, this was a reaction against attempts to capture entire businesses into a single

model. The word custom er means different things to people in sales, customer service, logistics,

support, and so on. Attributes needed in one context are irrelevant in another; more perniciously,

concepts with the same name can have entirely different meanings in different contexts. Rather

than trying to build a single model (or class, or database) to capture all the use cases, it’s better

to have several models, draw boundaries around each context, and handle the translation

between different contexts explicitly.

This concept translates very well to the world of microservices, where each microservice is free

to have its own concept of “customer” and its own rules for translating that to and from other

microservices it integrates with.

In our example, the allocation service has Product(sku, batches), whereas the ecommerce will

have Product(sku, description, price, image\_url, dimensions, etc...). As a rule of thumb,

your domain models should include only the data that they need for performing calculations.

Whether or not you have a microservices architecture, a key consideration in choosing your

aggregates is also choosing the bounded context that they will operate in. By restricting the

context, you can keep your number of aggregates low and their size manageable.

Once again, we find ourselves forced to say that we can’t give this issue the treatment it deserves

here, and we can only encourage you to read up on it elsewhere. The Fowler link at the start of

this sidebar is a good starting point, and either (or indeed, any) DDD book will have a chapter or

more on bounded contexts.



One Aggregate = One Repository

Once you define certain entities to be aggregates, we need to apply the

rule that they are the only entities that are publicly accessible to the

outside world. In other words, the only repositories we are allowed

should be repositories that return aggregates.

NOT E



The rule that repositories should only return aggregates is the main place where

we enforce the convention that aggregates are the only way into our domain

model. Be wary of breaking it!



In our case, we’ll switch from BatchRepository to

ProductRepository:

Our new UoW and repository (unit\_of\_work.py and repository.py)



classAbstractUnitOfWork (abc.ABC):

products:repository.AbstractProductRepository



...



classAbstractProductRepository (abc.ABC):



@abc.abstractmethod

def add(self,product):

...



@abc.abstractmethod

def get(self,sku)->model.Product:

...



The ORM layer will need some tweaks so that the right batches

automatically get loaded and associated with Product objects. The

nice thing is, the Repository pattern means we don’t have to worry

about that yet. We can just use our FakeRepository and then feed

through the new model into our service layer to see how it looks with

Product as its main entrypoint:

Service layer (src/allocation/service\_layer/services.py)



def add\_batch(

ref:str,sku:str,qty:int,eta:Optional\[date],

uow:unit\_of\_work.AbstractUnitOfWork

):

with uow:

product=uow.products.get(sku=sku)

if product is None:

product=model.Product(sku,batches=\[])

uow.products.add(product)

product.batches.append(model.Batch(ref,sku,qty,eta))

uow.commit()



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

product=uow.products.get(sku=line.sku)

if product is None:

raise InvalidSku(f'Invalid sku {line.sku}')

batchref=product.allocate(line)

uow.commit()

return batchref

What About Performance?

We’ve mentioned a few times that we’re modeling with aggregates

because we want to have high-performance software, but here we are

loading all the batches when we only need one. You might expect that

to be inefficient, but there are a few reasons why we’re comfortable

here.

First, we’re purposefully modeling our data so that we can make a

single query to the database to read, and a single update to persist our

changes. This tends to perform much better than systems that issue lots

of ad hoc queries. In systems that don’t model this way, we often find

that transactions slowly get longer and more complex as the software

evolves.

Second, our data structures are minimal and comprise a few strings

and integers per row. We can easily load tens or even hundreds of

batches in a few milliseconds.

Third, we expect to have only 20 or so batches of each product at a

time. Once a batch is used up, we can discount it from our

calculations. This means that the amount of data we’re fetching

shouldn’t get out of control over time.

If we did expect to have thousands of active batches for a product,

we’d have a couple of options. For one, we could use lazy-loading for

the batches in a product. From the perspective of our code, nothing

would change, but in the background, SQLAlchemy would page

through data for us. This would lead to more requests, each fetching a

smaller number of rows. Because we need to find only a single batch

with enough capacity for our order, this might work pretty well.

EXERCISE FOR THE READER



You’ve just seen the main top layers of the code, so this shouldn’t be too hard, but we’d like you

to implement the Product aggregate starting from Batch, just as we did.

Of course, you could cheat and copy/paste from the previous listings, but even if you do that, you’ll

still have to solve a few challenges on your own, like adding the model to the ORM and making

sure all the moving parts can talk to each other, which we hope will be instructive.

You’ll find the codeon GitHub. We’ve put in a “cheating” implementation in the delegates to the

existing allocate() function, so you should be able to evolve that toward the real thing.

We’ve marked a couple of tests with @pytest.skip(). After you’ve read the rest of this chapter,

come back to these tests to have a go at implementing version numbers. Bonus points if you can

get SQLAlchemy to do them for you by magic!



If all else failed, we’d just look for a different aggregate. Maybe we

could split up batches by region or by warehouse. Maybe we could

redesign our data access strategy around the shipment concept. The

Aggregate pattern is designed to help manage some technical

constraints around consistency and performance. There isn’t one

correct aggregate, and we should feel comfortable changing our minds

if we find our boundaries are causing performance woes.

Optimistic Concurrency with Version

Numbers

We have our new aggregate, so we’ve solved the conceptual problem

of choosing an object to be in charge of consistency boundaries. Let’s

now spend a little time talking about how to enforce data integrity at

the database level.

NOT E



This section has a lot of implementation details; for example, some of it is

Postgres-specific. But more generally, we’re showing one way of managing

concurrency issues, but it is just one approach. Real requirements in this area vary

a lot from project to project. You shouldn’t expect to be able to copy and paste

code from here into production.



We don’t want to hold a lock over the entire batches table, but how

will we implement holding a lock over just the rows for a particular

SKU?

One answer is to have a single attribute on the Product model that

acts as a marker for the whole state change being complete and to use

it as the single resource that concurrent workers can fight over. If two

transactions read the state of the world for batches at the same time,

and both want to update the allocations tables, we force both to also

try to update the version\_number in the products table, in such a

way that only one of them can win and the world stays consistent.

Figure 7-4illustrates two concurrent transactions doing their read

operations at the same time, so they see a Product with, for example,

version=3. They both call Product.allocate() in order to modify a

state. But we set up our database integrity rules such that only one of

them is allowed to commit the new Product with version=4, and the

other update is rejected.

T IP



Version numbers are just one way to implement optimistic locking. You could

achieve the same thing by setting the Postgres transaction isolation level to



SERIALIZABLE, but that often comes at a severe performance cost. Version

numbers also make implicit concepts explicit.



Figure 7-4. Sequence diagram: two transactions attempting a concurrent update on

Product

OPTIMISTIC CONCURRENCY CONTROL AND RETRIES



What we’ve implemented here is called optim istic concurrency control because our default

assumption is that everything will be fine when two users want to make changes to the

database. We think it’s unlikely that they will conflict with each other, so we let them go ahead and

just make sure we have a way to notice if there is a problem.

Pessim istic concurrency control works under the assumption that two users are going to cause

conflicts, and we want to prevent conflicts in all cases, so we lock everything just to be safe. In

our example, that would mean locking the whole batches table, or using SELECT FOR UPDATE—

we’re pretending that we’ve ruled those out for performance reasons, but in real life you’d want to

do some evaluations and measurements of your own.

With pessimistic locking, you don’t need to think about handling failures because the database

will prevent them for you (although you do need to think about deadlocks). With optimistic locking,

you need to explicitly handle the possibility of failures in the (hopefully unlikely) case of a clash.

The usual way to handle a failure is to retry the failed operation from the beginning. Imagine we

have two customers, Harry and Bob, and each submits an order for SHINY-TABLE. Both threads

load the product at version 1 and allocate stock. The database prevents the concurrent update,

and Bob’s order fails with an error. When we retry the operation, Bob’s order loads the product at

version 2 and tries to allocate again. If there is enough stock left, all is well; otherwise, he’ll

receive OutOfStock. Most operations can be retried this way in the case of a concurrency problem.

Read more on retries in“Recovering from Errors Synchronously”and“Footguns”.



Implementation Options for Version Numbers

There are essentially three options for implementing version numbers:

1\. version\_number lives in the domain; we add it to the

Product constructor, and Product.allocate() is

responsible for incrementing it.

2\. The service layer could do it! The version number isn’t

strictly a domain concern, so instead our service layer could

assume that the current version number is attached to Product

by the repository, and the service layer will increment it

before it does the commit().

3\. Since it’s arguably an infrastructure concern, the UoW and

repository could do it by magic. The repository has access to

version numbers for any products it retrieves, and when the

UoW does a commit, it can increment the version number for

any products it knows about, assuming them to have changed.

Option 3 isn’t ideal, because there’s no real way of doing it without

having to assume that all products have changed, so we’ll be

incrementing version numbers when we don’t have to.

Option 2 involves mixing the responsibility for mutating state between

the service layer and the domain layer, so it’s a little messy as well.

So in the end, even though version numbers don’t have to be a domain

concern, you might decide the cleanest trade-off is to put them in the

domain:

Our chosen aggregate, Product (src/allocation/domain/model.py)



classProduct :



def \_\_init\_\_(self,sku:str,batches:List\[Batch],version\_number:int= 0 ):



self.sku=sku

self.batches=batches

self.version\_number=version\_number



def allocate(self,line:OrderLine)->str:

try :

batch=next(

b for b in sorted(self.batches) if b.can\_allocate(line)

)

batch.allocate(line)

self.version\_number+= 1

return batch.reference



1



exceptStopIteration :

raise OutOfStock(f'Out of stock for sku {line.sku}')



There it is!

T IP



If you’re scratching your head at this version number business, it might help to

remember that the number isn’t important. What’s important is that the Product

database row is modified whenever we make a change to the Product aggregate.

The version number is a simple, human-comprehensible way to model a thing that

changes on every write, but it could equally be a random UUID every time.



Testing for Our Data Integrity Rules

Now to make sure we can get the behavior we want: if we have two

concurrent attempts to do allocation against the same Product, one of

them should fail, because they can’t both update the version number.

First, let’s simulate a “slow” transaction using a function that does

allocation and then does an explicit sleep:

time.sleep can reproduce concurrency behavior

(tests/integration/test\_uow.py)



def try\_to\_allocate(orderid,sku,exceptions):

line=model.OrderLine(orderid,sku, 10 )

try :

with unit\_of\_work.SqlAlchemyUnitOfWork() as uow:

product=uow.products.get(sku=sku)

product.allocate(line)

time.sleep(0.2)

2



uow.commit()

exceptExceptionas e:

print (traceback.format\_exc())

exceptions.append(e)



Then we have our test invoke this slow allocation twice, concurrently,

using threads:

An integration test for concurrency behavior

(tests/integration/test\_uow.py)



def

test\_concurrent\_updates\_to\_version\_are\_not\_allowed(postgres\_session\_factory):

sku,batch=random\_sku(),random\_batchref()

session=postgres\_session\_factory()

insert\_batch(session,batch,sku, 100 ,eta=None,product\_version= 1 )

session.commit()



order1,order2=random\_orderid( 1 ),random\_orderid( 2 )

exceptions=\[] # type: List\[Exception]

try\_to\_allocate\_order1= lambda :try\_to\_allocate(order1,sku,exceptions)

try\_to\_allocate\_order2= lambda :try\_to\_allocate(order2,sku,exceptions)

thread1=threading.Thread(target=try\_to\_allocate\_order1)

thread2=threading.Thread(target=try\_to\_allocate\_order2)

thread1.start()

thread2.start()

thread1.join()

thread2.join()



\[\[version]]=session.execute(

"SELECT version\_number FROM products WHERE sku=:sku",

dict(sku=sku),

)

assert version== 2

\[exception]=exceptions

assert 'could not serialize access due to concurrent update' in

str(exception)



orders=list(session.execute(

"SELECT orderid FROM allocations"

" JOIN batches ON allocations.batch\_id = batches.id"

" JOIN order\_lines ON allocations.orderline\_id = order\_lines.id"

" WHERE order\_lines.sku=:sku",

dict(sku=sku),

))

assert len(orders)== 1

with unit\_of\_work.SqlAlchemyUnitOfWork() as uow:

uow.session.execute('select 1')



We start two threads that will reliably produce the concurrency

behavior we want: read1, read2, write1, write2.

We assert that the version number has been incremented only once.

We can also check on the specific exception if we like.

And we double-check that only one allocation has gotten through.

Enforcing Concurrency Rules by Using Database

Transaction Isolation Levels

To get the test to pass as it is, we can set the transaction isolation level

on our session:

Set isolation level for session

(src/allocation/service\_layer/unit\_of\_work.py)



DEFAULT\_SESSION\_FACTORY=sessionmaker(bind=create\_engine(

config.get\_postgres\_uri(),

isolation\_level="REPEATABLE READ",

))

T IP



Transaction isolation levels are tricky stuff, so it’s worth spending time

understandingthe Postgres documentation.



Pessimistic Concurrency Control Example:

SELECT FOR UPDATE

There are multiple ways to approach this, but we’ll show one.SELECT

FOR UPDATEproduces different behavior; two concurrent transactions

will not be allowed to do a read on the same rows at the same time:

SELECT FOR UPDATE is a way of picking a row or rows to use as a

lock (although those rows don’t have to be the ones you update). If two

transactions both try to SELECT FOR UPDATE a row at the same time,

one will win, and the other will wait until the lock is released. So this

is an example of pessimistic concurrency control.

Here’s how you can use the SQLAlchemy DSL to specify FOR UPDATE

at query time:

SQLAlchemy with\_for\_update

(src/allocation/adapters/repository.py)



def get(self,sku):

return self.session.query(model.Product)\\

.filter\_by(sku=sku)\\

.with\_for\_update()\\

.first()



This will have the effect of changing the concurrency pattern from



3



read1, read2, write1, write2(fail)



to



read1, write1, read2, write2(succeed)



Some people refer to this as the “read-modify-write” failure mode.

Read“PostgreSQL Anti-Patterns: Read-Modify-Write Cycles”for a

good overview.

We don’t really have time to discuss all the trade-offs between

REPEATABLE READ and SELECT FOR UPDATE, or optimistic versus

pessimistic locking in general. But if you have a test like the one

we’ve shown, you can specify the behavior you want and see how it

changes. You can also use the test as a basis for performing some

performance experiments.

Wrap-Up

Specific choices around concurrency control vary a lot based on

business circumstances and storage technology choices, but we’d like

to bring this chapter back to the conceptual idea of an aggregate: we

explicitly model an object as being the main entrypoint to some subset

of our model, and as being in charge of enforcing the invariants and

business rules that apply across all of those objects.

Choosing the right aggregate is key, and it’s a decision you may revisit

over time. You can read more about it in multiple DDD books. We also

recommend these three online papers oneffective aggregate designby

Vaughn Vernon (the “red book” author).

Table 7-1has some thoughts on the trade-offs of implementing the

Aggregate pattern.

Table 7-1. Aggregates: the trade-offs



Pros Cons



Python might not have “official”

public and private methods, but

we do have

the underscores convention,

because it’s often useful to try

to indicate what’s for

“internal” use and what’s for

“outside code” to use. Choosing

aggregates is

just the next level up: it lets you

decide which of your domain

model classes

are the public ones, and which

aren’t.



Modeling our operations around

explicit consistency boundaries

helps us avoid

performance problems with our

ORM.



Putting the aggregate in sole

charge of state changes to its

subsidiary models

makes the system easier to

reason about, and makes it

easier to control invariants.



Yet another new concept for

new developers to take on.

Explaining entities versus

value objects was already a

mental load; now there’s a third

type of domain

model object?



Sticking rigidly to the rule that

we modify only one aggregate

at a time is a

big mental shift.



Dealing with eventual

consistency between

aggregates can be complex.



AGGREGATES AND CONSISTENCY BOUNDARIES RECAP



Aggregates are your entrypoints into the domain model



By restricting the number of ways that things can be changed, we make the system easier to

reason about.



Aggregates are in charge of a consistency boundary



An aggregate’s job is to be able to manage our business rules about invariants as they apply

to a group of related objects. It’s the aggregate’s job to check that the objects within its remit

are consistent with each other and with our rules, and to reject changes that would break the

rules.



Aggregates and concurrency issues go together



When thinking about implementing these consistency checks, we end up thinking about

transactions and locks. Choosing the right aggregate is about performance as well as

conceptual organization of your domain.



Part I Recap

Do you rememberFigure 7-5, the diagram we showed at the beginning

ofPart Ito preview where we were heading?



Figure 7-5. A component diagram for our app at the end of Part I



So that’s where we are at the end of Part I. What have we achieved?

We’ve seen how to build a domain model that’s exercised by a set of

high-level unit tests. Our tests are living documentation: they describe

the behavior of our system—the rules upon which we agreed with our

business stakeholders—in nice readable code. When our business

requirements change, we have confidence that our tests will help us to

prove the new functionality, and when new developers join the project,

they can read our tests to understand how things work.

We’ve decoupled the infrastructural parts of our system, like the

database and API handlers, so that we can plug them into the outside of

our application. This helps us to keep our codebase well organized

and stops us from building a big ball of mud.

By applying the dependency inversion principle, and by using ports-

and-adapters-inspired patterns like Repository and Unit of Work,

we’ve made it possible to do TDD in both high gear and low gear and

to maintain a healthy test pyramid. We can test our system edge to

edge, and the need for integration and end-to-end tests is kept to a

minimum.

Lastly, we’ve talked about the idea of consistency boundaries. We

don’t want to lock our entire system whenever we make a change, so

we have to choose which parts are consistent with one another.

For a small system, this is everything you need to go and play with the

ideas of domain-driven design. You now have the tools to build

database-agnostic domain models that represent the shared language of

your business experts. Hurrah!

NOT E



At the risk of laboring the point—we’ve been at pains to point out that each

pattern comes at a cost. Each layer of indirection has a price in terms of

complexity and duplication in our code and will be confusing to programmers

who’ve never seen these patterns before. If your app is essentially a simple

CRUD wrapper around a database and isn’t likely to be anything more than that

in the foreseeable future, you don’t need these patterns. Go ahead and use

Django, and save yourself a lot of bother.



In Part II, we’ll zoom out and talk about a bigger topic: if aggregates

are our boundary, and we can update only one at a time, how do we

model processes that cross consistency boundaries?



1 Perhaps we could get some ORM/SQLAlchemy magic to tell us when an object is dirty,

but how would that work in the generic case—for example, for a CsvRepository?



2 time.sleep() works well in our use case, but it’s not the most reliable or efficient way

to reproduce concurrency bugs. Consider using semaphores or similar synchronization

primitives shared between your threads to get better guarantees of behavior.



3 If you’re not using Postgres, you’ll need to read different documentation. Annoyingly,

different databases all have quite different definitions. Oracle’s SERIALIZABLE is

equivalent to Postgres’s REPEATABLE READ, for example.



Part II. Event-Driven

Architecture

I’m sorry that I long ago coined the term “objects” for this topic

because it gets many people to focus on the lesser idea.

The big idea is “messaging."...The key in making great and

growable systems is much more to design how its modules

communicate rather than what their internal properties and

behaviors should be.

—Alan Kay

It’s all very well being able to write one domain model to manage a

single bit of business process, but what happens when we need to

write many models? In the real world, our applications sit within an

organization and need to exchange information with other parts of the

system. You may remember our context diagram shown inFigure II-1.

Faced with this requirement, many teams reach for microservices

integrated via HTTP APIs. But if they’re not careful, they’ll end up

producing the most chaotic mess of all: the distributed big ball of mud.

In Part II, we’ll show how the techniques fromPart Ican be extended

to distributed systems. We’ll zoom out to look at how we can compose

a system from many small components that interact through

asynchronous message passing.

We’ll see how our Service Layer and Unit of Work patterns allow us to

reconfigure our app to run as an asynchronous message processor, and

how event-driven systems help us to decouple aggregates and

applications from one another.



Figure II-1. But exactly how will all these systems talk to each other?



We’ll look at the following patterns and techniques:

Domain Events

Trigger workflows that cross consistency boundaries.

Message Bus

Provide a unified way of invoking use cases from any endpoint.

CQRS

Separating reads and writes avoids awkward compromises in an

event-driven architecture and enables performance and scalability

improvements.

Plus, we’ll add a dependency injection framework. This has nothing to

do with event-driven architecture per se, but it tidies up an awful lot of

loose ends.

Chapter 8. Events and the

Message Bus

So far we’ve spent a lot of time and energy on a simple problem that

we could easily have solved with Django. You might be asking if the

increased testability and expressiveness are really worth all the effort.

In practice, though, we find that it’s not the obvious features that make

a mess of our codebases: it’s the goop around the edge. It’s reporting,

and permissions, and workflows that touch a zillion objects.

Our example will be a typical notification requirement: when we can’t

allocate an order because we’re out of stock, we should alert the

buying team. They’ll go and fix the problem by buying more stock, and

all will be well.

For a first version, our product owner says we can just send the alert

by email.

Let’s see how our architecture holds up when we need to plug in some

of the mundane stuff that makes up so much of our systems.

We’ll start by doing the simplest, most expeditious thing, and talk

about why it’s exactly this kind of decision that leads us to the Big Ball

of Mud.

Then we’ll show how to use the Domain Events pattern to separate

side effects from our use cases, and how to use a simple Message Bus

pattern for triggering behavior based on those events. We’ll show a

few options for creating those events and how to pass them to the

message bus, and finally we’ll show how the Unit of Work pattern can

be modified to connect the two together elegantly, as previewed in

Figure 8-1.



Figure 8-1. Events flowing through the system



T IP



The code for this chapter is in the chapter\_08\_events\_and\_message\_bus branch

on GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_08\_events\_and\_message\_bus

\# or to code along, checkout the previous chapter:

git checkout chapter\_07\_aggregate



Avoiding Making a Mess

So. Email alerts when we run out of stock. When we have new

requirements like ones that really have nothing to do with the core

domain, it’s all too easy to start dumping these things into our web

controllers.

First, Let’s Avoid Making a Mess of Our Web

Controllers

As a one-off hack, this might be OK:

Just whack it in the endpoint—what could go wrong?

(src/allocation/entrypoints/flask\_app.py)



@app.route("/allocate",methods=\['POST'])

def allocate\_endpoint():

line=model.OrderLine(

request.json\['orderid'],

request.json\['sku'],



request.json\['qty'],

)

try :

uow=unit\_of\_work.SqlAlchemyUnitOfWork()

batchref=services.allocate(line,uow)

except (model.OutOfStock,services.InvalidSku) as e:

send\_mail(

'out of stock',

'stock\_admin@made.com',

f'{line.orderid} - {line.sku}'

)

return jsonify({'message':str(e)}), 400



return jsonify({'batchref':batchref}), 201



...but it’s easy to see how we can quickly end up in a mess by patching

things up like this. Sending email isn’t the job of our HTTP layer, and

we’d like to be able to unit test this new feature.

And Let’s Not Make a Mess of Our Model Either

Assuming we don’t want to put this code into our web controllers,

because we want them to be as thin as possible, we may look at putting

it right at the source, in the model:

Email-sending code in our model isn’t lovely either

(src/allocation/domain/model.py)



def allocate(self,line:OrderLine)->str:

try :

batch=next(

b for b in sorted(self.batches) if b.can\_allocate(line)

)

\#...

exceptStopIteration :



email.send\_mail('stock@made.com',f'Out of stock for {line.sku}')

raise OutOfStock(f'Out of stock for sku {line.sku}')



But that’s even worse! We don’t want our model to have any

dependencies on infrastructure concerns like email.send\_mail.

This email-sending thing is unwelcome goop messing up the nice clean

flow of our system. What we’d like is to keep our domain model

focused on the rule “You can’t allocate more stuff than is actually

available.”

The domain model’s job is to know that we’re out of stock, but the

responsibility of sending an alert belongs elsewhere. We should be

able to turn this feature on or off, or to switch to SMS notifications

instead, without needing to change the rules of our domain model.

Or the Service Layer!

The requirement “Try to allocate some stock, and send an email if it

fails” is an example of workflow orchestration: it’s a set of steps that

the system has to follow to achieve a goal.

We’ve written a service layer to manage orchestration for us, but even

here the feature feels out of place:

And in the service layer, it’s out of place

(src/allocation/service\_layer/services.py)



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:



line=OrderLine(orderid,sku,qty)

with uow:

product=uow.products.get(sku=line.sku)

if product is None:

raise InvalidSku(f'Invalid sku {line.sku}')

try :

batchref=product.allocate(line)

uow.commit()

return batchref

except model.OutOfStock:

email.send\_mail('stock@made.com',f'Out of stock for {line.sku}')

raise



Catching an exception and reraising it? It could be worse, but it’s

definitely making us unhappy. Why is it so hard to find a suitable home

for this code?

Single Responsibility Principle

Really, this is a violation of the single responsibility principle

(SRP). Our use case is allocation. Our endpoint, service function, and

domain methods are all called allocate, not

allocate\_and\_send\_mail\_if\_out\_of\_stock.

T IP



Rule of thumb: if you can’t describe what your function does without using words

like “then” or “and,” you might be violating the SRP.



One formulation of the SRP is that each class should have only a single

reason to change. When we switch from email to SMS, we shouldn’t

1

have to update our allocate() function, because that’s clearly a

separate responsibility.

To solve the problem, we’re going to split the orchestration into

separate steps so that the different concerns don’t get tangled up. The

domain model’s job is to know that we’re out of stock, but the

responsibility of sending an alert belongs elsewhere. We should be

able to turn this feature on or off, or to switch to SMS notifications

instead, without needing to change the rules of our domain model.

We’d also like to keep the service layer free of implementation details.

We want to apply the dependency inversion principle to notifications

so that our service layer depends on an abstraction, in the same way as

we avoid depending on the database by using a unit of work.

All Aboard the Message Bus!

The patterns we’re going to introduce here are Domain Events and the

Message Bus. We can implement them in a few ways, so we’ll show a

couple before settling on the one we like most.

The Model Records Events

First, rather than being concerned about emails, our model will be in

charge of recording events —facts about things that have happened.

We’ll use a message bus to respond to events and invoke a new

operation.

Events Are Simple Dataclasses

2

An event is a kind of value object. Events don’t have any behavior,

because they’re pure data structures. We always name events in the

language of the domain, and we think of them as part of our domain

model.

We could store them in model.py , but we may as well keep them in

their own file (this might be a good time to consider refactoring out a

directory called domain so that we have domain/model.py and

domain/events.py ):

Event classes (src/allocation/domain/events.py)



fromdataclassesimport dataclass



classEvent :

pass



@dataclass

classOutOfStock (Event):

sku:str

Once we have a number of events, we’ll find it useful to have a

parent class that can store common attributes. It’s also useful for

type hints in our message bus, as you’ll see shortly.

dataclasses are great for domain events too.

The Model Raises Events

When our domain model records a fact that happened, we say it raises

an event.

Here’s what it will look like from the outside; if we ask Product to

allocate but it can’t, it should raise an event:

Test our aggregate to raise events (tests/unit/test\_product.py)



def test\_records\_out\_of\_stock\_event\_if\_cannot\_allocate():

batch=Batch('batch1','SMALL-FORK', 10 ,eta=today)

product=Product(sku="SMALL-FORK",batches=\[batch])

product.allocate(OrderLine('order1','SMALL-FORK', 10 ))



allocation=product.allocate(OrderLine('order2','SMALL-FORK', 1 ))

assert product.events\[- 1 ]==events.OutOfStock(sku="SMALL-FORK")

assert allocation is None



Our aggregate will expose a new attribute called .events that will

contain a list of facts about what has happened, in the form of

Event objects.

Here’s what the model looks like on the inside:

The model raises a domain event (src/allocation/domain/model.py)



classProduct :



def \_\_init\_\_(self,sku:str,batches:List\[Batch],version\_number:int= 0 ):

self.sku=sku

self.batches=batches

self.version\_number=version\_number

self.events=\[] # type: List\[events.Event]



def allocate(self,line:OrderLine)->str:

try :

\#...

exceptStopIteration :

self.events.append(events.OutOfStock(line.sku))

\# raise OutOfStock(f'Out of stock for sku {line.sku}')

return None



Here’s our new .events attribute in use.

Rather than invoking some email-sending code directly, we record

those events at the place they occur, using only the language of the

domain.

We’re also going to stop raising an exception for the out-of-stock

case. The event will do the job the exception was doing.

NOT E



We’re actually addressing a code smell we had until now, which is that we were

using exceptions for control flow. In general, if you’re implementing domain

events, don’t raise exceptions to describe the same domain concept. As you’ll see

later when we handle events in the Unit of Work pattern, it’s confusing to have to

reason about events and exceptions together.



The Message Bus Maps Events to Handlers

A message bus basically says, “When I see this event, I should invoke

the following handler function.” In other words, it’s a simple publish-

subscribe system. Handlers are subscribed to receive events, which

we publish to the bus. It sounds harder than it is, and we usually

implement it with a dict:

Simple message bus (src/allocation/service\_layer/messagebus.py)



def handle(event:events.Event):

for handler in HANDLERS\[type(event)]:

handler(event)



def send\_out\_of\_stock\_notification(event:events.OutOfStock):

email.send\_mail(

'stock@made.com',

f'Out of stock for {event.sku}',

)

HANDLERS={



events.OutOfStock: \[send\_out\_of\_stock\_notification],



} # type: Dict\[Type\[events.Event], List\[Callable]]

NOT E



Note that the message bus as implemented doesn’t give us concurrency because

only one handler will run at a time. Our objective isn’t to support parallel threads

but to separate tasks conceptually, and to keep each UoW as small as possible.

This helps us to understand the codebase because the “recipe” for how to run

each use case is written in a single place. See the following sidebar.



IS THIS LIKE CELERY?



Celery is a popular tool in the Python world for deferring self-contained chunks of work to an

asynchronous task queue. The message bus we’re presenting here is very different, so the short

answer to the above question is no; our message bus has more in common with a Node.js app,

a UI event loop, or an actor framework.

If you do have a requirement for moving work off the main thread, you can still use our event-

based metaphors, but we suggest you use external events for that. There’s more discussion in

Table 11-1, but essentially, if you implement a way of persisting events to a centralized store, you

can subscribe other containers or other microservices to them. Then that same concept of using

events to separate responsibilities across units of work within a single process/service can be

extended across multiple processes—which may be different containers within the same

service, or totally different microservices.

If you follow us in this approach, your API for distributing tasks is your event classes—or a JSON

representation of them. This allows you a lot of flexibility in who you distribute tasks to; they need

not necessarily be Python services. Celery’s API for distributing tasks is essentially “function

name plus arguments,” which is more restrictive, and Python-only.



Option 1: The Service Layer Takes

Events from the Model and Puts Them on

the Message Bus

Our domain model raises events, and our message bus will call the

right handlers whenever an event happens. Now all we need is to

connect the two. We need something to catch events from the model

and pass them to the message bus—the publishing step.

The simplest way to do this is by adding some code into our service

layer:

The service layer with an explicit message bus

(src/allocation/service\_layer/services.py)



from.import messagebus

...



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

product=uow.products.get(sku=line.sku)

if product is None:

raise InvalidSku(f'Invalid sku {line.sku}')

try :

batchref=product.allocate(line)

uow.commit()

return batchref

finally :

messagebus.handle(product.events)

We keep the try/finally from our ugly earlier implementation

(we haven’t gotten rid of all exceptions yet, just OutOfStock).

But now, instead of depending directly on an email infrastructure,

the service layer is just in charge of passing events from the model

up to the message bus.

That already avoids some of the ugliness that we had in our naive

implementation, and we have several systems that work like this one,

in which the service layer explicitly collects events from aggregates

and passes them to the message bus.

Option 2: The Service Layer Raises Its

Own Events

Another variant on this that we’ve used is to have the service layer in

charge of creating and raising events directly, rather than having them

raised by the domain model:

Service layer calls messagebus.handle directly

(src/allocation/service\_layer/services.py)



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

product=uow.products.get(sku=line.sku)

if product is None:

raise InvalidSku(f'Invalid sku {line.sku}')

batchref=product.allocate(line)

uow.commit()



if batchref is None:

messagebus.handle(events.OutOfStock(line.sku))

return batchref



As before, we commit even if we fail to allocate because the code

is simpler this way and it’s easier to reason about: we always

commit unless something goes wrong. Committing when we

haven’t changed anything is safe and keeps the code uncluttered.

Again, we have applications in production that implement the pattern

in this way. What works for you will depend on the particular trade-

offs you face, but we’d like to show you what we think is the most

elegant solution, in which we put the unit of work in charge of

collecting and raising events.

Option 3: The UoW Publishes Events to

the Message Bus

The UoW already has a try/finally, and it knows about all the

aggregates currently in play because it provides access to the

repository. So it’s a good place to spot events and pass them to the

message bus:

The UoW meets the message bus

(src/allocation/service\_layer/unit\_of\_work.py)



classAbstractUnitOfWork (abc.ABC):

...



def commit(self):

self.\_commit()

self.publish\_events()



def publish\_events(self):

for product in self.products.seen:

while product.events:

event=product.events.pop( 0 )

messagebus.handle(event)



@abc.abstractmethod



def \_commit(self):

raiseNotImplementedError



...



classSqlAlchemyUnitOfWork (AbstractUnitOfWork):

...



def \_commit(self):

self.session.commit()



We’ll change our commit method to require a private .\_commit()

method from subclasses.

After committing, we run through all the objects that our repository

has seen and pass their events to the message bus.

That relies on the repository keeping track of aggregates that have

been loaded using a new attribute, .seen, as you’ll see in the next

listing.

NOT E



Are you wondering what happens if one of the handlers fails? We’ll discuss error

handling in detail inChapter 10.



Repository tracks aggregates that pass through it

(src/allocation/adapters/repository.py)



classAbstractRepository (abc.ABC):



def \_\_init\_\_(self):

self.seen=set() # type: Set\[model.Product]



def add(self,product:model.Product):

self.\_add(product)



self.seen.add(product)



def get(self,sku)->model.Product:

product=self.\_get(sku)

if product:

self.seen.add(product)

return product



@abc.abstractmethod

def \_add(self,product:model.Product):

raiseNotImplementedError



@abc.abstractmethod

def \_get(self,sku)->model.Product:

raiseNotImplementedError



classSqlAlchemyRepository (AbstractRepository):



def \_\_init\_\_(self,session):

super().\_\_init\_\_()

self.session=session



def \_add(self,product):

self.session.add(product)



def \_get(self,sku):

return self.session.query(model.Product).filter\_by(sku=sku).first()



For the UoW to be able to publish new events, it needs to be able

to ask the repository for which Product objects have been used

during this session. We use a set called .seen to store them. That

means our implementations need to call super().init().

The parent add() method adds things to .seen, and now requires

subclasses to implement .\_add().

Similarly, .get() delegates to a .\_get() function, to be

implemented by subclasses, in order to capture objects seen.

NOT E



The use of .\_underscorey() methods and subclassing is definitely not the

only way you could implement these patterns. Have a go at theExercise for the

Readerin this chapter and experiment with some alternatives.



After the UoW and repository collaborate in this way to automatically

keep track of live objects and process their events, the service layer

can be totally free of event-handling concerns:

Service layer is clean again

(src/allocation/service\_layer/services.py)



def allocate(

orderid:str,sku:str,qty:int,

uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(orderid,sku,qty)

with uow:

product=uow.products.get(sku=line.sku)

if product is None:

raise InvalidSku(f'Invalid sku {line.sku}')

batchref=product.allocate(line)

uow.commit()

return batchref

We do also have to remember to change the fakes in the service layer

and make them call super() in the right places, and to implement

underscorey methods, but the changes are minimal:

Service-layer fakes need tweaking (tests/unit/test\_services.py)



classFakeRepository (repository.AbstractRepository):



def \_\_init\_\_(self,products):

super().\_\_init\_\_()

self.\_products=set(products)



def \_add(self,product):

self.\_products.add(product)



def \_get(self,sku):

return next((p for p in self.\_products if p.sku==sku),None)



...



classFakeUnitOfWork (unit\_of\_work.AbstractUnitOfWork):

...



def \_commit(self):

self.committed=True



EXERCISE FOR THE READER



Are you finding all those .\_add() and .\_commit() methods “super-gross,” in the words of our

beloved tech reviewer Hynek? Does it “make you want to beat Harry around the head with a

plushie snake”? Hey, our code listings are only meant to be examples, not the perfect solution!

Why not go see if you can do better?

One com position over inheritance way to go would be to implement a wrapper class:

A wrapper adds functionality and then delegates (src/adapters/repository.py)

classTrackingRepository :

seen:Set\[model.Product]

def \_\_init\_\_(self,repo:AbstractRepository):

self.seen=set() # type: Set\[model.Product]

self.\_repo=repo

def add(self,product:model.Product):

self.\_repo.add(product)

self.seen.add(product)

def get(self,sku)->model.Product:

product=self.\_repo.get(sku)

if product:

self.seen.add(product)

return product



By wrapping the repository, we can call the actual .add() and .get() methods, avoiding weird

underscorey methods.

See if you can apply a similar pattern to our UoW class in order to get rid of those Java-y

\_commit() methods too. You can find the code onGitHub.

Switching all the ABCs to typing.Protocol is a good way to force yourself to avoid using

inheritance. Let us know if you come up with something nice!



You might be starting to worry that maintaining these fakes is going to

be a maintenance burden. There’s no doubt that it is work, but in our

experience it’s not a lot of work. Once your project is up and running,

the interface for your repository and UoW abstractions really don’t

change much. And if you’re using ABCs, they’ll help remind you when

things get out of sync.

Wrap-Up

Domain events give us a way to handle workflows in our system. We

often find, listening to our domain experts, that they express

requirements in a causal or temporal way—for example, “When we try

to allocate stock but there’s none available, then we should send an

email to the buying team.”

The magic words “When X, then Y” often tell us about an event that

we can make concrete in our system. Treating events as first-class

things in our model helps us make our code more testable and

observable, and it helps isolate concerns.

AndTable 8-1shows the trade-offs as we see them.

Table 8-1. Domain events: the trade-offs



Pros Cons



A message bus gives us a

nice way to separate

responsibilities when we have

to take multiple actions in

response to a request.



Event handlers are nicely

decoupled from the “core”

application logic,

making it easy to change their

implementation later.



Domain events are a great

way to model the real world,

and we can use them

as part of our business

language when modeling with

stakeholders.



The message bus is an additional

thing to wrap your head around;

the implementation

in which the unit of work raises

events for us is neat but also

magic. It’s not

obvious when we call commit that

we’re also going to go and send

email to

people.



What’s more, that hidden event-

handling code executes

synchronously ,

meaning your service-layer

function

doesn’t finish until all the handlers

for any events are finished. That

could cause unexpected

performance problems in your

web endpoints

(adding asynchronous processing

is possible but makes things even

more confusing).



More generally, event-driven

workflows can be confusing

because after things

are split across a chain of multiple

handlers, there is no single place

in the system where you can

understand how a request will be

fulfilled.



Pros Cons



You also open yourself up to the

possibility of circular

dependencies between your

event handlers, and infinite loops.



Events are useful for more than just sending email, though. InChapter 7

we spent a lot of time convincing you that you should define

aggregates, or boundaries where we guarantee consistency. People

often ask, “What should I do if I need to change multiple aggregates as

part of a request?” Now we have the tools we need to answer that

question.

If we have two things that can be transactionally isolated (e.g., an

order and a product), then we can make them eventually consistent by

using events. When an order is canceled, we should find the products

that were allocated to it and remove the allocations.

DOMAIN EVENTS AND THE MESSAGE BUS RECAP



Events can help with the single responsibility principle

Code gets tangled up when we mix multiple concerns in one place. Events can help us to

keep things tidy by separating primary use cases from secondary ones. We also use events

for communicating between aggregates so that we don’t need to run long-running

transactions that lock against multiple tables.



A message bus routes messages to handlers

You can think of a message bus as a dict that maps from events to their consumers. It

doesn’t “know” anything about the meaning of events; it’s just a piece of dumb infrastructure

for getting messages around the system.



Option 1: Service layer raises events and passes them to message bus

The simplest way to start using events in your system is to raise them from handlers by

calling bus.handle(some\_new\_event) after you commit your unit of work.



Option 2: Domain model raises events, service layer passes them to message bus

The logic about when to raise an event really should live with the model, so we can improve

our system’s design and testability by raising events from the domain model. It’s easy for our

handlers to collect events off the model objects after commit and pass them to the bus.



Option 3: UoW collects events from aggregates and passes them to message bus

Adding bus.handle(aggregate.events) to every handler is annoying, so we can tidy up by

making our unit of work responsible for raising events that were raised by loaded objects.

This is the most complex design and might rely on ORM magic, but it’s clean and easy to

use once it’s set up.



InChapter 9, we’ll look at this idea in more detail as we build a more

complex workflow with our new message bus.



1 This principle is the S inSOLID.



2 Our tech reviewer Ed Jung likes to say that the move from imperative to event-based

flow control changes what used to be orchestration into choreography.



Chapter 9. Going to Town on

the Message Bus

In this chapter, we’ll start to make events more fundamental to the

internal structure of our application. We’ll move from the current state

inFigure 9-1, where events are an optional side effect...



Figure 9-1. Before: the message bus is an optional add-on



...to the situation inFigure 9-2, where everything goes via the message

bus, and our app has been transformed fundamentally into a message

processor.



Figure 9-2. The message bus is now the main entrypoint to the service layer



T IP



The code for this chapter is in the chapter\_09\_all\_messagebus branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_09\_all\_messagebus

\# or to code along, checkout the previous chapter:

git checkout chapter\_08\_events\_and\_message\_bus



A New Requirement Leads Us to a New

Architecture

Rich Hickey talks about situated software, meaning software that runs

for extended periods of time, managing a real-world process.

Examples include warehouse-management systems, logistics

schedulers, and payroll systems.

This software is tricky to write because unexpected things happen all

the time in the real world of physical objects and unreliable humans.

For example:

During a stock-take, we discover that three SPRINGY-

MATTRESSes have been water damaged by a leaky roof.

A consignment of RELIABLE-FORKs is missing the required

documentation and is held in customs for several weeks.

Three RELIABLE-FORKs subsequently fail safety testing and

are destroyed.

A global shortage of sequins means we’re unable to

manufacture our next batch of SPARKLY-BOOKCASE.

In these types of situations, we learn about the need to change batch

quantities when they’re already in the system. Perhaps someone made

a mistake on the number in the manifest, or perhaps some sofas fell off

a truck. Following a conversation with the business, we model the

situation as inFigure 9-3.



Figure 9-3. Batch quantity changed means deallocate and reallocate



An event we’ll call BatchQuantityChanged should lead us to change

the quantity on the batch, yes, but also to apply a business rule : if the

new quantity drops to less than the total already allocated, we need to

deallocate those orders from that batch. Then each one will require a

new allocation, which we can capture as an event called

AllocationRequired.

Perhaps you’re already anticipating that our internal message bus and

events can help implement this requirement. We could define a service

called change\_batch\_quantity that knows how to adjust batch

quantities and also how to deallocate any excess order lines, and then

each deallocation can emit an AllocationRequired event that can be

forwarded to the existing allocate service, in separate transactions.

1

Once again, our message bus helps us to enforce the single

responsibility principle, and it allows us to make choices about

transactions and data integrity.

Imagining an Architecture Change: Everything

Will Be an Event Handler

But before we jump in, think about where we’re headed. There are two

kinds of flows through our system:

API calls that are handled by a service-layer function

Internal events (which might be raised as a side effect of a

service-layer function) and their handlers (which in turn call

service-layer functions)

Wouldn’t it be easier if everything was an event handler? If we rethink

our API calls as capturing events, the service-layer functions can be

event handlers too, and we no longer need to make a distinction

between internal and external event handlers:

services.allocate() could be the handler for an

AllocationRequired event and could emit Allocated

events as its output.

services.add\_batch() could be the handler for a

BatchCreated event.

Our new requirement will fit the same pattern:

An event called BatchQuantityChanged can invoke a

handler called change\_batch\_quantity().

2

And the new AllocationRequired events that it may raise

can be passed on to services.allocate() too, so there is

no conceptual difference between a brand-new allocation

coming from the API and a reallocation that’s internally

triggered by a deallocation.

All sound like a bit much? Let’s work toward it all gradually. We’ll

follow thePreparatory Refactoringworkflow, aka “Make the change

easy; then make the easy change”:

1\. We refactor our service layer into event handlers. We can get

used to the idea of events being the way we describe inputs to

the system. In particular, the existing services.allocate()

function will become the handler for an event called

AllocationRequired.

2\. We build an end-to-end test that puts

BatchQuantityChanged events into the system and looks for

Allocated events coming out.

3\. Our implementation will conceptually be very simple: a new

handler for BatchQuantityChanged events, whose

implementation will emit AllocationRequired events,

which in turn will be handled by the exact same handler for

allocations that the API uses.

Along the way, we’ll make a small tweak to the message bus and UoW,

moving the responsibility for putting new events on the message bus

into the message bus itself.

Refactoring Service Functions to

Message Handlers

We start by defining the two events that capture our current API inputs

—AllocationRequired and BatchCreated:

BatchCreated and AllocationRequired events

(src/allocation/domain/events.py)



@dataclass

classBatchCreated (Event):

ref:str

sku:str

qty:int

eta:Optional\[date]=None



...



@dataclass

classAllocationRequired (Event):

orderid:str

sku:str

qty:int

Then we rename services.py to handlers.py ; we add the existing

message handler for send\_out\_of\_stock\_notification; and most

importantly, we change all the handlers so that they have the same

inputs, an event and a UoW:

Handlers and services are the same thing

(src/allocation/service\_layer/handlers.py)



def add\_batch(

event:events.BatchCreated,uow:unit\_of\_work.AbstractUnitOfWork

):

with uow:

product=uow.products.get(sku=event.sku)

...



def allocate(

event:events.AllocationRequired,uow:unit\_of\_work.AbstractUnitOfWork

)->str:

line=OrderLine(event.orderid,event.sku,event.qty)

...



def send\_out\_of\_stock\_notification(

event:events.OutOfStock,uow:unit\_of\_work.AbstractUnitOfWork,

):

email.send(

'stock@made.com',

f'Out of stock for {event.sku}',

)

The change might be clearer as a diff:

Changing from services to handlers

(src/allocation/service\_layer/handlers.py)



def add\_batch(



&#x20;   ref: str, sku: str, qty: int, eta: Optional\[date],

&#x20;   uow: unit\_of\_work.AbstractUnitOfWork



&#x20;   event: events.BatchCreated, uow: unit\_of\_work.AbstractUnitOfWork

&#x20;   ):

&#x20;   with uow:



&#x20;   product = uow.products.get(sku=sku)



&#x20;   product = uow.products.get(sku=event.sku)

&#x20;   ...



def allocate(



&#x20;   orderid: str, sku: str, qty: int,

&#x20;   uow: unit\_of\_work.AbstractUnitOfWork



&#x20;   event: events.AllocationRequired, uow: unit\_of\_work.AbstractUnitOfWork

&#x20;   ) -> str:



&#x20;   line = OrderLine(orderid, sku, qty)



&#x20;   line = OrderLine(event.orderid, event.sku, event.qty)

&#x20;   ...



+def send\_out\_of\_stock\_notification(



&#x20;   event: events.OutOfStock, uow: unit\_of\_work.AbstractUnitOfWork,

&#x20;   +):

&#x20;   email.send(

&#x20;   ...



Along the way, we’ve made our service-layer’s API more structured

and more consistent. It was a scattering of primitives, and now it uses

well-defined objects (see the following sidebar).

FROM DOMAIN OBJECTS, VIA PRIMITIVE OBSESSION, TO

EVENTS AS AN INTERFACE



Some of you may remember“Fully Decoupling the Service-Layer Tests from the Domain”, in

which we changed our service-layer API from being in terms of domain objects to primitives. And

now we’re moving back, but to different objects? What gives?

In OO circles, people talk about prim itive ob session as an anti-pattern: avoid primitives in public

APIs, and instead wrap them with custom value classes, they would say. In the Python world, a lot

of people would be quite skeptical of that as a rule of thumb. When mindlessly applied, it’s

certainly a recipe for unnecessary complexity. So that’s not what we’re doing per se.

The move from domain objects to primitives bought us a nice bit of decoupling: our client code

was no longer coupled directly to the domain, so the service layer could present an API that stays

the same even if we decide to make changes to our model, and vice versa.

So have we gone backward? Well, our core domain model objects are still free to vary, but

instead we’ve coupled the external world to our event classes. They’re part of the domain too, but

the hope is that they vary less often, so they’re a sensible artifact to couple on.

And what have we bought ourselves? Now, when invoking a use case in our application, we no

longer need to remember a particular combination of primitives, but just a single event class that

represents the input to our application. That’s conceptually quite nice. On top of that, as you’ll see

inAppendix E, those event classes can be a nice place to do some input validation.



The Message Bus Now Collects Events from the

UoW

Our event handlers now need a UoW. In addition, as our message bus

becomes more central to our application, it makes sense to put it

explicitly in charge of collecting and processing new events. There

was a bit of a circular dependency between the UoW and message bus

until now, so this will make it one-way:

Handle takes a UoW and manages a queue

(src/allocation/service\_layer/messagebus.py)



def handle(event:events.Event,uow:unit\_of\_work.AbstractUnitOfWork):

queue=\[event]

while queue:

event=queue.pop( 0 )

for handler in HANDLERS\[type(event)]:

handler(event,uow=uow)

queue.extend(uow.collect\_new\_events())

The message bus now gets passed the UoW each time it starts up.

When we begin handling our first event, we start a queue.

We pop events from the front of the queue and invoke their

handlers (the HANDLERS dict hasn’t changed; it still maps event

types to handler functions).

The message bus passes the UoW down to each handler.

After each handler finishes, we collect any new events that have

been generated and add them to the queue.

In unit\_of\_work.py , publish\_events() becomes a less active

method, collect\_new\_events():

UoW no longer puts events directly on the bus

(src/allocation/service\_layer/unit\_of\_work.py)



\-from. import messagebus



class AbstractUnitOfWork(abc.ABC):

@@ -23,13 +21,11 @@ class AbstractUnitOfWork(abc.ABC):



def commit(self):

self.\_commit()



&#x20;   self.publish\_events()

&#x20;   def publish\_events(self):



&#x20;   def collect\_new\_events(self):

&#x20;   for product in self.products.seen:

&#x20;   while product.events:



&#x20;   event = product.events.pop(0)

&#x20;   messagebus.handle(event)



&#x20;   yield product.events.pop(0)



The unit\_of\_work module now no longer depends on

messagebus.

We no longer publish\_events automatically on commit. The

message bus is keeping track of the event queue instead.

And the UoW no longer actively puts events on the message bus; it

just makes them available.

Our Tests Are All Written in Terms of Events Too

Our tests now operate by creating events and putting them on the

message bus, rather than invoking service-layer functions directly:

Handler tests use events (tests/unit/test\_handlers.py)



class TestAddBatch:



def test\_for\_new\_product(self):

uow = FakeUnitOfWork()



&#x20;   services.add\_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)



&#x20;   messagebus.handle(

&#x20;   events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow

&#x20;   )

&#x20;   assert uow.products.get("CRUNCHY-ARMCHAIR") is not None



assert uow.committed



...



class TestAllocate:



def test\_returns\_allocation(self):

uow = FakeUnitOfWork()



&#x20;   services.add\_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)

&#x20;   result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)



&#x20;   messagebus.handle(

&#x20;   events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow

&#x20;   )

&#x20;   result = messagebus.handle(

&#x20;   events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow

&#x20;   )

&#x20;   assert result == "batch1"



A Temporary Ugly Hack: The Message Bus Has to

Return Results

Our API and our service layer currently want to know the allocated

batch reference when they invoke our allocate() handler. This

means we need to put in a temporary hack on our message bus to let it

return events:

Message bus returns results

(src/allocation/service\_layer/messagebus.py)



def handle(event: events.Event, uow: unit\_of\_work.AbstractUnitOfWork):



&#x20;   results = \[]

&#x20;   queue = \[event]

&#x20;   while queue:

&#x20;   event = queue.pop(0)

&#x20;   for handler in HANDLERS\[type(event)]:



&#x20;   handler(event, uow=uow)



&#x20;   results.append(handler(event, uow=uow))

&#x20;   queue.extend(uow.collect\_new\_events())

&#x20;   return results



It’s because we’re mixing the read and write responsibilities in our

system. We’ll come back to fix this wart inChapter 12.

Modifying Our API to Work with Events

Flask changing to message bus as a diff

(src/allocation/entrypoints/flask\_app.py)



@app.route("/allocate", methods=\['POST'])

def allocate\_endpoint():

try:



&#x20;   batchref = services.allocate(

&#x20;   request.json\['orderid'],

&#x20;   request.json\['sku'],

&#x20;   request.json\['qty'],

&#x20;   unit\_of\_work.SqlAlchemyUnitOfWork(),



&#x20;   event = events.AllocationRequired(



&#x20;   request.json\['orderid'], request.json\['sku'], request.json\['qty'],

&#x20;   )



&#x20;   results = messagebus.handle(event, unit\_of\_work.SqlAlchemyUnitOfWork())



&#x20;   batchref = results.pop(0)

&#x20;   except InvalidSku as e:



Instead of calling the service layer with a bunch of primitives

extracted from the request JSON...

We instantiate an event.

Then we pass it to the message bus.

And we should be back to a fully functional application, but one that’s

now fully event-driven:

What used to be service-layer functions are now event

handlers.

That makes them the same as the functions we invoke for

handling internal events raised by our domain model.

We use events as our data structure for capturing inputs to the

system, as well as for handing off of internal work packages.

The entire app is now best described as a message processor,

or an event processor if you prefer. We’ll talk about the

distinction in thenext chapter.

Implementing Our New Requirement

We’re done with our refactoring phase. Let’s see if we really have

“made the change easy.” Let’s implement our new requirement, shown

inFigure 9-4: we’ll receive as our inputs some new

BatchQuantityChanged events and pass them to a handler, which in

turn might emit some AllocationRequired events, and those in turn

will go back to our existing handler for reallocation.



Figure 9-4. Sequence diagram for reallocation flow



WARNING



When you split things out like this across two units of work, you now have two

database transactions, so you are opening yourself up to integrity issues:

something could happen that means the first transaction completes but the second

one does not. You’ll need to think about whether this is acceptable, and whether

you need to notice when it happens and do something about it. See“Footguns”for

more discussion.



Our New Event

The event that tells us a batch quantity has changed is simple; it just

needs a batch reference and a new quantity:

New event (src/allocation/domain/events.py)



@dataclass

classBatchQuantityChanged (Event):

ref:str

qty:int

Test-Driving a New Handler

Following the lessons learned inChapter 4, we can operate in “high

gear” and write our unit tests at the highest possible level of

abstraction, in terms of events. Here’s what they might look like:

Handler tests for change\_batch\_quantity

(tests/unit/test\_handlers.py)



classTestChangeBatchQuantity :



def test\_changes\_available\_quantity(self):

uow=FakeUnitOfWork()

messagebus.handle(

events.BatchCreated("batch1","ADORABLE-SETTEE", 100 ,None),uow

)

\[batch]=uow.products.get(sku="ADORABLE-SETTEE").batches

assert batch.available\_quantity== 100



messagebus.handle(events.BatchQuantityChanged("batch1", 50 ),uow)



assert batch.available\_quantity== 50



def test\_reallocates\_if\_necessary(self):

uow=FakeUnitOfWork()

event\_history=\[

events.BatchCreated("batch1","INDIFFERENT-TABLE", 50 ,None),

events.BatchCreated("batch2","INDIFFERENT-TABLE", 50 ,

date.today()),

events.AllocationRequired("order1","INDIFFERENT-TABLE", 20 ),

events.AllocationRequired("order2","INDIFFERENT-TABLE", 20 ),

]

for e in event\_history:

messagebus.handle(e,uow)

\[batch1,batch2]=uow.products.get(sku="INDIFFERENT-TABLE").batches

assert batch1.available\_quantity== 10

assert batch2.available\_quantity== 50



messagebus.handle(events.BatchQuantityChanged("batch1", 25 ),uow)



\# order1 or order2 will be deallocated, so we'll have 25 - 20

assert batch1.available\_quantity== 5

\# and 20 will be reallocated to the next batch

assert batch2.available\_quantity== 30



The simple case would be trivially easy to implement; we just

modify a quantity.

But if we try to change the quantity to less than has been allocated,

we’ll need to deallocate at least one order, and we expect to

reallocate it to a new batch.

Implementation

Our new handler is very simple:

Handler delegates to model layer

(src/allocation/service\_layer/handlers.py)



def change\_batch\_quantity(

event:events.BatchQuantityChanged,uow:unit\_of\_work.AbstractUnitOfWork

):

with uow:

product=uow.products.get\_by\_batchref(batchref=event.ref)

product.change\_batch\_quantity(ref=event.ref,qty=event.qty)

uow.commit()

We realize we’ll need a new query type on our repository:

A new query type on our repository

(src/allocation/adapters/repository.py)



classAbstractRepository (abc.ABC):

...



def get(self,sku)->model.Product:

...



def get\_by\_batchref(self,batchref)->model.Product:

product=self.\_get\_by\_batchref(batchref)

if product:

self.seen.add(product)

return product



@abc.abstractmethod



def \_add(self,product:model.Product):

raiseNotImplementedError



@abc.abstractmethod

def \_get(self,sku)->model.Product:

raiseNotImplementedError



@abc.abstractmethod

def \_get\_by\_batchref(self,batchref)->model.Product:

raiseNotImplementedError

...



classSqlAlchemyRepository (AbstractRepository):

...



def \_get(self,sku):

return self.session.query(model.Product).filter\_by(sku=sku).first()



def \_get\_by\_batchref(self,batchref):

return self.session.query(model.Product).join(model.Batch).filter(

orm.batches.c.reference==batchref,

).first()



And on our FakeRepository too:

Updating the fake repo too (tests/unit/test\_handlers.py)



classFakeRepository (repository.AbstractRepository):

...



def \_get(self,sku):

return next((p for p in self.\_products if p.sku==sku),None)



def \_get\_by\_batchref(self,batchref):

return next((

p for p in self.\_products for b in p.batches

if b.reference==batchref

),None)



NOT E



We’re adding a query to our repository to make this use case easier to implement.

So long as our query is returning a single aggregate, we’re not bending any rules.

If you find yourself writing complex queries on your repositories, you might want

to consider a different design. Methods like get\_most\_popular\_products or

find\_products\_by\_order\_id in particular would definitely trigger our spidey

sense.Chapter 11and theepiloguehave some tips on managing complex queries.



A New Method on the Domain Model

We add the new method to the model, which does the quantity change

and deallocation(s) inline and publishes a new event. We also modify

the existing allocate function to publish an event:

Our model evolves to capture the new requirement

(src/allocation/domain/model.py)



classProduct :

...



def change\_batch\_quantity(self,ref:str,qty:int):

batch=next(b for b in self.batches if b.reference==ref)

batch.\_purchased\_quantity=qty

while batch.available\_quantity< 0 :

line=batch.deallocate\_one()

self.events.append(

events.AllocationRequired(line.orderid,line.sku,line.qty)

)

...



classBatch :

...



def deallocate\_one(self)->OrderLine:

return self.\_allocations.pop()



We wire up our new handler:

The message bus grows

(src/allocation/service\_layer/messagebus.py)

HANDLERS={



events.BatchCreated: \[handlers.add\_batch],

events.BatchQuantityChanged: \[handlers.change\_batch\_quantity],

events.AllocationRequired: \[handlers.allocate],

events.OutOfStock: \[handlers.send\_out\_of\_stock\_notification],



} # type: Dict\[Type\[events.Event], List\[Callable]]

And our new requirement is fully implemented.

Optionally: Unit Testing Event Handlers in

Isolation with a Fake Message Bus

Our main test for the reallocation workflow is edge-to-edge (see the

example code in“Test-Driving a New Handler”). It uses the real

message bus, and it tests the whole flow, where the

BatchQuantityChanged event handler triggers deallocation, and

emits new AllocationRequired events, which in turn are handled by

their own handlers. One test covers a chain of multiple events and

handlers.

Depending on the complexity of your chain of events, you may decide

that you want to test some handlers in isolation from one another. You

can do this using a “fake” message bus.

In our case, we actually intervene by modifying the

publish\_events() method on FakeUnitOfWork and decoupling it

from the real message bus, instead making it record what events it

sees:

Fake message bus implemented in UoW (tests/unit/test\_handlers.py)



classFakeUnitOfWorkWithFakeMessageBus (FakeUnitOfWork):



def \_\_init\_\_(self):

super().\_\_init\_\_()

self.events\_published=\[] # type: List\[events.Event]



def publish\_events(self):

for product in self.products.seen:

while product.events:

self.events\_published.append(product.events.pop( 0 ))



Now when we invoke messagebus.handle() using the

FakeUnitOfWorkWithFakeMessageBus, it runs only the handler for

that event. So we can write a more isolated unit test: instead of

checking all the side effects, we just check that

BatchQuantityChanged leads to AllocationRequired if the

quantity drops below the total already allocated:

Testing reallocation in isolation (tests/unit/test\_handlers.py)



def test\_reallocates\_if\_necessary\_isolated():

uow=FakeUnitOfWorkWithFakeMessageBus()



\# test setup as before

event\_history=\[

events.BatchCreated("batch1","INDIFFERENT-TABLE", 50 ,None),

events.BatchCreated("batch2","INDIFFERENT-TABLE", 50 ,date.today()),

events.AllocationRequired("order1","INDIFFERENT-TABLE", 20 ),



events.AllocationRequired("order2","INDIFFERENT-TABLE", 20 ),

]

for e in event\_history:

messagebus.handle(e,uow)

\[batch1,batch2]=uow.products.get(sku="INDIFFERENT-TABLE").batches

assert batch1.available\_quantity== 10

assert batch2.available\_quantity== 50



messagebus.handle(events.BatchQuantityChanged("batch1", 25 ),uow)



\# assert on new events emitted rather than downstream side-effects

\[reallocation\_event]=uow.events\_published

assert isinstance(reallocation\_event,events.AllocationRequired)

assert reallocation\_event.orderid in {'order1','order2'}

assert reallocation\_event.sku=='INDIFFERENT-TABLE'



Whether you want to do this or not depends on the complexity of your

chain of events. We say, start out with edge-to-edge testing, and resort

to this only if necessary.

EXERCISE FOR THE READER



A great way to force yourself to really understand some code is to refactor it. In the discussion of

testing handlers in isolation, we used something called FakeUnitOfWorkWithFakeMessageBus,

which is unnecessarily complicated and violates the SRP.

If we change the message bus to being a class, then building a FakeMessageBus is more

straightforward:

An ab stract m essage b us and its real and fak e versions

classAbstractMessageBus :

HANDLERS:Dict\[Type\[events.Event],List\[Callable]]

def handle(self,event:events.Event):

for handler in self.HANDLERS\[type(event)]:

handler(event)



classMessageBus (AbstractMessageBus):

HANDLERS={

events.OutOfStock: \[send\_out\_of\_stock\_notification],

}



classFakeMessageBus (messagebus.AbstractMessageBus):

def \_\_init\_\_(self):

self.events\_published=\[] # type: List\[events.Event]

self.handlers={

events.OutOfStock: \[ lambda e:self.events\_published.append(e)]

}

So jump into the code onGitHuband see if you can get a class-based version working, and then

write a version of test\_reallocates\_if\_necessary\_isolated() from earlier.

We use a class-based message bus inChapter 13, if you need more inspiration.



Wrap-Up

Let’s look back at what we’ve achieved, and think about why we did

it.

What Have We Achieved?



3



Events are simple dataclasses that define the data structures for inputs

and internal messages within our system. This is quite powerful from a

DDD standpoint, since events often translate really well into business

language (look up event storming if you haven’t already).

Handlers are the way we react to events. They can call down to our

model or call out to external services. We can define multiple handlers

for a single event if we want to. Handlers can also raise other events.

This allows us to be very granular about what a handler does and

really stick to the SRP.

Why Have We Achieved?

Our ongoing objective with these architectural patterns is to try to have

the complexity of our application grow more slowly than its size.

When we go all in on the message bus, as always we pay a price in

terms of architectural complexity (seeTable 9-1), but we buy

ourselves a pattern that can handle almost arbitrarily complex

requirements without needing any further conceptual or architectural

change to the way we do things.

Here we’ve added quite a complicated use case (change quantity,

deallocate, start new transaction, reallocate, publish external

notification), but architecturally, there’s been no cost in terms of

complexity. We’ve added new events, new handlers, and a new

external adapter (for email), all of which are existing categories of

things in our architecture that we understand and know how to reason

about, and that are easy to explain to newcomers. Our moving parts

each have one job, they’re connected to each other in well-defined

ways, and there are no unexpected side effects.

Table 9-1. Whole app is a message bus: the trade-offs



Pros Cons



Handlers

and

services

are the

same thing,

so that’s

simpler.



We have a

nice data

structure

for inputs

to the

system.



A message bus is still a slightly unpredictable way of

doing things from

a web point of view. You don’t know in advance

when things are going to end.



There will be duplication of fields and structure

between model objects and events, which will have a

maintenance cost. Adding a field to one usually

means adding a field to at least

one of the others.



Now, you may be wondering, where are those

BatchQuantityChanged events going to come from? The answer is

revealed in a couple chapters’ time. But first, let’s talk aboutevents

versus commands.



1 Event-based modeling is so popular that a practice called event storming has been

developed for facilitating event-based requirements gathering and domain model



elaboration.



2 If you’ve done a bit of reading about event-driven architectures, you may be thinking,

“Some of these events sound more like commands!” Bear with us! We’re trying to

introduce one concept at a time. In thenext chapter, we’ll introduce the distinction

between commands and events.



3 The “simple” implementation in this chapter essentially uses the messagebus.py module

itself to implement the Singleton Pattern.

Chapter 10. Commands and

Command Handler

In the previous chapter, we talked about using events as a way of

representing the inputs to our system, and we turned our application

into a message-processing machine.

To achieve that, we converted all our use-case functions to event

handlers. When the API receives a POST to create a new batch, it

builds a new BatchCreated event and handles it as if it were an

internal event. This might feel counterintuitive. After all, the batch

hasn’t been created yet; that’s why we called the API. We’re going to

fix that conceptual wart by introducing commands and showing how

they can be handled by the same message bus but with slightly different

rules.

T IP



The code for this chapter is in the chapter\_10\_commands branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_10\_commands

\# or to code along, checkout the previous chapter:

git checkout chapter\_09\_all\_messagebus



Commands and Events

Like events, commands are a type of message—instructions sent by

one part of a system to another. We usually represent commands with

dumb data structures and can handle them in much the same way as

events.

The differences between commands and events, though, are important.

Commands are sent by one actor to another specific actor with the

expectation that a particular thing will happen as a result. When we

post a form to an API handler, we are sending a command. We name

commands with imperative mood verb phrases like “allocate stock” or

“delay shipment.”

Commands capture intent. They express our wish for the system to do

something. As a result, when they fail, the sender needs to receive

error information.

Events are broadcast by an actor to all interested listeners. When we

publish BatchQuantityChanged, we don’t know who’s going to pick

it up. We name events with past-tense verb phrases like “order

allocated to stock” or “shipment delayed.”

We often use events to spread the knowledge about successful

commands.

Events capture facts about things that happened in the past. Since we

don’t know who’s handling an event, senders should not care whether

the receivers succeeded or failed.Table 10-1recaps the differences.

Table 10-1. Events versus commands



Event Command



Named Past tense Imperative mood



Error handling Fail independently Fail noisily



Sent to All listeners One recipient



What kinds of commands do we have in our system right now?

Pulling out some commands (src/allocation/domain/commands.py)



classCommand :

pass



@dataclass

classAllocate (Command):

orderid:str

sku:str

qty:int



@dataclass

classCreateBatch (Command):

ref:str

sku:str

qty:int

eta:Optional\[date]=None



@dataclass

classChangeBatchQuantity (Command):

ref:str

qty:int

commands.Allocate will replace

events.AllocationRequired.

commands.CreateBatch will replace events.BatchCreated.

commands.ChangeBatchQuantity will replace

events.BatchQuantityChanged.

Differences in Exception Handling

Just changing the names and verbs is all very well, but that won’t

change the behavior of our system. We want to treat events and

commands similarly, but not exactly the same. Let’s see how our

message bus changes:

Dispatch events and commands differently

(src/allocation/service\_layer/messagebus.py)



Message=Union\[commands.Command,events.Event]



def handle(message:Message,uow:unit\_of\_work.AbstractUnitOfWork):

results=\[]

queue=\[message]

while queue:

message=queue.pop( 0 )

if isinstance(message,events.Event):

handle\_event(message,queue,uow)

elif isinstance(message,commands.Command):

cmd\_result=handle\_command(message,queue,uow)

results.append(cmd\_result)

else :

raiseException (f'{message} was not an Event or Command')

return results

It still has a main handle() entrypoint that takes a message, which

may be a command or an event.

We dispatch events and commands to two different helper

functions, shown next.

Here’s how we handle events:

Events cannot interrupt the flow

(src/allocation/service\_layer/messagebus.py)



def handle\_event(

event:events.Event,

queue:List\[Message],

uow:unit\_of\_work.AbstractUnitOfWork

):

for handler in EVENT\_HANDLERS\[type(event)]:

try :

logger.debug('handling event%swith handler%s',event,handler)

handler(event,uow=uow)

queue.extend(uow.collect\_new\_events())

exceptException :

logger.exception('Exception handling event%s',event)

continue

Events go to a dispatcher that can delegate to multiple handlers per

event.

It catches and logs errors but doesn’t let them interrupt message

processing.

And here’s how we do commands:

Commands reraise exceptions

(src/allocation/service\_layer/messagebus.py)



def handle\_command(

command:commands.Command,

queue:List\[Message],



uow:unit\_of\_work.AbstractUnitOfWork

):

logger.debug('handling command%s',command)

try :

handler=COMMAND\_HANDLERS\[type(command)]

result=handler(command,uow=uow)

queue.extend(uow.collect\_new\_events())

return result

exceptException :

logger.exception('Exception handling command%s',command)

raise

The command dispatcher expects just one handler per command.

If any errors are raised, they fail fast and will bubble up.

return result is only temporary; as mentioned in“A Temporary

Ugly Hack: The Message Bus Has to Return Results”, it’s a

temporary hack to allow the message bus to return the batch

reference for the API to use. We’ll fix this inChapter 12.

We also change the single HANDLERS dict into different ones for

commands and events. Commands can have only one handler,

according to our convention:

New handlers dicts (src/allocation/service\_layer/messagebus.py)

EVENT\_HANDLERS={



events.OutOfStock: \[handlers.send\_out\_of\_stock\_notification],

} # type: Dict\[Type\[events.Event], List\[Callable]]



COMMAND\_HANDLERS={

commands.Allocate:handlers.allocate,

commands.CreateBatch:handlers.add\_batch,

commands.ChangeBatchQuantity:handlers.change\_batch\_quantity,

} # type: Dict\[Type\[commands.Command], Callable]

Discussion: Events, Commands, and

Error Handling

Many developers get uncomfortable at this point and ask, “What

happens when an event fails to process? How am I supposed to make

sure the system is in a consistent state?” If we manage to process half

of the events during messagebus.handle before an out-of-memory

error kills our process, how do we mitigate problems caused by the

lost messages?

Let’s start with the worst case: we fail to handle an event, and the

system is left in an inconsistent state. What kind of error would cause

this? Often in our systems we can end up in an inconsistent state when

only half an operation is completed.

For example, we could allocate three units of DESIRABLE\_BEANBAG to

a customer’s order but somehow fail to reduce the amount of remaining

stock. This would cause an inconsistent state: the three units of stock

are both allocated and available, depending on how you look at it.

Later, we might allocate those same beanbags to another customer,

causing a headache for customer support.

In our allocation service, though, we’ve already taken steps to prevent

that happening. We’ve carefully identified aggregates that act as

consistency boundaries, and we’ve introduced a UoW that manages the

atomic success or failure of an update to an aggregate.

For example, when we allocate stock to an order, our consistency

boundary is the Product aggregate. This means that we can’t

accidentally overallocate: either a particular order line is allocated to

the product, or it is not—there’s no room for inconsistent states.

By definition, we don’t require two aggregates to be immediately

consistent, so if we fail to process an event and update only a single

aggregate, our system can still be made eventually consistent. We

shouldn’t violate any constraints of the system.

With this example in mind, we can better understand the reason for

splitting messages into commands and events. When a user wants to

make the system do something, we represent their request as a

command. That command should modify a single aggregate and either

succeed or fail in totality. Any other bookkeeping, cleanup, and

notification we need to do can happen via an event. We don’t require

the event handlers to succeed in order for the command to be

successful.

Let’s look at another example (from a different, imaginary projet) to

see why not.

Imagine we are building an ecommerce website that sells expensive

luxury goods. Our marketing department wants to reward customers for

repeat visits. We will flag customers as VIPs after they make their

third purchase, and this will entitle them to priority treatment and

special offers. Our acceptance criteria for this story reads as follows:



Given a customer with two orders in their history,

When the customer places a third order,

Then they should be flagged as a VIP.



When a customer first becomes a VIP

Then we should send them an email to congratulate them



Using the techniques we’ve already discussed in this book, we decide

that we want to build a new History aggregate that records orders and

can raise domain events when rules are met. We will structure the code

like this:

VIP customer (example code for a different project)



classHistory : # Aggregate



def \_\_init\_\_(self,customer\_id:int):

self.orders=set() # Set\[HistoryEntry]

self.customer\_id=customer\_id



def record\_order(self,order\_id:str,order\_amount:int):

entry=HistoryEntry(order\_id,order\_amount)



if entry in self.orders:

return



self.orders.add(entry)



if len(self.orders)== 3 :

self.events.append(

CustomerBecameVIP(self.customer\_id)

)



def create\_order\_from\_basket(uow,cmd:CreateOrder):

with uow:

order=Order.from\_basket(cmd.customer\_id,cmd.basket\_items)

uow.orders.add(order)

uow.commit() # raises OrderCreated



def update\_customer\_history(uow,event:OrderCreated):

with uow:

history=uow.order\_history.get(event.customer\_id)

history.record\_order(event.order\_id,event.order\_amount)

uow.commit() # raises CustomerBecameVIP



def congratulate\_vip\_customer(uow,event:CustomerBecameVip):

with uow:

customer=uow.customers.get(event.customer\_id)

email.send(

customer.email\_address,

f'Congratulations {customer.first\_name}!'

)

The History aggregate captures the rules indicating when a

customer becomes a VIP. This puts us in a good place to handle

changes when the rules become more complex in the future.

Our first handler creates an order for the customer and raises a

domain event OrderCreated.

Our second handler updates the History object to record that an

order was created.

Finally, we send an email to the customer when they become a VIP.

Using this code, we can gain some intuition about error handling in an

event-driven system.

In our current implementation, we raise events about an aggregate after

we persist our state to the database. What if we raised those events

before we persisted, and committed all our changes at the same time?

That way, we could be sure that all the work was complete. Wouldn’t

that be safer?

What happens, though, if the email server is slightly overloaded? If all

the work has to complete at the same time, a busy email server can

stop us from taking money for orders.

What happens if there is a bug in the implementation of the History

aggregate? Should we fail to take your money just because we can’t

recognize you as a VIP?

By separating out these concerns, we have made it possible for things

to fail in isolation, which improves the overall reliability of the

system. The only part of this code that has to complete is the command

handler that creates an order. This is the only part that a customer cares

about, and it’s the part that our business stakeholders should prioritize.

Notice how we’ve deliberately aligned our transactional boundaries to

the start and end of the business processes. The names that we use in

the code match the jargon used by our business stakeholders, and the

handlers we’ve written match the steps of our natural language

acceptance criteria. This concordance of names and structure helps us

to reason about our systems as they grow larger and more complex.

Recovering from Errors Synchronously

Hopefully we’ve convinced you that it’s OK for events to fail

independently from the commands that raised them. What should we

do, then, to make sure we can recover from errors when they

inevitably occur?

The first thing we need is to know when an error has occurred, and for

that we usually rely on logs.

Let’s look again at the handle\_event method from our message bus:

Current handle function

(src/allocation/service\_layer/messagebus.py)



def handle\_event(

event:events.Event,

queue:List\[Message],

uow:unit\_of\_work.AbstractUnitOfWork

):

for handler in EVENT\_HANDLERS\[type(event)]:

try :

logger.debug('handling event%swith handler%s',event,handler)

handler(event,uow=uow)

queue.extend(uow.collect\_new\_events())

exceptException :

logger.exception('Exception handling event%s',event)

continue

When we handle a message in our system, the first thing we do is write

a log line to record what we’re about to do. For our

CustomerBecameVIP use case, the logs might read as follows:



Handling event CustomerBecameVIP(customer\_id=12345)

with handler <function congratulate\_vip\_customer at 0x10ebc9a60>



Because we’ve chosen to use dataclasses for our message types, we

get a neatly printed summary of the incoming data that we can copy and

paste into a Python shell to re-create the object.

When an error occurs, we can use the logged data to either reproduce

the problem in a unit test or replay the message into the system.

Manual replay works well for cases where we need to fix a bug before

we can re-process an event, but our systems will always experience

some background level of transient failure. This includes things like

network hiccups, table deadlocks, and brief downtime caused by

deployments.

For most of those cases, we can recover elegantly by trying again. As

the proverb says, “If at first you don’t succeed, retry the operation with

an exponentially increasing back-off period.”

Handle with retry (src/allocation/service\_layer/messagebus.py)



fromtenacityimport Retrying,RetryError,stop\_after\_attempt,wait\_exponential

...



def handle\_event(

event:events.Event,

queue:List\[Message],

uow:unit\_of\_work.AbstractUnitOfWork

):



for handler in EVENT\_HANDLERS\[type(event)]:

try :

for attempt in Retrying(

stop=stop\_after\_attempt( 3 ),

wait=wait\_exponential()

):



with attempt:

logger.debug('handling event%swith handler%s',event,

handler)

handler(event,uow=uow)

queue.extend(uow.collect\_new\_events())

except RetryError as retry\_failure:

logger.error(

'Failed to handle event%stimes, giving up!,

retry\_failure.last\_attempt.attempt\_number

)

continue

Tenacity is a Python library that implements common patterns for

retrying.

Here we configure our message bus to retry operations up to three

times, with an exponentially increasing wait between attempts.

Retrying operations that might fail is probably the single best way to

improve the resilience of our software. Again, the Unit of Work and

Command Handler patterns mean that each attempt starts from a

consistent state and won’t leave things half-finished.

WARNING



At some point, regardless of tenacity, we’ll have to give up trying to process the

message. Building reliable systems with distributed messages is hard, and we have

to skim over some tricky bits. There are pointers to more reference materials in

theepilogue.



Wrap-Up

In this book we decided to introduce the concept of events before the

concept of commands, but other guides often do it the other way

around. Making explicit the requests that our system can respond to by

giving them a name and their own data structure is quite a fundamental

thing to do. You’ll sometimes see people use the name Command

Handler pattern to describe what we’re doing with Events,

Commands, and Message Bus.

Table 10-2discusses some of the things you should think about before

you jump on board.

Table 10-2. Splitting commands and events: the trade-offs



Pros Cons



Treating commands and events

differently helps us understand

which things

have to succeed and which

things we can tidy up later.



CreateBatch is definitely a

less confusing name than Batc

hCreated. We are

being explicit about the intent

of our users, and explicit is

better than

implicit, right?



The semantic differences

between commands and events

can be subtle. Expect

bikeshedding arguments over the

differences.



We’re expressly inviting failure.

We know that sometimes things

will break, and

we’re choosing to handle that by

making the failures smaller and

more isolated.

This can make the system harder

to reason about and requires

better monitoring.



InChapter 11we’ll talk about using events as an integration pattern.

Chapter 11. Event-Driven

Architecture: Using Events to

Integrate Microservices

In the preceding chapter, we never actually spoke about how we would

receive the “batch quantity changed” events, or indeed, how we might

notify the outside world about reallocations.

We have a microservice with a web API, but what about other ways of

talking to other systems? How will we know if, say, a shipment is

delayed or the quantity is amended? How will we tell the warehouse

system that an order has been allocated and needs to be sent to a

customer?

In this chapter, we’d like to show how the events metaphor can be

extended to encompass the way that we handle incoming and outgoing

messages from the system. Internally, the core of our application is

now a message processor. Let’s follow through on that so it becomes a

message processor externally as well. As shown inFigure 11-1, our

application will receive events from external sources via an external

message bus (we’ll use Redis pub/sub queues as an example) and

publish its outputs, in the form of events, back there as well.



Figure 11-1. Our application is a message processor



T IP



The code for this chapter is in the chapter\_11\_external\_events branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_11\_external\_events

\# or to code along, checkout the previous chapter:

git checkout chapter\_10\_commands



Distributed Ball of Mud, and Thinking in

Nouns

Before we get into that, let’s talk about the alternatives. We regularly

talk to engineers who are trying to build out a microservices

architecture. Often they are migrating from an existing application, and

their first instinct is to split their system into nouns.

What nouns have we introduced so far in our system? Well, we have

batches of stock, orders, products, and customers. So a naive attempt

at breaking up the system might have looked likeFigure 11-2(notice

that we’ve named our system after a noun, Batches , instead of

Allocation ).



Figure 11-2. Context diagram with noun-based services



Each “thing” in our system has an associated service, which exposes

an HTTP API.

Let’s work through an example happy-path flow inFigure 11-3: our

users visit a website and can choose from products that are in stock.

When they add an item to their basket, we will reserve some stock for

them. When an order is complete, we confirm the reservation, which

causes us to send dispatch instructions to the warehouse. Let’s also

say, if this is the customer’s third order, we want to update the

customer record to flag them as a VIP.



Figure 11-3. Command flow 1



We can think of each of these steps as a command in our system:

ReserveStock, ConfirmReservation, DispatchGoods,

MakeCustomerVIP, and so forth.

This style of architecture, where we create a microservice per

database table and treat our HTTP APIs as CRUD interfaces to anemic

models, is the most common initial way for people to approach

service-oriented design.

This works fine for systems that are very simple, but it can quickly

degrade into a distributed ball of mud.

To see why, let’s consider another case. Sometimes, when stock

arrives at the warehouse, we discover that items have been water

damaged during transit. We can’t sell water-damaged sofas, so we

have to throw them away and request more stock from our partners. We

also need to update our stock model, and that might mean we need to

reallocate a customer’s order.

Where does this logic go?

Well, the Warehouse system knows that the stock has been damaged, so

maybe it should own this process, as shown inFigure 11-4.



Figure 11-4. Command flow 2



This sort of works too, but now our dependency graph is a mess. To

allocate stock, the Orders service drives the Batches system, which

drives Warehouse; but in order to handle problems at the warehouse,

our Warehouse system drives Batches, which drives Orders.

Multiply this by all the other workflows we need to provide, and you

can see how services quickly get tangled up.

Error Handling in Distributed Systems

“Things break” is a universal law of software engineering. What

happens in our system when one of our requests fails? Let’s say that a

network error happens right after we take a user’s order for three

MISBEGOTTEN-RUG, as shown inFigure 11-5.

We have two options here: we can place the order anyway and leave it

unallocated, or we can refuse to take the order because the allocation

can’t be guaranteed. The failure state of our batches service has

bubbled up and is affecting the reliability of our order service.

When two things have to be changed together, we say that they are

coupled. We can think of this failure cascade as a kind of temporal

coupling : every part of the system has to work at the same time for any

part of it to work. As the system gets bigger, there is an exponentially

increasing probability that some part is degraded.



Figure 11-5. Command flow with error



CONNASCENCE



We’re using the term coupling here, but there’s another way to describe the relationships

between our systems. Connascence is a term used by some authors to describe the different

types of coupling.



Connascence isn’t b ad , but some types of connascence are stronger than others. We want to

have strong connascence locally, as when two classes are closely related, but weak

connascence at a distance.



In our first example of a distributed ball of mud, we see Connascence of Execution: multiple

components need to know the correct order of work for an operation to be successful.



When thinking about error conditions here, we’re talking about Connascence of Timing: multiple

things have to happen, one after another, for the operation to work.



When we replace our RPC-style system with events, we replace both of these types of

connascence with a weak er type. That’s Connascence of Name: multiple components need to

agree only on the name of an event and the names of fields it carries.



We can never completely avoid coupling, except by having our software not talk to any other

software. What we want is to avoid inappropriate coupling. Connascence provides a mental

model for understanding the strength and type of coupling inherent in different architectural

styles. Read all about it atconnascence.io.

The Alternative: Temporal Decoupling

Using Asynchronous Messaging

How do we get appropriate coupling? We’ve already seen part of the

answer, which is that we should think in terms of verbs, not nouns. Our

domain model is about modeling a business process. It’s not a static

data model about a thing; it’s a model of a verb.

So instead of thinking about a system for orders and a system for

batches, we think about a system for ordering and a system for

allocating , and so on.

When we separate things this way, it’s a little easier to see which

system should be responsible for what. When thinking about ordering ,

really we want to make sure that when we place an order, the order is

placed. Everything else can happen later , so long as it happens.

NOT E



If this sounds familiar, it should! Segregating responsibilities is the same process

we went through when designing our aggregates and commands.



Like aggregates, microservices should be consistency boundaries.

Between two services, we can accept eventual consistency, and that

means we don’t need to rely on synchronous calls. Each service

accepts commands from the outside world and raises events to record

the result. Other services can listen to those events to trigger the next

steps in the workflow.

To avoid the Distributed Ball of Mud anti-pattern, instead of

temporally coupled HTTPAPI calls, we want to use asynchronous

messaging to integrate our systems. We want our

BatchQuantityChanged messages to come in as external messages

from upstream systems, and we want our system to publish Allocated

events for downstream systems to listen to.

Why is this better? First, because things can fail independently, it’s

easier to handle degraded behavior: we can still take orders if the

allocation system is having a bad day.

Second, we’re reducing the strength of coupling between our systems.

If we need to change the order of operations or to introduce new steps

in the process, we can do that locally.

Using a Redis Pub/Sub Channel for

Integration

Let’s see how it will all work concretely. We’ll need some way of

getting events out of one system and into another, like our message bus,

but for services. This piece of infrastructure is often called a message

broker. The role of a message broker is to take messages from

publishers and deliver them to subscribers.

At MADE.com, we useEvent Store; Kafka or RabbitMQ are valid

alternatives. A lightweight solution based on Redispub/sub channels

can also work just fine, and because Redis is much more generally

familiar to people, we thought we’d use it for this book.

NOT E



We’re glossing over the complexity involved in choosing the right messaging

platform. Concerns like message ordering, failure handling, and idempotency all

need to be thought through. For a few pointers, see“Footguns”.



Our new flow will look likeFigure 11-6: Redis provides the

BatchQuantityChanged event that kicks off the whole process, and

our Allocated event is published back out to Redis again at the end.



Figure 11-6. Sequence diagram for reallocation flow



Test-Driving It All Using an End-to-End

Test

Here’s how we might start with an end-to-end test. We can use our

existingAPI to create batches, and then we’ll test both inbound and

outbound messages:

An end-to-end test for our pub/sub model

(tests/e2e/test\_external\_events.py)



def test\_change\_batch\_quantity\_leading\_to\_reallocation():

\# start with two batches and an order allocated to one of them

orderid,sku=random\_orderid(),random\_sku()

earlier\_batch,later\_batch=random\_batchref('old'),

random\_batchref('newer')

api\_client.post\_to\_add\_batch(earlier\_batch,sku,qty= 10 ,eta='2011-01-02')



api\_client.post\_to\_add\_batch(later\_batch,sku,qty= 10 ,eta='2011-01-02')

response=api\_client.post\_to\_allocate(orderid,sku, 10 )

assert response.json()\['batchref']==earlier\_batch



subscription=redis\_client.subscribe\_to('line\_allocated')



\# change quantity on allocated batch so it's less than our order

redis\_client.publish\_message('change\_batch\_quantity', {

'batchref':earlier\_batch,'qty': 5

})



\# wait until we see a message saying the order has been reallocated

messages=\[]

for attempt in Retrying(stop=stop\_after\_delay( 3 ),reraise=True):

with attempt:

message=subscription.get\_message(timeout= 1 )

if message:



messages.append(message)

print (messages)

data=json.loads(messages\[- 1 ]\['data'])

assert data\['orderid']==orderid

assert data\['batchref']==later\_batch



You can read the story of what’s going on in this test from the

comments: we want to send an event into the system that causes an

order line to be reallocated, and we see that reallocation come out

as an event in Redis too.

api\_client is a little helper that we refactored out to share

between our two test types; it wraps our calls to requests.post.

redis\_client is another little test helper, the details of which

don’t really matter; its job is to be able to send and receive

messages from various Redis channels. We’ll use a channel called

change\_batch\_quantity to send in our request to change the

quantity for a batch, and we’ll listen to another channel called

line\_allocated to look out for the expected reallocation.

Because of the asynchronous nature of the system under test, we

need to use the tenacity library again to add a retry loop—first,

because it may take some time for our new line\_allocated

message to arrive, but also because it won’t be the only message

on that channel.

Redis Is Another Thin Adapter Around Our

Message Bus

Our Redis pub/sub listener (we call it an event consumer ) is very

much like Flask: it translates from the outside world to our events:

Simple Redis message listener

(src/allocation/entrypoints/redis\_eventconsumer.py)



r=redis.Redis(\*\*config.get\_redis\_host\_and\_port())



def main():

orm.start\_mappers()

pubsub=r.pubsub(ignore\_subscribe\_messages=True)

pubsub.subscribe('change\_batch\_quantity')



for m in pubsub.listen():

handle\_change\_batch\_quantity(m)



def handle\_change\_batch\_quantity(m):

logging.debug('handling%s',m)

data=json.loads(m\['data'])

cmd=commands.ChangeBatchQuantity(ref=data\['batchref'],qty=data\['qty'])



messagebus.handle(cmd,uow=unit\_of\_work.SqlAlchemyUnitOfWork())



main() subscribes us to the change\_batch\_quantity channel on

load.

Our main job as an entrypoint to the system is to deserialize JSON,

convert it to a Command, and pass it to the service layer—much as

the Flask adapter does.

We also build a new downstream adapter to do the opposite job—

converting domain events to public events:

Simple Redis message publisher

(src/allocation/adapters/redis\_eventpublisher.py)



r=redis.Redis(\*\*config.get\_redis\_host\_and\_port())



def publish(channel,event:events.Event):

logging.debug('publishing: channel=%s, event=%s',channel,event)

r.publish(channel,json.dumps(asdict(event)))

We take a hardcoded channel here, but you could also store a

mapping between event classes/names and the appropriate channel,

allowing one or more message types to go to different channels.

Our New Outgoing Event

Here’s what the Allocated event will look like:

New event (src/allocation/domain/events.py)



@dataclass

classAllocated (Event):

orderid:str

sku:str

qty:int

batchref:str

It captures everything we need to know about an allocation: the details

of the order line, and which batch it was allocated to.

We add it into our model’s allocate() method (having added a test

first, naturally):

Product.allocate() emits new event to record what happened

(src/allocation/domain/model.py)



classProduct :

...

def allocate(self,line:OrderLine)->str:

...



batch.allocate(line)

self.version\_number+= 1

self.events.append(events.Allocated(

orderid=line.orderid,sku=line.sku,qty=line.qty,



batchref=batch.reference,

))

return batch.reference



The handler for ChangeBatchQuantity already exists, so all we need

to add is a handler that publishes the outgoing event:

The message bus grows

(src/allocation/service\_layer/messagebus.py)

HANDLERS={



events.Allocated: \[handlers.publish\_allocated\_event],

events.OutOfStock: \[handlers.send\_out\_of\_stock\_notification],

} # type: Dict\[Type\[events.Event], List\[Callable]]

Publishing the event uses our helper function from the Redis wrapper:

Publish to Redis (src/allocation/service\_layer/handlers.py)



def publish\_allocated\_event(

event:events.Allocated,uow:unit\_of\_work.AbstractUnitOfWork,

):

redis\_eventpublisher.publish('line\_allocated',event)

Internal Versus External Events

It’s a good idea to keep the distinction between internal and external

events clear. Some events may come from the outside, and some events

may get upgraded and published externally, but not all of them will.

This is particularly important if you get intoevent sourcing(very much

a topic for another book, though).

T IP



Outbound events are one of the places it’s important to apply validation. See

Appendix Efor some validation philosophy and examples.



EXERCISE FOR THE READER



A nice simple one for this chapter: make it so that the main allocate() use case can also be

invoked by an event on a Redis channel, as well as (or instead of) via the API.

You will likely want to add a new E2E test and feed through some changes into

redis\_eventconsumer.py.



Wrap-Up

Events can come from the outside, but they can also be published

externally—our publish handler converts an event to a message on a

Redis channel. We use events to talk to the outside world. This kind of

temporal decoupling buys us a lot of flexibility in our application

integrations, but as always, it comes at a cost.

Event notification is nice because it implies a low level of

coupling, and is pretty simple to set up. It can become

problematic, however, if there really is a logical flow that runs

over various event notifications...It can be hard to see such a flow

as it’s not explicit in any program text....This can make it hard to

debug and modify.

—Martin Fowler,“What do you mean by ‘Event-

Driven’”

Table 11-1shows some trade-offs to think about.

Table 11-1. Event-based microservices integration: the trade-offs



Pros Cons



Avoids the distributed big ball

of mud.



Services are decoupled: it’s

easier to change individual

services and add

new ones.



The overall flows of information

are harder to see.



Eventual consistency is a new

concept to deal with.



Message reliability and choices

around at-least-once versus at-

most-once delivery

need thinking through.



More generally, if you’re moving from a model of synchronous

messaging to an async one, you also open up a whole host of problems

having to do with message reliability and eventual consistency. Read

on to“Footguns”.

Chapter 12. Command-Query

Responsibility Segregation

(CQRS)

In this chapter, we’re going to start with a fairly uncontroversial

insight: reads (queries) and writes (commands) are different, so they

should be treated differently (or have their responsibilities segregated,

if you will). Then we’re going to push that insight as far as we can.

If you’re anything like Harry, this will all seem extreme at first, but

hopefully we can make the argument that it’s not totally unreasonable.

Figure 12-1shows where we might end up.

T IP



The code for this chapter is in the chapter\_12\_cqrs branchon GitHub.



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_12\_cqrs

\# or to code along, checkout the previous chapter:

git checkout chapter\_11\_external\_events



First, though, why bother?



Figure 12-1. Separating reads from writes



Domain Models Are for Writing

We’ve spent a lot of time in this book talking about how to build

software that enforces the rules of our domain. These rules, or

constraints, will be different for every application, and they make up

the interesting core of our systems.

In this book, we’ve set explicit constraints like “You can’t allocate

more stock than is available,” as well as implicit constraints like

“Each order line is allocated to a single batch.”

We wrote down these rules as unit tests at the beginning of the book:

Our basic domain tests (tests/unit/test\_batches.py)



def test\_allocating\_to\_a\_batch\_reduces\_the\_available\_quantity():

batch=Batch("batch-001","SMALL-TABLE",qty= 20 ,eta=date.today())

line=OrderLine('order-ref',"SMALL-TABLE", 2 )



batch.allocate(line)



assert batch.available\_quantity== 18



...



def test\_cannot\_allocate\_if\_available\_smaller\_than\_required():

small\_batch,large\_line=make\_batch\_and\_line("ELEGANT-LAMP", 2 , 20 )

assert small\_batch.can\_allocate(large\_line) is False

To apply these rules properly, we needed to ensure that operations

were consistent, and so we introduced patterns like Unit of Work and

Aggregate that help us commit small chunks of work.

To communicate changes between those small chunks, we introduced

the Domain Events pattern so we can write rules like “When stock is

damaged or lost, adjust the available quantity on the batch, and

reallocate orders if necessary.”

All of this complexity exists so we can enforce rules when we change

the state of our system. We’ve built a flexible set of tools for writing

data.

What about reads, though?

Most Users Aren’t Going to Buy Your

Furniture

At MADE.com, we have a system very like the allocation service. In a

busy day, we might process one hundred orders in an hour, and we

have a big gnarly system for allocating stock to those orders.

In that same busy day, though, we might have one hundred product

views per second. Each time somebody visits a product page, or a

product listing page, we need to figure out whether the product is still

in stock and how long it will take us to deliver it.

The domain is the same—we’re concerned with batches of stock, and

their arrival date, and the amount that’s still available—but the access

pattern is very different. For example, our customers won’t notice if

the query is a few seconds out of date, but if our allocate service is

inconsistent, we’ll make a mess of their orders. We can take advantage

of this difference by making our reads eventually consistent in order

to make them perform better.

IS READ CONSISTENCY TRULY ATTAINABLE?



This idea of trading consistency against performance makes a lot of developers nervous at first,

so let’s talk quickly about that.

Let’s imagine that our “Get Available Stock” query is 30 seconds out of date when Bob visits the

page for ASYMMETRICAL-DRESSER. Meanwhile, though, Harry has already bought the last item. When

we try to allocate Bob’s order, we’ll get a failure, and we’ll need to either cancel his order or buy

more stock and delay his delivery.

People who’ve worked only with relational data stores get really nervous about this problem, but

it’s worth considering two other scenarios to gain some perspective.

First, let’s imagine that Bob and Harry both visit the page at the sam e tim e. Harry goes off to

make coffee, and by the time he returns, Bob has already bought the last dresser. When Harry

places his order, we send it to the allocation service, and because there’s not enough stock, we

have to refund his payment or buy more stock and delay his delivery.

As soon as we render the product page, the data is already stale. This insight is key to

understanding why reads can be safely inconsistent: we’ll always need to check the current state

of our system when we come to allocate, because all distributed systems are inconsistent. As

soon as you have a web server and two customers, you have the potential for stale data.

OK, let’s assume we solve that problem somehow: we magically build a totally consistent web

application where nobody ever sees stale data. This time Harry gets to the page first and buys

his dresser.

Unfortunately for him, when the warehouse staff tries to dispatch his furniture, it falls off the forklift

and smashes into a zillion pieces. Now what?

The only options are to either call Harry and refund his order or buy more stock and delay delivery.

No matter what we do, we’re always going to find that our software systems are inconsistent with

reality, and so we’ll always need business processes to cope with these edge cases. It’s OK to

trade performance for consistency on the read side, because stale data is essentially

unavoidable.



We can think of these requirements as forming two halves of a system:

the read side and the write side, shown inTable 12-1.

For the write side, our fancy domain architectural patterns help us to

evolve our system over time, but the complexity we’ve built so far

doesn’t buy anything for reading data. The service layer, the unit of

work, and the clever domain model are just bloat.

Table 12-1. Read versus write



Read side Write side



Behavior Simple read Complex business logic



Cacheability Highly cacheable Uncacheable



Consistency Can be stale Must be transactionally consistent



Post/Redirect/Get and CQS

If you do web development, you’re probably familiar with the

Post/Redirect/Get pattern. In this technique, a web endpoint accepts an

HTTP POST and responds with a redirect to see the result. For

example, we might accept a POST to /batches to create a new batch

and redirect the user to /batches/123 to see their newly created batch.

This approach fixes the problems that arise when users refresh the

results page in their browser or try to bookmark a results page. In the

case of a refresh, it can lead to our users double-submitting data and

thus buying two sofas when they needed only one. In the case of a

bookmark, our hapless customers will end up with a broken page when

they try to GET a POST endpoint.

Both these problems happen because we’re returning data in response

to a write operation. Post/Redirect/Get sidesteps the issue by

separating the read and write phases of our operation.

This technique is a simple example of command-query separation

(CQS). In CQS we follow one simple rule: functions should either

modify state or answer questions, but never both. This makes software

easier to reason about: we should always be able to ask, “Are the

lights on?” without flicking the light switch.

NOT E



When building APIs, we can apply the same design technique by returning a 201

Created, or a 202 Accepted, with a Location header containing the URI of our

new resources. What’s important here isn’t the status code we use but the logical

separation of work into a write phase and a query phase.



As you’ll see, we can use the CQS principle to make our systems

faster and more scalable, but first, let’s fix the CQS violation in our

existing code. Ages ago, we introduced an allocate endpoint that

takes an order and calls our service layer to allocate some stock. At

the end of the call, we return a 200 OK and the batch ID. That’s led to

some ugly design flaws so that we can get the data we need. Let’s

change it to return a simple OK message and instead provide a new

read-only endpoint to retrieve allocation state:

API test does a GET after the POST (tests/e2e/test\_api.py)



@pytest.mark.usefixtures('postgres\_db')

@pytest.mark.usefixtures('restart\_api')



def test\_happy\_path\_returns\_202\_and\_batch\_is\_allocated():

orderid=random\_orderid()

sku,othersku=random\_sku(),random\_sku('other')

earlybatch=random\_batchref( 1 )

laterbatch=random\_batchref( 2 )

otherbatch=random\_batchref( 3 )

api\_client.post\_to\_add\_batch(laterbatch,sku, 100 ,'2011-01-02')

api\_client.post\_to\_add\_batch(earlybatch,sku, 100 ,'2011-01-01')

api\_client.post\_to\_add\_batch(otherbatch,othersku, 100 ,None)



r=api\_client.post\_to\_allocate(orderid,sku,qty= 3 )

assert r.status\_code== 202



r=api\_client.get\_allocation(orderid)

assert r.ok

assert r.json()==\[

{'sku':sku,'batchref':earlybatch},

]



@pytest.mark.usefixtures('postgres\_db')

@pytest.mark.usefixtures('restart\_api')

def test\_unhappy\_path\_returns\_400\_and\_error\_message():

unknown\_sku,orderid=random\_sku(),random\_orderid()

r=api\_client.post\_to\_allocate(

orderid,unknown\_sku,qty= 20 ,expect\_success=False,

)

assert r.status\_code== 400

assert r.json()\['message']==f'Invalid sku {unknown\_sku}'



r=api\_client.get\_allocation(orderid)

assert r.status\_code== 404



OK, what might the Flask app look like?

Endpoint for viewing allocations

(src/allocation/entrypoints/flask\_app.py)



fromallocationimport views

...



@app.route("/allocations/",methods=\['GET'])

def allocations\_view\_endpoint(orderid):

uow=unit\_of\_work.SqlAlchemyUnitOfWork()

result=views.allocations(orderid,uow)

ifnot result:

return 'not found', 404

return jsonify(result), 200

All right, a views.py , fair enough; we can keep read-only stuff in

there, and it’ll be a real views.py , not like Django’s, something that

knows how to build read-only views of our data...

Hold On to Your Lunch, Folks

Hmm, so we can probably just add a list method to our existing

repository object:

Views do...raw SQL? (src/allocation/views.py)



fromallocation.service\_layerimport unit\_of\_work



def allocations(orderid:str,uow:unit\_of\_work.SqlAlchemyUnitOfWork):

with uow:

results=list(uow.session.execute(

'SELECT ol.sku, b.reference'

' FROM allocations AS a'

' JOIN batches AS b ON a.batch\_id = b.id'

' JOIN order\_lines AS ol ON a.orderline\_id = ol.id'

' WHERE ol.orderid = :orderid',

dict(orderid=orderid)

))

return \[{'sku':sku,'batchref':batchref} for sku,batchref in results]

Excuse me? Raw SQL?

If you’re anything like Harry encountering this pattern for the first time,

you’ll be wondering what on earth Bob has been smoking. We’re hand-

rolling our own SQL now, and converting database rows directly to

dicts? After all the effort we put into building a nice domain model?

And what about the Repository pattern? Isn’t that meant to be our

abstraction around the database? Why don’t we reuse that?

Well, let’s explore that seemingly simpler alternative first, and see

what it looks like in practice.

We’ll still keep our view in a separate views.py module; enforcing a

clear distinction between reads and writes in your application is still a

good idea. We apply command-query separation, and it’s easy to see

which code modifies state (the event handlers) and which code just

retrieves read-only state (the views).

T IP



Splitting out your read-only views from your state-modifying command and event

handlers is probably a good idea, even if you don’t want to go to full-blown

CQRS.



Testing CQRS Views

Before we get into exploring various options, let’s talk about testing.

Whichever approaches you decide to go for, you’re probably going to

need at least one integration test. Something like this:

An integration test for a view (tests/integration/test\_views.py)



def test\_allocations\_view(sqlite\_session\_factory):

uow=unit\_of\_work.SqlAlchemyUnitOfWork(sqlite\_session\_factory)

messagebus.handle(commands.CreateBatch('sku1batch','sku1', 50 ,None),uow)



messagebus.handle(commands.CreateBatch('sku2batch','sku2', 50 ,today),uow)

messagebus.handle(commands.Allocate('order1','sku1', 20 ),uow)

messagebus.handle(commands.Allocate('order1','sku2', 20 ),uow)

\# add a spurious batch and order to make sure we're getting the right ones

messagebus.handle(commands.CreateBatch('sku1batch-later','sku1', 50 ,

today),uow)

messagebus.handle(commands.Allocate('otherorder','sku1', 30 ),uow)

messagebus.handle(commands.Allocate('otherorder','sku2', 10 ),uow)



assert views.allocations('order1',uow)==\[

{'sku':'sku1','batchref':'sku1batch'},

{'sku':'sku2','batchref':'sku2batch'},

]



We do the setup for the integration test by using the public

entrypoint to our application, the message bus. That keeps our tests

decoupled from any implementation/infrastructure details about

how things get stored.

“Obvious” Alternative 1: Using the

Existing Repository

How about adding a helper method to our products repository?

A simple view that uses the repository (src/allocation/views.py)



fromallocationimport unit\_of\_work



def allocations(orderid:str,uow:unit\_of\_work.AbstractUnitOfWork):

with uow:

products=uow.products.for\_order(orderid=orderid)

batches=\[b for p in products for b in p.batches]



return \[

{'sku':b.sku,'batchref':b.reference}

for b in batches

if orderid in b.orderids

]



Our repository returns Product objects, and we need to find all

the products for the SKUs in a given order, so we’ll build a new

helper method called .for\_order() on the repository.

Now we have products but we actually want batch references, so

we get all the possible batches with a list comprehension.

We filter again to get just the batches for our specific order. That,

in turn, relies on our Batch objects being able to tell us which

order IDs it has allocated.

We implement that last using a .orderid property:

An arguably unnecessary property on our model

(src/allocation/domain/model.py)



classBatch :

...



@property

def orderids(self):

return {l.orderid for l in self.\_allocations}



You can start to see that reusing our existing repository and domain

model classes is not as straightforward as you might have assumed.

We’ve had to add new helper methods to both, and we’re doing a

bunch of looping and filtering in Python, which is work that would be

done much more efficiently by the database.

So yes, on the plus side we’re reusing our existing abstractions, but on

the downside, it all feels quite clunky.

Your Domain Model Is Not Optimized for

Read Operations

What we’re seeing here are the effects of having a domain model that

is designed primarily for write operations, while our requirements for

reads are often conceptually quite different.

This is the chin-stroking-architect’s justification for CQRS. As we’ve

said before, a domain model is not a data model—we’re trying to

capture the way the business works: workflow, rules around state

changes, messages exchanged; concerns about how the system reacts to

external events and user input. Most of this stuff is totally irrelevant

for read-only operations.

T IP



This justification for CQRS is related to the justification for the Domain Model

pattern. If you’re building a simple CRUD app, reads and writes are going to be

closely related, so you don’t need a domain model or CQRS. But the more

complex your domain, the more likely you are to need both.



To make a facile point, your domain classes will have multiple

methods for modifying state, and you won’t need any of them for read-

only operations.

As the complexity of your domain model grows, you will find yourself

making more and more choices about how to structure that model,

which make it more and more awkward to use for read operations.

“Obvious” Alternative 2: Using the ORM

You may be thinking, OK, if our repository is clunky, and working with

Products is clunky, then I can at least use my ORM and work with

Batches. That’s what it’s for!

A simple view that uses the ORM (src/allocation/views.py)



fromallocationimport unit\_of\_work,model



def allocations(orderid:str,uow:unit\_of\_work.AbstractUnitOfWork):

with uow:

batches=uow.session.query(model.Batch).join(

model.OrderLine,model.Batch.\_allocations

).filter(

model.OrderLine.orderid==orderid

)

return \[

{'sku':b.sku,'batchref':b.batchref}

for b in batches

]

But is that actually any easier to write or understand than the raw SQL

version from the code example in“Hold On to Your Lunch, Folks”? It

may not look too bad up there, but we can tell you it took several

attempts, and plenty of digging through the SQLAlchemy docs. SQL is

just SQL.

But the ORM can also expose us to performance problems.

SELECT N+1 and Other Performance

Considerations

The so-calledSELECT N+1problem is a common performance

problem with ORMs: when retrieving a list of objects, your ORM will

often perform an initial query to, say, get all the IDs of the objects it

needs, and then issue individual queries for each object to retrieve

their attributes. This is especially likely if there are any foreign-key

relationships on your objects.

NOT E



In all fairness, we should say that SQLAlchemy is quite good at avoiding the

SELECT N+1 problem. It doesn’t display it in the preceding example, and you can

requesteager loadingexplicitly to avoid it when dealing with joined objects.



Beyond SELECT N+1, you may have other reasons for wanting to

decouple the way you persist state changes from the way that you

retrieve current state. A set of fully normalized relational tables is a

good way to make sure that write operations never cause data

corruption. But retrieving data using lots of joins can be slow. It’s

common in such cases to add some denormalized views, build read

replicas, or even add caching layers.

Time to Completely Jump the Shark

On that note: have we convinced you that our raw SQL version isn’t so

weird as it first seemed? Perhaps we were exaggerating for effect?

Just you wait.

So, reasonable or not, that hardcoded SQL query is pretty ugly, right?

What if we made it nicer...

A much nicer query (src/allocation/views.py)



def allocations(orderid:str,uow:unit\_of\_work.SqlAlchemyUnitOfWork):

with uow:

results=list(uow.session.execute(

'SELECT sku, batchref FROM allocations\_view WHERE orderid =

:orderid',

dict(orderid=orderid)

))

...

...by keeping a totally separate, denormalized data store for our

view model?

Hee hee hee, no foreign keys, just strings, YOLO

(src/allocation/adapters/orm.py)



allocations\_view=Table(

'allocations\_view',metadata,

Column('orderid',String( 255 )),

Column('sku',String( 255 )),

Column('batchref',String( 255 )),

)

OK, nicer-looking SQL queries wouldn’t be a justification for anything

really, but building a denormalized copy of your data that’s optimized

for read operations isn’t uncommon, once you’ve reached the limits of

what you can do with indexes.

Even with well-tuned indexes, a relational database uses a lot of CPU

to perform joins. The fastest queries will always be SELECT \* from

mytable WHERE key = : value.

More than raw speed, though, this approach buys us scale. When we’re

writing data to a relational database, we need to make sure that we get

a lock over the rows we’re changing so we don’t run into consistency

problems.

If multiple clients are changing data at the same time, we’ll have weird

race conditions. When we’re reading data, though, there’s no limit to

the number of clients that can concurrently execute. For this reason,

read-only stores can be horizontally scaled out.

T IP



Because read replicas can be inconsistent, there’s no limit to how many we can

have. If you’re struggling to scale a system with a complex data store, ask

whether you could build a simpler read model.



Keeping the read model up to date is the challenge! Database views

(materialized or otherwise) and triggers are a common solution, but

that limits you to your database. We’d like to show you how to reuse

our event-driven architecture instead.

Updating a Read Model Table Using an Event

Handler

We add a second handler to the Allocated event:

Allocated event gets a new handler

(src/allocation/service\_layer/messagebus.py)

EVENT\_HANDLERS={



events.Allocated: \[

handlers.publish\_allocated\_event,

handlers.add\_allocation\_to\_read\_model

],



Here’s what our update-view-model code looks like:

Update on allocation (src/allocation/service\_layer/handlers.py)



def add\_allocation\_to\_read\_model(

event:events.Allocated,uow:unit\_of\_work.SqlAlchemyUnitOfWork,

):

with uow:

uow.session.execute(

'INSERT INTO allocations\_view (orderid, sku, batchref)'

' VALUES (:orderid, :sku, :batchref)',

dict(orderid=event.orderid,sku=event.sku,batchref=event.batchref)

)

uow.commit()

Believe it or not, that will pretty much work! And it will work against

the exact same integration tests as the rest of our options.

OK, you’ll also need to handle Deallocated:

A second listener for read model updates



events.Deallocated: \[

handlers.remove\_allocation\_from\_read\_model,

handlers.reallocate

],



...



def remove\_allocation\_from\_read\_model(

event:events.Deallocated,uow:unit\_of\_work.SqlAlchemyUnitOfWork,

):

with uow:

uow.session.execute(

'DELETE FROM allocations\_view '

' WHERE orderid = :orderid AND sku = :sku',

Figure 12-2shows the flow across the two requests.



Figure 12-2. Sequence diagram for read model



InFigure 12-2, you can see two transactions in the POST/write

operation, one to update the write model and one to update the read

model, which the GET/read operation can use.

REBUILDING FROM SCRATCH



“What happens when it breaks?” should be the first question we ask as engineers.

How do we deal with a view model that hasn’t been updated because of a bug or temporary

outage? Well, this is just another case where events and commands can fail independently.

If we never updated the view model, and the ASYMMETRICAL-DRESSER was forever in stock, that

would be annoying for customers, but the allocate service would still fail, and we’d take action to

fix the problem.

Rebuilding a view model is easy, though. Since we’re using a service layer to update our view

model, we can write a tool that does the following:

Queries the current state of the write side to work out what’s currently allocated

Calls the add\_allocate\_to\_read\_model handler for each allocated item



We can use this technique to create entirely new read models from historical data.



Changing Our Read Model

Implementation Is Easy

Let’s see the flexibility that our event-driven model buys us in action,

by seeing what happens if we ever decide we want to implement a

read model by using a totally separate storage engine, Redis.

Just watch:

Handlers update a Redis read model

(src/allocation/service\_layer/handlers.py)



def add\_allocation\_to\_read\_model(event:events.Allocated,\_):

redis\_eventpublisher.update\_readmodel(event.orderid,event.sku,

event.batchref)



def remove\_allocation\_from\_read\_model(event:events.Deallocated,\_):

redis\_eventpublisher.update\_readmodel(event.orderid,event.sku,None)

The helpers in our Redis module are one-liners:

Redis read model read and update

(src/allocation/adapters/redis\_eventpublisher.py)



def update\_readmodel(orderid,sku,batchref):

r.hset(orderid,sku,batchref)



def get\_readmodel(orderid):

return r.hgetall(orderid)

(Maybe the name redis\_eventpublisher.py is a misnomer now, but you

get the idea.)

And the view itself changes very slightly to adapt to its new backend:

View adapted to Redis (src/allocation/views.py)



def allocations(orderid):

batches=redis\_eventpublisher.get\_readmodel(orderid)

return \[

{'batchref':b.decode(),'sku':s.decode()}

for s,b in batches.items()

]

And the exact same integration tests that we had before still pass,

because they are written at a level of abstraction that’s decoupled from

the implementation: setup puts messages on the message bus, and the

assertions are against our view.

T IP



Event handlers are a great way to manage updates to a read model, if you decide

you need one. They also make it easy to change the implementation of that read

model at a later date.



EXERCISE FOR THE READER



Implement another view, this time to show the allocation for a single order line.

Here the trade-offs between using hardcoded SQL versus going via a repository should be much

more blurry. Try a few versions (maybe including going to Redis), and see which you prefer.



Wrap-Up

Table 12-2proposes some pros and cons for each of our options.

As it happens, the allocation service at MADE.com does use “full-

blown” CQRS, with a read model stored in Redis, and even a second

layer of cache provided by Varnish. But its use cases are quite a bit

different from what we’ve shown here. For the kind of allocation

service we’re building, it seems unlikely that you’d need to use a

separate read model and event handlers for updating it.

But as your domain model becomes richer and more complex, a

simplified read model become ever more compelling.

Table 12-2. Trade-offs of various view model options



Option Pros Cons



Just use

repositories



Simple, consistent approach. Expect performance issues with

complex query patterns.



Use custom

queries with

your ORM



Allows reuse of DB

configuration and model

definitions.



Adds another query language

with its own quirks and syntax.



Use hand-

rolled SQL



Offers fine control over

performance with a standard

query syntax.



Changes to DB schema have to

be made to your hand-rolled

queries and your

ORM definitions. Highly

normalized schemas may still

have performance

limitations.



Create

separate read

stores with

events



Read-only copies are easy to

scale out. Views can be

constructed when data

changes so that queries are as

simple as possible.



Complex technique. Harry will

be forever suspicious of your

tastes and

motives.



Often, your read operations will be acting on the same conceptual

objects as your write model, so using the ORM, adding some read

methods to your repositories, and using domain model classes for your

read operations is just fine.

In our book example, the read operations act on quite different

conceptual entities to our domain model. The allocation service thinks

in terms of Batches for a single SKU, but users care about allocations

for a whole order, with multiple SKUs, so using the ORM ends up

being a little awkward. We’d be quite tempted to go with the raw-SQL

view we showed right at the beginning of the chapter.

On that note, let’s sally forth into our final chapter.

Chapter 13. Dependency

Injection (and Bootstrapping)

Dependency injection (DI) is regarded with suspicion in the Python

world. And we’ve managed just fine without it so far in the example

code for this book!

In this chapter, we’ll explore some of the pain points in our code that

lead us to consider using DI, and we’ll present some options for how

to do it, leaving it to you to pick which you think is most Pythonic.

We’ll also add a new component to our architecture called

bootstrap.py ; it will be in charge of dependency injection, as well as

some other initialization stuff that we often need. We’ll explain why

this sort of thing is called a composition root in OO languages, and

why bootstrap script is just fine for our purposes.

Figure 13-1shows what our app looks like without a bootstrapper: the

entrypoints do a lot of initialization and passing around of our main

dependency, the UoW.

T IP



If you haven’t already, it’s worth readingChapter 3before continuing with this

chapter, particularly the discussion of functional versus object-oriented

dependency management.



Figure 13-1. Without bootstrap: entrypoints do a lot



T IP



The code for this chapter is in the chapter\_13\_dependency\_injection branchon

GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout chapter\_13\_dependency\_injection

\# or to code along, checkout the previous chapter:

git checkout chapter\_12\_cqrs



Figure 13-2shows our bootstrapper taking over those responsibilities.



Figure 13-2. Bootstrap takes care of all that in one place



Implicit Versus Explicit Dependencies

Depending on your particular brain type, you may have a slight feeling

of unease at the back of your mind at this point. Let’s bring it out into

the open. We’ve shown you two ways of managing dependencies and

testing them.

For our database dependency, we’ve built a careful framework of

explicit dependencies and easy options for overriding them in tests.

Our main handler functions declare an explicit dependency on the

UoW:

Our handlers have an explicit dependency on the UoW

(src/allocation/service\_layer/handlers.py)



def allocate(

cmd:commands.Allocate,uow:unit\_of\_work.AbstractUnitOfWork

):

And that makes it easy to swap in a fake UoW in our service-layer

tests:

Service-layer tests against a fake UoW: (tests/unit/test\_services.py)



uow=FakeUnitOfWork()

messagebus.handle(\[...],uow)



The UoW itself declares an explicit dependency on the session factory:

The UoW depends on a session factory

(src/allocation/service\_layer/unit\_of\_work.py)



classSqlAlchemyUnitOfWork (AbstractUnitOfWork):



def \_\_init\_\_(self,session\_factory=DEFAULT\_SESSION\_FACTORY):

self.session\_factory=session\_factory

...



We take advantage of it in our integration tests to be able to sometimes

use SQLite instead of Postgres:

Integration tests against a different DB

(tests/integration/test\_uow.py)



def test\_rolls\_back\_uncommitted\_work\_by\_default(sqlite\_session\_factory):

uow=unit\_of\_work.SqlAlchemyUnitOfWork(sqlite\_session\_factory)

Integration tests swap out the default Postgres session\_factory

for a SQLite one.

Aren’t Explicit Dependencies Totally

Weird and Java-y?

If you’re used to the way things normally happen in Python, you’ll be

thinking all this is a bit weird. The standard way to do things is to

declare our dependency implicitly by simply importing it, and then if

we ever need to change it for tests, we can monkeypatch, as is Right

and True in dynamic languages:

Email sending as a normal import-based dependency

(src/allocation/service\_layer/handlers.py)



fromallocation.adaptersimport email,redis\_eventpublisher

...



def send\_out\_of\_stock\_notification(

event:events.OutOfStock,uow:unit\_of\_work.AbstractUnitOfWork,

):

email.send(

'stock@made.com',

f'Out of stock for {event.sku}',

)

Hardcoded import

Calls specific email sender directly

Why pollute our application code with unnecessary arguments just for

the sake of our tests? mock.patch makes monkeypatching nice and

easy:

mock dot patch, thank you Michael Foord

(tests/unit/test\_handlers.py)



with mock.patch("allocation.adapters.email.send") as mock\_send\_mail:

...



The trouble is that we’ve made it look easy because our toy example

doesn’t send real email (email.send\_mail just does a print), but in

real life, you’d end up having to call mock.patch for every single test

that might cause an out-of-stock notification. If you’ve worked on

codebases with lots of mocks used to prevent unwanted side effects,

you’ll know how annoying that mocky boilerplate gets.

And you’ll know that mocks tightly couple us to the implementation.

By choosing to monkeypatch email.send\_mail, we are tied to doing

import email, and if we ever want to do from email import

send\_mail, a trivial refactor, we’d have to change all our mocks.

So it’s a trade-off. Yes, declaring explicit dependencies is

unnecessary, strictly speaking, and using them would make our

application code marginally more complex. But in return, we’d get

tests that are easier to write and manage.

On top of that, declaring an explicit dependency is an example of the

dependency inversion principle—rather than having an (implicit)

dependency on a specific detail, we have an (explicit) dependency on

an abstraction :

Explicit is better than implicit.

—The Zen of Python

The explicit dependency is more abstract

(src/allocation/service\_layer/handlers.py)



def send\_out\_of\_stock\_notification(

event:events.OutOfStock,send\_mail:Callable,

):

send\_mail(

'stock@made.com',

f'Out of stock for {event.sku}',

)

But if we do change to declaring all these dependencies explicitly,

who will inject them, and how? So far, we’ve really been dealing with

only passing the UoW around: our tests use FakeUnitOfWork, while

Flask and Redis eventconsumer entrypoints use the real UoW, and the

message bus passes them onto our command handlers. If we add real

and fake email classes, who will create them and pass them on?

That’s extra (duplicated) cruft for Flask, Redis, and our tests.

Moreover, putting all the responsibility for passing dependencies to

the right handler onto the message bus feels like a violation of the SRP.

Instead, we’ll reach for a pattern called Composition Root (a

bootstrap script to you and me), and we’ll do a bit of “manual DI”

(dependency injection without a framework). SeeFigure 13-3.

1

2



Figure 13-3. Bootstrapper between entrypoints and message bus



Preparing Handlers: Manual DI with

Closures and Partials

One way to turn a function with dependencies into one that’s ready to

be called later with those dependencies already injected is to use

closures or partial functions to compose the function with its

dependencies:

Examples of DI using closures or partial functions



\# existing allocate function, with abstract uow dependency

def allocate(

cmd:commands.Allocate,uow:unit\_of\_work.AbstractUnitOfWork

):

line=OrderLine(cmd.orderid,cmd.sku,cmd.qty)

with uow:

...



\# bootstrap script prepares actual UoW



def bootstrap(..):

uow=unit\_of\_work.SqlAlchemyUnitOfWork()



\# prepare a version of the allocate fn with UoW dependency captured in a

closure

allocate\_composed= lambda cmd:allocate(cmd,uow)



\# or, equivalently (this gets you a nicer stack trace)

def allocate\_composed(cmd):

return allocate(cmd,uow)



\# alternatively with a partial

importfunctools

allocate\_composed=functools.partial(allocate,uow=uow)



\# later at runtime, we can call the partial function, and it will have



\# the UoW already bound

allocate\_composed(cmd)

The difference between closures (lambdas or named functions) and

functools.partial is that the former uselate binding of

variables, which can be a source of confusion if any of the

dependencies are mutable.

Here’s the same pattern again for the

send\_out\_of\_stock\_notification() handler, which has different

dependencies:

Another closure and partial functions example



def send\_out\_of\_stock\_notification(

event:events.OutOfStock,send\_mail:Callable,

):

send\_mail(

'stock@made.com',

...



\# prepare a version of the send\_out\_of\_stock\_notification with dependencies

sosn\_composed = lambda event:send\_out\_of\_stock\_notification(event,

email.send\_mail)



...

\# later, at runtime:

sosn\_composed(event) # will have email.send\_mail already injected in

An Alternative Using Classes

Closures and partial functions will feel familiar to people who’ve

done a bit of functional programming. Here’s an alternative using

classes, which may appeal to others. It requires rewriting all our

handler functions as classes, though:

DI using classes



\# we replace the old def allocate(cmd, uow) with:



classAllocateHandler :



def \_\_init\_\_(self,uow:unit\_of\_work.AbstractUnitOfWork):

self.uow=uow



def \_\_call\_\_(self,cmd:commands.Allocate):

line=OrderLine(cmd.orderid,cmd.sku,cmd.qty)

with self.uow:

\# rest of handler method as before

...



\# bootstrap script prepares actual UoW

uow=unit\_of\_work.SqlAlchemyUnitOfWork()



\# then prepares a version of the allocate fn with dependencies already injected

allocate=AllocateHandler(uow)



...

\_# later at runtime, we can call the handler instance, and it will have

the UoW already injected\_



allocate(cmd)

The class is designed to produce a callable function, so it has a

call method.

But we use the init to declare the dependencies it requires. This

sort of thing will feel familiar if you’ve ever made class-based

descriptors, or a class-based context manager that takes arguments.

Use whichever you and your team feel more comfortable with.

A Bootstrap Script

We want our bootstrap script to do the following:

1\. Declare default dependencies but allow us to override them

2\. Do the “init” stuff that we need to get our app started

3\. Inject all the dependencies into our handlers

4\. Give us back the core object for our app, the message bus

Here’s a first cut:

A bootstrap function (src/allocation/bootstrap.py)



def bootstrap(

start\_orm:bool =True,

uow:unit\_of\_work.AbstractUnitOfWork=unit\_of\_work.SqlAlchemyUnitOfWork(),



send\_mail:Callable =email.send,

publish:Callable=redis\_eventpublisher.publish,

)->messagebus.MessageBus:



if start\_orm:

orm.start\_mappers()



dependencies={'uow':uow,'send\_mail':send\_mail,'publish':publish}

injected\_event\_handlers={

event\_type: \[

inject\_dependencies(handler,dependencies)

for handler in event\_handlers

]

for event\_type,event\_handlers in handlers.EVENT\_HANDLERS.items()

}

injected\_command\_handlers={

command\_type:inject\_dependencies(handler,dependencies)

for command\_type,handler in handlers.COMMAND\_HANDLERS.items()

}



return messagebus.MessageBus(

uow=uow,

event\_handlers=injected\_event\_handlers,



command\_handlers=injected\_command\_handlers,

)



orm.start\_mappers() is our example of initialization work that

needs to be done once at the beginning of an app. We also see

things like setting up the logging module.

We can use the argument defaults to define what the

normal/production defaults are. It’s nice to have them in a single

place, but sometimes dependencies have some side effects at

construction time, in which case you might prefer to default them to

None instead.

We build up our injected versions of the handler mappings by using

a function called inject\_dependencies(), which we’ll show

next.

We return a configured message bus ready for use.

Here’s how we inject dependencies into a handler function by

inspecting it:

DI by inspecting function signatures (src/allocation/bootstrap.py)



def inject\_dependencies(handler,dependencies):

params=inspect.signature(handler).parameters

deps={

name:dependency

for name,dependency in dependencies.items()

if name in params

}

return lambda message:handler(message,\*\*deps)

We inspect our command/event handler’s arguments.

We match them by name to our dependencies.

We inject them as kwargs to produce a partial.

EVEN-MORE-MANUAL DI WITH LESS MAGIC



If you’re finding the preceding inspect code a little harder to grok, this even simpler version may

appeal to you.



Harry wrote the code for inject\_dependencies() as a first cut of how to do “manual” dependency

injection, and when he saw it, Bob accused him of overengineering and writing his own DI

framework.



It honestly didn’t even occur to Harry that you could do it any more plainly, but you can, like this:



Manually creating partial functions inline (src/allocation/b ootstrap.py)



injected\_event\_handlers={

events.Allocated: \[

lambda e:handlers.publish\_allocated\_event(e,publish),

lambda e:handlers.add\_allocation\_to\_read\_model(e,uow),

],

events.Deallocated: \[

lambda e:handlers.remove\_allocation\_from\_read\_model(e,uow),

lambda e:handlers.reallocate(e,uow),

],

events.OutOfStock: \[

lambda e:handlers.send\_out\_of\_stock\_notification(e,send\_mail)

]

}

injected\_command\_handlers={

commands.Allocate: lambda c:handlers.allocate(c,uow),

commands.CreateBatch:\\

lambda c:handlers.add\_batch(c,uow),

commands.ChangeBatchQuantity:\\

lambda c:handlers.change\_batch\_quantity(c,uow),

}



Harry says he couldn’t even imagine writing out that many lines of code and having to look up that

many function arguments manually. This is a perfectly viable solution, though, since it’s only one

line of code or so per handler you add, and thus not a massive maintenance burden even if you

have dozens of handlers.



Our app is structured in such a way that we always want to do dependency injection in only one

place, the handler functions, so this super-manual solution and Harry’s inspect()-based one

will both work fine.



If you find yourself wanting to do DI in more things and at different times, or if you ever get into

dependency chains (in which your dependencies have their own dependencies, and so on), you

may get some mileage out of a “real” DI framework.



At MADE, we’ve usedInjectin a few places, and it’s fine, although it makes Pylint unhappy. You

might also check outPunq, as written by Bob himself, or the DRY-Python crew’sdependencies.

Message Bus Is Given Handlers at

Runtime

Our message bus will no longer be static; it needs to have the already-

injected handlers given to it. So we turn it from being a module into a

configurable class:

MessageBus as a class (src/allocation/service\_layer/messagebus.py)



classMessageBus :



def \_\_init\_\_(

self,

uow:unit\_of\_work.AbstractUnitOfWork,

event\_handlers:Dict\[Type\[events.Event],List\[Callable]],

command\_handlers:Dict\[Type\[commands.Command],Callable],

):

self.uow=uow

self.event\_handlers=event\_handlers

self.command\_handlers=command\_handlers



def handle(self,message:Message):

self.queue=\[message]

while self.queue:

message=self.queue.pop( 0 )

if isinstance(message,events.Event):

self.handle\_event(message)

elif isinstance(message,commands.Command):

self.handle\_command(message)

else :

raiseException (f'{message} was not an Event or Command')



The message bus becomes a class...

...which is given its already-dependency-injected handlers.

The main handle() function is substantially the same, with just a

few attributes and methods moved onto self.

Using self.queue like this is not thread-safe, which might be a

problem if you’re using threads, because the bus instance is global

in the Flask app context as we’ve written it. Just something to

watch out for.

What else changes in the bus?

Event and command handler logic stays the same

(src/allocation/service\_layer/messagebus.py)



def handle\_event(self,event:events.Event):

for handler in self.event\_handlers\[type(event)]:

try :

logger.debug('handling event%swith handler%s',event,

handler)

handler(event)

self.queue.extend(self.uow.collect\_new\_events())

exceptException :

logger.exception('Exception handling event%s',event)

continue



def handle\_command(self,command:commands.Command):

logger.debug('handling command%s',command)

try :

handler=self.command\_handlers\[type(command)]

handler(command)

self.queue.extend(self.uow.collect\_new\_events())

exceptException :

logger.exception('Exception handling command%s',command)

raise



handle\_event and handle\_command are substantially the same,

but instead of indexing into a static EVENT\_HANDLERS or

COMMAND\_HANDLERS dict, they use the versions on self.

Instead of passing a UoW into the handler, we expect the handlers

to already have all their dependencies, so all they need is a single

argument, the specific event or command.

Using Bootstrap in Our Entrypoints

In our application’s entrypoints, we now just call

bootstrap.bootstrap() and get a message bus that’s ready to go,

rather than configuring a UoW and the rest of it:

Flask calls bootstrap (src/allocation/entrypoints/flask\_app.py)



\-from allocation import views

+from allocation import bootstrap, views



app = Flask(name)

\-orm.start\_mappers()

+bus = bootstrap.bootstrap()



@app.route("/add\_batch", methods=\['POST'])

@@ -19,8 +16,7 @@ def add\_batch():

cmd = commands.CreateBatch(

request.json\['ref'], request.json\['sku'], request.json\['qty'], eta,

)



&#x20;   uow = unit\_of\_work.SqlAlchemyUnitOfWork()

&#x20;   messagebus.handle(cmd, uow)



&#x20;   bus.handle(cmd)

&#x20;   return 'OK', 201



We no longer need to call start\_orm(); the bootstrap script’s

initialization stages will do that.

We no longer need to explicitly build a particular type of UoW; the

bootstrap script defaults take care of it.

And our message bus is now a specific instance rather than the

global module.

Initializing DI in Our Tests

In tests, we can use bootstrap.bootstrap() with overridden

defaults to get a custom message bus. Here’s an example in an

integration test:

Overriding bootstrap defaults (tests/integration/test\_views.py)



@pytest.fixture

def sqlite\_bus(sqlite\_session\_factory):

bus=bootstrap.bootstrap(

start\_orm=True,

uow=unit\_of\_work.SqlAlchemyUnitOfWork(sqlite\_session\_factory),

send\_mail= lambda \*args:None,

publish= lambda \*args:None,

)

yield bus

clear\_mappers()



def test\_allocations\_view(sqlite\_bus):

sqlite\_bus.handle(commands.CreateBatch('sku1batch','sku1', 50 ,None))

sqlite\_bus.handle(commands.CreateBatch('sku2batch','sku2', 50 ,

date.today()))

...

assert views.allocations('order1',sqlite\_bus.uow)==\[

{'sku':'sku1','batchref':'sku1batch'},

{'sku':'sku2','batchref':'sku2batch'},

]

We do still want to start the ORM...

...because we’re going to use a real UoW, albeit with an in-

memory database.

3

But we don’t need to send email or publish, so we make those

noops.

In our unit tests, in contrast, we can reuse our FakeUnitOfWork:

Bootstrap in unit test (tests/unit/test\_handlers.py)



def bootstrap\_test\_app():

return bootstrap.bootstrap(

start\_orm=False,

uow=FakeUnitOfWork(),

send\_mail= lambda \*args:None,

publish= lambda \*args:None,

)

No need to start the ORM...

...because the fake UoW doesn’t use one.

We want to fake out our email and Redis adapters too.

So that gets rid of a little duplication, and we’ve moved a bunch of

setup and sensible defaults into a single place.

EXERCISE FOR THE READER 1



Change all the handlers to being classes as per theDI using classesexample, and amend the

bootstrapper’s DI code as appropriate. This will let you know whether you prefer the functional

approach or the class-based approach when it comes to your own projects.



Building an Adapter “Properly”: A

Worked Example

To really get a feel for how it all works, let’s work through an example

of how you might “properly” build an adapter and do dependency

injection for it.

At the moment, we have two types of dependencies:

Two types of dependencies

(src/allocation/service\_layer/messagebus.py)



uow:unit\_of\_work.AbstractUnitOfWork,

send\_mail:Callable,

publish:Callable,



The UoW has an abstract base class. This is the heavyweight

option for declaring and managing your external dependency. We’d

use this for the case when the dependency is relatively complex.

Our email sender and pub/sub publisher are defined as functions.

This works just fine for simple dependencies.

Here are some of the things we find ourselves injecting at work:

An S3 filesystem client

A key/value store client

A requests session object

Most of these will have more-complex APIs that you can’t capture as a

single function: read and write, GET and POST, and so on.

Even though it’s simple, let’s use send\_mail as an example to talk

through how you might define a more complex dependency.

Define the Abstract and Concrete

Implementations

We’ll imagine a more generic notifications API. Could be email, could

be SMS, could be Slack posts one day.

An ABC and a concrete implementation

(src/allocation/adapters/notifications.py)



classAbstractNotifications (abc.ABC):



@abc.abstractmethod

def send(self,destination,message):

raiseNotImplementedError



...



classEmailNotifications (AbstractNotifications):



def \_\_init\_\_(self,smtp\_host=DEFAULT\_HOST,port=DEFAULT\_PORT):

self.server=smtplib.SMTP(smtp\_host,port=port)

self.server.noop()



def send(self,destination,message):

msg=f'Subject: allocation service notification \\n {message}'

self.server.sendmail(

from\_addr='allocations@example.com',

to\_addrs=\[destination],

msg=msg

)



We change the dependency in the bootstrap script:

Notifications in message bus (src/allocation/bootstrap.py)



def bootstrap(

start\_orm: bool = True,

uow: unit\_of\_work.AbstractUnitOfWork = unit\_of\_work.SqlAlchemyUnitOfWork(),



&#x20;   send\_mail: Callable = email.send,



&#x20;   notifications: AbstractNotifications = EmailNotifications(),

&#x20;   publish: Callable = redis\_eventpublisher.publish,

&#x20;   ) -> messagebus.MessageBus:



Make a Fake Version for Your Tests

We work through and define a fake version for unit testing:

Fake notifications (tests/unit/test\_handlers.py)



classFakeNotifications (notifications.AbstractNotifications):



def \_\_init\_\_(self):

self.sent=defaultdict(list) # type: Dict\[str, List\[str]]



def send(self,destination,message):

self.sent\[destination].append(message)

...

And we use it in our tests:

Tests change slightly (tests/unit/test\_handlers.py)



def test\_sends\_email\_on\_out\_of\_stock\_error(self):

fake\_notifs=FakeNotifications()

bus=bootstrap.bootstrap(

start\_orm=False,

uow=FakeUnitOfWork(),

notifications=fake\_notifs,

publish= lambda \*args:None,

)

bus.handle(commands.CreateBatch("b1","POPULAR-CURTAINS", 9 ,None))

bus.handle(commands.Allocate("o1","POPULAR-CURTAINS", 10 ))

assert fake\_notifs.sent\['stock@made.com']==\[

f"Out of stock for POPULAR-CURTAINS",

]



Figure Out How to Integration Test the Real Thing

Now we test the real thing, usually with an end-to-end or integration

test. We’ve usedMailHogas a real-ish email server for our Docker

dev environment:

Docker-compose config with real fake email server (docker-

compose.yml)



version :"3"



services :



redis\_pubsub :

build :

context :.

dockerfile :Dockerfile

image :allocation-image

...



api :

image :allocation-image

...



postgres :

image :postgres:9.6

...



redis :

image :redis:alpine

...



mailhog :

image :mailhog/mailhog

ports :



&#x20;   "11025:1025"

&#x20;   "18025:8025"



In our integration tests, we use the real EmailNotifications class,

talking to the MailHog server in the Docker cluster:

Integration test for email (tests/integration/test\_email.py)



@pytest.fixture

def bus(sqlite\_session\_factory):

bus=bootstrap.bootstrap(

start\_orm=True,

uow=unit\_of\_work.SqlAlchemyUnitOfWork(sqlite\_session\_factory),

notifications=notifications.EmailNotifications(),

publish= lambda \*args:None,

)

yield bus

clear\_mappers()



def get\_email\_from\_mailhog(sku):

host,port=map(config.get\_email\_host\_and\_port().get, \['host',

'http\_port'])

all\_emails=requests.get(f'http://{host}:{port}/api/v2/messages').json()

return next(m for m in all\_emails\['items'] if sku in str(m))



def test\_out\_of\_stock\_email(bus):

sku=random\_sku()

bus.handle(commands.CreateBatch('batch1',sku, 9 ,None))

bus.handle(commands.Allocate('order1',sku, 10 ))

email=get\_email\_from\_mailhog(sku)

assert email\['Raw']\['From']=='allocations@example.com'

assert email\['Raw']\['To']==\['stock@made.com']

assert f'Out of stock for {sku}' in email\['Raw']\['Data']

We use our bootstrapper to build a message bus that talks to the

real notifications class.

We figure out how to fetch emails from our “real” email server.

We use the bus to do our test setup.

Against all the odds, this actually worked, pretty much at the first

go!

And that’s it really.

EXERCISE FOR THE READER 2



You could do two things for practice regarding adapters:

1.Try swapping out our notifications from email to SMS notifications using Twilio, for

example, or Slack notifications. Can you find a good equivalent to MailHog for

integration testing?

2.In a similar way to what we did moving from send\_mail to a Notifications class, try

refactoring our redis\_eventpublisher that is currently just a Callable to some sort of

more formal adapter/base class/protocol.



Wrap-Up

Once you have more than one adapter, you’ll start to feel a lot of pain

from passing dependencies around manually, unless you do some kind

of dependency injection.

Setting up dependency injection is just one of many typical

setup/initialization activities that you need to do just once when

starting your app. Putting this all together into a bootstrap script is

often a good idea.

The bootstrap script is also good as a place to provide sensible default

configuration for your adapters, and as a single place to override those

adapters with fakes for your tests.

A dependency injection framework can be useful if you find yourself

needing to do DI at multiple levels—if you have chained dependencies

of components that all need DI, for example.

This chapter also presented a worked example of changing an

implicit/simple dependency into a “proper” adapter, factoring out an

ABC, defining its real and fake implementations, and thinking through

integration testing.

DI AND BOOTSTRAP RECAP



In summary:

1.Define your API using an ABC.

2.Implement the real thing.

3.Build a fake and use it for unit/service-layer/handler tests.

4.Find a less fake version you can put into your Docker environment.

5.Test the less fake “real” thing.

6.Profit!



These were the last patterns we wanted to cover, which brings us to

the end ofPart II. Inthe epilogue, we’ll try to give you some pointers

for applying these techniques in the Real World.



1 Because Python is not a “pure” OO language, Python developers aren’t necessarily used

to the concept of needing to compose a set of objects into a working application. We just

pick our entrypoint and run code from top to bottom.



2 Mark Seemann calls this Pure DI or sometimes Vanilla DI.



3 However, it’s still a global in the flask\_app module scope, if that makes sense. This may

cause problems if you ever find yourself wanting to test your Flask app in-process by



TM



using the Flask Test Client instead of using Docker as we do. It’s worth researching

Flask app factoriesif you get into this.

Epilogue

What Now?

Phew! We’ve covered a lot of ground in this book, and for most of our

audience all of these ideas are new. With that in mind, we can’t hope

to make you experts in these techniques. All we can really do is show

you the broad-brush ideas, and just enough code for you to go ahead

and write something from scratch.

The code we’ve shown in this book isn’t battle-hardened production

code: it’s a set of Lego blocks that you can play with to make your first

house, spaceship, and skyscraper.

That leaves us with two big tasks. We want to talk about how to start

applying these ideas for real in an existing system, and we need to

warn you about some of the things we had to skip. We’ve given you a

whole new arsenal of ways to shoot yourself in the foot, so we should

discuss some basic firearms safety.

How Do I Get There from Here?

Chances are that a lot of you are thinking something like this:

“OK Bob and Harry, that’s all well and good, and if I ever get hired to

work on a green-field new service, I know what to do. But in the

meantime, I’m here with my big ball of Django mud, and I don’t see

any way to get to your nice, clean, perfect, untainted, simplistic model.

Not from here.”

We hear you. Once you’ve already built a big ball of mud, it’s hard to

know how to start improving things. Really, we need to tackle things

step by step.

First things first: what problem are you trying to solve? Is the software

too hard to change? Is the performance unacceptable? Have you got

weird, inexplicable bugs?

Having a clear goal in mind will help you to prioritize the work that

needs to be done and, importantly, communicate the reasons for doing

it to the rest of the team. Businesses tend to have pragmatic approaches

to technical debt and refactoring, so long as engineers can make a

reasoned argument for fixing things.

T IP



Making complex changes to a system is often an easier sell if you link it to feature

work. Perhaps you’re launching a new product or opening your service to new

markets? This is the right time to spend engineering resources on fixing the

foundations. With a six-month project to deliver, it’s easier to make the argument

for three weeks of cleanup work. Bob refers to this as architecture tax.



Separating Entangled Responsibilities

At the beginning of the book, we said that the main characteristic of a

big ball of mud is homogeneity: every part of the system looks the

same, because we haven’t been clear about the responsibilities of each

component. To fix that, we’ll need to start separating out

responsibilities and introducing clear boundaries. One of the first

things we can do is to start building a service layer (Figure E-1).



Figure E-1. Domain of a collaboration system



This was the system in which Bob first learned how to break apart a

ball of mud, and it was a doozy. There was logic everywhere —in the

web pages, in manager objects, in helpers, in fat service classes that

we’d written to abstract the managers and helpers, and in hairy

command objects that we’d written to break apart the services.

If you’re working in a system that’s reached this point, the situation can

feel hopeless, but it’s never too late to start weeding an overgrown

garden. Eventually, we hired an architect who knew what he was

doing, and he helped us get things back under control.

Start by working out the use cases of your system. If you have a user

interface, what actions does it perform? If you have a backend

processing component, maybe each cron job or Celery job is a single

use case. Each of your use cases needs to have an imperative name:

Apply Billing Charges, Clean Abandoned Accounts, or Raise Purchase

Order, for example.

In our case, most of our use cases were part of the manager classes and

had names like Create Workspace or Delete Document Version. Each

use case was invoked from a web frontend.

We aim to create a single function or class for each of these supported

operations that deals with orchestrating the work to be done. Each use

case should do the following:

Start its own database transaction if needed

Fetch any required data

Check any preconditions (see the Ensure pattern in

Appendix E)

Update the domain model

Persist any changes

Each use case should succeed or fail as an atomic unit. You might need

to call one use case from another. That’s OK; just make a note of it,

and try to avoid long-running database transactions.

NOT E



One of the biggest problems we had was that manager methods called other

manager methods, and data access could happen from the model objects

themselves. It was hard to understand what each operation did without going on a

treasure hunt across the codebase. Pulling all the logic into a single method, and

using a UoW to control our transactions, made the system easier to reason about.

CASE STUDY: LAYERING AN OVERGROWN SYSTEM



Many years ago, Bob worked for a software company that had outsourced the first version of its

application, an online collaboration platform for sharing and working on files.



When the company brought development in-house, it passed through several generations of

developers’ hands, and each wave of new developers added more complexity to the code’s

structure.



At its heart, the system was an ASP.NET Web Forms application, built with an NHibernate ORM.

Users would upload documents into workspaces, where they could invite other workspace

members to review, comment on, or modify their work.



Most of the complexity of the application was in the permissions model because each document

was contained in a folder, and folders allowed read, write, and edit permissions, much like a

Linux filesystem.



Additionally, each workspace belonged to an account, and the account had quotas attached to it

via a billing package.



As a result, every read or write operation against a document had to load an enormous number

of objects from the database in order to test permissions and quotas. Creating a new workspace

involved hundreds of database queries as we set up the permissions structure, invited users,

and set up sample content.



Some of the code for operations was in web handlers that ran when a user clicked a button or

submitted a form; some of it was in manager objects that held code for orchestrating work; and

some of it was in the domain model. Model objects would make database calls or copy files on

disk, and the test coverage was abysmal.



To fix the problem, we first introduced a service layer so that all of the code for creating a

document or workspace was in one place and could be understood. This involved pulling data

access code out of the domain model and into command handlers. Likewise, we pulled

orchestration code out of the managers and the web handlers and pushed it into handlers.



The resulting command handlers were long and messy, but we’d made a start at introducing

order to the chaos.

T IP



It’s fine if you have duplication in the use-case functions. We’re not trying to write

perfect code; we’re just trying to extract some meaningful layers. It’s better to

duplicate some code in a few places than to have use-case functions calling one

another in a long chain.



This is a good opportunity to pull any data-access or orchestration

code out of the domain model and into the use cases. We should also

try to pull I/O concerns (e.g., sending email, writing files) out of the

domain model and up into the use-case functions. We apply the

techniques fromChapter 3on abstractions to keep our handlers unit

testable even when they’re performing I/O.

These use-case functions will mostly be about logging, data access,

and error handling. Once you’ve done this step, you’ll have a grasp of

what your program actually does , and a way to make sure each

operation has a clearly defined start and finish. We’ll have taken a step

toward building a pure domain model.

Read Working Effectively with Legacy Code by Michael C. Feathers

(Prentice Hall) for guidance on getting legacy code under test and

starting separating responsibilities.

Identifying Aggregates and Bounded

Contexts

Part of the problem with the codebase in our case study was that the

object graph was highly connected. Each account had many

workspaces, and each workspace had many members, all of whom had

their own accounts. Each workspace contained many documents,

which had many versions.

You can’t express the full horror of the thing in a class diagram. For

one thing, there wasn’t really a single account related to a user.

Instead, there was a bizarre rule requiring you to enumerate all of the

accounts associated to the user via the workspaces and take the one

with the earliest creation date.

Every object in the system was part of an inheritance hierarchy that

included SecureObject and Version. This inheritance hierarchy was

mirrored directly in the database schema, so that every query had to

join across 10 different tables and look at a discriminator column just

to tell what kind of objects you were working with.

The codebase made it easy to “dot” your way through these objects

like so:



user.account.workspaces\[ 0 ].documents.versions\[ 1 ].owner.account.settings\[ 0 ];



Building a system this way with Django ORM or SQLAlchemy is easy

but is to be avoided. Although it’s convenient , it makes it very hard to

reason about performance because each property might trigger a

lookup to the database.

T IP



Aggregates are a consistency boundary. In general, each use case should

update a single aggregate at a time. One handler fetches one aggregate from a

repository, modifies its state, and raises any events that happen as a result. If you

need data from another part of the system, it’s totally fine to use a read model, but

avoid updating multiple aggregates in a single transaction. When we choose to

separate code into different aggregates, we’re explicitly choosing to make them

eventually consistent with one another.



A bunch of operations required us to loop over objects this way—for

example:



\# Lock a user's workspaces for nonpayment



def lock\_account(user):

for workspace in user.account.workspaces:

workspace.archive()



Or even recurse over collections of folders and documents:



def lock\_documents\_in\_folder(folder):



for doc in folder.documents:

doc.archive()



for child in folder.children:

lock\_documents\_in\_folder(child)



These operations killed performance, but fixing them meant giving up

our single object graph. Instead, we began to identify aggregates and to

break the direct links between objects.

NOT E



We talked about the infamous SELECT N+1 problem inChapter 12, and how we

might choose to use different techniques when reading data for queries versus

reading data for commands.



Mostly we did this by replacing direct references with identifiers.

Before aggregates:

After modeling with aggregates:

T IP



Bidirectional links are often a sign that your aggregates aren’t right. In our original

code, a Document knew about its containing Folder, and the Folder had a

collection of Documents. This makes it easy to traverse the object graph but stops

us from thinking properly about the consistency boundaries we need. We break

apart aggregates by using references instead. In the new model, a Document had

reference to its parent\_folder but had no way to directly access the Folder.



If we needed to read data, we avoided writing complex loops and

transforms and tried to replace them with straight SQL. For example,

one of our screens was a tree view of folders and documents.

This screen was incredibly heavy on the database, because it relied on

nested for loops that triggered a lazy-loaded ORM.

T IP



We use this same technique inChapter 11, where we replace a nested loop over

ORM objects with a simple SQL query. It’s the first step in a CQRS approach.



After a lot of head-scratching, we replaced the ORM code with a big,

ugly stored procedure. The code looked horrible, but it was much

faster and helped to break the links between Folder and Document.

When we needed to write data, we changed a single aggregate at a

time, and we introduced a message bus to handle events. For example,

in the new model, when we locked an account, we could first query for

all the affected workspaces via SELECT id FROM workspace

WHERE account\_id = ?.

We could then raise a new command for each workspace:



for workspace\_id in workspaces:

bus.handle(LockWorkspace(workspace\_id))



An Event-Driven Approach to Go to

Microservices via Strangler Pattern

The Strangler Fig pattern involves creating a new system around the

edges of an old system, while keeping it running. Bits of old

functionality are gradually intercepted and replaced, until the old

system is left doing nothing at all and can be switched off.

When building the availability service, we used a technique called

event interception to move functionality from one place to another.

This is a three-step process:

1\. Raise events to represent the changes happening in a system

you want to replace.

2\. Build a second system that consumes those events and uses

them to build its own domain model.

3\. Replace the older system with the new.

We used event interception to move fromFigure E-2...



Figure E-2. Before: strong, bidirectional coupling based on XML-RPC



toFigure E-3.



Figure E-3. After: loose coupling with asynchronous events (you can find a high-

resolution version of this diagram at cosmicpython.com)



Practically, this was a several month-long project. Our first step was

to write a domain model that could represent batches, shipments, and

products. We used TDD to build a toy system that could answer a

single question: “If I want N units of HAZARDOUS\_RUG, how long

will they take to be delivered?”

T IP



When deploying an event-driven system, start with a “walking skeleton.”

Deploying a system that just logs its input forces us to tackle all the infrastructural

questions and start working in production.



CASE STUDY: CARVING OUT A MICROSERVICE TO REPLACE A

DOMAIN



MADE.com started out with two monoliths: one for the frontend ecommerce application, and one

for the backend fulfillment system.

The two systems communicated through XML-RPC. Periodically, the backend system would

wake up and query the frontend system to find out about new orders. When it had imported all the

new orders, it would send RPC commands to update the stock levels.

Over time this synchronization process became slower and slower until, one Christmas, it took

longer than 24 hours to import a single day’s orders. Bob was hired to break the system into a

set of event-driven services.

First, we identified that the slowest part of the process was calculating and synchronizing the

available stock. What we needed was a system that could listen to external events and keep a

running total of how much stock was available.

We exposed that information via an API, so that the user’s browser could ask how much stock

was available for each product and how long it would take to deliver to their address.

Whenever a product ran out of stock completely, we would raise a new event that the ecommerce

platform could use to take a product off sale. Because we didn’t know how much load we would

need to handle, we wrote the system with a CQRS pattern. Whenever the amount of stock

changed, we would update a Redis database with a cached view model. Our Flask API queried

these view m odels instead of running the complex domain model.

As a result, we could answer the question “How much stock is available?” in 2 to 3 milliseconds,

and now the API frequently handles hundreds of requests a second for sustained periods.

If this all sounds a little familiar, well, now you know where our example app came from!



Once we had a working domain model, we switched to building out

some infrastructural pieces. Our first production deployment was a

tiny system that could receive a batch\_created event and log its

JSON representation. This is the “Hello World” of event-driven

architecture. It forced us to deploy a message bus, hook up a producer

and consumer, build a deployment pipeline, and write a simple

message handler.

Given a deployment pipeline, the infrastructure we needed, and a basic

domain model, we were off. A couple months later, we were in

production and serving real customers.

Convincing Your Stakeholders to Try

Something New

If you’re thinking about carving a new system out of a big ball of mud,

you’re probably suffering problems with reliability, performance,

maintainability, or all three simultaneously. Deep, intractable problems

call for drastic measures!

We recommend domain modeling as a first step. In many overgrown

systems, the engineers, product owners, and customers no longer speak

the same language. Business stakeholders speak about the system in

abstract, process-focused terms, while developers are forced to speak

about the system as it physically exists in its wild and chaotic state.

CASE STUDY: THE USER MODEL



We mentioned earlier that the account and user model in our first system were bound together by

a “bizarre rule.” This is a perfect example of how engineering and business stakeholders can

drift apart.

In this system, accounts parented work spaces , and users were m em b ers of workspaces.

Workspaces were the fundamental unit for applying permissions and quotas. If a user joined a

workspace and didn’t already have an account , we would associate them with the account that

owned that workspace.

This was messy and ad hoc, but it worked fine until the day a product owner asked for a new

feature:

When a user joins a com pany, we want to add them to som e default work spaces for the

com pany, lik e the HR work space or the Com pany Announcem ents work space.

We had to explain to them that there was no such thing as a company, and there was no sense in

which a user joined an account. Moreover, a “company” might have m any accounts owned by

different users, and a new user might be invited to any one of them.

Years of adding hacks and work-arounds to a broken model caught up with us, and we had to

rewrite the entire user management function as a brand-new system.



Figuring out how to model your domain is a complex task that’s the

subject of many decent books in its own right. We like to use

interactive techniques like event storming and CRC modeling, because

humans are good at collaborating through play. Event modeling is

another technique that brings engineers and product owners together to

understand a system in terms of commands, queries, and events.

T IP



Check out http://www.eventmodeling.org and http://www.eventstorming.org for some great

guides to visual modeling of systems with events.



The goal is to be able to talk about the system by using the same

ubiquitous language, so that you can agree on where the complexity

lies.

We’ve found a lot of value in treating domain problems as TDD kata.

For example, the first code we wrote for the availability service was

the batch and order line model. You can treat this as a lunchtime

workshop, or as a spike at the beginning of a project. Once you can

demonstrate the value of modeling, it’s easier to make the argument for

structuring the project to optimize for modeling.

CASE STUDY: DAVID SEDDON ON TAKING SMALL STEPS



Hi, I ’m David, one of the tech reviewers on this b ook. I ’ve work ed on several com plex Django

m onoliths, and so I’ve k nown the pain that Bob and Harry have m ade all sorts of grand prom ises

ab out soothing.



When I was first exposed to the patterns describ ed here, I was rather excited. I had successfully

used som e of the techniques already on sm aller projects, b ut here was a b lueprint for m uch

larger, datab ase-b ack ed system s lik e the one I work on in m y day job. So I started trying to figure

out how I could im plem ent that b lueprint at m y current organiz ation.



I chose to tack le a prob lem area of the codeb ase that had always b othered m e. I b egan b y

im plem enting it as a use case. But I found m yself running into unexpected questions. There were

things that I hadn’t considered while reading that now m ade it difficult to see what to do. Was it a

prob lem if m y use case interacted with two different aggregates? Could one use case call

another? And how was it going to exist within a system that followed different architectural

principles without resulting in a horrib le m ess?



What happened to that oh-so-prom ising b lueprint? Did I actually understand the ideas well

enough to put them into practice? Was it even suitab le for m y application? Even if it was, would

any of m y colleagues agree to such a m ajor change? Were these just nice ideas for m e to

fantasiz e ab out while I got on with real life?



It took m e a while to realiz e that I could start sm all. I didn’t need to b e a purist or to get it right the

first tim e: I could experim ent, finding what work ed for m e.



And so that’s what I ’ve done. I’ve b een ab le to apply some of the ideas in a few places. I’ve b uilt

new features whose b usiness logic can b e tested without the datab ase or m ock s. And as a team ,

we’ve introduced a service layer to help define the job s the system does.



If you start trying to apply these patterns in your work , you m ay go through sim ilar feelings to

b egin with. When the nice theory of a b ook m eets the reality of your codeb ase, it can b e

dem oraliz ing.



My advice is to focus on a specific prob lem and ask yourself how you can put the relevant ideas

to use, perhaps in an initially lim ited and im perfect fashion. You m ay discover, as I did, that the

first prob lem you pick m ight b e a b it too difficult; if so, m ove on to som ething else. Don’t try to b oil

the ocean, and don’t b e too afraid of m ak ing m istak es. I t will b e a learning experience, and you

can b e confident that you’re m oving roughly in a direction that others have found useful.



So, if you’re feeling the pain too, give these ideas a try. Don’t feel you need perm ission to

rearchitect everything. Just look for som ewhere sm all to start. And ab ove all, do it to solve a

specific prob lem. If you’re successful in solving it, you’ll k now you got som ething right—and

others will too.

Questions Our Tech Reviewers Asked

That We Couldn’t Work into Prose

Here are some questions we heard during drafting that we couldn’t

find a good place to address elsewhere in the book:

Do I need to do all of this at once? Can I just do a bit at a time?

No, you can absolutely adopt these techniques bit by bit. If you

have an existing system, we recommend building a service layer to

try to keep orchestration in one place. Once you have that, it’s

much easier to push logic into the model and push edge concerns

like validation or error handling to the entrypoints.

It’s worth having a service layer even if you still have a big, messy

Django ORM because it’s a way to start understanding the

boundaries of operations.

Extracting use cases will break a lot of my existing code; it’s too

tangled

Just copy and paste. It’s OK to cause more duplication in the short

term. Think of this as a multistep process. Your code is in a bad

state now, so copy and paste it to a new place and then make that

new code clean and tidy.

Once you’ve done that, you can replace uses of the old code with

calls to your new code and finally delete the mess. Fixing large

codebases is a messy and painful process. Don’t expect things to

get instantly better, and don’t worry if some bits of your

application stay messy.

Do I need to do CQRS? That sounds weird. Can’t I just use

repositories?

Of course you can! The techniques we’re presenting in this book

are intended to make your life easier. They’re not some kind of

ascetic discipline with which to punish yourself.

In our first case-study system, we had a lot of View Builder objects

that used repositories to fetch data and then performed some

transformations to return dumb read models. The advantage is that

when you hit a performance problem, it’s easy to rewrite a view

builder to use custom queries or raw SQL.

How should use cases interact across a larger system? Is it a

problem for one to call another?

This might be an interim step. Again, in the first case study, we had

handlers that would need to invoke other handlers. This gets really

messy, though, and it’s much better to move to using a message bus

to separate these concerns.

Generally, your system will have a single message bus

implementation and a bunch of subdomains that center on a

particular aggregate or set of aggregates. When your use case has

finished, it can raise an event, and a handler elsewhere can run.

Is it a code smell for a use case to use multiple

repositories/aggregates, and if so, why?

An aggregate is a consistency boundary, so if your use case needs

to update two aggregates atomically (within the same transaction),

then your consistency boundary is wrong, strictly speaking. Ideally

you should think about moving to a new aggregate that wraps up all

the things you want to change at the same time.

If you’re actually updating only one aggregate and using the

other(s) for read-only access, then that’s fine , although you could

consider building a read/view model to get you that data instead—

it makes things cleaner if each use case has only one aggregate.

If you do need to modify two aggregates, but the two operations

don’t have to be in the same transaction/UoW, then consider

splitting the work out into two different handlers and using a

domain event to carry information between the two. You can read

more inthese papers on aggregate designby Vaughn Vernon.

What if I have a read-only but business-logic-heavy system?

View models can have complex logic in them. In this book, we’ve

encouraged you to separate your read and write models because

they have different consistency and throughput requirements.

Mostly, we can use simpler logic for reads, but that’s not always

true. In particular, permissions and authorization models can add a

lot of complexity to our read side.

We’ve written systems in which the view models needed extensive

unit tests. In those systems, we split a view builder from a view

fetcher , as inFigure E-4.



Figure E-4. A view builder and view fetcher (you can find a high-resolution version of

this diagram at cosmicpython.com)



\+ This makes it easy to test the view builder by giving it mocked data

(e.g., a list of dicts). “Fancy CQRS” with event handlers is really a

way of running our complex view logic whenever we write so that we

can avoid running it when we read.

Do I need to build microservices to do this stuff?

Egads, no! These techniques predate microservices by a decade or

so. Aggregates, domain events, and dependency inversion are ways

to control complexity in large systems. It just so happens that when

you’ve built a set of use cases and a model for a business process,

moving it to its own service is relatively easy, but that’s not a

requirement.

I’m using Django. Can I still do this?

We have an entire appendix just for you:Appendix D!

Footguns

OK, so we’ve given you a whole bunch of new toys to play with.

Here’s the fine print. Harry and Bob do not recommend that you copy

and paste our code into a production system and rebuild your

automated trading platform on Redis pub/sub. For reasons of brevity

and simplicity, we’ve hand-waved a lot of tricky subjects. Here’s a list

of things we think you should know before trying this for real.

Reliable messaging is hard

Redis pub/sub is not reliable and shouldn’t be used as a general-

purpose messaging tool. We picked it because it’s familiar and

easy to run. At MADE, we run Event Store as our messaging tool,

but we’ve had experience with RabbitMQ and Amazon

EventBridge.

Tyler Treat has some excellent blog posts on his site

bravenewgeek.com ; you should read at least read“You Cannot

Have Exactly-Once Delivery”and“What You Want Is What You

Don’t: Understanding Trade-Offs in Distributed Messaging”.

We explicitly choose small, focused transactions that can fail

independently

InChapter 8, we update our process so that deallocating an order

line and reallocating the line happen in two separate units of

work. You will need monitoring to know when these transactions

fail, and tooling to replay events. Some of this is made easier by

using a transaction log as your message broker (e.g., Kafka or

EventStore). You might also look at theOutbox pattern.

We don’t discuss idempotency

We haven’t given any real thought to what happens when handlers

are retried. In practice you will want to make handlers idempotent

so that calling them repeatedly with the same message will not

make repeated changes to state. This is a key technique for building

reliability, because it enables us to safely retry events when they

fail.

There’s a lot of good material on idempotent message handling, try

starting with“How to Ensure Idempotency in an Eventual Consistent

DDD/CQRS Application”and“(Un)Reliability in Messaging”.

Your events will need to change their schema over time

You’ll need to find some way of documenting your events and

sharing schema with consumers. We like using JSON schema and

markdown because it’s simple but there is other prior art. Greg

Young wrote an entire book on managing event-driven systems

over time: Versioning in an Event Sourced System (Leanpub).

More Required Reading

A few more books we’d like to recommend to help you on your way:

Clean Architectures in Python by Leonardo Giordani

(Leanpub), which came out in 2019, is one of the few

previous books on application architecture in Python.

Enterprise Integration Patterns by Gregor Hohpe and Bobby

Woolf (Addison-Wesley Professional) is a pretty good start

for messaging patterns.

Monolith to Microservices by Sam Newman (O’Reilly), and

Newman’s first book, Building Microservices (O’Reilly).

The Strangler Fig pattern is mentioned as a favorite, along

with many others. These are good to check out if you’re

thinking of moving to microservices, and they’re also good on

integration patterns and the considerations of async

messaging-based integration.

Wrap-Up

Phew! That’s a lot of warnings and reading suggestions; we hope we

haven’t scared you off completely. Our goal with this book is to give

you just enough knowledge and intuition for you to start building some

of this for yourself. We would love to hear how you get on and what

problems you’re facing with the techniques in your own systems, so

why not get in touch with us over at http://www.cosmicpython.com?

Appendix A. Summary

Diagram and Table

Here’s what our architecture looks like by the end of the book:

Table A-1recaps each pattern and what it does.

Table A-1. The components of our architecture and what they all

do



Layer



Compo

nent Description



Domain



Defines the business

logic.



Entity A domain object whose attributes may

change but that has a recognizable identity

over time.



Value

object



An immutable domain object whose attributes

entirely define it. It is fungible with other

identical objects.



Aggregat

e



Cluster of associated objects that we treat as

a unit for the purpose of data changes.

Defines and enforces a consistency

boundary.



Event Represents something that happened.



Comman

d



Represents a job the system should perform.



Se rvice Laye r



Defines the jobs the

system should perform

and orchestrates

different components.



Handler Receives a command or an event and

performs what needs to happen.



Unit of

work



Abstraction around data integrity. Each unit

of work represents an atomic update. Makes

repositories available. Tracks new events on

retrieved aggregates.



Message

bus

(internal)



Handles commands and events by routing

them to the appropriate handler.



Adapte rs (Secondary)



Concrete

implementations of an

interface that goes



Repositor

y



Abstraction around persistent storage. Each

aggregate has its own repository.



Layer



Compo

nent Description



from our system

to the outside world

(I/O).



Event

publisher



Pushes events onto the external message bus.



Entrypoints (Primary

adapters)



Translate external

inputs into calls into

the service layer.



Web Receives web requests and translates them

into commands, passing them to the internal

message bus.



Event

consumer



Reads events from the external message bus

and translates them into commands, passing

them to the internal message bus.



N/A External

message

bus

(message

broker)



A piece of infrastructure that different

services use to intercommunicate, via events.



Appendix B. A Template

Project Structure

AroundChapter 4, we moved from just having everything in one folder

to a more structured tree, and we thought it might be of interest to

outline the moving parts.

T IP



The code for this appendix is in the appendix\_project\_structure branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout appendix\_project\_structure



The basic folder structure looks like this:

Project tree

.



├── Dockerfile

├── Makefile

├── README.md

├── docker-compose.yml

├── license.txt

├── mypy.ini

├── requirements.txt

├── src

│ ├── allocation

│ │ ├── init.py

│ │ ├── adapters

│ │ │ ├── init.py



│ │ │ ├── orm.py

│ │ │ └── repository.py

│ │ ├── config.py

│ │ ├── domain

│ │ │ ├── init.py

│ │ │ └── model.py

│ │ ├── entrypoints

│ │ │ ├── init.py

│ │ │ └── flask\_app.py

│ │ └── service\_layer

│ │ ├── init.py

│ │ └── services.py

│ └── setup.py

└── tests

├── conftest.py

├── e2e

│ └── test\_api.py

├── integration

│ ├── test\_orm.py

│ └── test\_repository.py

├── pytest.ini

└── unit

├── test\_allocate.py

├── test\_batches.py

└── test\_services.py

Our docker-compose.yml and our Dockerfile are the main bits of

configuration for the containers that run our app, and they can also

run the tests (for CI). A more complex project might have several

Dockerfiles, although we’ve found that minimizing the number of

images is usually a good idea.

A Makefile provides the entrypoint for all the typical commands a

developer (or a CI server) might want to run during their normal

workflow: make build, make test, and so on. This is optional.

You could just use docker-compose and pytest directly, but if

nothing else, it’s nice to have all the “common commands” in a list

somewhere, and unlike documentation, a Makefile is code so it has

less tendency to become out of date.

All the source code for our app, including the domain model, the

Flask app, and infrastructure code, lives in a Python package

1

2

inside src , which we install using pip install -e and the

setup.py file. This makes imports easy. Currently, the structure

within this module is totally flat, but for a more complex project,

you’d expect to grow a folder hierarchy that includes

domain\_model/ , infrastructure/ , services/ , and api/.

Tests live in their own folder. Subfolders distinguish different test

types and allow you to run them separately. We can keep shared

fixtures ( conftest.py ) in the main tests folder and nest more

specific ones if we wish. This is also the place to keep pytest.ini.

T IP



Thepytest docsare really good on test layout and importability.



Let’s look at a few of these files and concepts in more detail.

Env Vars, 12-Factor, and Config, Inside

and Outside Containers

The basic problem we’re trying to solve here is that we need different

config settings for the following:

Running code or tests directly from your own dev machine,

perhaps talking to mapped ports from Docker containers

Running on the containers themselves, with “real” ports and

hostnames

Different container environments (dev, staging, prod, and so

on)

3

Configuration through environment variables as suggested by the12-

factor manifestowill solve this problem, but concretely, how do we

implement it in our code and our containers?

Config.py

Whenever our application code needs access to some config, it’s going

to get it from a file called config.py. Here are a couple of examples

from our app:

Sample config functions (src/allocation/config.py)



importos



def get\_postgres\_uri():

host=os.environ.get('DB\_HOST','localhost')

port= 54321 if host=='localhost' else 5432

password=os.environ.get('DB\_PASSWORD','abc123')

user,db\_name='allocation','allocation'

return f"postgresql://{user}:{password}@{host}:{port}/{db\_name}"



def get\_api\_url():

host=os.environ.get('API\_HOST','localhost')

port= 5005 if host =='localhost' else 80

return f"http://{host}:{port}"

We use functions for getting the current config, rather than constants

available at import time, because that allows client code to modify

os.environ if it needs to.

config.py also defines some default settings, designed to work

when running the code from the developer’s local machine.^4

An elegant Python package called environ-config is worth looking at if

you get tired of hand-rolling your own environment-based config

functions.

T IP



Don’t let this config module become a dumping ground that is full of things only

vaguely related to config and that is then imported all over the place. Keep things

immutable and modify them only via environment variables. If you decide to use a

bootstrap script, you can make it the only place (other than tests) that config is

imported to.



Docker-Compose and Containers Config

We use a lightweight Docker container orchestration tool called

docker-compose. It’s main configuration is via a YAML file (sigh):

docker-compose config file (docker-compose.yml)



version :"3"

services :



app :

build :

context :.

dockerfile :Dockerfile

depends\_on :



&#x20;   postgres

&#x20;   environment :

&#x20;   DB\_HOST=postgres

&#x20;   DB\_PASSWORD=abc123

&#x20;   API\_HOST=app

&#x20;   PYTHONDONTWRITEBYTECODE=1

&#x20;   volumes :



5



&#x20;   ./src:/src

&#x20;   ./tests:/tests

&#x20;   ports :

&#x20;   "5005:80"



postgres :

image :postgres:9.6

environment :



&#x20;   POSTGRES\_USER=allocation

&#x20;   POSTGRES\_PASSWORD=abc123

&#x20;   ports :

&#x20;   "54321:5432"



In the docker-compose file, we define the different services

(containers) that we need for our app. Usually one main image

contains all our code, and we can use it to run our API, our tests,

or any other service that needs access to the domain model.

You’ll probably have other infrastructure services, including a

database. In production you might not use containers for this; you

might have a cloud provider instead, but docker-compose gives us

a way of producing a similar service for dev or CI.

The environment stanza lets you set the environment variables for

your containers, the hostnames and ports as seen from inside the

Docker cluster. If you have enough containers that information

starts to be duplicated in these sections, you can use

environment\_file instead. We usually call ours container.env.

Inside a cluster, docker-compose sets up networking such that

containers are available to each other via hostnames named after

their service name.

Pro tip: if you’re mounting volumes to share source folders

between your local dev machine and the container, the

PYTHONDONTWRITEBYTECODE environment variable tells Python to

not write .pyc files, and that will save you from having millions of

root-owned files sprinkled all over your local filesystem, being all

annoying to delete and causing weird Python compiler errors

besides.

Mounting our source and test code as volumes means we don’t

need to rebuild our containers every time we make a code change.

The ports section allows us to expose the ports from inside the

containers to the outside world —these correspond to the default

ports we set in config.py.

NOT E



Inside Docker, other containers are available through hostnames named after their

service name. Outside Docker, they are available on localhost, at the port

defined in the ports section.



Installing Your Source as a Package

All our application code (everything except tests, really) lives inside

an src folder:

The src folder



├── src

│ ├── allocation

│ │ ├── config.py

│ │ └── ...

│ └── setup.py

Subfolders define top-level module names. You can have multiple

if you like.

6

And setup.py is the file you need to make it pip-installable, shown

next.

pip-installable modules in three lines (src/setup.py)



fromsetuptoolsimport setup



setup(

name='allocation',

version='0.1',

packages=\['allocation'],

)

That’s all you need. packages= specifies the names of subfolders that

you want to install as top-level modules. The name entry is just

cosmetic, but it’s required. For a package that’s never actually going to

hit PyPI, it’ll do fine.

Dockerfile

Dockerfiles are going to be very project-specific, but here are a few

key stages you’ll expect to see:

Our Dockerfile (Dockerfile)



FROM python:3.8-alpine



RUN apk add --no-cache --virtual .build-deps gcc postgresql-dev musl-dev

python3-dev

RUN apk add libpq



COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt



RUN apk del --no-cache .build-deps

7



RUN mkdir -p /src

COPY src/ /src/

RUN pip install -e /src

COPY tests/ /tests/



WORKDIR /src

ENV FLASK\_APP=allocation/entrypoints/flask\_app.py FLASK\_DEBUG=1

PYTHONUNBUFFERED=1

CMD flask run --host=0.0.0.0 --port=80

Installing system-level dependencies

Installing our Python dependencies (you may want to split out your

dev from prod dependencies; we haven’t here, for simplicity)

Copying and installing our source

Optionally configuring a default startup command (you’ll probably

override this a lot from the command line)

T IP



One thing to note is that we install things in the order of how frequently they are

likely to change. This allows us to maximize Docker build cache reuse. I can’t tell

you how much pain and frustration underlies this lesson. For this and many more

Python Dockerfile improvement tips, check out“Production-Ready Docker

Packaging”.



Tests

Our tests are kept alongside everything else, as shown here:

Tests folder tree



└── tests

├── conftest.py

├── e2e

│ └── test\_api.py

├── integration

│ ├── test\_orm.py

│ └── test\_repository.py

├── pytest.ini

└── unit

├── test\_allocate.py

├── test\_batches.py

└── test\_services.py

Nothing particularly clever here, just some separation of different test

types that you’re likely to want to run separately, and some files for

common fixtures, config, and so on.

There’s no src folder or setup.py in the test folders because we usually

haven’t needed to make tests pip-installable, but if you have

difficulties with import paths, you might find it helps.

Wrap-Up

These are our basic building blocks:

Source code in an src folder, pip-installable using setup.py

Some Docker config for spinning up a local cluster that

mirrors production as far as possible

Configuration via environment variables, centralized in a

Python file called config.py , with defaults allowing things to

run outside containers

A Makefile for useful command-line, um, commands

We doubt that anyone will end up with exactly the same solutions we

did, but we hope you find some inspiration here.



1 Splitting out images for production and testing is sometimes a good idea, but we’ve

tended to find that going further and trying to split out different images for different types

of application code (e.g., Web API versus pub/sub client) usually ends up being more

trouble than it’s worth; the cost in terms of complexity and longer rebuild/CI times is too

high. YMMV.



2 A pure-Python alternative to Makefiles isInvoke, worth checking out if everyone on your

team knows Python (or at least knows it better than Bash!).



3 “Testing and Packaging”by Hynek Schlawack provides more information on src folders.



4 This gives us a local development setup that “just works” (as much as possible). You

may prefer to fail hard on missing environment variables instead, particularly if any of the

defaults would be insecure in production.



5 Harry is a bit YAML-weary. It’s everywhere , and yet he can never remember the

syntax or how it’s supposed to indent.



6 On a CI server, you may not be able to expose arbitrary ports reliably, but it’s only a

convenience for local dev. You can find ways of making these port mappings optional

(e.g., with docker-compose.override.yml ).



7 For more setup.py tips, seethis article on packagingby Hynek.



Appendix C. Swapping Out

the Infrastructure: Do

Everything with CSVs

This appendix is intended as a little illustration of the benefits of the

Repository, Unit of Work, and Service Layer patterns. It’s intended to

follow fromChapter 6.

Just as we finish building out our Flask API and getting it ready for

release, the business comes to us apologetically, saying they’re not

ready to use our API and asking if we could build a thing that reads

just batches and orders from a couple of CSVs and outputs a third CSV

with allocations.

Ordinarily this is the kind of thing that might have a team cursing and

spitting and making notes for their memoirs. But not us! Oh no, we’ve

ensured that our infrastructure concerns are nicely decoupled from our

domain model and service layer. Switching to CSVs will be a simple

matter of writing a couple of new Repository and UnitOfWork

classes, and then we’ll be able to reuse all of our logic from the

domain layer and the service layer.

Here’s an E2E test to show you how the CSVs flow in and out:

A first CSV test (tests/e2e/test\_csv.py)



def test\_cli\_app\_reads\_csvs\_with\_batches\_and\_orders\_and\_outputs\_allocations(

make\_csv

):

sku1,sku2=random\_ref('s1'),random\_ref('s2')

batch1,batch2,batch3=random\_ref('b1'),random\_ref('b2'),

random\_ref('b3')

order\_ref=random\_ref('o')

make\_csv('batches.csv', \[

\['ref','sku','qty','eta'],

\[batch1,sku1, 100 ,''],

\[batch2,sku2, 100 ,'2011-01-01'],

\[batch3,sku2, 100 ,'2011-01-02'],

])

orders\_csv=make\_csv('orders.csv', \[

\['orderid','sku','qty'],

\[order\_ref,sku1, 3 ],

\[order\_ref,sku2, 12 ],

])



run\_cli\_script(orders\_csv.parent)



expected\_output\_csv=orders\_csv.parent/'allocations.csv'

with open(expected\_output\_csv) as f:

rows=list(csv.reader(f))

assert rows ==\[

\['orderid','sku','qty','batchref'],

\[order\_ref,sku1,'3',batch1],

\[order\_ref,sku2,'12',batch2],

]



Diving in and implementing without thinking about repositories and all

that jazz, you might start with something like this:

A first cut of our CSV reader/writer (src/bin/allocate-from-csv)



\#!/usr/bin/env python

importcsv

importsys

fromdatetimeimport datetime



frompathlibimport Path



fromallocationimport model



def load\_batches(batches\_path):

batches=\[]

with batches\_path.open() as inf:

reader=csv.DictReader(inf)

for row in reader:

if row\['eta']:

eta=datetime.strptime(row\['eta'],'%Y-%m-%d').date()

else :

eta=None

batches.append(model.Batch(

ref=row\['ref'],

sku=row\['sku'],

qty=int(row\['qty']),

eta=eta

))

return batches



def main(folder):

batches\_path=Path(folder)/'batches.csv'

orders\_path=Path(folder)/'orders.csv'

allocations\_path=Path(folder)/'allocations.csv'



batches=load\_batches(batches\_path)



with orders\_path.open() as inf,allocations\_path.open('w') as outf:

reader=csv.DictReader(inf)

writer=csv.writer(outf)

writer.writerow(\['orderid','sku','batchref'])

for row in reader:

orderid,sku=row\['orderid'],row\['sku']

qty=int(row\['qty'])

line=model.OrderLine(orderid,sku,qty)

batchref=model.allocate(line,batches)

writer.writerow(\[line.orderid,line.sku,batchref])



if name =='main':

main(sys.argv\[ 1 ])

It’s not looking too bad! And we’re reusing our domain model objects

and our domain service.

But it’s not going to work. Existing allocations need to also be part of

our permanent CSV storage. We can write a second test to force us to

improve things:

And another one, with existing allocations (tests/e2e/test\_csv.py)



def test\_cli\_app\_also\_reads\_existing\_allocations\_and\_can\_append\_to\_them(

make\_csv

):

sku=random\_ref('s')

batch1,batch2=random\_ref('b1'),random\_ref('b2')

old\_order,new\_order=random\_ref('o1'),random\_ref('o2')

make\_csv('batches.csv', \[

\['ref','sku','qty','eta'],

\[batch1,sku, 10 ,'2011-01-01'],

\[batch2,sku, 10 ,'2011-01-02'],

])

make\_csv('allocations.csv', \[

\['orderid','sku','qty','batchref'],

\[old\_order,sku, 10 ,batch1],

])

orders\_csv=make\_csv('orders.csv', \[

\['orderid','sku','qty'],

\[new\_order,sku, 7 ],

])



run\_cli\_script(orders\_csv.parent)



expected\_output\_csv=orders\_csv.parent/'allocations.csv'

with open(expected\_output\_csv) as f:



rows=list(csv.reader(f))

assert rows ==\[

\['orderid','sku','qty','batchref'],

\[old\_order,sku,'10',batch1],

\[new\_order,sku,'7',batch2],

]



And we could keep hacking about and adding extra lines to that

load\_batches function, and some sort of way of tracking and saving

new allocations—but we already have a model for doing that! It’s

called our Repository and Unit of Work patterns.

All we need to do (“all we need to do”) is reimplement those same

abstractions, but with CSVs underlying them instead of a database.

And as you’ll see, it really is relatively straightforward.

Implementing a Repository and Unit of

Work for CSVs

Here’s what a CSV-based repository could look like. It abstracts away

all the logic for reading CSVs from disk, including the fact that it has

to read two different CSVs (one for batches and one for allocations),

and it gives us just the familiar .list() API, which provides the

illusion of an in-memory collection of domain objects:

A repository that uses CSV as its storage mechanism

(src/allocation/service\_layer/csv\_uow.py)



classCsvRepository (repository.AbstractRepository):



def \_\_init\_\_(self,folder):

self.\_batches\_path=Path(folder)/'batches.csv'



self.\_allocations\_path=Path(folder)/'allocations.csv'

self.\_batches={} # type: Dict\[str, model.Batch]

self.\_load()



def get(self,reference):

return self.\_batches.get(reference)



def add(self,batch):

self.\_batches\[batch.reference]=batch



def \_load(self):

with self.\_batches\_path.open() as f:

reader=csv.DictReader(f)

for row in reader:

ref,sku=row\['ref'],row\['sku']

qty=int(row\['qty'])

if row\['eta']:

eta=datetime.strptime(row\['eta'],'%Y-%m-%d').date()

else :

eta=None

self.\_batches\[ref]=model.Batch(

ref=ref,sku=sku,qty=qty,eta=eta

)

if self.\_allocations\_path.exists() is False:

return

with self.\_allocations\_path.open() as f:

reader=csv.DictReader(f)

for row in reader:

batchref,orderid,sku=row\['batchref'],row\['orderid'],

row\['sku']

qty=int(row\['qty'])

line=model.OrderLine(orderid,sku,qty)

batch=self.\_batches\[batchref]

batch.\_allocations.add(line)



def list(self):

return list(self.\_batches.values())



And here’s what a UoW for CSVs would look like:

A UoW for CSVs: commit = csv.writer

(src/allocation/service\_layer/csv\_uow.py)



classCsvUnitOfWork (unit\_of\_work.AbstractUnitOfWork):



def \_\_init\_\_(self,folder):

self.batches=CsvRepository(folder)



def commit(self):

with self.batches.\_allocations\_path.open('w') as f:

writer=csv.writer(f)

writer.writerow(\['orderid','sku','qty','batchref'])

for batch in self.batches.list():

for line in batch.\_allocations:

writer.writerow(

\[line.orderid,line.sku,line.qty,batch.reference]

)



def rollback(self):

pass



And once we have that, our CLI app for reading and writing batches

and allocations to CSV is pared down to what it should be—a bit of

code for reading order lines, and a bit of code that invokes our

existing service layer:

Allocation with CSVs in nine lines (src/bin/allocate-from-csv)



def main(folder):

orders\_path=Path(folder)/'orders.csv'

uow=csv\_uow.CsvUnitOfWork(folder)

with orders\_path.open() as f:

reader=csv.DictReader(f)

for row in reader:

orderid,sku=row\['orderid'],row\['sku']

qty=int(row\['qty'])

services.allocate(orderid,sku,qty,uow)

Ta-da! Now are y’all impressed or what?

Much love,

Bob and Harry

Appendix D. Repository and

Unit of Work Patterns with

Django

Suppose you wanted to use Django instead of SQLAlchemy and Flask.

How might things look? The first thing is to choose where to install it.

We put it in a separate package next to our main allocation code:



├──src

│ ├──allocation

│ │ ├──init.py

│ │ ├──adapters

│ │ │ ├──init.py

...

│ ├──djangoproject

│ │ ├──alloc

│ │ │ ├──init.py

│ │ │ ├──apps.py

│ │ │ ├──migrations

│ │ │ │ ├── 0001 \_initial.py

│ │ │ │ └──init.py

│ │ │ ├──models.py

│ │ │ └──views.py

│ │ ├──django\_project

│ │ │ ├──init.py

│ │ │ ├──settings.py

│ │ │ ├──urls.py

│ │ │ └──wsgi.py

│ │ └──manage.py

│ └──setup.py

└──tests

├──conftest.py

├──e2e

│ └──test\_api.py

├──integration



│ ├──test\_repository.py

...

T IP



The code for this appendix is in the appendix\_django branchon GitHub:



git clone https://github.com/cosmicpython/code.git

cd code

git checkout appendix\_django



Repository Pattern with Django

We used a plug-in calledpytest-djangoto help with test database

management.

Rewriting the first repository test was a minimal change—just

rewriting some raw SQL with a call to the Django ORM/QuerySet

language:

First repository test adapted (tests/integration/test\_repository.py)



fromdjangoproject.allocimport models as django\_models



@pytest.mark.django\_db

def test\_repository\_can\_save\_a\_batch():

batch=model.Batch("batch1","RUSTY-SOAPDISH", 100 ,eta=date( 2011 , 12 , 25 ))



repo=repository.DjangoRepository()

repo.add(batch)



\[saved\_batch]=django\_models.Batch.objects.all()

assert saved\_batch.reference==batch.reference

assert saved\_batch.sku==batch.sku



assert saved\_batch.qty==batch.\_purchased\_quantity

assert saved\_batch.eta==batch.eta



The second test is a bit more involved since it has allocations, but it is

still made up of familiar-looking Django code:

Second repository test is more involved

(tests/integration/test\_repository.py)



@pytest.mark.django\_db

def test\_repository\_can\_retrieve\_a\_batch\_with\_allocations():

sku="PONY-STATUE"

d\_line=django\_models.OrderLine.objects.create(orderid="order1",sku=sku,

qty= 12 )

d\_b1=django\_models.Batch.objects.create(

reference="batch1",sku=sku,qty= 100 ,eta=None

)

d\_b2=django\_models.Batch.objects.create(

reference="batch2",sku=sku,qty= 100 ,eta=None

)

django\_models.Allocation.objects.create(line=d\_line,batch=d\_batch1)



repo=repository.DjangoRepository()

retrieved=repo.get("batch1")



expected=model.Batch("batch1",sku, 100 ,eta=None)

assert retrieved==expected # Batch.\_\_eq\_\_ only compares reference

assert retrieved.sku==expected.sku

assert retrieved.\_purchased\_quantity==expected.\_purchased\_quantity

assert retrieved.\_allocations=={

model.OrderLine("order1",sku, 12 ),

}



Here’s how the actual repository ends up looking:

A Django repository (src/allocation/adapters/repository.py)



classDjangoRepository (AbstractRepository):



def add(self,batch):

super().add(batch)

self.update(batch)



def update(self,batch):

django\_models.Batch.update\_from\_domain(batch)



def \_get(self,reference):

return django\_models.Batch.objects.filter(

reference=reference

).first().to\_domain()



def list(self):

return \[b.to\_domain() for b in django\_models.Batch.objects.all()]



You can see that the implementation relies on the Django models

having some custom methods for translating to and from our domain

model.

Custom Methods on Django ORM Classes to

Translate to/from Our Domain Model

Those custom methods look something like this:

Django ORM with custom methods for domain model conversion

(src/djangoproject/alloc/models.py)



fromdjango.dbimport models

fromallocation.domainimport model as domain\_model



classBatch (models.Model):

reference=models.CharField(max\_length= 255 )

sku=models.CharField(max\_length= 255 )

qty=models.IntegerField()

eta=models.DateField(blank=True,null=True)



@staticmethod

def update\_from\_domain(batch:domain\_model.Batch):



1



try :

b=Batch.objects.get(reference=batch.reference)

except Batch.DoesNotExist:

b=Batch(reference=batch.reference)

b.sku=batch.sku

b.qty=batch.\_purchased\_quantity

b.eta=batch.eta

b.save()

b.allocation\_set.set(

Allocation.from\_domain(l,b)

for l in batch.\_allocations

)



def to\_domain(self)->domain\_model.Batch:

b=domain\_model.Batch(

ref=self.reference,sku=self.sku,qty=self.qty,eta=self.eta

)

b.\_allocations=set(

a.line.to\_domain()

for a in self.allocation\_set.all()

)

return b



classOrderLine (models.Model):

\#...

For value objects, objects.get\_or\_create can work, but for

entities, you probably need an explicit try-get/except to handle the

upsert.

We’ve shown the most complex example here. If you do decide to

do this, be aware that there will be boilerplate! Thankfully it’s not

very complex boilerplate.

Relationships also need some careful, custom handling.

2

NOT E



As inChapter 2, we use dependency inversion. The ORM (Django) depends on

the model and not the other way around.



Unit of Work Pattern with Django

The tests don’t change too much:

Adapted UoW tests (tests/integration/test\_uow.py)



def insert\_batch(ref,sku,qty,eta):

django\_models.Batch.objects.create(reference=ref,sku=sku,qty=qty,eta=eta)



def get\_allocated\_batch\_ref(orderid,sku):

return django\_models.Allocation.objects.get(

line\_\_orderid=orderid,line\_\_sku=sku

).batch.reference



@pytest.mark.django\_db(transaction=True)

def test\_uow\_can\_retrieve\_a\_batch\_and\_allocate\_to\_it():

insert\_batch('batch1','HIPSTER-WORKBENCH', 100 ,None)



uow=unit\_of\_work.DjangoUnitOfWork()

with uow:

batch=uow.batches.get(reference='batch1')

line=model.OrderLine('o1','HIPSTER-WORKBENCH', 10 )

batch.allocate(line)

uow.commit()



batchref=get\_allocated\_batch\_ref('o1','HIPSTER-WORKBENCH')

assert batchref =='batch1'



@pytest.mark.django\_db(transaction=True)



def test\_rolls\_back\_uncommitted\_work\_by\_default():

...



@pytest.mark.django\_db(transaction=True)

def test\_rolls\_back\_on\_error():

...

Because we had little helper functions in these tests, the actual

main bodies of the tests are pretty much the same as they were with

SQLAlchemy.

The pytest-django mark.django\_db(transaction=True) is

required to test our custom transaction/rollback behaviors.

And the implementation is quite simple, although it took me a few tries

to find which invocation of Django’s transaction magic would work:

UoW adapted for Django

(src/allocation/service\_layer/unit\_of\_work.py)



classDjangoUnitOfWork (AbstractUnitOfWork):



def \_\_enter\_\_(self):

self.batches=repository.DjangoRepository()

transaction.set\_autocommit(False)

return super().\_\_enter\_\_()



def \_\_exit\_\_(self,\*args):

super().\_\_exit\_\_(\*args)

transaction.set\_autocommit(True)



def commit(self):

for batch in self.batches.seen:

self.batches.update(batch)

transaction.commit()



def rollback(self):

transaction.rollback()



set\_autocommit(False) was the best way to tell Django to stop

automatically committing each ORM operation immediately, and to

begin a transaction.

Then we use the explicit rollback and commits.

One difficulty: because, unlike with SQLAlchemy, we’re not

instrumenting the domain model instances themselves, the

commit() command needs to explicitly go through all the objects

that have been touched by every repository and manually update

them back to the ORM.

API: Django Views Are Adapters

The Django views.py file ends up being almost identical to the old

flask\_app.py , because our architecture means it’s a very thin wrapper

around our service layer (which didn’t change at all, by the way):

Flask app→ Django views (src/djangoproject/alloc/views.py)



os.environ\['DJANGO\_SETTINGS\_MODULE']='djangoproject.django\_project.settings'

django.setup()



@csrf\_exempt

def add\_batch(request):

data=json.loads(request.body)

eta=data\['eta']

if eta is not None:

eta=datetime.fromisoformat(eta).date()

services.add\_batch(

data\['ref'],data\['sku'],data\['qty'],eta,

unit\_of\_work.DjangoUnitOfWork(),

)

return HttpResponse('OK',status= 201 )



@csrf\_exempt



def allocate(request):

data=json.loads(request.body)

try :

batchref=services.allocate(

data\['orderid'],

data\['sku'],

data\['qty'],

unit\_of\_work.DjangoUnitOfWork(),

)

except (model.OutOfStock,services.InvalidSku) as e:

return JsonResponse({'message':str(e)},status= 400 )



return JsonResponse({'batchref':batchref},status= 201 )



Why Was This All So Hard?

OK, it works, but it does feel like more effort than Flask/SQLAlchemy.

Why is that?

The main reason at a low level is because Django’s ORM doesn’t

work in the same way. We don’t have an equivalent of the

SQLAlchemy classical mapper, so our ActiveRecord and our domain

model can’t be the same object. Instead we have to build a manual

translation layer behind the repository. That’s more work (although

once it’s done, the ongoing maintenance burden shouldn’t be too high).

Because Django is so tightly coupled to the database, you have to use

helpers like pytest-django and think carefully about test databases,

right from the very first line of code, in a way that we didn’t have to

when we started out with our pure domain model.

But at a higher level, the entire reason that Django is so great is that

it’s designed around the sweet spot of making it easy to build CRUD

apps with minimal boilerplate. But the entire thrust of our book is

about what to do when your app is no longer a simple CRUD app.

At that point, Django starts hindering more than it helps. Things like

the Django admin, which are so awesome when you start out, become

actively dangerous if the whole point of your app is to build a complex

set of rules and modeling around the workflow of state changes. The

Django admin bypasses all of that.

What to Do If You Already Have Django

So what should you do if you want to apply some of the patterns in this

book to a Django app? We’d say the following:

The Repository and Unit of Work patterns are going to be

quite a lot of work. The main thing they will buy you in the

short term is faster unit tests, so evaluate whether that benefit

feels worth it in your case. In the longer term, they decouple

your app from Django and the database, so if you anticipate

wanting to migrate away from either of those, Repository and

UoW are a good idea.

The Service Layer pattern might be of interest if you’re seeing

a lot of duplication in your views.py. It can be a good way of

thinking about your use cases separately from your web

endpoints.

You can still theoretically do DDD and domain modeling with

Django models, tightly coupled as they are to the database;

you may be slowed by migrations, but it shouldn’t be fatal. So

as long as your app is not too complex and your tests not too

slow, you may be able to get something out of the fat models

approach: push as much logic down to your models as

possible, and apply patterns like Entity, Value Object, and

Aggregate. However, see the following caveat.

With that said,word in the Django communityis that people find that

the fat models approach runs into scalability problems of its own,

particularly around managing interdependencies between apps. In

those cases, there’s a lot to be said for extracting out a business logic

or domain layer to sit between your views and forms and your

models.py , which you can then keep as minimal as possible.

Steps Along the Way

Suppose you’re working on a Django project that you’re not sure is

going to get complex enough to warrant the patterns we recommend,

but you still want to put a few steps in place to make your life easier,

both in the medium term and if you want to migrate to some of our

patterns later. Consider the following:

One piece of advice we’ve heard is to put a logic.py into

every Django app from day one. This gives you a place to put

business logic, and to keep your forms, views, and models

free of business logic. It can become a stepping-stone for

moving to a fully decoupled domain model and/or service

layer later.

A business-logic layer might start out working with Django

model objects and only later become fully decoupled from the

framework and work on plain Python data structures.

For the read side, you can get some of the benefits of CQRS

by putting reads into one place, avoiding ORM calls

sprinkled all over the place.

When separating out modules for reads and modules for

domain logic, it may be worth decoupling yourself from the

Django apps hierarchy. Business concerns will cut across

them.

NOT E



We’d like to give a shout-out to David Seddon and Ashia Zawaduk for talking

through some of the ideas in this appendix. They did their best to stop us from

saying anything really stupid about a topic we don’t really have enough personal

experience of, but they may have failed.



For more thoughts and actual lived experience dealing with existing

applications, refer to theepilogue.



1 The DRY-Python project people have built a tool calledmappersthat looks like it might

help minimize boilerplate for this sort of thing.



2 @mr-bo-jangles suggested you might be able to useupdate\_or\_create, but that’s

beyond our Django-fu.



Appendix E. Validation

Whenever we’re teaching and talking about these techniques, one

question that comes up over and over is “Where should I do

validation? Does that belong with my business logic in the domain

model, or is that an infrastructural concern?”

As with any architectural question, the answer is: it depends!

The most important consideration is that we want to keep our code

well separated so that each part of the system is simple. We don’t want

to clutter our code with irrelevant detail.

What Is Validation, Anyway?

When people use the word validation , they usually mean a process

whereby they test the inputs of an operation to make sure that they

match certain criteria. Inputs that match the criteria are considered

valid , and inputs that don’t are invalid.

If the input is invalid, the operation can’t continue but should exit with

some kind of error. In other words, validation is about creating

preconditions. We find it useful to separate our preconditions into

three subtypes: syntax, semantics, and pragmatics.

Validating Syntax

In linguistics, the syntax of a language is the set of rules that govern the

structure of grammatical sentences. For example, in English, the

sentence “Allocate three units of TASTELESS-LAMP to order twenty-

seven” is grammatically sound, while the phrase “hat hat hat hat hat hat

wibble” is not. We can describe grammatically correct sentences as

well formed.

How does this map to our application? Here are some examples of

syntactic rules:

An Allocate command must have an order ID, a SKU, and a

quantity.

A quantity is a positive integer.

A SKU is a string.

These are rules about the shape and structure of incoming data. An

Allocate command without a SKU or an order ID isn’t a valid

message. It’s the equivalent of the phrase “Allocate three to.”

We tend to validate these rules at the edge of the system. Our rule of

thumb is that a message handler should always receive only a message

that is well-formed and contains all required information.

One option is to put your validation logic on the message type itself:

Validation on the message class (src/allocation/commands.py)



fromschemaimport And,Schema,Use



@dataclass



classAllocate (Command):



\_schema=Schema({

'orderid':int,

sku:str,

qty:And(Use(int), lambda n:n> 0 )

},ignore\_extra\_keys=True)



orderid:str

sku:str

qty:int



@classmethod

def from\_json(cls,data):

data =json.loads(data)

return cls(\*\*\_schema.validate(data))



Theschema librarylets us describe the structure and validation of

our messages in a nice declarative way.

The from\_json method reads a string as JSON and turns it into our

message type.

This can get repetitive, though, since we need to specify our fields

twice, so we might want to introduce a helper library that can unify the

validation and declaration of our message types:

A command factory with schema (src/allocation/commands.py)



def command(name,fields):

schema=Schema(And(Use(json.loads),fields),ignore\_extra\_keys=True)

cls=make\_dataclass(name,fields.keys())

cls.from\_json= lambda s:cls(schema.validate(s))

return cls



def greater\_than\_zero(x):

return x> 0



quantity=And(Use(int),greater\_than\_zero)



Allocate=command(

orderid=int,

sku=str,

qty=quantity

)



AddStock=command(

sku=str,

qty=quantity

The command function takes a message name, plus kwargs for the

fields of the message payload, where the name of the kwarg is the

name of the field and the value is the parser.

We use the make\_dataclass function from the dataclass module to

dynamically create our message type.

We patch the from\_json method onto our dynamic dataclass.

We can create reusable parsers for quantity, SKU, and so on to

keep things DRY.

Declaring a message type becomes a one-liner.

This comes at the expense of losing the types on your dataclass, so

bear that trade-off in mind.

Postel’s Law and the Tolerant Reader

Pattern

Postel’s law , or the robustness principle , tells us, “Be liberal in what

you accept, and conservative in what you emit.” We think this applies

particularly well in the context of integration with our other systems.

The idea here is that we should be strict whenever we’re sending

messages to other systems, but as lenient as possible when we’re

receiving messages from others.

For example, our system could validate the format of a SKU. We’ve

been using made-up SKUs like UNFORGIVING-CUSHION and

MISBEGOTTEN-POUFFE. These follow a simple pattern: two words,

separated by dashes, where the second word is the type of product and

the first word is an adjective.

Developers love to validate this kind of thing in their messages, and

reject anything that looks like an invalid SKU. This causes horrible

problems down the line when some anarchist releases a product named

COMFY-CHAISE-LONGUE or when a snafu at the supplier results in a

shipment of CHEAP-CARPET-2.

Really, as the allocation system, it’s none of our business what the

format of a SKU might be. All we need is an identifier, so we can

simply describe it as a string. This means that the procurement system

can change the format whenever they like, and we won’t care.

This same principle applies to order numbers, customer phone

numbers, and much more. For the most part, we can ignore the internal

structure of strings.

Similarly, developers love to validate incoming messages with tools

like JSON Schema, or to build libraries that validate incoming

messages and share them among systems. This likewise fails the

robustness test.

Let’s imagine, for example, that the procurement system adds new

fields to the ChangeBatchQuantity message that record the reason

for the change and the email of the user responsible for the change.

Since these fields don’t matter to the allocation service, we should

simply ignore them. We can do that in the schema library by passing

the keyword arg ignore\_extra\_keys=True.

This pattern, whereby we extract only the fields we care about and do

minimal validation of them, is the Tolerant Reader pattern.

T IP



Validate as little as possible. Read only the fields you need, and don’t overspecify

their contents. This will help your system stay robust when other systems change

over time. Resist the temptation to share message definitions between systems:

instead, make it easy to define the data you depend on. For more info, see Martin

Fowler’s article on theTolerant Reader pattern.



IS POSTEL ALWAYS RIGHT?



Mentioning Postel can be quite triggering to some people. They willtell youthat Postel is the

precise reason that everything on the internet is broken and we can’t have nice things. Ask Hynek

about SSLv3 one day.

We like the Tolerant Reader approach in the particular context of event-based integration

between services that we control, because it allows for independent evolution of those services.

If you’re in charge of an API that’s open to the public on the big bad internet, there might be good

reasons to be more conservative about what inputs you allow.



Validating at the Edge

Earlier, we said that we want to avoid cluttering our code with

irrelevant details. In particular, we don’t want to code defensively

inside our domain model. Instead, we want to make sure that requests

are known to be valid before our domain model or use-case handlers

see them. This helps our code stay clean and maintainable over the

long term. We sometimes refer to this as validating at the edge of the

system.

In addition to keeping your code clean and free of endless checks and

asserts, bear in mind that invalid data wandering through your system

is a time bomb; the deeper it gets, the more damage it can do, and the

fewer tools you have to respond to it.

Back inChapter 8, we said that the message bus was a great place to

put cross-cutting concerns, and validation is a perfect example of that.

Here’s how we might change our bus to perform validation for us:

Validation



classMessageBus :



def handle\_message(self,name:str,body:str):

try :

message\_type=next(mt for mt in EVENT\_HANDLERS if mt.name==

name)

message=message\_type.from\_json(body)

self.handle(\[message])

exceptStopIteration :

raiseKeyError (f"Unknown message name {name}")

except ValidationError as e:

logging.error(

f'invalid message of type {name} \\n '

f'{body} \\n '

f'{e}'

)



raise e



Here’s how we might use that method from our Flask API endpoint:

API bubbles up validation errors (src/allocation/flask\_app.py)



@app.route("/change\_quantity",methods=\['POST'])

def change\_batch\_quantity():

try :

bus.handle\_message('ChangeBatchQuantity',request.body)

except ValidationError as e:

return bad\_request(e)

except exceptions.InvalidSku as e:

return jsonify({'message':str(e)}), 400



def bad\_request(e:ValidationError):

return e.code, 400

And here’s how we might plug it in to our asynchronous message

processor:

Validation errors when handling Redis messages

(src/allocation/redis\_pubsub.py)



def handle\_change\_batch\_quantity(m,bus:messagebus.MessageBus):

try :

bus.handle\_message('ChangeBatchQuantity',m)

except ValidationError:

print ('Skipping invalid message')

except exceptions.InvalidSku as e:

print (f'Unable to change stock for missing sku {e}')

Notice that our entrypoints are solely concerned with how to get a

message from the outside world and how to report success or failure.

Our message bus takes care of validating our requests and routing them

to the correct handler, and our handlers are exclusively focused on the

logic of our use case.

T IP



When you receive an invalid message, there’s usually little you can do but log the

error and continue. At MADE we use metrics to count the number of messages a

system receives, and how many of those are successfully processed, skipped, or

invalid. Our monitoring tools will alert us if we see spikes in the numbers of bad

messages.



Validating Semantics

While syntax is concerned with the structure of messages, semantics is

the study of meaning in messages. The sentence “Undo no dogs from

ellipsis four” is syntactically valid and has the same structure as the

sentence “Allocate one teapot to order five,"” but it is meaningless.

We can read this JSON blob as an Allocate command but can’t

successfully execute it, because it’s nonsense :

A meaningless message

{



"orderid":"superman",

"sku":"zygote",

"qty":- 1

}

We tend to validate semantic concerns at the message-handler layer

with a kind of contract-based programming:

Preconditions (src/allocation/ensure.py)

"""



This module contains preconditions that we apply to our handlers.

"""



classMessageUnprocessable ( Exception ):



def \_\_init\_\_(self,message):

self.message=message



classProductNotFound (MessageUnprocessable):

""""

This exception is raised when we try to perform an action on a product

that doesn't exist in our database.

""" "



def \_\_init\_\_(self,message):

super().\_\_init\_\_(message)

self.sku=message.sku



def product\_exists(event,uow):

product=uow.products.get(event.sku)

if product is None:

raise ProductNotFound(event)

We use a common base class for errors that mean a message is

invalid.

Using a specific error type for this problem makes it easier to

report on and handle the error. For example, it’s easy to map

ProductNotFound to a 404 in Flask.

product\_exists is a precondition. If the condition is False, we

raise an error.

This keeps the main flow of our logic in the service layer clean and

declarative:

Ensure calls in services (src/allocation/services.py)



\# services.py



fromallocationimport ensure



def allocate(event,uow):

line=mode.OrderLine(event.orderid,event.sku,event.qty)

with uow:

ensure.product\_exists(uow,event)



product=uow.products.get(line.sku)

product.allocate(line)

uow.commit()



We can extend this technique to make sure that we apply messages

idempotently. For example, we want to make sure that we don’t insert

a batch of stock more than once.

If we get asked to create a batch that already exists, we’ll log a

warning and continue to the next message:

Raise SkipMessage exception for ignorable events

(src/allocation/services.py)



classSkipMessage ( Exception ):

""""

This exception is raised when a message can't be processed, but there's no

incorrect behavior. For example, we might receive the same message multiple

times, or we might receive a message that is now out of date.

""" "



def \_\_init\_\_(self,reason):

self.reason=reason



def batch\_is\_new(self,event,uow):

batch=uow.batches.get(event.batchid)



if batch is not None:

raise SkipMessage(f"Batch with id {event.batchid} already exists")



Introducing a SkipMessage exception lets us handle these cases in a

generic way in our message bus:

The bus now knows how to skip (src/allocation/messagebus.py)



classMessageBus :



def handle\_message(self,message):

try :

...

except SkipMessage as e:

logging.warn(f"Skipping message {message.id} because {e.reason}")



There are a couple of pitfalls to be aware of here. First, we need to be

sure that we’re using the same UoW that we use for the main logic of

our use case. Otherwise, we open ourselves to irritating concurrency

bugs.

Second, we should try to avoid putting all our business logic into these

precondition checks. As a rule of thumb, if a rule can be tested inside

our domain model, then it should be tested in the domain model.

Validating Pragmatics

Pragmatics is the study of how we understand language in context.

After we have parsed a message and grasped its meaning, we still

need to process it in context. For example, if you get a comment on a

pull request saying, “I think this is very brave,” it may mean that the

reviewer admires your courage—unless they’re British, in which case,

they’re trying to tell you that what you’re doing is insanely risky, and

only a fool would attempt it. Context is everything.

VALIDATION RECAP



Validation means different things to different people

When talking about validation, make sure you’re clear about what you’re validating. We find it

useful to think about syntax, semantics, and pragmatics: the structure of messages, the

meaningfulness of messages, and the business logic governing our response to

messages.



Validate at the edge when possible

Validating required fields and the permissible ranges of numbers is b oring , and we want to

keep it out of our nice clean codebase. Handlers should always receive only valid

messages.



Only validate what you require

Use the Tolerant Reader pattern: read only the fields your application needs and don’t

overspecify their internal structure. Treating fields as opaque strings buys you a lot of

flexibility.

Spend time writing helpers for validation

Having a nice declarative way to validate incoming messages and apply preconditions to

your handlers will make your codebase much cleaner. It’s worth investing time to make

boring code easy to maintain.



Locate each of the three types of validation in the right place

Validating syntax can happen on message classes, validating semantics can happen in the

service layer or on the message bus, and validating pragmatics belongs in the domain

model.



T IP



Once you’ve validated the syntax and semantics of your commands at the edges

of your system, the domain is the place for the rest of your validation. Validation

of pragmatics is often a core part of your business rules.



In software terms, the pragmatics of an operation are usually managed

by the domain model. When we receive a message like “allocate three

million units of SCARCE-CLOCK to order 76543,” the message is

syntactically valid and semantically valid, but we’re unable to

comply because we don’t have the stock available.

Index

SYMBOLS

@abc.abstractmethod,The Repository in the Abstract

A

abstract base classes (ABCs)

ABC for the repository,The Repository in the Abstract

defining for notifications,Define the Abstract and Concrete

Implementations

switching to typing.Protocol,Option 3: The UoW Publishes

Events to the Message Bus

using duck typing and protocols instead of,The Repository in the

Abstract

using for ports,What Is a Port and What Is an Adapter, in Python?

abstract methods,The Repository in the Abstract

abstractions,A Brief Interlude: On Coupling and Abstractions-Wrap-

Up

abstracting state to aid testability,Abstracting State Aids

Testability-Abstracting State Aids Testability

AbstractRepository, service function depending on,A Typical

Service Function

AbstractUnitOfWork,Unit of Work and Its Context Manager

choosing right abstraction,Choosing the Right Abstraction(s)-

Implementing Our Chosen Abstractions

explicit dependencies are more abstract,Aren’t Explicit

Dependencies Totally Weird and Java-y?

implementing chosen abstraction,Implementing Our Chosen

Abstractions-Wrap-Up

edge-to-edge testing with fakes and dependency injection,

Testing Edge to Edge with Fakes and Dependency Injection-

Testing Edge to Edge with Fakes and Dependency Injection

not using mock.patch for testing,Why Not Just Patch It Out?

simplifying interface between business logic and I/O,Wrap-Up

using to reduce coupling,A Brief Interlude: On Coupling and

Abstractions

adapters

building adapter and doing dependency injection for it,Building

an Adapter “Properly”: A Worked Example-Wrap-Up

defining abstract and concrete implementations,Define the

Abstract and Concrete Implementations

defined,What Is a Port and What Is an Adapter, in Python?

Django views,API: Django Views Are Adapters

exercise for the reader,Figure Out How to Integration Test the

Real Thing

ports-and-adapters inspired patterns,Part I Recap

putting into folder,Putting Things in Folders to See Where It All

Belongs

Aggregate pattern,What Is an Aggregate?

aggregates

about,What Is an Aggregate?

acting as consistency boundaries,Discussion: Events, Commands,

and Error Handling

and consistency boundaries recap,Wrap-Up

changing multiple aggregates in a request,Wrap-Up

choosing an aggregrate,Choosing an Aggregate-Choosing an

Aggregate

exercise for the reader,What About Performance?

History aggregate recording orders and raising domain events,

Discussion: Events, Commands, and Error Handling

identifying aggregates and bounded contexts,Identifying

Aggregates and Bounded Contexts-An Event-Driven Approach to

Go to Microservices via Strangler Pattern

one aggregrate = one repository,One Aggregate = One

Repository

optimistic concurrency with version numbers,Optimistic

Concurrency with Version Numbers-Implementation Options for

Version Numbers

performance and,What About Performance?

Product aggregate,Aggregates and Consistency Boundaries

pros and cons or trade-offs,Wrap-Up

query on repository returning single aggregate,Implementation

raising events about,Discussion: Events, Commands, and Error

Handling

repository keeping track of aggregates passing through it,Option

3: The UoW Publishes Events to the Message Bus

testing for data integrity rules,Testing for Our Data Integrity

Rules-Pessimistic Concurrency Control Example: SELECT FOR

UPDATE

testing Product object to raise events,The Model Raises Events

UoW collecting events from and passing them to message bus,

Wrap-Up

allocate service

allocating against all batches with,Choosing an Aggregate

moving to be a method on Product aggregate,Choosing an

Aggregate

Allocated event,Our New Outgoing Event

AllocationRequired event,Refactoring Service Functions to Message

Handlers

passing to services.allocate,Imagining an Architecture Change:

Everything Will Be an Event Handler

Anemic Domain anti-pattern,The DIP in Action

APIs

adding API for adding a batch,Carrying the Improvement

Through to the E2E Tests

Django views as adapters,API: Django Views Are Adapters

end-to-end test of allocate API,A First End-to-End Test

modifying API to work with events,A Temporary Ugly Hack: The

Message Bus Has to Return Results

using repository directly in API endpoint,What Is the Trade-Off?

without Unit of Work pattern, talking directly to three layers,Unit

of Work Pattern

application services,Why Is Everything Called a Service?

architecture, summary diagram and table,Summary Diagram and

Table-Summary Diagram and Table

asynchronous messaging, temporal decoupling with,The Alternative:

Temporal Decoupling Using Asynchronous Messaging

atomic operations,Unit of Work Pattern

Unit of Work as abstraction over,Wrap-Up

using Unit of Work to group operations into atomic unit,

Examples: Using UoW to Group Multiple Operations into an

Atomic Unit-Example 2: Change Batch Quantity

B

Ball of Mud pattern,A Brief Interlude: On Coupling and Abstractions

distributed ball of mud and thinking in nouns,Distributed Ball of

Mud, and Thinking in Nouns-Distributed Ball of Mud, and

Thinking in Nouns

separating responsibilities,Separating Entangled Responsibilities

BatchCreated event,Refactoring Service Functions to Message

Handlers

services.add\_batch as handler for,Imagining an Architecture

Change: Everything Will Be an Event Handler

batches

allocating against all batches using domain service,Choosing an

Aggregate

asking Product to allocate against,Choosing an Aggregate

batch quantities changed means deallocate and reallocate,A New

Requirement Leads Us to a New Architecture

collection of,Choosing an Aggregate

BatchQuantityChanged event

implementing,Our New Event

invoking handler change\_batch\_quantity,Imagining an

Architecture Change: Everything Will Be an Event Handler

Bernhardt, Gary,Implementing Our Chosen Abstractions

bootstrapping,Dependency Injection (and Bootstrapping)

bootstrapping script, capabilities of,A Bootstrap Script

changing notifications dependency in bootstrap script,Define the

Abstract and Concrete Implementations

dependency injection and bootstrap recap,Wrap-Up

dependency injection with,Aren’t Explicit Dependencies Totally

Weird and Java-y?

initializing dependency injection in tests,Initializing DI in Our

Tests

using in entrypoints,Using Bootstrap in Our Entrypoints

using to build message bus that talks to real notification class,

Figure Out How to Integration Test the Real Thing

bounded contexts,Choosing an Aggregate

identifying aggregates and,Identifying Aggregates and Bounded

Contexts-An Event-Driven Approach to Go to Microservices via

Strangler Pattern

product concept and,Choosing an Aggregate

business logic

abstractions simplifying interface with messy I/O,Wrap-Up

separating from state in code,Implementing Our Chosen

Abstractions

business logic layer,What Is a Domain Model?

business rules

invariants, concurrency, and locks,Invariants, Concurrency, and

Locks

invariants, constraints, and consistency,Invariants, Constraints,

and Consistency

C

Celery tool,The Message Bus Maps Events to Handlers

change\_batch\_quantity

handler tests for,Test-Driving a New Handler

implementation, handler delegating to model layer,

Implementation

choreography,Single Responsibility Principle

classes, dependency injection using,An Alternative Using Classes

classical mapping,Inverting the Dependency: ORM Depends on

Model

closures

dependency injection using,Preparing Handlers: Manual DI with

Closures and Partials

difference from partial functions,Preparing Handlers: Manual DI

with Closures and Partials

cohesion, high, between coupled elements,A Brief Interlude: On

Coupling and Abstractions

collaborators,The Unit of Work Collaborates with the Repository

collections,What Is an Aggregate?

Command Handler pattern,Wrap-Up

command-query responsibility segregation (CQRS),Command-Query

Responsibility Segregation (CQRS)-Wrap-Up

building read-only views into our data,Hold On to Your Lunch,

Folks

changing read model implementation to use Redis,Changing Our

Read Model Implementation Is Easy

denormalized copy of your data optimized for read operations,

Time to Completely Jump the Shark

domain model not optimized for read operations,Your Domain

Model Is Not Optimized for Read Operations

domain models for writing,Domain Models Are for Writing

full-blown CQRS versus simpler options,Wrap-Up

Post/Redirect/Get pattern and CQS,Post/Redirect/Get and CQS

read side and write side,Most Users Aren’t Going to Buy Your

Furniture

reads,Most Users Aren’t Going to Buy Your Furniture

consistency of,Most Users Aren’t Going to Buy Your

Furniture

rebuilding view model from scratch,Updating a Read Model

Table Using an Event Handler

SELECT N+1 and other performance problems,SELECT N+1

and Other Performance Considerations

simple view using existing repository,“Obvious” Alternative 1:

Using the Existing Repository

testing views,Testing CQRS Views

trade-offs for view model options,Wrap-Up

updating read model table using event handler,Time to

Completely Jump the Shark

view that uses the ORM,“Obvious” Alternative 2: Using the

ORM

commands,Commands and Command Handler-Wrap-Up

command flow to reserve stock, confirm reservation, dispatch

goods, and make customer VIP,Distributed Ball of Mud, and

Thinking in Nouns

command flow when warehouse knows stock is damaged,

Distributed Ball of Mud, and Thinking in Nouns

command flow with error,Error Handling in Distributed Systems

command handler logic in message bus,Message Bus Is Given

Handlers at Runtime

events versus,Commands and Events-Commands and Events

events, commands, and error handling,Discussion: Events,

Commands, and Error Handling-Discussion: Events, Commands,

and Error Handling

recovering from errors synchronously,Recovering from

Errors Synchronously

exception handling,Differences in Exception Handling

handlers for,Differences in Exception Handling

in our system now,Commands and Events

program output as list of commands,Choosing the Right

Abstraction(s)

splitting commands and events, trade-offs,Wrap-Up

commits

commit method,The Real Unit of Work Uses SQLAlchemy

Sessions

explicit tests for,Explicit Tests for Commit/Rollback Behavior

explicit versus implicit,Explicit Versus Implicit Commits

component diagram at end of Part One,Part I Recap

composition over inheritance in TrackingRepository wrapper class,

Option 3: The UoW Publishes Events to the Message Bus

composition root,Dependency Injection (and Bootstrapping),Aren’t

Explicit Dependencies Totally Weird and Java-y?

concurrency,Invariants, Concurrency, and Locks

aggregates and concurrency issues,Wrap-Up

allowing for greatest degree of,What Is an Aggregate?

enforcing rules using database transactions,Enforcing

Concurrency Rules by Using Database Transaction Isolation

Levels

integration test for,Testing for Our Data Integrity Rules

not provided by message bus implementation,The Message Bus

Maps Events to Handlers

optimistic concurrency with version numbers,Optimistic

Concurrency with Version Numbers-Implementation Options for

Version Numbers

pessimistic concurrency example, SELECT FOR UPDATE,

Pessimistic Concurrency Control Example: SELECT FOR

UPDATE

reproducing behavior with time.sleep function,Testing for Our

Data Integrity Rules

connascence,Error Handling in Distributed Systems

consistency,Invariants, Constraints, and Consistency

attainment of read consistency,Most Users Aren’t Going to Buy

Your Furniture

eventually consistent reads,Most Users Aren’t Going to Buy Your

Furniture

consistency boundaries,Aggregates and Consistency Boundaries,What

Is an Aggregate?

aggregates acting as,Discussion: Events, Commands, and Error

Handling

microservices as,The Alternative: Temporal Decoupling Using

Asynchronous Messaging

recap,Wrap-Up

constraints,Invariants, Constraints, and Consistency

context manager,Unit of Work Pattern

starting Unit of Work as,The Unit of Work Collaborates with the

Repository

Unit of Work and,Unit of Work and Its Context Manager-Fake

Unit of Work for Testing

control flow, using exceptions for,The Model Raises Events

coupling,A Brief Interlude: On Coupling and Abstractions

avoiding inappropriate coupling,Error Handling in Distributed

Systems

disadvantages of,A Brief Interlude: On Coupling and

Abstractions

domain logic coupled with I/O,Abstracting State Aids Testability

failure cascade as temporal coupling,Error Handling in

Distributed Systems

in tests that use mocks,Why Not Just Patch It Out?

reducing by abstracting away details,A Brief Interlude: On

Coupling and Abstractions

separating what you want to do from how to do it,Choosing the

Right Abstraction(s)

temporal decoupling using asynchronous messaging,The

Alternative: Temporal Decoupling Using Asynchronous

Messaging

trade-off between design feedback and,On Deciding What Kind

of Tests to Write

CQRS (see command-query responsibility segregation)

CQS (command-query separation),Post/Redirect/Get and CQS

CRUD wrapper around a database,Part I Recap

CSV over SMTP architecture,Why Not Just Run Everything in a

Spreadsheet?

CSVs, doing everything with,Swapping Out the Infrastructure: Do

Everything with CSVs-Implementing a Repository and Unit of Work

for CSVs

D

data access, applying dependency inversion principle to,Applying the

DIP to Data Access

data integrity

issues arising from splitting operation across two UoWs,

Implementing Our New Requirement

testing for,Testing for Our Data Integrity Rules-Pessimistic

Concurrency Control Example: SELECT FOR UPDATE

data storage, Repository pattern and,Repository Pattern

databases

SQLAlchemy adding session for Unit of Work,The Real Unit of

Work Uses SQLAlchemy Sessions

testing allocations persisted to database,The Straightforward

Implementation

testing transactions against real database,Explicit Tests for

Commit/Rollback Behavior

Unit of Work pattern managing state for,Unit of Work Pattern

dataclasses

events,Events Are Simple Dataclasses

use for message types,Recovering from Errors Synchronously

use for value objects,Dataclasses Are Great for Value Objects

deallocate service, building (exerise),A Typical Service Function

dependencies

abstract dependencies of service layer,The DIP in Action

testing,The DIP in Action

circular dependencies between event handlers,Wrap-Up

depending on abstractions,A Typical Service Function

edge-to-edge testing with dependency injection,Testing Edge to

Edge with Fakes and Dependency Injection-Testing Edge to Edge

with Fakes and Dependency Injection

keeping all domain dependencies in fixture functions,Mitigation:

Keep All Domain Dependencies in Fixture Functions

none in domain model,Applying the DIP to Data Access

real service layer dependencies at runtime,The DIP in Action

service layer dependency on abstract UoW,Using the UoW in the

Service Layer

UoW no longer dependent on message bus,The Message Bus

Now Collects Events from the UoW

dependency chains,A Bootstrap Script

dependency injection,Dependency Injection (and Bootstrapping)-An

Alternative Using Classes

by inspecting function signatures,A Bootstrap Script

explicit dependencies are better than implicit dependencies,

Aren’t Explicit Dependencies Totally Weird and Java-y?

implicit versus explicit dependencies,Implicit Versus Explicit

Dependencies

manual creation of partial functions inline,A Bootstrap Script

manual DI with closures or partial functions,Preparing Handlers:

Manual DI with Closures and Partials

recap of DI and bootstrap,Wrap-Up

using classes,An Alternative Using Classes

using DI framework,A Bootstrap Script

dependency inversion principle,Applying the DIP to Data Access,

Wrap-Up

declaring explicit dependency as example of,Aren’t Explicit

Dependencies Totally Weird and Java-y?

ORM depends on the data model,Inverting the Dependency:

ORM Depends on Model

dictionaries

dictionary of hashes to paths,Implementing Our Chosen

Abstractions

for filesystem operations,Choosing the Right Abstraction(s)

HANDLERS dicts for commands and events,Differences in

Exception Handling

directory structure, putting project into folders,Putting Things in

Folders to See Where It All Belongs

Distributed Ball of Mud anti-pattern

and thinking in nouns,Distributed Ball of Mud, and Thinking in

Nouns-Distributed Ball of Mud, and Thinking in Nouns

avoiding,The Alternative: Temporal Decoupling Using

Asynchronous Messaging

Django,Repository and Unit of Work Patterns with Django-Steps

Along the Way

applying patterns to Django app,What to Do If You Already Have

Django

steps along the way,Steps Along the Way

installing,Repository and Unit of Work Patterns with Django

ORM example,The “Normal” ORM Way: Model Depends on

ORM

Repository pattern with,Repository Pattern with Django-Custom

Methods on Django ORM Classes to Translate to/from Our

Domain Model

Unit of Work pattern with,Unit of Work Pattern with Django-Unit

of Work Pattern with Django

using, difficulty of,Why Was This All So Hard?

views are adapters,API: Django Views Are Adapters

Docker dev environment with real fake email server,Figure Out How

to Integration Test the Real Thing

domain driven design (DDD),Domain Modeling,What Is a Domain

Model?

(see also domain model; domain modeling)

Aggregate pattern,What Is an Aggregate?

bounded contexts,Choosing an Aggregate

choosing the right aggregate, references on,Wrap-Up

domain, defined,What Is a Domain Model?

Repository pattern and,What Is the Trade-Off?

Domain Events pattern,Events and the Message Bus

domain exceptions,Exceptions Can Express Domain Concepts Too

domain language,Exploring the Domain Language

domain layer

fully decoupling service layer from,Fully Decoupling the

Service-Layer Tests from the Domain-Adding a Missing Service

tests moving to service layer,Should Domain Layer Tests Move

to the Service Layer?

reasons for,Should Domain Layer Tests Move to the

Service Layer?

domain model,Reminder: Our Model-Introducing the Repository

Pattern

deciding whether to write tests against,On Deciding What Kind

of Tests to Write

Django custom ORM methods for conversion,Custom Methods

on Django ORM Classes to Translate to/from Our Domain Model

email sending code in, avoiding,And Let’s Not Make a Mess of

Our Model Either

events from, passing to message bus in service layer,Option 1:

The Service Layer Takes Events from the Model and Puts Them

on the Message Bus

folder for,Putting Things in Folders to See Where It All Belongs

getting benefits of rich model,The DIP in Action

invariants, constraints, and consistency,Invariants, Constraints,

and Consistency

maintaining small core of tests written against,Wrap-Up

new method on, change\_batch\_quantity,A New Method on the

Domain Model

not optimized for read operations,Your Domain Model Is Not

Optimized for Read Operations

persisting,Persisting Our Domain Model

raising events,The Model Raises Events

raising events and service layer passing them to message bus,

Wrap-Up

trade-offs as a diagram,Wrap-Up

translating to relational database

normal ORM way, model depends on ORM,The “Normal”

ORM Way: Model Depends on ORM

ORM depends on the model,Inverting the Dependency:

ORM Depends on Model

using spreadsheets instead of,Why Not Just Run Everything in a

Spreadsheet?

writing data,Domain Models Are for Writing

writing tests against,High and Low Gear

domain modeling,Domain Modeling-Exceptions Can Express Domain

Concepts Too

domain language,Exploring the Domain Language

functions for domain services,Not Everything Has to Be an

Object: A Domain Service Function-Exceptions Can Express

Domain Concepts Too

unit testing domain models,Unit Testing Domain Models-Value

Objects and Entities

dataclasses for value objects,Dataclasses Are Great for

Value Objects

value objects and entities,Value Objects and Entities

domain services,Not Everything Has to Be an Object: A Domain

Service Function,Why Is Everything Called a Service?

function for,Not Everything Has to Be an Object: A Domain

Service Function

driven adapters,Putting Things in Folders to See Where It All Belongs

duck typing,The Repository in the Abstract

for ports,What Is a Port and What Is an Adapter, in Python?

E

E2E tests (see end-to-end tests)

eager loading,SELECT N+1 and Other Performance Considerations

edge-to-edge testing,Implementing Our Chosen Abstractions-Testing

Edge to Edge with Fakes and Dependency Injection

Effective Aggregate Design (Vernon),Wrap-Up

email alerts, sending when out of stock,Avoiding Making a Mess-Or

the Service Layer!

end-to-end tests

aiming for one test per feature,Wrap-Up

decoupling of service layer from domain, carrying through to,

Carrying the Improvement Through to the E2E Tests

of allocate API,A First End-to-End Test

replacement with unit tests,Why Not Just Patch It Out?

enter and exit magic methods,Unit of Work and Its Context

Manager,The Real Unit of Work Uses SQLAlchemy Sessions

entities

defined,Value Objects and Entities

identity equality,Value Objects and Entities

value objects versus,Exceptions Can Express Domain Concepts

Too

entrypoints,Putting Things in Folders to See Where It All Belongs

\_\_eq\_\_magic method,Value Objects and Entities

equality operators, implementing on entities,Value Objects and

Entities

error handling

counting as a feature,Wrap-Up

events, commands, and,Discussion: Events, Commands, and

Error Handling-Discussion: Events, Commands, and Error

Handling

in distributed systems,Error Handling in Distributed Systems-

The Alternative: Temporal Decoupling Using Asynchronous

Messaging

errors, recovering from synchronously,Recovering from Errors

Synchronously

Evans, Eric,What Is an Aggregate?

event handlers

imagined architecture in which everything is an event handler,

Imagining an Architecture Change: Everything Will Be an Event

Handler

in message bus,Message Bus Is Given Handlers at Runtime

managing updates to read model,Changing Our Read Model

Implementation Is Easy

updating read model table using,Time to Completely Jump the

Shark

event storming,A New Requirement Leads Us to a New Architecture

event-driven architecture

going to microservices via Strangler pattern,An Event-Driven

Approach to Go to Microservices via Strangler Pattern-An

Event-Driven Approach to Go to Microservices via Strangler

Pattern

using events to integrate microservices,Event-Driven

Architecture: Using Events to Integrate Microservices-Wrap-Up

events

changing schema over time,Footguns

commands versus,Commands and Events-Differences in

Exception Handling

events, commands, and error handling,Discussion: Events,

Commands, and Error Handling-Discussion: Events, Commands,

and Error Handling

internal versus external,Internal Versus External Events

splitting command and events, trade-offs,Wrap-Up

events and the message bus,Events and the Message Bus-Wrap-Up

domain events and message bus recap,Wrap-Up

domain model raising events,The Model Raises Events

events as simple dataclasses,Events Are Simple Dataclasses

events flowing through the system,Events and the Message Bus

message bus mapping events to handlers,The Message Bus Maps

Events to Handlers

pros and cons or trade-offs,Wrap-Up

recording events,The Model Records Events

sending email alerts when out of stock,Avoiding Making a Mess-

Or the Service Layer!

avoiding messing up domain model,And Let’s Not Make a

Mess of Our Model Either

avoiding messing up web controllers,First, Let’s Avoid

Making a Mess of Our Web Controllers

out of place in the service layer,Or the Service Layer!

violating the single responsibility principle,Single

Responsibility Principle

service layer raising its own events,Option 2: The Service Layer

Raises Its Own Events

service layer with explicit message bus,Option 1: The Service

Layer Takes Events from the Model and Puts Them on the

Message Bus

transforming our app into message processor,Going to Town on

the Message Bus-Why Have We Achieved?

imagined architecture, everything will be an event handler,

Imagining an Architecture Change: Everything Will Be an

Event Handler

implementing the new requirement,Implementing Our New

Requirement-Test-Driving a New Handler

modifying API to work with events,A Temporary Ugly

Hack: The Message Bus Has to Return Results

new requirement and new architecture,A New Requirement

Leads Us to a New Architecture

refactoring service functions to message handlers,

Refactoring Service Functions to Message Handlers

temporary hack, message bus returning results,A Temporary

Ugly Hack: The Message Bus Has to Return Results

test driving new handler,Test-Driving a New Handler

tests writtern to in terms of events,Our Tests Are All

Written in Terms of Events Too

unit testing event handlers with fake message bus,

Optionally: Unit Testing Event Handlers in Isolation with a

Fake Message Bus

whole app as message bus, trade-offs,Why Have We

Achieved?

UoW publishes events to message bus,Option 3: The UoW

Publishes Events to the Message Bus

eventually consistent reads,Most Users Aren’t Going to Buy Your

Furniture

exception handling, differences for events and commands,Differences

in Exception Handling

exceptions

expressing domain concepts,Exceptions Can Express Domain

Concepts Too

using for control flow,The Model Raises Events

external events,The Message Bus Maps Events to Handlers,Event-

Driven Architecture: Using Events to Integrate Microservices-Wrap-

Up

extreme programming (XP), exhortation to listen to the code,On

Deciding What Kind of Tests to Write

F

faking

FakeNotifications for unit testing,Make a Fake Version for Your

Tests

FakeRepository,Introducing a Service Layer, and Using

FakeRepository to Unit Test It

adding fixture function on,Mitigation: Keep All Domain

Dependencies in Fixture Functions

new query type on,Implementation

using to unit test the service layer,Introducing a Service

Layer, and Using FakeRepository to Unit Test It

fakes versus mocks,Why Not Just Patch It Out?

FakeSession, using to unit test the service layer,Introducing a

Service Layer, and Using FakeRepository to Unit Test It

FakeUnitOfWork for service layer testing,Fake Unit of Work for

Testing

faking I/O in edge-to-edge test,Testing Edge to Edge with Fakes

and Dependency Injection

tweaking fakes in service layer to call super and implement

underscorey methods,Option 3: The UoW Publishes Events to the

Message Bus

filesystems

writing code to synchronize source and target directories,

Abstracting State Aids Testability-Abstracting State Aids

Testability

choosing right abstraction,Choosing the Right

Abstraction(s)-Implementing Our Chosen Abstractions

implementing chosen abstraction,Implementing Our Chosen

Abstractions-Wrap-Up

fixture functions, keeping all domain dependencies in,Mitigation:

Keep All Domain Dependencies in Fixture Functions

Flask framework,Some Pseudocode: What Are We Going to Need?

API endpoint,What Is the Trade-Off?

calling bootstrap in entrypoints,Using Bootstrap in Our

Entrypoints

endpoint for viewing allocations,Post/Redirect/Get and CQS

Flask API and service layer,Our First Use Case: Flask API and

Service Layer-The DIP in Action

app delegating to service layer,A Typical Service Function

connecting the app to real world,Connecting Our

Application to the Real World

different types of services,Why Is Everything Called a

Service?

end-to-end tests for happy and unhappy paths,A Typical

Service Function

error conditions requiring database checks,Error Conditions

That Require Database Checks

first API end-to-end test,A First End-to-End Test-A First

End-to-End Test

first cut of the app,The Straightforward Implementation-The

Straightforward Implementation

introducing service layer and fake repo to unit test it,

Introducing a Service Layer, and Using FakeRepository to

Unit Test It-A Typical Service Function

putting project into folders,Putting Things in Folders to See

Where It All Belongs

service layer benefits,Wrap-Up

service layer dependencies,The DIP in Action

service layer pros and cons,The DIP in Action

typical service layer function,A Typical Service Function

putting API endpoint in front of allocate domain service,

Connecting Our Application to the Real World

Fowler, Martin,Why Not Just Patch It Out?,Wrap-Up

Freeman, Steve,Why Not Just Patch It Out?

Functional Core, Imperative Shell (FCIS),Implementing Our Chosen

Abstractions

functions,Exceptions Can Express Domain Concepts Too

for domain services,Not Everything Has to Be an Object: A

Domain Service Function

service layer,A Typical Service Function

G

"Global Complexity, Local Simplicity" post,Wrap-Up

gt magic method,Python’s Magic Methods Let Us Use Our

Models with Idiomatic Python

H

handlers

event and command handlers in message bus,Message Bus Is

Given Handlers at Runtime

new HANDLERS dicts for commands and events,Differences in

Exception Handling

hash magic method,Value Objects and Entities

hashing a file,Abstracting State Aids Testability

dictionary of hashes to paths,Choosing the Right Abstraction(s)

hoisting I/O,Why Not Just Patch It Out?

I

I/O

disentangling details from program logic,Implementing Our

Chosen Abstractions

domain logic tightly coupled to,Abstracting State Aids

Testability

simplifying interface with business logic using abstractions,

Wrap-Up

idempotent message handling,Footguns

identity equality (entities),Value Objects and Entities

implicit versus explicit commits,Explicit Versus Implicit Commits

importing dependenies,Aren’t Explicit Dependencies Totally Weird

and Java-y?

inheritance, avoiding use of with wrapper class,Option 3: The UoW

Publishes Events to the Message Bus

integration tests

for concurrency behavior,Testing for Our Data Integrity Rules

test-driving Unit of Work with,Test-Driving a UoW with

Integration Tests

interfaces, Python and,What Is a Port and What Is an Adapter, in

Python?

invariants

invariants, concurrency, and locks,Invariants, Concurrency, and

Locks

invariants, constraints, and consistency,Invariants, Constraints,

and Consistency

protecting while allowing concurrency,What Is an Aggregate?

inward-facing adapters,Putting Things in Folders to See Where It All

Belongs

isolation levels (transaction),Enforcing Concurrency Rules by Using

Database Transaction Isolation Levels

J

Jung, Ed,Why Not Just Patch It Out?

K

katas,A Brief Interlude: On Coupling and Abstractions

L

layered architecture,Applying the DIP to Data Access

case study, layering an overgrown system,Separating Entangled

Responsibilities

locks on database tables,Invariants, Concurrency, and Locks

optimistic locking,Optimistic Concurrency with Version

Numbers,Optimistic Concurrency with Version Numbers

pessimistic locking,Optimistic Concurrency with Version

Numbers

London-school versus classic-style TDD,Why Not Just Patch It Out?

M

magic methods

allowing use of domain model with idiomatic Python,Python’s

Magic Methods Let Us Use Our Models with Idiomatic Python

enter and exit,Unit of Work and Its Context Manager

eq,Value Objects and Entities

hash,Value Objects and Entities

MagicMock objects,Why Not Just Patch It Out?

mappers,Inverting the Dependency: ORM Depends on Model

message brokers,Using a Redis Pub/Sub Channel for Integration

message bus

abstract message bus and its real and fake versions,Optionally:

Unit Testing Event Handlers in Isolation with a Fake Message

Bus

before, message buse as optional add-on,Going to Town on the

Message Bus

Celery and,The Message Bus Maps Events to Handlers

class given handlers at runtime,Message Bus Is Given Handlers

at Runtime

dispatching events and commands differently,Differences in

Exception Handling

event and command handler logic staying the same,Message Bus

Is Given Handlers at Runtime

getting custom with overridden bootstrap defaults,Initializing DI

in Our Tests

handler publishing outgoing event,Our New Outgoing Event

handle\_event method,Recovering from Errors Synchronously

handle\_event with retries,Recovering from Errors Synchronously

mapping events to handlers,The Message Bus Maps Events to

Handlers

now collecting events from UoW,The Message Bus Now

Collects Events from the UoW

now the main entrypoint to service layer,Going to Town on the

Message Bus

pros and cons or trade-offs,Wrap-Up

recap,Wrap-Up

Redis pub/sub listener as thin adapter around,Redis Is Another

Thin Adapter Around Our Message Bus

returning results in temporary hack,A Temporary Ugly Hack: The

Message Bus Has to Return Results

service layer raising events and calling messagebus.handle,

Option 2: The Service Layer Raises Its Own Events

service layer with explicit message bus,Option 1: The Service

Layer Takes Events from the Model and Puts Them on the

Message Bus

Unit of Work publishing events to,Option 3: The UoW Publishes

Events to the Message Bus

unit testing event handlers with fake message bus,Optionally:

Unit Testing Event Handlers in Isolation with a Fake Message

Bus

whole app as, trade-offs,Why Have We Achieved?

wiring up new event handlers to,A New Method on the Domain

Model

Message Bus pattern,Events and the Message Bus

messaging

asynchronous, temporal decoupling with,The Alternative:

Temporal Decoupling Using Asynchronous Messaging

idempotent message handling,Footguns

reliable messaging is hard,Footguns

using Redis pub/sub channel for microservices integration,Using

a Redis Pub/Sub Channel for Integration

microservices

bounded contexts and,Choosing an Aggregate

event-based integration,Event-Driven Architecture: Using Events

to Integrate Microservices-Wrap-Up

distributed Ball of Mud and thinking in nouns,Distributed

Ball of Mud, and Thinking in Nouns-Distributed Ball of

Mud, and Thinking in Nouns

error handling in distributed systems,Error Handling in

Distributed Systems-The Alternative: Temporal Decoupling

Using Asynchronous Messaging

temporal decoupling using asynchronous messaging,The

Alternative: Temporal Decoupling Using Asynchronous

Messaging

testing with end-to-end test,Test-Driving It All Using an

End-to-End Test-Internal Versus External Events

trade-offs,Wrap-Up

using Redis pub/sub channel for ntegration,Using a Redis

Pub/Sub Channel for Integration

event-driven approach, using Strangler pattern,An Event-Driven

Approach to Go to Microservices via Strangler Pattern-An

Event-Driven Approach to Go to Microservices via Strangler

Pattern

minimum viable product,Persisting Our Domain Model

mock.patch method,Why Not Just Patch It Out?,Aren’t Explicit

Dependencies Totally Weird and Java-y?

mocking

avoiding use of mock.patch,Why Not Just Patch It Out?

don't mock what you don't own,Fake Unit of Work for Testing

mocks versus fakes,Why Not Just Patch It Out?

overmocked tests, pitfalls of,Why Not Just Patch It Out?

"Mocks Aren't Stubs" (Fowler),Why Not Just Patch It Out?

model (domain),What Is a Domain Model?

N

named tuples,Dataclasses Are Great for Value Objects

(see also dataclasses)

nouns, splitting system into,Distributed Ball of Mud, and Thinking in

Nouns-Distributed Ball of Mud, and Thinking in Nouns

O

object neighborhoods,The Unit of Work Collaborates with the

Repository

object-oriented composition,Why Not Just Patch It Out?

object-oriented design principles,Exceptions Can Express Domain

Concepts Too

object-relational mappers (ORMs),The “Normal” ORM Way: Model

Depends on ORM

associating right batches with Product objects,One Aggregate =

One Repository

Django ORM example,The “Normal” ORM Way: Model

Depends on ORM

Django, custom methods to translate to/from domain model,

Custom Methods on Django ORM Classes to Translate to/from

Our Domain Model

ORM depends on the data model,Inverting the Dependency:

ORM Depends on Model

testing the ORM,Inverting the Dependency: ORM Depends

on Model

orm.start\_mappers function,A Bootstrap Script

Repository pattern and,What Is the Trade-Off?

SELECT N+1 performance problem,SELECT N+1 and Other

Performance Considerations

simple view using the ORM,“Obvious” Alternative 2: Using the

ORM

SQLAlchemy, model depends on ORM,The “Normal” ORM

Way: Model Depends on ORM

onion architecture,Applying the DIP to Data Access

optimistic concurrency with version numbers,Optimistic Concurrency

with Version Numbers-Implementation Options for Version Numbers

orchestration,Introducing a Service Layer, and Using FakeRepository

to Unit Test It

changing to choreography,Single Responsibility Principle

using application service,Why Is Everything Called a Service?

orchestration layer (see service layer)

Outbox pattern,Footguns

P

partial functions

dependency injection with,Preparing Handlers: Manual DI with

Closures and Partials

difference from closures,Preparing Handlers: Manual DI with

Closures and Partials

manually creating inline,A Bootstrap Script

patterns, deciding whether you need to use them,Part I Recap

PEP 544 protocols,The Repository in the Abstract

performance

consistency boundaries and,Aggregates and Consistency

Boundaries,Wrap-Up

impact of using aggregates,Choosing an Aggregate,What About

Performance?

persistence ignorance,The “Normal” ORM Way: Model Depends on

ORM

trade-offs,Wrap-Up

pessimistic concurrency,Optimistic Concurrency with Version

Numbers

example, SELECT FOR UPDATE,Pessimistic Concurrency

Control Example: SELECT FOR UPDATE

ports

defined,What Is a Port and What Is an Adapter, in Python?

ports-and-adapters inspired patterns,Part I Recap

putting in folder with adapters,Putting Things in Folders to See

Where It All Belongs

Post/Redirect/Get pattern,Post/Redirect/Get and CQS

command-query separation (CQS),Post/Redirect/Get and CQS

PostgreSQL

Anti-Patterns: Read-Modify-Write Cycles,Pessimistic

Concurrency Control Example: SELECT FOR UPDATE

documentation for transaction isolation levels,Enforcing

Concurrency Rules by Using Database Transaction Isolation

Levels

managing concurrency issues,Optimistic Concurrency with

Version Numbers

SERIALIZABLE transaction isolation level,Optimistic

Concurrency with Version Numbers

preparatory refactoring workflow,Imagining an Architecture Change:

Everything Will Be an Event Handler

primitives

moving from domain objects to, in service layer,Refactoring

Service Functions to Message Handlers

primitive obsession,Refactoring Service Functions to Message

Handlers

Product object,Aggregates and Consistency Boundaries

acting as consistency boundary,Discussion: Events, Commands,

and Error Handling

asking Product to allocate against its batches,Choosing an

Aggregate

code for,Choosing an Aggregate

service layer using,One Aggregate = One Repository

two transactions attempting concurrent update on,Optimistic

Concurrency with Version Numbers

version numbers implemented on,Implementation Options for

Version Numbers

ProductRepository object,One Aggregate = One Repository

projects

organizing into folders,Putting Things in Folders to See Where It

All Belongs

template project structure,A Template Project Structure-Wrap-

Up

protocols, abstract base classes, duck typing, and,The Repository in

the Abstract

publish-subscribe system

message bus as

handlers subscribed to receive events,The Message Bus

Maps Events to Handlers

publishing step,Option 1: The Service Layer Takes Events

from the Model and Puts Them on the Message Bus

using Redis pub/sub channel for microservices integration,Using

a Redis Pub/Sub Channel for Integration

PyCon talk on Mocking Pitfalls,Why Not Just Patch It Out?

pytest

@pytest.skip,What About Performance?

fixtures,Abstracting State Aids Testability

pytest-django plug-in,Repository Pattern with Django,Why Was

This All So Hard?

session argument,Inverting the Dependency: ORM Depends on

Model

Q

queries,Command-Query Responsibility Segregation (CQRS)

(see also command-query responsibility segregation)

questions from tech reviewers,Questions Our Tech Reviewers Asked

That We Couldn’t Work into Prose-Footguns

R

read-modify-write failure mode,Pessimistic Concurrency Control

Example: SELECT FOR UPDATE

reallocate service function,Example 1: Reallocate

reallocation

sequence diagram for flow,Implementing Our New Requirement

testing in isolation using fake message bus,Optionally: Unit

Testing Event Handlers in Isolation with a Fake Message Bus

Redis pub/sub channel, using for microservices integration,Using a

Redis Pub/Sub Channel for Integration

testing pub/sub model,Test-Driving It All Using an End-to-End

Test

publishing outgoing event,Our New Outgoing Event

Redis as thin adapter around message bus,Redis Is Another

Thin Adapter Around Our Message Bus

Redis, changing read model implementation to use,Changing Our Read

Model Implementation Is Easy

repositories

adding list method to existing repository object,Hold On to Your

Lunch, Folks

CSV-based repository,Implementing a Repository and Unit of

Work for CSVs

new query type on our repository,Implementation

one aggregrate = one repository,One Aggregate = One

Repository

repository keeping track of aggregates passing through it,Option

3: The UoW Publishes Events to the Message Bus

service layer function depending on abstract repository,A

Typical Service Function

simple view using existing repository,“Obvious” Alternative 1:

Using the Existing Repository

TrackerRepository wrapper class,Option 3: The UoW Publishes

Events to the Message Bus

Unit of Work collaborating with,The Unit of Work Collaborates

with the Repository

Repository pattern,Repository Pattern,Introducing the Repository

Pattern-Wrap-Up

and persistence ignorance, trade-offs,Wrap-Up

building fake repository for tests,Building a Fake Repository for

Tests Is Now Trivial!

ORMs and,What Is the Trade-Off?

recap of important points,Wrap-Up

simplest possible repository,The Repository in the Abstract

testing the repository with retrieving a complex object,What Is

the Trade-Off?

testing the repository with saving an object,What Is the Trade-

Off?

trade-offs,What Is the Trade-Off?

typical repository,What Is the Trade-Off?

using repository directly in API endpoint,What Is the Trade-Off?

with Django,Repository Pattern with Django-Custom Methods on

Django ORM Classes to Translate to/from Our Domain Model

resources, additional required reading,More Required Reading

responsibilities of code,Choosing the Right Abstraction(s)

separating responsibilities,Separating Entangled Responsibilities

case study, layering overgrown system,Separating Entangled

Responsibilities

retries

message bus handle\_event with,Recovering from Errors

Synchronously

optimistic concurrency control and,Optimistic Concurrency with

Version Numbers

Tenacity library for,Recovering from Errors Synchronously

Rhodes, Brandon,Why Not Just Patch It Out?

rollbacks,Unit of Work and Its Context Manager

explicit tests for,Explicit Tests for Commit/Rollback Behavior

rollback method,The Real Unit of Work Uses SQLAlchemy

Sessions

S

seams,Wrap-Up

secondary adapters,Putting Things in Folders to See Where It All

Belongs

Seemann, Mark, blog post,Applying the DIP to Data Access

SELECT \* FROM WHERE queries,Time to Completely Jump the

Shark

SELECT FOR UPDATE statement,Optimistic Concurrency with

Version Numbers

pessimistic concurrency control example with,Pessimistic

Concurrency Control Example: SELECT FOR UPDATE

SELECT N+1,SELECT N+1 and Other Performance Considerations

service functions

making them event handlers,Imagining an Architecture Change:

Everything Will Be an Event Handler

refactoring to message handlers,Refactoring Service Functions to

Message Handlers

service layer,Our First Use Case: Flask API and Service Layer-The

DIP in Action

benefits of,Wrap-Up

benefits to test-driven development,Wrap-Up

connecting our application to real world,Connecting Our

Application to the Real World

dependencies of,The DIP in Action

real dependencies at runtime,The DIP in Action

testing,The DIP in Action

difference between domain service and,Why Is Everything

Called a Service?

domain layer tests moving to,Should Domain Layer Tests Move

to the Service Layer?

reasons for,Should Domain Layer Tests Move to the

Service Layer?

end-to-end test of allocate API, testing happy and unhappy paths,

A Typical Service Function

error conditions requiring database checks in Flask app,Error

Conditions That Require Database Checks

first cut of Flask app,The Straightforward Implementation-The

Straightforward Implementation

Flask app delegating to,A Typical Service Function

from domain objects to primitives to events as interface,

Refactoring Service Functions to Message Handlers

fully decoupling from the domain,Fully Decoupling the Service-

Layer Tests from the Domain-Adding a Missing Service

introducing and using FakeRepository to unit test it,Introducing a

Service Layer, and Using FakeRepository to Unit Test It-Why Is

Everything Called a Service?

message bus as main entrypoint,Going to Town on the Message

Bus

pros and cons or trade-offs,The DIP in Action

putting project in folders,Putting Things in Folders to See Where

It All Belongs

raising events and passing them to message bus,Wrap-Up

raising its own events,Option 2: The Service Layer Raises Its

Own Events

sending email alerts when out of stock, avoiding,Or the Service

Layer!

taking events from model and putting them on message bus,

Option 1: The Service Layer Takes Events from the Model and

Puts Them on the Message Bus

totally free of event handling concerns,Option 3: The UoW

Publishes Events to the Message Bus

tweaking fakes in to call super and implement underscorey

methods,Option 3: The UoW Publishes Events to the Message

Bus

typical service function,A Typical Service Function

using Product objects,One Aggregate = One Repository

using Unit of Work in,Using the UoW in the Service Layer

using, test pyramid and,How Is Our Test Pyramid Looking?

writing bulk of tests against,Wrap-Up

writing tests against,High and Low Gear

service-layer services vs. domain services,Not Everything Has to Be

an Object: A Domain Service Function

services

application service and domain service,Why Is Everything

Called a Service?

service layer tests only using services,Adding a Missing Service

Session object,Wrap-Up

set, fake repository as wrapper around,Building a Fake Repository for

Tests Is Now Trivial!

simplifying abstractions,Choosing the Right Abstraction(s)

single responsibility principle (SRP),Single Responsibility Principle

Singleton pattern, messagebus.py implementing,Optionally: Unit

Testing Event Handlers in Isolation with a Fake Message Bus

situated software,A New Requirement Leads Us to a New

Architecture

Software Engineering Stack Exchange site,Why Not Just Patch It Out?

spreadsheets, using instead of domain model,Why Not Just Run

Everything in a Spreadsheet?

spy objects,Testing Edge to Edge with Fakes and Dependency

Injection

SQL

generating for domain model objects,The “Normal” ORM Way:

Model Depends on ORM

helpers for Unit of Work,Test-Driving a UoW with Integration

Tests

ORM and Repository pattern as abstractions in front of,What Is

the Trade-Off?

raw SQL in views,Hold On to Your Lunch, Folks

repository test for retrieving complex object,What Is the Trade-

Off?

repository test for saving an object,What Is the Trade-Off?

SQLAlchemy

database session for Unit of Work,The Real Unit of Work Uses

SQLAlchemy Sessions

not mocking,Fake Unit of Work for Testing

declarative syntax, model depends on ORM,The “Normal” ORM

Way: Model Depends on ORM

explicit ORM mapping with SQLAlchemy Table objects,

Inverting the Dependency: ORM Depends on Model

SELECT N+1 problem and,SELECT N+1 and Other

Performance Considerations

Session object,Wrap-Up

using directly in API endpoint,Inverting the Dependency: ORM

Depends on Model

using DSL to specify FOR UPDATE,Pessimistic Concurrency

Control Example: SELECT FOR UPDATE

stakeholders, convincing to try something new,Convincing Your

Stakeholders to Try Something New-Questions Our Tech Reviewers

Asked That We Couldn’t Work into Prose

state

abstracting to aid testability,Abstracting State Aids Testability-

Abstracting State Aids Testability

splitting off from logic in the program,Implementing Our Chosen

Abstractions

storage,Repository Pattern

(see also repositories; Repository pattern)

permanent, UoW providing entrypoint to,The Unit of Work

Collaborates with the Repository

Strangler pattern, going to microservices via,An Event-Driven

Approach to Go to Microservices via Strangler Pattern-An Event-

Driven Approach to Go to Microservices via Strangler Pattern

stubbing, mocks and stubs,Why Not Just Patch It Out?

super function,Option 3: The UoW Publishes Events to the Message

Bus

tweaking fakes in service layer to call,Option 3: The UoW

Publishes Events to the Message Bus

synchronous execution of event-handling code,Wrap-Up

T

temporal coupling,Error Handling in Distributed Systems

temporal decoupling using asynchronous messaging,The Alternative:

Temporal Decoupling Using Asynchronous Messaging

Tenacity library,Recovering from Errors Synchronously

test doubles

mocks versus fakes,Why Not Just Patch It Out?

mocks versus stubs,Why Not Just Patch It Out?

using lists to build,Testing Edge to Edge with Fakes and

Dependency Injection

"Test-Driven Development: That's Not What We Meant",Why Not Just

Patch It Out?

test-driven development (TDD),TDD in High Gear and Low Gear-

Wrap-Up

benefits of service layer to,Wrap-Up

classic versus London-school,Why Not Just Patch It Out?

deciding what kinds of tests to write,On Deciding What Kind of

Tests to Write

domain layer tests moving to service layer,Should Domain Layer

Tests Move to the Service Layer?

fully decoupling service layer from the domain,Fully Decoupling

the Service-Layer Tests from the Domain-Adding a Missing

Service

adding missing service,Adding a Missing Service

carrying improvement through to E2E tests,Carrying the

Improvement Through to the E2E Tests

keeping all domain dependencies in fixture functions,

Mitigation: Keep All Domain Dependencies in Fixture

Functions

high and low gear,High and Low Gear

test pyramid with service layer added,How Is Our Test Pyramid

Looking?

test pyramid, examining,TDD in High Gear and Low Gear

types of tests, rules of thumb for,Wrap-Up

unit tests operating at lower level, acting directly on model,TDD

in High Gear and Low Gear

testing

abstracting state to aid testability,Abstracting State Aids

Testability-Abstracting State Aids Testability

after implementing chosen abstraction,Implementing Our Chosen

Abstractions-Wrap-Up

avoiding use of mock.patch,Why Not Just Patch It Out?-

Wrap-Up

edge-to-edge testing with fakes and dependency injection,

Testing Edge to Edge with Fakes and Dependency Injection-

Testing Edge to Edge with Fakes and Dependency Injection

end-to-end test of pub/sub model,Test-Driving It All Using an

End-to-End Test

fake database session at service layer,Introducing a Service

Layer, and Using FakeRepository to Unit Test It

fake UoW for service layer testing,Fake Unit of Work for Testing

for data integrity rules,Testing for Our Data Integrity Rules-

Pessimistic Concurrency Control Example: SELECT FOR

UPDATE

integration test for CQRS view,Testing CQRS Views

integration test for overriding bootstrap defaults,Initializing DI in

Our Tests

integration tests for rollback behavior,Explicit Tests for

Commit/Rollback Behavior

tests folder tree,Tests

tests written in terms of events,Our Tests Are All Written in

Terms of Events Too

handler tests for change\_batch\_quantity,Test-Driving a New

Handler

unit testing event handlers with fake message bus,

Optionally: Unit Testing Event Handlers in Isolation with a

Fake Message Bus

Unit of Work with integration tests,Test-Driving a UoW with

Integration Tests

tidying up tests,Tidying Up the Integration Tests

unit test for bootstrap,Initializing DI in Our Tests

unit testing with fakes at service layer,Introducing a Service

Layer, and Using FakeRepository to Unit Test It

time.sleep function,Testing for Our Data Integrity Rules

reproducing concurrency behavior with,Testing for Our Data

Integrity Rules

transactions

concurrent, attempting update on Product,Optimistic Concurrency

with Version Numbers

simulating a slow transaction,Testing for Our Data Integrity

Rules

Unit of Work and,Wrap-Up

using to enforce concurrency rules,Enforcing Concurrency Rules

by Using Database Transaction Isolation Levels

type hints,Unit Testing Domain Models,Unit Testing Domain Models

U

underscorey methods

avoiding by implementing TrackingRepository wrapper class,

Option 3: The UoW Publishes Events to the Message Bus

tweaking fakes in service layer to implement,Option 3: The UoW

Publishes Events to the Message Bus

Unit of Work pattern,The Repository in the Abstract,Unit of Work

Pattern-Wrap-Up

and its context manager,Unit of Work and Its Context Manager

fake UoW for testing,Fake Unit of Work for Testing

real UoW using SQLAlchemy session,The Real Unit of

Work Uses SQLAlchemy Sessions

benefits of using,Wrap-Up

collaboration with repository,The Unit of Work Collaborates

with the Repository

explicit tests for commit/rollback behavior,Explicit Tests for

Commit/Rollback Behavior

explicit versus implicit commits,Explicit Versus Implicit

Commits

fake message bus implemented in UoW,Optionally: Unit Testing

Event Handlers in Isolation with a Fake Message Bus

getting rid of underscorey methods in UoW class,Option 3: The

UoW Publishes Events to the Message Bus

managing database state,Unit of Work Pattern

message bus now collecting events from UoW,The Message Bus

Now Collects Events from the UoW

modifying to connect domain events and message bus,Events and

the Message Bus

pros and cons or trade-offs,Wrap-Up

recap of important points,Wrap-Up

splitting operations across two UoWs,Implementing Our New

Requirement

test driving with integration tests,Test-Driving a UoW with

Integration Tests

tidying up integration tests,Tidying Up the Integration Tests

UoW and product repository,One Aggregate = One Repository

UoW collecting events from aggregates and passing them to

message bus,Wrap-Up

UoW for CSVs,Implementing a Repository and Unit of Work for

CSVs

UoW managing success or failure of aggregate update,

Discussion: Events, Commands, and Error Handling

UoW publishing events to message bus,Option 3: The UoW

Publishes Events to the Message Bus

using UoW in service layer,Using the UoW in the Service Layer

using UoW to group multiple operations into atomic unit,

Examples: Using UoW to Group Multiple Operations into an

Atomic Unit-Example 2: Change Batch Quantity

changing batch quantity example,Example 2: Change Batch

Quantity

reallocate function example,Example 1: Reallocate

with Django,Unit of Work Pattern with Django-Unit of Work

Pattern with Django

without, API talking directly to three layers,Unit of Work Pattern

unit testing,Introducing a Service Layer, and Using FakeRepository to

Unit Test It

(see also test-driven development; testing)

of domain models,Unit Testing Domain Models-Value Objects

and Entities

unit tests replacing end-to-end tests,Why Not Just Patch It Out?

unittest.mock function,Why Not Just Patch It Out?

UoW (see Unit of Work pattern)

use-case layer (see service layer)

V

validation,Validation-Validating Pragmatics

value objects

defined,Dataclasses Are Great for Value Objects

and entities,Value Objects and Entities

entities versus,Exceptions Can Express Domain Concepts Too

math with,Dataclasses Are Great for Value Objects

using dataclasses for,Dataclasses Are Great for Value Objects

Vens, Rob,Wrap-Up

Vernon, Vaughn,Wrap-Up

version numbers

implementation options for,Implementation Options for Version

Numbers

in the products table, implementing optimistic locking,Optimistic

Concurrency with Version Numbers

views

Django views as adapters,API: Django Views Are Adapters

keeping totally separate, denormalized datastore for view model,

Time to Completely Jump the Shark

read-only,Post/Redirect/Get and CQS

rebuilding view model from scratch,Updating a Read Model

Table Using an Event Handler

simple view that uses the ORM,“Obvious” Alternative 2: Using

the ORM

simple view that uses the repository,“Obvious” Alternative 1:

Using the Existing Repository

testing CQRS views,Testing CQRS Views

trade-offs for view model options,Wrap-Up

updating read model table using event handler,Time to

Completely Jump the Shark

W

web controllers, sending email alerts via, avoiding,Avoiding Making

a Mess

About the Authors

Harry Percival spent a few years being deeply unhappy as a

management consultant. Soon he rediscovered his true geek nature and

was lucky enough to fall in with a bunch of XP fanatics, working on

pioneering the sadly defunct Resolver One spreadsheet. He worked at

PythonAnywhere LLP, spreading the gospel of TDD worldwide at

talks, workshops, and conferences. He is now with MADE.com.

Bob Gregory is a UK-based software architect with MADE.com. He

has been building event-driven systems with domain-driven design for

more than a decade.

Colophon

The animal on the cover of Architecture Patterns with Python is a

Burmese python ( Python bivitattus ). As you might expect, the Burmese

python is native to Southeast Asia. Today it lives in jungles and

marshes in South Asia, Myanmar, China, and Indonesia; it’s also

invasive in Florida’s Everglades.

Burmese pythons are one of the world’s largest species of snakes.

These nocturnal, carnivorous constrictors can grow to 23 feet and 200

pounds. Females are larger than males. They can lay up to a hundred

eggs in one clutch. In the wild, Burmese pythons live an average of 20

to 25 years.

The markings on a Burmese python begin with an arrow-shaped spot of

light brown on top of the head and continue along the body in

rectangles that stand out against its otherwise tan scales. Before they

reach their full size, which takes two to three years, Burmese pythons

live in trees hunting small mammals and birds. They also swim for

long stretches of time—going up to 30 minutes without air.

Because of habitat destruction, the Burmese python has a conservation

status of Vulnerable. Many of the animals on O’Reilly’s covers are

endangered; all of them are important to the world.

The color illustration is by Jose Marzan, based on a black-and-white

engraving from Encyclopedie D’Histoire Naturelle. The cover fonts

are URW Typewriter and Guardian Sans. The text font is Adobe

Minion Pro; the heading font is Adobe Myriad Condensed; and the

code font is Dalton Maag’s Ubuntu Mono.



This is a offline tool, your data stays locally and is not send to any server!



Feedback \& Bug Reports

<!-- END_FILE: vault/06-Cosmic-Python-Journey/references/architecture_patterns_with_python.md -->

---

## File 38: `backend/prompts/router_decomposition.md`

<!-- START_FILE: backend/prompts/router_decomposition.md -->

﻿You are a Principal Enterprise Software Architect & Domain-Driven Design (DDD) Lead.

Analyze the following natural language business pitch and perform a STRICT SEPARATION between:
1. DOMAIN STRUCTURE (Entities, Value Objects, Types, Aggregate Roots)
2. BEHAVIOR INBOX (Atomic Business Rules, Invariants, Edge Cases, State Transitions)

BUSINESS PITCH:
"{business_pitch}"

CRITICAL DECOMPOSITION INSTRUCTIONS:
- STRUCTURE:
  - Identify the primary Aggregate Roots (e.g. Order, Pallet, Booking).
  - Define clear entity attributes with primitive/semantic types ("string", "float", "int", "boolean", "datetime").
  - Do NOT put business logic or rules inside the structure section.

- BEHAVIOR INBOX:
  - Extract each distinct business rule, invariant, pricing formula, or edge case as an atomic spec item.
  - Formulate a precise BDD specification ("Given ... When ... Then ...").
  - Target the specific Aggregate Root that owns the invariant.
  - Set `is_mathematical_boundary` to true if the rule enforces mathematical formulas, capacity limits, ranges, or expiration windows.

Respond STRICTLY with a valid JSON object matching this schema (no markdown, no explanations):
{
  "structure": {
    "domain_name": "<DomainName>",
    "entities": [
      {
        "name": "<EntityName>",
        "is_aggregate_root": true,
        "attributes": [
          {"name": "<attr_name>", "type": "<type>", "required": true, "default_value": null}
        ],
        "relationships": [
          {"target": "<TargetEntity>", "relation_type": "one_to_many"}
        ]
      }
    ],
    "value_objects": [
      {
        "name": "<ValueObjectName>",
        "is_aggregate_root": false,
        "attributes": [
          {"name": "<attr_name>", "type": "<type>", "required": true, "default_value": null}
        ]
      }
    ]
  },
  "inbox": {
    "domain_name": "<DomainName>",
    "specs": [
      {
        "spec_id": "SPEC-001",
        "title": "<Short Rule Title>",
        "description": "<Detailed Rule Description>",
        "given_when_then": "Given <preconditions> When <action> Then <expected outcome>",
        "target_aggregate": "<EntityName>",
        "is_mathematical_boundary": false,
        "priority": "High",
        "status": "PENDING"
      }
    ]
  }
}

<!-- END_FILE: backend/prompts/router_decomposition.md -->

---

## File 39: `backend/prompts/domain_discovery.md`

<!-- START_FILE: backend/prompts/domain_discovery.md -->

You are a World-Class Domain-Driven Design (DDD) Enterprise Architect.
Analyze the following business pitch and extract a complete, formal 6-part Domain-Driven Design (DDD) domain schema.

BUSINESS PITCH:
"{business_pitch}"

CRITICAL DOMAIN VOCABULARY ISOLATION INSTRUCTION:
- You MUST extract entities, value objects, domain services, and invariants using terms EXCLUSIVELY native to the specific business pitch provided.
- You MUST NOT use generic or unrelated terms like "SKU", "Batch", "OrderLine", "allocate", or "_purchased_quantity" unless the business pitch explicitly describes retail inventory allocation.

Respond STRICTLY with a valid JSON object matching this exact structure (no markdown explanations):
{
  "ubiquitous_language": {
    "<TermName>": "<Definition in domain terms>"
  },
  "value_objects": [
    {
      "name": "<ValueObjectName>",
      "fields": {"<field1>": "<type1>", "<field2>": "<type2>"},
      "description": "<Description>"
    }
  ],
  "entities": [
    {
      "name": "<EntityName>",
      "identity_key": "<id_field>",
      "fields": {"<id_field>": "str", "<field2>": "<type>"},
      "methods": [
        {"name": "<method_name>", "params": {"<param1>": "<type>"}, "return_type": "None", "description": "<Description>"}
      ]
    }
  ],
  "domain_services": [
    {
      "name": "<service_name>",
      "params": {"<param1>": "<type>"},
      "return_type": "<type>",
      "description": "<Description>"
    }
  ],
  "domain_exceptions": [
    {
      "name": "<ExceptionName>",
      "description": "<Description of when this exception is raised>"
    }
  ],
  "invariants": [
    {"id": "INV-001", "rule": "<Domain Rule Statement>", "affected_entities": ["<EntityName>"]}
  ],
  "mermaid_class_diagram": "classDiagram\\n    class <EntityName> {\\n        +str <id_field>\\n        +<method_name>()\\n    }",
  "mermaid_sequence_diagram": "sequenceDiagram\\n    autonumber\\n    actor Client\\n    participant Service as <service_name>()\\n    Client->>Service: invoke"
}

<!-- END_FILE: backend/prompts/domain_discovery.md -->

---

## File 40: `backend/prompts/test_case_generation.md`

<!-- START_FILE: backend/prompts/test_case_generation.md -->

You are a senior software development engineer in test (SDET).
Your task is to write an automated pytest test case that verifies the following requirement for a React (Vite + TypeScript) application.

Requirement Details:
ID: {req_id}
Title: {title}
Description: {description}

CRITICAL INSTRUCTIONS FOR TEST CODE:
1. The test MUST be a functional/layout browser-runtime test using standard `selenium` WebDriver.
2. Do NOT import or use third-party test wrappers like 'seleniumbase' or 'webdriver_manager'. Stick strictly to standard 'selenium' imports.
3. Configure the Chrome WebDriver to run in headless mode with these exact flags:
   - '--headless=new'
   - '--no-sandbox'
   - '--disable-dev-shm-usage'
   - '--disable-gpu'
   - '--remote-debugging-port=9222'
4. The test must navigate to the Vite application local URL: 'http://localhost:5174'.
5. Use standard Selenium wait strategies (like WebDriverWait) to wait for elements to render.
6. The test case function in Python MUST contain a docstring formatted EXACTLY like this:
   \"\"\"<Short title of the test>

   <Detailed description of the test>

   id: {test_case_id}
   req: {req_id}
   Given: <Preconditions for the test>
   When: <Action or triggers taken in the test>
   Then: <Expected outcomes or assertions>
   \"\"\"
7. Include proper decorators for Allure (once integrated) or links in the docstring.
8. The test MUST fail initially because the requested features described in the requirement description have not been implemented in the application yet. Ensure it asserts on DOM elements/text/styles that are expected to exist once the requirement is met, but do not exist in a blank "Hello, World!" application.

Respond ONLY with the complete, valid Python test code for this single test. Do not include markdown fences or any explanations.

<!-- END_FILE: backend/prompts/test_case_generation.md -->

---

## File 41: `backend/prompts/code_generation.md`

<!-- START_FILE: backend/prompts/code_generation.md -->

You are a developer working on a React (Vite + TypeScript) application.

Here are the current source files in the project:
{current_workspace_context}

Please implement the following ticket:
{task_desc}
{feedback_note_attempt}
{test_context}

You MUST implement the requested changes in the codebase AND write a corresponding automated pytest test file under `{test_file_path}` to verify the functionality.{bug_test_instruction}

ARCHITECTURE & LAYERING RULES:
- Follow clean Domain-Driven Design (DDD) boundaries (Domain Model -> Repository Pattern -> Service Layer / Unit of Work -> Presentation / Entrypoints).
- Domain models must remain pure (no database framework/ORM imports).
- Abstract data persistence behind Repositories and manage transactions with Unit of Work (UoW).
- Keep API route handlers thin: NEVER place SQL/ORM queries or business rules directly inside HTTP routes.

The pytest tests should run in a Python environment using Selenium WebDriver in headless mode to verify that the app behaves correctly at runtime.
Your test file `{test_file_path}` should define test functions that setup a headless Selenium webdriver, navigate to 'http://localhost:5174' (where the workspace application runs), and perform functional/layout checks.


CRITICAL INSTRUCTIONS FOR BROWSER RUNTIME TESTS:
1. Always run Chrome in headless mode with parameters '--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', and '--remote-debugging-port=9222'.
2. Do NOT import or use 'webdriver_manager' or 'ChromeDriverManager'. Use standard 'webdriver.Chrome(options=chrome_options)' directly (Selenium 4 handles driver binaries automatically).
3. Use standard Selenium wait strategies (like WebDriverWait) to ensure components are loaded.
4. Assert on runtime properties (like element position, dimensions, computed visibility, or text content in the browser DOM) instead of reading source files as plain text.
5. CRITICAL RESPONSIVENESS REQUIREMENT: The application MUST be fully responsive and display correctly on both desktop (e.g. 1280px width) and mobile (e.g. 375px width) viewports. Ensure that your styling (CSS) accommodates different screen widths without content overlapping, getting truncated, or causing horizontal scrollbars on mobile. If you write automated Selenium tests, verify that layout and elements align correctly at both viewport sizes.
6. NO THIRD-PARTY LIBRARIES: Do NOT import or use third-party test wrappers such as 'seleniumbase'. Stick strictly to standard 'selenium' imports (e.g. `from selenium import webdriver`).
7. SCROLLBAR TOLERANCE: When comparing computed element widths against the viewport width in tests, do NOT assume they match exactly down to the pixel. Vertical scrollbars consume about 15-20px of space. Instead, assert that they match `document.documentElement.clientWidth` (which excludes scrollbar width) or allow a tolerance of at least 20px (e.g. `abs(header_width - viewport_width) <= 20`).
8. CLEAN UP OVERRIDDEN STYLES: When updating or moving layouts (e.g., changing header positioning), ensure you clean up and remove any old properties (such as relative centering offsets like `left: 50%` or `transform: translateX(-50%)`) rather than leaving them to conflict with the new styles.

CRITICAL REQUIREMENT FOR TEST CASES:
Each test case function in `{test_file_path}` MUST contain a docstring formatted EXACTLY like this:
\"\"\"<Short title of the test>

<Detailed description of the test>

id: TST-<unique 4-digit number>
req: {parent_id}
Given: <Preconditions for the test>
When: <Action or triggers taken in the test>
Then: <Expected outcomes or assertions>
\"\"\"

Example:
\"\"\"Test home page header layout.

Verify that the app homepage header is fixed at the top and the main content does not overlap it.

id: TST-1001
req: {parent_id}
Given: The Vite app is running
When: Opening the page in headless Chrome and checking element positions
Then: The header bounding box y is 0, and the content container y is greater than or equal to the header height
\"\"\"

Modify the necessary files to implement the requested changes. Only output files that need to be changed or created.

IMPORTANT: Respond ONLY with file blocks in this exact format (no markdown fences):
=== FILE: src/App.tsx ===
<full file content here>
=== END FILE ===
=== FILE: {test_file_path} ===
<full pytest test content here>
=== END FILE ===

You may output multiple file blocks. Each block must contain the COMPLETE file content (not a diff). Do NOT include any other text outside the file blocks.

<!-- END_FILE: backend/prompts/code_generation.md -->

---

## File 42: `backend/prompts/ui_generation.md`

<!-- START_FILE: backend/prompts/ui_generation.md -->

You are an expert Principal Frontend Engineer and UI/UX Designer creating a live, full-stack React application for a user's business pitch.

## Application Context
- **Business Pitch**: "{business_pitch}"
- **Domain Schema / Entities**: {domain_schema_json}
- **Selected Feature Blocks**: {selected_blocks_json}

## Design & UI Guidelines

### 1. Visual Theme & Identity
Design an attractive, modern, and polished interface **tailored specifically** to the business pitch domain.

- **Customer-facing services & Care** (booking, appointments, wellness, sessions): **Default to Light Warm Palettes** (Cream `#FAF7F2`, Coral accents `#C85A44`, Mint pills `#E2F6ED`, Serif typography `'Playfair Display', Georgia, serif`). Include trust badges, provider cards, stat counters, interactive weekly availability matrix, and booking CTAs.
- **Retail, Storefronts & Hospitality**: Fresh Light Palettes (Crisp Off-White `#FAFAFA`, Warm/Vibrant accents), product grids, cart drawers, order status pipelines.
- **B2B / Operational tools**: Clean Light Slate dashboards (`#F8FAFC`), metric stat cards, Kanban status pipelines.
- **Developer Tools ONLY**: Dark Slate (`#0F172A`) is strictly reserved for developer CLI, kernel logs, or terminal tools.

### 2. UI Component Styling
- Use CSS custom variables (`var(--bg-main)`, `var(--bg-card)`, `var(--text-primary)`, `var(--color-primary)`, `var(--color-mint)`, `var(--border-color)`, `var(--font-heading)`) defined in a top `:root` style block.
- DO NOT hardcode dark background colors (`#0f172a`, `#1e293b`) for consumer or service booking pitches.
- Ensure high contrast, smooth rounded corners (`1rem` to `1.5rem`), readable typography, hover states, and clear call-to-action buttons.
- Use SVG icons or emoji for decorative elements. Do NOT import missing image files.

### 3. Backend Integration
Connect form submissions and list views to backend API endpoints. Use RESTful conventions that match the domain:
- Use `fetch('/api/...')` calls that make sense for the business pitch domain.
- Maintain optimistic local state updates for instantaneous UI response.
- Do NOT assume endpoints are `/batches` unless the pitch is about batch inventory.

### 4. Domain-Native Spatial & Interactive Controls (Zero "Square Hole" Trap)
- DO NOT default to a generic spreadsheet table or standard 3-column e-commerce grid if the user's business domain demands specialized interactive tools.
- For quantum, math, or physics domains: Render interactive wire diagrams, gate matrix canvases, probability distribution amplitude bars, and phase visualizers.
- For audio, acoustics, or telemetry domains: Render frequency waterfall spectrograms, beamformer controls, Doppler curves, or radar grids.
- For robotics, UAVs, or fleet logistics: Render geofence radar maps, waypoint schedulers, coordinate blips, and telemetry HUDs.
- For bespoke builders & configurators: Render interactive step-by-step customizers, real-time formula estimators, and visual preview containers.

### 5. Mobile-First Responsiveness Invariant
- Every generated UI MUST be mobile-first responsive and render cleanly on 375px mobile viewports as well as 1280px desktop viewports.
- Define global CSS reset rules in `:root` style: `* { box-sizing: border-box; } body { margin: 0; overflow-x: hidden; } img, svg { max-width: 100%; }`.
- Header navigation bars MUST use `flex-wrap: wrap` and flexible gaps (`gap: '0.75rem'`) so titles and nav links wrap gracefully on mobile viewports without horizontal scrolling.
- Slide-over drawers, modals, and card containers MUST use fluid max-width constraints (e.g. `width: '100%', maxWidth: '380px'`). NEVER use fixed width like `width: '380px'` without `maxWidth: '100%'`.

### 6. Domain State Contracts & Immutable Order Tracking Snapshots
- **Catalog-Driven Cart**: Cart items (`cart`) must be driven by items selected from the domain catalog (`items`). Adding an item to the cart must reference catalog properties (`title`/`name`, `price_or_rate`/`price`).
- **Immutable Order Tracking Snapshot**: When completing checkout (`handleSimulatePayment`), convert current cart items into an immutable Order Snapshot object added to `orders`:
  `{ id: String(Date.now()), ref: 'ORD-' + Math.floor(1000 + Math.random()*9000), item: summaryText, total: cartTotal, status: 'Received', eta: '25-35 mins' }`
- **Decoupled Order History**: Order tracking records (`orders`) represent historical purchases. They MUST remain intact as immutable snapshots even if catalog items in `items` are mutated, filtered, or deleted later.
- **Data Fixtures Sync**: Sync state updates back to the backend host using:
  `fetch(getApiUrl('/api/components/fixtures/update'), { method: 'POST', body: JSON.stringify({ canonical_key, fixtures }) })` and `window.parent.postMessage({ type: 'FIXTURES_UPDATED', canonical_key, fixtures }, '*')`.

### 7. Domain Entity Attributes & Tag Chips
- When domain items include structured attributes such as `specs`, `ingredients`, `features`, or `tags`, render them as clean, rounded pill/chip badges inside the item card:
  `{item.specs && item.specs.map((spec: string) => <span key={spec} style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: '9999px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>{spec}</span>)}`

Respond STRICTLY with valid React TypeScript code inside a single ```tsx code block. Do NOT include any Markdown conversational intro or outro text.

<!-- END_FILE: backend/prompts/ui_generation.md -->

---

## File 43: `backend/prompts/visual_qa.md`

<!-- START_FILE: backend/prompts/visual_qa.md -->

You are an automated visual QA gate for a web application.
Evaluate whether the rendered screenshots of the app match the requirements of the ticket and are responsive.

Ticket Details:
ID: {ticket_id}
Title: {title}
Description: {description}

You are provided with two screenshots of the rendered application:
1. Desktop Viewport (1280x800)
2. Mobile Viewport (375x812)

Here is the code and tests written by the developer agent for this ticket:
{code_context}

Please analyze both screenshots and verify if they satisfy the requirement.
Specifically, verify:
- Desktop view (1280x800): No styling bugs, overlapping elements, or alignment issues.
- Mobile view (375x812): The site is responsive. Text does not wrap awkwardly, buttons/elements are not cut off or overlapping, and there is no horizontal overflow/scrollbar issues.
- Check for general styling bugs (e.g. text hidden behind headers, wrong colors, broken margins).
- Inspect if the test code is adequate or if it passes superficially without actually testing the layout/responsiveness requirements.

You MUST respond with a single, valid JSON object matching this schema:
{{
  "passed": bool,
  "reasoning_and_discrepancy": "Detailed analysis of what is visible in both the desktop and mobile screenshots, and any layout/rendering/responsiveness issues found.",
  "test_adequacy": "Analysis of whether the written tests are sufficient to verify this requirement or if they are superficial/insufficient.",
  "correction_advice": "Clear, actionable advice for the developer agent to fix any layout, responsiveness, code, or test issues."
}}

Respond ONLY with the JSON object. Do not wrap it in markdown fences.

<!-- END_FILE: backend/prompts/visual_qa.md -->

---

## File 44: `backend/prompts/visual_audit.md`

<!-- START_FILE: backend/prompts/visual_audit.md -->

You are an expert UI/UX Visual Quality Inspector and Design Auditor reviewing a live application preview screenshot.

## Inspection Objective
Analyze the attached screenshot of the application UI generated for the business pitch: "{business_pitch}".

## Visual Audit Checklist
Critique the screenshot against these 3 core visual criteria:

1. **Header & Navigation Structure**:
   - Is there a SINGLE unified header bar?
   - FAIL if there are duplicate navigation bars, secondary dark tab bars below the hero, or competing top menus.

2. **Color Palette & Theme System**:
   - Is the color scheme harmonious and consistent across the page?
   - FAIL if dark-mode slate panels (`#1e293b`) bleed into a light boutique theme (`#fcfbf7` / white) or vice-versa.

3. **Typography, Layout & Contrast**:
   - Is text high-contrast, clean, and legible?
   - Are call-to-action buttons clearly styled and aligned?
   - Are card grid elements spaced neatly without overlapping?

## Output Requirement
Respond strictly with JSON in the following format:

```json
{
  "passed": true,
  "score": 95,
  "summary": "Clean unified header with consistent light boutique styling and no duplicate tabs.",
  "critique": [],
  "suggested_fixes": []
}
```

If any rule fails, set `"passed": false`, list specific visual issues in `"critique"`, and provide actionable code fix instructions in `"suggested_fixes"`.

<!-- END_FILE: backend/prompts/visual_audit.md -->

---

## File 45: `backend/prompts/task_decomposition.md`

<!-- START_FILE: backend/prompts/task_decomposition.md -->

Break down the following requirement into 1 to 3 distinct technical tasks.
Requirement Title: {title}. Description: {description}.
If there are logical dependencies between these tasks (e.g., task B depends on task A being implemented first), assign a temporary ID (e.g. "t1", "t2", "t3") to each task in the 'id' field, and list the prerequisite task IDs in its 'dependencies' field.
Respond ONLY with a JSON array of objects, where each object has: 'id' (string, e.g. "t1"), 'title' (string), 'description' (string), and 'dependencies' (array of strings of temporary IDs, e.g. ["t1"]).

<!-- END_FILE: backend/prompts/task_decomposition.md -->

---

## File 46: `backend/prompts/requirement_audit.md`

<!-- START_FILE: backend/prompts/requirement_audit.md -->

You are a senior product manager and developer agent auditing a requirement modification.
The parent requirement has been updated. You need to analyze the changes to determine if:
1. Any new technical tasks (tickets) are needed to implement this new behavior.
2. Any existing technical tasks' descriptions/titles need to be modified.
3. Any new python/pytest tests are needed in `{test_file_path}`.
4. Any existing python/pytest tests in `{test_file_path}` are expected to fail now because of the updated requirement (and thus should be decorated with `@pytest.mark.xfail(reason="...")`).

--- REQUIREMENT ---
ID: {req_id}
Title: {title}
Description: {description}

--- EXISTING CHILD TASKS ---
{existing_tasks_summary}

--- CURRENT WORKSPACE CODEBASE ---
{workspace_context}

--- CURRENT TESTS FILE ({test_file_path}) ---
{test_code}

--- INSTRUCTIONS ---
Based on the requirement, analyze the existing tasks and test file.
If the requirement changed the expected behavior, decorate the obsolete/failing tests with `@pytest.mark.xfail(reason="...")` in the updated test code.
If new tests are needed, append them to the updated test code. Every test function in `{test_file_path}` MUST contain a docstring with:
  id: TST-<unique 4-digit number>
  req: {req_id}
  Given: ...
  When: ...
  Then: ...
Ensure all imports like `import pytest` are preserved.

Respond ONLY with a JSON object. No markdown formatting, no explanation. The JSON object must have EXACTLY these fields:
{{
  "new_tasks": [
    {{
      "title": "Task title",
      "description": "Task description explaining what to change/implement"
    }}
  ],
  "update_tasks": [
    {{
      "id": "REQ-XXXX",
      "description": "New updated task description"
    }}
  ],
  "updated_test_code": "<the complete contents of {test_file_path} with new tests added and target existing tests decorated with @pytest.mark.xfail(...)>"
}}

<!-- END_FILE: backend/prompts/requirement_audit.md -->

---

## File 47: `backend/prompts/merge_resolution.md`

<!-- START_FILE: backend/prompts/merge_resolution.md -->

You are a senior software engineer resolving a git merge conflict in the file '{fname}'.
         
Here is the content of the file containing merge conflict markers:
{content}

Please resolve all the conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in this file and combine the changes from both sides logically and cleanly.

CRITICAL REQUIREMENTS:
1. Do NOT include any git conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in your output.
2. If you are resolving conflicts in CSS files (especially 'src/index.css'), you MUST ensure that the 'body {{ ... }}' style block is placed BEFORE the 'html, body {{ ... }}' style block (or similar) to prevent regex/index matching errors in the test suite.
3. Output the COMPLETE resolved file contents and absolutely NOTHING else. No markdown block formatting, no explanation, just the plain text of the resolved file.
4. Keep modifications minimal and preserve the exact styling rules and declarations of unaffected lines. Do not merge body block properties (like font-size) into the global html, body block.

<!-- END_FILE: backend/prompts/merge_resolution.md -->

---

## File 48: `backend/prompts/ddd_guidelines_template.md`

<!-- START_FILE: backend/prompts/ddd_guidelines_template.md -->

# DDD Architecture & Code Structure Guidelines

When implementing code for this ticket, you MUST adhere to Domain-Driven Design (DDD) layer separation and clean architecture principles:

1. **Domain Model Layer (`domain/`)**:
   - Write pure domain logic (Entities, Value Objects, Domain Services).
   - Domain objects must NOT import ORMs (SQLAlchemy, Django), database connection pools, or web frameworks (FastAPI, Flask).
   - Enforce business invariants directly in domain entity methods.

2. **Repository Protocol & Adapters (`adapters/`)**:
   - Abstract data storage behind a Repository interface (`AbstractRepository`).
   - Standard operations: `.add(entity)`, `.get(id)`, `.list()`.
   - Keep ORM mappings or raw SQL isolated strictly within repository adapters (`SqlAlchemyRepository`).

3. **Application Service Layer & Unit of Work (`service_layer/`)**:
   - Orchestrate use cases in service functions.
   - Use the Unit of Work (UoW) pattern (`with uow:`) for atomic transaction management.
   - Service layer functions accept primitive parameters (e.g. `order_id: str`, `qty: int`), fetch entities via UoW repositories, execute domain operations, and commit transactions.

4. **Entrypoints & Presentation (`entrypoints/` or API routes)**:
   - Keep controllers, HTTP route handlers, and CLI commands thin.
   - Entrypoints must delegate requests to the Service Layer functions.
   - NEVER place raw SQL, ORM queries, or business rules inside API route handlers.

5. **Test-Driven Development (TDD)**:
   - Write **Low Gear** unit tests (`tests/unit/`) directly against `domain/` objects.
   - Write **High Gear** integration tests (`tests/integration/`) against `service_layer/` using `FakeUnitOfWork` and `FakeRepository`.
   - Write **End-to-End** API tests (`tests/e2e/`) against `entrypoints/` to verify HTTP contracts.

<!-- END_FILE: backend/prompts/ddd_guidelines_template.md -->

---

## File 49: `backend/prompts/green_class_repair.md`

<!-- START_FILE: backend/prompts/green_class_repair.md -->

You are a Principal Python Software Engineer executing the GREEN phase of a strict Test-Driven Development (TDD) and Domain-Driven Design (DDD) state machine.

A pytest unit test has failed in the RED phase. Your task is to update the target domain class implementation so that the test passes cleanly.

## Target Class Code (Extracted via LibCST):
\\python
{extracted_class_code}
\
## BDD Specification:
- **Title**: {spec_title}
- **Scenario**: {spec_given_when_then}
- **Target Aggregate**: {target_aggregate}
- **Mutation Type**: {spec_type}

## Failing Pytest AssertionError & Execution Output (RED Phase):
\{failure_output}
\
## Architectural & Code Rules:
1. Return ONLY the complete, updated Python class definition for \{target_class_name}\.
2. The class MUST use \@dataclass\ and pure Python standard library types.
3. Fix all missing attributes, methods, invariant validators, or state transitions required by the test.
4. Strictly follow PEP8, SOLID principles, and strict OOP.
5. DO NOT include any inline comments. Use Google-style docstrings if documenting methods.
6. Return the code inside a single \\python \\ block with zero conversational intro or outro.

<!-- END_FILE: backend/prompts/green_class_repair.md -->

