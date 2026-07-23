import subprocess
import os
import json
import urllib.request
import urllib.error
import re
import time
import ast
import dotenv
import socket
import base64
import yaml
from typing import List, Dict, Any, Optional, TypedDict
from openai import OpenAI
import db.store as store
from langgraph.graph import StateGraph, START, END
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

def is_port_active(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('127.0.0.1', port))
            return True
        except Exception:
            return False

def ensure_preview_server():
    """Ensure that the dev server for the active workspace is active on port 5174."""
    PORT = 5174
    ws_path = str(WORKSPACE_BASE)

    if not os.path.exists(os.path.join(ws_path, 'package.json')):
        print(f"🤖 Preview server skipped: package.json not found in {ws_path}.")
        return None, None

    if is_port_active(PORT):
        print(f"🤖 Preview server already active on port {PORT}.")
        return None, PORT
        
    print(f"🤖 Preview server not active. Starting Vite dev server in workspace...")
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=ws_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True
    )
    
    for _ in range(30):
        if is_port_active(PORT):
            print(f"🤖 Preview server successfully started on port {PORT}.")
            time.sleep(1)
            return process, PORT
        time.sleep(0.5)
        
    process.terminate()
    raise RuntimeError(f"Failed to start preview server on port {PORT} within 15 seconds.")

