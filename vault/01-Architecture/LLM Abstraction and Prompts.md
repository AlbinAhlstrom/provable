# LLM Abstraction Layer & Prompt Catalog

All LLM calls go through `call_gemini()` in `backend/agent_orchestrator.py`, a thin wrapper over the OpenAI Python SDK. Because it speaks the OpenAI-compatible protocol, any compatible provider works.

---

## 1. Configuration (environment variables)

There is no model YAML; configuration is environment-only (see `.env.example`):

| Variable | Purpose | Default |
| :--- | :--- | :--- |
| `LLM_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` | API key (first one set wins) | none (calls return empty and the pipeline fails loudly) |
| `OPENAI_BASE_URL` | Provider endpoint | Gemini's OpenAI-compatible endpoint |
| `LLM_MODEL` | Model name | `gemini-2.5-flash` |

The test suite never needs a key: `backend/tests/conftest.py` mocks `call_gemini` per `stage` name.

---

## 2. Where prompts live

**File-based prompts** (`backend/prompts/`, loaded with `agent_orchestrator.load_prompt(name, {placeholder: value})`; a missing file or a placeholder not present in the template raises):

| File | Used by | Placeholders |
| :--- | :--- | :--- |
| `router_decomposition.md` | `onboarding/router_engine.py` | `{business_pitch}` |
| `green_class_repair.md` | `service_layer/tdd_machine.py` (GREEN phase) | `{extracted_class_code}`, `{spec_title}`, `{spec_given_when_then}`, `{target_aggregate}`, `{spec_type}`, `{failure_output}`, `{target_class_name}` |
| `visual_qa.md`, `visual_audit.md` | `onboarding/visual_auditor.py` (read directly) | see file |

**Inline prompts** (f-strings in code, one per LLM `stage`):
`domain_ontology`, `component_planning`, `aesthetic_planning`, `app_assembly`, `pitch_component_analysis` (`onboarding/domain_ontology.py`, `onboarding/frontend_planning_engine.py`), `dynamic_requirements` (`requirement_generator.py`), `self_healing` (`code_verifier.py`), plus the prompt in `test_importer.py`.

> [!NOTE]
> Externalizing the inline prompts into `backend/prompts/` (the original intent of [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]) is unfinished. When touching an inline prompt, consider moving it to a file and loading it with `load_prompt`.

---

## 3. History
Earlier prototypes had prompt files for a Jira/Kanban developer-agent pipeline (`code_generation`, `test_case_generation`, `task_decomposition`, `requirement_audit`, `merge_resolution`, `ddd_guidelines_template`), a `domain_discovery` prompt, a `ui_generation` prompt and a `models.yaml` router. None were wired into the current pipeline and they were removed.

---

## Related Documentation
- [[System Architecture]]
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]
