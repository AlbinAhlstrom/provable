# ADR-008: Who owns the aggregate, and who the UI serves

Status: accepted. Follows [[ADR-006 Spec-Derived RED Tests and Fragment GREEN]] and [[ADR-007 Product Intent Step]].

## Problem
Merging the one-shot UI/domain synthesizer with the spec-by-spec TDD loop exposed two defects, found by tracing every step of one run (`logs/trace`):

1. Two stages wrote the same domain file. `domain_engine_synthesis` generated the whole aggregate as a state-object class and overwrote the skeleton's router, so the dataclass the skeleton tests and the TDD loop expect no longer existed and every spec dead-ended on a regression failure.
2. A back-office control panel appeared in a public website. The expansion stage invented a staff role with a lifecycle, the decomposition turned it into a spec, and the presentation stage rendered buttons for it.

## Decisions
- **The skeleton and the TDD loop own the aggregate.** `domain_engine_synthesizer.synthesize_action_protocol` writes no code; it returns an action manifest only. Every generated router exposes `POST /api/<aggregates>/{id}/action`, which calls the aggregate's own public method (deterministic WIRE step; domain errors are 400, unknown action 404, wrong parameters 422).
- **Intent reaches every stage that designs behavior or UI** (expansion, decomposition, action protocol, UX plan, presentation), not only the first.
- **The UI serves the audience only.** Each action declares `performed_by` (`audience` or `other`). `onboarding/action_protocol.format_action_protocol` lists `other` actions as API-only and the UI prompts forbid controls for them.
- **No silent fallback in the expander:** an expansion failure raises `ExpansionError` (policy in rule 03 section 4).
- **Tailwind is bundled** in the workspace build (no runtime CDN) and kickstart installs missing npm packages, restarting the preview afterward because Vite reads its config at startup.

## Known gaps (not fixed yet)
- Action names in the manifest are chosen before the specs run, so a manifest action can name a method the TDD loop never creates. Nothing checks the manifest against the final class.
- View-type specs go through `delta_evolution` with no RED/GREEN, so FULFILLED there is unverified, and one such run ended in REQUIRES_HUMAN_INTERVENTION with no attempts logged.
- The generated client calls `GET /api/<aggregates>/default`, which the skeleton router answers with 404 (the removed LLM router used to auto-create a default).
- Specs from one decomposition can contradict each other; the loop shows later specs the verified tests but does not detect conflicts up front.
- The same model writes the test and the code unless `LLM_MODEL_<STAGE>` overrides it.
- Kickstart takes about two minutes, mostly the per-file `aesthetic_styling` calls.
- One integration test builds the live `workspace/`, so it fails whenever the live preview is broken.
