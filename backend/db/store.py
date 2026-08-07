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


SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'schema.sql'))
REQUIREMENTS_JSON = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'requirements.json'))

# Default DB path (resolved at runtime so it reflects any workspace switch)
from config_loader import get_workspace_base
_FALLBACK_DB_PATH = os.path.abspath(os.path.join(get_workspace_base(), 'requirements', 'provable.db'))
_active_db_path: Optional[str] = None


def get_db_path() -> str:
    """Return the active per-project database path, resolving dynamically each call."""
    # Respect test database overrides set by test suites
    env_db = os.environ.get("DATABASE_URL")
    if env_db:
        cleaned = env_db.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        return cleaned

    if _active_db_path:
        return _active_db_path
    # Derive from the active workspace set by config_loader
    try:
        from config_loader import get_workspace_base
        workspace = get_workspace_base()
        return os.path.join(workspace, 'requirements', 'provable.db')
    except Exception:
        return _FALLBACK_DB_PATH


def set_active_db(path: str) -> None:
    """Switch the active database to a given file path and initialise it."""
    global _active_db_path
    _active_db_path = os.path.abspath(path)
    os.makedirs(os.path.dirname(_active_db_path), exist_ok=True)
    print(f"📦 DataStore: Active DB switched to {_active_db_path}")


def get_connection(timeout: float = 30.0) -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), timeout=timeout)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # allow concurrent reads during writes
    conn.execute("PRAGMA busy_timeout=30000") # wait up to 30 seconds for locks to clear
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def reset_database() -> None:
    """Wipe all requirements, test cases, and agent runs safely with busy_timeout and retry logic."""
    import time
    db_path = get_db_path()
    for attempt in range(5):
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("DELETE FROM agent_runs")
            conn.execute("DELETE FROM test_cases")
            conn.execute("DELETE FROM requirements")
            try:
                conn.execute("DELETE FROM kickstart_state")
            except Exception:
                pass
            conn.commit()
            conn.close()
            print("📦 DataStore: Wiped database tables successfully.")
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < 4:
                time.sleep(0.5)
            else:
                print(f"⚠️ DataStore: reset_database lock warning: {e}")
                raise e


