### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience", so no records are loaded from an external catalogue.
- The page opens directly on the team's one board, with its name in the top bar.
- Board and TeamMember records load together; while they load, the board area shows a grey "Loading board…" line.
- If the load fails, the board area shows "Board could not load." with a "Try again" button.
- A board with no columns shows only the "+ Add column" panel, which is the first thing to use.
- An empty column shows only its "+ Add card" control; no placeholder text is added.
- A column with no cards shows only its "+ Add card" control, as the specification states.
- The team member selector shows the acting member's initials circle until a member is chosen.

### 2. Primary Navigation & View Structure
- The product is one view: the board. There are no tabs, menus or secondary pages.
- The top bar holds the board name at left and the team member selector at right.
- Columns sit left to right in the board area and scroll sideways when they overflow.
- Each column's menu (a "⋯" button beside its name) holds one item: "Delete column".
- The card dialog opens over the board and is the only overlay besides confirmations.
- Confirmations appear as small centred panels over the dimmed backdrop.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column; the "+ Add card" control appears only inside existing columns.
- Adding a column needs no prerequisite; "+ Add column" is always shown after the last column.
- Assignee dropdown is shown in the card dialog only; it lists the board's team members and "Unassigned" first.
- Card title field: text input, label "Title", required; empty submit gives a red outline and no message.
- Description field: textarea, label "Description", optional; saves on blur, empty allowed.
- Assignee field: select input, label "Assignee", options "Unassigned" plus each team member's name.
- Column name field: text input, label "Column name", required; empty entry gives a red outline and is refused.
- Delete and drag-and-drop are never blocked; a drop outside any column silently returns the card to its place.
- Renaming, adding and deleting are refused, not disabled, when the name is empty or confirmation is cancelled.

### 4. Human Copy & Action Labeling
Seen:
- "Board name" heading text in the top bar, taken from Board.name.
- "+ Add card" at each column bottom, on the add control.
- "+ Add column" panel after the last column.
- "Add" and "Cancel" on inline add fields (Enter adds, Escape cancels).
- Column count badge showing the number of cards in the column header.
- "Title" and "Description" labels in the card dialog.
- "Assignee" label with the dropdown in the card dialog.
- "Unassigned" as the first dropdown option and the cleared assignee state.
- "Delete" (red text) and "Close" buttons in the card dialog.
- Confirmation for cards: "Delete this card?" with "Delete" and "Cancel".
- Confirmation for columns: "Delete this column and its N cards?" with "Delete column" and "Cancel".
- "Column name" label in the rename field and the add-column field.
- "Loading board…", "Board could not load." and "Try again" for load states.
Spoken only:
- "Add card to [column name]" on each add-card control.
- "Column [name], N cards" on each column header.
- "Card [title], assigned to [member name]" or "Card [title], unassigned" on each card.
- "Assignee circle, [member name]" or "No assignee" on each assignee circle.
- "Team member selector, [member name]" on the top-bar selector.
- "Column menu for [column name]" on each column's "⋯" button.

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its own column, in grey.
- "+ Add column" sits as a panel after the last column, in the board area.
- Rename happens on the column name itself; clicking it turns it into an input in place.
- Column reorder happens by dragging the column header sideways.
- Delete column sits in that column's "⋯" menu, beside the column it removes.
- Card edit, assignee and Delete all sit inside the card dialog, opened from the card.
- Card drag happens directly on the card; no separate move control exists.
- Team member selector sits at the top bar's right edge, where the identity of the user is shown.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: flat grey page, tall columns, white cards, calm and quick to scan.
- **Palette**: page background #F1F2F4; column surface #E2E4E8; card surface #FFFFFF; top bar and main text #1F2A44; accent #2563EB for focus outlines and the primary "Add" button; error red #DC2626 for validation outlines and Delete text; drop highlight #D6E4FF for a column under a dragged card; dashed placeholder outline #9CA3AF; unassigned circle fill #E2E4E8 with the dashed outline #9CA3AF; initials text #FFFFFF on each member's colour; body secondary text #6B7280 for counts and labels.
- **Type**: sans family (Inter, or system sans) for everything. Board name is 18px, semibold, white on navy. Column names are 14px bold. Card titles are 14px regular. Counts and labels are 12px.
- **First screen**: the top bar with the board name, then the board area with its columns (or the "+ Add column" panel on an empty board), all visible without scrolling. No introductory text, no hero, no photographs.
- **Form of the main view**: a kanban board of vertical columns side by side. Each column is a fixed 272px wide rounded panel with 8px gaps between columns. Columns are as tall as the board area and do not stretch. Cards are full column width minus 16px, stacked with 8px gaps, each with its own height from content. An empty column shows only its add control. On a narrow screen the board keeps 272px columns and scrolls sideways.
- **Shape and rhythm**: column radius 12px; card radius 8px with a soft shadow (0 1px 2px rgba(31,42,68,0.12)) that deepens on hover; assignee circle 24px; spacing 16px between the top bar and board, 12px inside columns; medium density with generous padding.

LAYOUT columns=1 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#2563EB on_accent=#FFFFFF heading=sans