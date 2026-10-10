### 1. Default Landing & Cold-Start Behavior

- No entity is marked "shown to audience"; the page loads the board and its fixed team members, with a loading line "Loading board…" while they arrive.
- If the board fails to load, show "The board could not be loaded." with a "Try again" button in the centre of the board area.
- The board opens directly, with no welcome text above it.
- A new board starts with columns "To do", "In progress" and "Done", in that order.
- Each column with no cards shows "No cards" in faint grey, beside its "+ Add card" button.
- The header shows `Board.name` (default "Team board") at left and one avatar per `TeamMember` at right.
- Each `TeamMember.avatar_colour` fills that member's avatar with white initials from `TeamMember.name`.
- The board opens with no card selected, no dialog open and no form open.

### 2. Primary Navigation & View Structure

- The product is one view: the board. There are no tabs, menus or navigation.
- The board fills the window below the header and scrolls sideways when columns overflow.
- Columns are placed left to right in workflow order, with 12px gaps, starting 16px from the left edge.
- Each column scrolls its own card list vertically when cards exceed the available height.
- The card dialog opens over the board as a centred modal, and closes back to the same board position.
- The delete confirmation opens as a small modal over the card dialog.

### 3. Workflow Prerequisites & Form Ergonomics

- The "+ Add card" form opens in place of its button at the bottom of its column, with the title field focused.
- The Add button is disabled until the title field holds text; the field placeholder "Enter a card title" sits beside it.
- Title input is a single-line text input labelled "Card title"; Enter submits, Escape cancels.
- Adding a card with a title places it at the bottom of its column and clears the form, leaving it open for the next card.
- The card dialog title is a single-line text input labelled "Title"; it saves on blur.
- An emptied card title is refused on blur with "Title is required" beneath the field, and the previous title is restored.
- The card dialog description is a textarea labelled "Description", placeholder "Add a more detailed description…", optional, saved on blur.
- Assignees are a checklist labelled "Assignees", one row per `TeamMember` with avatar and full name; ticking saves immediately.
- A column name is a text input that opens when its name is clicked, labelled "Column name", saved on Enter or blur.
- An empty column name is refused with "Column name is required" beneath the input, and the previous name is kept.
- A duplicate column name is refused with "A column with this name already exists" beneath the input, and the original name is kept.
- The column delete mark is shown only on an empty column when more than one column exists.
- Deleting a column that holds cards is refused with "Move or delete its cards first" beneath the column header.
- Deleting the last remaining column is refused with "A board needs at least one column" beneath the column header.
- Refusal messages stay until the person's next action on that column or card.
- Dropping a card outside any column returns it silently to its origin; no message appears.
- Cancelling the delete confirmation changes nothing and closes it.

### 4. Human Copy & Action Labeling

**Seen:**
- `Board.name`, default "Team board" — header, left.
- "Loading board…" — board area, while loading.
- "The board could not be loaded." and "Try again" — board area, on failure.
- "To do", "In progress", "Done" — default column names, column header.
- Card count pill, showing the number only — column header.
- "No cards" — empty column, faint grey.
- "+ Add card" — foot of each column.
- "Enter a card title" — placeholder in new card field.
- "Add" and "Cancel" — new card form.
- "Card title" — label, new card field.
- "Title" — label, card dialog title field.
- "Description" — label, card dialog textarea.
- "Add a more detailed description…" — placeholder, description textarea.
- "Assignees" — label, card dialog checklist.
- "Title is required" — message, card dialog.
- "Column name" — label and placeholder, column name input.
- "Column name is required" — message, column name input.
- "A column with this name already exists" — message, column name input.
- "Move or delete its cards first" — message, column header.
- "A board needs at least one column" — message, column header.
- "+ Add column" — end of the column row.
- "Delete this card?" — delete confirmation text.
- "Delete" (red) and "Cancel" — delete confirmation.
- "Delete" (red) and "Close" — card dialog footer.

**Spoken only:**
- Each header avatar: the full `TeamMember.name`.
- Each assignee avatar on a card: the full `TeamMember.name`.
- Each card: its title, then "assigned to" and the names, then its column name.
- Column delete mark: "Delete column".
- Card dialog: "Card details", announced when it opens.
- Delete confirmation: "Confirm card deletion".
- Each column header: the stage name followed by its card count.
- Dragged card original spot: "Empty position".
- Drag handle on a card: "Drag card".

### 5. Contextual Action Placement

- "+ Add card" sits at the foot of each column, under its cards.
- The new card form replaces "+ Add card" in the same column, at the same spot.
- Clicking a card opens its dialog; no separate edit button exists on the card.
- Delete sits in the card dialog footer, beside Close, because it acts on the open card.
- Assignment sits in the card dialog, beside the title and description it belongs to.
- Renaming a column happens by clicking its name in the column header.
- The column delete mark sits at the right of the column header, shown only when the column is empty.
- "+ Add column" sits at the end of the column row, after the last column.
- Dragging a column happens from its header; dragging a card happens from anywhere on the card.
- Member avatars in the header are display only; assignment is done in the card dialog.

### 6. Visual Direction

**Feel:** A familiar team kanban board: calm, flat, low-contrast columns of white cards on a blue-grey floor, dense and quiet.

**Palette:**
- Page background: `#DDE3EA`.
- Header bar: `#1F2A44`, with white header text.
- Column surface: `#EBECF0`; column hover while a card is dragged over it: `#DFE1E6`.
- Card surface: `#FFFFFF`.
- Primary text: `#172B4D` for titles and column names.
- Secondary text: `#5E6C84` for descriptions, card count and "No cards".
- Accent (Add button, focus ring, links): `#2F6FDE`, with white text `#FFFFFF`.
- "+ Add card" hover background: `#D0D5DD`.
- Destructive (Delete button, delete text): `#C9372C`, white text.
- Avatar blue `#2F6FDE`, green `#2E8B57`, orange `#E07B20`, purple `#7E57C2`, red `#C9372C`, teal `#00897B`; initials `#FFFFFF`.
- Dragged card's original spot outline: dashed `#8993A4`, 2px.
- Dialog dim layer: `rgba(0,0,0,0.5)`.
- Refusal message text: `#C9372C`.

**Type:** Sans throughout (`font-sans`). Board name 18px, weight 600, in the header. Column names 14px, weight 700. Card titles 14px, weight 600. Descriptions and counts 13px, weight 400. Largest text on the first screen is the 18px board name.

**First screen:** The header bar fills the top 56px full width with the board name left and avatars right. Below it, three columns start at the left edge of the board area, each 280px wide, filling the height under the header. The three empty columns with "No cards" and "+ Add card" are the first things seen; no text is written above them.

**Form of the main view:** A kanban board: columns in a horizontal row, each a vertical stack of cards. Each column is a fixed 280px wide and each card is full column width minus 16px padding, so all columns are alike whatever they hold. Columns are not fixed proportions; each grows downward with its cards and scrolls internally when long. The row scrolls sideways on narrower screens rather than reflowing, and the "+ Add column" control stays at the row's end. An empty column keeps its full 280px width and shows "No cards" centred in its list area.

**Shape and rhythm:** Columns have 12px corner radius and no border, with 8px internal padding. Cards have 8px corner radius, `shadow-sm` at rest, `shadow-md` on hover, and `shadow-xl` with a 2deg tilt while dragged. Spacing: 8px between cards, 12px between columns, 16px dialog padding. Density is compact.

LAYOUT columns=3 rows=auto

TOKENS background=#DDE3EA surface=#FFFFFF text=#172B4D accent=#2F6FDE on_accent=#FFFFFF heading=sans