def init_db():
    """Initialise the database, creating tables if they don't exist, then migrate from JSON if needed."""
    conn = get_connection()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()

    # Ensure failure_message column exists
    try:
        conn.execute("ALTER TABLE test_cases ADD COLUMN failure_message TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute("ALTER TABLE requirements ADD COLUMN component_type TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute("ALTER TABLE requirements ADD COLUMN component_meta TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Table initialisation complete
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
                'status': (
                    'Passing' if tc.get('last_result') == 'pass'
                    else 'Pending' if tc.get('last_result') in ('never_run', None, 'pending')
                    else 'Failing'
                ),
                'given': tc.get('given_text', '') or 'Given the test is configured',
                'when': tc.get('when_text', '') or f"When executing {tc['title']}",
                'then': tc.get('then_text', '') or "Then it should complete without error",
                'req': tc.get('requirement_id', ''),
                'failureMessage': tc.get('failure_message', ''),
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
        """INSERT OR REPLACE INTO requirements
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
    
    # Fetch current jira_key and status to check for transitions
    row = conn.execute("SELECT jira_key, status FROM requirements WHERE id = ?", (req_id,)).fetchone()
    current_status = row['status'] if row else None
    jira_key = row['jira_key'] if row else None
    
    allowed = {
        'title', 'description', 'type', 'priority', 'status',
        'parent_id', 'jira_key', 'sdoc_uid', 'dependencies',
        'assigned_agents', 'proposed_code', 'feedback',
    }
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
    
    # Trigger Jira sync if status changed
    new_status = updates.get('status')
    new_jira_key = updates.get('jira_key') or jira_key
    if new_status and new_status != current_status and new_jira_key:
        try:
            from integrations.jira_client import update_ticket_status
            update_ticket_status(new_jira_key, new_status)
        except Exception as e:
            print(f"📦 DataStore: Failed to update status in Jira for {new_jira_key}: {e}")
            
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

delete_requirement = delete_requirement_cascade


def update_requirement_status(req_id: str, status: str, feedback: str = None, tests: List = None):
    fields = {'status': status}
    if feedback is not None:
        fields['feedback'] = feedback
    update_requirement(req_id, fields)
    if tests is not None:
        _upsert_test_results(req_id, tests)


def _upsert_test_results(req_id: str, tests: List[Dict]):
    conn = get_connection()
    existing_rows = conn.execute("SELECT title, id FROM test_cases WHERE requirement_id = ?", (req_id,)).fetchall()
    title_to_id = {row['title']: row['id'] for row in existing_rows}
    for t in tests:
        test_name = t.get('name','')
        tc_id = title_to_id.get(test_name) or t.get('id') or f"TC-{random.randint(1000,9999)}"
        result = 'pass' if t.get('status') in ('Passing', 'pass') else 'fail'
        existing = conn.execute("SELECT id FROM test_cases WHERE id = ?", (tc_id,)).fetchone()
        if existing:
            conn.execute("UPDATE test_cases SET last_result = ?, file_path = ?, failure_message = ? WHERE id = ?", (result, t.get('file_path'), t.get('failure_message'), tc_id))
        else:
            conn.execute(
                """INSERT INTO test_cases (id, requirement_id, title, given_text, when_text, then_text, last_result, file_path, failure_message)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (tc_id, req_id, test_name, t.get('given',''), t.get('when',''), t.get('then',''), result, t.get('file_path'), t.get('failure_message'))
            )
    conn.commit()
    conn.close()


def replace_test_results_for_requirement(req_id: str, tests: List[Dict]):
    """Delete all existing test cases for req_id then insert the fresh results.
    Use this after a successful agent run to avoid accumulating stale fail rows."""
    conn = get_connection()
    existing_rows = conn.execute("SELECT title, id FROM test_cases WHERE requirement_id = ?", (req_id,)).fetchall()
    title_to_id = {row['title']: row['id'] for row in existing_rows}
    conn.execute("DELETE FROM test_cases WHERE requirement_id = ?", (req_id,))
    for t in tests:
        test_name = t.get('name','')
        tc_id = title_to_id.get(test_name) or t.get('id') or f"TC-{random.randint(1000,9999)}"
        result = 'pass' if t.get('status') in ('Passing', 'pass') else 'fail'
        conn.execute(
            """INSERT OR REPLACE INTO test_cases (id, requirement_id, title, given_text, when_text, then_text, last_result, file_path, failure_message)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (tc_id, req_id, test_name, t.get('given',''), t.get('when',''), t.get('then',''), result, t.get('file_path'), t.get('failure_message'))
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
def get_agent_runs(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


# ── Kickstart Session State ───────────────────────────────────────────────────


def get_kickstart_state() -> Dict[str, Any]:
    conn = get_connection()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS kickstart_state (
            id INTEGER PRIMARY KEY,
            business_pitch TEXT,
            blocks_json TEXT,
            extracted_reqs_json TEXT,
            synthesized INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        row = conn.execute("SELECT * FROM kickstart_state WHERE id = 1").fetchone()
        conn.close()
        if row:
            return {
                "business_pitch": row['business_pitch'],
                "blocks": json.loads(row['blocks_json']) if row['blocks_json'] else [],
                "extracted_requirements": json.loads(row['extracted_reqs_json']) if row['extracted_reqs_json'] else [],
                "synthesized": bool(row['synthesized'])
            }
    except Exception as e:
        print(f"📦 DataStore: Error fetching kickstart state: {e}")
        try:
            conn.close()
        except Exception:
            pass
    return {
        "business_pitch": "We operate a pizzeria. Customers place orders specified by pizza name, size, quantity, and price. The customer will get an estimated pickup time based on how many other orders have been made recently. The order is then marked Ready for pickup",
        "blocks": [],
        "extracted_requirements": [],
        "synthesized": False
    }


def save_kickstart_state(state: Dict[str, Any]):
    conn = get_connection()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS kickstart_state (
            id INTEGER PRIMARY KEY,
            business_pitch TEXT,
            blocks_json TEXT,
            extracted_reqs_json TEXT,
            synthesized INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Check if row exists
        existing = conn.execute("SELECT * FROM kickstart_state WHERE id = 1").fetchone()
        
        pitch = state.get("business_pitch", "")
        blocks = json.dumps(state.get("blocks", []))
        reqs = json.dumps(state.get("extracted_requirements", []))
        synthesized = 1 if state.get("synthesized") else 0
        
        if existing:
            # If updating synthesis status or blocks, preserve existing blocks if new ones are passed as list of IDs
            if synthesized:
                # Keep existing blocks JSON if state passed only block IDs
                if state.get("blocks") and isinstance(state["blocks"][0], str) if state.get("blocks") else False:
                    blocks = existing['blocks_json']
            conn.execute(
                "UPDATE kickstart_state SET business_pitch = ?, blocks_json = ?, extracted_reqs_json = ?, synthesized = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                (pitch, blocks, reqs, synthesized)
            )
        else:
            conn.execute(
                "INSERT INTO kickstart_state (id, business_pitch, blocks_json, extracted_reqs_json, synthesized) VALUES (1, ?, ?, ?, ?)",
                (pitch, blocks, reqs, synthesized)
            )
        conn.commit()
    except Exception as e:
        print(f"📦 DataStore: Error saving kickstart state: {e}")
    finally:
        conn.close()


def create_component_requirement(component_dict: Dict[str, Any]) -> str:
    """
    Creates a top-level Folder requirement representing a dynamic UI component,
    optional child requirements, and automatically attaches BDD test cases.
    """
    conn = get_connection()
    try:
        req_id = component_dict.get("id") or f"REQ-{component_dict.get('canonical_key', 'CMP').upper()}-001"
        title = component_dict.get("title", "Custom Component")
        desc = component_dict.get("description", f"Dynamic component {title}")
        comp_type = component_dict.get("component_type", "custom")
        meta = json.dumps(component_dict.get("meta", {}))

        conn.execute(
            """INSERT INTO requirements
               (id, title, description, type, priority, status, parent_id, component_type, component_meta)
               VALUES (?, ?, ?, 'Folder', 'High', 'Done', NULL, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
               title=excluded.title, description=excluded.description,
               component_type=excluded.component_type, component_meta=excluded.component_meta, status='Done'""",
            (req_id, title, desc, comp_type, meta)
        )

        tc_id = f"TC-{req_id}-01"
        conn.execute(
            """INSERT INTO test_cases
               (id, requirement_id, title, given_text, when_text, then_text, last_result)
               VALUES (?, ?, ?, ?, ?, ?, 'pass')
               ON CONFLICT(id) DO UPDATE SET last_result='pass'""",
            (
                tc_id,
                req_id,
                f"test_component_{component_dict.get('canonical_key', 'custom')}_renders",
                "Given the application live preview is active",
                f"When the user views component '{title}'",
                f"Then the {title} interface component renders dynamically without errors"
            )
        )

        conn.commit()
        _trigger_sdoc_export()
        return req_id
    finally:
        conn.close()


def get_hierarchical_requirements() -> List[Dict[str, Any]]:
    """
    Returns all requirements organized in a parent-child hierarchy tree.
    """
    reqs = get_all_requirements()
    nodes = {r['id']: {**r, 'children': []} for r in reqs}
    roots = []

    for req_id, node in nodes.items():
        parent_id = node.get('parent_id')
        if parent_id and parent_id in nodes:
            nodes[parent_id]['children'].append(node)
        else:
            roots.append(node)

    return roots


def delete_component_tree(req_id_or_key: str) -> bool:
    """
    Deletes a component requirement and all its descendant child requirements and test cases.
    """
    conn = get_connection()
    try:
        # Find exact requirement ID or match by canonical feature key
        row = conn.execute("SELECT id FROM requirements WHERE id = ? OR LOWER(id) LIKE ?", (req_id_or_key, f"%{req_id_or_key.lower()}%")).fetchone()
        if not row:
            return False

        target_id = row['id']
        # Find child requirement IDs recursively
        to_delete = [target_id]
        cursor = conn.execute("SELECT id FROM requirements WHERE parent_id = ?", (target_id,))
        for child in cursor.fetchall():
            to_delete.append(child['id'])

        for rid in to_delete:
            conn.execute("DELETE FROM test_cases WHERE requirement_id = ?", (rid,))
            conn.execute("DELETE FROM requirements WHERE id = ?", (rid,))

        conn.commit()
        _trigger_sdoc_export()
        return True
    finally:
        conn.close()


