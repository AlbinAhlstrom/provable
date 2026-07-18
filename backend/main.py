from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import dotenv
import yaml

# Load environment variables from root .env file if present
dotenv.load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from fastapi.middleware.cors import CORSMiddleware
from agent_orchestrator import run_openhands_loop, resolve_merge_conflict, run_requirement_audit, call_gemini
import db.store as store
from integrations.strictdoc_client import sync_sdoc_to_db
from config_loader import (
    get_workspace_base, get_project_settings, get_all_projects,
    set_active_project, add_project
)

app = FastAPI(title="Provable Backend")

@app.on_event("startup")
def startup_event():
    import sys
    # Skip live DB initialization and sync during test suite execution
    if os.environ.get("DATABASE_URL") or "pytest" in sys.modules:
        print("📦 Startup: Test execution context detected. Skipping live DB sync.")
        return

    # ── Startup: initialise per-project database ────────────────────────────────
    _active_db = os.path.join(get_workspace_base(), 'requirements', 'provable.db')
    store.set_active_db(_active_db)
    store.init_db()
    
    try:
        from integrations.strictdoc_client import sync_sdoc_to_db
        sync_sdoc_to_db()
    except Exception as e:
        print(f"📦 Startup: Failed to sync SDoc: {e}")
        
    try:
        from integrations.jira_client import sync_jira_to_db
        sync_jira_to_db()
    except Exception as e:
        print(f"📦 Startup: Failed to sync Jira: {e}")

    # Auto-create Allure project if enabled
    try:
        from integrations.allure_client import load_allure_config, get_allure_project_id
        allure_cfg = load_allure_config()
        if allure_cfg.get('enabled'):
            import requests
            _proj_slug = get_allure_project_id()
            allure_url = f"{allure_cfg.get('server_url', 'http://localhost:5050').rstrip('/')}/projects"
            res = requests.post(allure_url, json={"id": _proj_slug}, timeout=5)
            print(f"📊 Allure Integration: Project '{_proj_slug}' init response: {res.status_code}")
    except Exception as allure_init_err:
        print(f"📊 Allure Integration: Could not auto-create project: {allure_init_err}")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'integrations.yaml'))


# ── Project Management Endpoints ─────────────────────────────────────────────

@app.get("/api/projects")
def list_projects():
    """Return all registered projects and which one is currently active."""
    projects = get_all_projects()
    active_path = get_workspace_base()
    result = []
    for p in projects:
        result.append({
            "name": p.get("name", os.path.basename(p["path"])),
            "path": p["path"],
            "active": os.path.abspath(p["path"]) == os.path.abspath(active_path)
        })
    return result


@app.get("/api/project/settings")
def get_active_project_settings():
    """Return configuration for the currently active project."""
    settings = get_project_settings()
    settings["workspace_path"] = get_workspace_base()
    return settings


class ProjectSwitchPayload(BaseModel):
    path: str

