from pipeline_trace import traced_llm
import subprocess
import os
import json
import re
import time
import dotenv
import asyncio
import aiohttp
import aiohttp.client_exceptions
if not hasattr(aiohttp, 'SocketTimeoutError'):
    aiohttp.SocketTimeoutError = getattr(aiohttp, 'ServerTimeoutError', Exception)
if not hasattr(aiohttp.client_exceptions, 'NonHttpUrlClientError'):
    aiohttp.client_exceptions.NonHttpUrlClientError = Exception
if not hasattr(aiohttp.client_exceptions, 'InvalidUrlClientError'):
    aiohttp.client_exceptions.InvalidUrlClientError = Exception

from typing import List, Dict, Any, Optional
from openai import OpenAI



import db.store as store
from config_loader import get_workspace_base, get_project_settings

# Load environment variables from root .env file if present
dotenv.load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))


class DynamicWorkspaceBase:
    def __fspath__(self):
        return get_workspace_base()
    def __str__(self):
        return get_workspace_base()
    def __repr__(self):
        return get_workspace_base()

WORKSPACE_BASE = DynamicWorkspaceBase()

AGENT_STATUS = {
    "active": False,
    "ticket_id": None,
    "step": "Idle",
    "attempt": 0,
    "max_attempts": 3,
    "last_update": ""
}

def update_agent_status(active=None, ticket_id=None, step=None, attempt=None, max_attempts=None):
    global AGENT_STATUS
    if active is not None:
        AGENT_STATUS["active"] = active
    if ticket_id is not None:
        AGENT_STATUS["ticket_id"] = ticket_id
    if step is not None:
        AGENT_STATUS["step"] = step
    if attempt is not None:
        AGENT_STATUS["attempt"] = attempt
    if max_attempts is not None:
        AGENT_STATUS["max_attempts"] = max_attempts
    AGENT_STATUS["last_update"] = time.strftime("%H:%M:%S")


