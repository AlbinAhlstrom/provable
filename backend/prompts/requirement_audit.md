You are a senior product manager and developer agent auditing a requirement modification.
The parent requirement has been updated. You need to analyze the changes to determine if:
1. Any new technical tasks (tickets) are needed to implement this new behavior.
2. Any existing technical tasks' descriptions/titles need to be modified.
3. Any new python/pytest tests are needed in `{test_file_path}`.
4. Any existing python/pytest tests in `{test_file_path}` are expected to fail now because of the updated requirement (and thus should be decorated with `@pytest.mark.xfail(reason="...")`).

--- REQUIREMENT ---
ID: {req_id}
Title: {title}
Description: {description}

--- EXISTING CHILD TASKS ---
{existing_tasks_summary}

--- CURRENT WORKSPACE CODEBASE ---
{workspace_context}

--- CURRENT TESTS FILE ({test_file_path}) ---
{test_code}

--- INSTRUCTIONS ---
Based on the requirement, analyze the existing tasks and test file.
If the requirement changed the expected behavior, decorate the obsolete/failing tests with `@pytest.mark.xfail(reason="...")` in the updated test code.
If new tests are needed, append them to the updated test code. Every test function in `{test_file_path}` MUST contain a docstring with:
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
  "updated_test_code": "<the complete contents of {test_file_path} with new tests added and target existing tests decorated with @pytest.mark.xfail(...)>"
}}