@app.post("/api/projects/switch")
def switch_project(payload: ProjectSwitchPayload, background_tasks: BackgroundTasks):
    """Switch the active project workspace, re-initialise the DB, and re-sync requirements."""
    project_path = os.path.abspath(payload.path)
    if not os.path.exists(project_path):
        return {"success": False, "error": f"Path does not exist: {project_path}"}

    try:
        # 1. Switch workspace env
        set_active_project(project_path)

        # 2. Switch per-project database
        db_path = os.path.join(project_path, 'requirements', 'provable.db')
        store.set_active_db(db_path)
        store.init_db()

        # 3. Re-sync requirements from the project's sdoc (clearing old data first)
        sync_sdoc_to_db(clear_first=True)

        # 4. Auto-create the Allure project for this workspace
        try:
            from integrations.allure_client import load_allure_config, get_allure_project_id
            allure_cfg = load_allure_config()
            if allure_cfg.get('enabled'):
                import requests as _req
                slug = get_allure_project_id()
                allure_url = f"{allure_cfg['server_url'].rstrip('/')}/projects"
                _req.post(allure_url, json={"id": slug}, timeout=5)
        except Exception:
            pass

        # 5. Launch the project's dev server in background
        try:
            from onboarding.server_manager import start_project_servers
            background_tasks.add_task(start_project_servers, project_path)
        except Exception as server_err:
            print(f"⚠️ Failed to schedule server start: {server_err}")

        settings = get_project_settings()
        return {
            "success": True,
            "project": {
                "name": settings.get("name"),
                "path": project_path,
                "preview_url": settings.get("dev_server", {}).get("base_url", "http://localhost:5174")
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


class ProjectAddPayload(BaseModel):
    path: str
    run_synthesis: bool = True

@app.post("/api/projects/add")
def add_project_endpoint(payload: ProjectAddPayload, background_tasks: BackgroundTasks):
    """Onboard a new local project folder (runs the full onboarding pipeline in background)."""
    project_path = os.path.abspath(payload.path)
    if not os.path.exists(project_path):
        return {"success": False, "error": f"Path does not exist: {project_path}"}

    def _run_onboarding():
        from onboarding.onboard import onboard_project
        onboard_project(project_path, run_synthesis=payload.run_synthesis)

    background_tasks.add_task(_run_onboarding)
    return {
        "success": True,
        "message": f"Onboarding started for {project_path}. This may take a minute."
    }


@app.post("/api/requirements/synthesize-from-tests")
def synthesize_requirements(background_tasks: BackgroundTasks):
    """Run the reverse-TDD synthesizer on the active project's test suite."""
    workspace = get_workspace_base()

    def _run_synthesis():
        from onboarding.requirements_synthesizer import synthesize_requirements_from_tests
        synthesize_requirements_from_tests(workspace)

    background_tasks.add_task(_run_synthesis)
    return {"success": True, "message": "Requirement synthesis started in background."}


# ── Requirements Models ───────────────────────────────────────────────────────

class Requirement(BaseModel):

    id: str
    title: str
    description: str
    priority: str
    status: str
    tests: List[Dict[str, Any]]
    assignedAgents: List[str]
    proposedCode: Optional[str] = None
    feedback: Optional[str] = None
    type: Optional[str] = None
    parentId: Optional[str] = None
    dependencies: Optional[List[str]] = []

@app.get("/api/requirements")
def get_requirements():
    return store.get_requirements_for_frontend()

@app.post("/api/requirements")
def update_requirements(reqs: List[Requirement]):
    for r in reqs:
        existing = store.get_requirement(r.id)
        if existing:
            store.update_requirement(r.id, r.dict())
        else:
            store.create_requirement(r.dict())
    return {"success": True}

@app.delete("/api/requirements/{req_id}")
def delete_requirement(req_id: str):
    existing = store.get_requirement(req_id)
    if not existing:
        return {"success": False, "error": f"Requirement {req_id} not found"}
    store.delete_requirement_cascade(req_id)
    return {"success": True}

@app.get("/api/settings")
def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.put("/api/settings")
def update_settings(payload: dict):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        yaml.safe_dump(payload, f)
    return {"success": True}

@app.get("/api/diff/{ticket_id}")
def get_diff(ticket_id: str):
    import subprocess
    WORKSPACE_BASE = get_workspace_base()
    try:
        # Get the diff between main and the ticket branch
        result = subprocess.run(["git", "diff", "main...ticket/" + ticket_id], cwd=WORKSPACE_BASE, capture_output=True, text=True)
        return {"diff": result.stdout}
    except Exception as e:
        return {"diff": f"Error fetching diff: {str(e)}"}

@app.get("/api/diff-files/{ticket_id}")
def get_diff_files(ticket_id: str):
    import subprocess
    import difflib
    WORKSPACE_BASE = get_workspace_base()
    try:
        # Find merge base
        mb_res = subprocess.run(
            ["git", "merge-base", "main", f"ticket/{ticket_id}"],
            cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
        )
        merge_base = mb_res.stdout.strip()
        
        # Get list of files changed
        files_res = subprocess.run(
            ["git", "diff", "--name-only", f"main...ticket/{ticket_id}"],
            cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
        )
        filenames = [f.strip() for f in files_res.stdout.splitlines() if f.strip()]
        # Filter out pycache, compiled files, and internal git paths
        filenames = [
            f for f in filenames
            if not f.endswith('.pyc')
            and '__pycache__' not in f
            and not f.endswith('.pyo')
            and not f.endswith('.pyd')
            and not f.endswith('.sdoc')
            and '.git/' not in f
        ]
        
        files_data = []
        for fname in filenames:
            # Get original file content from merge base
            try:
                orig_res = subprocess.run(
                    ["git", "show", f"{merge_base}:{fname}"],
                    cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
                )
                original_content = orig_res.stdout
            except Exception:
                original_content = ""
                
            # Get modified file content from branch
            try:
                mod_res = subprocess.run(
                    ["git", "show", f"ticket/{ticket_id}:{fname}"],
                    cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
                )
                modified_content = mod_res.stdout
            except Exception:
                modified_content = ""
                
            original_lines = original_content.splitlines()
            modified_lines = modified_content.splitlines()
            
            # Use SequenceMatcher to find operations
            sm = difflib.SequenceMatcher(None, original_lines, modified_lines)
            opcodes = sm.get_opcodes()
            
            row_pairs = []
            for tag, i1, i2, j1, j2 in opcodes:
                if tag == 'equal':
                    for offset in range(i2 - i1):
                        row_pairs.append({
                            "type": "equal",
                            "left": {
                                "lineNum": i1 + offset + 1,
                                "content": original_lines[i1 + offset]
                            },
                            "right": {
                                "lineNum": j1 + offset + 1,
                                "content": modified_lines[j1 + offset]
                            }
                        })
                elif tag == 'delete':
                    for offset in range(i2 - i1):
                        row_pairs.append({
                            "type": "delete",
                            "left": {
                                "lineNum": i1 + offset + 1,
                                "content": original_lines[i1 + offset]
                            },
                            "right": None
                        })
                elif tag == 'insert':
                    for offset in range(j2 - j1):
                        row_pairs.append({
                            "type": "insert",
                            "left": None,
                            "right": {
                                "lineNum": j1 + offset + 1,
                                "content": modified_lines[j1 + offset]
                            }
                        })
                elif tag == 'replace':
                    D = i2 - i1
                    I = j2 - j1
                    max_len = max(D, I)
                    for k in range(max_len):
                        left_val = None
                        right_val = None
                        if k < D:
                            left_val = {
                                "lineNum": i1 + k + 1,
                                "content": original_lines[i1 + k]
                            }
                        if k < I:
                            right_val = {
                                "lineNum": j1 + k + 1,
                                "content": modified_lines[j1 + k]
                            }
                        row_pairs.append({
                            "type": "replace",
                            "left": left_val,
                            "right": right_val
                        })
            
            status = "modified"
            if not original_content and modified_content:
                status = "added"
            elif original_content and not modified_content:
                status = "deleted"
                
            has_changes = any(p["type"] != "equal" for p in row_pairs)
            if status == "modified" and not has_changes:
                continue
                
            files_data.append({
                "filename": fname,
                "status": status,
                "rowPairs": row_pairs
            })
            
        return {"files": files_data}
    except Exception as e:
        return {"files": [], "error": str(e)}

@app.get("/api/reviews")
def get_reviews():
    import subprocess
    import time
    WORKSPACE_BASE = get_workspace_base()
    
    requirements = store.get_all_requirements()
        
    review_items = []
    for r in requirements:
        if r.get('type') not in ('Task', 'Bug'):
            continue
        status = r.get('status')
        if status in ('Done', 'Test'):
            continue
        ticket_id = r['id']
        branch_name = f"ticket/{ticket_id}"
        
        # Check if the branch exists
        branch_exists_res = subprocess.run(
            ["git", "show-ref", f"refs/heads/{branch_name}"],
            cwd=WORKSPACE_BASE, capture_output=True
        )
        
        # Include if branch exists AND status is Review/Conflict
        if branch_exists_res.returncode == 0 and status in ('Review', 'Conflict'):
            review_items.append(r)
    
    results = []
    for req in review_items:
        ticket_id = req['id']
        waiting_time_str = "Unknown"
        insertions = 0
        deletions = 0
        size = "XS"
        
        # Get wait time (latest commit timestamp on the branch)
        try:
            log_res = subprocess.run(
                ["git", "log", "-1", "--format=%ct", f"ticket/{ticket_id}"],
                cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
            )
            timestamp_str = log_res.stdout.strip()
            if timestamp_str.isdigit():
                commit_time = int(timestamp_str)
                elapsed = int(time.time()) - commit_time
                if elapsed < 60:
                    waiting_time_str = "Just now"
                elif elapsed < 3600:
                    waiting_time_str = f"{elapsed // 60}m ago"
                elif elapsed < 86400:
                    waiting_time_str = f"{elapsed // 3600}h ago"
                else:
                    waiting_time_str = f"{elapsed // 86400}d ago"
        except Exception:
            waiting_time_str = "1h ago"
            
        # Get diff stats (insertions/deletions)
        try:
            numstat_res = subprocess.run(
                ["git", "diff", "--numstat", f"main...ticket/{ticket_id}"],
                cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
            )
            lines = numstat_res.stdout.splitlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    ins_str, del_str = parts[0], parts[1]
                    if ins_str.isdigit():
                        insertions += int(ins_str)
                    if del_str.isdigit():
                        deletions += int(del_str)
                        
            total_changes = insertions + deletions
            if total_changes <= 15:
                size = "XS"
            elif total_changes <= 50:
                size = "S"
            elif total_changes <= 150:
                size = "M"
            elif total_changes <= 500:
                size = "L"
            else:
                size = "XL"
        except Exception:
            pass
            
        results.append({
            "id": ticket_id,
            "title": req.get('title', 'Unknown Task'),
            "status": req.get('status'),
            "size": size,
            "waitingTime": waiting_time_str,
            "insertions": insertions,
            "deletions": deletions
        })
        
    return results

@app.get("/api/logs/{ticket_id}")
def get_logs(ticket_id: str):
    log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', f"{ticket_id}.log"))
    if not os.path.exists(log_file_path):
        return {"logs": "Agent has not started yet or log file not created."}
    
    try:
        with open(log_file_path, 'r') as f:
            lines = f.readlines()
            return {"logs": "".join(lines[-150:])}
    except Exception as e:
        return {"logs": f"Error reading logs: {str(e)}"}

@app.get("/api/agent-status")
def get_agent_status():
    from agent_orchestrator import AGENT_STATUS
    
    backlog_analysis = []
    try:
        reqs = store.get_all_requirements()
        
        # Map status of each item
        status_map = {r['id']: r.get('status', 'Backlog') for r in reqs}
        
        # Find all Backlog items that are tasks or bugs
        backlog_items = [r for r in reqs if r.get('status') == 'Backlog' and r.get('type') in ('Task', 'Bug')]
        
        for item in backlog_items:
            deps = item.get('dependencies', [])
            incomplete_deps = [dep for dep in deps if status_map.get(dep) != 'Done']
            
            blocked_by_siblings = []
            if item.get('type') == 'Bug':
                parent_id = item.get('parent_id')
                if parent_id:
                    sibling_tasks = [r for r in reqs if r.get('parent_id') == parent_id and r.get('type') == 'Task']
                    incomplete_siblings = [r['id'] for r in sibling_tasks if r.get('status') != 'Done']
                    blocked_by_siblings = incomplete_siblings
            
            is_blocked = bool(incomplete_deps or blocked_by_siblings)
            reasons = []
            if incomplete_deps:
                reasons.append(f"Blocked by dependencies: {', '.join(incomplete_deps)}")
            if blocked_by_siblings:
                reasons.append(f"Blocked by sibling tasks: {', '.join(blocked_by_siblings)}")
            
            backlog_analysis.append({
                "id": item['id'],
                "title": item['title'],
                "type": item.get('type', 'Task'),
                "is_blocked": is_blocked,
                "reasons": reasons
            })
    except Exception as e:
        print(f"Error in backlog analysis: {e}")
        
    return {
        "status": AGENT_STATUS,
        "backlog_analysis": backlog_analysis
    }

class ApprovePayload(BaseModel):
    id: str
    code: str

@app.post("/api/approve-code")
def approve_code(payload: ApprovePayload):
    store.update_requirement(payload.id, {'status': 'Test'})
    return {"success": True, "message": "Code approved, moving to Test phase."}

@app.post("/api/merge-code")
def merge_code(payload: ApprovePayload, background_tasks: BackgroundTasks):
    import subprocess
    WORKSPACE_BASE = get_workspace_base()
    branch_name = f"ticket/{payload.id}"
    
    try:
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, check=True)
    except Exception as e:
        return {"success": False, "error": f"Failed to checkout main: {str(e)}"}

    try:
        subprocess.run(["git", "merge", branch_name], cwd=WORKSPACE_BASE, check=True)
        subprocess.run(["git", "branch", "-d", branch_name], cwd=WORKSPACE_BASE)
    except subprocess.CalledProcessError as e:
        store.update_requirement_status(payload.id, 'Conflict', feedback="Merge conflict detected. Triggering automated resolution...")
        background_tasks.add_task(resolve_merge_conflict, payload.id)
        return {"success": True, "status": "Conflict", "message": "Merge conflict detected. Triggering resolution agent..."}
    except Exception as e:
        return {"success": False, "error": str(e)}

    store.update_requirement(payload.id, {'status': 'Done'})
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "status": "Done", "message": "Code deployed and merged to main!"}

