You decide what a product is, how it looks, and the contract its two halves are built against. A user has given this pitch:

"{pitch}"

## Who reads what you write
Four builders start from your answer at the same moment, and none of them sees the pitch, each other's work, or can ask you anything:
- one writes the records and their rules as code behind an API,
- one writes a test for every rule, before that code exists,
- one writes the page,
- one writes a test of the page for every rule, before the page exists.

They only agree where your answer is exact. A field, an action, a status, a refusal, a label, a visible wording or the name a part is read out by is used by all four as you write it. Anything you leave open is guessed four different ways. So every name appears once, in the part of the answer that owns it, and every rule is stated in those names.

The product is one loop of use, done well: what a person does from arriving to being done, with the choices the product is known to offer on the way. A product people know by sight (a well-known game, a month calendar, an inbox) looks and behaves the way they know it, and it is built whole: every part, every choice it is known to offer (how hard, how large, which view, which period) and every convenience people expect of it belongs to it. Each choice is offered where and how the thing itself offers it (in its menu, its toolbar, its dialog), not in a control of your own making. What the thing has never had is not added to it: no extra panel, no extra shortcut, no extra line of text; what it tells a person without words (by a colour, a mark, a count, a picture that changes) it does not say again in words. Left out is only what a single page with one API cannot have (accounts, payment, messages sent to people) and what acts on the machine around the product (sound, printing, quitting); nothing is cut to keep the product small. Nobody is asked anything: decide.

How it is built, so that you decide inside it: one page in a browser and one API that stores records. The page sends an action to the API and shows the record that comes back; nothing runs beside the two. Everyone who opens the page sees the same records, and sees what others changed when the page next loads them.

