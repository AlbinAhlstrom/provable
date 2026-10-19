# ADR-015: A decision several stages depend on is made once, upstream

Status: accepted (2026-10-19). Implemented: the present moment; a rule whose test the TDD loop corrected is
corrected with it (2026-10-20). Open: wordings in read-out names that the contract leaves undefined, and
situations whose outcomes the contract works out by hand.
Builds on [[ADR-011 The Product Contract]].

## Problem
Four builders start from the product contract at once and cannot ask each other anything: the class's code, its
first tests, the page and the page tests. Where the contract leaves something open, each of them decides it on its
own, and they decide it differently. The app then fails its own rules though every builder did what it was told.

An audit of the prompts and recorded runs found eight decisions that more than one stage depends on. Names, field
wordings, chance and starting values each have one owner. The present moment had none: the contract said "the API's
clock", which did not exist; the first tests were told never to depend on the clock, the RED tests to pass times as
arguments, and the page tests to write times into records. One class froze "now" at a constant to pass its unit
test, so its timer never moved in the real app, and page tests that arranged times from the real clock missed the
moment they waited for.

## Decisions
1. **Every decision two or more stages depend on has one owner upstream** (the contract, or the engine where it is
   mechanism), and every later stage receives it as input. A stage never settles such a decision alone.
2. **The present moment is engine mechanism.** Every generated app has the clock module in the generated domain (clock.py): `clock.now()` is
   the real time in the running app, and `clock.set_now(...)` holds a moment for a test.
   - The class's code reads the time only from `clock.now()` (`green_class_repair.md`).
   - A situation whose rules depend on the time states its moment as `now <moment>` (`product_contract.md`).
   - First tests and RED tests hold the clock there (`first_tests.md`, `red_test_generation.md`); the generated
     `tests/conftest.py` lets it go after each test.
   - Page tests call `app.at(moment)`, which holds the moment for the test's API (`PUT /test/clock`, offered
     only when the page tests start the API with `APP_CLOCK_SETTABLE=1`) and for the browser (Playwright's clock).
3. **A corrected outcome has one owner too.** When the TDD loop finds that a rule's first test expected the
   wrong thing and its writer corrects it (`tdd_batch.reconsider_test`), the writer states the outcome the rule
   truly has, and that replaces the rule's Then in its text and on its card (`rule_tests.correct_outcome`). The
   page's test is written later from that text: left as it was, it asserted the outcome the unit test had been
   corrected away from (a live run failed two rules this way).
4. **Policy is per category, never per app.** The clock is written into every app, whether or not it has a rule
   about time.

## Consequences
- A rule about time has the same outcome on every run, in unit tests, in page tests and in the running app.
- The running app's clock cannot be set from outside: the route exists only in an API a page test started.
- The remaining shared decisions without a check (undefined wordings in read-out names, situations worked out by
  hand) are handled by the same rule: decided and checked where the contract is written.