class CreateRequirementPayload(BaseModel):
    title: str
    description: str
    parentId: Optional[str] = None

class CreateFolderPayload(BaseModel):
    title: str
    description: Optional[str] = ""
    parentId: Optional[str] = None

@app.post("/api/create-folder")
def create_folder(payload: CreateFolderPayload):
    import random
    folder_id = f"FLD-{random.randint(100, 999)}"
    store.create_requirement({
        "id": folder_id,
        "title": payload.title,
        "description": payload.description or "",
        "priority": "Med",
        "status": "Backlog",
        "type": "Folder",
        "parentId": payload.parentId,
    })
    return {"success": True, "id": folder_id}

@app.post("/api/requirements/{req_id}/move")
def move_requirement(req_id: str, payload: dict):
    """Change a requirement's parent (or unparent it)."""
    new_parent = payload.get("parentId")  # None to move to root
    store.update_requirement(req_id, {"parent_id": new_parent})
    return {"success": True}

@app.post("/api/create-requirement")
def create_requirement(payload: CreateRequirementPayload, background_tasks: BackgroundTasks):
    import random
    
    req_id = f"REQ-{random.randint(1000, 9999)}"
    
    # Create the parent requirement
    store.create_requirement({
        "id": req_id,
        "title": payload.title,
        "description": payload.description,
        "priority": "High",
        "status": "Backlog",
        "type": "Requirement",
        "parentId": payload.parentId
    })
    
    # Load task decomposition template
    prompt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'prompts'))
    with open(os.path.join(prompt_dir, 'task_decomposition.md'), 'r', encoding='utf-8') as f:
        template = f.read()
    prompt = template.format(title=payload.title, description=payload.description)
    
    new_items_count = 0
    try:
        text_response = call_gemini(prompt)
        text_response = text_response.strip()
        if text_response.startswith('```json'):
            text_response = text_response[7:-3]
        elif text_response.startswith('```'):
            text_response = text_response[3:-3]
                
        tasks = json.loads(text_response)
        
        id_mapping = {}
        for task in tasks:
            temp_id = task.get('id')
            actual_id = f"REQ-{random.randint(1000, 9999)}"
            if temp_id:
                id_mapping[temp_id] = actual_id
        
        for task in tasks:
            temp_id = task.get('id')
            actual_id = id_mapping.get(temp_id, f"REQ-{random.randint(1000, 9999)}")
            
            temp_deps = task.get('dependencies', [])
            actual_deps = []
            for dep in temp_deps:
                if dep in id_mapping:
                    actual_deps.append(id_mapping[dep])
            
            store.create_requirement({
                "id": actual_id,
                "title": task.get('title', 'Generated Task'),
                "description": task.get('description', 'Task description'),
                "priority": "Med",
                "status": "Backlog",
                "type": "Task",
                "parentId": req_id,
                "dependencies": actual_deps,
                "assignedAgents": ["Frontend"]
            })
            new_items_count += 1
                
    except Exception as e:
        print(f"LLM Breakdown failed: {e}. Using fallback.")
        task_id = f"REQ-{random.randint(1000, 9999)}"
        store.create_requirement({
            "id": task_id,
            "title": f"Implement {payload.title}",
            "description": payload.description,
            "priority": "Med",
            "status": "Backlog",
            "type": "Task",
            "parentId": req_id,
            "dependencies": [],
            "assignedAgents": ["Frontend"]
        })
        new_items_count += 1
        
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": f"Created requirement and {new_items_count} child tasks."}

