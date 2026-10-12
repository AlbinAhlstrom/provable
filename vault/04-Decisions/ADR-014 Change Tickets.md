# ADR-014: Change tickets, every change as a delta of the product contract

Status: accepted (2026-10-12). Implemented so far: the contract is stored with the build state, a ticket is a typed
delta that is applied to it, and the planner writes one. Nothing is built from a ticket yet. See "Order of work".
Builds on [[ADR-011 The Product Contract]] and [[ADR-010 One Kind of Rule Proved on the Page]].

## Problem
A generated app can be built once and then barely changed. The only way to change it is one rule at a time, and that
path does less than it says (see "What exists today"). There is no way to ask for a feature in plain words, see what
it will change, and get proof that nothing else broke. That proof is the product: change your app without breaking
it.

## Decisions
1. **Every change is a ticket.** Free text goes in; the planner turns it into rules; the build is limited to what
   those rules touch; it is done when the new rules are green and every other rule still is. Changing the look or
   the page is a ticket whose rules are of the page alone. No path changes code without rules.
2. **A ticket is a delta of the product contract.** The contract is what an app is built from (ADR-011), so a change
   of the app is a change of the contract: records and fields added, actions added or changed, situations added,
   rules added, changed or retired, each changed or retired rule with its reason. The contract after the ticket is
   the contract before it with the delta applied. A ticket is never a second description of the app.
3. **The contract is stored.** It used to be thrown away after the kickstart read the structure, the deck and the
   manifest out of it. It is now kept with the build state as it was answered (`KickstartState.contract`,
   `product_contract.stored_contract`), and a ticket that is built replaces it.
4. **One shape of rule.** The contract's `Rule` is the only shape that is stored and edited. It gains an `unless`
   and example rows. What the builders read (`BusinessSpec`) and what a card shows are read out of it by code each
   time, never stored beside it. See "What exists today" for the four shapes this replaces.
5. **One rule per behaviour a person would notice.** An edge case is an `unless` or an example row, never a rule of
   its own. One rule is one test on the page; example rows are that test with several sets of values.
6. **Anchors.** A rule that is built records where it lives: the record's class, the action's method, the view, the
   test. They are written from the contract when the code is written, so none is guessed. A ticket's scope is the
   anchors of its rules. After a build every anchor must still exist, and a missing one fails by name. A build that
   renames something writes the new anchors itself.
7. **Two levels of scope.** The anchored class, method or view is given in full and may be changed. What it imports
   from the app is given as an outline (names, fields, signatures) made by code, and may not be changed. Changing an
   imported class means declaring it as a second anchor, and the card says the change is wider.
8. **The gate.** A ticket is done when its new rules are green and every rule it did not declare as changed or
   retired is still green. The gate runs once per ticket, not once per rule. A rule outside the ticket that turns
   red fails the ticket, the app is put back as it was, and the card says which rule broke.
