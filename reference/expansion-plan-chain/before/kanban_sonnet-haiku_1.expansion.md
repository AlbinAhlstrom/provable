# A kanban board for a small team

## 1. People and their journey

**Team member** (the only role). Every member has the same abilities.
- Needs to see: what work exists, which column each card is in, who holds it.
- Decides: what to create, who does it, when it moves.
- Path: open the board, scan the columns, add or open a card, assign it, drag it onward as work progresses, until it sits in the last column.

## 2. How it looks

A kanban board as people know it from Trello: a pale page with a horizontal row of tall, rounded grey column lanes, each holding a vertical stack of white cards.

- **Page background**: flat soft blue-grey (#E8EDF2), filling the window behind everything.
- **Top bar**: flat dark navy strip across the top, with the board name in white and the member avatar chips at the right.
- **Member chips**: small round coloured circles with white initials. Each member has a distinct colour: blue, green, orange, purple, teal, red. A chip is outlined white when it is the active filter.
- **Column row**: sits below the bar and scrolls sideways when columns overflow.
- **Column**: flat light grey (#DDE2E8) rounded lane with a title and a card count. While a card is dragged over it, it turns light blue.
- **Column menu**: a "⋯" button in the column header. Hovering darkens its background.
- **Card**: raised white rectangle with a faint shadow, showing the title and the assignee chip at the bottom right. Hover deepens the shadow. While dragged it tilts slightly with a larger shadow. A dashed grey gap marks its drop spot.
- **Unassigned card**: shows a dashed empty circle instead of a chip.
- **Add card button**: text button at the bottom of each column. While open it becomes a text box with "Add" and "Cancel".
- **Add column**: a translucent lane at the row's right end reading "+ Add column"; it turns into a name box when clicked.
- **Card dialog**: a white raised panel centred over a dimmed backdrop, with title field, description field, assignee picker, Delete (red text) and Close.
- **Delete confirmation**: a small dialog with a red "Delete" button and a grey "Cancel".
- **Empty column**: shows a faint dashed outline where cards would go.

## 3. How it is used

- Click "Add card" in a column, type a title, press Enter or click Add: the card goes to the bottom.
- Press Escape or click Cancel while adding: nothing is created.
- Click a card: the card dialog opens.
- Edit the title or description in the dialog: changes save when the field loses focus.
- Choose a member in the assignee picker: the card shows their chip. Choose "Unassigned" to clear it.
- Drag a card with the mouse to a spot in any column: it moves there.
- Touch: long press a card, then drag it to a new spot.
- Click "+ Add column", type a name, press Enter: the column is added at the right end.
- Click a column title: it becomes editable; Enter saves.
- Drag a column header sideways: the column changes place.
- Open the column menu and choose Delete: a confirmation appears.
- Click a member chip in the top bar: only that member's cards show. Click it again to clear.
- Click the backdrop or Close, or press Escape: the dialog closes.

## 4. Scope

One board for the team. Members create, edit, assign, filter and move cards across ordered columns, and manage the columns. Not included: outside access, billing, reports, integrations.

## 5. Things and their states

- **Board**: a name and an ordered list of columns.
- **Column**: a name, a position, and an ordered list of cards. It is either present or deleted.
- **Card**: a title, a description, at most one assignee, a column and a position. It is unassigned or assigned, and it is either present or deleted.
- **Member**: a name, a colour and initials.

## 6. Rules

- A card title is required; an empty title is refused and the card is not created.
- A title is at most 120 characters; extra typing is ignored.
- A card is in exactly one column at one position.
- A card has at most one assignee, who must be a team member.
- Dropping a card outside any column returns it to its original spot.
- Moving a card reorders the other cards without gaps.
- Column names are required and unique; an empty or duplicate name is refused and the old name stays.
- Deleting a column that has cards is refused until the cards are moved or deleted; the confirmation says so.
- The last remaining column cannot be deleted.
- Deleting a card needs confirmation; Cancel changes nothing.
- The member filter only hides cards; it never changes them.
- Every member can edit any card.
- The board remembers card positions and column order after reload.