@app.post("/api/trigger-agents")
def trigger_agents(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": "Agents have been dispatched."}

@app.post("/api/trigger-ticket/{ticket_id}")
def trigger_ticket(ticket_id: str, background_tasks: BackgroundTasks):
    import re
    if not re.match(r'^[A-Za-z0-9_\-]+$', ticket_id):
        return {"success": False, "error": "Invalid ticket ID format."}
        
    background_tasks.add_task(run_openhands_loop, ticket_id)
    return {"success": True, "message": f"Agent dispatched for ticket {ticket_id}."}

@app.post("/api/abandon-ticket/{ticket_id}")
def abandon_ticket(ticket_id: str):
    import re
    import subprocess
    if not re.match(r'^[A-Za-z0-9_\-]+$', ticket_id):
        return {"success": False, "error": "Invalid ticket ID format."}
        
    WORKSPACE_BASE = get_workspace_base()
    
    try:
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
        subprocess.run(["git", "branch", "-D", f"ticket/{ticket_id}"], cwd=WORKSPACE_BASE, capture_output=True)
    except Exception as e:
        print(f"Error cleaning up git branch on abandon: {e}")
        
    store.update_requirement(ticket_id, {'status': 'Backlog', 'feedback': ''})
    return {"success": True, "message": f"Ticket {ticket_id} abandoned and reset to Backlog."}

class ReportBugPayload(BaseModel):
    title: str
    parentId: str
    steps: str
    expected: str
    actual: str

@app.post("/api/report-bug")
def report_bug(payload: ReportBugPayload, background_tasks: BackgroundTasks):
    import random
    bug_id = f"BUG-{random.randint(1000, 9999)}"
    description = f"### Steps to Reproduce\n{payload.steps}\n\n### Expected Behavior\n{payload.expected}\n\n### Actual Behavior\n{payload.actual}"
    
    store.create_requirement({
        "id": bug_id,
        "title": payload.title,
        "description": description,
        "priority": "High",
        "status": "Backlog",
        "type": "Bug",
        "parentId": payload.parentId,
        "dependencies": [],
        "assignedAgents": ["Frontend"]
    })
    
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": f"Created bug {bug_id} associated with requirement {payload.parentId}."}

class CheckoutPreviewPayload(BaseModel):
    branch: str

@app.post("/api/checkout-preview")
def checkout_preview(payload: CheckoutPreviewPayload):
    import subprocess
    WORKSPACE_BASE = get_workspace_base()
    
    branch = payload.branch.strip()
    import re
    if branch != 'main' and not re.match(r'^ticket/[A-Za-z0-9_\-]+$', branch):
        return {"success": False, "error": f"Invalid branch name: {branch}"}
    
    try:
        subprocess.run(
            ["git", "checkout", branch],
            cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
        )
        return {"success": True, "branch": branch}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr or str(e)}

