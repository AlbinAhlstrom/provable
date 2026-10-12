### 1. Default Landing & Cold-Start Behavior
- The app opens directly on the team's single board; no landing page, login or splash screen.
- The board is the active and only view; it never opens empty because a seeded starter set of three columns ("To do", "Doing", "Done") is created with the board.
- Board name shown in the top bar is read from `Board.name`; while loading, the top bar shows "Loading board…".
- Loading state: columns appear as grey placeholder panels with three grey placeholder bars each; no spinner.
- Failed load: the board area shows "Couldn't load the board." with a "Try again" button beside it.
- Team members list (`TeamMember.name`, `initials`, `colour`) fills the team member selector and assignee dropdown; while loading the selector reads "Loading…".
- Team members list empty: the selector reads "No team members yet" and the assignee dropdown shows only "Unassigned".
- Empty column: shows only the "+ Add card" control; no message text.
- Empty board (all columns deleted): the board area shows "No columns yet." beside the "+ Add column" control.

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, menus or secondary pages.
- Team member selector in the top bar identifies who is acting; choosing a member sets the acting identity for the session.
- Card dialog opens as an overlay on the board; closing returns to the same scroll position.
- Columns scroll sideways inside the board area; the page itself does not scroll sideways.
- Column menu (a "⋯" icon at the header's right) holds one item: "Delete column".
- Card and column reordering stays on the board; no separate ordering screen.

### 3. Workflow Prerequisites & Form Ergonomics
- A card can be created only from an open column add field; no prerequisite beyond the column existing.
- The assignee dropdown is shown in the card dialog only; it lists "Unassigned" first, then team members by name.
- Title field: text input, label "Title", required; empty on blur or Enter shows red outline and message "Enter a title."
- Description field: textarea, label "Description", optional; may be empty.
- Column name field: text input, label "Column name", required; empty on Enter shows red outline and message "Enter a column name."
- Duplicate column names are accepted without warning.
- A drop outside every column returns the card silently to its original place; no error message.
- Delete actions are not offered while a drag is in progress.

### 4. Human Copy & Action Labeling
**Seen:**
- "Board name" heading text: `Board.name`, top bar, left.
- "Team member" label above the selector at right of the top bar.
- Column header: `Column.name` bold; card count badge shows the number only.
- "+ Add card" at each column bottom.
- "Add card" field placeholder: "Card title"; buttons: none, Enter and Escape act.
- "+ Add column" panel after the last column; field placeholder "Column name".
- Card dialog: heading "Card"; field labels "Title", "Description", "Assignee"; dropdown first option "Unassigned"; buttons "Delete" (red text) and "Close".
- Delete confirmation for card: "Delete this card?" with "Delete" and "Cancel".
- Delete confirmation for column: "Delete this column and its N cards?" with "Delete" and "Cancel".
- Column menu item: "Delete column".
- Validation messages: "Enter a title." and "Enter a column name."
- Loading: "Loading board…"; error: "Couldn't load the board." with "Try again".
- Empty team selector: "No team members yet".
- Empty board: "No columns yet."

**Spoken only:**
- Assignee circle: "Assigned to {TeamMember.name}" or "Unassigned".
- Column menu button: "Column options".
- Close icon on card dialog: "Close".
- Team member selector: "Acting as {TeamMember.name}".
- Dragged card: "Moving {Card.title}".

### 5. Contextual Action Placement
- "+ Add card" sits at the foot of its own column.
- "+ Add column" sits after the last column, on the board.
- Delete column sits in the column's header menu, beside the column it removes.
- Delete card sits in the card dialog, beside Close, the card it removes.
- Column rename happens on the column name in its header, in place.
- Assignee dropdown sits in the card dialog, under Description.
- Team member selector sits in the top bar, right, where the acting identity is set.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: calm, light, dense enough to scan many cards at once.
- **Palette**: page background #F1F2F4; top bar #1F2A44 with white text; column surface #E2E4E8; card surface #FFFFFF; primary text #1F2A44; secondary text (counts, placeholders) #6B7280; accent (focus outline, add-field outline) #2563EB; drop target highlight #D6E4FF; error outline and Delete text #DC2626; dashed empty assignee and dragged-origin outline #9CA3AF; add-card hover background #CFD3D9; assignee initials text #FFFFFF on each member's colour; backdrop for dialog rgba(15,23,42,0.5).
- **Type**: `font-sans` for everything (headings and body); column names 14px bold; card titles 14px regular; top bar board name 18px bold; largest text on first screen 18px bold.
- **First screen**: a top bar across the full width, then the board with its columns side by side from the first pixel row downward; no introductory text, no photographs; the seeded columns and any cards are visible immediately.
- **Form of the main view**: a kanban board; columns are fixed-width vertical lanes of 272px, separated by 12px gaps, each column as tall as the board area and scrolling internally when its cards overflow; cards are 272px-minus-16px wide (256px) with a minimum height of 56px and grow with their title; an empty column keeps its full height and shows only "+ Add card". Below 768px wide the board keeps the 272px column width and scrolls sideways; the top bar keeps the board name and selector, with the selector collapsing to initials only.
- **Shape and rhythm**: columns 8px radius, no border, flat #E2E4E8; cards 6px radius with shadow `0 1px 2px rgba(0,0,0,0.12)`, hover `0 4px 8px rgba(0,0,0,0.16)`; dialog 8px radius with shadow `0 8px 24px rgba(0,0,0,0.24)`; 8px gap between cards, 12px inner column padding, 16px gap between header and first card; medium density.

LAYOUT columns=3 rows=auto
TOKENS background=#F1F2F4 surface=#E2E4E8 text=#1F2A44 accent=#2563EB on_accent=#FFFFFF heading=sans