### 1. Default Landing & Cold-Start Behavior

- No entity is marked "shown to audience"; the board's member list feeds the top-bar chips and the assignee picker.
- The board opens directly, with no splash or intro text, in its only view.
- Loading: the board area shows "Loading board…" in grey text, centred in the column row.
- Load failure: the column row shows "The board could not be loaded." with a "Try again" button beneath it.
- Empty board (no columns): the row holds only the "+ Add column" lane, which opens the name box at once.
- Empty column: a faint dashed outline (2px, `#94A3B8`) with no text, beside the "Add card" button at its foot.
- No team members: the assignee picker lists only "Unassigned" and one line reads "No team members on this board yet."
- Top bar with no members: the chip area is empty; no chips or text appear.

### 2. Primary Navigation & View Structure

- One view only: the board. No tabs, no menu, no second page.
- Top bar, left to right: board name, then member chips at the right end.
- Column row sits below the top bar and scrolls sideways when columns overflow.
- Column order runs left to right, with "+ Add column" as the last lane.
- Card dialog is an overlay over the board, opened by clicking a card.
- Delete card and delete column confirmations are small overlays over the board.
- Member filter is the chip set in the top bar; it lives on the board and needs no separate page.

### 3. Workflow Prerequisites & Form Ergonomics

- "Add card" needs a column; it appears only in columns, so no prerequisite line is needed.
- Empty card title: the Add button stays pressable; submitting shows "A card needs a title." beneath the field and creates nothing.
- Title field holds at most 120 characters; typing past that is ignored with no message.
- Card title field in the dialog: text input labelled "Title"; empty on blur shows "A card needs a title." and restores the previous title.
- Description: textarea labelled "Description"; saves on blur with no validation message.
- Assignee picker: a select labelled "Assignee", listing "Unassigned" first, then each member by name.
- Assignment to a non-member is refused silently; the picker only offers members, so no message appears.
- Column name: text input labelled by its position; empty or duplicate name shows "A column needs a unique name." beneath it and keeps the old name.
- Deleting a column with cards: the confirmation shows "Move or delete the cards in this column first." and only "Cancel" is offered.
- Deleting the last column: the menu item "Delete column" shows "A board needs at least one column." in place of the confirmation.
- Member filter pressed with no cards: chips still work; no message appears.
- Drop outside any column: the card snaps back to its original spot with no message.

### 4. Human Copy & Action Labeling

**Seen:**
- Top bar: board name, default "Team board", at the left of the bar.
- Column header: column name, then card count as a number beside it.
- Column header menu button: "⋯" with accessible name in Spoken only.
- Column menu item: "Delete column".
- Column row end lane: "+ Add column".
- Column name box: placeholder "Column name"; buttons "Add" and "Cancel".
- Card foot button: "Add card"; open state: text box placeholder "Enter a title for this card", buttons "Add" and "Cancel".
- Card dialog heading: the card title, shown in the Title field.
- Card dialog fields: "Title", "Description", "Assignee".
- Card dialog buttons: "Delete" (red text, left), "Close" (right).
- Card dialog assignee option: "Unassigned".
- Card delete confirmation: heading "Delete this card?", buttons "Delete" (red) and "Cancel" (grey).
- Column delete confirmation: heading "Delete column "[name]"?", buttons "Delete" (red) and "Cancel" (grey).
- Column delete refused: "Move or delete the cards in this column first."
- Last column refused: "A board needs at least one column."
- Column name refused: "A column needs a unique name."
- Card title refused: "A card needs a title."
- Load: "Loading board…", "The board could not be loaded.", "Try again".
- Empty board: "Add a column to start your board." beside "+ Add column".
- No members: "No team members on this board yet."

**Spoken only:**
- Member chip: "[Name]. Show only their cards." when inactive; "[Name]. Clear filter." when active.
- Unassigned card dashed circle: "Unassigned".
- Column menu button: "Column options for [name]".
- Card: "[Title], [column name], assigned to [name]" or "unassigned".
- Column drag handle: "Move column [name]".
- Backdrop of dialog: "Close card".

### 5. Contextual Action Placement

- "Add card" sits at the foot of each column, under the last card.
- The card add box opens in place of the "Add card" button, inside the same column.
- Column options "⋯" sit at the right of each column header.
- "Delete column" lives only in the column menu, not on the board surface.
- "+ Add column" sits in the lane at the far right end of the row.
- Column title is clicked in place to edit; Enter saves it there.
- Member chips sit in the top bar at the right; clicking one filters cards on the board below.
- Card delete sits in the card dialog, bottom left, away from Close.
- Card dialog Close sits bottom right, with the backdrop and Escape as alternatives.
- Assignee picker sits in the card dialog beneath the description.

### 6. Visual Direction

- **Feel**: A familiar Trello-style kanban board: pale blue-grey page, navy top bar, grey lanes, white cards, calm and dense.
- **Palette**: Page background `#E8EDF2`; top bar and text `#172B4D`; surface (cards, dialog) `#FFFFFF`; column lane `#DDE2E8`; accent `#1D4ED8` for "Add" buttons and the active focus ring; on-accent `#FFFFFF`. Drop-target column `#BFDBFE`; card hover shadow `rgba(23,43,77,0.25)`; column menu hover `#CBD2DB`; delete red `#DC2626`; cancel grey text `#5E6C84`; unassigned circle and drop gap dashed `#94A3B8`; add-column lane `rgba(255,255,255,0.5)`. Member chips: blue `#2563EB`, green `#16A34A`, orange `#EA580C`, purple `#9333EA`, teal `#0D9488`, red `#DC2626`, initials white.
- **Type**: `font-sans` for everything. Board name 18px semibold; column titles 14px semibold; card titles 14px regular; counts and meta 12px regular.
- **First screen**: The board itself fills the window: navy top bar with board name and chips, then the column row starting at 16px from the left edge. On an empty board, only the "+ Add column" lane and its line of guidance show. No text sits above the board.
- **Form of the main view**: A Trello-style horizontal row of lanes. Each lane is 272px wide, fixed, with 8px gaps, lanes as tall as the row. Cards are full lane width minus 16px, each as tall as its content, 8px apart. Empty lanes show the dashed outline. Row scrolls sideways when lanes overflow; below 640px wide the row keeps lane widths and scrolls, and the top-bar chips wrap to a second line.
- **Shape and rhythm**: Lanes 12px radius; cards 6px radius with `0 1px 2px rgba(23,43,77,0.2)` shadow, rising to `0 4px 10px rgba(23,43,77,0.25)` on hover and while dragged, tilted 2 degrees; chips fully round, 28px diameter; dialog 8px radius with `0 8px 24px rgba(23,43,77,0.3)` shadow; padding 8px in lanes and cards, 16px around the dialog body; sections spaced 12px; dense, Trello-like.

LAYOUT columns=1 rows=1
TOKENS background=#E8EDF2 surface=#FFFFFF text=#172B4D accent=#1D4ED8 on_accent=#FFFFFF heading=sans