import os
import sys
import re
from typing import List, Dict, Any

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
