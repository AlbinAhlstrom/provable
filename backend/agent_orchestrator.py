import subprocess
import os
import json
import urllib.request
import urllib.error
import re
import time
import ast

REQUIREMENTS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'requirements.json'))
WORKSPACE_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
API_KEY = os.environ.get("LLM_API_KEY", "")

def parse_docstring_fields(docstring):
    """Extract id, req, Given, When, Then from docstring."""
    fields = {}
    lines = [line.strip() for line in docstring.split('\n')]
    
    # Title is the first non-empty line
    title = ""
    for line in lines:
        if line:
            title = line
            break
    fields['title'] = title
    
    # Parse key-value lines
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
    """Parse docstrings from a python file using AST."""
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

def run_pytest(workspace_base):
    """Run pytest in workspace and return parsed list of test results."""
    # We use the python executable in the venv to run pytest
    venv_pytest = os.path.abspath(os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'pytest'))
    if not os.path.exists(venv_pytest):
        # Fallback to system pytest
        venv_pytest = 'pytest'
        
    try:
        # Run pytest with verbose output
        result = subprocess.run(
            [venv_pytest, "-v"], 
            cwd=workspace_base, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        stdout = result.stdout
        stderr = result.stderr
        print(f"Pytest stdout:\n{stdout}")
        print(f"Pytest stderr:\n{stderr}")
    except Exception as e:
        print(f"Error running pytest: {e}")
        return [{"name": "pytest execution", "status": "Failing"}]
        
    test_results = []
    lines = stdout.split('\n')
    for line in lines:
        if '::' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line):
            # Extract test name and status
            match = re.search(r'([^:\s]+::[^\s]+)\s+(PASSED|FAILED|ERROR)', line)
            if match:
                test_path_name = match.group(1)
                # Just take the test function name for cleaner display
                test_name = test_path_name.split('::')[-1]
                raw_status = match.group(2)
                status = 'Passing' if raw_status == 'PASSED' else 'Failing'
                test_results.append({
                    "name": test_name,
                    "status": status
                })
                
    if not test_results:
        if "no tests ran" in stdout.lower() or "collected 0 items" in stdout.lower():
            test_results.append({
                "name": "No tests defined",
                "status": "Failing"
            })
        else:
            test_results.append({
                "name": "Test Suite Execution",
                "status": "Failing"
            })
            
    # Parse docstrings of tests/test_example.py to enrich results
    test_filepath = os.path.join(workspace_base, 'tests', 'test_example.py')
    docstrings = parse_test_docstrings(test_filepath)
    
    for result in test_results:
        test_name = result['name']
        if test_name in docstrings:
            result.update(docstrings[test_name])
            
    return test_results