def capture_app_screenshots(port, screenshot_paths):
    """Start headless Chrome, open the app, and take screenshots for multiple viewports."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    if os.path.exists("/usr/bin/chromium-browser"):
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        
    driver = webdriver.Chrome(options=chrome_options)
    try:
        url = f"http://127.0.0.1:{port}"
        print(f"🤖 Selenium navigating to {url} for screenshots...")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        time.sleep(2)
        
        # 1. Desktop viewport (1280x800)
        if "desktop" in screenshot_paths:
            driver.set_window_size(1280, 800)
            time.sleep(0.5)
            driver.save_screenshot(screenshot_paths["desktop"])
            print(f"🤖 Desktop screenshot saved to {screenshot_paths['desktop']}")
            
        # 2. Mobile viewport (375x812)
        if "mobile" in screenshot_paths:
            driver.set_window_size(375, 812)
            time.sleep(0.5)
            driver.save_screenshot(screenshot_paths["mobile"])
            print(f"🤖 Mobile screenshot saved to {screenshot_paths['mobile']}")
            
    finally:
        driver.quit()

def capture_app_screenshot(port, output_path):
    capture_app_screenshots(port, {"desktop": output_path})

def parse_docstring_fields(docstring):
    fields = {}
    lines = [line.strip() for line in docstring.split('\n')]
    
    title = ""
    for line in lines:
        if line:
            title = line
            break
    fields['title'] = title
    
    for line in lines:
        if line.lower().startswith('id:'):
            fields['id'] = line[3:].strip()
        elif line.lower().startswith('req:'):
            fields['req'] = line[4:].strip()
        elif line.lower().startswith('given:'):
            fields['given'] = line[6:].strip()
        elif line.lower().startswith('when:'):
            fields['when'] = line[5:].strip()
        elif line.lower().startswith('then:'):
            fields['then'] = line[5:].strip()
            
    return fields

def parse_test_docstrings(filepath):
    docstrings = {}
    if not os.path.exists(filepath):
        return docstrings
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings[node.name] = parse_docstring_fields(doc)
    except Exception as e:
        print(f"AST parsing failed for {filepath}: {e}")
    return docstrings


def parse_pytest_failures(stdout: str) -> dict:
    failures = {}
    idx = stdout.find("=== FAILURES ===")
    if idx == -1:
        idx = stdout.find(" FAILURES ")
    if idx == -1:
        return failures
        
    failures_text = stdout[idx:]
    import re
    matches = list(re.finditer(r'_{3,}\s*(\w+)\s*_{3,}', failures_text))
    for i, match in enumerate(matches):
        test_name = match.group(1)
        start = match.end()
        if i + 1 < len(matches):
            end = matches[i+1].start()
        else:
            end_match = re.search(r'\n={3,}', failures_text[start:])
            if end_match:
                end = start + end_match.start()
            else:
                end = len(failures_text)
        failures[test_name] = failures_text[start:end].strip()
    return failures


def run_pytest(workspace_base, test_target: str = None):
    # Retrieve project settings
    settings = get_project_settings()
    test_runner_cfg = settings.get('test_runner', {})
    
    # Base command (e.g., "pytest" or "pytest tests/")
    base_cmd = test_runner_cfg.get('test_command', 'pytest -v')
    
    # Auto-detect local virtual environments in the target workspace
    venv_prefix = ""
    for venv_dir in ('venv', '.venv'):
        activate_path = os.path.join(workspace_base, venv_dir, 'bin', 'activate')
        if os.path.exists(activate_path):
            venv_prefix = f"source {venv_dir}/bin/activate && "
            break

    # Build the full command string
    allure_dir = os.path.join(workspace_base, 'allure-results')
    
    # If a specific target is provided, strip any default test folder (like tests/ or tests) from the command
    if test_target:
        # Keep only the pytest command and flags, removing default directory targets
        tokens = base_cmd.split()
        cleaned_tokens = []
        for t in tokens:
            # Keep commands, executors, and options/flags, discard target folders
            if t.startswith('-') or t in ('pytest', 'python', 'python3', 'poetry', 'run', 'pip', 'pytest-3'):
                cleaned_tokens.append(t)
        # Ensure verbose mode is enabled so we can parse '::' lines from stdout
        if '-v' not in cleaned_tokens and '-vv' not in cleaned_tokens:
            cleaned_tokens.append('-v')
        cleaned_base = " ".join(cleaned_tokens)
        full_cmd = f"{venv_prefix}{cleaned_base} {test_target} --alluredir={allure_dir} --timeout=25"
    else:
        # Ensure verbose mode for general base command execution
        cmd_parts = base_cmd.split()
        if '-v' not in cmd_parts and '-vv' not in cmd_parts:
            cmd_parts.append('-v')
        full_cmd = f"{venv_prefix}{' '.join(cmd_parts)} --alluredir={allure_dir} --clean-alluredir --timeout=25"

    stdout = ""
    stderr = ""
    try:
        print(f"🚀 Running test command: {full_cmd}")
        result = subprocess.run(
            full_cmd,
            shell=True,
            executable='/bin/bash', # use bash to support source/activation
            cwd=workspace_base,
            capture_output=True,
            text=True,
            timeout=240
        )
        stdout = result.stdout
        stderr = result.stderr
        print(f"Pytest stdout length: {len(stdout)}")
        print(f"Pytest stderr length: {len(stderr)}")
    except Exception as e:
        print(f"Error running pytest: {e}")
        return [{"name": "pytest execution", "status": "Failing"}], f"Error running pytest: {e}"
        
    test_results = []
    lines = stdout.split('\n')
    for line in lines:
        if '::' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
            match = re.search(r'([^:\s]+::[^\s]+)\s+(PASSED|FAILED|ERROR)', line)
            if match:
                test_path_name = match.group(1)
                parts = test_path_name.split('::')
                test_name = parts[-1]
                file_path = parts[0]
                raw_status = match.group(2)
                status = 'Passing' if raw_status == 'PASSED' else 'Failing'
                test_results.append({
                    "name": test_name,
                    "status": status,
                    "file_path": file_path
                })
                
    if not test_results:
        fallback_file_path = test_target.split('::')[0] if test_target else ""
        if "no tests ran" in stdout.lower() or "collected 0 items" in stdout.lower():
            test_results.append({
                "name": "No tests defined",
                "status": "Failing",
                "file_path": fallback_file_path
            })
        else:
            test_results.append({
                "name": "Test Suite Execution",
                "status": "Failing",
                "file_path": fallback_file_path
            })
            
    # Extract tracebacks/errors
    failures_summary = ""
    failures_idx = stdout.find("=== FAILURES ===")
    if failures_idx == -1:
        failures_idx = stdout.find(" FAILURES ")
    errors_idx = stdout.find("=== ERRORS ===")
    if errors_idx == -1:
        errors_idx = stdout.find(" ERRORS ")
        
    parts = []
    if failures_idx != -1 or errors_idx != -1:
        indices = [idx for idx in (failures_idx, errors_idx) if idx != -1]
        start_idx = min(indices)
        failures_part = stdout[start_idx:]
        lines = failures_part.split('\n')
        for line in lines:
            if line.startswith("===") and "FAILURES" not in line and "ERRORS" not in line:
                break
            parts.append(line)
        failures_summary = "\n".join(parts)
            
    # Parse docstrings from all test files in the tests/ directory
    docstrings = {}
    tests_dir = os.path.join(workspace_base, 'tests')
    if os.path.exists(tests_dir):
        for fname in os.listdir(tests_dir):
            if fname.startswith('test_') and fname.endswith('.py'):
                fpath = os.path.join(tests_dir, fname)
                try:
                    file_docs = parse_test_docstrings(fpath)
                    rel_fpath = os.path.relpath(fpath, workspace_base)
                    for test_name, info in file_docs.items():
                        info['file_path'] = rel_fpath
                    docstrings.update(file_docs)
                except Exception as parse_err:
                    print(f"Error parsing docstrings from {fname}: {parse_err}")
    
    failures_map = parse_pytest_failures(stdout)
    for result in test_results:
        test_name = result['name']
        if test_name in docstrings:
            result.update(docstrings[test_name])
        result['failure_message'] = failures_map.get(test_name, '')
            
    return test_results, failures_summary

def load_models_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'models.yaml'))
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def load_prompt(template_name: str, variables: dict) -> str:
    prompt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'prompts'))
    prompt_path = os.path.join(prompt_dir, template_name)
    with open(prompt_path, 'r', encoding='utf-8') as f:
        template = f.read()
    return template.format(**variables)

def call_gemini(prompt, image_path=None, image_paths=None, stage=None):
    """Call LLM using OpenAI SDK based on models.yaml configuration, supporting optional visual inputs."""
    config = load_models_config()
    stage_config = config.get('stages', {}).get(stage) if stage else None
    if not stage_config:
        stage_config = config.get('default', {})
        
    model = stage_config.get('model', 'gemini-2.5-flash')
    base_url = stage_config.get('base_url', 'https://generativelanguage.googleapis.com/v1beta/openai/')
    api_key_env = stage_config.get('api_key_env', 'LLM_API_KEY')
    api_key = os.environ.get(api_key_env) or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
    
    if not api_key:
        print(f"⚠️ call_gemini: No API key found in {api_key_env}, GEMINI_API_KEY, or OPENAI_API_KEY.")
        if stage == "test_case_generation":
            return '''```python
def test_generated_bdd_spec():
    """
    Given: The application is configured
    When: Inspecting target requirement
    Then: Expected behavior should hold
    """
    assert False, "Failing TDD initial test case (LLM API key not configured)"
```'''

    client = OpenAI(api_key=api_key or "dummy-key", base_url=base_url)
    
    parts = [{"type": "text", "text": prompt}]
    
    paths_to_load = []
    if image_path:
        paths_to_load.append(image_path)
    if image_paths:
        if isinstance(image_paths, list):
            paths_to_load.extend(image_paths)
        elif isinstance(image_paths, dict):
            paths_to_load.extend(image_paths.values())
        else:
            paths_to_load.append(image_paths)
            
    for path in paths_to_load:
        try:
            with open(path, 'rb') as f:
                b64_data = base64.b64encode(f.read()).decode('utf-8')
            parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_data}"
                }
            })
        except Exception as e:
            print(f"Error loading image {path} for LLM: {e}")
            
    messages = [{"role": "user", "content": parts}]
    last_error = None
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"    LLM API attempt {attempt + 1}/3 failed with error: {e}")
            if "Missing credentials" in str(e) or "api_key" in str(e):
                if stage == "test_case_generation":
                    return '''```python
def test_generated_bdd_spec():
    """
    Given: The application is configured
    When: Inspecting target requirement
    Then: Expected behavior should hold
    """
    assert False, "Failing TDD initial test case (LLM API key missing)"
```'''
                raise last_error
            wait_time = 15 * (attempt + 1)
            time.sleep(wait_time)
            
    raise last_error

def select_relevant_files(workspace_base, ticket_desc, test_code_or_desc):
    """Fast pre-check using LLM to select the top 3-5 most relevant source files to minimize prompt size on attempt 1."""
    all_files = []
    for root, dirs, files in os.walk(os.path.join(workspace_base, 'src')):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'assets']]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, workspace_base)
            all_files.append(rel_path.replace('\\', '/'))
            
    index_path = os.path.join(workspace_base, 'index.html')
    if os.path.exists(index_path):
        all_files.append('index.html')
        
    if not all_files:
        return []
        
    prompt = f"""You are an expert developer agent analyzing a repository.
