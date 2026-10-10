# A kanban board for a small team

## 1. People and their journey
**Team member** (the only role). Needs to see what work exists, its stage, and who is on it.
Path: open the board → scan columns → create a card in a column → edit title and description → assign teammates → drag the card to the next column as work progresses → remove the card when it is no longer needed.

## 2. How it looks
A kanban board as people know it: a coloured backdrop with a horizontal row of tall, narrow column lists, each holding a vertical stack of white cards.

- **Page backdrop**: fills the whole window, flat blue (#0079BF); behind everything else.
- **Top bar**: full-width strip across the top, flat dark blue (#026AA7), showing the board name in white bold text.
- **Board area**: below the top bar, a horizontal row of columns; scrolls sideways when columns overflow.
- **Column**: light grey (#EBECF0) rounded panel, about 272px wide, raised slightly. While a card is dragged over it, its fill darkens to #DFE1E6.
- **Column header**: top of the column, bold dark grey (#172B4D) column name, with a card count in grey at right. Name becomes an editable text field while being renamed.
- **Card**: white rounded rectangle with a faint shadow inside a column, showing the title in dark text and small round assignee badges at the bottom. Hover: shade darkens slightly. Dragged: tilted slightly, stronger shadow. Its original slot shows a grey placeholder.
- **Assignee badge**: small circle with the member's initials, in that member's own colour; one of six: red #EB5A46, orange #FF9F1A, green #61BD4F, purple #C377E0, sky #00C2E0, pink #FF78CB. Members are given the colours in order of joining, wrapping around.
- **Add-card control**: bottom of each column, flat text "+ Add a card" in grey; hover gives a light grey fill. Click turns it into a text box with a green (#5AAC44) "Add" button and a close "×".
- **Add-column control**: after the last column, translucent white panel reading "+ Add another column"; click opens a name field with green "Add" button and "×".
- **Card dialog**: centred white panel over a dark translucent overlay, containing editable title, description box, assignee list with checkmarks, red "Delete" button and a "×" close.
- **Empty column**: shows only its header and the add-card control.

## 3. How it is used
- Click "+ Add a card": type a title, press Enter or Add; the card appears at the column's bottom.
- Press Escape or click "×" in the add form: the form closes and nothing is created.
- Click a card: opens the card dialog.
- Edit title in the dialog: click it, type, press Enter or click away to save.
- Edit description: click the box, type; it saves when focus leaves.
- Click a member in the dialog's assignee list: toggles assignment on or off.
- Click Delete in the dialog: asks for confirmation, then removes the card.
- Drag a card (mouse), or long-press then drag (finger): a placeholder shows the drop spot; release to place it.
- Drag a card to another column: it moves there at the dropped position.
- Click a column name: rename it; Enter saves, Escape cancels.
- Click "+ Add another column": type a name, Enter adds it at the right end.
- Drag a column header: reorders columns; release to drop.
- Click a column's "⋯" menu, then "Delete column": asks for confirmation, then removes it and its cards.
- Click "×" on the dialog, press Escape, or click the overlay: closes the dialog.

## 4. Scope
One board per team. A member creates columns (stages) and cards, edits, assigns, reorders and moves cards, and deletes them. Excluded: external access, billing, reports, integrations. Forms ask only for a title or name.

## 5. Things and their states
- **Board**: name, ordered columns. Always exists.
- **Column**: name, position, ordered cards. States: empty, populated.
- **Card**: title, description (optional), assignees, column, position. Moves between columns by drag; it ends by deletion.
- **Team member**: name, initials, colour. Assigned to zero or more cards.

## 6. Rules
- Card title is required; an empty title is refused and the form stays open.
- Titles are trimmed; whitespace-only counts as empty.
- Title is at most 200 characters; extra typing is ignored.
- Column name is required, at most 50 characters; an empty rename restores the old name.
- Column names need not be unique.
- A card belongs to exactly one column.
- New cards go to the bottom of their column.
- Dropping a card outside any column returns it to its original place.
- Card order is kept exactly as placed, including after reload.
- A card may have any number of assignees, including none; a member is assigned to a card at most once.
- Deleting a card or column requires confirmation; cancelling changes nothing.
- Deleting a column also deletes its cards, and the confirmation states how many.
- The last remaining column cannot be deleted; the option is shown disabled.
- Changes are saved immediately and shown to all team members.