def call_gemini(prompt):
    """Call Gemini API with retry logic for rate limiting."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 4:
                wait_time = (2 ** attempt) * 5  # 5, 10, 20, 40 seconds
                print(f"    API returned {e.code}. Retrying in {wait_time}s (attempt {attempt + 1}/5)...")
                time.sleep(wait_time)
            else:
                raise

def read_workspace_files():
    """Read all source files in the workspace to give context to the LLM."""
    context = []
    for root, dirs, files in os.walk(os.path.join(WORKSPACE_BASE, 'src')):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'assets']]
        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, WORKSPACE_BASE)
            try:
                with open(fpath, 'r') as f:
                    content = f.read()
                context.append(f"--- FILE: {rel_path} ---\n{content}\n")
            except Exception:
                pass
    # Also include index.html
    index_path = os.path.join(WORKSPACE_BASE, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            context.append(f"--- FILE: index.html ---\n{f.read()}\n")
    return "\n".join(context)

def parse_file_blocks(response_text):
    """Parse the LLM response to extract file path and content blocks.
    
    Expected format:
    === FILE: src/App.tsx ===
    <file content>
    === END FILE ===
    """
    files = {}
    lines = response_text.split('\n')
    current_file = None
    current_content = []
    
    for line in lines:
        if line.startswith('=== FILE:') and line.endswith('==='):
            # Save previous file if any
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
    
    # Handle last file if no END marker
    if current_file and current_content:
        files[current_file] = '\n'.join(current_content)
    
    return files

def run_openhands_loop():
    print("🤖 Agent Orchestrator: Waking up...")
    
    if not os.path.exists(REQUIREMENTS_FILE):
        return
    
    with open(REQUIREMENTS_FILE, 'r') as f:
        reqs = json.load(f)
        
    items_to_process = [r for r in reqs if r.get('status') == 'Backlog' and r.get('type') in ('Task', 'Bug')]
    
    # Filter items to only process those with all dependencies in 'Done' status
    status_map = {r['id']: r.get('status', 'Backlog') for r in reqs}
    ready_items = []
    for item in items_to_process:
        # Check standard dependencies
        deps = item.get('dependencies', [])
        incomplete_deps = [dep for dep in deps if status_map.get(dep) != 'Done']
        if incomplete_deps:
            print(f"🤖 Agent Orchestrator: Skipping {item['id']} because of incomplete dependencies: {incomplete_deps}")
            continue
            
        # Check bug parent requirements tasks constraints
        if item.get('type') == 'Bug':
            parent_id = item.get('parentId')
            if parent_id:
                sibling_tasks = [r for r in reqs if r.get('parentId') == parent_id and r.get('type') == 'Task']
                incomplete_siblings = [r['id'] for r in sibling_tasks if r.get('status') != 'Done']
                if incomplete_siblings:
                    print(f"🤖 Agent Orchestrator: Skipping Bug {item['id']} because parent requirement tasks {incomplete_siblings} are not Done.")
                    continue
                    
        ready_items.append(item)
    
    if not ready_items:
        print("🤖 Agent Orchestrator: No ready backlog tasks to process.")
        return
        
    for item in ready_items:
        ticket_id = item['id']
        print(f"  -> Processing {ticket_id}: {item['title']}")
        
        # 1. Prepare Git Branch
        branch_name = f"ticket/{ticket_id}"
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
        subprocess.run(["git", "branch", "-D", branch_name], cwd=WORKSPACE_BASE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=WORKSPACE_BASE, capture_output=True)
        
        # 2. Read current workspace context
        workspace_context = read_workspace_files()
        
        # 3. Build prompt for Gemini
        parent_id = item.get('parentId', 'N/A')
        is_bug = item.get('type') == 'Bug'
        
        bug_context = ""
        bug_test_instruction = ""
        if is_bug:
            # Find the parent requirement description
            parent_req = next((r for r in reqs if r['id'] == parent_id), None)
            parent_desc = parent_req.get('description', '') if parent_req else 'N/A'
            bug_context = (
                f"\nThis is a BUG report. Your task is to fix this bug.\n"
                f"The parent requirement defines the expected behavior of this feature:\n"
                f"{parent_desc}\n"
            )
            bug_test_instruction = (
                "\nSince this is a BUG, you MUST write a test case in `tests/test_example.py` "
                "that specifically asserts the correct behavior to reproduce/verify the bug fix.\n"
            )
            
        task_desc = f"Ticket ID: {ticket_id}\nParent Requirement ID: {parent_id}\nTitle: {item.get('title')}\nDescription: {item.get('description')}\n"
        if is_bug:
            task_desc += bug_context
            
        feedback_note = ""
        if item.get('feedback'):
            feedback_note = f"\nCRITICAL FEEDBACK FROM PM on previous attempt: {item['feedback']}\n"
            
        full_prompt = f"""You are a developer working on a React (Vite + TypeScript) application.

Here are the current source files in the project:
{workspace_context}

Please implement the following ticket:
{task_desc}
{feedback_note}

