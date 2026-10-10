### 1. Default Landing & Cold-Start Behavior
- The app opens straight onto the team's single board (no landing page, no tabs), with the board name and member selector in the top bar.
- Loading: the columns appear as grey skeleton panels with placeholder cards. Failure: an inline message in the board area, "Couldn't load the board. Try again", with a Try again button.
- A new board with no columns shows one welcoming panel in the board area: "No columns yet. Add your first column to start." Beside it sits the "+ Add column" panel with its name field already open and focused.
- A column with no cards shows only "+ Add card", as the spec requires. Nothing else is added.
- If `Board.team_members` is empty, the assignee dropdown shows only "Unassigned", with the note "No team members yet."

### 2. Primary Navigation & View Structure
One view: **the board**.
- Top bar: `Board.name` at left, team member selector at right.
- Board area: columns left to right, then "+ Add column".
- Overlays: the card dialog and the confirmation dialogs (delete card, delete column). Neither is a separate page.
- Nothing else exists: no settings, reports or admin surfaces.

### 3. Workflow Prerequisites & Form Ergonomics
- **Add card**: no prerequisite. Single-line text field, label "Card title" (placeholder "Enter a title…"). Enter creates, Escape cancels. If the title is empty, nothing is created, the field gets a red outline, and the message "Add a title to create the card." appears.
- **Card dialog**: title is a text input labelled "Title". Description is a textarea labelled "Description", with placeholder "Add more detail (optional)". Assignee is a dropdown labelled "Assignee", listing "Unassigned" plus each `TeamMember.name`. Edits save on blur, and a quiet "Saved" appears after a save. An empty title on blur reverts nothing silently: it shows a red outline and "A card needs a title."
- **Column name**: text field. If empty, it is refused with a red outline and "A column needs a name." Duplicate names are allowed, so no warning is shown.
- **Delete confirmations** state the consequence. A column with cards reads: "Delete this column and its N cards? This can't be undone."
- Dragging needs no setup. Dropping outside a column snaps the card back.

### 4. Human Copy & Action Labeling
- Buttons: "+ Add card", "+ Add column", "Add card", "Add column", "Close", "Delete", "Cancel", "Delete card", "Delete column".
- Column menu (a "⋯" button): "Rename", "Delete column".
- Card delete confirmation: "Delete this card? This can't be undone."
- Drag hint: none. Cursor changes and visual feedback carry the meaning.
- Unassigned circle: no text, with an accessible label "Unassigned". An assigned circle shows `TeamMember.initials` and has the label `TeamMember.name`.
- Count badge: `N`, the number of cards in the column.

### 5. Contextual Action Placement
- Add card sits at the bottom of its own column. Add column sits after the last column.
- Rename is done by clicking the column name. Column delete is in that column's "⋯" menu in the header.
- Card edit, assign and delete live only in the card dialog, with Delete (red text) at the dialog's left and Close at the right.
- Drag handles: the whole card for cards, the header for columns.

### 6. Visual Direction
- **Feel**: Trello-style kanban board, light and tactile, recognisable at once.
- **Palette**: page `#F1F2F4` (slate-100), column `#E2E4E8` (slate-200), surface white, text slate-800, accent blue-600, top bar `#1F2A44`, drag-over column `#D6E4FF`, error red-500. Member colours are mid-tones (400–600) so white initials stay readable.
- **Type**: `font-sans` for headings and body. Board name is 18px semibold white. Column names are bold at 14px.
- **First screen**: the board itself, ready to use, with no introduction text.
- **Form of main view**: horizontally scrolling row of fixed-width columns (about 272px) of equal gaps. Columns grow in height with their cards, and cards are as tall as their content.
- **Shape and rhythm**: 8px radius on columns, 6px on cards, soft shadow on cards that deepens on hover, 8px gaps, compact density.

LAYOUT columns=4 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#1E293B accent=#2563EB on_accent=#FFFFFF heading=sans