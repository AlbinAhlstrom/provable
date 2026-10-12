You are writing the product specification that a product is built from. A user has given this pitch:

"{business_pitch}"

## Product intent (already decided: do not contradict it)
{intent_block}

The specification elaborates the product inside this intent. It adds no persona, workflow, entity or feature the intent rules out, and it does not turn the product into a different kind of product than the one stated.

## Who reads the specification
The people who build the product read this specification and nothing else. They do not see the pitch and they cannot ask you anything. One of them decides how the page looks, one writes the page, and one turns every rule into a test.

- What the specification states exactly is built as stated.
- What it leaves to a phrase ("as in the original", "the usual colours", "and so on", "a clean modern look") is filled in with a guess, and the guess is a generic page that could belong to any product.
- What it does not mention is not built.

So wherever you know a detail, write the detail: every colour by name, every part, every state, every rule. A list is written out to its last item.

## What to write

### 1. People and their journey
- The human roles that use this product: only the roles the intent implies. If it implies one, do not invent another.
- For each role: what they need to see, decide and accomplish, and the path they take from arriving to being done.
- A role outside the intent's audience (for example staff who handle what the audience submits) may be named in one line where a lifecycle needs it, marked as outside the interface. It gets no screens, journeys or controls.

### 2. How it looks
Start with one sentence that says what the product looks like as a whole. When the product is of a kind people know by sight (a well-known game, a month calendar, a spreadsheet, an inbox), it looks the way they know it: name that look, and then describe it closely enough that someone who has never seen it could draw it. Only a product with no such look gets a look of its own: the character that fits the audience named in the intent, described just as closely.

Then one line for each part a person sees, in the order the parts sit on the page, starting with what lies behind and around the main view. A line is at most 30 words. It names the part, says where it sits, gives its colour and surface (flat, raised, sunken, outlined, shadowed) and what it shows, and then every other look the part can have with what brings that look about (while it is pressed or dragged, when it is selected, unavailable, finished, failed). Where things of one kind are told apart by a colour or a mark, the line gives every one of them its colour or mark.

A product known by sight is described as the thing itself, the one people picture, and not as a page made after it. It keeps what it is seen in and against (the titled window of a desktop program and the desktop behind it, the table under a card game, the coloured backdrop of a well-known tool), and it offers each choice where and how the thing itself offers it (in its menu, its toolbar, its dialog), not in a control of your own making. It runs here as one page in a browser: every choice that acts on the thing itself is kept, and the ones that act on the machine around it (quitting, sound, printing, help files) are left out. It is described whole: every part, every choice it offers and every convenience people know it to have belongs to it, whether or not the intent names it. The intent rules out only what it lists. What the product has never had is not added to it: no extra panel, no extra shortcut, no extra line of text. What it tells a person without words (by a colour, a mark, a count, a picture that changes) it does not say again in words.

### 3. How it is used
One line for each thing a person can do, at most 30 words: the gesture (click, right-click or long press, drag, type), the part it is done on, and what happens. Where a mouse and a finger do it differently, the line gives both. A product known by sight is used the way people know it to be, with the conveniences they expect of it.

Write sections 2 and 3 in the plain language of the people who use the product, never in the language of its code.

### 4. Scope
The one loop of use the pitch implies, done well: what a person does from start to finish, with the choices the product is known to offer on the way (how hard, how large, which view, which period). Left out is what the intent rules out, and nothing else is cut. Forms ask only for what the people in the loop need in order to act.

### 5. Things and their states
The things the loop needs, as many as it needs and no more. For each: what it holds, the states it moves through, and what moves it from one to the next.

### 6. Rules
- Every rule that governs the loop, one line each, with what happens when someone tries something that is not allowed (it is refused, or ignored, and nothing changes).
- When the product follows an established set of rules (the official rules of a game, a standard, a legal or trade convention), list every rule of that set by name, one line each, with its special cases and exceptions as lines of their own: each special case, each exemption, each convenience the people who know the product expect of it, and each way the thing can end (the ways the rules end it and the ways the people themselves end it, such as withdrawing or agreeing to stop). The product enforces exactly the rules listed here: a rule that is only implied by naming the rule set is not built.

## Form
- Markdown, with the six headings above, each present.
- Name the product as the pitch names it (or, where the pitch gives it no name, by the plain name of what it is), in the title and throughout, with nothing added to the name.
- No file names, folder layouts, component names, programming types or database schemas: the builders decide those.
- Sections 1, 4 and 5 are brief: under 250 words together. Sections 2, 3 and 6 are lists with as many lines as the product has parts, things to do and rules, and each line is short.
