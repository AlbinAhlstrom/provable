# ADR-006: Spec-Derived RED Tests and Fragment-Based GREEN

## Context
Tracing a real run of "a personal website for a babysitters firm" through the TDD loop showed that "FULFILLED" proved nothing:
- The RED test was a hardcoded template (`hasattr(x, "validate_invariants")` and `validate_invariants() is True`); the BDD scenario only appeared in a docstring. It also built objects with an `id` argument the generated model did not have, so it failed with a `TypeError` that the RED gate accepted.
- The GREEN generator never saw the test, so it guessed, and wrapped everything in reflection and `*args/**kwargs` hacks (one class grew to 1,067 lines).
- GREEN returned "only the class", so a model that needed `datetime` could not add the import: the module stopped importing, the retry hit the same wall, the broken class stayed in the file, and every later spec was blamed on "broken tests".
- When the LLM returned nothing, the loop silently injected `validate_invariants() -> True`, so a provider outage could produce FULFILLED specs.

## Decision
1. **RED test from the spec** (`generate_red_test`, `prompts/red_test_generation.md`): the LLM writes a behavioral pytest from the Given/When/Then, shown the class's real fields and method signatures. Existence checks (`hasattr`/`getattr`/`inspect`) and assert-free tests are refused by `lint_red_test` before pytest runs.
2. **RED gate checks the reason for failing**: assertion failures, "DID NOT RAISE", missing methods and signature mismatches are valid RED. Constructor `TypeError`, import/name/syntax errors and timeouts are broken tests. A collection error through `src/domain/` is `REJECTED_DOMAIN_BROKEN`: an immediate dead end, because regenerating the test cannot help.
3. **GREEN sees the frozen test** and concise failure evidence (not the raw JSON report); the SHA-256 hash lock still prevents changing it.
4. **GREEN returns a module fragment**: import lines, helper classes (e.g. domain exceptions) and the target class. `merge_module_fragment` (LibCST) adds missing imports, places helpers before the target and replaces the class; invalid fragments raise `FragmentError`, which counts as a GREEN rejection.
5. **Rollback:** a spec that dead-ends, or any unexpected error, restores the domain file to its pre-GREEN content (`rolled_back` in the result).
6. **No fake implementations:** an empty or unusable LLM answer raises; there is no stub fallback.
7. **Retry policy** (rule 03 section 4): RED and GREEN each get at most one feedback retry, only for a verifying step's verdict; provider and parse errors are never retried.
8. LLM calls cap hidden reasoning with `reasoning_effort=low` (see `LLM_REASONING_EFFORT`).

## Evidence (live run, same prompt, `gemini-3.8-flash`)
| | Before | After |
| :--- | :--- | :--- |
| Specs FULFILLED | 3 of 6, vacuously | 5 of 5, behaviorally |
| LLM time per spec | 116-227 s | 10-18 s |
| `Booking` size | 1,067 lines, 84 methods | 103 lines |
| Mutation check (4 deliberate bugs) | tests could not detect them | all 4 caught by the right spec's test |

## Follow-ups implemented after the first evidence run
- **Both sides of every boundary:** specs flagged `is_mathematical_boundary` must have a rejected case beyond the limit and an accepted case exactly at it (`lint_red_test(require_both_sides=True)`; the RED prompt asks for touching intervals on range rules). A mutation run showed a one-sided test lets `<` to `<=` survive; with two sides it is caught.
- **Regression gate:** after a spec's own test passes, `tests/unit` runs in full; breaking an earlier spec is a GREEN rejection that names the broken files and consumes the single retry. A spec that dead-ends has its unverified test moved to `tests/pending` (a test rejected twice at RED is deleted), so it cannot fail later specs.
- **Member-wise merge:** GREEN returns only the fields and methods it adds or changes; `_merge_class_members` (LibCST) replaces same-named members, keeps everything else and orders required dataclass fields first. Output no longer grows with the class.
- **Existing tests as context:** both generators see the other verified tests for the same module (`collect_existing_tests`), because independently written tests contradicted each other (one expected status `submitted` after `submit()`, the next `NEW`).
- **One module per class:** the loop used `target_class.lower()` while the skeleton, routers and repositories use snake_case, so for any multi-word aggregate the verified code lived in a module nothing imports. Both now use `skeleton_builder.to_snake_case`.
- **Reviewable tests:** each spec stores its generated test, attempt history, error and rollback flag; PM Studio shows them in a collapsible section. `LLM_MODEL_<STAGE>` lets a different model write the tests than the code.

## Evidence (second live run, intent step on, 3 domains tried)
Six of six specs FULFILLED in 8-15 s each, one module per class, 16 tests passing together, classes of 19-43 lines, and 8 of 8 mutants (operator flips and removed `raise`) caught.

## Known gaps
- One model still writes both test and code by default; the review UI and `LLM_MODEL_RED_TEST_GENERATION` mitigate but do not enforce independence.
- The WIRE step is missing: verified behavior lives in domain methods (`submit`, `schedule`, ...) that the generated CRUD routers never call, and GREEN may add required fields that the generated request schemas do not know about.
- Specs from the decomposition can still conflict with each other; the context and regression gate stop a contradictory spec from corrupting earlier ones, but the spec itself ends in `REQUIRES_HUMAN_INTERVENTION`.

## Status
Accepted.
