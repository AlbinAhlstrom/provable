# Kanban Board

## 1. People and their journey
**Team member** (the only role). Every member has the same powers.
- **Needs to see:** every card, which column it sits in, and who it is assigned to.
- **Decides:** what work to add, who takes it, and when it moves to the next stage.
- **Path:**
  1. Opens the board. All columns appear left to right.
  2. Scans the columns and the faces on the cards.
  3. Adds a card or opens one to edit it.
  4. Assigns the card to themselves or a teammate.
  5. Drags the card to the next column as the work progresses.
  6. Leaves when the board matches reality.

## 2. How it looks
The product looks like a classic kanban board, as in Trello. Pale vertical columns stand side by side in one horizontally scrolling row. Each column holds a stack of white cards with titles. The board's background is a muted blue.

- **Page background:** solid muted blue, flat. It fills the window behind everything.
- **Top bar:** across the top of the page, dark navy, flat. It shows the board name in white on the left and a row of member avatars on the right.
- **Member avatar (top bar):** a small circle with initials in white, filled with the member's own colour. When selected as a filter it gets a thick white ring.
- **Board area:** below the top bar, transparent over the blue background. Columns sit left to right in it, and it scrolls sideways when they overflow.
- **Column:** light grey (#EBECF0), flat, with rounded corners and a fixed width. While it is being dragged, it tilts slightly and casts a shadow.
- **Column header:** at the top of each column. It shows the column name in bold dark grey, a card count in grey, and a "⋯" menu button. While the name is being edited, it becomes an outlined white text box.
- **Column drop gap:** a dark-grey outlined empty slot. It shows where a dragged column will land.
- **Card:** white and raised, with a soft shadow. It shows the title in dark text and, at its bottom right, the assignee's avatar.
  - On hover it turns light grey.
  - While dragged it tilts with a deeper shadow, and its old spot stays as a grey sunken placeholder.
- **Card description mark:** a small grey lines icon at the card's bottom left. It appears only when the card has a description.
- **Card drop gap:** a grey sunken slot the height of the dragged card. It shows where the card will land.
- **"+ Add a card" button:** at the bottom of each column, grey text, flat. On hover its background becomes a darker grey.
- **New card box:** an outlined white text area that replaces the add button. Below it sit a green "Add card" button and an "×" button. The green button is faded and does nothing while the box is empty.
- **"+ Add another column" tile:** after the last column, translucent white, flat, with white text. On hover it becomes more opaque.
- **Column menu:** a white raised popup under the "⋯" button. It contains "Rename" and "Delete column". "Delete column" is shown in red.
- **Card detail window:** a white, centred, shadowed panel over a dimmed page. It contains:
  - the title field;
  - an "Assignee" picker;
  - a "Description" box;
  - a red "Delete card" button;
  - an "×" close button.
- **Assignee picker list:** a white raised dropdown. It lists every member with their avatar, and "Unassigned" at the top. The current choice has a checkmark.
- **Delete confirmation:** a white raised small popup with a red "Delete" button and a grey "Cancel" button.
- **Member colours:** members get colours in join order: red, orange, yellow, green, teal, blue, purple, pink. After pink the sequence starts again with red.

## 3. How it is used
- **Add a card:** click "+ Add a card", type a title, then press Enter or click "Add card". The card appears at the bottom of that column.
- **Add several cards in a row:** press Enter in the new card box. The card is added and the box stays open for the next one.
- **Cancel adding a card:** click "×" or press Escape. The box closes and nothing is added.
- **Open a card:** click the card or tap it on a touchscreen. The card detail window opens.
- **Edit a title:** click the title in the detail window, type, then click away or press Enter. The change is saved.
- **Edit a description:** click the description box, type, then click away. The change is saved.
- **Assign a card:** click "Assignee" and choose a member or "Unassigned". The avatar on the card updates.
- **Close the detail window:** click "×", click the dimmed page, or press Escape.
- **Move a card:**
  - *Mouse:* drag the card to any column and position, then release. It drops into the gap.
  - *Touch:* long-press the card, then drag it and release.
- **Reorder cards within a column:** drag the card up or down in the same column.
- **Cancel a drag:** press Escape, or release outside any column. The card returns to where it was.
- **Delete a card:** in the detail window, click "Delete card", then click "Delete" to confirm.
- **Add a column:** click "+ Add another column", type a name, then press Enter.
- **Rename a column:** click its name, or choose "⋯" then "Rename". Type the new name, then press Enter.
- **Reorder columns:**
  - *Mouse:* drag the column by its header.
  - *Touch:* long-press the header, then drag.
- **Delete a column:** choose "⋯", then "Delete column", then confirm.
- **Filter by member:** click an avatar in the top bar. Other members' cards fade. Click the avatar again to clear the filter.
- **Scroll sideways:** use the scroll wheel with Shift, use the trackpad, swipe, or drag an empty area of the board.

## 4. Scope
**The loop:** a member creates a card, assigns it, and moves it through the columns until it reaches the last column.

**Forms** ask only for:
- a card title (required);
- a description (optional);
- an assignee (optional);
- a column name.

**Left out:**
- external or customer access;
- billing;
- reports and analytics;
- integrations;
- due dates, labels, comments, attachments and multiple boards.

## 5. Things and their states
- **Board:** one per team. It holds its name, its members, and its ordered columns. It has no states.
- **Column:** holds a name, its position, and its ordered cards. It is either present or deleted. A confirmed delete removes it.
- **Card:** holds a title, a description, an assignee, a column, and a position.
  - Its state is the column it sits in.
  - A drop moves it to another state, and a confirmed delete removes it.
  - Its assignment is either unassigned or assigned. Choosing an assignee changes it.
- **Member:** holds a name, initials and a colour. It belongs to the board.

## 6. Rules
- **Card titles:** a card title cannot be empty.
  - Adding a card with an empty title is ignored.
  - Clearing a title restores the previous one.
- **Column names:** a column name cannot be empty. An empty rename restores the old name.
- **Title length:** titles and column names are limited to 200 characters. Further typing is ignored.
- **Assignees:** a card has at most one assignee, and only a board member can be one.
- **Card order:** cards keep the order members give them. A drop places the card exactly at the gap shown.
- **Failed drops:** a drop outside any column changes nothing.
- **Column order:** columns keep the order members give them.
- **New cards and columns:** a new card goes to the bottom of its column, and a new column goes to the right end of the board.
- **Last column:** the board must keep at least one column. "Delete column" is unavailable when only one column remains.
- **Deleting a column:** deleting a column also deletes its cards. The confirmation states how many cards will be removed.
- **Confirmation:** deleting a card or a column needs confirmation. "Cancel" changes nothing.
- **Equal powers:** every member can do every action.
- **Who can see the board:** only board members can see the board. Anyone else is refused.
- **Saving and sharing:** changes save immediately and appear to the other members without reloading.
- **Card count:** the column card count always equals the number of cards in that column.
- **Filtering:** the member filter only fades cards. It never hides, moves or changes them.