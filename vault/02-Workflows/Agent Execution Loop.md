# OpenHands Agent Execution Pipeline

Provable utilizes an **OpenHands Agent Execution Runner** (`backend/agent_orchestrator.py`) to execute developer tasks inside target workspaces (`workspace/`).

```mermaid
sequenceDiagram
    participant PM as PM Studio UI
    participant Backend as FastAPI Backend
    participant Runner as OpenHands Execution Runner
    participant Git as Workspace Git Repository
    participant Pytest as Pytest Runner / Allure

    PM->>Backend: 1. Trigger Agent for Requirement (REQ-101)
    Backend->>Runner: 2. Invoke run_openhands_loop(REQ-101)
    activate Runner
    Runner->>Git: 3. Create & Checkout ticket/REQ-101 branch from main
    Runner->>Runner: 4. Formulate Task Prompt (Requirement + Failing Test Spec)
    Runner->>Git: 5. OpenHands executes edits in workspace/
    Runner->>Pytest: 6. Run pytest on workspace/tests/test_REQ-101.py
    
    alt Test Verification Passed (Green)
        Pytest-->>Runner: 0 Errors / All Tests Passed
        Runner->>Git: Commit changes to ticket/REQ-101
        Runner->>Backend: Update status to "Review"
        Backend-->>PM: Submit to Code Review Queue
    else Test Verification Failed (Red)
        Pytest-->>Runner: Assertion Error / Test Failures
        Runner->>Git: Rollback workspace (git checkout -- . & git clean -fd)
        Runner->>Backend: Update status to "Backlog" with error log
        Backend-->>PM: Display failure log in Agent Tray
    end
    deactivate Runner
```

## Detailed Execution Steps

### 1. Task Selection & Initialization
- `run_openhands_loop(req_id)` identifies the target `Backlog` item.
- Initializes agent status tracking and creates log stream at `backend/logs/<TICKET_ID>.log`.

### 2. Git Branch Isolation
- Checks out `main` and creates/resets dedicated working branch `ticket/<TICKET_ID>`.

### 3. OpenHands Task Prompt Assembly
- Formulates the task prompt containing requirement title, detailed description, and path to target BDD pytest spec (`workspace/tests/test_<REQ_ID>.py`).

### 4. Sandbox Execution
- OpenHands runs inside the target workspace directory (`workspace/`), performing code modifications to satisfy the failing test spec.

### 5. Verification & Review Queue Finalization
- Executes `run_pytest()` on the target test spec.
- On **PASS**: Commits branch `ticket/<TICKET_ID>` and transitions ticket to `Review` status for PM git diff inspection and 1-click merge approval.
- On **FAIL**: Cleans up workspace (`git checkout -- .`, `git clean -fd`) and records failure logs in DataStore.
