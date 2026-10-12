# Kanban Board for a Small Team

## 1. People and their journey

**Team member.** Any person on the team. Every member has the same access: they see the one board, every column and card, and can create, edit, assign, move and delete cards and columns, and manage the member list.

Journey: open the board, scan the columns to see what work exists, which stage each item is in and who holds it, then add or move a card. The change shows at once for everyone.

## 2. How it looks

A kanban board: a single wide page of side-by-side columns, each a vertical stack of cards, with a plain header bar above.

- **Page background:** flat light grey #F0F2F5, filling the whole window behind everything.
- **Header bar:** flat dark slate #1F2933 across the top, showing the board name in white bold text on the left and member initials on the right.
- **Member initials row:** in the header's right side, overlapping white-on-#3E4C59 circles, one per member; a "+" circle opens the member list.
- **Board canvas:** the area below the header, holding columns left to right in a single row; scrolls sideways when columns overflow.
- **Column:** rounded flat rectangle, background #E4E7EB, about 280px wide, holding a header and its cards stacked top to bottom.
- **Column header:** column name in bold #1F2933 on the left, a grey #616E7C count badge showing the number of cards, and a "..." icon on the right.
- **Column name while editing:** white field with a 2px #2563EB outline replacing the name text.
- **Empty column:** centred italic grey #616E7C text "No cards" under the header.
- **Card:** rounded white #FFFFFF rectangle with a 1px #CBD2D9 border and a faint shadow, showing the title in bold #1F2933 and, if assigned, a 24px #3E4C59 initials circle at bottom right in white text.
- **Card unassigned:** no initials circle is shown; the card's bottom-right corner is empty.
- **Card while dragged:** lifted with a larger shadow and 90% opacity, following the pointer.
- **Drop slot:** a 2px dashed #9AA5B1 outline the height of the card, appearing where the dragged card will land.
- **Card open:** 2px #2563EB outline while its detail panel is shown.
- **Add card control:** grey #616E7C "+ Add a card" text at the foot of each column; becomes a white field with a #2563EB outline when clicked.
- **Add column control:** a rounded #E4E7EB rectangle at the far right of the canvas reading "+ Add another column" in #616E7C.
- **Column menu:** white popover with a 1px #CBD2D9 border listing Rename, Move left, Move right and Delete; Delete is in red #B42318.
- **Card detail panel:** white sheet sliding in from the right edge, about 400px wide, shadowed, covering part of the canvas.
- **Detail panel contents:** title field, description box, assignee dropdown, column dropdown, and a red #B42318 "Delete card" text button at the bottom.
- **Members dialog:** centred white modal over a dimmed grey overlay, listing each member's name and initials with a grey "x" to remove, and a field at the bottom to add a member.
- **Confirmation dialog:** small centred white modal asking to confirm deletion, with a red "Delete" button and a grey "Cancel" button.

## 3. How it is used

- **Click the "+ Add a card" control:** opens a white text field at the foot of that column; type a title.
- **Press Enter in a new card field:** saves the card at the bottom of that column; the field stays open for the next card.
- **Press Escape in a new card field:** discards the unsaved card and closes the field.
- **Click a card:** opens its detail panel on the right.
- **Tap a card (touch):** opens its detail panel.
- **Drag a card within a column (mouse):** moves it to the new position in that column; the drop slot shows where it lands.
- **Long press a card then drag (touch):** lifts the card and moves it to a new position.
- **Drag a card into another column (mouse):** places it in that column at the drop position.
- **Drag a card into another column (touch):** places it there at the drop position after a long press.
- **Change the column dropdown in the detail panel (mouse or touch):** moves the card to the chosen column at the bottom of it.
- **Change the assignee dropdown in the detail panel:** assigns the card to a member, or to nobody.
- **Type in the title or description field of the detail panel:** changes the card; the change saves when the field loses focus.
- **Click "Delete card" in the detail panel:** asks for confirmation, then removes the card.
- **Click a column name (mouse or touch):** opens it for renaming; Enter saves, Escape cancels.
- **Click a column's "..." icon:** opens the column menu.
- **Choose Move left or Move right in the column menu:** swaps that column with its neighbour.
- **Drag a column header (mouse):** reorders the column among the others.
- **Click "+ Add another column":** adds a new column at the far right, opened for naming.
- **Click the "+" in the member initials row:** opens the members dialog.
- **Type a name in the members dialog and press Enter:** adds that person as a member.
- **Click the grey "x" beside a member in the members dialog:** removes that member from the team.

## 4. Scope

The loop: a team member opens the team board, adds a card to the first column with a title and optional description, assigns it to a member, and drags it across columns as the work moves. When the work is finished the card sits in the last column. Members can add or rename columns along the way so the board matches how the team works.

The card detail panel asks only for title, description, assignee and column. Nothing else is asked for.

## 5. Things and their states

- **Board:** one per team. Holds ordered columns and team members. Exists from team creation onward; never deleted.
- **Column:** a name and a position. Created by "Add another column", renamed, reordered, or deleted only when it has no cards.
- **Card:** a title, a description, an optional assignee, a column and a position. Moves through: being typed (unsaved), saved in a column, moved to another column or position, deleted. Moved by drag or by the column dropdown.
- **Team member:** a name and initials. Added from the members dialog, removed from it, and then no longer sees the board.

## 6. Rules

- A card title is required, 1 to 120 characters; a blank title is refused and the card is not saved.
- Editing a card title to blank reverts it to its previous title.
- A card description is optional, up to 5,000 characters; longer text is refused.
- Every card is in exactly one column at all times.
- A card may have no assignee or exactly one team member as assignee; assigning a non-member is refused.
- A card dropped into a column takes the position where it was dropped; other cards shift to make room.
- Column names are required, 1 to 40 characters, and unique on the board; a duplicate or blank name is refused and the old name stays.
- The board always has at least one column; deleting the last column is refused.
- A column with any cards cannot be deleted; the attempt is refused and the cards stay where they are.
- Deleting a column removes only that column; the board keeps the others in their order.
- Moving a column left of the first column or right of the last is ignored.
- Deleting a card requires confirmation; cancelling leaves the card unchanged.
- A deleted card is gone; there is no archive.
- Any team member may create, edit, assign, move or delete any card or column; no member has restricted rights.
- Pressing Escape in an open inline edit discards the unsaved change.
- Two members editing the same card at once: the last saved change is kept.
- Adding a person who is already a member is refused.
- Removing a member clears the assignee on every card they held; those cards stay in their columns.
- A removed member cannot open the board until added again.
- A team has exactly one board; creating a second board is not offered.