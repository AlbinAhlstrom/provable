# ADR-009: Which kinds of product the engine builds, and in what order it learns the rest

Status: accepted (roadmap). Follows [[ADR-007 Product Intent Step]] and [[ADR-008 Aggregate Ownership and Audience-Scoped UI]].

## Problem
Most prompt tuning was done on one shape of product: a business that publishes content to visitors on a single page. A pitch of another shape (a game on a grid) then showed two things at once:

- **Wording bias.** The prompts ask every product for what that one shape needs: a headline in the product's own voice, a brand header and a footer, one accent colour, "what the page says about the business". A product with nothing to say there fills the space with invented text, and a product people know by sight is given an invented look.
- **Capability gaps.** Some products cannot be built whatever the prompt says, because the generated app has no place for what they need (a rule that reads a second record, a second screen, a clock).

## Decision
1. **Every kind in the table below is in scope.** They are reached in phases; until a phase lands, the kickstart says plainly what the product needed that the engine cannot build yet.
2. **Kinds are a review lens and a test matrix, never a branch in the pipeline.** `.claude/rules/pipeline.md` ("Derivation, not classification") stands: no stage keys its behaviour off a kind. A prompt rule is written in terms of a property a product has (it is known by sight, it lists many records, its page is meant to persuade), so it applies to every product with that property.
3. **A prompt change is checked on two pitches of unrelated kinds** from the matrix, with the smallest run that shows it (a page rebuild for page rules, see [[Page Rebuild]]).

## The lens
A product is described by properties, and a kind is a common combination of them:

- **What its page is for**: to persuade, to do a job again and again, to play, to read, to look up numbers.
- **Who writes the records**: the owner publishes them, the audience creates them, or time and other systems do.
- **How many records are on screen**: one in focus, a handful, hundreds.
- **Who sees whose records**: everyone sees the same, each person their own, or it depends on a role.
- **Where its rules live**: on one record, across several, or nowhere.
- **What moves it**: only what the person does, a clock, or what other people do meanwhile.
- **Whether people know it by sight**: a familiar form and look, or none.

| Kind | Example pitches for the matrix | State before this ADR |
| --- | --- | --- |
| Text that persuades | a personal firm's website, a restaurant's page | Good: the prompts were written for it |
| Rules on one record | a grid game, a product configurator | Works; invented look and filler text |
| Rules across records | stock that orders draw down, slots that cannot be double-booked | Not possible: a class reads only its own fields |
| Many records | an inventory, a contact register | Weak: no edit, search, sort or paging; starts with 3 to 5 records |
| Several roles | a help desk with customers and agents, a marketplace | Half: only the audience gets a screen |
| A person's own records | my orders, my bookings | Not possible: nothing knows whose a record is |
| Numbers and charts | a sales dashboard | Nothing supports it |
| Reading | a blog, a recipe collection | Weak: one screen, no page per item, no images |
| Driven by a clock | a timed quiz, an auction | Not possible: nothing advances time |
| No records | a calculator, a unit converter | Awkward: a record must be created to compute |
| No page | an API, a data pipeline | The intent step can name it; the pipeline builds a page anyway |

## Roadmap
Ordered by how many kinds a phase helps per unit of work. Each phase names what it unlocks, where the change goes and the pitch that proves it.

### Phase 0: wording (prompts only)
- The look follows the familiar thing: for a product known by sight, its usual look (colours, surfaces, its parts built as one unit) is the direction; a feel is invented only where there is none.
- Every text on a page has a job: a label, a state, an instruction needed to act, or a record. A header, a footer and a first-screen headline are written when they have something to carry.
- A product keeps the name its pitch gave it.
- Rules about "the business" are stated for whoever publishes the records.
- A wide thing (a table, a grid, a timeline) scrolls inside its own container; the page itself does not.
- Starting records: as many as such a product would really hold; entities: as many as the value loop needs.
- Where: `backend/prompts/prompt_expansion.md`, `backend/prompts/router_decomposition.md`, `backend/prompts/ux_planning.md`, `backend/prompts/presentation_projection_synthesis.md`, `backend/prompts/seed_data.md`, `backend/prompts/visual_review.md`.
- Proof: page rebuilds of a grid game and a personal firm's website.

