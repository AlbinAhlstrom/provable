"""
DataStore — SQLite-backed data access layer.
Replaces all direct requirements.json reads/writes.
"""
import sqlite3
import json
import os
import random
from typing import List, Optional, Dict, Any

def _trigger_sdoc_export():
    try:
        from integrations.strictdoc_client import export_sdoc
        export_sdoc()
    except Exception as e:
        print(f"📦 DataStore: Failed to export SDoc: {e}")


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'provable.db'))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'schema.sql'))
REQUIREMENTS_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'requirements.json'))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # allow concurrent reads during writes
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialise the database, creating tables if they don't exist, then migrate from JSON if needed."""
    conn = get_connection()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()

    # One-time migration from requirements.json
    cursor = conn.execute("SELECT COUNT(*) FROM requirements")
    if cursor.fetchone()[0] == 0 and os.path.exists(REQUIREMENTS_JSON):
        _migrate_from_json(conn)

    conn.close()


def _migrate_from_json(conn: sqlite3.Connection):
    """Migrate existing requirements.json data into SQLite on first startup."""
    print("📦 DataStore: Migrating requirements.json → SQLite...")
    try:
        with open(REQUIREMENTS_JSON, 'r') as f:
            reqs = json.load(f)
        for r in reqs:
            conn.execute(
                """INSERT OR IGNORE INTO requirements
                   (id, title, description, type, priority, status, parent_id,
                    dependencies, assigned_agents, proposed_code, feedback)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    r.get('id'),
                    r.get('title', ''),
                    r.get('description', ''),
                    r.get('type'),
                    r.get('priority', 'Med'),
                    r.get('status', 'Backlog'),
                    r.get('parentId'),
                    json.dumps(r.get('dependencies', [])),
                    json.dumps(r.get('assignedAgents', [])),
                    r.get('proposedCode'),
                    r.get('feedback', ''),
                )
            )
            # Migrate test cases
            for t in r.get('tests', []):
                tc_id = t.get('id') or f"TC-{random.randint(1000,9999)}"
                conn.execute(
                    """INSERT OR IGNORE INTO test_cases
                       (id, requirement_id, title, given_text, when_text, then_text, last_result)
                       VALUES (?,?,?,?,?,?,?)""",
                    (
                        tc_id,
                        r.get('id'),
                        t.get('name') or t.get('title', ''),
                        t.get('given', ''),
                        t.get('when', ''),
                        t.get('then', ''),
                        'pass' if t.get('status') == 'Passing' else 'fail',
                    )
                )
        conn.commit()
        print(f"📦 DataStore: Migrated {len(reqs)} requirements from JSON.")
    except Exception as e:
        print(f"📦 DataStore: Migration failed: {e}")


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    # Parse JSON fields
    for field in ('dependencies', 'assigned_agents', 'stages_json'):
        if field in d and d[field]:
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    return d


# ── Requirements ─────────────────────────────────────────────────────────────

def get_all_requirements() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM requirements ORDER BY created_at").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_requirement(req_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM requirements WHERE id = ?", (req_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_requirements_for_frontend() -> List[Dict]:
    """Return requirements in the shape the frontend App.tsx expects (camelCase fields)."""
    reqs = get_all_requirements()
    test_cases = get_all_test_cases()
    tc_by_req: Dict[str, List] = {}
    for tc in test_cases:
        rid = tc.get('requirement_id')
        if rid:
            tc_by_req.setdefault(rid, []).append({
                'id': tc['id'],
                'name': tc['title'],
                'title': tc['title'],
                'status': 'Passing' if tc.get('last_result') == 'pass' else 'Failing',
                'given': tc.get('given_text', ''),
                'when': tc.get('when_text', ''),
                'then': tc.get('then_text', ''),
                'req': tc.get('requirement_id', ''),
            })
    result = []
    for r in reqs:
        result.append({
            'id': r['id'],
            'title': r['title'],
            'description': r['description'],
            'type': r.get('type'),
            'priority': r.get('priority', 'Med'),
            'status': r['status'],
            'parentId': r.get('parent_id'),
            'jiraKey': r.get('jira_key'),
            'dependencies': r.get('dependencies', []),
            'assignedAgents': r.get('assigned_agents', []),
            'proposedCode': r.get('proposed_code'),
            'feedback': r.get('feedback', ''),
            'tests': tc_by_req.get(r['id'], []),
        })
    return result


def create_requirement(data: Dict) -> Dict:
    conn = get_connection()
    req_id = data.get('id') or f"REQ-{random.randint(1000, 9999)}"
    conn.execute(
        """INSERT INTO requirements
           (id, title, description, type, priority, status, parent_id,
            dependencies, assigned_agents, proposed_code, feedback)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            req_id,
            data.get('title', ''),
            data.get('description', ''),
            data.get('type', 'Requirement'),
            data.get('priority', 'Med'),
            data.get('status', 'Backlog'),
            data.get('parentId') or data.get('parent_id'),
            json.dumps(data.get('dependencies', [])),
            json.dumps(data.get('assignedAgents', data.get('assigned_agents', []))),
            data.get('proposedCode') or data.get('proposed_code'),
            data.get('feedback', ''),
        )
    )
    conn.commit()
    conn.close()
    _trigger_sdoc_export()
    return get_requirement(req_id)


