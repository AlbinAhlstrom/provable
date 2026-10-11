### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience"; Board and Card are created by the team, so no records need a loading or empty note.
- The board opens directly on the team's single board, with no sign-in or landing page.
- Top bar shows `Board.name` in white at left and the team member selector at right.
- Board loading: centre text "Loading board…" in grey, replacing the board area.
- Board load failure: centre text "The board could not be loaded." with a button "Try again".
- A board with no columns shows only the "+ Add column" panel, with the line "Add a column for each stage of the work." above it.
- Column with no cards shows only the "+ Add card" control; no extra text.
- Team member selector with no members shows the single line "No team members yet" in its menu.

### 2. Primary Navigation & View Structure
- The product has one view: the board, shown on every visit.
- No tabs, menus or pages beyond the board, the card dialog and confirmation prompts.
- Columns run left to right in `Column.position` order, with equal 16px gaps.
- Board area scrolls sideways when columns overflow; the top bar stays fixed.
- Card dialog opens over the board and returns to the same scroll position when closed.
- Team member selector at top right opens a menu listing `TeamMember.name` with initials; it shows the current member.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column first, so "+ Add card" appears only on existing columns.
- Assigning needs a team member: when none exist, the assignee menu shows "Unassigned" and the line "No team members on this board yet."
- Card title field: text input, label "Title", required; empty submit shows the message "Enter a title." with a red outline.
- Description: textarea, label "Description", optional, may save empty.
- Assignee: select, label "Assignee", options are "Unassigned" then each team member name.
- Column name field: text input, required; empty submit shows "Enter a column name." with a red outline.
- Inline add-card and add-column fields save on Enter and cancel on Escape; both cancel on blur when empty.
- Card title and description save on blur; the dialog shows no save button.
- Drag refused outside every column: the card returns to its original spot without a message.
- Deleting an already-removed card or column does nothing and shows no message.

### 4. Human Copy & Action Labeling
**Seen:**
- "Board" top bar: `Board.name` (white).
- "+ Add card" (button, bottom of each column).
- "Card title" (placeholder in add-card field).
- "+ Add column" (button, after last column).
- "Column name" (placeholder in add-column field).
- "Add a column for each stage of the work." (empty board guidance).
- "Enter a title." and "Enter a column name." (validation messages).
- Card dialog labels: "Title", "Description", "Assignee".
- "Unassigned" (assignee option and state).
- "No team members on this board yet." (assignee menu).
- "Delete" (red text, card dialog); "Close" (card dialog).
- Card delete confirmation: heading "Delete this card?", buttons "Delete card" and "Cancel".
- Column delete confirmation: heading "Delete this column?", line "Its cards will be deleted too.", buttons "Delete column" and "Cancel".
- Column menu item: "Delete column".
- "Loading board…", "The board could not be loaded.", "Try again", "No team members yet".

**Spoken only:**
- Column header count badge: "N cards".
- Assignee circle: "Assigned to [name]" or "Unassigned".
- Column options control (menu icon): "Column options".
- Team member selector: "Team member".
- Card: "[title], [column name], assigned to [name]" or "unassigned".
- Column name in rename mode: "Rename column".
- Drop target while dragging: "Drop card in [column name]".

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its column, under the cards.
- "Column options" icon sits at the right of the column header, opening "Delete column".
- Column name is renamed in place by clicking it, next to the header badge.
- "+ Add column" sits after the last column, at the board's right edge.
- Card Delete sits in the card dialog's footer, left of Close.
- Card assignee control sits in the card dialog, under the description field.
- Team member selector sits in the top bar at right, not in the board.
- Confirmation prompts appear centred over the dimmed board, not beside the item.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: light grey surface, tall columns, white cards with soft shadows.
- **Palette**: page background #F1F2F4; column surface #E2E4E8; card surface #FFFFFF; text #1B2433; top bar #1F2A44; accent #2563EB for focus outlines and primary buttons; drop highlight #D6E4FF; error #DC2626; assignee empty circle border #9CA3AF; badge background #CBD0D8 with text #1B2433.
- **Type**: `font-sans` for everything; column names `font-bold` at 15px; card titles 14px regular; board name 18px bold in the top bar.
- **First screen**: top bar with board name and team member selector, then the columns (or the single "+ Add column" panel on an empty board) filling the board area. No text above the board.
- **Form of the main view**: a horizontal row of columns, each a fixed 272px-wide panel with 8px gaps between cards and 12px internal padding; columns grow in height with their cards. Cards are full column width, 64px minimum height, sized to their content. Below 768px width, the board keeps the same column width and scrolls sideways; no reflow into a stack.
- **Shape and rhythm**: columns and cards have 8px corner radius; cards carry a soft shadow (`shadow-sm`, deepening to `shadow-md` on hover); columns have no shadow. Spacing 12px between cards and 16px between columns. Density is comfortable, not compact.

LAYOUT columns=1 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#1B2433 accent=#2563EB on_accent=#FFFFFF heading=sans