You MUST implement the requested changes in the codebase AND write a corresponding automated pytest test file under `tests/test_example.py` to verify the functionality.{bug_test_instruction}
The pytest tests should run in a Python environment and verify that the correct files have been modified or contain the expected code/behavior. For example, checking if specific strings, React elements, or features are present in the files (e.g., in `src/App.tsx` or other modified files).

CRITICAL REQUIREMENT FOR TEST CASES:
Each test case function in `tests/test_example.py` MUST contain a docstring formatted EXACTLY like this:
\"\"\"<Short title of the test>

<Detailed description of the test>

id: TST-<unique 4-digit number>
req: {parent_id}
Given: <Preconditions for the test>
When: <Action or triggers taken in the test>
Then: <Expected outcomes or assertions>
\"\"\"

Example:
\"\"\"Test home page title.

Verify that the app homepage renders the correct welcome message.

id: TST-1001
req: {parent_id}
Given: The App component is rendered
When: Reading the content of src/App.tsx
Then: The title text 'Hello, World!' is present
\"\"\"

Modify the necessary files to implement the requested changes. Only output files that need to be changed or created.

IMPORTANT: Respond ONLY with file blocks in this exact format (no markdown fences):
=== FILE: src/App.tsx ===
<full file content here>
=== END FILE ===
=== FILE: tests/test_example.py ===
<full pytest test content here>
=== END FILE ===

You may output multiple file blocks. Each block must contain the COMPLETE file content (not a diff). Do NOT include any other text outside the file blocks."""
        
        # Update state to InProgress
        item['status'] = 'InProgress'
        with open(REQUIREMENTS_FILE, 'w') as f:
            json.dump(reqs, f, indent=2)
        
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, f"{ticket_id}.log")
        
        try:
            with open(log_file_path, 'w') as log_file:
                log_file.write(f"🤖 Agent starting work on: {item['title']}\n")
                log_file.write(f"Calling Gemini API...\n")
            
            # 4. Call Gemini API
            response_text = call_gemini(full_prompt)
            
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Gemini responded. Parsing file blocks...\n")
                log_file.write(f"--- RAW RESPONSE ---\n{response_text}\n--- END RAW ---\n")
            
            # 5. Parse response and write files
            file_blocks = parse_file_blocks(response_text)
            
            if not file_blocks:
                with open(log_file_path, 'a') as log_file:
                    log_file.write("WARNING: No file blocks parsed from response.\n")
            
            for file_path, content in file_blocks.items():
                full_path = os.path.join(WORKSPACE_BASE, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f"✅ Wrote file: {file_path}\n")
            
            # Run pytest and parse the results
            with open(log_file_path, 'a') as log_file:
                log_file.write("Running pytest suite...\n")
            
            test_results = run_pytest(WORKSPACE_BASE)
            item['tests'] = test_results
            
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"Test execution complete. Results: {json.dumps(test_results)}\n")
            
            # 6. Git add and commit
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE_BASE, capture_output=True)
            commit_msg = f"feat({ticket_id}): {item['title']}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=WORKSPACE_BASE, capture_output=True)
            
            # Update state on success
            item['status'] = 'Review'
            item['feedback'] = ""

            with open(log_file_path, 'a') as log_file:
                log_file.write(f"✅ Committed changes: {commit_msg}\n")
                log_file.write(f"🎉 Agent completed successfully!\n")
            
            print(f"  ✅ Agent completed {ticket_id} successfully.")
            
        except Exception as e:
            print(f"  ❌ Agent failed for {ticket_id}: {e}")
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"\n❌ Agent failed: {e}\n")
            # Update state on failure
            item['status'] = 'Backlog'
            item['feedback'] = f"Agent failed: {str(e)}"
            
        # 7. Return to main branch so PM can review diff
        subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
        
        with open(REQUIREMENTS_FILE, 'w') as f:
            json.dump(reqs, f, indent=2)
            
    print("🤖 Agent Orchestrator: Finished processing all tasks.")


def resolve_merge_conflict(ticket_id):
    print(f"🤖 Merge Agent: Starting conflict resolution for {ticket_id}")
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"{ticket_id}.log")
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"\n⚡ --- AUTOMATED MERGE AGENT ACTIVATED ---\n")
        log_file.write(f"Merge conflict detected during merge of ticket/{ticket_id}.\n")
        log_file.write(f"Identifying conflicted files...\n")
        
    try:
        # 1. Get conflicted files
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
                
            prompt = f"""You are a senior software engineer resolving a git merge conflict in the file '{fname}'.
     
