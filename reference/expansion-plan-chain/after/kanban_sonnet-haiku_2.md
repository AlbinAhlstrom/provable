### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience"; Board and TeamMember are created by the team, so no business records load.
- While the board loads, the top bar shows "Loading board" and grey placeholder columns fill the board area.
- If the board fails to load, show "The board could not be loaded." with a "Try again" button.
- A board with no columns opens with the add-column form already open, name field focused.
- The add-column form shows "Add a column to start the board." beside its name field.
- An empty column shows its header with count "0" and the "+ Add a card" control only.
- The top bar shows Board.name in white bold text and nothing else.
- With no teammates yet, the card dialog's member list shows "No teammates on this board yet."

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, separate pages, menus of other areas or consoles.
- Card dialog: centred overlay opened by clicking a card; the board stays visible behind it.
- Column menu: popover opened from the "⋯" control in the column header, holding "Delete column".
- Top bar stays fixed; the board area scrolls sideways when columns overflow the window.
- Every change applies immediately; no save or submit control exists for the board as a whole.

### 3. Workflow Prerequisites & Form Ergonomics
- Add-card form: single text input, label "Card title", Add button always enabled; empty submit keeps the form open.
- Empty card title refused with inline message "Enter a title to add the card." beneath the input.
- Column rename input is prefilled with the current name; an empty rename restores the old name without a message.
- Add-column form: text input labelled "Column name"; empty submit shows "Enter a column name." and stays open.
- Column name input refuses more than 50 characters by ignoring extra typing; no counter shown.
- Card title input in the dialog ignores characters beyond 200; no counter shown.
- Description: optional textarea labelled "Description"; saves when focus leaves; empty is valid.
- "Delete column" in a one-column board is shown disabled, with "A board needs at least one column." beside it.
- Dragging a card outside any column returns it silently to its original place; no message.
- Assigning an already assigned member toggles it off, so no duplicate state is ever shown.

### 4. Human Copy & Action Labeling
**Seen**
- Top bar: Board.name (board name, white bold).
- Loading: "Loading board" (top bar, while loading).
- Load failure: "The board could not be loaded." and "Try again" button (board area).
- Add-column hint: "Add a column to start the board." (first-visit form).
- Column count: number in grey beside column name (column header).
- Add-card control: "+ Add a card" (column bottom).
- Add-card form: label "Card title"; "Add" button; "×" close (add-card form).
- Add-card error: "Enter a title to add the card." (add-card form).
- Add-column control: "+ Add another column" (after last column).
- Add-column form: label "Column name"; "Add" button; "×" close.
- Add-column error: "Enter a column name." (add-column form).
- Column menu item: "Delete column" (column menu).
- Disabled-delete reason: "A board needs at least one column." (column menu).
- Card dialog title field: label "Title" (card dialog).
- Description label: "Description"; placeholder "Add a description" (card dialog).
- Member list heading: "Members" (card dialog).
- Empty member list: "No teammates on this board yet." (card dialog).
- Delete button: "Delete" in red (card dialog).
- Card delete confirmation: "Delete this card? It cannot be undone." with "Delete" and "Cancel".
- Column delete confirmation with cards: "Delete this column and its {count} cards?" (confirmation).
- Column delete confirmation, empty: "Delete this column?" (confirmation).
- Confirmation buttons: "Delete" and "Cancel" (both confirmations).

**Spoken only**
- Card: "{title}, assigned to {names}" or "{title}, no assignees" (each card).
- Assignee badge: "{member name}" (each badge).
- Member row in dialog: "{name}, assigned" or "{name}, not assigned" (member list).
- Close controls: "Close" (×, dialog and forms).
- Column menu trigger: "Column menu for {column name}" ("⋯").
- Drop placeholder: "Drop position" (grey placeholder).
- Column count: "{count} cards" (header count).
- Overlay: "Close dialog" (dialog overlay).

### 5. Contextual Action Placement
- Column rename: click the column name in its header; the name becomes the input in place.
- Column delete: "⋯" in the column header opens the menu holding "Delete column".
- Add a card: "+ Add a card" sits at the bottom of each column, under its last card.
- Add a column: "+ Add another column" sits at the right end, after the last column.
- Card title, description, members and "Delete": all inside the card dialog, on the card's own panel.
- Delete card: "Delete" sits at the foot of the card dialog, away from the title field.
- Confirmations appear over the item they affect, beside its Delete or Cancel choice.

### 6. Visual Direction
- **Feel**: a familiar Trello-style team board: a bright blue wall of grey columns holding white cards.
- **Palette**: page background #0079BF; top bar #026AA7; column surface #EBECF0; column drag-over #DFE1E6; card #FFFFFF; card hover #F4F5F7; text #172B4D; muted text #5E6C84; accent (Add buttons) #5AAC44 with white text; delete button #C9372C with white text; placeholder #C1C7D0; dialog overlay #091E42 at 54% opacity; add-column panel white at 24% opacity; badge colours #EB5A46, #FF9F1A, #61BD4F, #C377E0, #00C2E0, #FF78CB, with initials #172B4D on orange and sky, white on the rest.
- **Type**: `font-sans` throughout; column names 14px bold #172B4D; card titles 14px regular; board name 18px bold; badge initials 12px bold.
- **First screen**: a 48px top bar at the top edge, then the board area filling the rest of the window edge to edge. The first column's add-column form sits 16px in from the top-left of the board area, with nothing else above it.
- **Form of the main view**: a horizontal row of kanban columns, each 272px wide and all alike, stacked cards inside. Columns run to the window height and the row scrolls sideways when wider than the window. An empty column shows its header and "+ Add a card" only. On a narrow window, columns keep 272px and the board scrolls sideways; nothing reflows or stacks.
- **Shape and rhythm**: columns 12px radius, light shadow `0 1px 2px rgba(9,30,66,0.25)`, 8px inner padding; cards 8px radius, 1px bottom shadow `0 1px 0 rgba(9,30,66,0.25)`, 12px padding, 8px gap between cards; 16px gap between columns; badges 32px circles, 4px apart; dialog 8px radius, 24px padding, max width 576px. Dense but calm, with no decorative elements.

LAYOUT columns=1 rows=auto

TOKENS background=#0079bf surface=#ebecf0 text=#172b4d accent=#5aac44 on_accent=#ffffff heading=sans