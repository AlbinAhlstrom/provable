### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience"; Board and Card are created by the team, so no records load from outside.
- The page opens on the team's one board, showing `Board.name` in the top bar.
- A new board has no columns, so the only thing shown is the "+ Add column" panel.
- Show "Add a column to start the board." beside the "+ Add column" panel when the board has no columns.
- A column with no cards shows only the "+ Add card" control; no other text.
- If the board fails to load, show "The board could not load. Try again." with a "Try again" button.
- While the board loads, show the top bar and grey page with no columns and no spinner.

### 2. Primary Navigation & View Structure
- One view only: the board. There are no tabs, menus or pages besides the card dialog.
- Top bar, left to right: `Board.name` in white, then the team member selector at right.
- The team member selector shows the acting member's initials circle and name; choosing a name sets who is acting.
- Card dialog opens as a centred overlay over the board; it is the only other surface.
- Column menu (a "⋯" button at the column header's right) holds one item: "Delete column".
- Board area scrolls sideways when columns overflow; the top bar stays fixed while scrolling.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column; "+ Add card" is shown only inside existing columns, so no prerequisite line is needed.
- Adding a column needs only a name; the add-column panel opens an inline text field immediately on click.
- The assignee dropdown lists only team members, followed by "Unassigned" as the first option.
- Card title field: label "Title", required; placeholder "Card title"; error message "Enter a title." beside the field.
- Card description: label "Description", textarea, may be empty; no error message.
- Assignee dropdown: label "Assignee"; options are team members by name, plus "Unassigned".
- Column name field: placeholder "Column name"; error message "Enter a column name." beside the field.
- A refused empty title keeps the field open with a red outline and the message; the card is not created.
- Pressing Escape in the add-card or add-column field closes it and creates nothing.
- Clicking the Delete control in the card dialog asks for confirmation before anything is removed.
- A drop outside every column returns the card silently to its original place; no message is shown.

### 4. Human Copy & Action Labeling
**Seen:**
- "+ Add card" — bottom of each column, grey text button.
- "+ Add column" — translucent panel after the last column.
- "Card title" — placeholder in the add-card field.
- "Column name" — placeholder in the add-column and rename fields.
- "Title", "Description", "Assignee" — labels in the card dialog.
- "Unassigned" — first option in the assignee dropdown.
- "Delete" — red text in the card dialog.
- "Close" — button in the card dialog.
- "Delete this card?" — confirmation text; buttons "Delete" and "Cancel".
- "Delete column and its N cards?" — confirmation text; buttons "Delete" and "Cancel".
- "Delete column" — item in the column menu.
- "Enter a title." — error beside the title field.
- "Enter a column name." — error beside the column name field.
- "Add a column to start the board." — empty-board line beside "+ Add column".
- "The board could not load. Try again." and "Try again" — load error.
- "Acting as" — label above the team member selector.

**Spoken only:**
- Column card-count badge: "N cards".
- Assignee circle: the member's full name, or "Unassigned".
- Column menu button: "Column options".
- Card element: its title and assignee name.
- Team member selector: "Acting as, [name]".
- Dialog backdrop: none; the overlay is announced as "Card dialog".

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its own column.
- The card count badge sits beside the column name in its header.
- Renaming happens by clicking the column name in its header, in place.
- "Delete column" sits in the column's "⋯" menu in its header.
- Column reorder happens by dragging the column header.
- Card edits, assignment and Delete sit in the card dialog opened from the card.
- Card moves happen by dragging the card itself; no move control exists.
- Confirmation for card or column deletion appears over the item's own surface, not on a separate page.

### 6. Visual Direction
- **Feel:** a Trello-style kanban board: light grey page, tall columns, white cards, calm and dense.
- **Palette:** page `#F1F2F4`; surface (cards and dialog) `#FFFFFF`; column `#E2E4E8`; top bar `#1F2A44`; text `#172033`; secondary text `#5B6475`; accent (focus outline and links) `#1F6FEB`; error and Delete `#D92D20`; drop-target column `#D6E4FF`; dashed outline `#9AA1AD`; badge `#CDD1D8` with text `#1F2A44`; add-card hover `#D0D3D9`; add-column panel `rgba(255,255,255,0.5)`; dialog backdrop `rgba(15,20,35,0.5)`; unassigned circle border `#9AA1AD`.
- **Type:** `font-sans` for everything. Board name is 20px semibold on the top bar; column names 14px bold; card titles 14px regular; labels 12px medium.
- **First screen:** the top bar with the board name, then the board area with its columns (or the add-column panel on a new board), ready to use. Nothing is written above it.
- **Form of the main view:** a Trello-style board. Columns are 272px wide, 12px apart, full available height, scrolling sideways. Cards are full column width, 8px apart. Each card is 8px radius; each column is 12px radius with 8px inner padding. An empty column is the same width with only "+ Add card". On narrow screens the board keeps column widths and scrolls sideways.
- **Shape and rhythm:** columns have no border; cards have a shadow `0 1px 2px rgba(31,42,68,0.15)`, deepening on hover to `0 4px 8px rgba(31,42,68,0.2)`. Card padding is 8px 10px. Top bar is 48px tall. Assignee circles are 24px. Dashed outlines are 2px. Dense, with 12px between sections of the board.

LAYOUT columns=1 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#172033 accent=#1F6FEB on_accent=#FFFFFF heading=sans