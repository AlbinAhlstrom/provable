# Shared Decisions Inventory

What the generated page and its page tests fail on, traced to the decisions behind each failure. It applies
[[ADR-015 Decisions Shared by Stages]] to the evidence of 2026-10-20.

## Evidence
- Recorded rule-test runs since commit e5180ad (part names from code): 41 page tests failed.
- An Opus 5.5 low, strict run of Minesweeper (every stage on Opus, no second attempts): 12 of 31 rules failed.
  In that run the classes, their unit tests and the TDD loop held. Every failure sat between the plan, the page
  and the page test.
- An Opus contract has about twice the rules of a Sonnet one (31 against 17 for Minesweeper). A smaller contract
  meets fewer of these decisions, so a valid run on a cheap model can mean the run covered less of the pitch.
  It does not have to mean the pipe works.

## The finding
The plan already decides most of these things. The contract names each refusal with its exact sentence and where it
appears, the trigger of each action and the parts a person meets. The break is how a decision reaches the stages
after the plan: as prose, which each LLM writer reads and puts into code of its own. The class, the page and the page
test then each turn the same sentence into a different detail.

- A refusal's sentence reaches the class's writer as "raised with exactly this message". One class kept it; another
  wrote `rows must be 9..24` in the same run.
- A gesture ("click with both buttons") is turned into an event handler by the page's writer, and into a
  Playwright step by the test's writer, separately.

Part names already travel as code (`page_parts.py` writes a parts module for the page and one for
the tests). That is why name mismatches, the largest group before e5180ad, have mostly stopped. The remedy is to
do the same for every other shared decision.

**Principle: a decision the plan made reaches every builder as code written from the contract, never as prose
for a writer to put into code again.** What the plan leaves open is an error in the contract, found where the
contract is written. A later stage that has to guess means the contract has an error.

## Inventory

| # | Decision | Who decides today | How it reaches the builders | Failures seen | Remedy |
|---|---|---|---|---|---|
| 1 | A refusal's words and where they show | contract (`refusals`) | prose to the class; the page shows the class's message through a part | 16 (8 cheap-model, 8 Opus) | **done**: `action_protocol.write_refusals` writes each class with its sentence before the TDD loop; a code answer cannot replace it (`CONTRACT_REFUSALS`) |
| 2 | How a person performs an action (gesture on a part) | contract (`trigger`, prose) | prose to the page and to the page test, each on its own | ~6 (chord, press and hold) | **done**: the contract names gestures from the set the page's helper answers (`page_gestures.GESTURES_TS`); a page test does each through generated steps from the same module (`GESTURES_PY`, `tests/e2e/gestures.py`), proved in a browser. In the Opus run the page bound every gesture; the test clicked with the middle button, which nothing answers |
| 3 | How a value is written inside a name (digits, padding) and undefined name slots | contract (`shown value`, prose); undefined slots: no one | prose formula written twice (TypeScript and Python) | ~10 | a fixed set of formats written into both part modules; a `{slot}` that resolves to nothing is a contract error |
| 4 | What a situation shows on screen (which dialog is open after loading) | no one | each writer infers it | 2 | a dialog part states what opens it (a person's step or a record condition); the test's opening helper reads it |
| 5 | Whether a situation's records replace the records a kind starts with | no one | the test harness adds them | 1 | engine mechanism: a situation that names records of a kind with starting records replaces them |
| 6 | A rule's outcome in its situation | contract writer, worked out by hand | text; spec review finds the errors afterwards (67 conflicts in 33 runs) | 1 page test plus the reworks | fix A covers the case where the TDD loop corrects an outcome; checking situations against the record's own limits is still open |
| 7 | The present moment | engine (clock module) | code | 0 since bbf6d03 | done (ADR-015) |

Counts are from the classifier over `logs/runs/*/trace/*page_test.prove.json`, grouped by hand; ~ marks groups where
one failure could belong to two rows.

## Order
By failures removed per unit of work, all without extra LLM calls:
1. Refusals (1): ~16 failures. Code only, plus one line less in the class's prompt. About 0 SEK and 0 s per run.
2. Starting records (5): 1 failure. Engine code only.
3. Value formats and undefined slots (3): ~10 failures. Code, plus a contract check before any builder starts.
4. Gestures (2): ~6 failures, including the held-press face. Needs a typed trigger in the contract (a few more
   output tokens from the plan, under 0.05 SEK).
5. Screen state per situation (4): 2 failures. Same pattern as gestures, on dialog parts.
6. Situation outcomes (6): needs its own design.

Rows 1 to 5 cover about 35 of the 41 recent failures. Each is checked by a strict run on the cheap models: one
Minesweeper and one to-do kickstart, about 2 to 4 SEK and 6 to 8 minutes for the pair.
