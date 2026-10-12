### 1. Default Landing & Cold-Start Behavior
- Opening the app shows the team's single board directly, with its columns and cards visible; no splash, no login gate.
- Board name appears in the top bar at left; the team member selector sits at right.
- Board.name loads into the top bar; while loading, a grey bar pulses where the name sits.
- Load failure: a centred line "Could not load the board." with a "Try again" button beneath it.
- A new board has no columns: the board area shows one line "Add a column to start the board." beside the "+ Add column" panel.
- Empty column (Board.columns with no cards): shows only the "+ Add card" control; no placeholder text.
- Team members loaded from Board.team_members into the selector; while loading, the selector shows "Loading members…".
- No team members yet: the selector reads "No members" and the assignee dropdown shows only "Unassigned".
- Card count badge in each column header shows the number of cards held (Card.column_id).

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, no menus beyond the top bar, the column menu and the card dialog.
- Top bar holds the board name (left) and the team member selector (right); selector opens a list of Board.team_members to pick the acting member.
- Board area scrolls sideways when columns overflow; the top bar stays fixed.
- Card dialog opens over the board from a card click and closes with "Close" or Escape.
- Column menu (a "⋯" icon at the header's right) holds one item: "Delete column".
- Keyboard: Tab moves between cards and controls in reading order; Enter opens a focused card.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card: the title field appears only after "+ Add card" is clicked; no field is shown beforehand.
- Adding a column: the name field appears only after "+ Add column" is clicked.
- Title field is a text input labelled "Card title"; empty submit refused, field outlined red with the message "Enter a title."
- Column name field is a text input labelled "Column name"; empty submit refused, outlined red with "Enter a column name."
- Description is a textarea labelled "Description"; may be empty.
- Assignee is a dropdown labelled "Assignee", listing "Unassigned" then each Board.team_members name.
- Renaming a column: clicking the name turns it into an input; Enter saves, empty name refused with the same red outline and message.
- Drag rule: a card cannot be dropped outside a column; it returns to its original place with no message.
- Deleting a column or card: confirmation dialog must be answered before anything is removed; Cancel changes nothing.
- Delete action for a card is available only in the open card dialog, not on the board.

### 4. Human Copy & Action Labeling
**Seen:**
- "Board" name from Board.name in the top bar.
- "+ Add card" at each column bottom.
- "Card title" label and placeholder "Enter a card title" in the add-card field.
- "Enter a title." error below the card title field, shown in red.
- "+ Add column" in the translucent panel after the last column.
- "Column name" label; "Enter a column name." error text.
- Card dialog: heading is Card.title; fields "Title", "Description", "Assignee"; buttons "Delete" (red text) and "Close".
- Delete confirmation: "Delete this card?" with "Delete" and "Cancel".
- Column delete confirmation: "Delete column “[column name]” and its cards?" with "Delete" and "Cancel".
- Assignee option "Unassigned".
- Column menu item "Delete column".
- Load error: "Could not load the board." with "Try again".
- Empty board: "Add a column to start the board."
- Selector placeholder when no members: "No members".

**Spoken only:**
- Card: "Card, [title], in [column name], assigned to [member name] or unassigned".
- Assignee circle: "Assigned to [member name]" or "Unassigned".
- Column menu button: "Column options for [column name]".
- Add card control: "Add card to [column name]".
- Column count badge: "[N] cards".
- Team member selector: "Acting as [member name]".
- Dragged card: "Moving [title]"; drop target: "Drop in [column name]".

### 5. Contextual Action Placement
- "+ Add card" sits at the foot of its own column.
- Card dialog holds Title, Description, Assignee, Delete, Close, because those change only that card.
- Column rename happens on the column name in its header.
- Column delete sits in the column's "⋯" menu, beside the header.
- "+ Add column" sits after the last column, at the board's right edge.
- Card deletion sits in the card dialog only, not on the card face.
- Team member selection sits in the top bar, because it sets who is acting for the whole board.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: light, airy, and quick to scan.
- **Palette**: page background #F1F2F4; surfaces white #FFFFFF for cards and dialogs; column background #E2E4E8; text #1F2A44 for headings and #44506A for body and secondary text; accent #1F6FEB for focus outlines and the primary dialog action; top bar #1F2A44 with white text; drop-target highlight #D6E4FF; error red #D93025 for outlines and error text; delete text red #C5221F; assignee circle initials on the member's own stored colour (Board.team_members.colour); unassigned circle border #9AA3B2 dashed; card count badge #C9CED8 with text #1F2A44; drag placeholder outline dashed #9AA3B2; dialog backdrop rgba(31,42,68,0.45).
- **Type**: sans (font-sans, system UI stack); column names 14px bold; card titles 14px regular; top bar board name 18px semibold; largest text on the first screen is the board name at 18px semibold.
- **First screen**: the top bar with the board name and member selector, then the board itself: columns side by side with their cards, ready to use. Nothing written above the board.
- **Form of the main view**: a kanban board: columns as fixed-width vertical lanes of 272px, each with a header, a stack of cards and a footer "+ Add card". Cards are 8px-radius white rectangles with a soft shadow (0 1px 2px rgba(31,42,68,0.2)), spaced 8px apart, each sized to its content in height and 248px wide. Column gaps 12px. Empty column shows only its footer control. Below 768px wide, the board keeps column width and scrolls sideways; the top bar stays fixed.
- **Shape and rhythm**: column and dialog corners 12px; cards 8px; inputs 6px; section spacing 12px; cards hover shadow deepens to 0 4px 8px rgba(31,42,68,0.25); dense, scan-friendly layout with 12px internal padding in columns and 16px in the card dialog.

LAYOUT columns=3 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#1F6FEB on_accent=#FFFFFF heading=sans