Your task is to select the most relevant source files that need to be read or modified to implement the following ticket or fix the following test case.

--- TICKET DESCRIPTION ---
{ticket_desc}

--- TEST CASE / DETAILS ---
{test_code_or_desc}

--- SOURCE FILES IN THE PROJECT ---
{chr(10).join(f"- {f}" for f in all_files)}

Respond ONLY with a JSON array of relative file paths (from the list above) that are most relevant. Do NOT wrap the JSON in markdown fences, and do not include any other text.
Example:
[
  "src/App.tsx",
  "src/App.css"
]
"""
    try:
        response = call_gemini(prompt, stage="code_generation")
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:-3].strip()
        elif response.startswith("```"):
            response = response[3:-3].strip()
            
        selected = json.loads(response)
        if isinstance(selected, list):
            valid_selected = [f for f in selected if f.replace('\\', '/') in all_files]
            if valid_selected:
                return valid_selected
    except Exception as e:
        print(f"Error in select_relevant_files LLM selector: {e}")
        
    fallback = []
    for candidate in ["src/App.tsx", "src/App.css", "src/index.css", "index.html"]:
        if candidate in all_files:
            fallback.append(candidate)
    return fallback

def update_system_spec(workspace_base, ticket_desc, git_diff):
    """Auto-generates or updates system_spec.md in requirements/ to keep a high-level layout description of the app."""
    spec_dir = os.path.join(workspace_base, 'requirements')
    os.makedirs(spec_dir, exist_ok=True)
    spec_path = os.path.join(spec_dir, 'system_spec.md')
    
    current_spec = ""
    if os.path.exists(spec_path):
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                current_spec = f.read()
        except Exception:
            pass

    prompt = f"""You are an automated system architect keeping a layout and style specification sheet of the application up to date.
Below is the existing system specification sheet (which may be empty if this is the first run), the ticket that was just implemented, and the git diff of the implementation.

Your task is to update the system specification sheet (in Markdown format) to document:
1. The page layout (elements, fixed headers, content containers).
2. Key CSS classes and their functions.
3. Design tokens (colors used, text styling, heights, paddings).
4. Responsiveness behavior on mobile vs desktop.

Ensure you retain existing documentation about components that were NOT changed by the diff. Keep the description concise but clear.

--- CURRENT SPECIFICATION SHEET ---
{current_spec}

--- TICKET COMPLETED ---
{ticket_desc}

--- GIT DIFF OF CHANGES ---
{git_diff}

