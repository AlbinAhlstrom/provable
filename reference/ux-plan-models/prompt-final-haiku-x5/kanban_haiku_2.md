### 1. Default Landing & Cold-Start Behavior
- The app opens directly on the team's single board; no landing page, login, or splash screen.
- The board shows its named columns and cards immediately; the top bar shows the board name at left.
- Board data loads with a loading state: a grey skeleton of three empty columns with pale grey bars, no spinner text.
- If the board fails to load: "Couldn't load the board." with a "Try again" button, centred in the board area.
- A new team with no columns sees no empty board: "Add your first column" is the only prominent control, plus "+ Add column" after it.
- A column with no cards shows only the "+ Add card" control; no text inside the column.
- Team member records load into the top-bar selector; while loading, the selector reads "Loading team…".
- If team members fail to load: "Couldn't load the team." beside the selector, with "Try again".
- Board.team_members empty: the assignee dropdown shows only "Unassigned" and the selector reads "No team members yet."
- Card and column records are never shown as a copy; the page reads them from the board record each time.

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, sidebar, or menus beyond the top bar and column menus.
- Top bar holds: board name (left) and team member selector (right).
- The team member selector identifies who is acting; choosing a member sets the "acting as" name shown in the selector.
- Clicking a card opens the card dialog over the board; Close returns to the board with no navigation change.
- Column menu (three-dot icon at the header's right) holds one item: "Delete column".
- Board area scrolls horizontally when columns overflow; the top bar stays fixed.
- On narrow screens, the board keeps its horizontal scroll; columns stay at fixed width and are not stacked.
- No reports, settings, integrations, or outside-access views.

### 3. Workflow Prerequisites & Form Ergonomics
- Add card: the title field appears at the column bottom with focus; it does not need prior steps.
- Card title field: text input, label "Card title" (visually hidden label in the add field, placeholder "Card title").
- Empty title on Enter: the field gets a red outline and keeps focus; the card is not created.
- Card dialog title field: text input, label "Title"; empty title on blur shows a red outline and the previous saved title is kept.
- Card description: textarea, label "Description", may be empty; saved on blur.
- Assignee: dropdown labelled "Assignee", first option "Unassigned", then each team member by name.
- Column name field: text input, label "Column name"; empty name on Enter shows a red outline and the rename is refused.
- Add column field: text input, placeholder "Column name"; empty name on Enter shows a red outline and nothing is added.
- Delete actions need no prior step; the confirmation is the second step.
- Card dragging needs no prior step; a card cannot be dragged while its dialog is open.
- Dropping outside any column returns the card silently to its original place; no message.
- Column name may repeat; no duplicate warning.

### 4. Human Copy & Action Labeling
**Seen:**
- "Board name" (top bar, the board's name value is an attribute of the board; no heading text added)
- "Team member" (selector label, visually shown as the selector's current name or "Select member")
- "Loading team…" (selector while loading)
- "No team members yet." (selector when empty)
- "Couldn't load the board." / "Try again" (board load error)
- "Couldn't load the team." / "Try again" (team load error)
- "+ Add column" (add column control)
- "+ Add card" (add card control in each column)
- "Add" (add card submit button, Enter also submits)
- "Card title" (add field placeholder)
- "Column name" (rename and add column placeholder)
- "Title", "Description", "Assignee" (card dialog labels)
- "Unassigned" (assignee option and empty state)
- "Delete" (card dialog, red text)
- "Close" (card dialog)
- "Delete this card? This can't be undone." / "Delete card" / "Cancel" (card delete confirmation)
- "Delete column?" / "This removes the column and its N cards." / "Delete column" / "Cancel" (column delete confirmation; N is the card count)
- "Delete column" (column menu item)
- Card count badge: the number only.
- Validation: "Enter a title." under the card title field; "Enter a column name." under the column name field.

**Spoken only:**
- Assignee circle: "Assigned to [member name]" or "Unassigned".
- Column menu button: "Column options for [column name]".
- Card: "[title], [column name], [assignee or unassigned]".
- Column count badge: "[N] cards".
- Column name button: "Rename column [name]".
- Dragged card: "Moving [title]".
- Dialog backdrop close: "Close dialog".

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its own column.
- Card edit controls (title, description, assignee, Delete, Close) sit in the card dialog that opens from the card.
- Column rename happens by clicking the column name in its header.
- Column delete sits in the column menu on that column's header.
- "+ Add column" sits after the last column on the board.
- Team member selector sits at the top bar's right, identifying the acting member.
- Card delete confirmation sits in the card dialog's flow, with Delete and Cancel as its two buttons.
- Column delete confirmation sits as a centred dialog over the dimmed board.
- Drag feedback (column highlight, card tilt) appears on the target column and the dragged card only.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: calm, light, tidy, and quick to scan.
- **Palette**: page background #F1F2F4; surface (cards) #FFFFFF; column surface #E2E4E8; top bar #1F2A44; text #172B4D; accent #0C66E4 for the primary "Add" button and focus outline; drop target #D6E4FF; error red #C9372C; card shadow rgba(9,30,66,0.25); dashed placeholder #8C93A3; assignee circles use each team member's own colour; unassigned circle uses grey #C4C8D0 dashed; "Delete" text #C9372C; badge background #DCDFE4 with text #44546F.
- **Type**: `font-sans` for headings and body; column names 14px bold; card titles 14px regular; board name 18px bold in white; the largest text on the first screen is the board name at 18px, weight 700.
- **First screen**: the board itself, opened immediately: top bar with the board name and team member selector, then the columns with their cards. No introduction text, no banner.
- **Form of the main view**: a Trello-style horizontal board of fixed-width columns. Each column is 272px wide, with 8px gaps between columns and 12px inner padding. Cards are placed in a vertical list, each card full column width minus padding, with 8px spacing. An empty column holds only the "+ Add card" control, same width as the column. The whole board keeps no fixed proportions; its height grows with its tallest column, and the board area scrolls horizontally when columns exceed the viewport. On narrow screens, columns keep 272px width and the board scrolls sideways.
- **Shape and rhythm**: column and card corners 8px radius (cards 6px); cards use a soft shadow (0 1px 1px rgba(9,30,66,0.25), 0 0 1px rgba(9,30,66,0.31)), deepening on hover; section spacing 16px; dense enough to scan many cards, with 8px card gaps and 14px card title text. Card dialog is 560px wide, 12px radius, centred over a rgba(9,30,66,0.54) backdrop. Form fields 36px high with 4px radius; red error outline 2px.

LAYOUT columns=4 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#172B4D accent=#0C66E4 on_accent=#FFFFFF heading=sans