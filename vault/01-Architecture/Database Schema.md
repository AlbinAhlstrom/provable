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

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original database schema intended for a purely relational domain representation. The current store.py stores serialized JSON blobs in text columns (`component_meta`, `custom_fixtures_json`, `entity_schemas_json`) to accommodate rapid prototype evolution. A normalized SQL schema for domain entities and attributes provides superior relational integrity.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Backend REST API]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]

