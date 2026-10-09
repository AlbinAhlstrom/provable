# LLM Abstraction Layer & Prompt Catalog

All LLM calls go through `call_gemini()` in `backend/agent_orchestrator.py`, a thin wrapper over the OpenAI Python SDK. Because it speaks the OpenAI-compatible protocol, any compatible provider works.

---

## 1. Configuration (environment variables)

There is no model YAML; configuration is environment-only (see `.env.example`):

| Variable | Purpose | Default |
| :--- | :--- | :--- |
| `LLM_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` | API key (first one set wins) | none (calls return empty and the pipeline fails loudly) |
| `OPENAI_BASE_URL` | Provider endpoint | Gemini's OpenAI-compatible endpoint |
| `LLM_MODEL` | Model name | `gemini-3.8-flash` |
| `LLM_PROVIDER` | Names a provider in `backend/llm_provider.py` (`gemini`, `openai`), which then supplies the endpoint, the default model and the setting its key is read from (`GEMINI_API_KEY`, `OPENAI_API_KEY`). The three rows above are ignored while it is set; `LLM_MODEL_<STAGE>` still applies. An unknown name fails loudly. | unset (the rows above decide) |

The test suite never needs a key: `backend/tests/conftest.py` mocks `call_gemini` per `stage` name.

---

## 2. Where prompts live

**Prompts** (`backend/prompts/`, loaded with `agent_orchestrator.load_prompt(name, {placeholder: value})`; a missing file or a placeholder not present in the template raises):

| File | Used by | Placeholders |
| :--- | :--- | :--- |
| `router_decomposition.md` | `onboarding/router_engine.py` | `{business_pitch}` |
| `green_class_repair.md` | `service_layer/tdd_machine.py` (GREEN phase) | `{extracted_class_code}`, `{spec_title}`, `{spec_given_when_then}`, `{target_aggregate}`, `{spec_type}`, `{failure_output}`, `{target_class_name}` |
| `visual_qa.md`, `visual_audit.md` | `onboarding/visual_auditor.py` (read directly) | see file |
| `domain_ontology.md` | `onboarding/domain_ontology.py` | `{business_pitch}` |
| `component_planning.md` | `onboarding/frontend_planning_engine.py` | `{pitch}`, `{noun}`, `{category_id}`, `{layout_name}`, `{invariants_json}` |
| `aesthetic_planning.md` | `onboarding/frontend_planning_engine.py` | `{pitch}`, `{category_id}`, `{archetype}` |
| `app_assembly.md` | `onboarding/frontend_planning_engine.py` (`assemble_app_tsx_from_blueprint`) | `{pitch}`, `{category_id}`, `{layout_name}`, `{brand_title}`, `{archetype}`, `{css_variables}`, `{seed_data_json}`, `{components_json}` |
| `pitch_component_analysis.md` | `onboarding/frontend_planning_engine.py` | `{business_pitch}` |
| `dynamic_requirements.md` | `onboarding/requirement_generator.py` | `{schema_json}` |
| `self_healing.md` | `onboarding/code_verifier.py` | `{error_message}`, `{business_pitch}`, `{broken_code}` |

`load_prompt` substitutes in a single pass (values are never re-scanned), raises `FileNotFoundError` for a missing template and `KeyError` for a placeholder the template lacks. `backend/tests/unit/test_load_prompt.py` checks every template against its caller's placeholders. To change what the generator asks the LLM, edit the `.md` file, not Python.

**Still inline:** the one-off prompt in `onboarding/test_importer.py` (a standalone helper that decorates imported test files with Allure metadata).

---

## 3. History
Earlier prototypes had prompt files for a Jira/Kanban developer-agent pipeline (`code_generation`, `test_case_generation`, `task_decomposition`, `requirement_audit`, `merge_resolution`, `ddd_guidelines_template`), a `domain_discovery` prompt, a `ui_generation` prompt and a `models.yaml` router. None were wired into the current pipeline and they were removed.

---

## Related Documentation
- [[System Architecture]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]
