# A kanban board for a small team

## 1. People and their journey
**Team member** (the only role). Needs to see what work exists, its stage, and who is doing it. Arrives at the team's board, scans the columns, creates or opens a card, edits it, assigns it, drags it to the next column, and leaves when the board shows the truth.

## 2. How it looks
A kanban board as people know it from Trello-style tools: a pale grey workspace with a row of tall, narrow, rounded column lanes side by side, each holding a vertical stack of white cards.

- **Page background**: flat light grey (#EEF0F3) behind everything, filling the window.
- **Top bar**: full-width strip at top, flat white with a thin grey bottom line; shows the board name left and the current member's name right.
- **Board area**: below the top bar; columns sit left to right and scroll sideways when they overflow.
- **Column**: tall lane, flat mid-grey (#E1E4E8) with rounded corners. While a card is dragged over it, it turns pale blue (#D6E6FA) with a blue outline.
- **Column header**: top of the column; bold dark title and a card count. Title becomes an editable text field while renaming.
- **Card list**: vertical stack inside the column; shows an empty-space dashed outline when the column has no cards.
- **Card**: white raised rectangle, soft shadow, rounded; shows title, and an assignee initials circle at bottom right. Hover: shadow deepens. Dragged: tilts slightly, stronger shadow. Original spot shows a grey placeholder.
- **Unassigned mark**: an empty dashed grey circle where initials would be.
- **Assignee initials circle**: filled circle with white initials; each member has their own fixed colour: blue, green, orange, purple, teal, red, assigned in order of joining.
- **Description mark**: small grey lines icon on a card that has a description.
- **Add card control**: text button at the bottom of each column, grey text, darkens on hover. When pressed it becomes a text box with Add and Cancel buttons.
- **Add column control**: dashed-outline lane after the last column; pressed, it becomes a name field with Add and Cancel.
- **Card detail panel**: white panel centered over a dim dark overlay; shows editable title, description box, assignee picker, column name, Delete button in red, Close button.
- **Column menu**: small three-dot button in the header opens a white raised list: Rename, Move left, Move right, Delete.
- **Confirmation box**: small white centered dialog over the overlay with the message, a red Delete button, and Cancel.
- **Error text**: small red line beneath a field when it is refused.

## 3. How it is used
- Click Add card, type a title, press Enter or click Add: the card appears at the column's bottom.
- Press Escape or Cancel in an add box: the box closes and nothing is created.
- Drag a card with the mouse, or press and hold then drag with a finger, to another position or column: it drops there.
- Click a card: the detail panel opens.
- Edit the title or description in the panel: changes save when the field loses focus.
- Choose a member (or Unassigned) in the picker: the card's assignee changes at once.
- Click Delete in the panel: the confirmation box appears.
- Click Add column, type a name, press Enter: a column is added at the far right.
- Click the three-dot menu, choose Rename: the title becomes editable; Enter saves, Escape cancels.
- Choose Move left or Move right in the column menu: the column swaps with its neighbour.
- Choose Delete in the column menu: confirmation appears.
- Click the overlay, Close, or press Escape: the panel closes.

## 4. Scope
One board per team, with ordered columns and cards. Loop: open the board, add cards, assign, move them through columns, edit, and remove finished or obsolete ones. Starting columns: To Do, In Progress, Done.

## 5. Things and their states
- **Board**: name; ordered columns.
- **Column**: name, position; holds ordered cards.
- **Card**: title, description (optional), assignee (optional), column, position. Moves between columns by dragging.
- **Member**: name, colour; can be assigned cards.

## 6. Rules
- A card title is required, 1–120 characters; an empty title is refused with error text.
- A description may be empty, up to 2000 characters.
- A card is in exactly one column at a time.
- A card has at most one assignee; assignment is optional.
- Only existing team members can be assigned.
- Dropping a card outside any column returns it to where it was.
- Dropping a card in its own spot changes nothing.
- A column name is required, 1–40 characters, and unique on the board; otherwise refused.
- Deleting a column that holds cards is refused until the cards are moved or deleted; its menu item shows the refusal message.
- The last remaining column cannot be deleted.
- Deleting a card needs confirmation; Cancel changes nothing.
- Card order within a column is kept after reload.
- Every team member can edit every card and column.