class EditRequirementPayload(BaseModel):
    id: str
    title: str
    description: str
    priority: str

@app.post("/api/edit-requirement")
def edit_requirement(payload: EditRequirementPayload, background_tasks: BackgroundTasks):
    store.update_requirement(payload.id, {
        'title': payload.title,
        'description': payload.description,
        'priority': payload.priority
    })
    background_tasks.add_task(run_requirement_audit, payload.id)
    return {"success": True, "message": f"Updated requirement {payload.id} and scheduled Audit Agent."}

@app.get("/api/coverage")
def get_coverage():
    from integrations.allure_client import get_allure_report_url, get_coverage_summary
    
    summary = get_coverage_summary()
    reqs = store.get_requirements_for_frontend()
    
    coverage_reqs = []
    for r in reqs:
        if r.get('type') != 'Requirement':
            continue
            
        tcs = r.get('tests', [])
        if not tcs:
            state = "uncovered"
        elif any(t.get('status') == 'Failing' for t in tcs):
            state = "failing"
        elif all(t.get('status') == 'Passing' for t in tcs):
            state = "passing"
        else:
            state = "pending"
            
        coverage_reqs.append({
            "id": r['id'],
            "title": r['title'],
            "coverage_state": state,
            "tests": tcs
        })
        
    return {
        "summary": summary,
        "requirements": coverage_reqs,
        "allure_report_url": get_allure_report_url()
    }

