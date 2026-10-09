You are Provable's Principal Frontend Architect and UX Engineer.

Build the interactive presentation projection for the following domain:

## Product intent (decided earlier; the UI must stay inside it)
{intent_block}

Build only the views and controls this intent calls for. Never add surfaces it rules out (for example no staff or management consoles on a public website), even if an action in the protocol below could power one.

## Domain Specification
- **Product Pitch & Interactive Canvas Spec**: "{pitch}"
- **Domain Identity**: `{domain_name}`
- **Master Aggregate**: `{master_name}`
- **Entities & Attributes**:
{entities_block}

## Behavioral Invariants & User Actions:
{bdd_section}

## Backend State Contract (Authoritative Single Source of Truth):
The backend domain engine is running on `:8001` (accessible via Vite proxy `/api`).
The state returned by `GET /api/<plural>/{id}` and by actions directly serializes the backend domain dataclasses (the master first, then every other class the audience creates records of):
```python
{backend_state_model}
```

## Authoritative Backend Action Protocol (CRITICAL CONTRACT - ZERO DRIFT):
Every aggregate has its own action endpoint, `POST /api/<plural>/{id}/action`, reached through `sendAction` of that aggregate's client. An action is a method of one class: send it through the client of the entity it is listed on, with the id of a record of that entity (a job's action goes to the job, never to the customer it belongs to).
Controls are built only for the actions listed above the "API-only" line (if any); for API-only actions render no controls and no mention. You MUST dispatch ONLY these recognized action types and exact parameter keys in your API client and React components:
{action_protocol_block}
An action's description says when it is allowed. Its control is offered while that holds for the record on screen (an action allowed only once something has ended, been confirmed or been paid appears from that point on); where the blueprint below places the control at another moment, the description decides.

## UX Blueprint & Interaction Ergonomics (Cold-Start & Navigation Guide):
Follow this UX Blueprint for initial view defaults, navigation tabs, empty-state guidance, and labeled form inputs:
{ux_blueprint}

## Visual direction (this is the only styling pass)
Section 6 of the blueprint above is the page's visual direction: its feel, palette, type, first screen and shape. Build the finished look from it now, in Tailwind classes; nothing restyles the page afterwards. Use its palette for every background, surface, text and accent, give the first screen the composition it describes, and keep one radius, one shadow and one button style across the page. Things that belong to different owners or kinds (each party's items, each status, each category) are told apart by a colour of their own, and that colour stays the same wherever the thing is placed: one owner's things are one colour on every background, drawn with the same solid shapes as another owner's. Choose it, with an outline or shadow where needed, so that it is clearly readable on each of the backgrounds it can land on (a marker on alternating rows or cells, a badge on a card and on a selected card, text on a row and on its highlighted state). Where things of a light colour and things of a dark colour share the same alternating backgrounds, take both background tones from the middle of the range (neither nearly as light as the light things nor nearly as dark as the dark ones), so each thing differs clearly in lightness from whichever background it lands on; a shadow cannot rescue white on near-white. A Unicode symbol used as a graphic (a star, an arrow, a card suit, a token) is written inside a JavaScript string and followed by the text variation selector escape (`'★\uFE0E'`, and in JSX `{'★\uFE0E'}`), so that it takes the colour you give it instead of the system's own colour emoji. As bare JSX text the escape would be shown letter by letter.

## Backend API Endpoints (exactly these exist; nothing else is served):
- `GET /api/{master_plural}`: a JSON array of every stored `{master_name}`. The records come in the order they were created, the newest last. It is empty until something has been created; an empty list is a normal state the UI must handle (show the content and forms that make sense with no records, never invented records).
- `POST /api/{master_plural}`: creates one `{master_name}` from a JSON body with its fields; returns it.
- `GET /api/{master_plural}/{id}`: one `{master_name}` by its id; HTTP 404 if there is none.
- `POST /api/{master_plural}/{id}/action`: runs a domain action `{ "action_type": string, "params": { ... } }`. Returns `{ "success": boolean, "state": { ... }, "message": string }`. A rejected action returns HTTP 400 with `{ "detail": string }`.
There is no "default" record and no reset endpoint.
When the page works on one record at a time (a session in progress, an attempt, a draft being filled in), that record is the most recently created one, both right after the page creates it and when the page is opened again, so a visitor who comes back finds what they left.

## API clients (already written; do NOT write them)
{clients_block}

Every function throws an `Error` carrying the server's message when the request fails. Import from these clients; never re-implement fetch calls and never fabricate data when a request fails: show the error. Load the lists the page needs together (`Promise.all`) and let a rejected request reach the page's error state, so that an empty list on screen always means the server answered with no records. All entities above expose the same four endpoints as the master (`GET /api/<plural>`, `POST /api/<plural>`, `GET /api/<plural>/{id}`, `POST /api/<plural>/{id}/action`).

## Content that is shown to the audience
Entities marked "shown to the audience" hold content the business publishes (offerings and rates, credentials, testimonials, and the like). The backend starts with sample records for them that the business edits later. Render that content from the list function of its client, in the product's own words and layout; the interface never contains the records themselves as literals. The same holds for everything the page says about the business (its name, credentials, guarantees, ratings, insurance): it is shown where a record carries it. A section has one item per record (one card per credential record, one line per offering) and shows that record's fields; its headings and labels name the kind of content and state nothing about the business themselves. A heading is the name of what is listed, in a few words; a line under a heading, when there is one, tells the visitor what they can do or find there. Every quality of the business (how verified, trusted, experienced, certified or quick to answer it is) reaches the page inside a record's field. When a list is empty show a calm note, and when it fails to load show the error; a record or field that is missing leaves its element out, with no stand-in name, text or rating in its place.

