### 1. Default Landing & Cold-Start Behavior
- On opening, the app shows the team's one board (`Board.name` in the top bar). There is no picker and no onboarding screen.
- **Loading:** grey skeleton columns at fixed width, with no text.
- **Load failed:** a centered note reads "Couldn't load the board." with a "Try again" button.
- **Board with no columns:** only the "+ Add column" panel shows, already open as a name field, with the hint "Name your first stage, e.g. To do".
- **Empty column:** shows only "+ Add card" and nothing else.

### 2. Primary Navigation & View Structure
- There is a single view, the **Board**, with no tabs.
- **Top bar:** `Board.name` at left. The "Viewing as" member selector at right, listing `TeamMember.name` with initials circles.
- **Board area:** columns in position order, then the "+ Add column" panel. It scrolls sideways when the columns overflow.
- **Card dialog:** an overlay on the board, not a separate page.
- **Confirm dialogs:** small overlays for deleting a card or a column.

### 3. Workflow Prerequisites & Form Ergonomics
- **Adding a card needs a column.** With no columns, the only control on the board is the open column-name field, so there is nothing disabled to explain.
- **Card title:** a single-line text input.
  - Pressing Enter with an empty title keeps the field open, outlines it red and shows "Give the card a title."
  - Escape cancels.
  - In the dialog, clearing the title and leaving the field restores the previous title, with a red outline and the same message.
- **Description:** a multi-line textarea labelled "Description", with the placeholder "Add more detail (optional)". It saves when it loses focus and may be empty.
- **Assignee:** a select labelled "Assigned to". It offers "Unassigned" first, then only `TeamMember.name` entries.
- **Column name:** an inline text input with a blue outline.
  - Empty plus Enter is refused, shown with a red outline and "Give the column a name."
  - Escape reverts the edit.
  - Repeated names are allowed.

### 4. Human Copy & Action Labeling
- **Buttons:** "+ Add card", "+ Add column", "Close", "Delete card" (red text), "Delete column".
- **Card delete confirm:** "Delete this card?" with "Delete" and "Keep card".
- **Column delete confirm:** "Delete column "{name}" and its N cards?" with "Delete" and "Keep column".
- **Card count:** a plain number in the column's badge.
- **Unassigned:** the dashed circle carries the tooltip "Unassigned".

### 5. Contextual Action Placement
- **Card actions:**
  - Adding a card sits at the bottom of its own column.
  - Editing, assigning and deleting a card happen inside the card dialog.
  - A card is moved by dragging it with the mouse, or by long-pressing and dragging on touch.
  - Dropping a card outside every column animates it back to its original place.
- **Column actions:**
  - A column is renamed by clicking its name.
  - A column is reordered by dragging its header.
  - Deleting a column is done from the "⋯" menu in the column header.
- **New columns:** created from the trailing "+ Add column" panel and always added at the end.

### 6. Visual Direction
- **Feel:** a familiar Trello-style board that is calm, practical and recognisable at once.
- **Palette:**
  - Page background: #F1F2F4 (gray-100).
  - Top bar: navy #1F2A44.
  - Columns: #E2E4E8. A column turns #D6E4FF while a card is dragged over it.
  - Cards: white.
  - Text: slate-800.
  - Accent: blue-600, used for focus outlines and dialog action buttons.
  - Errors: red-600.
  - Member circles use each `TeamMember.colour` with white initials.
- **Type:** `font-sans` throughout. The board name is text-lg semibold. Column names are text-sm bold. Card titles are text-sm.
- **First screen:** the board itself, ready to use, under the top bar. There is no intro text.
- **Form of the main view:** a kanban board.
  - Columns are fixed at 272px wide with 12px gaps. Each grows with its cards and scrolls internally past the viewport height.
  - Cards are full column width, and each card's height fits its title.
  - The assignee circle sits at the bottom right of each card.
  - A dragged card tilts about 3° and leaves a dashed grey placeholder at its original spot.
- **Shape and rhythm:**
  - Columns use rounded-xl corners with no border.
  - Cards use rounded-lg corners with shadow-sm, deepening to shadow-md on hover.
  - Spacing is 8px between cards and 16px of board padding.
  - The dialog is rounded-xl with shadow-xl over a black/40 backdrop.

LAYOUT columns=4 rows=auto
TOKENS background=#F1F2F4 surface=#ffffff text=#1e293b accent=#2563eb on_accent=#ffffff heading=sans