Respond ONLY with the complete updated system specification markdown text. Do NOT wrap it in markdown fences, and do not write any other explanation.
"""
    try:
        updated_spec = call_gemini(prompt, stage="code_generation").strip()
        if updated_spec.startswith("```markdown"):
            updated_spec = updated_spec[11:-3].strip()
        elif updated_spec.startswith("```"):
            updated_spec = updated_spec[3:-3].strip()
            
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(updated_spec)
        print(f"✅ Auto-updated system_spec.md for the workspace app.")
    except Exception as e:
        print(f"Failed to update system specification sheet: {e}")

def read_workspace_files(include_tests=False, limit_files=None):
    context = []
    
    # Prepend the system specification spec sheet if it exists
    spec_path = os.path.join(WORKSPACE_BASE, 'requirements', 'system_spec.md')
    if os.path.exists(spec_path):
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                context.append(f"--- SYSTEM SPECIFICATION (WIP) ---\n{f.read()}\n")
        except Exception:
            pass

    # Gather source files
    for root, dirs, files in os.walk(os.path.join(WORKSPACE_BASE, 'src')):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'assets']]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, WORKSPACE_BASE)
            rel_path_norm = rel_path.replace('\\', '/')
            if limit_files is not None:
                limit_files_norm = [lf.replace('\\', '/') for lf in limit_files]
                if rel_path_norm not in limit_files_norm:
                    continue
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                context.append(f"--- FILE: {rel_path_norm} ---\n{content}\n")
            except Exception:
                pass

    index_path = os.path.join(WORKSPACE_BASE, 'index.html')
    if os.path.exists(index_path):
        rel_index = 'index.html'
        if limit_files is None or rel_index in [lf.replace('\\', '/') for lf in limit_files]:
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    context.append(f"--- FILE: index.html ---\n{f.read()}\n")
            except Exception:
                pass

    if include_tests:
        tests_dir = os.path.join(WORKSPACE_BASE, 'tests')
        if os.path.exists(tests_dir):
            for fname in os.listdir(tests_dir):
                if fname.startswith('test_') and fname.endswith('.py'):
                    fpath = os.path.join(tests_dir, fname)
                    rel_path = os.path.relpath(fpath, WORKSPACE_BASE).replace('\\', '/')
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        context.append(f"--- FILE: {rel_path} ---\n{content}\n")
                    except Exception:
                        pass

    return "\n".join(context)

def parse_file_blocks(response_text):
    files = {}
    lines = response_text.split('\n')
    current_file = None
    current_content = []
    
    for line in lines:
        if line.startswith('=== FILE:') and line.endswith('==='):
            if current_file:
                files[current_file] = '\n'.join(current_content)
            current_file = line.replace('=== FILE:', '').replace('===', '').strip()
            current_content = []
        elif line.strip() == '=== END FILE ===' and current_file:
            files[current_file] = '\n'.join(current_content)
            current_file = None
            current_content = []
        elif current_file is not None:
            current_content.append(line)
            
    if current_file and current_content:
        files[current_file] = '\n'.join(current_content)
        
    return files

def run_vision_validation(ticket_id, title, description, screenshot_paths, file_blocks):
    code_context = ""
    for path, content in file_blocks.items():
        code_context += f"--- FILE: {path} ---\n{content}\n\n"
        
    try:
        prompt = load_prompt("visual_qa.md", {
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "code_context": code_context
        })
        response_text = call_gemini(prompt, image_paths=screenshot_paths, stage="visual_qa")
        
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        result = json.loads(clean_text)
        return result
    except Exception as e:
        print(f"🤖 Vision Validation API call failed: {e}")
        return {
            "passed": False,
            "reasoning_and_discrepancy": f"Vision validation failed to execute: {str(e)}",
            "test_adequacy": "Unknown",
            "correction_advice": "Retry the generation and ensure code compiles and runs."
        }

def log_validation_fault(ticket_id, attempt, requirement_desc, file_blocks, screenshot_path, vision_result):
    audit_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', 'visual_validation_audit.json'))
    
    audit_logs = []
    if os.path.exists(audit_file):
        try:
            with open(audit_file, 'r') as f:
                audit_logs = json.load(f)
        except Exception:
            pass
            
    code_context = {path: content for path, content in file_blocks.items()}
    
    new_entry = {
        "ticket_id": ticket_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attempt": attempt,
        "requirement": requirement_desc,
        "code_changes": code_context,
        "screenshot_path": screenshot_path,
        "vision_analysis": vision_result
    }
    
    audit_logs.append(new_entry)
    
    try:
        os.makedirs(os.path.dirname(audit_file), exist_ok=True)
        with open(audit_file, 'w') as f:
            json.dump(audit_logs, f, indent=2)
        print(f"🤖 Logged validation fault to central audit: {audit_file}")
    except Exception as e:
        print(f"🤖 Failed to write audit log: {e}")

def sync_test_results(test_results):
    conn = store.get_connection()
    try:
        # Load title -> (requirement_id, test_case_id) mapping
        rows = conn.execute("SELECT title, id, requirement_id FROM test_cases").fetchall()
        title_map = {row['title']: (row['requirement_id'], row['id']) for row in rows}
        
        # Sync file-level test cases (Linked test: <basename>)
        linked_rows = conn.execute("SELECT id, file_path FROM test_cases WHERE title LIKE 'Linked test:%'").fetchall()
        for row in linked_rows:
            row_path = row['file_path']
            if not row_path:
                continue
            norm_row_path = os.path.normpath(row_path)
            file_results = [
                t for t in test_results
                if t.get('file_path') and os.path.normpath(t['file_path']) == norm_row_path
            ]
            if file_results:
                overall_status = "pass"
                if any(t.get('status') == 'Failing' for t in file_results) or any(t.get('name') == 'No tests defined' for t in file_results):
                    overall_status = "fail"
                conn.execute(
                    "UPDATE test_cases SET last_result = ? WHERE id = ?",
                    (overall_status, row['id'])
                )
        conn.commit()
    except Exception as e:
        print(f"⚠️ sync_test_results: Failed to read/update test_cases mapping: {e}")
        title_map = {}
    finally:
        conn.close()

    grouped = {}
    for t in test_results:
        test_name = t.get('name')
        # Try to resolve req ID from DB mapping
        req_id = None
        if test_name in title_map:
            req_id = title_map[test_name][0]
            t['id'] = title_map[test_name][1]
        
        # Fallback to 'req' tag if present in result dictionary
        if not req_id:
            req_id = t.get('req')
            
        if req_id:
            req_ids = [r.strip() for r in str(req_id).split(',') if r.strip()]
            for rid in req_ids:
                grouped.setdefault(rid, []).append(t)
                
    for req_id, tests in grouped.items():
        store._upsert_test_results(req_id, tests)


# ── LangGraph Architecture ───────────────────────────────────────────────────

class AgentState(TypedDict):
    ticket_id: str
    item: Dict[str, Any]
    attempt: int
    max_attempts: int
    qa_feedback: str
    success: bool
    branch_name: str
    active_port: int
    started_server_proc: Any
    file_blocks: Dict[str, str]
    screenshot_paths: Dict[str, str]
    test_results: List[Dict[str, Any]]
    log_file_path: str
    task_desc: str
    feedback_note: str
    bug_test_instruction: str
    parent_id: str


def prepare_branch_node(state: AgentState) -> Dict[str, Any]:
    ticket_id = state['ticket_id']
    item = state['item']
    print(f"🤖 [LangGraph] Node: Prepare Branch | Processing {ticket_id}")
    update_agent_status(active=True, ticket_id=ticket_id, step="Preparing branch", attempt=0)
    
    # Immediately move ticket status in SQLite to InProgress
    item['status'] = 'InProgress'
    store.update_requirement(ticket_id, {'status': 'InProgress'})
    
    branch_name = f"ticket/{ticket_id}"
    branch_exists_res = subprocess.run(
        ["git", "show-ref", f"refs/heads/{branch_name}"],
        cwd=WORKSPACE_BASE, capture_output=True
    )
    if branch_exists_res.returncode == 0:
        subprocess.run(["git", "checkout", branch_name], cwd=WORKSPACE_BASE, capture_output=True)
    else:
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
        subprocess.run(["git", "branch", "-D", branch_name], cwd=WORKSPACE_BASE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=WORKSPACE_BASE, capture_output=True)
        
    return {"branch_name": branch_name, "item": item}


def code_generation_node(state: AgentState) -> Dict[str, Any]:
    ticket_id = state['ticket_id']
    attempt = state['attempt'] + 1
    max_attempts = state['max_attempts']
    log_file_path = state['log_file_path']
    task_desc = state['task_desc']
    feedback_note = state['feedback_note']
    bug_test_instruction = state['bug_test_instruction']
    parent_id = state['parent_id']
    qa_feedback = state['qa_feedback']
    
    print(f"🤖 [LangGraph] Node: Code Generation | Attempt {attempt}/{max_attempts}")
    update_agent_status(active=True, ticket_id=ticket_id, step="Generating code changes", attempt=attempt, max_attempts=max_attempts)
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"\n=========================================\n")
        log_file.write(f"🔄 ATTEMPT {attempt}/{max_attempts}\n")
        log_file.write(f"=========================================\n")
        log_file.write(f"Calling Gemini API for code generation...\n")
        
    # Resolve the correct test file path linked to this ticket/requirement
    test_file_path = None
    conn = store.get_connection()
    row = conn.execute("SELECT file_path FROM test_cases WHERE requirement_id = ?", (ticket_id,)).fetchone()
    if row and row['file_path']:
        test_file_path = row['file_path']
    elif parent_id and parent_id != 'N/A':
        row = conn.execute("SELECT file_path FROM test_cases WHERE requirement_id = ?", (parent_id,)).fetchone()
        if row and row['file_path']:
            test_file_path = row['file_path']
    conn.close()
    
    if not test_file_path:
        if parent_id and parent_id != 'N/A':
            test_file_path = f"tests/test_{parent_id}.py"
        else:
            test_file_path = f"tests/test_{ticket_id}.py"

    # Load test case context
    test_context = ""
    full_test_path = os.path.join(WORKSPACE_BASE, test_file_path)
    if os.path.exists(full_test_path):
        try:
            with open(full_test_path, 'r', encoding='utf-8') as f:
                test_context = f"\nHere are the existing test cases associated with this ticket that your code changes must pass:\n--- TEST FILE: {test_file_path} ---\n{f.read()}\n"
        except Exception as e:
            print(f"Failed to read test file {test_file_path}: {e}")

    # Implement Staged Context
    if attempt == 1:
        selected_files = select_relevant_files(WORKSPACE_BASE, task_desc, test_context or bug_test_instruction)
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Attempt 1: Targeted context selected: {json.dumps(selected_files)}\n")
        current_workspace_context = read_workspace_files(include_tests=True, limit_files=selected_files)
    else:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Attempt {attempt}: Expanding context to full workspace source files.\n")
        current_workspace_context = read_workspace_files(include_tests=True)
    
    feedback_note_attempt = feedback_note
    if attempt > 1 and qa_feedback:
        feedback_note_attempt = feedback_note + f"\n\n{qa_feedback}\n"
        
    attempt_prompt = load_prompt("code_generation.md", {
        "current_workspace_context": current_workspace_context,
        "task_desc": task_desc,
        "feedback_note_attempt": feedback_note_attempt,
        "bug_test_instruction": bug_test_instruction,
        "parent_id": parent_id,
        "test_file_path": test_file_path,
        "test_context": test_context
    })
    
    response_text = call_gemini(attempt_prompt, stage="code_generation")
    file_blocks = parse_file_blocks(response_text)
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Gemini responded. Writing files...\n")
        
    for file_path, content in file_blocks.items():
        full_path = os.path.join(WORKSPACE_BASE, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"   Wrote file: {file_path}\n")
            
    return {"attempt": attempt, "file_blocks": file_blocks}


def test_runner_node(state: AgentState) -> Dict[str, Any]:
    ticket_id = state['ticket_id']
    attempt = state['attempt']
    log_file_path = state['log_file_path']
    
    print(f"🤖 [LangGraph] Node: Test Runner | Running tests for {ticket_id}")
    update_agent_status(active=True, ticket_id=ticket_id, step="Running automated tests", attempt=attempt)
    
    with open(log_file_path, 'a') as log_file:
        log_file.write("Running pytest suite...\n")
        
    test_results, failures_summary = run_pytest(WORKSPACE_BASE)
    sync_test_results(test_results)
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Test execution complete. Results: {json.dumps(test_results)}\n")
        if failures_summary:
            log_file.write(f"Pytest failures/errors traceback:\n{failures_summary}\n")
        
    # Check if all tests pass
    all_passing = all(t.get('status') == 'Passing' for t in test_results)
    
    qa_feedback = ""
    if not all_passing:
        failed_tests = [t.get('name') for t in test_results if t.get('status') == 'Failing']
        qa_feedback = f"""AUTOMATED QA FEEDBACK (Attempt {attempt} failed):
    Your code changes failed automated pytest verification.
    Failed tests: {', '.join(failed_tests)}"""
        if failures_summary:
            qa_feedback += f"\n\nPytest Failure details:\n{failures_summary}"
        qa_feedback += "\n\nPlease review the test failures and correct the implementation and/or test assertions."
    
    return {"test_results": test_results, "qa_feedback": qa_feedback}


def visual_qa_node(state: AgentState) -> Dict[str, Any]:
    ticket_id = state['ticket_id']
    attempt = state['attempt']
    item = state['item']
    log_file_path = state['log_file_path']
    active_port = state['active_port']
    file_blocks = state['file_blocks']
    
    print(f"🤖 [LangGraph] Node: Visual QA | Validating UI design for {ticket_id}")
    update_agent_status(active=True, ticket_id=ticket_id, step="Running visual validation", attempt=attempt)
    
    screenshot_paths = {
        "desktop": os.path.join(os.path.dirname(log_file_path), f"screenshot_{ticket_id}_attempt_{attempt}_desktop.png"),
        "mobile": os.path.join(os.path.dirname(log_file_path), f"screenshot_{ticket_id}_attempt_{attempt}_mobile.png")
    }
    
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write("Capturing app screenshots (desktop and mobile) using Selenium...\n")
        capture_app_screenshots(active_port, screenshot_paths)
    except Exception as screenshot_err:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"❌ Failed to capture screenshots: {screenshot_err}\n")
        qa_feedback = f"AUTOMATED QA FEEDBACK (Attempt {attempt} failed):\nFailed to capture screenshots of preview app: {str(screenshot_err)}"
        return {"success": False, "qa_feedback": qa_feedback, "screenshot_paths": screenshot_paths}
        
    with open(log_file_path, 'a') as log_file:
        log_file.write("Calling Gemini Vision API to validate layout and responsiveness...\n")
        
    vision_result = run_vision_validation(
        ticket_id,
        item.get('title'),
        item.get('description'),
        screenshot_paths,
        file_blocks
    )
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Vision validation response: {json.dumps(vision_result)}\n")
        
    if vision_result.get('passed') is True:
        with open(log_file_path, 'a') as log_file:
            log_file.write("✅ Visual validation passed successfully!\n")
        return {"success": True, "screenshot_paths": screenshot_paths}
    else:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"❌ Visual validation failed: {vision_result.get('reasoning_and_discrepancy')}\n")
            
        log_validation_fault(
            ticket_id,
            attempt,
            item.get('description'),
            file_blocks,
            screenshot_paths,
            vision_result
        )
        
        qa_feedback = f"""AUTOMATED QA FEEDBACK (Attempt {attempt} failed):
    Your code changes did not pass the visual verification gate.
    Visual Discrepancies: {vision_result.get('reasoning_and_discrepancy')}
    Test Adequacy: {vision_result.get('test_adequacy')}
    Correction Advice: {vision_result.get('correction_advice')}
    Please revise your code, styles, and test assertions to address these issues."""
    
        return {"success": False, "qa_feedback": qa_feedback, "screenshot_paths": screenshot_paths}


def finalize_node(state: AgentState) -> Dict[str, Any]:
    ticket_id = state['ticket_id']
    item = state['item']
    success = state['success']
    log_file_path = state['log_file_path']
    started_server_proc = state['started_server_proc']
    attempt = state['attempt']
    qa_feedback = state['qa_feedback']
    test_results = state['test_results']
    
    print(f"🤖 [LangGraph] Node: Finalize | Concluding run (Success: {success})")
    
    if started_server_proc:
        try:
            started_server_proc.terminate()
        except Exception:
            pass
        
    if success:
        update_agent_status(active=True, ticket_id=ticket_id, step="Committing changes", attempt=attempt)
        
        # Get git diff before committing so LLM knows what changed to update system spec
        diff_res = subprocess.run(["git", "diff", "main"], cwd=WORKSPACE_BASE, capture_output=True, text=True)
        git_diff = diff_res.stdout
        
        try:
            update_system_spec(WORKSPACE_BASE, f"Ticket ID: {ticket_id}\nTitle: {item['title']}\nDescription: {item.get('description', '')}", git_diff)
        except Exception as spec_err:
            print(f"Error updating system spec: {spec_err}")
            
        subprocess.run(["git", "add", "-A"], cwd=WORKSPACE_BASE, capture_output=True)
        commit_msg = f"feat({ticket_id}): {item['title']}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKSPACE_BASE, capture_output=True)
        
        item['status'] = 'Review'
        item['feedback'] = ""
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"✅ Committed changes: {commit_msg}\n")
            log_file.write(f"🎉 Agent completed successfully!\n")
        print(f"  ✅ Agent completed {ticket_id} successfully.")
    else:
        # Revert changes to prevent unclean state on failure
        subprocess.run(["git", "checkout", "--", "."], cwd=WORKSPACE_BASE, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=WORKSPACE_BASE, capture_output=True)
        
        item['status'] = 'Backlog'
        item['feedback'] = f"QA Validation failed after {attempt} attempts. Final QA Feedback:\n{qa_feedback}"
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"❌ Visual validation failed after all attempts. Reverting code and returning to Backlog.\n")
        print(f"  ❌ Agent failed QA validation for {ticket_id}.")
        
    subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)

    if success and test_results:
        # Replace (not just upsert) so stale fail rows from previous runs are cleared
        parent_id = state.get('parent_id', 'N/A')
        store.replace_test_results_for_requirement(ticket_id, test_results)
        if parent_id and parent_id != 'N/A':
            store.replace_test_results_for_requirement(parent_id, test_results)

    store.update_requirement_status(ticket_id, item['status'], feedback=item.get('feedback'), tests=test_results)
    
    return {}


def route_after_test(state: AgentState):
    all_passing = all(t.get('status') == 'Passing' for t in state['test_results'])
    if not all_passing:
        if state['attempt'] < state['max_attempts']:
            return "code_generation"
        else:
            return "finalize"
    return "visual_qa"


def route_after_visual(state: AgentState):
    if state['success']:
        return "finalize"
    else:
        if state['attempt'] < state['max_attempts']:
            return "code_generation"
        else:
            return "finalize"


# Define LangGraph StateGraph
workflow = StateGraph(AgentState)
workflow.add_node("prepare_branch", prepare_branch_node)
workflow.add_node("code_generation", code_generation_node)
workflow.add_node("test_runner", test_runner_node)
workflow.add_node("visual_qa", visual_qa_node)
workflow.add_node("finalize", finalize_node)

workflow.set_entry_point("prepare_branch")
workflow.add_edge("prepare_branch", "code_generation")
workflow.add_edge("code_generation", "test_runner")

workflow.add_conditional_edges(
    "test_runner",
    route_after_test,
    {
        "code_generation": "code_generation",
        "visual_qa": "visual_qa",
        "finalize": "finalize"
    }
)

workflow.add_conditional_edges(
    "visual_qa",
    route_after_visual,
    {
        "code_generation": "code_generation",
        "finalize": "finalize"
    }
)

workflow.add_edge("finalize", END)
compiled_graph = workflow.compile()


# ── Business Flow Actions ────────────────────────────────────────────────────

def run_openhands_loop(target_ticket_id: str = None):
    print("🤖 Agent Orchestrator: Waking up...")
    update_agent_status(active=True, step="Scanning Backlog", ticket_id=None, attempt=0)

    # Reset any tickets left stuck in InProgress from a previous crashed run
    try:
        stale = [r for r in store.get_all_requirements() if r.get('status') == 'InProgress']
        for r in stale:
            print(f"🤖 Agent Orchestrator: Resetting stale InProgress ticket {r['id']} → Backlog")
            store.update_requirement(r['id'], {'status': 'Backlog'})
    except Exception as cleanup_err:
        print(f"🤖 Agent Orchestrator: Cleanup error: {cleanup_err}")

    try:
        reqs = store.get_requirements_for_frontend()
            
        if target_ticket_id:
            ready_items = [r for r in reqs if r.get('id') == target_ticket_id]
            if not ready_items:
                print(f"🤖 Agent Orchestrator: Target ticket {target_ticket_id} not found in backlog or requirements.")
                return
        else:
            items_to_process = [r for r in reqs if r.get('status') == 'Backlog' and r.get('type') in ('Task', 'Bug')]
            status_map = {r['id']: r.get('status', 'Backlog') for r in reqs}
            ready_items = []
            for item in items_to_process:
                deps = item.get('dependencies', [])
                incomplete_deps = [dep for dep in deps if status_map.get(dep) != 'Done']
                if incomplete_deps:
                    print(f"🤖 Agent Orchestrator: Skipping {item['id']} because of incomplete dependencies: {incomplete_deps}")
                    continue
                    
                if item.get('type') == 'Bug':
                    parent_id = item.get('parentId')
                    if parent_id:
                        sibling_tasks = [r for r in reqs if r.get('parentId') == parent_id and r.get('type') == 'Task']
                        incomplete_siblings = [r['id'] for r in sibling_tasks if r.get('status') != 'Done']
                        if incomplete_siblings:
                            print(f"🤖 Agent Orchestrator: Skipping Bug {item['id']} because parent requirement tasks {incomplete_siblings} are not Done.")
                            continue
                            
                # Allow requirements to be processed if they have test cases defined
                if item.get('type') == 'Requirement' and not item.get('tests'):
                    continue
                    
                ready_items.append(item)
        
        if not ready_items:
            print("🤖 Agent Orchestrator: No ready backlog tasks to process.")
            return
            
        for item in ready_items:
            ticket_id = item['id']
            log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, f"{ticket_id}.log")
            
            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                log_file.write(f"🤖 Agent starting work on: {item['title']}\n")
                
            # Setup task variables
            parent_id = item.get('parentId', 'N/A')
            is_bug = item.get('type') == 'Bug'
            
            # Resolve test file path dynamically
            test_file_path = None
            conn = store.get_connection()
            row = conn.execute("SELECT file_path FROM test_cases WHERE requirement_id = ?", (ticket_id,)).fetchone()
            if row and row['file_path']:
                test_file_path = row['file_path']
            elif parent_id and parent_id != 'N/A':
                row = conn.execute("SELECT file_path FROM test_cases WHERE requirement_id = ?", (parent_id,)).fetchone()
                if row and row['file_path']:
                    test_file_path = row['file_path']
            conn.close()
            
            if not test_file_path:
                if parent_id and parent_id != 'N/A':
                    test_file_path = f"tests/test_{parent_id}.py"
                else:
                    test_file_path = f"tests/test_{ticket_id}.py"
            
            bug_context = ""
            bug_test_instruction = ""
            if is_bug:
                parent_req = next((r for r in reqs if r['id'] == parent_id), None)
                parent_desc = parent_req.get('description', '') if parent_req else 'N/A'
                bug_context = (
                    f"\nThis is a BUG report. Your task is to fix this bug.\n"
                    f"The parent requirement defines the expected behavior of this feature:\n"
                    f"{parent_desc}\n"
                )
                bug_test_instruction = (
                    f"\nSince this is a BUG, you MUST write a test case in `{test_file_path}` "
                    "that specifically asserts the correct behavior to reproduce/verify the bug fix.\n"
                )
                
            task_desc = f"Ticket ID: {ticket_id}\nParent Requirement ID: {parent_id}\nTitle: {item.get('title')}\nDescription: {item.get('description')}\n"
            if is_bug:
                task_desc += bug_context
                
            feedback_note = ""
            if item.get('feedback'):
                feedback_note = f"\nCRITICAL FEEDBACK FROM PM on previous attempt: {item['feedback']}\n"
                
            started_server_proc, active_port = ensure_preview_server()
            
            # Setup initial StateGraph dict
            initial_state = {
                "ticket_id": ticket_id,
                "item": item,
                "attempt": 0,
                "max_attempts": 3,
                "qa_feedback": "",
                "success": False,
                "branch_name": "",
                "active_port": active_port,
                "started_server_proc": started_server_proc,
                "file_blocks": {},
                "screenshot_paths": {},
                "test_results": [],
                "log_file_path": log_file_path,
                "task_desc": task_desc,
                "feedback_note": feedback_note,
                "bug_test_instruction": bug_test_instruction,
                "parent_id": parent_id
            }
            
            try:
                # Invoke the LangGraph pipeline
                compiled_graph.invoke(initial_state)
            except Exception as e:
                print(f"❌ LangGraph execution failed for {ticket_id}: {e}")
                if started_server_proc:
                    try:
                        started_server_proc.terminate()
                    except Exception:
                        pass
                # Rollback on fatal crash
                subprocess.run(["git", "checkout", "--", "."], cwd=WORKSPACE_BASE, capture_output=True)
                subprocess.run(["git", "clean", "-fd"], cwd=WORKSPACE_BASE, capture_output=True)
                item['status'] = 'Backlog'
                item['feedback'] = f"LangGraph pipeline crash: {str(e)}"
                store.update_requirement_status(ticket_id, 'Backlog', feedback=item['feedback'])
                
        print("🤖 Agent Orchestrator: Finished processing all tasks.")
    finally:
        update_agent_status(active=False, step="Idle", ticket_id=None, attempt=0)

def resolve_merge_conflict(ticket_id):
    print(f"🤖 Merge Agent: Starting conflict resolution for {ticket_id}")
    update_agent_status(active=True, ticket_id=ticket_id, step="Conflict Resolution", attempt=1, max_attempts=1)
    
    try:
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"{ticket_id}.log")
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"\n⚡ --- AUTOMATED MERGE AGENT ACTIVATED ---\n")
            log_file.write(f"Merge conflict detected during merge of ticket/{ticket_id}.\n")
            log_file.write(f"Identifying conflicted files...\n")
            
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"], 
                cwd=WORKSPACE_BASE, capture_output=True, text=True, check=True
            )
            conflicted_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
            
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Conflicted files found: {conflicted_files}\n")
                
            for fname in conflicted_files:
                file_path = os.path.join(WORKSPACE_BASE, fname)
                if not os.path.exists(file_path):
                    continue
                    
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"Reading content of {fname}...\n")
                    
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"Calling Gemini to resolve conflicts in {fname}...\n")
                    
                prompt = load_prompt("merge_resolution.md", {
                    "fname": fname,
                    "content": content
                })
                resolved_content = call_gemini(prompt, stage="merge_resolution").strip()
                
                if resolved_content.startswith("```"):
                    lines = resolved_content.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    resolved_content = "\n".join(lines)
                    
                with open(file_path, 'w') as f:
                    f.write(resolved_content)
                    
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"✅ Resolved and saved: {fname}\n")
                    
                subprocess.run(["git", "add", fname], cwd=WORKSPACE_BASE, check=True)
                
            with open(log_file_path, 'a') as log_file:
                log_file.write("Running pytest suite to verify resolution...\n")
                
            test_results, _ = run_pytest(WORKSPACE_BASE)
            all_passing = all(t.get('status') == 'Passing' for t in test_results)
            sync_test_results(test_results)
            
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Pytest results: {json.dumps(test_results)}\n")
                
            if all_passing:
                with open(log_file_path, 'a') as log_file:
                    log_file.write("All tests passed! Finalizing git merge...\n")
                    
                subprocess.run(
                    ["git", "commit", "-m", f"Merge branch 'ticket/{ticket_id}' (auto-resolved)"], 
                    cwd=WORKSPACE_BASE, check=True
                )
                subprocess.run(["git", "branch", "-d", f"ticket/{ticket_id}"], cwd=WORKSPACE_BASE)
                
                store.update_requirement_status(ticket_id, 'Done', feedback="", tests=test_results)
                        
                with open(log_file_path, 'a') as log_file:
                    log_file.write("🎉 Conflict resolved successfully and merged!\n")
            else:
                with open(log_file_path, 'a') as log_file:
                    log_file.write("❌ Tests failed after merge resolution. Aborting merge...\n")
                    
                subprocess.run(["git", "merge", "--abort"], cwd=WORKSPACE_BASE)
                subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE)
                
                failed_test_names = [t.get('name') for t in test_results if t.get('status') != 'Passing']
                feedback = f"Automated merge failed: tests {failed_test_names} failed after conflict resolution."
                
                store.update_requirement_status(ticket_id, 'Review', feedback=feedback, tests=test_results)
                        
        except Exception as e:
            print(f"❌ Error in merge resolution agent: {e}")
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"❌ Exception in merge agent: {str(e)}. Aborting merge...\n")
                
            try:
                subprocess.run(["git", "merge", "--abort"], cwd=WORKSPACE_BASE)
                subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE)
            except Exception:
                pass
                
            store.update_requirement_status(ticket_id, 'Review', feedback=f"Automated merge failed with error: {str(e)}")
    finally:
        update_agent_status(active=False, step="Idle", ticket_id=None, attempt=0)

def run_requirement_audit(req_id: str):
    print(f"🤖 Audit Agent: Auditing requirement {req_id}...")
    update_agent_status(active=True, ticket_id=req_id, step="Auditing Requirement", attempt=1, max_attempts=1)
    
    try:
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"audit_{req_id}.log")
        
        with open(log_file_path, 'w') as log_file:
            log_file.write(f"🤖 Audit Agent starting work on requirement: {req_id}\n")
            
        try:
            reqs = store.get_requirements_for_frontend()
            target_req = next((r for r in reqs if r['id'] == req_id), None)
            if not target_req:
                print(f"❌ Audit Agent failed: Requirement {req_id} not found.")
                return
                
            child_tasks = [r for r in reqs if r.get('parentId') == req_id and r.get('type') == 'Task']
            
            # Query for the test file path linked to this requirement in database
            test_file_path = None
            conn = store.get_connection()
            row = conn.execute("SELECT file_path FROM test_cases WHERE requirement_id = ?", (req_id,)).fetchone()
            conn.close()
            if row and row['file_path']:
                test_file_path = row['file_path']
            else:
                test_file_path = f"tests/test_{req_id}.py"

            test_filepath = os.path.join(WORKSPACE_BASE, test_file_path)
            test_code = ""
            if os.path.exists(test_filepath):
                with open(test_filepath, 'r', encoding='utf-8') as f:
                    test_code = f.read()
                    
            workspace_context = read_workspace_files(include_tests=True)
            
            existing_tasks_summary = json.dumps([
                {"id": t['id'], "title": t['title'], "description": t['description'], "status": t.get('status')}
                for t in child_tasks
            ], indent=2)
            
            prompt = load_prompt("requirement_audit.md", {
                "req_id": req_id,
                "title": target_req.get('title'),
                "description": target_req.get('description'),
                "existing_tasks_summary": existing_tasks_summary,
                "workspace_context": workspace_context,
                "test_code": test_code,
                "test_file_path": test_file_path
            })
            
            with open(log_file_path, 'a') as log_file:
                log_file.write("Calling Gemini API...\n")
                
            response_text = call_gemini(prompt, stage="requirement_audit").strip()
            
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Gemini raw response:\n{response_text}\n")
                
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
                
            audit_result = json.loads(response_text)
            
            new_tasks = audit_result.get('new_tasks', [])
            update_tasks = audit_result.get('update_tasks', [])
            updated_test_code = audit_result.get('updated_test_code', '')
            
            if updated_test_code:
                os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
                with open(test_filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_test_code)
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"✅ Updated {test_file_path}\n")
                    
                subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
                subprocess.run(["git", "add", test_file_path], cwd=WORKSPACE_BASE, capture_output=True)
                subprocess.run(["git", "commit", "-m", f"test(audit): update tests for requirement {req_id}"], cwd=WORKSPACE_BASE, capture_output=True)
                with open(log_file_path, 'a') as log_file:
                    log_file.write("✅ Committed tests update to main\n")
                    
            import random
            changes_made = False
            
            for task in new_tasks:
                task_id = f"REQ-{random.randint(1000, 9999)}"
                store.create_requirement({
                    "id": task_id,
                    "title": task.get('title', 'Audit Generated Task'),
                    "description": task.get('description', 'Task description'),
                    "priority": "Med",
                    "status": "Backlog",
                    "type": "Task",
                    "parentId": req_id,
                    "dependencies": [],
                    "assignedAgents": ["Frontend"]
                })
                changes_made = True
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"➕ Created new task {task_id}: {task['title']}\n")
                    
            for task in update_tasks:
                t_id = task.get('id')
                t_desc = task.get('description')
                store.update_requirement(t_id, {'description': t_desc, 'status': 'Backlog'})
                changes_made = True
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"✏️ Updated task {t_id} and reset to Backlog\n")
                        
            if updated_test_code or changes_made:
                test_results, _ = run_pytest(WORKSPACE_BASE)
                sync_test_results(test_results)
                        
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"✅ Updated test execution states in database\n")
                    
            if changes_made:
                with open(log_file_path, 'a') as log_file:
                    log_file.write("🚀 Backlog updated. Dispatched developer agent.\n")
                run_openhands_loop()
            else:
                with open(log_file_path, 'a') as log_file:
                    log_file.write("No backlog changes needed. Audit complete.\n")
                    
        except Exception as e:
            print(f"❌ Error in requirement audit agent: {e}")
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"❌ Exception in audit agent: {str(e)}\n")
    finally:
        update_agent_status(active=False, step="Idle", ticket_id=None, attempt=0)
