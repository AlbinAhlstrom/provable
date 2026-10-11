### 1. Default Landing & Cold-Start Behavior

- The board opens as the only view, filling the browser window below the top bar.
- No entity is marked "shown to audience", so no record-loaded part is planned. The page writes no starting records.
- While the board loads, the column area shows the page backdrop only, with no placeholder text.
- If the board fails to load, the column area shows "The board could not load." and "Try again" beneath it.
- With no columns, the board shows one tile, "+ Add another column", and the line "Columns show the stages of your work. Add the first one."
- Empty column: no cards, and the line "Cards for this stage appear here." sits above "+ Add a card".
- Empty member list in the card dialog: "No members on this team yet." replaces the checkbox list.
- Top bar shows the board name "Team board" and the signed-in member's initials circle.

### 2. Primary Navigation & View Structure

- One view only: the team board. There is no navigation menu, tab bar or secondary page.
- Columns sit left to right in position order, each 272px wide, and scroll sideways when they overflow.
- Add-column tile sits after the last column, always visible at the right end of the row.
- Card dialog opens over the board; closing it returns to the same scroll position.
- Column "⋯" menu opens a small menu anchored to the column header, holding "Delete column" only.
- Delete confirmations open as small centred dialogs over the dimmed board.

### 3. Workflow Prerequisites & Form Ergonomics

- A card needs a column: "+ Add a card" appears only in columns, so no column means no card control.
- Adding the first column comes first on an empty board; the add-column tile is the only control shown there.
- Assigning needs a member: the assignee list is shown in the dialog; with no members it shows its empty line instead.
- Card title field: text input, label "Title", required; refusal line "A card needs a title." under the box.
- Title over 120 characters: refusal line "Use 120 characters or fewer." under the box; the text is kept.
- Column name field: text input, label "Column name"; empty refusal "A column needs a name."; over 40 characters "Use 40 characters or fewer."
- Description field: textarea, label "Description", up to 5,000 characters; over-limit refusal "Use 5,000 characters or fewer."
- Refused description keeps the previous saved text in the field's stored value; the field shows the refusal line.
- Column delete with no cards: removes the column at once, no confirmation.
- Last column delete: the menu item stays and does nothing when chosen.
- Member assignment is refused for an inactive member with the line "This member is no longer on the team."

### 4. Human Copy & Action Labeling

**Seen**

- "Team board" — top bar, board name.
- "+ Add a card" — bottom of each column.
- "Enter a title for this card" — placeholder in the add-card box.
- "Add" — button in the add-card box and add-column box.
- "×" — close button in add boxes and the card dialog.
- "+ Add another column" — add-column tile.
- "Enter column name" — placeholder in the add-column box.
- "Title" — label, card dialog.
- "Description" — label, card dialog.
- "Add a more detailed description" — placeholder, empty description.
- "Assignees" — label above the member checkbox list.
- "Column" — label, card dialog column name selector.
- "Delete card" — red text link in the card dialog.
- "Delete this card? This cannot be undone." — delete card confirmation.
- "Delete" — red button in every delete confirmation.
- "Cancel" — grey button in every delete confirmation.
- "Delete column" — item in the column menu.
- "Delete this column?" — column delete confirmation heading.
- "This column and its 3 cards will be deleted. This cannot be undone." — shown when the column holds cards; the count is the number of cards.
- "A card needs a title." — refusal line.
- "Use 120 characters or fewer." — refusal line.
- "A column needs a name." — refusal line.
- "Use 40 characters or fewer." — refusal line.
- "Use 5,000 characters or fewer." — refusal line.
- "This member is no longer on the team." — refusal line.
- "The board could not load." and "Try again" — load failure.
- "Cards for this stage appear here." — empty column.
- "Columns show the stages of your work. Add the first one." — empty board.
- "No members on this team yet." — empty assignee list.

**Spoken only**

- "Your account, initials [name]" — signed-in member's initials circle.
- "Close" — the "×" buttons.
- "Column menu" — the "⋯" button.
- "Member: [name]" — each assignee chip on a card.
- "Unassigned" — dashed unassigned mark.
- "[n] cards" — column card count beside the title.
- "Drag card" — announced on a card while it is grabbed.
- "Drag column" — announced on a column header while it is grabbed.

### 5. Contextual Action Placement

- "+ Add a card" sits at the bottom of its column, under the last card.
- "Add" and "×" for a card sit in the add box at the column bottom.
- Column rename happens on the column title in its header; no separate rename control.
- "⋯" menu sits at the right of each column header.
- "Delete column" sits in that column's menu.
- Card title, description, assignees and column selector sit in the card dialog for that card.
- "Delete card" sits at the foot of the card dialog, away from the save-on-blur fields.
- Delete confirmations sit centred over the dimmed board, beside their own Cancel button.
- Add-column tile sits at the right end of the column row, the only action on that side.
- Refusal lines sit directly under the box that caused them, in red.

### 6. Visual Direction

- **Feel**: the familiar Trello-style kanban board: flat blue field, grey columns, white cards, quiet and dense.
- **Palette**: page background #0079bf; top bar #026aa7; column surface #ebecf0; column hover-drop #dfe1e6; placeholder #c1c7d0; card white #ffffff; text #172b4d; accent #0079bf for the Add button; delete red #eb5a46; cancel grey #dfe1e6 with text #172b4d; dim layer rgba(0,0,0,0.5); member colours red #eb5a46, orange #ff9f1a, green #61bd4f, purple #c377e0, teal #00c2e0, pink #ff78cb.
- **Type**: sans (system-ui, Helvetica, Arial); column titles 14px bold; card titles 14px regular; top bar board name 18px bold, the largest text on the first screen.
- **First screen**: the board fills the window edge to edge below a 40px top bar; columns start at the top-left with 12px margin; nothing sits above or around the board.
- **Form of the main view**: a horizontal row of columns; each column is 272px wide, 8px gap between columns, column padding 8px; cards 40px minimum height; a column with no cards holds only its header and the add control; the board is not fixed-width, so columns stack in a single row and scroll sideways on narrow screens.
- **Shape and rhythm**: column radius 12px, card radius 8px, card shadow 0 1px 0 rgba(9,30,66,0.25); hover shadow 0 4px 8px rgba(9,30,66,0.25); dragged card rotates 3deg with shadow 0 8px 16px rgba(9,30,66,0.3); assignee chips 32px circles at card bottom right; 8px spacing between cards; dense, with 12px between the top bar and columns.

LAYOUT columns=1 rows=auto

TOKENS background=#0079bf surface=#ebecf0 text=#172b4d accent=#0079bf on_accent=#ffffff heading=sans