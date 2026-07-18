"""
Requirements Synthesizer — derives requirements from existing test functions.
Implements reverse-TDD: tests → inferred requirements → linked Backlog items.
"""
import os
import sys
import re
import ast
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_orchestrator import call_gemini
from config_loader import get_workspace_base


def _extract_test_functions(filepath: str) -> List[Dict[str, Any]]:
    """Parse a Python test file and extract test function names + their source code."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception as e:
        print(f"⚠️ synthesizer: Could not parse {filepath}: {e}")
        return []

    results = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                # Check if already linked to a requirement
                docstring = ast.get_docstring(node) or ''
                if re.search(r'\breq:\s*REQ-\d+', docstring, re.IGNORECASE):
                    continue  # Already linked — skip

                # Extract function source lines
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, 'end_lineno') else start + 20
                func_source = '\n'.join(lines[start:end])

                results.append({
                    'name': node.name,
                    'source': func_source,
                    'file': filepath,
                    'docstring': docstring
                })
    return results


def _uid_exists_in_sdoc(sdoc_path: str, uid: str) -> bool:
    """Check whether a UID already exists in the sdoc file."""
    if not os.path.exists(sdoc_path):
        return False
    with open(sdoc_path, 'r', encoding='utf-8') as f:
        return uid in f.read()


def synthesize_requirements_from_tests(project_path: str) -> int:
    """
    Scan test files in the project, derive requirements from each unlinked test,
    append them to requirements.sdoc, and sync to the database.
    Returns the number of requirements synthesized.
    """
    project_path = os.path.abspath(project_path)
    tests_root = os.path.join(project_path, 'tests')
    sdoc_path = os.path.join(project_path, 'requirements', 'requirements.sdoc')

    if not os.path.exists(tests_root):
        print(f"⚠️ synthesizer: No tests/ directory found in {project_path}")
        return 0

    # Collect all unlinked test functions
    all_tests = []
    for root, _, files in os.walk(tests_root):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = os.path.join(root, file)
                funcs = _extract_test_functions(filepath)
                for fn in funcs:
                    fn['rel_path'] = os.path.relpath(filepath, project_path).replace('\\', '/')
                all_tests.extend(funcs)

    if not all_tests:
        print("✅ synthesizer: No unlinked tests found — all tests already have requirements.")
        return 0

    print(f"🔍 synthesizer: Found {len(all_tests)} unlinked test functions — synthesizing requirements...")

    # Generate a unique UID base that won't clash
    import random
    uid_counter = random.randint(5000, 8999)

    new_sdoc_blocks = []

    for test in all_tests:
        uid = f"REQ-{uid_counter}"
        uid_counter += 1

        # Skip if somehow this UID already exists
        while _uid_exists_in_sdoc(sdoc_path, uid):
            uid = f"REQ-{uid_counter}"
            uid_counter += 1

        prompt = f"""
You are a requirements engineer performing reverse-TDD analysis.
Given the following Python test function, write a concise, user-facing software requirement
that this test is implicitly verifying.

TEST FUNCTION:
```python
{test['source']}
```

Also classify the requirement into the canonical requirement hierarchy:
  Functional > GUI > Pages
  Functional > GUI > <other GUI sub-section>
  Functional > Business Logic > <sub-section>
  Non-Functional > Performance
  Non-Functional > Security

Return ONLY a JSON object with these fields (no markdown, no explanation):
{{
  "title": "<Short imperative requirement title (max 8 words)>",
  "statement": "<Full requirement statement describing the expected system behaviour (1-3 sentences)>",
  "priority": "<High|Med|Low>",
  "section_path": "<e.g. Functional > GUI > Game Board UI>"
}}
"""

        try:
            raw = call_gemini(prompt)
            raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
            raw = re.sub(r'\n?```$', '', raw.strip())

            import json
            req_data = json.loads(raw)
            title = req_data.get('title', test['name'].replace('_', ' ').title())
            statement = req_data.get('statement', f"The system should pass test {test['name']}.")
            priority = req_data.get('priority', 'Med')
            section_path = req_data.get('section_path', 'Functional > Business Logic > Tests')
        except Exception as e:
            print(f"  ⚠️ synthesizer: LLM failed for {test['name']}: {e} — using fallback")
            title = test['name'].replace('_', ' ').replace('test ', '').strip().title()
            statement = f"The system shall satisfy the behaviour verified by test `{test['name']}`."
            priority = 'Med'
            section_path = 'Functional > Business Logic > Tests'

        block = f"""
[REQUIREMENT]
UID: {uid}
TITLE: {title}
STATEMENT: {statement}
REQ_TYPE: Requirement
PRIORITY: {priority}
STATUS: Backlog
RELATIONS:
  - TYPE: File
    VALUE: {test['rel_path']}
"""
        new_sdoc_blocks.append({'block': block, 'section_path': section_path, 'uid': uid, 'title': title})
        print(f"  ✅ {uid}: [{section_path}] {title}")

    # Append new requirements to the sdoc file, grouped by section_path
    if new_sdoc_blocks:
        os.makedirs(os.path.dirname(sdoc_path), exist_ok=True)

        # Ensure document header exists
        if not os.path.exists(sdoc_path):
            header = "[DOCUMENT]\nTITLE: Project System Requirements\n"
            with open(sdoc_path, 'w', encoding='utf-8') as f:
                f.write(header)

        # Group blocks by their section_path
        from collections import defaultdict
        by_section: dict = defaultdict(list)
        for item in new_sdoc_blocks:
            by_section[item['section_path']].append(item['block'])

        with open(sdoc_path, 'a', encoding='utf-8') as f:
            for section_path, blocks in by_section.items():
                # Build nested section opening tags from the path
                # e.g. "Functional > GUI > Game Board UI" → 3 nested sections
                parts = [p.strip() for p in section_path.split('>')]
                # Write opening sections
                for part in parts:
                    f.write(f'\n[SECTION]\nTITLE: {part}\n')
                for block in blocks:
                    f.write(block)
                # Write closing sections (innermost first)
                for _ in parts:
                    f.write('\n[/SECTION]\n')

        # Sync to database
        from integrations.strictdoc_client import sync_sdoc_to_db
        sync_sdoc_to_db()
        print(f"🎉 synthesizer: Added {len(new_sdoc_blocks)} synthesized requirements to the database.")

    return len(new_sdoc_blocks)
