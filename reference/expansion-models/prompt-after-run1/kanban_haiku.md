# Kanban Board

## 1. People and their journey

**Team member** is the only role. Every member of the team sees the whole board and can change any card or column.

- **Needs to see:** every column in order, every card in its column, and who holds each card.
- **Needs to decide:** what work exists, which stage each item is in, and who is doing it.
- **Journey:** opens the board, scans the columns, adds a card for new work or opens an existing one, assigns it, edits its details, and moves it across columns as the work advances. Work is done when its card sits in the last column.

## 2. How it looks

A kanban board: a wide, flat, light-grey page with vertical columns side by side, each holding a stack of white cards, like a wall of sticky notes sorted into stages.

- **Page background:** flat light grey (#F4F5F7) filling the window behind everything.
- **Board header:** white flat strip across the top showing the team name and the words "Board", with "Team" and "Add column" buttons at the right.
- **Team button:** grey text button in the header; opens the Team panel.
- **Add column button:** blue (#0C66E4) text button in the header; opens a name field at the end of the columns.
- **Column:** flat pale grey-blue (#EBECF0) panel with rounded corners, same height as the others, placed left to right in order.
- **Column header:** bold dark-navy (#172B4D) column name with the card count in grey beside it, and a three-dot menu icon at the right.
- **Column header while renaming:** name becomes a white field with a 2px blue outline; Enter saves it.
- **Column header while dragged:** the whole column lifts with a larger shadow and follows the pointer sideways.
- **Column drop marker:** a 4px blue vertical bar appears between columns while a column is dragged.
- **Card:** white flat rectangle with a thin grey (#DFE1E6) border and a soft shadow, showing its title in dark navy, with 8px gaps between cards.
- **Card assignee badge:** small filled circle at the card's bottom right showing the member's initials in white on that member's colour; unassigned cards show an empty grey circle with a dashed outline.
- **Card while dragged:** lifted with a larger shadow and 90% opacity, following the pointer.
- **Card while selected:** 2px blue (#0C66E4) outline around the card.
- **Card save failed:** red (#C9372C) line "Could not save" under the title; the card reverts to its last saved state after the message shows.
- **Drop position marker:** 3px blue (#0C66E4) horizontal line between cards in a column while a card is dragged over it.
- **Add card row:** grey text "+ Add card" at the bottom of each column; becomes a white text field with a blue outline when clicked.
- **Empty column:** dashed grey outline box inside the column reading "No cards" in grey text.
- **Card detail panel:** white flat panel covering the right third of the page, with a sunken grey divider on its left edge, showing the fields listed in section 3 and a close (X) icon at top right.
- **Delete button in panel:** red (#C9372C) text at the panel's bottom.
- **Confirmation box:** small white centred box with a dimmed grey overlay behind it, two buttons: "Delete" in red and "Cancel" in grey.
- **Team panel:** white flat panel on the right, listing each member as a coloured initials circle and name, with a name field and "Add" button at its top.
- **Column menu:** small white shadowed list under the three-dot icon with "Rename" and "Delete column".

## 3. How it is used

- **Click "+ Add card"** at a column's bottom, type a title, press Enter: card appears at the bottom of that column. Escape cancels.
- **Click a card:** opens the card detail panel.
- **Click the title in the panel,** type, then press Tab or click outside: title saves.
- **Click the description area in the panel,** type, then click outside: description saves.
- **Choose a name in the panel's Assignee list:** card is assigned to that member; choose "Unassigned" to clear it.
- **Choose a column in the panel's Column list:** card moves to the bottom of that column.
- **Drag a card within its column:** card takes the new position where the drop marker shows.
- **Drag a card into another column:** card lands at the drop marker's position.
- **Touch: long-press a card, then drag with the finger:** same as dragging with the mouse.
- **Right-click a card (touch: long-press):** menu with "Open", "Assign to", "Move to" and "Delete".
- **Click the Delete button in the panel,** then "Delete" in the confirmation box: card is removed; "Cancel" leaves it unchanged.
- **Click a column name:** renames it in place; Enter saves, Escape cancels.
- **Drag a column by its header (touch: long-press, then drag):** reorders columns; cards stay in their columns.
- **Click the three-dot icon on a column header,** then "Delete column": column is removed after confirmation, if it is empty.
- **Click "Add column" in the header,** type a name, press Enter: new column appears at the far right.
- **Click "Team" in the header,** type a member's name, click "Add": member joins the team list.
- **In the Team panel, click a member's "Remove":** member leaves the team and their cards become unassigned.
- **Press Escape or click the X:** closes the open panel or confirmation without saving unfinished edits.

## 4. Scope

A team member opens the team's board, sees all work by column, adds a card for new work, writes its title and description, assigns it to a member, and moves it through the columns as it progresses, editing or deleting it when needed. The board holds one team's work only. The product has no filters, no sort options and no board-size choices beyond the columns and cards themselves. Customer access, billing, reports and external integrations are not part of this product.

## 5. Things and their states

- **Board:** holds the team name and an ordered list of columns. One per team. Changed when columns are added, renamed, reordered or deleted.
- **Column:** holds a name, a position and an ordered list of cards. Active until deleted. Deleted only when empty.
- **Card:** holds a title, a description, one column, one position in that column, and at most one assignee. Created, then edited, moved, assigned or deleted. Its only removal is deletion.
- **Team member:** holds a name and a colour. Active while on the team; removed by "Remove" in the Team panel, which unassigns their cards.

## 6. Rules

- A column name must not be blank or repeat another column's name on the board; the change is refused and the old name stays.
- A card title must not be blank; a card with a blank title is not created.
- A card description holds up to 5,000 characters; longer text is refused and not saved.
- Every card is in exactly one column at exactly one position.
- A new card goes to the bottom of its column.
- A card moved by the panel's Column list goes to the bottom of the chosen column.
- A card has at most one assignee; choosing a name that is not a team member is refused.
- Removing a team member clears that member from every card they held; the cards stay where they are.
- A column that holds cards cannot be deleted; the request is refused with the message "Move or delete its cards first."
- The board always keeps at least one column; deleting the last column is refused.
- Reordering columns changes only their order; no card changes column.
- Each change saves as soon as it is made; if saving fails, the item shows "Could not save" and reverts to its last saved state.
- When two members edit the same card, the last saved change is kept; there is no locking.
- Escape cancels any edit in progress; nothing is saved.
- Deleting a card or column requires confirmation; "Cancel" leaves it unchanged.
- Only team members can see or change the board; no other person can view it.
- Each team has exactly one board.