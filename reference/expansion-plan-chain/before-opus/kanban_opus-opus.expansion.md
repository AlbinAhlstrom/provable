# Kanban Board

## 1. People and their journey

**Team member** is the only role. Every member has the same abilities.

- **Needs to see:** every column in order, every card in each column, and who is assigned to each card.
- **Decides:** what work to add, which stage it is in, and who takes it.
- **Path:**
  1. Opens the board, which loads ready to use.
  2. Scans the columns.
  3. Adds a card to the first column.
  4. Opens a card to write its description and assign members.
  5. Drags cards rightward as the work progresses.
  6. Leaves when the board matches reality.
- **Occasionally:** adds, renames, reorders or deletes columns, and adds teammates.

## 2. How it looks

The Kanban Board looks like a familiar card board, like a corkboard of index cards:

- A coloured backdrop with a bar along the top.
- A row of grey vertical lanes running left to right, one lane per stage, each headed by its name.
- Inside each lane, a stack of white rounded cards.
- On each card, its title and small round initial badges for the people doing it.
- When the lanes overflow the window, the row of lanes scrolls sideways.

The parts, in order:

- **Backdrop:** full-page flat deep blue (#0B5394) behind everything.
- **Top bar:** full-width strip across the top, translucent darker blue, flat. Shows the board name in white bold text at left. Shows the team's member badges and a white "Team" button at right.
- **Board name:** white bold text in the top bar. While being edited, it becomes a white outlined text box with dark text.
- **Member badge:** 28px circle in the member's chosen colour, showing white initials. The available colours are red, orange, amber, green, teal, blue, purple and pink.
- **Team panel:** white raised, shadowed panel that drops below the "Team" button. Lists each member's badge and name, a remove "×" beside each member, and an "Add member" field.
- **Lane area:** sits below the top bar, flat and transparent over the backdrop. Lanes sit 12px apart and the area scrolls sideways when full.
- **Column:** 272px wide, light grey (#EBECF0), rounded, flat. Its height grows with its cards, then the column scrolls internally.
  - While dragged: tilted slightly, shadowed, semi-transparent.
  - Its gap is shown as a darker grey slot.
- **Column header:** bold dark grey name at the top of the column, with a grey count of cards beside it and a "⋯" menu button at the right.
  - While renaming, the name becomes an outlined text box.
- **Column menu:** white shadowed popover with three items: "Rename", "Move left", "Move right" and "Delete column".
  - Delete is shown in red.
  - Move left is greyed and unavailable in the first column. Move right is greyed and unavailable in the last column.
- **Card:** white, rounded, with a light shadow. Shows the title in dark text, a "≡" mark if a description exists, and assignee badges at the bottom right.
  - On hover: light grey.
  - While dragged: tilted and with a deeper shadow.
- **Drop slot:** a darker grey card-sized gap that appears where a dragged card will land.
- **Add-card link:** grey "+ Add a card" text at the bottom of each column.
  - On hover: darker grey background.
  - When clicked, it becomes a white text box with a green "Add card" button and a "×" button.
- **Add-column tile:** translucent white lane at the end of the row, reading "+ Add another column" in white.
  - When clicked, it becomes a name box with a green "Add column" button.
- **Card window:** centred white shadowed dialog over a dimmed backdrop. It contains:
  - an editable title;
  - the current column name;
  - a description box;
  - an assignee list with checkboxes;
  - a red "Delete card" button;
  - a "×" close button.
- **Confirm prompt:** small white dialog asking "Delete this column and its N cards?" or "Delete this card?". Has a red "Delete" button and a grey "Cancel" button.
- **Empty column:** shows only its header and the add-card link.

## 3. How it is used

**Cards**
- **Add a card:** click "+ Add a card", type a title, then press Enter or click "Add card". The card joins the column's bottom and the box stays open for the next card. Press Esc to cancel.
- **Move a card:** with a mouse, drag the card to any position in any column. With a finger, long-press the card, then drag. The other cards shift to show the drop slot. Releasing places the card there.
- **Cancel a drag:** release the card outside every column, or press Esc. The card returns to its original place.
- **Open a card:** click or tap it to open the card window.
- **Edit a card title:** click the title in the card window, type, then press Enter or click away to save. An empty title restores the previous title.
- **Edit a description:** click the description box, type, then click away to save.
- **Assign members:** tick or untick members in the card window. Their badges appear on or disappear from the card immediately.
- **Close the card window:** click "×", click the dimmed backdrop, or press Esc.
- **Delete a card:** click "Delete card", then confirm. The card disappears.

**Columns**
- **Add a column:** click "+ Add another column", type a name, then press Enter. The column appears last.
- **Rename a column:** double-click the column name, or choose "Rename" from the column menu. Type, then press Enter to save. Press Esc to cancel.
- **Reorder columns:** drag a column by its header. With a finger, long-press the header, then drag. You can also choose "Move left" or "Move right" from the column menu.
- **Delete a column:** choose "Delete column" from the column menu, then confirm. The column and all its cards are removed.

**Board and team**
- **Rename the board:** click the board name, type, then press Enter.
- **Manage the team:**
  - Click "Team" to open the team panel.
  - To add a member, type a name, pick a colour, then press Enter.
  - To remove a member, click "×" beside them, then confirm.
  - Click outside the panel to close it.

## 4. Scope

The loop: add cards, describe them, assign members, and move them through columns until they are done.

The board starts with three columns: To Do, In Progress and Done. Columns can be added, renamed, reordered and deleted.

Each form asks only for what is needed:
- a card asks for its title;
- a column asks for its name;
- a member asks for a name and a colour.

There is one board per team. All members see changes on the board.

## 5. Things and their states

- **Board:** holds a name, its ordered columns and the team's members. It is always active.
- **Column:** holds a name and a position. It moves from created, to renamed or moved any number of times, to deleted. Deleting it removes its cards.
- **Card:** holds a title, a description, its column, its position within the column and its assignees. It moves from created (at the bottom of a column), to moved or edited, to deleted.
- **Member:** holds a name, initials and a colour. It moves from added to removed. Removing a member unassigns them from every card.

## 6. Rules

**Cards**
- A card's title must contain at least one non-space character. Adding a blank title is ignored and nothing changes.
- Titles are limited to 200 characters and descriptions to 5,000 characters. Typing beyond the limit is ignored.
- A card belongs to exactly one column at one position.
- Dropping a card renumbers the positions in both the source and target columns with no gaps.
- Dropping a card outside every column returns it unchanged.
- A card may have zero or more assignees, each a current member, and each listed at most once.
- Deleting a card requires confirmation. Cancelling changes nothing.

**Columns**
- A column name must be non-blank and at most 40 characters. A blank rename restores the old name.
- Column names may repeat.
- The board must keep at least one column. Delete is unavailable on the last remaining column.
- Deleting a column requires confirmation and deletes all its cards.
- Moving the first column left, or the last column right, is unavailable.

**Members**
- A member name must be non-blank. Initials are the first letters of the first two words of the name.
- Adding a member whose name exactly matches an existing member's name is refused, with "Already on the team" shown below the field.
- Removing a member requires confirmation and clears their assignments from every card.

**Board**
- A board name must be non-blank. A blank rename restores the old name.
- Every change is saved immediately and appears for all members without reloading.