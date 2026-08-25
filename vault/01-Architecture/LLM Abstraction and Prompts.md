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

All prompt files reside in `backend/prompts/`. They dictate system persona, context placeholders, and output schemas:

### 1. `router_decomposition.md`
- **Purpose**: Decomposes raw natural language business pitches into structured `DomainStructureSchema` (Entities/Value Objects/Aggregate Roots) and `DomainBehaviorInboxSchema` (Atomic BDD Given/When/Then specs with mathematical boundary flags).
- **Placeholders**: `{business_pitch}`.

### 2. `domain_discovery.md`
- **Purpose**: Extracts ubiquitous language, core domain nouns, entity attributes, commands, and domain invariants from raw business pitches.
- **Placeholders**: `{business_pitch}`.

### 3. `test_case_generation.md`
- **Purpose**: Generates failing pytest BDD test cases (`workspace/tests/test_<REQ_ID>.py`) establishing the initial TDD Red state with BDD Given/When/Then docstrings.
- **Placeholders**: `{req_id}`, `{title}`, `{description}`, `{test_case_id}`.

### 4. `code_generation.md`
- **Purpose**: Generates drop-in source code files and accompanying pytest test files.
- **Placeholders**: `{current_workspace_context}`, `{task_desc}`, `{feedback_note_attempt}`, `{test_context}`, `{test_file_path}`, `{parent_id}`.

### 5. `visual_qa.md` & `visual_audit.md`
- **Purpose**: Multi-modal vision analysis evaluating mobile (`375x812`) and desktop (`1280x800`) screenshots against layout defect rubrics.
- **Placeholders**: `{proposed_code}`, `{screen_type}`.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - Externalizing all prompt templates into backend/prompts/*.md enables independent prompt iteration without touching Python code. However, ui_generation.md still contains references to legacy e-commerce cart and pizza order snapshot patterns, which should be sanitized to pure industrial domain standards.]

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]

