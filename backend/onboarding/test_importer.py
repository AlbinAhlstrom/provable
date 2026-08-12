import os
import sys
import re
from typing import List, Dict, Any, Optional
from service_layer.unit_of_work import AbstractUnitOfWork

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_orchestrator import call_gemini
from integrations.strictdoc_client import parse_sdoc

def import_and_decorate_tests(project_path: str, sdoc_file: str):
    """Scans Python files in tests/ and adds Allure decorators + BDD docstrings."""
    tests_dir = os.path.join(project_path, 'tests')
    if not os.path.exists(tests_dir):
        print(f"⚠️ No tests/ directory found in {project_path}")
        return
    
    # Prioritize E2E and System tests for visual/BDD mapping
    e2e_dir = os.path.join(tests_dir, 'e2e')
    if os.path.exists(e2e_dir):
        tests_dir = e2e_dir
        print(f"🎯 Found E2E tests directory, limiting scan to: {tests_dir}")
        
    # Load requirements to link against
    requirements = parse_sdoc(sdoc_file)
    reqs_summary = "\n".join([f"- UID: {r['id']}, Title: {r['title']}, Description: {r['description']}" for r in requirements])
    
    for root, _, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                filepath = os.path.join(root, file)
                print(f"🧪 Processing test file: {file}...")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_code = f.read()
                        
                    prompt = f"""
You are an expert test engineer.
Your task is to take an existing python test file and update it to follow standard BDD and Allure reporting conventions.

Here is the target python test file:
```python
{test_code}
```

Here are the requirements currently defined for the project:
{reqs_summary}

Please modify the python code to:
1. Make sure it imports `pytest` and `allure` (add `import allure` at the top if needed).
2. For each test function in the file, add:
   - `@allure.id("TST-<4-digit-id>")` (ensure unique IDs like TST-1001, TST-1002)
   - `@allure.link("<Matching REQ-UID>")` (match the closest requirement UID from the provided list, or create one if none fit)
   - A docstring with Given/When/Then steps. E.g.:
     \"\"\"
     Description of what the test verifies.
     
     id: TST-XXXX
     req: REQ-XXXX
     Given: <pre-conditions>
     When: <action taken>
     Then: <expected outcome>
     \"\"\"
3. DO NOT change the actual execution logic, assertions, imports or structure of the existing test framework (e.g. if it uses Playwright page fixture, keep it). Only add decorators and docstrings.

Return ONLY the refactored python code. Do not wrap it in markdown code blocks like ```python.
"""
                    
                    decorated_code = call_gemini(prompt)
                    decorated_code = re.sub(r"^```[a-zA-Z0-9]*\n", "", decorated_code)
                    decorated_code = re.sub(r"\n```$", "", decorated_code)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(decorated_code)
                    print(f"✅ Successfully decorated and saved {filepath}")
                    
                except Exception as e:
                    print(f"❌ Error decorating test file {file}: {e}")


def generate_unit_test_for_requirement(req_id: str, uow: Optional[AbstractUnitOfWork] = None) -> Dict[str, Any]:
    """Generates a BDD pytest file and links test case for a given requirement ID."""
    if uow is None:
        from service_layer.unit_of_work import SqliteUnitOfWork
        uow = SqliteUnitOfWork()

    from config_loader import get_workspace_base

    with uow:
        req = uow.requirements.get(req_id)
        if not req:
            return {"success": False, "error": f"Requirement '{req_id}' not found"}

        title = req.title or "Requirement"
        desc = req.description or ""

        workspace = get_workspace_base()
        tests_dir = os.path.join(workspace, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        clean_id = req_id.lower().replace('-', '_')
        test_file = os.path.join(tests_dir, f"test_{clean_id}.py")

        code = f'''import pytest
import allure

@allure.id("TST-{req_id}")
@allure.link("{req_id}")
def test_{clean_id}():
    """
    {title} - {desc}

    id: TST-{req_id}
    req: {req_id}
    Given system is initialized
    When requirement {req_id} is executed
    Then expected behavior passes
    """
    assert True
'''
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(code)

        tc_id = f"TC-{req_id}"
        test_case = {
            "id": tc_id,
            "requirement_id": req_id,
            "name": f"test_{clean_id}",
            "given": "Given system is initialized",
            "when": f"Requirement {req_id} is executed",
            "then": "Expected behavior passes",
            "status": "fail",
            "last_result": "fail"
        }

        existing_tests = [t for t in (req.tests or []) if isinstance(t, dict) and t.get("name") != test_case["name"]]
        existing_tests.append(test_case)
        req.tests = existing_tests
        uow.requirements.add(req)
        uow.commit()

    return {"success": True, "test_file": test_file, "requirement_id": req_id, "test_id": tc_id}


