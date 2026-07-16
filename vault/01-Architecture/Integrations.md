# Integrations

Provable supports external tool syncing through integrations located in `backend/integrations/`. These clients bridge Provable's local SQLite database with Jira, StrictDoc, and Allure.

## 1. StrictDoc Client (`strictdoc_client.py`)
[StrictDoc](https://github.com/strictdoc-project/strictdoc) is a requirements engineering tool that uses text-based `.sdoc` specification files.
- **Path**: Syncs with `workspace/requirements/requirements.sdoc`.
- **Sync Direction**: Bidirectional.
  - **Import**: `sync_sdoc_to_db()` parses `.sdoc` requirement blocks on startup and inserts/updates them in SQLite.
  - **Export**: `export_sdoc()` is triggered on DataStore changes, rewriting the `.sdoc` file with updated node properties (like title, description, parent ID, priority).
- **Format**: Parses documents using custom tag-matching (`[REQUIREMENT]`, `[SECTION]`, `UID:`, `STATEMENT:`, `RELATIONS:`).

## 2. Jira Client (`jira_client.py`)
Provides issue tracking capabilities by mapping SQLite requirements and bugs to Atlassian Jira.
- **Triggers**: Runs status updates asynchronously on task completion, transition to code review, and merge events.
- **Endpoints**:
  - `sync_jira_to_db()`: Pulls tickets and issues from the configured Jira board, importing them as Backlog items.
  - `update_ticket_status(jira_key, status)`: Transitions Jira tickets dynamically when tasks move between Kanban columns (`In Progress`, `Review`, `Done`).
- **Configuration**: Mapped via `backend/config/integrations.yaml`.

## 3. Allure Client (`allure_client.py`)
Allure is an industry-standard test reporting portal.
- **Project Setup**: Backend attempts to auto-initialize the `provable` project on startup:
  ```python
  requests.post("http://localhost:5050/projects", json={"id": "provable"})
  ```
- **Result Output**: Pytest execution outputs allure-compatible results into `workspace/allure-results/`.
- **Dashboard**: The frontend Test Suite tab embeds Allure live dashboards when loaded, displaying execution timelines, suites, and coverage analytics.
