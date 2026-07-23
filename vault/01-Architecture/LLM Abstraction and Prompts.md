# LLM Abstraction Layer & System Prompt Catalog

Provable routes all LLM calls through a model-agnostic abstraction layer defined in `backend/config_loader.py` and `backend/agent_orchestrator.py`. Prompts are externalized into dedicated markdown files in `backend/prompts/`.

---

## 1. Model Configuration (`backend/config/models.yaml`)

Models and provider settings are configured centrally in YAML:

```yaml
default:
  model: gemini-2.5-flash
  base_url: https://generativelanguage.googleapis.com/v1beta/openai/
  api_key_env: LLM_API_KEY

stages:
  code_generation:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  visual_qa:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  task_decomposition:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  merge_resolution:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  requirement_audit:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY

  test_case_generation:
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key_env: LLM_API_KEY
```

---

## 2. Prompt Template Catalog & Format Rules

All prompt files reside in `backend/prompts/`. They dictate system persona, context placeholders, and output delimiters.

### 1. `code_generation.md`
- **Purpose**: Generates drop-in source code files and accompanying pytest test files.
- **Output Delimiter Protocol**:
  ```
  === FILE: src/App.tsx ===
  <full file content>
  === END FILE ===
  === FILE: workspace/tests/test_REQ-1002.py ===
  <full pytest content>
  === END FILE ===
  ```
- **Placeholders**: `{current_workspace_context}`, `{task_desc}`, `{feedback_note_attempt}`, `{test_context}`, `{test_file_path}`, `{parent_id}`.

### 2. `test_case_generation.md`
- **Purpose**: Generates failing pytest BDD test cases (`workspace/tests/test_<REQ_ID>.py`) establishing the initial TDD Red state.
- **Docstring Protocol**:
  ```python
  """<Short title of the test>

  <Detailed description of the test>

  id: TST-1001
  req: REQ-1002
  Given: <Preconditions>
  When: <Actions>
  Then: <Expected assertions>
  """
  ```
- **Placeholders**: `{req_id}`, `{title}`, `{description}`, `{test_case_id}`.

### 3. `visual_qa.md`
- **Purpose**: Multi-modal vision analysis evaluating mobile/desktop screenshots against proposed code.
- **Verdict Schema**: JSON output:
  ```json
  {
    "verdict": "PASSED" | "FAILED",
    "feedback": "Detailed description of layout defects, text overlaps, or contrast issues."
  }
  ```
- **Placeholders**: `{proposed_code}`, `{screen_type}`.

### 4. `task_decomposition.md`
- **Purpose**: Breaks high-level requirement epics into sub-tasks and bug items.
- **Placeholders**: `{requirement_title}`, `{requirement_desc}`.

### 5. `requirement_audit.md`
- **Purpose**: Scans specification nodes for missing acceptance criteria or duplicate UIDs.
- **Placeholders**: `{requirements_json}`.

### 6. `merge_resolution.md`
- **Purpose**: Resolves git merge conflicts between ticket branch and `main`.
- **Placeholders**: `{conflict_diff}`, `{main_code}`, `{ticket_code}`.
