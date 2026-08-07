# Testing Strategy & Quality Assurance Architecture

Provable enforces a 5-tier test architecture combined with Shift-Left Test-Driven Development (TDD). Every requirement must be backed by automated test specs before developer agents generate implementation code.

---

## 5-Tier Test Architecture

```
tests/
├── unit/         # Isolated functions, DataStore queries, helper logic
├── api/          # FastAPI endpoint integration tests (httpx / TestClient)
├── integration/  # StrictDoc, Jira, and Allure sync client tests
├── system/       # LangGraph agent state machine node execution tests
└── e2e/          # End-to-end full application workflows (Selenium / Playwright)
```

### Tier 1: Unit Tests (`tests/unit/`)
- Tests isolated utility functions, database helper methods in `store.py`, and model config parsing in `config_loader.py`.
- Fast execution (<1s).

### Tier 2: API Tests (`tests/api/`)
- Uses FastAPI `TestClient` or `httpx.AsyncClient` to validate REST endpoints (`/api/requirements`, `/api/requirements/{id}/merge`, `/api/review-queue`).
- Verifies HTTP status codes, JSON schema response structures, and error responses.

### Tier 3: Integration Tests (`tests/integration/`)
- Verifies synchronization loops with external tools:
  - StrictDoc parser/exporter (`strictdoc_client.py`).
  - Jira ticket status transition calls (`jira_client.py`).
  - Allure Docker Service REST API (`allure_client.py`).

### Tier 4: System Tests (`tests/system/`)
- Tests individual nodes of the LangGraph agent state machine (`prepare_branch`, `code_generation`, `test_runner`, `visual_qa`, `finalize`).
- Mocks LLM responses to test graph state transitions, attempt counters, and branch rollback mechanics.

### Tier 5: End-to-End Tests (`tests/e2e/`)
- Headless Selenium/Chrome automation testing complete end-to-end PM Studio UI user flows:
  - Creating a requirement in the explorer.
  - Generating a failing TDD test spec.
  - Dispatching an autonomous agent.
  - Approving a code review diff and verifying git main branch merge.

---

## BDD Test Docstring & Allure Metadata Tagging

All generated pytest specs (`workspace/tests/test_*.py`) must include `@allure` metadata decorators and Given-When-Then docstrings:

```python
import allure
import pytest

@allure.id("REQ-1002")
@allure.title("Requirements Explorer Tree Selection")
@allure.link("http://localhost:5173/#/requirements/REQ-1002", name="Requirement REQ-1002")
def test_requirements_tree_selection():
    """
    Given a hierarchical Requirements Explorer tree
    When a PM selects a requirement node
    Then the detail panel displays linked BDD test cases and execution status
    """
    # Test implementation
    ...
```

---

## Test Execution Commands

Run full test suite:
```bash
pytest -v --alluredir=allure-results
```

Run specific test tier:
```bash
pytest tests/unit/
pytest tests/api/
pytest tests/integration/
pytest tests/system/
pytest tests/e2e/
```
