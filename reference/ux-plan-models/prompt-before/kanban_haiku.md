### 1. Default Landing & Cold-Start Behavior
- The board is the landing view. There is one board per team, so opening the app shows `Board.name` in the top bar with its ordered columns immediately. No splash, no login wall, no separate home page.
- Team member selector sits top-right; the selected member identifies who is acting (used for assignment context only).
- Loading state: columns appear as grey skeleton panels with pale placeholder bars, labelled "Loading board…".
- Error state: a calm inline bar at the top of the board: "The board couldn't load. Try again." with a Retry button.
- Empty board (no columns yet): the board area shows one centred prompt, "Start with a column, such as To do, Doing or Done.", beside the "+ Add column" panel, which is focused on arrival.
- Empty column: only the "+ Add card" control is shown; no extra text.

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, menus or secondary pages.
- Hierarchy: Top bar (board name, team member selector) → Board area (columns left to right, horizontal scroll) → Column (header, cards, add-card control) → Card dialog (modal, opened by clicking a card).
- Column header holds the rename (click name) and column menu (Delete column).
- "+ Add column" sits as the final item in the board row.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card: no prerequisite beyond an existing column. A column with no cards shows only "+ Add card". If the board has no columns, "+ Add column" is the only action and is explained by the empty-board prompt.
- Assignment: the dropdown lists only team members of `Board.team_members`, plus "Unassigned" at the top. No gated or disabled options.
- Title field: single-line text input, label "Card title", placeholder "What needs doing?". Required; an empty submit shows the red outline and the message "Add a title to save this card."
- Description: multi-line textarea, label "Description", placeholder "Add details (optional)".
- Column name: single-line text input, label "Column name", required; empty entry keeps the field open with the red outline.
- Saving: card dialog edits save on blur; no save button needed.

### 4. Human Copy & Action Labeling
- Buttons: "+ Add card", "+ Add column", "Delete", "Close", "Cancel", "Delete card", "Delete column".
- Card title: `Card.title`. Description: `Card.description`, or a grey hint "No description yet" when empty.
- Column header: `Column.name` with badge showing the card count.
- Assignee: `TeamMember.name` on tooltip; initials from `TeamMember.initials` on `TeamMember.colour`; unassigned shows an empty dashed circle with tooltip "Unassigned".
- Confirmations: "Delete this card? This can't be undone." and "Delete column “[Column.name]” and its [N] cards? This can't be undone."
- Errors: "Add a title to save this card." / "Give the column a name."

### 5. Contextual Action Placement
- Card actions (edit, assign, delete) live inside the card dialog, opened by clicking the card.
- Column actions (rename, delete) live in the column header.
- Add-card control sits at the foot of each column; add-column control sits after the last column.
- Drag-and-drop is the movement control; no move menu is needed. A dropped card outside any column returns silently to its origin.

### 6. Visual Direction
This is a Trello-style kanban board, a known look: grey page, dark navy top bar, grey columns holding white raised cards. The direction is kept faithfully so the team recognises it at once.

- **Feel**: calm, familiar, workmanlike.
- **Palette**: page background `slate-100` (#F1F2F4 close match); column surface `#E2E4E8`; cards `white`; text `slate-900`; top bar navy `#1F2A44`; accent `blue-600` for focus outlines and the primary action; drag-over column `#D6E4FF`. Middle tones for avatar circles (400–600) keep white initials readable on member colours.
- **Type**: `font-sans` throughout; column names and board name in `font-bold`, board name at `text-lg`; card titles `text-sm font-medium`.
- **Shape and rhythm**: columns `rounded-xl` with 16px padding, equal 16px gaps; cards `rounded-lg` with `shadow-sm`, deepening to `shadow-md` on hover; dense but airy, about 12px between cards.
- **Form of the main view**: a horizontal row of fixed-width columns, each sized to its content vertically (cards stack top-down). Empty columns keep full height and show only the add-card control. Columns keep equal width; the row scrolls sideways.

LAYOUT columns=auto rows=auto

TOKENS background=#F1F2F4 surface=#E2E4E8 text=#172B4D accent=#2563EB on_accent=#FFFFFF heading=sans