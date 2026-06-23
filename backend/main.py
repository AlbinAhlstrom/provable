from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import dotenv

# Load environment variables from root .env file if present
dotenv.load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

from fastapi.middleware.cors import CORSMiddleware
from agent_orchestrator import run_openhands_loop, resolve_merge_conflict, run_requirement_audit

app = FastAPI(title="ScrumSim Backend")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'src', 'requirements.json')

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
    if not os.path.exists(REQUIREMENTS_FILE):
        return []
    with open(REQUIREMENTS_FILE, 'r') as f:
        data = json.load(f)
    return data

@app.post("/api/requirements")
def update_requirements(reqs: List[Requirement]):
    with open(REQUIREMENTS_FILE, 'w') as f:
        # Convert Pydantic models to dicts before dumping
        json.dump([r.dict() for r in reqs], f, indent=2)
    return {"success": True}

@app.get("/api/diff/{ticket_id}")
def get_diff(ticket_id: str):
    import subprocess
    WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
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
    WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
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
                    # align deleted lines on left and inserted lines on right
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
                
            # If the file is marked modified but has no actual diff changes, skip it
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
    WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
    
    # Get all requirements
    if not os.path.exists(REQUIREMENTS_FILE):
        return []
    with open(REQUIREMENTS_FILE, 'r') as f:
        requirements = json.load(f)
        
    review_items = [r for r in requirements if r.get('status') in ('Review', 'Conflict') and r.get('type') in ('Task', 'Bug')]
    
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
            # Read last 150 lines to prevent payload from getting too huge
            lines = f.readlines()
            return {"logs": "".join(lines[-150:])}
    except Exception as e:
        return {"logs": f"Error reading logs: {str(e)}"}

class ApprovePayload(BaseModel):
    id: str
    code: str

