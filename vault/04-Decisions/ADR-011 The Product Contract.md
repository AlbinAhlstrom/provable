# ADR-011: The product contract, one answer everything is built from

Status: accepted, first two steps implemented (the front of a kickstart, and the domain in one round). The later
steps are listed under "Order of work".
Replaces, for a live kickstart, the separate steps of [[ADR-007 Product Intent Step]] and the expansion,
decomposition, action protocol and UX plan that followed it. Builds on
[[ADR-010 One Kind of Rule Proved on the Page]].

## Problem
One pitch ("a minesweeper game") took 280 s to build and another 210 s to test, against under three minutes for a
comparable product elsewhere. The timeline of that run:

- The front was five model calls in a row before anything was built: intent, expansion, decomposition, then the
  action protocol and the UX plan (some 60 s). Each re-read the one before and was free to name things its own way.
- Nothing fixed the fields a class holds before the page was written against them. The test loop added fields, so
  the page was written twice (91 s, then 108 s).
- The names a page test finds a part by were decided by the page writer and guessed by the test writer.

## Decisions
1. **One call says what is built.** The product contract (`backend/onboarding/product_contract.py`, prompt
   `backend/prompts/product_contract.md`) names the product and what it has, the look, what a person meets on
   arrival, the records and their fields, the fixed values, the actions with where each is done, the names parts are
   read out by, the refusals with their exact sentences, and the rules.
2. **Everything later is read out of it by code.** The domain structure, the rule deck, the action manifest, the
   intent and the page's blueprint (with the draft theme's `TOKENS` and `LAYOUT` lines) are methods of the contract.
   The action protocol and UX plan stages are answered from it without a call of their own
   (`kickstart_front.Front.stage_overrides`), so builders that start side by side cannot disagree.
3. **It runs on the middle model at low effort.** Measured alone on three kinds of product: the middle model answers
   in 24 to 37 s; the small one took 30 to 141 s and wrote up to ten times the hidden thinking, and more effort made
   neither better. The dilemmas are spelled out in the prompt instead (an inventory of what the product has, each
   entry kept or left out with the reason).
4. **The schema holds what code reads.** The answer is a structured one. Who performs an action, the kind of a rule
   and the type of a field are fixed sets, and every key is required, so an action "by user" or a rule without its
   action cannot be written. The provider refuses a schema whose properties and lists together count more than about 65
   (measured; `SCHEMA_WEIGHT_LIMIT`, guarded by a test), so what is read as words is a text or a list of texts, and
   what one part of a list holds is a field of the same list (`part_of`) rather than an object nested inside it.
5. **A rule is of the records or of the page.** A rule the records obey names exactly one action and goes through
   the domain's test loop; a rule of the page alone (no action is sent) does not. Both are proved on the running
   page as ADR-010 says. The spec kinds `behavior` and `presentation` carry this distinction and nothing else.
6. **No contract, no build.** A provider error or an answer that is no contract fails the kickstart with the reason.
   Nothing is retried and nothing falls back to the earlier front.
7. **The domain is written in one round.** The actions' methods and the deck's rules used to be two passes of the
   test loop, the second waiting for the first (61 s, then 52 s). Both are named before either starts, so they are
   one batch (`backend/onboarding/domain_round.py`): every first test side by side (one per action, one per rule,
   one for what a new object holds), then one code answer per class. Measured alone on the same contract: 57 s,
   every action and all 15 rules fulfilled. Writing first tests ahead of the loop, which only existed to fill the
   wait, is gone.
8. **What the contract says of a field is in the class.** The class's description is what the test writers, the
   code writer and the page writer all read, so it carries each field's `holds` (a position counted from 1), and
   the one form a date, a time and a moment are written in (`product_contract.FORMS`; a moment always with its
   UTC offset). Before, one writer wrote a moment without an offset and another with, and they could not be
   compared.
9. **The earlier front stays for comparison.** An offline or mock kickstart runs it (no model is called), and a live
   one does with `KICKSTART_FRONT=stages`, so the two can be measured on the same pitch
   (`backend/onboarding/kickstart_front.py`).

## Measured: hidden thinking
The small model thinks by default, and at low effort that was 70 to 80% of what its writers were billed for.
Measured by replaying recorded prompts and by whole domain rounds in a scratch folder, thinking on and off:

- **The page**: 67 to 70 s with thinking, 12 to 13 s without; all answers pass the type check and use the
  contract's read-out names. Whether the page behaves the same was not measured.
- **The domain round, a product with few rules that interact (a booking)**: 48 to 50 s with, 28 to 29 s without,
  everything fulfilled either way once a starting state held by the defaults had no spec.
