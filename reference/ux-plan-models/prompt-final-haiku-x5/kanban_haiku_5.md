### 1. Default Landing & Cold-Start Behavior
- The page opens directly on the team's single board; no landing page, no login screen, no welcome text.
- The board is the active and only view on arrival; it is never shown empty of structure.
- Board name shown in the top bar at left, as "Team board" until the name is set (board name is not editable in scope, so it is fixed).
- Columns load from `Board.columns` ordered by `Column.position`; cards load from `Card.position` within each `Card.column_id`.
- Team member selector at top-right lists `Board.team_members`, showing each `TeamMember.initials` on `TeamMember.colour`.
- Loading state: columns appear as grey panels with grey placeholder bars where headers and cards will sit; no spinner text.
- Load failure: a single line in the board area reading "The board could not be loaded." with a button "Try again".
- Empty board (no columns): board area shows one line "Add a column to start the board." beside the "+ Add column" panel.
- Empty column: shows only the "+ Add card" control, per specification; no extra text.
- Empty team member list: the selector reads "No team members" and the assignee dropdown shows only "Unassigned".

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, no menus beyond the column menu and the card dialog.
- Top bar holds the board name (left) and team member selector (right); nothing else.
- Board area scrolls sideways when columns overflow; the top bar stays fixed.
- Card dialog opens as a modal over the board, closed by "Close" or Escape.
- Column menu (a "⋯" button in the column header, shown on hover and focus) offers one item: "Delete column".
- Column delete confirmation is a small modal over the backdrop with "Delete column" (red) and "Cancel".
- Card delete confirmation is a small modal with "Delete card" (red) and "Cancel".
- Team member selector opens a small list of members with initials and names; selecting one sets the viewing member for nothing else (no filtering in scope), so it shows the member's name only and changes no data.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column; "+ Add card" is shown only in existing columns, so no prerequisite is hidden.
- Card title is required: the title input is focused on open; Enter with empty title keeps the input open and outlines it red.
- Card title input: text input, label "Card title" (visually shown as placeholder "Card title"), error message none beyond the red outline.
- Card description: textarea, label "Description", may be empty; saves on blur.
- Assignee: select control, label "Assignee", options "Unassigned" then each team member name; a non-member is never listed.
- Column name input: text input, label "Column name", empty name refused; the name field keeps its old value and outlines red.
- Column rename: Enter saves when non-empty; blur with empty name restores the previous name with no message.
- Escape in any add or rename field cancels and restores the prior state.
- Dropping outside every column returns the card silently to its original place; no message.
- Delete actions show a confirmation first; cancelling leaves the item unchanged.
- Board never offers an action that would be refused: the delete and add controls are always enabled.

### 4. Human Copy & Action Labeling
**Seen**
- "Team board" — top bar board name.
- "No team members" — team member selector when empty.
- "+ Add card" — add card control at column bottom.
- "+ Add column" — add column panel after last column.
- "Card title" — placeholder of card title field.
- "Description" — label of description textarea.
- "Assignee" — label of assignee dropdown.
- "Unassigned" — first assignee option and clears assignee.
- "Close" — card dialog button.
- "Delete" — red text in card dialog.
- "Delete card?" — heading of card delete confirmation; buttons "Delete card" and "Cancel".
- "Delete column?" — heading of column delete confirmation; body "Its cards will be removed too."; buttons "Delete column" and "Cancel".
- "Column name" — placeholder of column name field.
- "The board could not be loaded." — load failure message.
- "Try again" — load failure button.
- "Add a column to start the board." — empty board line.

**Spoken only**
- "Card: [title], assigned to [member name]" or "Card: [title], unassigned" — card button name.
- "Column: [name], [N] cards" — column region name.
- "Assignee circle" — badge with initials; the initials are read as the member name.
- "Options" — column menu button.
- "Team member selector" — selector button.
- "Drag handle" — column header during drag.

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of each column, inside the column panel.
- Card title input for new cards opens in place at the column bottom, replacing the "+ Add card" control.
- "+ Add column" sits as a panel after the last column on the board area.
- Column rename happens in place on the column name in the header.
- Column delete sits in the column header's "⋯" menu, beside the column it removes.
- Card edit, assignee, and delete sit inside the card dialog, the one place the card is changed.
- Assignee circle on each card shows state; the dropdown is reached only through the dialog.
- Card delete confirmation appears over the dialog that holds the Delete button.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: calm, light and flat, with white cards on grey columns.
- **Palette**: page background #F1F2F4; top bar and accent #1F2A44 (navy); column surface #E2E4E8; card surface #FFFFFF; text #1F2A44; secondary text #6B7280; drop target #D6E4FF; error #DC2626; assignee circle fallback grey #9CA3AF; empty assignee dashed outline #9CA3AF; column count badge #CBD0D8; hover column button #D1D5DB; focus/edit outline #2563EB; translucent add column panel rgba(255,255,255,0.35).
- **Type**: sans throughout (`font-sans`); column names bold 14px; card titles regular 14px; board name white 16px semibold.
- **First screen**: the top bar with the board name and member selector, then the board: columns side by side with their cards, ready to use. Nothing is written above the board.
- **Form of the main view**: a horizontal row of vertical columns, as on Trello. Columns are fixed at 272px wide, 8px gap, each as tall as the board area and scrolling internally when cards overflow. Cards are full column width minus 16px padding, each sized to its content (auto height). An empty column shows only its "+ Add card" control. On narrower screens the board keeps the 272px columns and scrolls sideways; nothing reflows into a grid.
- **Shape and rhythm**: column corner radius 12px, card corner radius 8px, card shadow `0 1px 2px rgba(0,0,0,0.15)` deepening to `0 3px 8px rgba(0,0,0,0.2)` on hover; 8px between cards, 8px inside column padding, 16px between columns; dense but airy.

LAYOUT columns=3 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#1F2A44 on_accent=#FFFFFF heading=sans