def update_requirement(req_id: str, fields: Dict) -> Optional[Dict]:
    conn = get_connection()
    allowed = {
        'title', 'description', 'type', 'priority', 'status',
        'parent_id', 'jira_key', 'sdoc_uid', 'dependencies',
        'assigned_agents', 'proposed_code', 'feedback',
    }
    # Accept camelCase from frontend
    camel_map = {
        'parentId': 'parent_id', 'jiraKey': 'jira_key', 'sdocUid': 'sdoc_uid',
        'assignedAgents': 'assigned_agents', 'proposedCode': 'proposed_code',
    }
    updates = {}
    for k, v in fields.items():
        col = camel_map.get(k, k)
        if col in allowed:
            if col in ('dependencies', 'assigned_agents') and isinstance(v, list):
                v = json.dumps(v)
            updates[col] = v

    if not updates:
        conn.close()
        return get_requirement(req_id)

    set_clause = ', '.join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [req_id]
    conn.execute(f"UPDATE requirements SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()
    _trigger_sdoc_export()
    return get_requirement(req_id)


def delete_requirement_cascade(req_id: str):
    conn = get_connection()
    # Cascade: also delete children
    children = conn.execute("SELECT id FROM requirements WHERE parent_id = ?", (req_id,)).fetchall()
    conn.close()
    for child in children:
        delete_requirement_cascade(child['id'])  # recursive
    conn = get_connection()
    conn.execute("DELETE FROM test_cases WHERE requirement_id = ?", (req_id,))
    conn.execute("DELETE FROM requirements WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    _trigger_sdoc_export()


def update_requirement_status(req_id: str, status: str, feedback: str = None, tests: List = None):
    fields = {'status': status}
    if feedback is not None:
        fields['feedback'] = feedback
    update_requirement(req_id, fields)
    if tests is not None:
        _upsert_test_results(req_id, tests)


def _upsert_test_results(req_id: str, tests: List[Dict]):
    conn = get_connection()
    for t in tests:
        tc_id = t.get('id') or f"TC-{random.randint(1000,9999)}"
        result = 'pass' if t.get('status') == 'Passing' else 'fail'
        existing = conn.execute("SELECT id FROM test_cases WHERE id = ?", (tc_id,)).fetchone()
        if existing:
            conn.execute("UPDATE test_cases SET last_result = ? WHERE id = ?", (result, tc_id))
        else:
            conn.execute(
                """INSERT INTO test_cases (id, requirement_id, title, given_text, when_text, then_text, last_result)
                   VALUES (?,?,?,?,?,?,?)""",
                (tc_id, req_id, t.get('name',''), t.get('given',''), t.get('when',''), t.get('then',''), result)
            )
    conn.commit()
    conn.close()


def get_backlog_tasks() -> List[Dict]:
    """Return all Task/Bug items in Backlog status."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM requirements WHERE status = 'Backlog' AND type IN ('Task', 'Bug') ORDER BY created_at"
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_children(parent_id: str) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM requirements WHERE parent_id = ?", (parent_id,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


# ── Test Cases ────────────────────────────────────────────────────────────────

def get_all_test_cases() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM test_cases ORDER BY created_at").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_test_cases_for_requirement(req_id: str) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM test_cases WHERE requirement_id = ?", (req_id,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


# ── Agent Runs ────────────────────────────────────────────────────────────────

def create_agent_run(ticket_id: str, requirement_id: str = None, jira_key: str = None) -> str:
    import uuid
    run_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    conn.execute(
        """INSERT INTO agent_runs (id, ticket_id, requirement_id, jira_key, status, started_at)
           VALUES (?,?,?,?,'running', CURRENT_TIMESTAMP)""",
        (run_id, ticket_id, requirement_id, jira_key)
    )
    conn.commit()
    conn.close()
    return run_id


def update_agent_run(run_id: str, status: str = None, attempts: int = None, stages: List = None):
    conn = get_connection()
    updates = {}
    if status:
        updates['status'] = status
    if attempts is not None:
        updates['attempts'] = attempts
    if stages is not None:
        updates['stages_json'] = json.dumps(stages)
    if not updates:
        conn.close()
        return

    # Handle completed_at automatically on terminal status
    set_parts = []
    values = []
    for k, v in updates.items():
        set_parts.append(f"{k} = ?")
        values.append(v)

    if status in ('success', 'failed', 'cancelled'):
        set_parts.append("completed_at = CURRENT_TIMESTAMP")

    values.append(run_id)
    conn.execute(f"UPDATE agent_runs SET {', '.join(set_parts)} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_agent_runs(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]