Here is the content of the file containing merge conflict markers:
{content}

Please resolve all the conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in this file and combine the changes from both sides logically and cleanly.

CRITICAL REQUIREMENTS:
1. Do NOT include any git conflict markers ('<<<<<<< HEAD', '=======', '>>>>>>>') in your output.
2. If you are resolving conflicts in CSS files (especially 'src/index.css'), you MUST ensure that the 'body {{ ... }}' style block is placed BEFORE the 'html, body {{ ... }}' style block (or similar) to prevent regex/index matching errors in the test suite.
3. Output the COMPLETE resolved file contents and absolutely NOTHING else. No markdown block formatting, no explanation, just the plain text of the resolved file.
4. Keep modifications minimal and preserve the exact styling rules and declarations of unaffected lines. Do not merge body block properties (like font-size) into the global html, body block.
"""
            resolved_content = call_gemini(prompt).strip()
            
            # Strip markdown code blocks if the model returned them
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
                
            # Stage the resolved file
            subprocess.run(["git", "add", fname], cwd=WORKSPACE_BASE, check=True)
            
        # 2. Run pytest to verify the fix
        with open(log_file_path, 'a') as log_file:
            log_file.write("Running pytest suite to verify resolution...\n")
            
        test_results = run_pytest(WORKSPACE_BASE)
        all_passing = all(t.get('status') == 'Passing' for t in test_results)
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Pytest results: {json.dumps(test_results)}\n")
            
        if all_passing:
            with open(log_file_path, 'a') as log_file:
                log_file.write("All tests passed! Finalizing git merge...\n")
                
            # Commit the merge
            subprocess.run(
                ["git", "commit", "-m", f"Merge branch 'ticket/{ticket_id}' (auto-resolved)"], 
                cwd=WORKSPACE_BASE, check=True
            )
            # Delete branch
            subprocess.run(["git", "branch", "-d", f"ticket/{ticket_id}"], cwd=WORKSPACE_BASE)
            
            # Update status in requirements.json to Done
            if os.path.exists(REQUIREMENTS_FILE):
                with open(REQUIREMENTS_FILE, 'r') as f:
                    reqs = json.load(f)
                for r in reqs:
                    if r['id'] == ticket_id:
                        r['status'] = 'Done'
                        r['tests'] = test_results
                        r['feedback'] = ""
                        break
                with open(REQUIREMENTS_FILE, 'w') as f:
                    json.dump(reqs, f, indent=2)
                    
            with open(log_file_path, 'a') as log_file:
                log_file.write("🎉 Conflict resolved successfully and merged!\n")
        else:
            # Tests failed, abort the merge
            with open(log_file_path, 'a') as log_file:
                log_file.write("❌ Tests failed after merge resolution. Aborting merge...\n")
                
            subprocess.run(["git", "merge", "--abort"], cwd=WORKSPACE_BASE)
            subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE)
            
            # Construct feedback message containing the failed tests
            failed_test_names = [t.get('name') for t in test_results if t.get('status') != 'Passing']
            feedback = f"Automated merge failed: tests {failed_test_names} failed after conflict resolution."
            
            # Revert status to Review and save tests/feedback
            if os.path.exists(REQUIREMENTS_FILE):
                with open(REQUIREMENTS_FILE, 'r') as f:
                    reqs = json.load(f)
                for r in reqs:
                    if r['id'] == ticket_id:
                        r['status'] = 'Review'
                        r['tests'] = test_results
                        r['feedback'] = feedback
                        break
                with open(REQUIREMENTS_FILE, 'w') as f:
                    json.dump(reqs, f, indent=2)
                    
    except Exception as e:
        print(f"❌ Error in merge resolution agent: {e}")
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"❌ Exception in merge agent: {str(e)}. Aborting merge...\n")
            
        try:
            subprocess.run(["git", "merge", "--abort"], cwd=WORKSPACE_BASE)
            subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE)
        except Exception:
            pass
            
        if os.path.exists(REQUIREMENTS_FILE):
            with open(REQUIREMENTS_FILE, 'r') as f:
                reqs = json.load(f)
            for r in reqs:
                if r['id'] == ticket_id:
                    r['status'] = 'Review'
                    r['feedback'] = f"Automated merge failed with error: {str(e)}"
                    break
            with open(REQUIREMENTS_FILE, 'w') as f:
                json.dump(reqs, f, indent=2)
    except Exception as e:
        print(f"❌ Error in merge resolution agent: {e}")
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"❌ Exception in merge agent: {str(e)}. Aborting merge...\n")

def run_requirement_audit(req_id: str):
    print(f"🤖 Audit Agent: Auditing requirement {req_id}...")
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, f"audit_{req_id}.log")
    
    with open(log_file_path, 'w') as log_file:
        log_file.write(f"🤖 Audit Agent starting work on requirement: {req_id}\n")
        
    try:
        # 1. Load requirements.json
        if not os.path.exists(REQUIREMENTS_FILE):
            print(f"❌ Audit Agent failed: {REQUIREMENTS_FILE} not found.")
            return
            
        with open(REQUIREMENTS_FILE, 'r') as f:
            reqs = json.load(f)
            
        target_req = next((r for r in reqs if r['id'] == req_id), None)
        if not target_req:
            print(f"❌ Audit Agent failed: Requirement {req_id} not found.")
            return
            
        child_tasks = [r for r in reqs if r.get('parentId') == req_id and r.get('type') == 'Task']
        
        # 2. Read workspace/tests/test_example.py
        test_filepath = os.path.join(WORKSPACE_BASE, 'tests', 'test_example.py')
        test_code = ""
        if os.path.exists(test_filepath):
            with open(test_filepath, 'r') as f:
                test_code = f.read()
                
        # 3. Read current workspace codebase files (for context)
        workspace_context = read_workspace_files()
        
        # 4. Formulate prompt for Gemini
        existing_tasks_summary = json.dumps([
            {"id": t['id'], "title": t['title'], "description": t['description'], "status": t.get('status')}
            for t in child_tasks
        ], indent=2)
        
        prompt = f"""You are a senior product manager and developer agent auditing a requirement modification.