## What to write
One JSON object with the keys below. Every text is short; a list is written out to its last item. Records and refusals are named in `CamelCase` (a refusal's name ends in `Error`); fields, actions, parameters and the values of a fixed set in `snake_case`. A name is written the same way everywhere it appears.

### `product`
- `name`: the product as the pitch names it, or the plain name of what it is, with nothing added.
- `product_type`: the kind of product it is, one of `public_website`, `customer_app`, `internal_tool`, `api_service`, `marketplace`, `game`, `data_pipeline`, `other`.
- `audience`: who uses it.
- `loop`: what a person does from start to finish.
- `has`: every choice, setting and convenience the product offers a person, one entry each, and for a product known by sight every entry of its menus, toolbars and dialogs; each entry ends in "(kept)" or "(left out: the reason)". Everything kept appears below as fields, actions and rules.

### `look`
- `summary`: one sentence for the look as a whole.
- `tokens`: the five colours and the heading typeface the page is themed with before it is written, as one line in exactly this form, each colour a six-digit hex value and the typeface one of `serif`, `sans`, `mono`: `background=#f4f1ea surface=#ffffff text=#1f2328 accent=#0b6e4f on_accent=#ffffff heading=sans`.
- `palette`: every colour as a hex value with what it is for, separated by semicolons.
- `type`: the typeface and sizes.
- `parts`: one entry per part a person sees, in the order the parts sit on the page, starting with what lies behind and around the main view, at most 30 words each: the part, where it sits, its size in pixels where it has a fixed one, its colour and surface (flat, raised, sunken, outlined, shadowed), what it shows, and every other look it can have with what brings that about (while pressed or held, when selected, unavailable, finished, failed). Where things of one kind are told apart by a colour or a mark, every one of them is given its colour or mark.
- `narrow`: what changes on a screen 375 pixels wide (what stacks, what scrolls inside itself, what shrinks).
- `grid_columns`, `grid_rows`: when the main view is a grid of equal parts (a playing field, a calendar month, a seating plan), how many columns and rows it opens with; 0 for a view that is not a grid or grows with its content.

### `opening`
What a person meets on arrival, before doing anything, in three sentences: which records exist at that moment and which one the page shows (the newest, a chosen one, a list of all), and when none exists yet, what the page does about it (creates one with which values, or shows which empty wording); the parts visible and what each holds at that moment; and what a person sees who reloads the page in the middle of the loop.

### `records`
A record is something the API stores. What a person has picked or typed but not yet sent (a half-filled form, an open menu, a highlighted choice) is the page's own: it is no record and has no field here.

One entry per kind of record: its `name` and its `origin` (the page creates it, or it exists from the start; a kind that exists from the start gives its `starting_records`, every one with its values, separated by semicolons). Its `fields`, one entry each:
- `name`, `type`, `starts_as` (the value a new record holds, empty when it has none) and `holds` (a few words on what it is). Every record has an `id` you need not list. A date is written `YYYY-MM-DD`, a time `HH:MM`.
- A field that points at another record holds that record's id and is named after it with `_id` at the end.
- A field of type `one_of` lists in `values` every value it can hold, one entry each as `value: what it means; shown as "the wording or mark a person sees for it"`. Every other field has no values.
- A field of type `list_of_parts` holds smaller things the record owns: `part_name` names one of them in `CamelCase`, and `starts_as` says how many there are from the moment the record exists (empty for a list that starts with none). A list the page draws is whole from the start, never filled in later. What one part holds follows the list as fields of their own, each with `part_of` set to the list's name; `part_of` is empty for a field of the record itself.
- Include every field a rule reads or changes, and every field the page shows: a value the product must remember between two actions (the last choice made, whether something has already been counted) is a field.

`shown` lists each value the page shows that is worked out from fields (a remaining count, a total, a free or taken slot), as `name = how it is worked out`.

### `fixed`
Every number or wording the rules depend on that never changes (a limit, opening hours, a size per level), one entry each as `name = value`, stated here once and used by name below.

### `actions`
An action is something the page sends to the API that creates or changes a record; picking and typing before that are not actions. One entry per action:
- `name`, the `record` it is sent to, and its `params`, each as `name: type`.
- `performed_by`: `audience`; `automatic` when it happens by itself while the product is in use, and the page sends it when its moment comes; or `other` when it is done by whoever runs the product, with no control on the page.
- `trigger`: for an action of the audience, the part it is done on, the gesture (both mouse and finger where they differ), and the exact label a person reads on it, in quotes, if it has one. For an automatic action, the moment the page sends it, as words that complete "the page sends it ...". Empty for `other`.
- `does`: everything it changes, in the fields and values of `records`, including what follows from it in the same moment (a result recorded, a total brought up to date, a status that moves on). Nothing changes a record except an action listed here.

Where an action depends on the present moment (what is past, what is due, how long something took), it takes that moment from the API's clock; where it depends on chance (what is dealt, where something is placed), `does` says what must hold of the outcome whatever the chance.

### `read_out`
How each part is found by someone who cannot see the page, and by a test: one entry per part or control, as `part · role · "name"`, with the role one of button, textbox, grid, gridcell, dialog, menuitem, checkbox, status, heading, list, listitem, img. A name built from a record's values is written as a pattern with the fields in braces (`"Row {row}, column {column}, {state wording}"`, `"Table {number}, {status wording}"`) and is the same in every state except for those values. Include every control of `actions`, every part that shows a field, and every dialog and message.

### `refusals`
One entry per way an action is turned down: its `name`, the `action` it belongs to, `raised_when`, the exact `sentence` the person reads, and where on the page it `appears`. An action that is simply ignored (nothing changes, nothing is said) is not a refusal; the rule says so.

### `rules`
One entry per rule. Every rule that governs the loop is here, with its special cases and exceptions as rules of their own; where the product follows an established set of rules, every rule of that set. Each has a short `title`, the `record` it is about, and a `kind`:
- `api`, a rule the records obey: `given` the fields and values the records start with; `action`, exactly one action of `actions`, and `when` that action with its parameters; `then` the fields and values afterwards, or the refusal by name, or "nothing changes"; `sees` what the person sees on the page as a result, in the names of `read_out` and the wordings and looks above.
- `page`, a rule of the page alone, where no action is sent (what is offered or unavailable, what a held press shows, what a dialog does when dismissed): `given` what the page shows, `when` the gesture, `sees` the result; `action` and `then` are empty.

A rule about something that follows from an action (the loop ends, a result is recorded) is an `api` rule whose action is the one that brings it about, from a `given` one step before it. `states_limit` is true for a rule that states a limit; such a rule gives the number, by its name in `fixed`.
