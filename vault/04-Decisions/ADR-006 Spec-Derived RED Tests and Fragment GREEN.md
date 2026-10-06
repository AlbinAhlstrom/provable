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

## Known gaps
- Tests assert one side of a boundary (119 minutes rejected) but not the other (120 accepted); the RED prompt should demand both sides.
- One model writes both the test and the code, so a shared misreading of the spec can pass. Showing the generated test on the spec card for review in PM Studio is not built.
- GREEN still rewrites the whole class; method-level merging and a regression gate across earlier specs are not built.

## Status
Accepted.
