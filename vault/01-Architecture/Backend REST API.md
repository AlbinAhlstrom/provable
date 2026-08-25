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

