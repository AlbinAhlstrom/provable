### 1. Default Landing & Cold-Start Behavior
- The app opens directly on the team's single board; no landing page, login or splash.
- The board shows its columns and cards immediately; the view is never empty of structure.
- Board data loads with a calm "Loading board…" line centred in the board area while the request runs.
- A failed load shows "Board could not load." with a "Try again" button in the same area.
- A new team's board opens with default columns "To do", "Doing", "Done" so the first visit has something to act on.
- Each default column is empty and shows only its "+ Add card" control; no explanatory text is added.
- The top bar shows the board name in white at left; the team member selector sits at right.
- Team members (`Board.team_members`) load with the board; the selector shows a loading state of "Loading team…" until they arrive.
- If the team has no members, the selector reads "No team members yet" and the assignee dropdown shows only "Unassigned".
- "Board name" comes from `Board.name`; the page keeps no copy of it.

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, menus or secondary pages.
- Columns sit left to right in `Column.position` order with 16px gaps; the board area scrolls sideways on overflow.
- Column name is shown as the header, with the card count badge beside it.
- Clicking a card opens the card dialog over a dimmed backdrop; closing returns to the board unchanged.
- The team member selector at top right opens a small list of members showing the name of the active member; choosing one sets who is acting, used only for attribution display.
- "+ Add column" sits as the final item after the last column.
- Column deletion is reached through a "⋯" menu button in the column header, which opens a menu with "Delete column".
- Card deletion is reached only from inside the card dialog.
- On narrow screens the board keeps its column width and scrolls sideways; nothing is stacked.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column; every column always offers its "+ Add card" control, so no prerequisite step is hidden.
- Card creation shows an inline text input at the column bottom, focused on open; Enter creates, Escape cancels.
- The inline title input is a text input labelled "Card title" (screen reader only) with placeholder "Enter a title for this card".
- An empty title on Enter keeps the input open with a red outline and the message "Enter a title to create the card."
- The card dialog title field is a text input labelled "Title"; empty title on blur shows a red outline and "A title is required." and the previous title is restored.
- The description field is a textarea labelled "Description", optional, saved on blur.
- The assignee dropdown is labelled "Assignee" and lists "Unassigned" first, then each team member by name.
- Column rename field is a text input labelled "Column name"; empty name on Enter keeps edit mode with a red outline and "A column name is required."
- Adding a column uses the same inline input pattern with placeholder "Column name"; empty Enter shows the same message.
- Dragging a card onto an unavailable spot (outside every column) is refused by returning it to its original place with no message.
- Actions that are not allowed do nothing: a second confirmation for an already-removed card simply closes the dialog.

### 4. Human Copy & Action Labeling
**Seen**
- "+ Add card" — add-card control at column bottom, every column.
- "+ Add column" — add-column panel after the last column.
- "Enter a title for this card" — placeholder in the inline card input.
- "Enter a title to create the card." — error under the inline card input when empty.
- "Card title" — label of the card title input (visually hidden when inline; visible label "Title" in the dialog).
- "Title" — label of the title field in the card dialog.
- "A title is required." — error under the dialog title field.
- "Description" — label of the description textarea in the dialog.
- "Assignee" — label of the assignee dropdown in the dialog.
- "Unassigned" — first option of the assignee dropdown and its clearing choice.
- "Delete" — red text button in the card dialog.
- "Close" — button in the card dialog.
- "Delete this card? This cannot be undone." — confirmation text in the card dialog.
- "Cancel" and "Delete card" — confirmation buttons for card deletion.
- "Column name" — placeholder for add and rename inputs.
- "A column name is required." — error for empty column name.
- "Delete column" — menu item in each column's "⋯" menu.
- "Delete this column and its N cards? This cannot be undone." — confirmation; N is the card count from the column.
- "Cancel" and "Delete column" — confirmation buttons for column deletion.
- "Loading board…", "Board could not load.", "Try again", "Loading team…", "No team members yet" — load states.

**Spoken only**
- "Team member selector" — name of the top-right selector button.
- "Options menu for [column name]" — name of each column's "⋯" button.
- "Card: [title], assigned to [name]" or "Card: [title], unassigned" — name of each card.
- "Close dialog" — name of the dialog's close icon.
- "Assignee circle, [name]" or "Unassigned" — name of each assignee circle.

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its own column, the place where the card will appear.
- "⋯" column menu sits at the right of its column header, holding "Delete column".
- Column rename happens in place: clicking the header name edits that name where it stands.
- Card deletion sits in the card dialog's footer, left of "Close", where the card is being viewed.
- The assignee dropdown sits in the card dialog beside the title and description it changes.
- "+ Add column" sits after the last column, the place a new column will join.
- Card move happens by dragging the card itself; no move button exists.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: calm, light, and quick to scan.
- **Palette**: page background #F1F2F4; column surface #E2E4E8; card surface #FFFFFF; top bar #1F2A44; primary text #1F2A44; secondary text #5B6478; accent (actions and focus outlines) #2563EB; drop-target highlight #D6E4FF; error outline and delete text #DC2626; dashed placeholder outline #9CA3AF; count badge background #CBD0D9; add-card hover #D3D6DC; add-column panel background rgba(255,255,255,0.5); dialog backdrop rgba(31,42,68,0.4).
- **Type**: `font-sans` for everything; column names and the board name in semibold 600; card titles in regular 400 at 14px; the largest text on screen is the board name at 18px semibold.
- **First screen**: the top bar, then the board with its default columns and their cards in view, ready to use; no introduction text is written above it.
- **Form of the main view**: a horizontal row of fixed-width columns, like a Trello board. Columns are 272px wide, all alike, and grow in height with their content up to the viewport. Cards are full column width minus 16px padding, each as tall as its content. An empty column shows only its add control. Below 640px width the board keeps 272px columns and scrolls sideways.
- **Shape and rhythm**: columns and dialog 8px radius; cards 6px radius with a shadow of `0 1px 2px rgba(0,0,0,0.15)` deepening to `0 3px 8px rgba(0,0,0,0.2)` on hover; 8px gaps between cards; 16px between columns; 12px column padding; dense but unhurried; no borders except the 2px blue focus outline and red error outline.

LAYOUT columns=3 rows=auto

TOKENS background=#F1F2F4 surface=#E2E4E8 text=#1F2A44 accent=#2563EB on_accent=#FFFFFF heading=sans