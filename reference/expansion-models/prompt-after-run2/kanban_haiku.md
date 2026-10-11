# Kanban board for a small team

## 1. People and their journey

**Team member.** Anyone on the team who shares the board.

- **Needs to see:** every column in order, every card in its column, and who holds each card.
- **Needs to do:** add work, describe it, assign it, and move it across columns as it progresses.
- **Journey:** opens the board, sees where work stands, adds or picks up a card, assigns it, moves it column by column, and leaves it in the last column when it is done.

## 2. How it looks

A classic kanban board: a single row of vertical columns, each holding a stack of small cards, all on one screen.

- **Page background:** flat light grey filling the whole screen, behind everything else.
- **Top bar:** flat white strip along the top edge. Board name at the left in bold dark grey. Member initials in small circles at the right; clicking them opens the Team panel.
- **Board area:** fills the space below the top bar. Columns sit side by side left to right in their order and scroll sideways when they do not fit.
- **Column:** flat pale grey-blue panel, one per workflow stage, with a thin grey edge. Dragged, it lifts with a soft shadow.
- **Column header:** column name in bold dark grey, with the card count in grey in brackets after it. While renaming, it becomes a white box with a blue outline.
- **Column menu:** a three-dot icon at the header's right edge; opens a small white menu listing Rename and Delete column.
- **Empty column:** a dashed grey outline inside the panel with "No cards" in grey, centred.
- **Add card link:** blue text "+ Add card" at the foot of each column, with no border or fill.
- **Card:** white rectangle with thin grey outline and faint shadow. Title in bold dark grey; assignee's initials in a small grey circle at bottom right, or empty if unassigned. Hovered, its outline darkens. Selected, it gets a 2-pixel blue outline. Dragged, it turns 80% transparent and its shadow deepens.
- **Drop marker:** a thin blue horizontal line between cards showing where a dragged card will land.
- **Add column tile:** narrow pale grey panel at the far right of the row, with blue "+ Add column" text.
- **Card editor:** white panel sliding in from the right with title box, description box, assignee dropdown, blue filled Save button with white text, and grey outlined Cancel button. Red "Delete card" text sits bottom-left.
- **Assignee dropdown:** "Unassigned" at the top, then each team member with initials circle and name.
- **Team panel:** white panel from the top bar listing members with initials circles, and an "Add member" button in blue text.

## 3. How it is used

- **Click "+ Add card"** in a column: a text box opens in that column. Type a title and press Enter to add the card at the column's foot. Esc cancels.
- **Click a card:** opens the card editor on the right.
- **Edit in the editor and click Save:** title, description and assignee are saved. Cancel or Esc discards changes.
- **Drag a card (mouse) or press and hold, then drag (finger):** moves it to another column, dropped at the marker position.
- **Drag a card within its column:** changes its position in that column.
- **Drag a column header:** reorders columns.
- **Click a column name:** type a new name; Enter saves, Esc cancels.
- **Click a column's three-dot icon:** choose Rename or Delete column.
- **Right-click a card (long press on touch):** menu with Edit, Assign to, and Delete card.
- **Click "+ Add column":** type a name and press Enter; the column appears at the far right.
- **Click a member's initials in the top bar:** opens the Team panel; "Add member" then type a name and press Enter.
- **Click "Delete card" in the editor:** the button changes to "Click again to delete"; a second click deletes the card.

## 4. Scope

A team member opens the board and sees every column and card. They add a card to the first column with a title, open it to add a description and an assignee, and drag it through the columns as the work moves. A card in the last column is done. The board is the team's only board, and its only choice is how many columns it has and what they are called.

## 5. Things and their states

- **Board:** name, ordered columns, team members. One per team; exists from creation.
- **Column:** name, position. Created, renamed, reordered, or deleted when empty. Moved by dragging its header.
- **Card:** title (required), description (optional), assignee (optional), column, position within column. Created in a column; edited in the editor; moved by drag or menu; deleted by the two-click confirmation.
- **Team member:** name, initials. Added from the Team panel; can be assigned cards.

## 6. Rules

- A board always has at least one column; deleting the last one is refused.
- A column can be deleted only when empty; otherwise it is refused and the message "Move or delete its cards first" appears.
- A card needs a title; an empty title is refused and no card is created.
- A title is at most 200 characters; longer input is cut off at 200.
- A card is in exactly one column at a time.
- A card has at most one assignee; choosing "Unassigned" clears it.
- Only team members can be assigned; any other choice is refused.
- Column names must be unique within the board; a duplicate name is refused and the old name stays.
- A column name cannot be empty; an empty name is refused and the old name stays.
- Any team member can edit, move, assign, or delete any card.
- A card dropped outside any column returns to where it was.
- A card dropped in a column takes the position shown by the drop marker; cards below shift down.
- Esc or Cancel during any edit discards the change and nothing is saved.
- A deleted card is removed from its column and cannot be recovered.