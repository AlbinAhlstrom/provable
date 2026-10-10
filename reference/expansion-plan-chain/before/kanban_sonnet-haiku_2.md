### 1. Default Landing & Cold-Start Behavior

- No entity is marked "shown to audience"; the Board record fills the whole page, loaded from the API on arrival.
- Loading: the top bar shows no name yet; the board area shows three empty grey column shapes with no text.
- Load failure: the board area shows "The board could not load." with a "Try again" button beneath it.
- Opens directly on the board; no landing page, splash, or intro text.
- Board with no columns: the board area shows only "+ Add column" and one line: "Columns hold the stages of work. Add the first one."
- Member list empty: the assignee dropdown offers only "Unassigned" and a disabled line "No members yet."
- Empty column: shows only the "+ Add a card" button, no text.
- Top bar name: shows Board.name; if the record has no name, the bar shows nothing at left.
- Member records fill the top-bar picker and assignee dropdown; if they fail to load, show "Members could not load." in the dropdown.

### 2. Primary Navigation & View Structure

- One view only: the board. No tabs, no sidebar, no separate pages.
- Columns run left to right in ascending position, with "+ Add column" after the last column.
- The board area scrolls sideways when columns overflow; the top bar stays fixed.
- The card detail panel is an overlay on the board, opened by clicking a card, and closed by Close or outside click.
- Delete confirmations are dialogs over whichever surface opened them.
- The member picker at top right opens a small menu listing existing members under "Signed in as".
- No navigation between boards; one board per team.

### 3. Workflow Prerequisites & Form Ergonomics

- Adding a card needs no prerequisite; the "+ Add a card" button is always available in every column.
- Assignee dropdown is usable only once members exist; before that it shows "No members yet."
- Column dropdown in the panel lists all columns in order; no prerequisite.
- "Move left" is greyed out on the first column; "Move right" is greyed out on the last column.
- "Delete" in the column menu is greyed out when only one column exists.
- Title input: text input, label "Title", limited to 120 characters; extra typing ignored.
- Empty title submitted: box stays open, with message "A title is needed." beneath the field.
- Description: textarea, label "Description", no length limit stated.
- Assignee: select, label "Assignee"; options are "Unassigned" then existing members.
- Column: select, label "Column"; options are existing column names.
- Column name input: text input, label "Column name"; empty save reverts silently to the previous name.
- Failed save of a card or column: message "Changes could not be saved. Try again." beside the field.
- Card title and description save on focus loss; no save button.

### 4. Human Copy & Action Labeling

**Seen**

- Top bar: Board.name (no added label).
- Top bar member circle, menu heading: "Signed in as".
- Column header count pill: the card count as a number.
- Column menu items: "Rename", "Move left", "Move right", "Delete".
- Column add-card button: "+ Add a card".
- Add-card box: placeholder "Enter a title", buttons "Add" and "Cancel".
- Add-column button: "+ Add column"; box placeholder "Column name"; buttons "Add" and "Cancel".
- Empty board line: "Columns hold the stages of work. Add the first one."
- Empty-column: no text beyond the add button.
- Message on empty title: "A title is needed."
- Card panel: field labels "Title", "Description", "Assignee", "Column"; description placeholder "Add a description"; buttons "Delete" (red text), "Close".
- Card delete dialog: heading "Delete this card?", body "It will be removed from the board.", buttons "Delete" (red) and "Cancel" (grey).
- Column delete dialog with cards: heading "Delete this column?", body "Its {card count} cards will be deleted too." Without cards: heading only.
- Column delete dialog buttons: "Delete" (red) and "Cancel" (grey).
- Load failure: "The board could not load." with "Try again".
- Member load failure: "Members could not load."
- Empty members: "No members yet."
- Save failure: "Changes could not be saved. Try again."

**Spoken only**

- Column region: "Column {name}, {count} cards".
- Column menu button: "Column menu for {name}".
- Card: "Card {title}, assigned to {member name}" or "Card {title}, unassigned".
- Assignee circle: the member's name; empty circle: "Unassigned".
- Close icon in panel: "Close".
- Drag live region: "Moved {title} to position {n} in {column}".
- Top-bar circle: "Signed in as {name}".
- Drop indicator: "Drop position {n}".

### 5. Contextual Action Placement

- Add-card button: foot of each column, inside the column.
- Column rename: activated by clicking the column name in its header.
- Column menu (Rename, Move left, Move right, Delete): header right of each column.
- Add-column button: directly after the last column, on the board.
- Card detail panel: opened from the card it edits; Delete sits in the panel footer, left of Close.
- Card delete confirmation: over the panel, centred.
- Column delete confirmation: over the board, centred.
- Member picker: top bar, right, beside the signed-in circle.
- Assignee and Column selects: inside the card panel, beneath the title and description.
- Drag-and-drop acts on the card itself; no separate move control on the card.

### 6. Visual Direction

- **Feel**: a familiar Trello-style kanban board: pale blue-grey floor, grey column panels, white cards that lift off the page.
- **Palette**: page #E9EEF4; surfaces (top bar, cards, panel) #FFFFFF; columns #DDE3EA; primary text #1E293B; secondary text #64748B; accent and focus #2563EB; text on accent #FFFFFF; top-bar bottom line #CBD5E1; drop-target column #CBD5E1 with a #2563EB outline; danger text and button #DC2626; overlay #0F172A at 50% opacity; count pill background #FFFFFF with #64748B text; add-button hover fill #F1F5F9; assignee circles in join order: #3B82F6, #22C55E, #F97316, #A855F7, #14B8A6, #EF4444, with white initials; unassigned empty circle dashed #94A3B8.
- **Type**: sans throughout (system sans, Tailwind `font-sans`); column names 14px bold; card titles 14px medium; largest text on the first screen is Board.name at 18px semibold.
- **First screen**: a top bar of 56px with Board.name at left and the signed-in circle at right, below it the row of columns filling the rest of the viewport; no introduction above the board.
- **Form of the main view**: a Trello-style kanban board. Columns are fixed at 272px wide and fill the board-area height; cards fill the column width minus 16px padding and stack with 8px gaps; the column stack scrolls inside the column. An empty column holds only its add button. The "+ Add column" button is a 272px column-sized translucent white (#FFFFFF at 50%) panel. On a narrow screen the columns keep 272px and the board area scrolls sideways.
- **Shape and rhythm**: columns radius 12px; cards radius 8px with a small shadow, deepening on hover; assignee circles 24px, fully round; panel and dialogs radius 12px with a large shadow; 16px gap between columns; top bar 56px; comfortable density with 8px internal spacing.

LAYOUT columns=1 rows=auto

TOKENS background=#E9EEF4 surface=#FFFFFF text=#1E293B accent=#2563EB on_accent=#FFFFFF heading=sans