You plan one change to a product that is already built and in use. Its owner asks for this:

"{request}"

## The product as it is
The product was built from the contract below, and the contract is the whole truth about it: its records and their fields, the actions the page sends, the names its parts are read out by, the situations its rules start from, its refusals and its rules. Each rule has a test that passes today.

```json
{contract}
```

## Who reads what you write
Your answer is appended to that contract, and the changed product is built from the result. Four builders start from it at the same moment, and none of them sees the request, each other's work, or can ask you anything:
- one changes the code of the records behind the API,
- one writes a test for every new rule, before that code exists,
- one changes the page,
- one writes a test of the page for every new rule, before the page is changed.

They only agree where your answer is exact, so everything you add is written the way the contract above already writes that kind of thing: a field as its fields are written, an action as its actions, a rule as its rules. A name the contract already has is used as it stands. Every rule the product has today must still pass after the change, so you add to the product and leave what it does alone.

## What to decide
The owner says what they want in a sentence or two and is asked nothing further: decide. Read the request as the smallest change that gives a person who uses the product what was asked for, complete enough to use: where it is done on the page, what it changes, what the person then sees, and what is turned down. What was not asked for is not added, however natural it seems as a next step.

A change is proved by its rules, so every change has at least one. Write one rule for each thing a person would notice: what now happens when they do the new thing, and each way it is turned down. Most requests are one to three rules. A request that would need more than five is too large for one change: plan its first useful part and say in `understood` what you left for later.

## What to write
One JSON object with the keys below. A list with nothing to add is empty. Records and refusals are named in `CamelCase` (a refusal's name ends in `Error`); fields, actions, parameters and the values of a fixed set in `snake_case`.

- `title`: the change in a few words, as the owner would name it in a list of changes.
- `understood`: one sentence of at most twenty everyday words, saying what will be different for a person who uses the product once the change is built. The owner reads it at a glance to check you understood, so it says the one main thing and leaves the rest to `decided`; it holds none of the contract's names.
- `decided`: each choice you made that the request left open, as a line of its own of at most twelve everyday words, saying one thing: where it is done, what is left out, a limit you set, when it does not apply. What the request itself said is not repeated, and neither is what stays as it was. A request that left nothing open has none. It holds none of the contract's names.
- `fields`: each field a record gains, written as the contract's fields are, with `record` naming the record it is added to. Records already saved keep working without being touched, so `starts_as` is a plain value of the field's type (a number, `true` or `false`, one of its `values`, a short text) or empty for a field that starts with nothing. Add a field only when a rule reads or changes it or the page shows it.
- `actions`: each action that is new or does more than before, written whole, as the contract's actions are. Something a person does that creates or changes a record is an action. Where the change belongs to something a person already does (one more thing to fill in on a form they send, one more choice when they place or start something), it is that action of the contract under its own name, with every parameter it has, the new ones after them, and `does` saying everything it now changes; it is still sent to the same record in the same way, and a new parameter may be left out by a person, so that everything done with the action today still works. Otherwise it is a new action with a name the contract does not have. `does` names every field changed; `works_with` lists every kind of stored record the action's rules read or change besides the one it is sent to.
- `read_out`: one entry for each new part or control on the page, as `part · role · "name"`, with the role one of button, textbox, grid, gridcell, dialog, menuitem, checkbox, status, heading, list, listitem, img, and a name built from a record's values written as a pattern with the fields in braces: the control of every new action, the part that shows every new field, every new message.
- `situations`: a rule starts from a situation. Use one the contract has wherever its values show the rule. Add one only when none does, written as the contract's are and as small as shows the rule: `name = what it is in a person's words: the values it holds`, and where it differs little from an existing one, as that one's name and what differs.
- `refusals`: one entry per way a new action is turned down, written as the contract's are, with the exact sentence the person reads and where it appears.
- `rules`: each new rule, written as the contract's rules are. `given` is the name of one situation, of the contract or of this answer, and after it only what differs. For a rule the records obey, `action` is exactly one action and `when` is that action with the value of every parameter; `then` gives the fields and values afterwards, or the refusal by name, or "nothing changes"; `sees` names each part of `read_out` that changed, as it is then read with the values filled in, and a refusal by its sentence. For a rule of the page alone, `action` and `then` are empty and `when` is the gesture and the part it is done on. `plain` is the same rule as a person who uses the product would tell it to another, as `Given ..., When ..., Then ...` in everyday words, each of the three short enough to read at a glance. Its When always describes the concrete thing the person does: the gesture and what it is done on, as the action's `trigger` gives them (the mouse's gesture where a mouse and a finger differ), never a word that only names the action.

Before you answer, go through each new rule against what you wrote: its situation holds the values its outcome depends on, its action and every field it names are in the contract or in this answer, and what `sees` promises is a part of `read_out`.
