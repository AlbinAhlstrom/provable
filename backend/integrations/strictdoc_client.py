"""
StrictDoc Client — Handles parsing, generating, and syncing .sdoc files.
Requirements are stored in git-versioned `workspace/requirements/requirements.sdoc`.
"""
import os
import re
import db.store as store
from typing import List, Dict, Any
from config_loader import get_workspace_base

def get_sdoc_path() -> str:
    return os.path.abspath(os.path.join(get_workspace_base(), 'requirements', 'requirements.sdoc'))


def _slugify_section_title(title: str) -> str:
    """Convert a section title to a stable, DB-safe ID.  e.g. 'Game Board UI' → 'FOLDER-game-board-ui'"""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.strip()).strip('-').lower()
    return f"FOLDER-{slug}"


def parse_sdoc(file_path: str) -> List[Dict[str, Any]]:
    """Parse an .sdoc file into a list of requirement/folder dicts.

    [SECTION] blocks are emitted as Folder rows.  Every [REQUIREMENT] inside
    a section gets its parent_id set to that section's folder ID, building
    the full nested tree structure.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ── First pass: extract raw blocks ──────────────────────────────────────
    # Each entry is either a section event or a requirement dict
    events: List[Dict] = []        # {'kind': 'section_open'/'section_close'/'req', ...}
    current_req: Optional[Dict] = None
    current_field: Optional[str] = None
    current_content: List[str] = []

    for line in lines:
        stripped = line.strip()

        if stripped == "[SECTION]":
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                events.append({'kind': 'req', 'data': current_req})
                current_req = None
            current_field = None
            current_content = []
            # The next TITLE: line will name this section
            events.append({'kind': 'section_open', 'title': None})
            continue

        if stripped == "[/SECTION]":
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                events.append({'kind': 'req', 'data': current_req})
                current_req = None
            current_field = None
            current_content = []
            events.append({'kind': 'section_close'})
            continue

        if stripped in ("[DOCUMENT]", "[TASK]"):
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                events.append({'kind': 'req', 'data': current_req})
                current_req = None
            current_field = None
            current_content = []
            if stripped == "[TASK]":
                current_req = {"type": "Task"}
            continue

        if stripped == "[REQUIREMENT]":
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                events.append({'kind': 'req', 'data': current_req})
            current_req = {"type": "Requirement"}
            current_field = None
            current_content = []
            continue

        # Capture TITLE for a pending section_open
        if events and events[-1]['kind'] == 'section_open' and events[-1]['title'] is None:
            m = re.match(r'^TITLE:\s*(.*)', stripped)
            if m:
                events[-1]['title'] = m.group(1).strip()
                continue

        if current_req is None:
            continue

        # Key: value inside a block
        match = re.match(r"^([A-Z_]+):\s*(.*)", line)
        if match:
            if current_field:
                current_req[current_field] = "\n".join(current_content).strip()
            current_field = match.group(1).lower()
            current_content = [match.group(2)]
        else:
            current_content.append(line.rstrip('\n'))

    if current_req:
        if current_field:
            current_req[current_field] = "\n".join(current_content).strip()
        events.append({'kind': 'req', 'data': current_req})

    # ── Second pass: walk events with a section stack ────────────────────────
    # Stack entries: {'id': folder_id, 'title': title, 'parent_id': ...}
    section_stack: List[Dict] = []
    processed: List[Dict[str, Any]] = []
    seen_folder_ids: set = set()

    for event in events:
        if event['kind'] == 'section_open':
            title = event.get('title') or 'Untitled'
            folder_id = _slugify_section_title(title)

            # Make ID unique if the same title appears at different nesting levels
            base_id = folder_id
            counter = 1
            while folder_id in seen_folder_ids:
                folder_id = f"{base_id}-{counter}"
                counter += 1
            seen_folder_ids.add(folder_id)

            parent_id = section_stack[-1]['id'] if section_stack else None
            section_stack.append({'id': folder_id, 'title': title, 'parent_id': parent_id})

            processed.append({
                'id': folder_id,
                'title': title,
                'description': '',
                'type': 'Folder',
                'priority': 'Med',
                'status': 'Backlog',
                'parent_id': parent_id,
                'jira_key': None,
                'sdoc_uid': folder_id,
                'test_file': None,
            })

        elif event['kind'] == 'section_close':
            if section_stack:
                section_stack.pop()

        elif event['kind'] == 'req':
            req = event['data']
            uid = req.get('uid')
            if not uid:
                continue

            # Determine parent: innermost section on the stack
            parent_id = section_stack[-1]['id'] if section_stack else None

            # Parse RELATIONS block for additional overrides
            relations_str = req.get('relations', '')
            rel_parent_id = None
            test_file = None
            if relations_str:
                current_rel_type = None
                for rline in relations_str.split('\n'):
                    rline_strip = rline.strip()
                    if rline_strip.startswith('- TYPE:'):
                        current_rel_type = rline_strip.replace('- TYPE:', '').strip()
                    elif rline_strip.startswith('VALUE:') and current_rel_type:
                        val = rline_strip.replace('VALUE:', '').strip()
                        if current_rel_type.lower() == 'parent':
                            rel_parent_id = val
                        elif current_rel_type.lower() == 'file':
                            test_file = val
                        current_rel_type = None

            # RELATIONS Parent overrides section nesting only if explicitly set
            effective_parent = rel_parent_id or parent_id

            processed.append({
                'id': uid,
                'title': req.get('title', ''),
                'description': req.get('statement', ''),
                'type': req.get('req_type', req.get('type', 'Requirement')),
                'priority': req.get('priority', 'Med'),
                'status': req.get('status', 'Backlog'),
                'parent_id': effective_parent,
                'jira_key': req.get('jira_key'),
                'sdoc_uid': uid,
                'test_file': test_file,
            })

    return processed



def generate_sdoc_content(requirements: List[Dict[str, Any]]) -> str:
    """Generate the contents of an .sdoc file from requirement records."""
    lines = [
        "[DOCUMENT]",
        "TITLE: Provable System Requirements",
        ""
    ]
    
    for r in requirements:
        # Exclude pure Folders if Strictdoc shouldn't track them as requirements
        if r.get('type') == 'Folder':
            continue
            
        lines.append("[REQUIREMENT]")
        lines.append(f"UID: {r['id']}")
        lines.append(f"TITLE: {r.get('title', '')}")
        
        # Format statement/description
        statement = r.get('description', '')
        lines.append(f"STATEMENT: {statement}")
        
        # Custom attributes for Provable state tracking
        lines.append(f"REQ_TYPE: {r.get('type', 'Requirement')}")
        lines.append(f"PRIORITY: {r.get('priority', 'Med')}")
        lines.append(f"STATUS: {r.get('status', 'Backlog')}")
        if r.get('jira_key'):
            lines.append(f"JIRA_KEY: {r['jira_key']}")
            
        # Relations block (Parent and Test File links)
        relations = []
        if r.get('parent_id') and r.get('parent_id') != 'None':
            relations.append("- TYPE: Parent")
            relations.append(f"  VALUE: {r['parent_id']}")
            
        # Check if there is an associated test case
        tcs = store.get_test_cases_for_requirement(r['id'])
        if tcs:
            for tc in tcs:
                if tc.get('file_path'):
                    relations.append("- TYPE: File")
                    relations.append(f"  VALUE: {tc['file_path']}")
                    
        if relations:
            lines.append("RELATIONS:")
            for rel in relations:
                lines.append(f"  {rel}")
                
        lines.append("") # empty line spacing
        
    return "\n".join(lines)


def export_sdoc():
    """Export SQLite requirement data to requirements.sdoc."""
    reqs = store.get_all_requirements()
    content = generate_sdoc_content(reqs)
    
    os.makedirs(os.path.dirname(get_sdoc_path()), exist_ok=True)
    with open(get_sdoc_path(), 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 strictdoc_client: Exported requirements to {get_sdoc_path()}")


def sync_sdoc_to_db(clear_first: bool = False):
    """Sync workspace/requirements/requirements.sdoc into SQLite database.

    Args:
        clear_first: If True, DELETE all existing requirements and test_cases before
                     re-importing. Use this on project switch to prevent stale rows
                     from the previous project appearing in the Kanban board.
    """
    if not os.path.exists(get_sdoc_path()):
        os.makedirs(os.path.dirname(get_sdoc_path()), exist_ok=True)
        with open(get_sdoc_path(), 'w', encoding='utf-8') as f:
            f.write('[DOCUMENT]\nTITLE: System Architecture & Business Requirements\n')
        return

    print(f"📄 strictdoc_client: Syncing {get_sdoc_path()} → SQLite...")
    parsed_reqs = parse_sdoc(get_sdoc_path())

    conn = store.get_connection()
    try:
        if clear_first:
            if parsed_reqs:
                sdoc_ids = [r['id'] for r in parsed_reqs]
                placeholders = ', '.join('?' for _ in sdoc_ids)
                conn.execute(f"DELETE FROM test_cases WHERE requirement_id NOT IN ({placeholders})", sdoc_ids)
                conn.execute(f"DELETE FROM requirements WHERE id NOT IN ({placeholders})", sdoc_ids)
                conn.commit()
                print("📄 strictdoc_client: Cleaned up stale requirements and associated test cases.")
            else:
                conn.execute("DELETE FROM test_cases")
                conn.execute("DELETE FROM requirements")
                conn.commit()
                print("📄 strictdoc_client: Purged all requirements and test cases from SQLite.")

        for r in parsed_reqs:
            # Check if it exists in SQLite
            existing = conn.execute("SELECT id FROM requirements WHERE id = ?", (r['id'],)).fetchone()
            if existing:
                conn.execute(
                    """UPDATE requirements SET
                       title = ?, description = ?, type = ?, priority = ?, status = ?,
                       parent_id = ?, jira_key = ?, sdoc_uid = ?
                       WHERE id = ?""",
                    (
                        r['title'],
                        r['description'],
                        r['type'],
                        r['priority'],
                        r['status'],
                        r['parent_id'],
                        r['jira_key'],
                        r['sdoc_uid'],
                        r['id']
                    )
                )
            else:
                conn.execute(
                    """INSERT INTO requirements
                       (id, title, description, type, priority, status, parent_id, jira_key, sdoc_uid)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (
                        r['id'],
                        r['title'],
                        r['description'],
                        r['type'],
                        r['priority'],
                        r['status'],
                        r['parent_id'],
                        r['jira_key'],
                        r['sdoc_uid']
                    )
                )
            
            # Sync test case file path reference if present — INSERT row if missing
            if r.get('test_file'):
                tc_id = f"TC-FILE-{r['id']}"
                existing_tc = conn.execute(
                    "SELECT id FROM test_cases WHERE requirement_id = ? AND file_path = ?",
                    (r['id'], r['test_file'])
                ).fetchone()
                if not existing_tc:
                    conn.execute(
                        """INSERT OR IGNORE INTO test_cases
                           (id, requirement_id, title, file_path, last_result)
                           VALUES (?, ?, ?, ?, ?)""",
                        (tc_id, r['id'], f"Linked test: {os.path.basename(r['test_file'])}", r['test_file'], 'never_run')
                    )
                else:
                    conn.execute(
                        "UPDATE test_cases SET file_path = ? WHERE requirement_id = ?",
                        (r['test_file'], r['id'])
                    )
                
        conn.commit()
        print(f"📄 strictdoc_client: Synced {len(parsed_reqs)} requirements successfully.")
    except Exception as e:
        print(f"📄 strictdoc_client: Sync failed: {e}")
    finally:
        conn.close()
