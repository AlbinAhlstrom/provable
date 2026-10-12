# A kanban board for a small team

## 1. People and their journey
**Team member** (the only role). Needs to see what work exists, its stage, and who owns it; decides what to start, hand over or finish; moves cards to show progress.
Path: open the board → scan columns → create or open a card → edit, assign, move it → see the board reflect the change.

## 2. How it looks
A kanban board: a full-width page of tall vertical columns side by side, each holding a stack of white cards, like Trello-style boards.

- **Page backdrop**: fills the whole browser window, flat medium blue (#0079BF); nothing else sits behind the board.
- **Top bar**: thin strip across the top, flat darker blue (#026AA7), white text with the board name on the left and the signed-in member's initials circle on the right.
- **Column area**: below the top bar; columns sit left to right and scroll sideways when they overflow.
- **Column**: flat light grey (#EBECF0) rounded panel, 272px wide. While a card is dragged over it, it darkens to #DFE1E6.
- **Column header**: top of the column; bold dark-grey title and a small grey card count. Turns into a text box while renamed.
- **Card**: white, raised with a faint shadow, rounded, showing title and assignee initials circles. Hover: shadow deepens. Dragged: tilts slightly with a stronger shadow.
- **Card placeholder**: a flat grey (#C1C7D0) empty slot where the dragged card will land.
- **Assignee circle**: small round chip at the card's bottom right; each member has a fixed colour: red, orange, green, purple, teal, pink, in order of joining. It shows two-letter initials in white.
- **Unassigned mark**: a dashed grey outline circle on the card.
- **Add-card button**: bottom of each column, flat grey text "+ Add a card"; hover darkens the background. Pressed it becomes a title box with a blue "Add" button and a grey "×".
- **Add-column panel**: after the last column, translucent white tile "+ Add another column"; pressed becomes a name box with "Add" and "×".
- **Card dialog**: centred white panel over a 50% black dim layer, with title box, description box, assignee list with checkboxes, column name, and "Delete card" in red text. Closed by "×", Escape or clicking the dim layer.
- **Delete confirmation**: small white dialog, with a red "Delete" button and a grey "Cancel" button.
- **Refusal message**: a thin red line under the box that caused it.

## 3. How it is used
- Click "+ Add a card", type a title, press Enter or "Add": the card appears at the column bottom.
- Click a card: the card dialog opens.
- Edit title or description in the dialog: changes save when the box loses focus.
- Tick or untick a member in the dialog: assigns or unassigns them.
- Drag a card (mouse, or touch after a short hold) to any column position: it moves and the slot shows where it lands.
- Drag a column header sideways: the column is reordered.
- Click a column title: rename it; Enter saves, Escape cancels.
- Click "+ Add another column", name it, press Enter: a column is appended at the right.
- Open the column's "⋯" menu (click, or long press) and choose "Delete column": confirmation appears first.
- In the card dialog click "Delete card": confirmation appears first.
- Escape while typing in an add box: closes it, discarding the text.

## 4. Scope
One loop: view the single team board, create columns, add cards, describe and assign them, move them across columns as work progresses, and remove what is no longer needed. Customer access, billing, reports and integrations are out.

## 5. Things and their states
- **Board**: name, ordered columns. One per team.
- **Column**: name, position, ordered cards. States: normal, being renamed, being dragged.
- **Card**: title, description (may be empty), assignees, column, position. States: resting, being dragged, open in dialog.
- **Member**: name, initials, colour. Active only.

## 6. Rules
- Card title is required, 1–120 characters; empty is refused and the card is not created.
- Column name is required, 1–40 characters; empty is refused and the old name is kept.
- Description is up to 5,000 characters; excess is refused.
- A card lives in exactly one column.
- A card may have zero or many assignees; each member is assigned at most once.
- Dropping a card outside any column returns it to its original place.
- Moving a card changes only its column and position; other cards keep their order.
- Deleting a non-empty column asks for confirmation and states the number of cards that will be deleted.
- The last remaining column cannot be deleted; the action is ignored.
- Column names need not be unique.
- Deleted cards and columns are gone permanently.
- Any team member may edit any card or column.