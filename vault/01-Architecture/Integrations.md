# Integrations Engine & Data Formats

Provable supports external tool syncing through integrations located in `backend/integrations/`. These clients bridge Provable's local SQLite database with StrictDoc, Jira, and Allure.

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

## 2. Jira Client (`jira_client.py`)

Maps SQLite requirements and bugs to Atlassian Jira tickets.

### Configuration (`backend/config/integrations.yaml`)
```yaml
jira:
  enabled: true
  server: "https://your-domain.atlassian.net"
  email_env: "JIRA_EMAIL"
  api_token_env: "JIRA_API_TOKEN"
  project_key: "PROV"

status_mapping:
  Backlog: "To Do"
  In Progress: "In Progress"
  Review: "In Review"
  Done: "Done"
```

---

## 3. Allure Client (`allure_client.py`)

Allure Docker Service API client.
- **Base URL**: `http://localhost:5050`
- **Endpoints**:
  - `POST /projects`: Registers project ID `provable`.
  - `POST /send-results?project_id=provable`: Uploads pytest JSON results from `workspace/allure-results/`.
  - `GET /generate-report?project_id=provable`: Triggers HTML report rendering.