@app.post("/api/approve-code")
def approve_code(payload: ApprovePayload):
    # Update requirements status to Test
    if os.path.exists(REQUIREMENTS_FILE):
        with open(REQUIREMENTS_FILE, 'r') as f:
            data = json.load(f)
        for req in data:
            if req['id'] == payload.id:
                req['status'] = 'Test'
                break
        with open(REQUIREMENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    return {"success": True, "message": "Code approved, moving to Test phase."}

@app.post("/api/merge-code")
def merge_code(payload: ApprovePayload, background_tasks: BackgroundTasks):
    import subprocess
    WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
    branch_name = f"ticket/{payload.id}"
    
    try:
        # Checkout main
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, check=True)
    except Exception as e:
        return {"success": False, "error": f"Failed to checkout main: {str(e)}"}

    try:
        # Attempt to merge
        subprocess.run(["git", "merge", branch_name], cwd=WORKSPACE_BASE, check=True)
        # Delete branch on successful auto-merge
        subprocess.run(["git", "branch", "-d", branch_name], cwd=WORKSPACE_BASE)
    except subprocess.CalledProcessError as e:
        # Merge conflict or other merge failure
        if os.path.exists(REQUIREMENTS_FILE):
            with open(REQUIREMENTS_FILE, 'r') as f:
                data = json.load(f)
            for req in data:
                if req['id'] == payload.id:
                    req['status'] = 'Conflict'
                    req['feedback'] = "Merge conflict detected. Triggering automated resolution..."
                    break
            with open(REQUIREMENTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        
        # Trigger merge agent in background
        background_tasks.add_task(resolve_merge_conflict, payload.id)
        return {"success": True, "status": "Conflict", "message": "Merge conflict detected. Triggering resolution agent..."}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Update requirements status to Done
    if os.path.exists(REQUIREMENTS_FILE):
      with open(REQUIREMENTS_FILE, 'r') as f:
        data = json.load(f)
      for req in data:
        if req['id'] == payload.id:
          req['status'] = 'Done'
          break
      with open(REQUIREMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    # Trigger agent loop to process unblocked tasks/bugs
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "status": "Done", "message": "Code deployed and merged to main!"}

class CreateRequirementPayload(BaseModel):
    title: str
    description: str
    parentId: Optional[str] = None

@app.post("/api/create-requirement")
def create_requirement(payload: CreateRequirementPayload, background_tasks: BackgroundTasks):
    import urllib.request
    import urllib.error
    import random
    
    req_id = f"REQ-{random.randint(1000, 9999)}"
    
    # Create the parent requirement
    parent_req = Requirement(
        id=req_id,
        title=payload.title,
        description=payload.description,
        priority="High",
        status="Backlog",
        tests=[],
        assignedAgents=[],
        type="Requirement",
        parentId=payload.parentId
    )
    
    new_items = [parent_req.dict()]
    
    api_key = os.environ.get("LLM_API_KEY", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = (
        f"Break down the following requirement into 1 to 3 distinct technical tasks. "
        f"Requirement Title: {payload.title}. Description: {payload.description}. "
        f"If there are logical dependencies between these tasks (e.g., task B depends on task A being implemented first), "
        f"assign a temporary ID (e.g. \"t1\", \"t2\", \"t3\") to each task in the 'id' field, and list the prerequisite task IDs in its 'dependencies' field. "
        f"Respond ONLY with a JSON array of objects, where each object has: "
        f"'id' (string, e.g. \"t1\"), 'title' (string), 'description' (string), and 'dependencies' (array of strings of temporary IDs, e.g. [\"t1\"])."
    )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up markdown JSON block if present
            text_response = text_response.strip()
            if text_response.startswith('```json'):
                text_response = text_response[7:-3]
            elif text_response.startswith('```'):
                text_response = text_response[3:-3]
                
            tasks = json.loads(text_response)
            
            # Map temporary ID to actual generated REQ-XXXX ID
            id_mapping = {}
            for task in tasks:
                temp_id = task.get('id')
                actual_id = f"REQ-{random.randint(1000, 9999)}"
                if temp_id:
                    id_mapping[temp_id] = actual_id
            
            for task in tasks:
                temp_id = task.get('id')
                actual_id = id_mapping.get(temp_id, f"REQ-{random.randint(1000, 9999)}")
                
                # Resolve dependencies using the mapping
                temp_deps = task.get('dependencies', [])
                actual_deps = []
                for dep in temp_deps:
                    if dep in id_mapping:
                        actual_deps.append(id_mapping[dep])
                
                child_task = Requirement(
                    id=actual_id,
                    title=task.get('title', 'Generated Task'),
                    description=task.get('description', 'Task description'),
                    priority="Med",
                    status="Backlog",
                    tests=[],
                    assignedAgents=["Frontend"],
                    type="Task",
                    parentId=req_id,
                    dependencies=actual_deps
                )
                new_items.append(child_task.dict())
                
    except Exception as e:
        print(f"LLM Breakdown failed: {e}. Using fallback.")
        # Fallback
        task_id = f"REQ-{random.randint(1000, 9999)}"
        child_task = Requirement(
            id=task_id,
            title=f"Implement {payload.title}",
            description=payload.description,
            priority="Med",
            status="Backlog",
            tests=[],
            assignedAgents=["Frontend"],
            type="Task",
            parentId=req_id,
            dependencies=[]
        )
        new_items.append(child_task.dict())

    # Read existing and append
    if os.path.exists(REQUIREMENTS_FILE):
        with open(REQUIREMENTS_FILE, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
        
    existing_data.extend(new_items)
    
    with open(REQUIREMENTS_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    # Trigger agents automatically
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": f"Created requirement and {len(new_items)-1} child tasks."}

@app.post("/api/trigger-agents")
def trigger_agents(background_tasks: BackgroundTasks):
    """
    Called by the PM when concluding the Stand-Up.
    This kicks off the asynchronous LangGraph loop to process the backlog.
    """
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": "Agents have been dispatched."}

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
    
    # Format steps, expected, actual into description
    description = f"### Steps to Reproduce\n{payload.steps}\n\n### Expected Behavior\n{payload.expected}\n\n### Actual Behavior\n{payload.actual}"
    
    new_bug = Requirement(
        id=bug_id,
        title=payload.title,
        description=description,
        priority="High",
        status="Backlog",
        tests=[],
        assignedAgents=["Frontend"],
        type="Bug",
        parentId=payload.parentId,
        dependencies=[]
    )
    
    if os.path.exists(REQUIREMENTS_FILE):
        with open(REQUIREMENTS_FILE, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
        
    existing_data.append(new_bug.dict())
    
    with open(REQUIREMENTS_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    # Trigger agents automatically
    background_tasks.add_task(run_openhands_loop)
    return {"success": True, "message": f"Created bug {bug_id} associated with requirement {payload.parentId}."}

class CheckoutPreviewPayload(BaseModel):
    branch: str  # 'main' or 'ticket/<id>'

@app.post("/api/checkout-preview")
def checkout_preview(payload: CheckoutPreviewPayload):
    import subprocess
    WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
    
    # Validate branch name to prevent injection — allow only 'main' or 'ticket/ID' patterns
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
    if not os.path.exists(REQUIREMENTS_FILE):
        return {"success": False, "error": "Requirements file not found."}
    
    with open(REQUIREMENTS_FILE, 'r') as f:
        data = json.load(f)
        
    found = False
    for req in data:
        if req['id'] == payload.id:
            req['title'] = payload.title
            req['description'] = payload.description
            req['priority'] = payload.priority
            found = True
            break
            
    if not found:
        return {"success": False, "error": f"Requirement {payload.id} not found."}
        
    with open(REQUIREMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        
    # Trigger requirement audit in the background
    background_tasks.add_task(run_requirement_audit, payload.id)
    return {"success": True, "message": f"Updated requirement {payload.id} and scheduled Audit Agent."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