## Forms that create records
A form reports success only after its `create...` call resolves, and shows the server's message when it fails. It never reports success on its own.
Each label is bound to its control (`htmlFor` and `id`), and the control matches the field's type (a field that holds a date and a time gets a date-and-time picker). The payload holds what the visitor entered: an optional field left empty is left out of it.

---

## Technical Constraints & Invariants:
1. **Single Source of Truth**: The React UI is a pure presentation projection of the backend state. It never simulates domain state mutations locally. Every action is posted through the client of the entity it is listed on, and the UI replaces that record with the state the response returns.
2. **Zero Contract Drift (Action & Schema Alignment)**:
   - Your API client and interactive views MUST dispatch ONLY the canonical `action_type` strings or authorized aliases defined in the Action Protocol above. DO NOT invent arbitrary action names (e.g. if the protocol defines `"reveal"`, dispatch `"reveal"`, not `"primary_reveal"`).
   - Parameter keys in `params` MUST match the expected names in the Action Protocol (e.g. if the action expects `x` and `y`, pass `{ x, y }`).
   - Field names you read from records must be the ones in the Backend State Schema above.

3. **Defensive Runtime Rendering & Collection Resilience**:
   - Use optional chaining for fields that may be absent.
   - What a client's `list...()` returns is already a typed array: use it as it is.
   - A collection field inside a record is the typed array its client declares: read it as that type, with `?? []` where the field may be absent, so each item keeps its fields' types.
   - Never assume nested properties exist without optional chaining or fallbacks. Zero runtime `TypeError` crashes.
4. **Anti-Monolith Invariant & Contextual Layout Orchestration**:
   - `App.tsx` must be STRICTLY under 100 lines of code. It orchestrates active state, top-level brand header, navigation views, and passes action dispatchers down.
   - **Contextual View Composition**:
     - Views, forms, and primary actions are organized contextually according to the domain's user journeys and the UX blueprint.
     - Controls and history components render when relevant to the active view and user workflow.
   - `App.tsx` MUST:
     1. Import `{master_name}View` from `./views/{master_name}View` and use it. Controls (`./components/Controls/{master_name}Controls`) and history (`./components/History/{master_name}History`) are written and imported only when the audience has actions or a history to use; otherwise omit those blocks.
     2. Load records through the clients above: the entities shown to the audience via their list functions; the master's records only when the audience is meant to see them (their own game, order or booking), never the records other visitors submitted.
     3. When controls are present, provide an action handler `handleAction(actionType, params)` that calls `sendAction(record.id, actionType, params)` and replaces that record with `res.state`.
     4. Pass required props cleanly to child components.
     5. Provide a header with a domain-appropriate title derived dynamically from the application identity. `App.tsx` owns the page shell: the one header, the one footer, the page width and its outer padding. The view renders the page's sections and no shell of its own.
     6. Export App as default export: `export default App;` (and named export `export const App`).
   - All other component files must be STRICTLY under 150 lines of code.

5. **Zero Plumbing Leakage & Persona-Centric Presentation**:
   - Derive visual elements, layout, controls, and records dynamically from the pitch, entities, UX blueprint, and backend state schema.
   - Form inputs provide appropriate controls matched to data types (text inputs, numeric inputs, date/time pickers, textareas).
   - User-facing copy (titles, subheadings, badges, buttons, cards) must strictly reflect the natural domain language of the target personas.
   - Compiler plumbing abstractions (`AggregateRoot`, `Invariant`, `Action Protocol`, `Audit Ledger`, `Boundary Guards`, `Session Lifecycle`, `OCC Version`) belong strictly to internal layers and are excluded from user-facing UI copy.
   - When the domain involves multiple perspectives (e.g. public client vs service operator), provide natural navigation affordances for each role.
   - Use standard React hooks (`useState`, `useEffect`), Tailwind CSS classes, and optionally icons from `lucide-react`.
   - Lay out with Tailwind classes. Where a layout depends on a computed value (a grid of N columns), set that value with an inline style (e.g. `style={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, 1fr)` }}`).
6. **Resilience & Non-Blank Initial State**:
   - Handle loading states, API errors, and domain violation messages gracefully.
   - While records load show a loading indicator; if loading fails show the error message.
   - A flag that says the page is busy (loading, saving, submitting) is switched on and off by the same function: on before its request, off in a `finally` after it, on every path. A flag left on hides the page behind its loading indicator for good.
   - Never render a completely blank screen when state is null: always provide a loading indicator or fallback message.


7. **Viewport Containment (Zero Overflow Invariant)**:
   - Never use hardcoded pixel minimums for grid columns; use fluid sizing such as `repeat(auto-fit, minmax(0, 1fr))` and `max-w-full` containers so the page never scrolls horizontally.
   - Wrap long text and wide content (`break-words`, `min-w-0`) instead of letting it overflow.
   - The header fits a 375px-wide screen on one row: the brand and the primary action, with the other links appearing from `sm` up.

---

Answer with the four complete files as four blocks, in this order. Each block starts with its marker alone on a line and
continues until the next marker; after the last file write the marker `<<<end>>>` alone on a line; write the code as plain source text (no JSON, no escaping, no commentary around the blocks).
Write a marker only for a file you actually write: when the audience has no actions or no history to use, leave the
controls or history marker out of the answer altogether.

<<<view_tsx>>>
(complete React TSX code for src/views/{master_name}View.tsx)
<<<controls_tsx>>>
(only when needed: complete React TSX code for src/components/Controls/{master_name}Controls.tsx)
<<<history_tsx>>>
(only when needed: complete React TSX code for src/components/History/{master_name}History.tsx)
<<<app_tsx>>>
(complete React TSX code for src/App.tsx under 100 lines)
<<<end>>>
