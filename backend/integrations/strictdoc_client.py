"""
StrictDoc Client — Handles parsing, generating, and syncing .sdoc files.
Requirements are stored in git-versioned `workspace/requirements/requirements.sdoc`.
"""
import os
import re
import db.store as store
from typing import List, Dict, Any

SDOC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'workspace', 'requirements', 'requirements.sdoc'))


def parse_sdoc(file_path: str) -> List[Dict[str, Any]]:
    """Parse an .sdoc file into a list of requirement dicts."""
    if not os.path.exists(file_path):
        return []

    requirements = []
    current_req = None
    current_field = None
    current_content = []
    
    # We parse [DOCUMENT], [SECTION], and [REQUIREMENT] blocks
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        
        # Check block tags
        if stripped == "[REQUIREMENT]":
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                requirements.append(current_req)
            current_req = {"type": "Requirement"}
            current_field = None
            current_content = []
            continue
        elif stripped in ("[DOCUMENT]", "[SECTION]", "[/SECTION]"):
            if current_req:
                if current_field:
                    current_req[current_field] = "\n".join(current_content).strip()
                requirements.append(current_req)
                current_req = None
            current_field = None
            current_content = []
            continue

        if current_req is None:
            continue

        # Inside [REQUIREMENT] block, match keys
        match = re.match(r"^([A-Z_]+):\s*(.*)", line)
        if match:
            # Save previous field if any
            if current_field:
                current_req[current_field] = "\n".join(current_content).strip()
            
            key = match.group(1)
            val = match.group(2)
            
            current_field = key.lower()
            current_content = [val]
        else:
            # Continuation of multi-line field
            current_content.append(line.rstrip('\n'))

    if current_req:
        if current_field:
            current_req[current_field] = "\n".join(current_content).strip()
        requirements.append(current_req)

    # Process relations and fields for each parsed requirement
    processed = []
    for req in requirements:
        uid = req.get("uid")
        if not uid:
            continue

        # Parse STATEMENT from statement attribute
        statement = req.get("statement", "")
        
        # Parse RELATIONS block if present
        relations_str = req.get("relations", "")
        parent_id = None
        test_file = None
        
        # Simple relations parser
        if relations_str:
            rel_lines = relations_str.split("\n")
            current_rel_type = None
            for rline in rel_lines:
                rline_strip = rline.strip()
                if rline_strip.startswith("- TYPE:"):
                    current_rel_type = rline_strip.replace("- TYPE:", "").strip()
                elif rline_strip.startswith("VALUE:") and current_rel_type:
                    val = rline_strip.replace("VALUE:", "").strip()
                    if current_rel_type.lower() == "parent":
                        parent_id = val
                    elif current_rel_type.lower() == "file":
                        test_file = val
                    current_rel_type = None

        processed.append({
            "id": uid,
            "title": req.get("title", ""),
            "description": statement,
            "type": req.get("req_type", "Requirement"),
            "priority": req.get("priority", "Med"),
            "status": req.get("status", "Backlog"),
            "parent_id": parent_id,
            "jira_key": req.get("jira_key"),
            "sdoc_uid": uid,
            # we will store test_file in test_cases if mapped
            "test_file": test_file
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
    
    os.makedirs(os.path.dirname(SDOC_PATH), exist_ok=True)
    with open(SDOC_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 strictdoc_client: Exported requirements to {SDOC_PATH}")


def sync_sdoc_to_db():
    """Sync workspace/requirements/requirements.sdoc into SQLite database."""
    if not os.path.exists(SDOC_PATH):
        # If .sdoc doesn't exist yet, seed it from SQLite database
        export_sdoc()
        return

    print(f"📄 strictdoc_client: Syncing {SDOC_PATH} → SQLite...")
    parsed_reqs = parse_sdoc(SDOC_PATH)
    
    conn = store.get_connection()
    try:
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
            
            # Sync test case file path reference if present
            if r.get('test_file'):
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