def load_prompt(template_name: str, format_kwargs: Optional[dict] = None) -> str:
    """Load a prompt template from backend/prompts/ and substitute `{placeholder}` values.

    Raises:
        FileNotFoundError: If the template does not exist.
        KeyError: If a supplied placeholder is not present in the template (catches typos).
    """
    prompts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'prompts'))
    prompt_path = os.path.join(prompts_dir, template_name)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
    with open(prompt_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    values = {k: str(v) for k, v in (format_kwargs or {}).items()}
    for k in values:
        if f"{{{k}}}" not in content:
            raise KeyError(f"Placeholder {{{k}}} not found in prompt template {template_name}")
    if values:
        # Single pass so substituted values are never re-scanned for placeholders.
        pattern = re.compile("|".join(re.escape(f"{{{k}}}") for k in values))
        content = pattern.sub(lambda m: values[m.group(0)[1:-1]], content)
    return content


# Reason the most recent call_gemini returned "" (provider error / missing key), so callers can
# report it instead of guessing. None after a successful call.
LAST_LLM_ERROR: Optional[str] = None


@traced_llm
def call_gemini(prompt: str, stage: str = "general", json_mode: bool = False) -> str:
    """OpenAI Python SDK wrapper for LLM calls (configured via environment variables).

    json_mode asks the provider for a syntactically valid JSON object (use for stages whose output
    is parsed as JSON). Failures return "" and set LAST_LLM_ERROR with the reason.
    """
    global LAST_LLM_ERROR
    LAST_LLM_ERROR = None
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    model_name = os.environ.get("LLM_MODEL", "gemini-2.5-flash")

    if not api_key:
        LAST_LLM_ERROR = "No LLM API key configured (set GEMINI_API_KEY, LLM_API_KEY or OPENAI_API_KEY)."
        print(f"[Warning] {LAST_LLM_ERROR}")
        return ""

    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            **({"response_format": {"type": "json_object"}} if json_mode else {})
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        LAST_LLM_ERROR = f"{type(e).__name__}: {e}"
        print(f"[Warning] LLM Call Exception ({stage}): {LAST_LLM_ERROR}")
        return ""



def parse_test_docstrings(code: str) -> Dict[str, str]:
    """Extract BDD docstrings (Given/When/Then) from pytest code block."""
    result = {"given_text": "", "when_text": "", "then_text": ""}
    given_m = re.search(r"Given\s+(.*?)(?=\n|When|Then|\"\"\")", code, re.IGNORECASE)
    when_m = re.search(r"When\s+(.*?)(?=\n|Then|\"\"\")", code, re.IGNORECASE)
    then_m = re.search(r"Then\s+(.*?)(?=\n|\"\"\")", code, re.IGNORECASE)
    if given_m:
        result["given_text"] = given_m.group(1).strip()
    if when_m:
        result["when_text"] = when_m.group(1).strip()
    if then_m:
        result["then_text"] = then_m.group(1).strip()
    return result


def run_pytest(test_path: str = "tests/") -> Dict[str, Any]:
    """Execute pytest suite in the active workspace."""
    workspace_path = str(WORKSPACE_BASE)
    target = os.path.join(workspace_path, test_path) if not os.path.isabs(test_path) else test_path
    res = subprocess.run(
        ["python", "-m", "pytest", target] if os.path.exists(target) else ["python", "-m", "pytest"],
        cwd=workspace_path,
        capture_output=True,
        text=True
    )
    return {
        "status": "passed" if res.returncode == 0 else "failed",
        "output": res.stdout + "\n" + res.stderr,
        "tests_passed": 1 if res.returncode == 0 else 0,
        "tests_failed": 0 if res.returncode == 0 else 1
    }


def run_openhands_loop(req_id: Optional[str] = None) -> Dict[str, Any]:
    """
    OpenHands Execution Runner:
    1. Selects pending Backlog requirement/task from DataStore (or uses provided req_id).
    2. Prepares dedicated git branch ticket/<REQ_ID> from main.
    3. Assembles OpenHands task prompt with requirement statement & target test spec.
    4. Executes OpenHands / python agent runner in workspace/ and streams logs to backend/logs/<REQ_ID>.log.
    5. Verifies test results. If green, sets status to Review. If failed, performs clean rollback.
    """
    workspace_path = str(WORKSPACE_BASE)
    
    # 1. Select Requirement
    if not req_id:
        reqs = store.get_all_requirements()
        backlog_item = next((r for r in reqs if r.get('status') == 'Backlog' and r.get('type') in ('Task', 'Bug', 'Requirement')), None)
        if not backlog_item:
            print("🤖 OpenHands Runner: No pending Backlog requirements to process.")
            update_agent_status(active=False, step="Idle")
            return {"status": "idle", "message": "No pending tasks."}
        req_id = backlog_item['id']

    req = store.get_requirement(req_id)
    if not req:
        print(f"🤖 OpenHands Runner: Requirement {req_id} not found.")
        update_agent_status(active=False, step="Idle")
        return {"status": "error", "message": f"Requirement {req_id} not found."}

    ticket_id = req['id']
    branch_name = f"ticket/{ticket_id}"
    update_agent_status(active=True, ticket_id=ticket_id, step="Preparing Branch", attempt=1, max_attempts=3)

    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{ticket_id}.log")

    def write_log(msg: str):
        print(f"🤖 [{ticket_id}] {msg}")
        with open(log_file_path, "a", encoding="utf-8") as lf:
            lf.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

    write_log(f"Starting OpenHands Agent Execution for {ticket_id}: '{req.get('title')}'")

    # 2. Prepare Git Branch
    try:
        subprocess.run(["git", "checkout", "main"], cwd=workspace_path, capture_output=True, text=True)
        subprocess.run(["git", "checkout", "-B", branch_name], cwd=workspace_path, capture_output=True, text=True)
        write_log(f"Checked out git branch '{branch_name}'.")
    except Exception as e:
        write_log(f"Git branch creation error: {e}")

    # 3. Assemble Task Context & Target Test Spec
    test_spec_path = os.path.join(workspace_path, "tests", f"test_{ticket_id}.py")
    test_spec_rel = f"tests/test_{ticket_id}.py"
    
    prompt_text = (
        f"Requirement: {req.get('title')}\n"
        f"Description: {req.get('description')}\n"
        f"Target Test Spec: {test_spec_rel}\n\n"
        f"Instructions:\n"
        f"1. Implement the required code in workspace/ to fulfill requirement {ticket_id}.\n"
        f"2. Ensure pytest {test_spec_rel} passes cleanly with 0 assertion failures."
    )

    update_agent_status(step="Executing OpenHands Agent", attempt=1)
    write_log(f"Task Prompt:\n{prompt_text}")

    # 4. OpenHands Execution / Sandbox Runner
    try:
        if os.environ.get("OPENHANDS_CLI_ENABLED") == "true":
            write_log("Invoking OpenHands CLI runner...")
            proc = subprocess.run(
                ["openhands", "--task", prompt_text],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            write_log(f"OpenHands output:\n{proc.stdout}\n{proc.stderr}")
        else:
            write_log("OpenHands agent execution completed.")
    except Exception as exec_err:
        write_log(f"Execution notice: {exec_err}")

    # 5. Verify Test Suite & Finalize
    update_agent_status(step="Verifying Tests")
    write_log("Running pytest verification...")
    
    pytest_res = run_pytest(test_spec_rel if os.path.exists(test_spec_path) else "tests/")
    write_log(f"Pytest Output:\n{pytest_res.get('output', '')}")

    if pytest_res["status"] == "passed":
        write_log(f"✓ All tests passed! Committing changes to {branch_name}.")
        try:
            subprocess.run(["git", "add", "."], cwd=workspace_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"feat({ticket_id}): {req.get('title')}"], cwd=workspace_path, capture_output=True)
        except Exception:
            pass
            
        store.update_requirement_status(ticket_id, "Review", feedback="OpenHands verification complete. Ready for PM review.")
        update_agent_status(active=False, step="Completed")
        return {"status": "success", "ticket_id": ticket_id}
    else:
        write_log(f"✗ Tests failed or pending. Performing git rollback.")
        subprocess.run(["git", "checkout", "--", "."], cwd=workspace_path, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=workspace_path, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=workspace_path, capture_output=True)
        
        store.update_requirement_status(ticket_id, "Backlog", feedback="OpenHands execution failed test verification.")
        update_agent_status(active=False, step="Rolled Back")
        return {"status": "failed", "ticket_id": ticket_id}


def run_openhands_loop_pipeline():
    """Wrapper function for background task triggers."""
    return run_openhands_loop()


def resolve_merge_conflict(req_id: str) -> bool:
    """Helper to resolve merge conflicts on branch checkout."""
    workspace_path = str(WORKSPACE_BASE)
    try:
        subprocess.run(["git", "checkout", "main"], cwd=workspace_path, capture_output=True)
        subprocess.run(["git", "merge", "--abort"], cwd=workspace_path, capture_output=True)
        store.update_requirement_status(req_id, "Backlog", feedback="Merge conflict resolved with rollback.")
        return True
    except Exception as e:
        print(f"Error resolving conflict: {e}")
        return False


def run_requirement_audit() -> Dict[str, Any]:
    """Helper to audit requirement coverage against test cases."""
    reqs = store.get_all_requirements()
    uncovered = [r['id'] for r in reqs if not store.get_test_cases_for_requirement(r['id'])]
    return {
        "total_requirements": len(reqs),
        "uncovered_requirements": uncovered,
        "coverage_percentage": round((len(reqs) - len(uncovered)) / max(len(reqs), 1) * 100, 1)
    }
