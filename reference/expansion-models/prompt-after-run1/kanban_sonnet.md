# A kanban board for a small team

## 1. People and their journey

**Team member** (the only role): someone on the small team who tracks shared work.
- Needs to see: which cards exist, which column each is in, who is assigned.
- Decides: what to add, who does it, when it moves on.
- Journey: opens the board, scans the columns, adds or edits a card, assigns it, drags it to the next column as work progresses, and removes it when it is no longer needed.

## 2. How it looks

A kanban board as people know it from Trello-style tools: a light grey page, with tall columns side by side, each holding a vertical stack of white cards.

- **Page background**: flat light grey (#F1F2F4), filling the window behind everything.
- **Top bar**: flat dark navy (#1F2A44) strip across the top, with the board name in white at left and the team member selector at right.
- **Board area**: below the top bar, scrolls sideways when columns overflow; columns sit left to right with equal gaps.
- **Column**: flat mid-grey (#E2E4E8) rounded panel, fixed width. Shows the name and card count at the top. While a card is dragged over it, the background turns light blue (#D6E4FF).
- **Column header**: column name in bold dark text, card count in a small grey badge. Clicking the name turns it into an editable text field with a blue outline.
- **Card**: raised white rounded rectangle with a soft shadow. Shows the title and an assignee circle. Hover deepens the shadow. While dragged it tilts slightly and the original spot shows a dashed grey outline.
- **Assignee circle**: small round badge at the card's bottom right showing the member's initials on that member's own colour. An unassigned card shows an empty grey dashed circle.
- **Add card control**: text button "+ Add card" at the bottom of each column, in grey. On hover its background turns darker grey.
- **Add column control**: flat translucent panel after the last column, reading "+ Add column".
- **Card dialog**: centered white raised panel over a dimmed backdrop, with title field, description field, assignee dropdown, Delete (red text), and Close.
- **Empty column**: shows only the add-card control.
- **Validation state**: a field with an error gets a red outline.

## 3. How it is used

- Click "+ Add card": a title field appears at the column bottom; type and press Enter to create it, Escape to cancel.
- Click a card: opens the card dialog.
- Edit title or description in the dialog: changes save when the field loses focus.
- Choose an assignee in the dropdown: the card shows that member's circle. Choosing "Unassigned" clears it.
- Drag a card with the mouse, or long-press then drag with a finger, to another column or position: it drops there.
- Click Delete in the dialog, then confirm: the card is removed.
- Click "+ Add column", type a name, press Enter: a column is added at the end.
- Click a column name, edit it, press Enter: it is renamed.
- Drag a column header sideways: the column moves to a new place.
- Use a column's menu to delete it, after confirming.

## 4. Scope

One board per team. A member creates columns, adds cards, writes titles and descriptions, assigns members, and moves cards between columns until the work is done. Excluded: outside access, billing, reports, integrations.

## 5. Things and their states

- **Board**: name, ordered columns.
- **Column**: name, position, ordered cards.
- **Card**: title, description, assignee (optional), column, position. States: open for viewing, being edited, being dragged, deleted.
- **Team member**: name, initials, colour.

## 6. Rules

- A card title is required; an empty title is refused and the field is outlined red.
- A column name is required; an empty name is refused.
- A card belongs to exactly one column.
- A card has at most one assignee.
- Only team members can be assigned; anyone else is not listed.
- Dropping a card outside any column returns it to its original place.
- Moving a card changes only its column and position; other cards keep their order.
- Deleting a column that holds cards asks for confirmation and removes its cards too.
- Deleting a card asks for confirmation; cancelling changes nothing.
- Column names may repeat.
- Descriptions may be empty.