- **The domain round, a product whose rules interact (a board game)**: 58 to 65 s with and everything
  fulfilled; 25 to 45 s without, and every one of four runs left something unfulfilled. What remained after
  the settled dilemmas (decision 8, the action's one call, the starting state) was work, not a choice: a Given
  whose counts agree with where its pieces are, and one class that passes twenty tests.

So the page is written without thinking (`llm_provider.Provider.unthinking_stages`; a call made so is marked
`thinking: off` in the trace), and the test and code writers keep it. Thinking off for the tests alone saves
little: the code answer is the long call. A stage moved to another model by `LLM_MODEL_<STAGE>` keeps that
model's default. A first page rebuild so written took 12 s and passed QA; its page tests could not judge it,
because a rebuild plans the page anew and the stored tests were written for the earlier plan's wording.

The first whole build so written showed what the check above had missed: the page compiled, used the right
names and was a fifth of the planned size. A menu entry, the dialog it opens and two effects the plan named were
absent in four of four replays; with thinking they were there in two of two, at 98 to 108 s. The plan was not
unclear, only long: the parts were spread over six sections of 36,000 characters, and a writer that does not
think first writes the part it meets first and stops. So the extent of the page is now stated once, as a list
(`backend/onboarding/page_parts.py`): the plan's read-out lines are the page's parts, the prompt closes on them,
and the answer opens with a `<<<parts>>>` block that says, part by part, which file it is written in and what
brings it up. That block is the thinking the page needs, written where it can be read. The list alone left
the dialog out in one of three; with the block every part was there in four of four (16 to 19 s) and, on a
booking page, three of three (14 to 16 s). The same list is checked against the written files in QA, and a part
that is absent is a defect for QA's one rework, which is then shown the plan.

## Who makes the first record
A page that works on one record (a round, a draft) has to have one when a person arrives. That used to be a
clause in the opening's prose ("if none exists the page creates one with ..."), and one page in about twenty
left it out: it listed the records, found none and showed its loading text for good. QA measured a tidy page.
It is now a fact of the contract and code acts on it. A record's `origin` has three values: `created_by_person`
(a form or a button: an order, a booking), `created_on_opening` (the page makes one by itself when it opens and
finds none) and `exists_from_start`. For a record made on opening the generated client exports `open<Record>()`:
the newest record, or a new one in its starting state. The page's writer is told to call it once and never
writes the list-or-create itself. Measured: the contract chose the origin as meant for a grid game, a booking
page and a board of cards, and six of six pages written from the game's contract call the open function and
neither list nor create a record themselves.

## What a rule is written from
A rule used to start from loose words ("playing, a hidden square with no mines around it") and end in free prose
("the square looks flat", "clicking outside closes it"). Every test writer then made up its own whole state, which is
where its hidden thinking went and where states the product can never be in came from; and the page writer and the
test writer each read the outcome their own way, so neither a pass nor a fail said much.

- **Situations.** The contract writes the few states its rules start from once (`situations`, each as
  `name = what it is in words: the values it holds`), as small as shows the rules and with nothing left to chance.
  A rule's Given names one. The spec carries it (`BusinessSpec.situation`), and both test writers are shown it and
  told to arrange exactly that.
- **One action, with its values.** A rule's When is one action with the value of every parameter. What has to have
  happened first belongs to the situation.
- **Outcomes that are read out.** `sees` names the parts of `read_out` that changed, by the name each then carries.
  A part a rule tells apart by its state says that state in its name; a look alone is the look's, not a rule's.
- **Two wordings.** `given_when_then` is the exact line tests are written from, in the contract's names. `plain`
  is the same rule as a person who uses the product says it, which is what a card shows.
- **The deck is the contract's rules and nothing else** (`backend/onboarding/rule_deck.py`). Six cards every
  product used to get (a visual workspace, a status display, viewport containment and the like) are gone: no rule
  stood behind them, so their tests were invented and their verdicts said nothing. What they stood for is QA's.
- **A rule's record is read, not written.** It is the record its action is sent to; for a rule of the page alone,
  the record a person or the page makes.

Measured on the minesweeper pitch, the first tests of the eleven rules written side by side: the slowest took 15 s
(30 s before) and the mean 11 s (15 s). The contract itself grew by about 5 s (32 s to 37 s).

## Consequences
- The front is one stage (`contract`) of some 25 to 40 s in place of five.
- Later writers read the contract's brief where they read the expanded pitch. The stored specification also holds
  the page's plan, so a page rebuild plans from the same look.
- The contract is not stored as a record of its own; a page rebuild still calls the UX planner. Storing it is part
  of the next step.
- A structured answer costs more tokens than free text. Not yet measured against the earlier front on a whole run.

## Order of work
1. Done: the contract as the front of a live kickstart.
2. Done: the domain's tests are written from the contract's actions and rules in one round, before the code.
3. Page tests are written from the read-out names while the page is written, before it exists.
4. The page is not sent back when a class gains a field, because the contract already names every field.
5. One test run at the end, and a fix-up that is an emergency exit, not a stage to rely on.
