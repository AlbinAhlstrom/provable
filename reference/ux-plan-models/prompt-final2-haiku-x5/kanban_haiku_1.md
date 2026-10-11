### 1. Default Landing & Cold-Start Behavior

- No entity is marked "shown to audience"; `Board` is loaded from the API and its `team_members` fill the top-bar selector and assignee dropdown.
- While `Board` loads, the board area shows "Loading board…" in grey text, with no columns.
- If the board fails to load, the board area shows "The board could not be loaded." and a "Try again" button.
- The opening view is the team's single board, with its columns and cards already in place.
- A board with no columns opens on the "+ Add column" panel alone, with the line "No columns yet." above it.
- A column with no cards shows only the "+ Add card" control; no empty-state line is added.
- With no team members, the selector reads "No team members yet." and the assignee dropdown lists only "Unassigned".

### 2. Primary Navigation & View Structure

- The product is one view: the board. There is no navigation bar, tab set or menu of pages.
- The top bar holds the board name at left and the team member selector at right.
- The team member selector lists `Board.team_members` with initials circles; choosing a member sets who is acting, changing no card data.
- Below 640px wide, the selector shows only the selected member's initials circle.
- The card dialog is a modal over the board, not a separate view; closing it returns to the board.
- Confirmation prompts for card and column deletion are modal over the board.
- Columns sit left to right in one horizontal row; the board area scrolls sideways when columns overflow.
- On narrow screens, the board keeps its column width and scrolls sideways rather than reflowing.

### 3. Workflow Prerequisites & Form Ergonomics

- The "+ Add card" control is shown on every column, including empty ones, so cards can be created at once.
- The assignee dropdown appears in the card dialog only; an unassigned card needs no member first.
- With no team members, the dropdown shows "Unassigned" and the line "No team members on this board." beneath it.
- Add-card field: text input, placeholder "Card title", opens at the column bottom with focus.
- Enter with a non-empty title creates the card at the bottom of the column.
- Enter with an empty title keeps the field open, outlines it red, and shows "Enter a title."
- Escape closes the add-card field and creates nothing; blurring an empty add-card field also closes it without error.
- Card dialog title: text input labelled "Title"; empty on blur keeps the last saved title, outlines red, and shows "Enter a title."
- Card dialog description: textarea labelled "Description"; it may be empty and saves on blur.
- Card dialog assignee: select labelled "Assignee", options "Unassigned" then each team member's name.
- Column rename: text input labelled "Column name"; Enter with a non-empty name renames it.
- Empty column rename: refused, the previous name stays, the field outlines red, and shows "Enter a column name."
- Add-column field: text input labelled "Column name", opens in the "+ Add column" panel; Enter appends the column.
- Column deletion and card deletion each ask a confirmation before acting; Cancel changes nothing.
- A card can be dragged only onto a column or a position; it cannot be dragged onto the top bar.

### 4. Human Copy & Action Labeling

**Seen:**
- "Loading board…" — board area, while loading.
- "The board could not be loaded." and "Try again" — board area, on load failure.
- "No columns yet." — board area, when the board has no columns.
- "No team members yet." — team member selector, when the list is empty.
- "No team members on this board." — card dialog, below the assignee select, when the list is empty.
- "+ Add card" — bottom of each column.
- "Card title" — placeholder in the add-card field.
- "+ Add column" — panel after the last column.
- "Column name" — label and placeholder for add and rename fields.
- "Title" — label in the card dialog.
- "Description" — label in the card dialog.
- "Assignee" — label in the card dialog.
- "Unassigned" — first option in the assignee select.
- "Delete" — red text button in the card dialog.
- "Delete column" — item in the column menu.
- "Close" — button in the card dialog.
- "Cancel" — button in each confirmation.
- "Delete" — confirm button in each confirmation.
- "Delete this card? This cannot be undone." — card deletion confirmation.
- "Delete this column and its cards? This cannot be undone." — column deletion confirmation.
- "Enter a title." — message under a card title field with an error.
- "Enter a column name." — message under a column name field with an error.

**Spoken only:**
- "Team member" — selector at top right.
- "Column menu" — the column's ⋯ button.
- "Board" — board region.
- "Card: [title], assigned to [name]" or "Card: [title], unassigned" — each card.
- "[n] cards" — column count badge.
- "Unassigned" — empty dashed assignee circle.
- "[Name], [initials]" — each assignee circle.
- "Close dialog" — the dialog's dismiss control.

### 5. Contextual Action Placement

- "+ Add card" sits at the bottom of each column, inside it.
- Clicking a column's name turns it into an edit field in place in the header.
- The column menu (⋯) sits at the right of the column header and holds "Delete column".
- Clicking a card opens the card dialog; Delete sits inside the dialog, beside Close.
- The assignee select sits inside the card dialog, below the description.
- "+ Add column" sits as a panel after the last column, on the board.
- Dragging a column moves it by its header; the header is the drag handle.
- Confirmation prompts appear centred over the board, beside their Cancel and Delete buttons.
- The team member selector sits in the top bar at right, always visible.

### 6. Visual Direction

- **Feel**: a familiar Trello-style kanban board: light grey page, tall columns, white cards, calm and utilitarian.
- **Palette**: page background #F1F2F4; surface (cards, dialogs) #FFFFFF; text #1F2A44; accent #0C66E4 for focus outlines, primary buttons and links; top bar #1F2A44 with #FFFFFF text; column #E2E4E8; column drop highlight #D6E4FF; column count badge #DFE1E6 with #44546F text; add-card hover #D0D3D9; add-column panel #FFFFFF at 50% opacity; error outline and error text #DC2626; delete text #C9372C; unassigned circle border #9CA3AF, dashed; dragged-card original spot outline #9CA3AF, dashed; card shadow rgba(9,30,66,0.25) at 1px offset, deepened on hover.
- **Type**: sans (Inter or system sans) for headings and body; board name 20px semibold in the top bar; column names 14px bold; card titles 14px regular.
- **First screen**: the top bar at 48px high with the board name and team member selector, then the board with its columns, or the "+ Add column" panel when there are none. Nothing is written above the board.
- **Form of the main view**: a Trello-style board: one horizontal row of fixed-width columns, each a tall rounded panel with cards stacked vertically; an empty column shows only its "+ Add card" control. Columns are 272px wide with 12px gaps; each column's height fills the board area and its card list scrolls inside it. Board area padding is 16px. On narrow screens the row keeps column width and scrolls sideways.
- **Shape and rhythm**: columns 12px corner radius; cards 8px radius with 8px vertical gap and 12px inner padding; assignee circles 28px; dialogs 12px radius, 24px padding, centred and max 560px wide; medium density, one thin rhythm throughout.

LAYOUT columns=1 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#0C66E4 on_accent=#FFFFFF heading=sans