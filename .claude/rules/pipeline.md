---
paths:
  - "backend/onboarding/**"
  - "backend/prompts/**"
  - "backend/service_layer/**"
  - "backend/agent_orchestrator.py"
---

# Pipeline rules: how the generator must behave

These govern the generation pipeline itself (COO -> intent -> Analyst -> Architect -> Product Manager -> TDD -> Backend -> Frontend -> Styling -> QA).

## Root cause only

If a stage emits bad output, fix the upstream schema, prompt or contract. No post-hoc regex or string repair of generated output, and no "MUST NOT" lines added to a prompt to hide a bug. Describe the wanted behaviour positively. If you are tempted to patch downstream, stop and flag it to the user.

What the generated product must look like (copy in the audience's own words, plain-English GIVEN / WHEN / THEN / UNLESS cards, the acceptance checks every generated app ships with) is encoded in the prompts (`prompt_expansion.md`, `presentation_projection_synthesis.md`) and generator templates. When output misses it, change those; do not restate the spec here.

## Derivation, not classification

Personas, interactions and layouts are derived from the user's intent. Never sort a pitch into fixed bins (`B2B`, `B2C`, `GAME`, `CRUD`) and never key behaviour off hard-coded domain keywords.

## Typed contracts

Stages exchange dataclasses, not loose dicts. Behaviour changes to existing code go through `cst_isolator.py` (surgical deltas); presentation changes go through `presentation_specs.py` (one view, proved by a build). The kickstart asks the user nothing: the user is the CEO, and the pipeline makes opinionated assumptions.

## Retry policy (retries mask errors)

- At most ONE retry, ever, and only when a verifying step rejects what a generating step produced. The verdict and its failing evidence are fed back for exactly one more attempt. The model case is the TDD GREEN phase (`TddExecutionState.max_attempts = 2`: first attempt plus one feedback retry, then `REQUIRES_HUMAN_INTERVENTION`).
- Never retry provider, network or quota errors, parse failures, test tampering, or anything that is not a gate verdict. They fail loudly with the real reason (`agent_orchestrator.LAST_LLM_ERROR`).
- No hidden retries: no retry loops, fallbacks-on-error or SDK auto-retries (the OpenAI client is built with `max_retries=0`). Every attempt is visible in the result (`attempts`) and in the trace.
- Changing this policy needs an explicit decision from the user.

Known deviations awaiting that decision: `qa_gate.py` allows `max_rework_attempts=2` (two rework rounds, not one), and `agent_orchestrator.py` and `domain/model.py` report `max_attempts=3` in status payloads. Do not copy these patterns into new code.

## Test integrity (5-line hash lock)

The TDD loop hash-locks the RED test (`compute_test_file_hash` / `verify_test_file_integrity`). The GREEN generator must never modify or weaken test assertions; tampering fails the run and is not retried.

## Observing the pipeline

Every step's input and output is traced to `logs/trace` while the app runs. Clear it with `rm -rf logs/trace` before an experiment, then `python scripts/trace_report.py logs/trace` (`--full N` shows one step). Use `/fix-pipeline-bug` to trace a defect in generated output to the responsible stage.