The parent requirement has been updated. You need to analyze the changes to determine if:
1. Any new technical tasks (tickets) are needed to implement this new behavior.
2. Any existing technical tasks' descriptions/titles need to be modified.
3. Any new python/pytest tests are needed in `tests/test_example.py`.
4. Any existing python/pytest tests in `tests/test_example.py` are expected to fail now because of the updated requirement (and thus should be decorated with `@pytest.mark.xfail(reason="...")`).

--- REQUIREMENT ---
ID: {req_id}
Title: {target_req.get('title')}
Description: {target_req.get('description')}

--- EXISTING CHILD TASKS ---
{existing_tasks_summary}

--- CURRENT WORKSPACE CODEBASE ---
{workspace_context}

--- CURRENT TESTS FILE (tests/test_example.py) ---
{test_code}

--- INSTRUCTIONS ---
Based on the requirement, analyze the existing tasks and test file.
If the requirement changed the expected behavior, decorate the obsolete/failing tests with `@pytest.mark.xfail(reason="...")` in the updated test code.
If new tests are needed, append them to the updated test code. Every test function in `tests/test_example.py` MUST contain a docstring with:
  id: TST-<unique 4-digit number>
  req: {req_id}
  Given: ...
  When: ...
  Then: ...
Ensure all imports like `import pytest` are preserved.

