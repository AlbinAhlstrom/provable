# ADR-010: One kind of rule, proved on the running page

Status: accepted, being implemented in steps (see "Order of work"). Changes what
[[ADR-006 Spec-Derived RED Tests and Fragment GREEN]] and [[ADR-008 Aggregate Ownership and Audience-Scoped UI]]
call proof.

## Problem
One pitch ("a minesweeper game") was built by the pipeline with the larger model: verdict OK, 46 of 46 rules proved,
every light green. In the browser, starting a new game froze the board and changing difficulty did nothing.

- A rule was one of two kinds. A behaviour rule was proved by a test of the domain class alone. A presentation rule
  had no test: running it had a model rewrite one view, and green meant "the view compiles".
- The defect lay between the layers: the class returned a new record, the router dropped it, the page expected it.
  Each layer was correct by its own test. No rule could go red, because no test reached the page.
- Running a rule from the Studio also changed code, so a light could go from "not run" to green without ever
  showing that anything had been wrong.

## Decisions
1. **One kind of rule.** A rule says what a person can do and what then holds. Whether the class, the API or the page
   makes it true is not part of the rule and is not shown.
2. **One proof: a page test.** Each rule maps to one test that opens the running app in a browser, does the When as
   a person would, and checks the Then. A rule's light in the Studio comes from this test and from nothing else.
3. **The Given goes through the API.** A test cannot click its way to "a record in this exact state". It creates the
   records it needs through the app's API, and may read a record back where the rule is about something the page
   does not show. The When is always done on the page.
4. **Each test gets records of its own.** The harness (`tests/e2e/conftest.py`, written by the engine) starts the
   app's API for the test with nothing saved, and gives the test's browser an address of its own where every
   `/api/` call goes to that API and everything else to the running page. The person's own records are never
   touched. Listening in on the page's requests and redirecting them was tried first and is not enough: a request a
   page sends while it is being left goes past it, so no rule about leaving could be proved.
5. **Running a test changes no code.** The run ends red, green or broken (the test could not judge). Fixing is a
   separate step that starts from a red test and its evidence, with the one retry the retry policy allows.
6. **A test is written once.** It is stored with the rule and run again as it is. It is written again only when the
   rule's text changes or the test turned out broken.
7. **Tests of the domain class stay for now, out of sight.** They are the model's inner loop while it writes the
   class, and two thirds of a run's cost. They are linked to no rule in the Studio. Whether they stay is decided by
   measuring a run with and without them.

## How a control is found
The test and the page are written by different calls and must agree on how a control is found. A test finds controls
the way a person does: by role and by the name read out for it. For an app that exists, the test writer is shown
what a browser read out from the opened page (roles and names, a long run of like controls condensed to its first
few and the forms their names take) and the page's source for what is not open yet. Names guessed from the source
alone were the most common reason a first test was wrong. For a new app, where tests and page are written side by side, the UX plan will
name every control and state first (not built yet).

## What a run can say
- **pass:** every assertion held.
- **fail:** an assertion did not hold, or the page had no control the test could use.
- **broken:** the test could not judge: it did not import, the harness could not start, the provider failed.
  A broken test is written again once with the error as feedback; that is the single retry.

## Consequences
- An app that is broken for a person has at least one red light, or a rule is missing. A missing rule is a
  decomposition defect, fixed there and checked by running that stage alone.
- A light is slower to get: seconds per rule, not milliseconds. Tests run side by side, one process per rule.
- The page's wording becomes something tests depend on. Rewriting a page can turn lights red for no change in
  behaviour until controls are named by the UX plan.
- A test with a wrong expectation fails a correct app. This risk existed before; it is now visible on the page.

## Order of work
1. Harness and the run step (no code changes, three outcomes).
2. Test-writing step, run alone on rules of an existing app.
3. Studio: Run shows red or green; Fix is a separate action on a red rule.
4. Every rule of the reference app run; gaps traced to decomposition.
5. An action that returns a new record of its own kind: the router stores it and answers with it as `created`,
   beside the `state` of the record the action was run on.
6. The kind of a rule leaves decomposition and the kickstart; page tests are written during the kickstart.
   - A kickstart that built a page starts one run of every rule's page test when it has answered
     (`entrypoints/routers/onboarding.py`), so the lights fill in while the app is used. The first run writes the
     tests: about 2.5 minutes and 1.2 SEK for 41 rules, which is why the answer does not wait for it.
7. A run with and without the domain tests, then a decision.

## Fixing a red rule
`POST /api/specs/rules/{id}/fix` (`service_layer/rule_tests.py`, the Fix button on a red specification).
- It starts from a test that ran and failed. A rule that never ran, passed or has a broken test is not touched.
- **The cause is found before anything is changed** (`backend/onboarding/rule_diagnosis.py`, one call, stage
  `rule_diagnosis`). A fix that could only change the page spent two attempts on a fault that was in the record's
  class, and behind that in two rules that could not both hold. The answer is one of four:
  - `page`: the page is changed (`rule_fix.py`, below).
  - `logic`: the record's class is changed (`logic_fix.py`, below).
  - `rules`: specifications disagree with what the plan says the action does. Nothing is changed; they are named.
  - `test`: the test checks something the rule does not state. Nothing is changed.
- What the diagnosis reads beyond the rule and its test:
  - What the page asked the app to change, what the app answered, and the test's records as the app held them when
    the test ended. The harness notes these on a failed test (`App.seen()` in the page-test harness template). A red
    rule from before this is run once more first.
  - The action's method with the helpers it calls, and what the plan says the action does.
  - The rule's unit test and whether it passes, and the other rules about the same action.
- The answer first works each rule through against the plan (`checked`: how many of what closes the whole are left,
  what the action leaves, whether the rule holds), and a rule that does not hold makes the fault `rules` by code.
  Asked for the verdict alone, the standard models named the class for a fault that was two rules disagreeing.
- A rule left red keeps what was found (`page_test.cause`), shown under the specification in the Studio.

### The page
- The writer is shown the rule, the test, what the test saw, the API and the page, and answers with whole page files.
  A file outside the page is refused.
- A change is kept only when the page builds, the rule's test passes and every rule that was green still is. A
  rejected change goes back once with what the check said; after a second rejection the page is as it was.
- The writer is told to correct the cause for every case that shares it. Told only to change as little as possible,
  it special-cased the one action the test used and left six rules with the same cause red.

### What the app does
- The class changes where every change of a class is made, in the test-first loop. The rule's unit test was green,
  so it arranged something the page test did not: the test writer is shown the page test and what the app held, and
  writes the unit test again for those records.
- The loop keeps its gates (red first, then green, every other rule's unit test still green). Then the same check as
  for the page decides. A change that is not kept leaves the class and the rule's unit test as they were.
- A change taken back because it broke other rules' unit tests names those rules by title: this rule and those
  cannot be kept together, which is for a person to settle.
