# A kanban board for a small team

## 1. People and their journey
**Team member** (the only role). Needs to see what work exists, which stage each item is in, and who is doing it.
Path: open the board, scan the columns, create a card in a column, fill in title and description, assign it to teammates, drag it to the next column as work progresses, edit or delete it when done.

## 2. How it looks
A kanban board as people picture it: a pale blue-grey backdrop with a horizontal row of tall, light grey columns, each holding a vertical stack of white cards.

- **Page backdrop**: fills the window, flat blue-grey (#DDE3EA), with the board filling the space below the header.
- **Header bar**: top, full width, flat dark navy (#1F2A44), white board name at left, member avatars at right.
- **Member avatars**: small circles in the header; each has its own fixed colour (blue, green, orange, purple, red, teal) with white initials. Hover shows the full name.
- **Column row**: below the header, scrolls sideways when columns overflow; columns sit left to right in workflow order with 12px gaps.
- **Column**: flat light grey (#EBECF0) rounded panel, fixed width 280px. While a card hovers over it while dragging, it turns slightly darker (#DFE1E6).
- **Column header**: top of column, bold dark-grey stage name and a card count in a small grey pill.
- **Card list**: inside the column, vertical stack of cards, scrolls within the column when long. Empty column shows the faint text "No cards".
- **Card**: white, raised with a soft shadow, rounded; shows bold title, then one line of description in grey, then assignee avatars at the bottom right. Hover: stronger shadow. Dragged: tilted slightly, with a larger shadow, and its original spot shows as a dashed grey outline.
- **Add card button**: bottom of each column, flat text button "+ Add card" in grey; hover gives a darker grey background.
- **New card form**: replaces the button; a white title box with Add (blue #2F6FDE) and Cancel buttons. An empty title leaves Add greyed out.
- **Card dialog**: centred white raised panel over a 50% black dim layer, with an editable title, description box, assignee checklist with avatars, Delete (red) and Close. Opens when a card is clicked.
- **Delete confirmation**: small dialog with the text "Delete this card?", a red Delete button and a Cancel button.

## 3. How it is used
- Click "+ Add card" in a column: the form opens at the bottom of that column.
- Type a title and press Enter or click Add: the card is created at the bottom of the column.
- Press Escape or click Cancel: the form closes and nothing is created.
- Click a card: the card dialog opens.
- Edit the title or description in the dialog: changes save when the field loses focus.
- Tick or untick a member in the dialog: assigns or unassigns them.
- Drag a card (mouse), or press and hold then drag (finger), to another column or a new spot in its own column: the card drops there and the others shift.
- Click Delete in the dialog, then confirm: the card is removed.
- Click a column's name: edit the name in place; Enter saves.
- Click "+ Add column" at the row's end: a new column is added at the end, ready for a name.
- Drag a column header sideways: reorders columns.
- Click a column's delete mark (shown only when the column is empty): removes the column.

## 4. Scope
One board per team, with ordered columns (new boards start with To do, In progress, Done) and cards. Team members create, edit, assign, move and delete cards, and manage the columns. Excluded: outside user access, billing, reports and integrations.

## 5. Things and their states
- **Board**: name, ordered columns.
- **Column**: name, position, ordered cards. It is either empty or holding cards.
- **Card**: title, description, assignees, column, position. It is moved by dragging, and ends when deleted.
- **Team member**: name, avatar colour. Members are fixed and assigned to cards.

## 6. Rules
- A card title is required; an empty title is refused and the previous title kept.
- A description is optional.
- A card sits in exactly one column at one position.
- A card has zero or more assignees, with each member counted once.
- A drop outside any column returns the card to its origin.
- Moving a card renumbers the positions in both columns.
- A column that holds cards cannot be deleted; the attempt is refused with the message "Move or delete its cards first".
- A column name is required and must be unique on the board; otherwise the edit is refused.
- Deleting a card needs confirmation; cancelling changes nothing.
- The last remaining column cannot be deleted.