### 1. Default Landing & Cold-Start Behavior

- No entity is marked "shown to audience"; the board and team members are created by the team, so no records part is loaded from the API.
- The board opens directly on arrival, with the team's single board, its top bar and its columns. No separate landing page.
- While the board loads, the board area shows "Loading board" centred in grey text.
- If the board fails to load, the board area shows "The board could not load." with a "Try again" button beneath.
- A board with no columns shows only "+ Add column" and the line "Add a column to start the board." above it.
- A column with no cards shows only the "+ Add card" control; it carries no text of its own.
- Team members come from the board; with none, the assignee dropdown lists only "Unassigned" and "No team members yet."

### 2. Primary Navigation & View Structure

- The product is one view: the board. There are no tabs, menus or secondary pages.
- The card dialog is an overlay on the board, opened by clicking a card, and closed without leaving the board.
- The top bar holds the board name at left and the "Viewing as" team member selector at right.
- Columns sit left to right in their saved order; the "+ Add column" panel always follows the last column.
- Cards stack top to bottom inside each column, in their saved position order.
- On a narrow screen the top bar stays fixed and the columns keep their width and scroll sideways.

### 3. Workflow Prerequisites & Form Ergonomics

- Adding a card needs a column; with no columns, no "+ Add card" control appears, only "+ Add column".
- Clicking "+ Add card" opens a title field at the column bottom, focused, with placeholder "Enter a title for this card".
- Enter creates the card at the column bottom; Escape closes the field and creates nothing.
- An empty title is refused: the field gets a red outline and the line "A title is required." beneath it.
- Card title: single-line text input, label "Title", required.
- Card description: textarea, label "Description", placeholder "Add a description", may be empty.
- Assignee: dropdown, label "Assignee", options "Unassigned" then each team member by name.
- Title and description save when their field loses focus; no save button.
- Column name: text input with placeholder "Column name"; empty names are refused with the same red outline and "A column name is required."
- Renaming a column: Enter saves a non-empty name; Escape or blur with an empty name restores the previous name.
- Duplicate column names are accepted without warning.
- Delete card and delete column each require a confirmation step before anything is removed.
- Moving a card to a column or position takes effect on drop; a drop outside every column returns the card to where it was.

### 4. Human Copy & Action Labeling

**Seen:**
- "Viewing as" — label beside the team member selector in the top bar.
- Board name — the board's name, in the top bar.
- "+ Add card" — button at the bottom of each column.
- "Enter a title for this card" — placeholder in the new-card field.
- "A title is required." — message beneath a refused card title.
- "+ Add column" — panel after the last column.
- "Column name" — placeholder in the new-column and rename fields.
- "A column name is required." — message beneath a refused column name.
- "Title" — label on the card dialog's title field.
- "Description" — label on the card dialog's description field.
- "Add a description" — placeholder in an empty description field.
- "Assignee" — label on the assignee dropdown.
- "Unassigned" — first option in the assignee dropdown.
- "No team members yet." — text in the dropdown when the board has no members.
- "Delete" — red text button in the card dialog.
- "Close" — button in the card dialog.
- "Delete this card?" — confirmation heading; buttons "Delete" and "Cancel".
- "Delete column "[name]" and its [N] cards?" — confirmation heading; buttons "Delete column" and "Cancel".
- "Delete column" — item in the column menu.
- "Loading board" — text while the board loads.
- "The board could not load." with "Try again" — error state.
- "Add a column to start the board." — text on an empty board.

**Spoken only:**
- "Board name" — top bar title region.
- "Team member selector" — dropdown in the top bar.
- "[Column name], [N] cards" — column header with its badge.
- "Column menu" — icon button on each column header.
- "Card: [title], assigned to [member name]" or "Card: [title], unassigned" — each card.
- "Assignee: [initials]" or "Unassigned" — each assignee circle.
- "Dragging [title]" — announced while a card is dragged.
- "Close dialog" — icon control on the card dialog.

### 5. Contextual Action Placement

- "+ Add card" sits at the foot of its own column, where the new card will appear.
- "+ Add column" sits after the last column, the position the new column takes.
- The column menu, with "Delete column", sits in the column header, beside the name it deletes.
- Clicking the column name edits it in place; no separate rename control.
- Delete card sits inside the card dialog, at its foot, away from Close.
- Assignee dropdown, title and description sit in the card dialog, the thing they change.
- The "Viewing as" selector sits in the top bar, the only place it is needed.
- Confirmation prompts appear in place: over the dialog for a card, over the board for a column.

### 6. Visual Direction

- **Feel:** Trello-style kanban: a light grey working surface with tall columns of white cards, calm and dense.
- **Palette:** Page background #F1F2F4. Surface (cards, dialog) #FFFFFF. Text #172B4D. Top bar #1F2A44 with white text. Accent (focus outlines, primary button) #2563EB, text on it #FFFFFF. Column background #E2E4E8. Drop-target highlight #D6E4FF. Error and Delete text #DC2626. Dashed placeholder and empty assignee outline #9CA3AF. Add-card hover background #D3D6DC. Add-column panel rgba(255,255,255,0.24). Card shadow rgba(9,30,66,0.25); hover deepens to rgba(9,30,66,0.35). Member colours come from each TeamMember.colour.
- **Type:** Sans throughout (font-sans). Board name 20px semibold in the top bar. Column names 14px bold. Card titles 14px regular. Badges and labels 12px.
- **First screen:** The board itself, ready to use: top bar with the board name and selector, then columns and cards directly below. No introductory text above the board.
- **Form of the main view:** A Trello-style board: fixed-width columns side by side in one horizontal row, cards stacked vertically inside. Each column is 272px wide with 12px gaps; columns grow in height with their content, and the board area scrolls sideways when columns overflow. Cards fill the column width minus 12px padding each side and size to their content. An empty column keeps its 272px width and shows only its add control. On a narrow screen the columns keep 272px and the board scrolls sideways.
- **Shape and rhythm:** Columns have 12px corner radius and no border. Cards have 6px radius and the card shadow. The card dialog has 12px radius, 480px maximum width, centred over a rgba(9,30,66,0.54) backdrop. Spacing: 8px between cards, 12px inside columns, 16px around the board area. Top bar 48px tall. Assignee circles 24px. Dense, with no decorative elements.

LAYOUT columns=1 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#172B4D accent=#2563EB on_accent=#FFFFFF heading=sans