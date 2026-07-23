# Backend REST API Specification & Data Contracts

The FastAPI backend application (`backend/main.py`) serves as the primary REST API and orchestrator for PM Studio, database persistence, and agent execution control.

- **Base URL**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

---

## Pydantic Request & Response Models

To deterministically recreate the API contract, implement the following Pydantic schemas:

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class RequirementBase(BaseModel):
    title: str
    description: Optional[str] = ""
    type: str = Field(..., pattern="^(Folder|Requirement|Task|Bug)$")
    priority: str = Field("Med", pattern="^(High|Med|Low)$")
    status: str = Field("Backlog", pattern="^(Backlog|In Progress|Review|Conflict|Done)$")
    parent_id: Optional[str] = None
    jira_key: Optional[str] = None
    sdoc_uid: Optional[str] = None
    dependencies: List[str] = []
    assigned_agents: List[str] = []

class RequirementCreate(RequirementBase):
    id: str

class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    parent_id: Optional[str] = None
    dependencies: Optional[List[str]] = None
    assigned_agents: Optional[List[str]] = None

class TestCaseCreate(BaseModel):
    id: str
    requirement_id: str
    title: str
    given_text: Optional[str] = ""
    when_text: Optional[str] = ""
    then_text: Optional[str] = ""
    file_path: str

class RejectRequest(BaseModel):
    feedback: str

class ProjectSelectRequest(BaseModel):
    workspace_path: str
```

---

## REST Endpoints Overview

### 1. Requirements Management

#### `GET /api/requirements`
- **Response**: `List[RequirementResponse]` containing all hierarchy nodes.

#### `POST /api/requirements`
- **Body**: `RequirementCreate`
- **Response**: Created `RequirementResponse` object. Side-effect: triggers `strictdoc_client.export_sdoc()`.

#### `PUT /api/requirements/{req_id}`
- **Body**: `RequirementUpdate`
- **Response**: Updated `RequirementResponse` object.

#### `DELETE /api/requirements/{req_id}`
- **Response**: `{"success": true, "deleted_id": req_id}`.

---

### 2. TDD Test Spec Generation & Agent Execution

#### `POST /api/requirements/{req_id}/generate-test`
- **Response**: Created `TestCaseResponse` object. Writes `workspace/tests/test_<req_id>.py` and verifies TDD Red state (failing test).

#### `POST /api/requirements/{req_id}/run-agent`
- **Response**: `{"status": "started", "run_id": run_id, "ticket_id": req_id}`. Spawns background LangGraph agent loop.

#### `GET /api/agent-status/{ticket_id}`
- **Response**: `{"ticket_id": ticket_id, "status": "running|success|failed", "current_stage": stage, "attempts": attempts, "logs": list_of_logs}`.

---

### 3. Review Queue & Branch Operations

#### `GET /api/review-queue`
- **Response**: List of requirements in `Review` state with `proposed_code` diff strings and test execution reports.

#### `POST /api/requirements/{req_id}/merge`
- **Response**: `{"status": "merged", "branch": "ticket/<req_id>"}`. Merges ticket branch into `main`.

#### `POST /api/requirements/{req_id}/reject`
- **Body**: `RejectRequest`
- **Response**: `{"status": "rejected", "requirement_id": req_id}`. Rolls back branch and resets status to `Backlog`.

---

### 4. Workspace & Diffs

#### `GET /api/diff/{ticket_id}`
- **Response**: `{"ticket_id": ticket_id, "diff": git_diff_string}`.

#### `POST /api/projects/select`
- **Body**: `ProjectSelectRequest`
- **Response**: `{"status": "active", "path": workspace_path}`.