### Phase 1: the matrix and honest limits
- One pitch per kind, kept in the repository, with a script that runs the cheap stages (intent, expansion, decomposition) for all of them and one full kickstart on request.
- The intent step lists what the pitch needs that the engine lacks; the kickstart result and the Studio show it.
- Where: `scripts/`, `backend/onboarding/intent.py`.

### Phase 2: a record holds what its own rules need
- A value an action needs from a record it refers to is copied onto it when it is created (a line keeps the price it was sold at, a session keeps the size it was started with). Stated in the decomposition contract and checked against the action manifest.
- QA fails a page whose main view shows none of the parts its layout promised.
- One rule per behaviour, not one per case of it.
- Where: `backend/prompts/router_decomposition.md`, `backend/onboarding/action_protocol.py`, `backend/onboarding/qa_gate.py` and its checks.
- Proof: the grid game on the cheaper model.

### Phase 3: many records
- The generated API gains an update, and the list takes search, order and a page size.
- Starting records for every entity the audience works with, not only for published content.
- The UX plan can name a table as the form of the main view; the page gets editing in place.
- Where: `backend/onboarding/skeleton_builder.py`, `backend/onboarding/seed_data.py`, `backend/prompts/ux_planning.md`.
- Proof: an inventory with two hundred items.

### Phase 4: several views
- The UX plan becomes a typed list of views with routes (a list and the page of one item); the page stage writes one file per view instead of a fixed set of four.
- An attribute can hold an image address the owner supplies.
- Unlocks reading, a shop's item pages, and a screen per role.
- Where: `backend/onboarding/presentation_projection_synthesizer.py`, `backend/onboarding/planning_contracts.py`, the scaffold in `backend/onboarding/skeleton_builder.py`.
- Proof: a recipe collection.

### Phase 5: rules across records
- An action declares which other records it reads; the generated router loads them through the unit of work and hands them to the method, and the RED test builds them as plain objects.
- Unlocks stock, double booking, uniqueness, capacity.
- Where: `backend/onboarding/action_protocol.py`, `backend/onboarding/skeleton_builder.py`, `backend/prompts/domain_engine_synthesis.md`, `backend/prompts/red_test_generation.md`.
- Proof: bookable slots that two people cannot take.

### Phase 6: who sees and does what
- A person is known to the app (a session at first, accounts later); a record knows whose it is; lists are scoped to it.
- Actions performed by someone other than the audience get a screen of their own for that role.
- A field can be hidden from the audience, so the browser never receives what the person must not know yet (what a covered cell holds, another person's details).
- Where: `backend/onboarding/skeleton_builder.py` (schemas, routers), `backend/onboarding/action_protocol.py`, the UX plan's views from phase 4.
- Proof: a help desk with customers and agents.

### Phase 7: time
- What depends on time is computed when it is read (elapsed time from when it started) and passed to methods as an argument, as the tests already do.
- Actions an automated process performs are run by a scheduler in the generated app.
- Proof: a timed quiz.

### Phase 8: numbers and charts
- Read endpoints that total and group records; a chart component in the scaffold; the UX plan can name a chart as a view's form.
- Proof: a sales dashboard.

### Phase 9: products without records or without a page
- A computation is served without storing anything.
- An API or a pipeline is built as such, with its documentation as what the Studio shows.
- Proof: a unit converter; a small API.

## Consequences
- Phases 0 to 2 are prompt and contract work and help every kind already half-supported. Phases 3 to 9 change what the skeleton generates and each needs its own ADR when it starts.
- The matrix replaces "the pitch we happened to be debugging" as the measure of a prompt change.
- Until phase 6, a product with hidden information sends it to the browser; until phase 7, a planned timer does not run. Phase 1 makes the engine say so.
