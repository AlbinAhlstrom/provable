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
   app's API for the test with nothing saved, and sends the page's API calls there. The person's own records are
   never touched.
5. **Running a test changes no code.** The run ends red, green or broken (the test could not judge). Fixing is a
   separate step that starts from a red test and its evidence, with the one retry the retry policy allows.
6. **A test is written once.** It is stored with the rule and run again as it is. It is written again only when the
   rule's text changes or the test turned out broken.
7. **Tests of the domain class stay for now, out of sight.** They are the model's inner loop while it writes the
   class, and two thirds of a run's cost. They are linked to no rule in the Studio. Whether they stay is decided by
   measuring a run with and without them.

## How a control is found
The test and the page are written by different calls and must agree on how a control is found. A test finds controls
the way a person does: by role and by the name read out for it. For an app that exists, the test writer is shown the
page's source to learn those names. For a new app, where tests and page are written side by side, the UX plan will
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
5. An action that returns a new record of its own kind: the router stores it and answers with it.
6. The kind of a rule leaves decomposition and the kickstart; page tests are written during the kickstart.
7. A run with and without the domain tests, then a decision.
