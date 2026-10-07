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
- **No silent fallback in the expander:** an expansion failure raises `ExpansionError` (policy in .claude/rules/pipeline.md, retry policy).
- **Specs declare what they constrain.** `BusinessSpec.kind` is `behavior` (RED/GREEN in the TDD loop) or `presentation` (what the user sees), decided by the decomposition step; the old keyword classifier and `delta_compiler` (which edited the first view file it found and reported success when a file was written) are gone. `onboarding/presentation_specs.py` rewrites the target aggregate's own view, proves it with `npm run build`, feeds a build error back once, and otherwise restores the original and reports REQUIRES_HUMAN_INTERVENTION with every attempt. A spec that needs both kinds is split in two by the decomposition prompt.
- **Tailwind is bundled** in the workspace build (no runtime CDN) and kickstart installs missing npm packages, restarting the preview afterward because Vite reads its config at startup.

- **The master API client is generated, not written by the model** (`skeleton_builder.generate_master_client`): list/get/create/action, errors thrown with the server's message, no `default` record, no fabricated fallback data. The presentation prompt states the real endpoints. A model App that does not wire the master view is a failed stage (no substitute shell), and kickstart reports `stage_failures`.
- **The action protocol is persisted and checked against the code.** The TDD loop's RED prompt lists the methods the interface was promised for the target class (`format_interface_contract`); `GET /api/specs/action-contract` reports manifest actions that have no method on their aggregate.
- **Spec conflicts are reported up front** (`onboarding/spec_review.py`, one call, report only) as `spec_conflicts` in the kickstart result. The Studio states whether the test and the code were written by the same model.

## Known gaps (not fixed yet)
- A presentation spec is proved only by a successful build; nothing checks the rendered page shows what the spec says.
- The contract check reports; nothing yet repairs a manifest action whose method the loop named differently (live confirmation that the RED prompt now aligns them is pending).
- Test and code use the same model unless `LLM_MODEL_RED_TEST_GENERATION` is set; this is reported, not enforced.
- Kickstart takes about 2.5 minutes (presentation ~70s, styling ~40s, now with up to 6 parallel styling calls).
