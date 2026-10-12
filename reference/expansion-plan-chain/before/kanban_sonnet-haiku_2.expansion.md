# A kanban board for a small team

## 1. People and their journey
**Team member** (the only role). Needs to see what work exists, its stage, and who is doing it. Decides what to create, assign and move. Path: open the board, scan columns, add or open a card, assign it, drag it onward until it reaches the last column.

## 2. How it looks
A kanban board as people know it from Trello: a pale grey-blue page, with tall rounded columns side by side, each holding a vertical stack of white cards.

- **Page background**: flat light blue-grey (#E9EEF4), fills the screen behind everything.
- **Top bar**: flat white strip across the top, thin grey bottom line, showing the board name at left and the member picker with the signed-in member's initials circle at right.
- **Board area**: horizontal row of columns on the background; scrolls sideways when columns overflow.
- **Column**: rounded flat light-grey (#DDE3EA) panel, fixed width. Shows header, card stack, and add-card button. While a card is dragged over it, its fill darkens to #CBD5E1 with a blue outline.
- **Column header**: bold dark-slate name at the top of a column, with the card count in a small grey pill. Name becomes an editable text box when clicked.
- **Column menu button**: three dots at header right; grey, darkens on hover. Opens rename, move left, move right, delete.
- **Card**: raised white rectangle, soft shadow, rounded corners, title in dark slate, a one-line description preview in grey when a description exists, assignee initials circle at bottom right. Hovered: shadow deepens. Being dragged: tilted slightly, stronger shadow, and its original spot shows a dashed empty outline.
- **Assignee circle**: round, filled with a colour fixed per member: blue, green, orange, purple, teal, red, in order of joining. An unassigned card shows a dashed grey empty circle.
- **Add-card button**: flat text button at the foot of a column, "+ Add a card", grey, with a pale fill on hover. Pressed, it becomes a title box with "Add" and cancel buttons.
- **Add-column area**: a translucent white column-sized button after the last column, "+ Add column"; becomes a name box when clicked.
- **Card detail panel**: white panel centred over a dimmed dark overlay, with an editable title, a description box, an assignee dropdown, a column dropdown, and Delete (red text) and Close buttons.
- **Delete confirmation**: small white dialog over the overlay, with a red Delete button and a grey Cancel button.
- **Empty column**: shows only the add-card button.

## 3. How it is used
- Click "+ Add a card", type a title, press Enter or click Add: the card appears at the bottom of that column.
- Press Escape or the cancel button in the add box: it closes and nothing is created.
- Click a card: the detail panel opens.
- Edit the title or description in the panel: the change saves when the field loses focus.
- Choose a member in the assignee dropdown: the card shows their circle. Choosing "Unassigned" clears it.
- Choose a column in the panel's column dropdown: the card moves to the bottom of that column.
- Drag a card with the mouse, or long-press then drag with a finger, to a spot in any column: it drops there.
- Click the panel's Delete: the confirmation appears; confirming removes the card.
- Click a column name: type a new name, press Enter to save, Escape to cancel.
- Use the column menu to move a column left or right, or delete it after confirming.
- Click "+ Add column", type a name, press Enter: the column is added at the end.
- Click outside the panel, or Close: it closes.

## 4. Scope
One board for the team. A member creates columns, adds cards, describes and assigns them, and moves them across columns until done. Nothing outside the board is included.

## 5. Things and their states
- **Board**: name, ordered columns. Always exists.
- **Column**: name, position. Exists until deleted.
- **Card**: title, description, assignee (optional), column, position. Moves between columns; exists until deleted.
- **Member**: name, colour. Can be assigned to any number of cards.

## 6. Rules
- A card title is required; an empty title is refused and the box stays open.
- A column name is required; an empty name reverts to the previous one.
- Titles are limited to 120 characters; extra typing is ignored.
- A card has at most one assignee.
- A card is in exactly one column at a time.
- Dropping a card outside any column returns it to its original place.
- Moving a card within a column reorders it; other cards shift to fit.
- Deleting a column that holds cards requires confirmation stating the card count; cancelling changes nothing.
- Deleting a column deletes its cards.
- The last remaining column cannot be deleted; the option is greyed out.
- Moving the first column left or the last right is unavailable.
- Deleting a card needs confirmation.
- Deleting a member is not offered; assignment is chosen only from existing members.
- Column names may repeat.