Respond ONLY with a JSON object. No markdown formatting, no explanation. The JSON object must have EXACTLY these fields:
{{
  "new_tasks": [
    {{
      "title": "Task title",
      "description": "Task description explaining what to change/implement"
    }}
  ],
  "update_tasks": [
    {{
      "id": "REQ-XXXX",
      "description": "New updated task description"
    }}
  ],
  "updated_test_code": "<the complete contents of tests/test_example.py with new tests added and target existing tests decorated with @pytest.mark.xfail(...)>"
}}
"""
        with open(log_file_path, 'a') as log_file:
            log_file.write("Calling Gemini API...\n")
            
        response_text = call_gemini(prompt).strip()
        
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"Gemini raw response:\n{response_text}\n")
            
        # Clean up markdown JSON block if present
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
            
        audit_result = json.loads(response_text)
        
        new_tasks = audit_result.get('new_tasks', [])
        update_tasks = audit_result.get('update_tasks', [])
        updated_test_code = audit_result.get('updated_test_code', '')
        
        # 5. Write updated test code if returned
        if updated_test_code:
            os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
            with open(test_filepath, 'w') as f:
                f.write(updated_test_code)
            with open(log_file_path, 'a') as log_file:
                log_file.write("✅ Updated tests/test_example.py\n")
                
            # Commit the updated test suite to main
            subprocess.run(["git", "checkout", "main"], cwd=WORKSPACE_BASE, capture_output=True)
            subprocess.run(["git", "add", "tests/test_example.py"], cwd=WORKSPACE_BASE, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"test(audit): update tests for requirement {req_id}"], cwd=WORKSPACE_BASE, capture_output=True)
            with open(log_file_path, 'a') as log_file:
                log_file.write("✅ Committed tests update to main\n")
                
        # 6. Apply database changes to requirements.json
        import random
        changes_made = False
        
        # Create new tasks
        for task in new_tasks:
            task_id = f"REQ-{random.randint(1000, 9999)}"
            new_task = {
                "id": task_id,
                "title": task.get('title', 'Audit Generated Task'),
                "description": task.get('description', 'Task description'),
                "priority": "Med",
                "status": "Backlog",
                "tests": [],
                "assignedAgents": ["Frontend"],
                "type": "Task",
                "parentId": req_id,
                "dependencies": []
            }
            reqs.append(new_task)
            changes_made = True
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"➕ Created new task {task_id}: {new_task['title']}\n")
                
        # Update existing tasks
        for task in update_tasks:
            t_id = task.get('id')
            t_desc = task.get('description')
            for r in reqs:
                if r['id'] == t_id:
                    r['description'] = t_desc
                    r['status'] = 'Backlog'  # Reset to backlog so developer works on it
                    changes_made = True
                    with open(log_file_path, 'a') as log_file:
                        log_file.write(f"✏️ Updated task {t_id} and reset to Backlog\n")
                    break
                    
        # Update tests fields in requirements.json by running pytest
        if updated_test_code or changes_made:
            test_results = run_pytest(WORKSPACE_BASE)
            # Group tests by req id
            # We will clear out existing tests and update them
            for r in reqs:
                if r.get('parentId') == req_id or r['id'] == req_id:
                    r['tests'] = [t for t in test_results if t.get('req') == r['id']]
                    
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"✅ Updated test execution states in requirements.json\n")
                
        with open(REQUIREMENTS_FILE, 'w') as f:
            json.dump(reqs, f, indent=2)
            
        # 7. If tasks were added or updated, trigger developer agent
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

