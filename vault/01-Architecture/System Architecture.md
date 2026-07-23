# System Architecture

Provable is an agentic software development simulator. It features a React-based PM Studio frontend and a FastAPI backend that orchestrates autonomous developer agents within a sandboxed target git repository (`workspace/`).

```mermaid
graph TD
    subgraph Frontend [PM Studio Frontend - React / Vite]
        App[App.tsx Entrypoint] --> ProjectSelector[components/ProjectSelector.tsx]
        App --> KanbanBoard[components/KanbanBoard.tsx]
        App --> RequirementsList[components/RequirementsList.tsx]
        App --> CodeReview[components/CodeReview.tsx]
        App --> CoverageHub[components/CoverageHub.tsx]
        App --> AgentTray[components/AgentTray.tsx]
        CodeReview --> DiffViewer[components/DiffViewer.tsx]
        App --> useRequirements[hooks/useRequirements.ts Hook]
    end

    subgraph Backend [FastAPI Backend Engine]
        API[main.py REST API] --> Store[db/store.py DataStore API]
        API --> Orchestrator[agent_orchestrator.py LangGraph]
        API --> Prompts[prompts/ Externalized Templates]
        API --> Config[config/models.yaml & integrations.yaml]
        Orchestrator --> LLM[OpenAI Client - Abstraction]
        Orchestrator --> Git[Git CLI Sandbox Manager]
        Orchestrator --> Pytest[Pytest Test Runner]
        Orchestrator --> Selenium[Selenium Screenshot Capture]
        Orchestrator --> Vision[Gemini Vision Quality Gate]
    end

    subgraph DB [Persistence Layer]
        Store --> SQLite[SQLite provable.db Database]
        Store <-->|Bidirectional Sync| SDoc[requirements/requirements.sdoc]
    end

    subgraph Workspace [Target Project Sandbox]
        Git --> TargetCode[workspace/ Source Files]
        Pytest --> TargetTests[workspace/tests/ Test Files]
    end

    subgraph Docker [Allure Reporting Container]
        Orchestrator --> AllureContainer[Allure Docker Service :5050]
        CoverageHub --> AllureContainer
    end

    App <-->|REST API / JSON| API
```

## 1. Subsystem Breakdown

### PM Studio Frontend (`src/`)
Built with React, TypeScript, Vite, and custom CSS styling. It provides project management control over autonomous developer agents:
- **`App.tsx`**: Main application container housing header controls, navigation tabs (Kanban, Requirements Explorer, Code Review, Coverage Hub), and global agent status banners.
- **`components/KanbanBoard.tsx`**: Displays tickets in Kanban lifecycle columns (`Backlog`, `In Progress`, `Review`, `Conflict`, `Done`) with real-time state badges.
- **`components/RequirementsList.tsx`**: Hierarchical tree viewer for folders, requirements, tasks, and bugs. Supports full CRUD operations, parent assignment, dependency management, and TDD test spec generation triggers.
- **`components/CodeReview.tsx`**: Embeds side-by-side git diffs (`DiffViewer`), pytest log tracebacks, and review approval/rejection action buttons.
- **`components/CoverageHub.tsx`**: Aggregates requirement-to-test mapping matrices and embeds the live Allure Docker portal (`:5050`) within an iframe.
- **`components/AgentTray.tsx`**: Collapsible console tray displaying active LangGraph execution nodes, attempt counters, streaming stdout/stderr log output, and review queue items.
- **`components/ProjectSelector.tsx`**: Drawer modal for switching workspace project directories and configuring model provider keys.

### FastAPI Backend Engine (`backend/`)
The core orchestrator and REST service layer:
- **`main.py`**: Exposes endpoints for requirement CRUD, project selection, git diff generation, agent run statuses, and ticket merge approvals. Performs automatic project initialization against the Allure Docker container on startup.
- **`agent_orchestrator.py`**: Executes the autonomous agent state machine using **LangGraph**. Coordinates branch creation, LLM code generation, preview dev server execution, pytest runner, Selenium screenshot capture, Gemini Vision visual layout evaluation, and git rollbacks.
- **`db/store.py`**: High-performance SQLite wrapper (`provable.db`) managing relational data for requirements, test cases, and agent runs.
- **`integrations/`**: Modules for syncing SQLite state with StrictDoc specification files (`strictdoc_client.py`), Jira tickets (`jira_client.py`), and Allure Docker API endpoints (`allure_client.py`).

### Data Storage & Specifications
- **SQLite Database (`backend/provable.db`)**: Primary operational database powering real-time queries.
- **StrictDoc Specs (`requirements/requirements.sdoc`)**: Text-based specification files synchronized bidirectionally with the SQLite database to maintain version-controlled requirements in Git.

### Containerized Infrastructure
- **Allure Docker Service (`frankescobar/allure-docker-service:5050`)**: Containerized reporting service that aggregates pytest execution outputs from `workspace/allure-results/` and renders coverage metrics.