9. **No retry to begin with.** A ticket that fails its gate is rolled back and reported. Whether a failed build gets
   a second attempt, and what it is shown, is decided when there are real failures to reason from. (Decided by the
   user; `pipeline.md` allows one retry on a verifier's verdict, and this uses none.)
10. **The plan is checked before Build is offered.** Every rule is in the strict form and names only records,
    fields, actions and situations the contract after the ticket holds; each has exactly one test; and no new rule
    contradicts a rule that is to stay green unless that rule is declared changed or retired. The last check reads
    two rules and says whether both can hold. That is a verifying step and judging is its whole job, so the
    principle that steps do not judge quality (which is about builders marking their own work) does not apply to it.
    What code can check is checked by code; only the contradiction needs a model.
11. **Roll back all three stores together.** A change touches the app's code, the engine's build state (contract,
    deck, manifest) and the app's saved records. A version is all three. Until records can be migrated, a ticket may
    only add fields that have a starting value, so every saved record stays valid.
12. **The kickstart is the first ticket**, on an empty contract: its scope is everything and nothing has to stay
    green. It runs without review, with every fork at its default, and its card is shown while the app loads; an
    edit there is the next ticket.
13. **Nothing existing is reused on its word.** Before a ticket builds on an existing function, the function is read
    and a test shows it does what the ticket needs. Its docstring is not evidence.

## What the person sees
A card before Build, in the person's words ("rules" and "the app", never spec, entity or assertion):

- the request as one short paragraph of what was understood; editing it plans again;
- each proposed rule as a card: title, Given / When / Then / Unless, example rows; it can be edited, removed, or
  added from a plain sentence;
- where what a person would see is ambiguous, two whole rules side by side with one chosen; about three such forks
  at most, and a request that needs more is split;
- existing rules that change or are replaced, marked so;
- one line: "Your N other rules will be checked too";
- the estimated time and cost, and Build, which is unavailable with one stated reason when a check fails.

Records, fields, scope and build order are behind "Advanced".

## What exists today
Read on 2026-10-12, before any of this was built.

**Four shapes of one rule**, left by four rounds of work, none removed when the next arrived:

| Shape | Where | State |
| --- | --- | --- |
| `Rule` | `backend/onboarding/product_contract.py` | What the model writes. Was never stored. |
| `BusinessSpec` | `backend/onboarding/router_engine.py` | What every builder reads (20 files). Made from `Rule` by `ProductContract.specs`, stored as `inbox_specs`. |
| rule card | `backend/onboarding/rule_deck.py` | A dict stored as `rule_cards`, made by cutting the spec's one line back into clauses with a regular expression. Test results are hung on the card, or on the spec when there is no card. |
| `RuleCard`, `TestSpec` | `backend/domain/model.py` | `RuleCard` is constructed only by tests. `TestSpec` belongs to the requirements flow, whose endpoints the Studio no longer calls. |

So one rule is stored twice in two forms, and edits reach only one of them.

**Adding a rule today** (`/api/specs/deck/add` in `backend/entrypoints/routers/specs.py`, then
`execute_inbox_spec_tdd` in `backend/service_layer/services.py`):

- the card's Unless is not passed on: the line the test is written from is joined from Given, When and Then only;
- the rule has no action and no situation, and its class is the card's `target`, which the request defaults to
  `global`;
- only the domain class is changed. The page is not, so a new rule cannot be reached by a person, and no page test
  is run;
- the answer is `success: true` whatever the build said; the card's id is a random number from 100 to 999.

**Rolling back today**: the test loop (`backend/service_layer/tdd_machine.py`) puts one domain file back and reruns
the domain's unit tests after every rule. Nothing commits to the app's repository except the earlier agent loop in
`backend/agent_orchestrator.py`, which the kickstart does not use. The page has a guard of its own
(`backend/service_layer/rule_tests.py`, `backend/onboarding/rule_fix.py`): a fix is kept only when every green
page test is still green. Neither covers the build state or the saved records.

**Cutting out one part** exists and is what scoped building starts from: one class
(`backend/onboarding/cst_isolator.py`) and one view (`backend/onboarding/presentation_specs.py`). Both are to be
proved by a test for the ticket's use before they are relied on (decision 13).

## Order of work
A thin slice first, because the planner's prompt is the part most likely to be wrong and should meet a model early.

1. Done: the contract is stored.
   Done: the ticket as a typed delta and its application (`backend/onboarding/change_ticket.py`), and the planner
   (`backend/onboarding/ticket_planner.py`, prompt `backend/prompts/change_ticket.md`, on the model the contract
   is written on). So far a ticket only adds: fields, actions, situations, refusals, read-out names, rules, and
   parameters of an action the app already has.
2. The slice: one ticket that adds one rule to an existing record. The ticket as a typed delta of the contract;
   the planner that writes it from the request, the brief and the stored contract; the delta applied; the rule
   built in the record's class and on the page; the gate once; roll back on red. No Studio work, no retry, fields
   only with starting values.
3. One shape of rule: `unless` and example rows on `Rule`; the deck and the builders' specs read out of the stored
   contract; `RuleCard`, `TestSpec` and the requirements flow removed.
4. The checks of decision 10, and anchors.
5. Versions: the three stores together, a changelog entry in plain words, undo.
6. The Studio: the text box in the live workspace, the card, the pre-kickstart view removed.
7. The kickstart as a ticket; forks; a large request split into follow-up tickets; estimates.

## Measured: the planner alone
One call per request on the middle model at low effort, against a recorded contract of a game (17 rules, a button
that does something new) and a small contract of a booking page (3 rules, a note on the form). Each answer was applied
to its contract by code.

| Product | Seconds | Cost | Rules added | Applies |
| --- | --- | --- | --- | --- |
| Game | 10 | 0.35 SEK | 5 | yes |
| Booking | 7 | 0.20 SEK | 3 | yes |

The first form of a ticket could only add actions. The booking request belongs to the form a guest already sends,
and the planner, given no way to say so, wrote the field and no rule at all. A ticket can now carry an action the
app has, whole, with parameters added (it keeps every one it had and is sent the same way), and both requests plan.
Whether the builders can build from these tickets is not measured: nothing is built from a ticket yet.

## Consequences
- A change costs one planner call plus the build of what it touches, and the gate's test run. The gate's run grows
  with the number of rules; it is run once per ticket to keep that linear.
- Until step 3, an app's rules still live in three places and a rule added through the deck is still built by the
  path described above.
- An app built before the contract was stored has none, and cannot take a ticket until it is built again.