@app.post("/api/requirements/{req_id}/create-test-case")
def create_test_case(req_id: str, background_tasks: BackgroundTasks):

    import random
    from agent_orchestrator import load_prompt, call_gemini, run_pytest
    
    # 1. Load requirement
    req = store.get_requirement(req_id)
    if not req:
        return {"success": False, "error": f"Requirement {req_id} not found."}
        
    test_case_id = f"TST-{random.randint(1000, 9999)}"
    
    # 2. Call LLM to generate test
    try:
        prompt = load_prompt("test_case_generation.md", {
            "req_id": req_id,
            "title": req.get('title', ''),
            "description": req.get('description', ''),
            "test_case_id": test_case_id
        })
        test_code = call_gemini(prompt, stage="test_case_generation")
        
        # Clean up markdown code block formatting if present
        test_code = test_code.strip()
        if test_code.startswith("```python"):
            test_code = test_code[9:-3]
        elif test_code.startswith("```"):
            test_code = test_code[3:-3]
        test_code = test_code.strip()
        
        # 3. Write test file
        workspace_base = get_workspace_base()
        test_dir = os.path.join(workspace_base, 'tests')
        os.makedirs(test_dir, exist_ok=True)
        test_file_path = os.path.join(test_dir, f"test_{req_id}.py")
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
            
        # Run pytest (sanity check / registers the test in pytest output)
        background_tasks.add_task(run_pytest, workspace_base)
        
        # 4. Parse docstring fields from test code
        test_func_name = "test_case"
        for line in test_code.splitlines():
            if line.strip().startswith("def test_"):
                test_func_name = line.split("def ")[1].split("(")[0].strip()
                break
                
        from agent_orchestrator import parse_test_docstrings
        docstrings = parse_test_docstrings(test_file_path)
        tc_doc = docstrings.get(test_func_name, {})
        
        conn = store.get_connection()
        conn.execute(
            """INSERT OR REPLACE INTO test_cases
               (id, requirement_id, title, given_text, when_text, then_text, file_path, last_result)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                test_case_id,
                req_id,
                test_func_name,
                tc_doc.get('given', ''),
                tc_doc.get('when', ''),
                tc_doc.get('then', ''),
                f"tests/test_{req_id}.py",
                'fail'  # always fails at creation (TDD red)
            )
        )
        conn.commit()
        conn.close()
        
        store._trigger_sdoc_export()
        
        return {
            "success": True,
            "test_case_id": test_case_id,
            "test_code": test_code,
            "file_path": f"tests/test_{req_id}.py"
        }
        
    except Exception as e:
        print(f"❌ Failed to create test case: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/requirements/{req_id}/fix-test-case")
def fix_test_case(req_id: str, background_tasks: BackgroundTasks):
    from integrations.jira_client import create_jira_ticket
    
    # 1. Load requirement
    req = store.get_requirement(req_id)
    if not req:
        return {"success": False, "error": f"Requirement {req_id} not found."}
        
    # 2. Get the failing test case
    tcs = store.get_test_cases_for_requirement(req_id)
    if not tcs:
        return {"success": False, "error": f"No test cases linked to requirement {req_id}."}
        
    # 3. Create Jira ticket
    title = f"Fix failing test for {req.get('title')}"
    description = f"The automated test case for requirement {req_id} is failing.\nImplement the missing behavior and ensure the test case passes."
    jira_key = create_jira_ticket(title, description, req_id)
    
    # 4. Update status in database to Backlog and link JIRA key
    store.update_requirement(req_id, {
        "status": "Backlog",
        "jira_key": jira_key,
        "feedback": ""
    })
    
    # 5. Find the child Task to dispatch (agent only processes Task/Bug, not Requirement)
    child_tasks = [
        r for r in store.get_all_requirements()
        if r.get('parent_id') == req_id and r.get('type') in ('Task', 'Bug')
    ]
    backlog_tasks = [r for r in child_tasks if r.get('status') == 'Backlog']
    task_to_dispatch = (backlog_tasks or child_tasks or [None])[0]

    if task_to_dispatch:
        background_tasks.add_task(run_openhands_loop, task_to_dispatch['id'])
    else:
        # No child task — dispatch general loop to pick up whatever is ready
        background_tasks.add_task(run_openhands_loop)
    
    return {
        "success": True,
        "jira_key": jira_key,
        "message": f"Created Jira ticket {jira_key} and dispatched developer agent."
    }

@app.post("/api/tests/run")
def run_all_tests(background_tasks: BackgroundTasks):
    from agent_orchestrator import run_pytest, sync_test_results
    from integrations.allure_client import trigger_allure_generation
    WORKSPACE_BASE = get_workspace_base()
    test_results, failures = run_pytest(WORKSPACE_BASE)
    sync_test_results(test_results)
    background_tasks.add_task(trigger_allure_generation)
    return {"success": True, "results": test_results, "failures": failures}

@app.post("/api/tests/{test_id}/run")
def run_single_test(test_id: str, background_tasks: BackgroundTasks):
    from agent_orchestrator import run_pytest, sync_test_results
    from integrations.allure_client import trigger_allure_generation
    WORKSPACE_BASE = get_workspace_base()
    conn = store.get_connection()
    row = conn.execute("SELECT title, file_path FROM test_cases WHERE id = ?", (test_id,)).fetchone()
    conn.close()
    if not row or not row['title']:
        return {"success": False, "error": f"Test case {test_id} not found or has no title."}
    test_name = row['title']
    file_path = row['file_path'] or f"tests/test_{test_id}.py"
    if test_name.startswith("Linked test:"):
        test_target = file_path
    else:
        test_target = f"{file_path}::{test_name}"
    test_results, failures = run_pytest(WORKSPACE_BASE, test_target=test_target)
    sync_test_results(test_results)
    background_tasks.add_task(trigger_allure_generation)
    return {"success": True, "results": test_results, "failures": failures}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

