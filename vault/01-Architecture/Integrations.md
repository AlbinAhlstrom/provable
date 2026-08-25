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
