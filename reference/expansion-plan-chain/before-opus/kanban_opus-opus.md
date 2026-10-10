### 1. Default Landing & Cold-Start Behavior
- No entity is marked "shown to audience"; the Board record is created and edited by team members and fills the whole page.
- Arrival opens the single board view, ready to use, with no welcome text and no tutorial.
- First visit shows the board name from `Board.name`, then the columns from `Board.columns` in position order: To Do, In Progress, Done, all empty.
- An empty column shows only its column header with count "0" and the "+ Add a card" link. It has no other text.
- After the lanes comes the add-column tile, "+ Add another column".
- The top bar shows no member badges when `Board.members` is empty. The "Team" button is still shown.
- While the board loads, the top bar and three grey 272px lane outlines appear without text. Each outline is 120px tall.
- If the load fails, the lane area shows one centred white line, "Couldn't load the board.", and a white "Try again" button.
- When a save fails, the change is undone and a white toast at bottom centre reads "Couldn't save. Try again." It closes after 4 seconds.
- Changes made by other members appear in place without reloading and without any notice.
- With no members, the card window's assignee list shows "No team members yet. Add them from Team."

### 2. Primary Navigation & View Structure
- One view: "Board". It has no tabs and no navigation menu.
- The overlays open from their owners: the team panel from "Team", the card window from a card, the column menu from "⋯", and the confirm prompt from deletes.
- Only one overlay is open at a time. The confirm prompt stacks above the card window or the team panel.

### 3. Workflow Prerequisites & Form Ergonomics
- Assigning needs members. The empty assignee list points to Team with its one line. No other step has a prerequisite.
- Add-card box: a single-line text input with placeholder "Enter a title for this card…". Text stops at 200 characters.
- Confirming a blank card title does nothing and shows no message. The box stays open.
- Card title in the card window: a single-line input styled as a heading, 200 characters maximum. A blank title restores the previous title silently.
- Description: a textarea with placeholder "Add a more detailed description…", 5,000 characters maximum, 6 rows. It saves when you click away.
- Add-column box: a text input with placeholder "Enter column name…", 40 characters maximum. A blank name does nothing.
- Column rename and board rename: inline inputs. A blank name restores the old one, and Esc cancels.
- Member name: a text input with placeholder "Name". Pressing Enter with a blank name does nothing.
- Member colour: a row of eight 24px swatches as radio buttons. Blue is preselected, and the selected swatch has a 2px white ring plus dark outline.
- A duplicate member name is refused with red text "Already on the team" below the field. The text clears on the next keystroke.
- On the only remaining column, "Delete column" is greyed and unavailable. Clicking it does nothing.
- "Move left" is greyed in the first column and "Move right" is greyed in the last. Both do nothing when clicked.

### 4. Human Copy & Action Labeling
- **Seen:** "+ Add a card" (column foot), "Add card" (green button), "×" (cancel and close buttons).
- **Seen:** "+ Add another column" (tile), "Add column" (green button), "Enter column name…" (placeholder).
- **Seen:** "Enter a title for this card…" (add-card box placeholder).
- **Seen:** "Rename", "Move left", "Move right", "Delete column" (column menu items).
- **Seen:** "Team" (top bar button), "Add member" (team panel field heading), "Name" (member name placeholder).
- **Seen:** "Already on the team" (error below the member name field).
- **Seen:** "in list " followed by the column name (card window, under the title).
- **Seen:** "Description" (card window heading), "Add a more detailed description…" (description placeholder).
- **Seen:** "Members" (card window assignee heading), "Delete card" (card window red button).
- **Seen:** "No team members yet. Add them from Team." (empty assignee list).
- **Seen:** "Delete this column and its N cards?", "Delete this card?" and "Remove [name] from the team?" (confirm prompts).
- **Seen:** "Delete" (red confirm button for columns and cards), "Remove" (red confirm button for members), "Cancel" (grey button).
- **Seen:** "Couldn't load the board.", "Try again", "Couldn't save. Try again." (failure messages).
- **Seen:** the card count number beside each column name. It has no extra label.
- **Spoken only:** "Column actions" (⋯), "Has description" (≡), "Close" (×), "Remove [name]" (team ×).
- **Spoken only:** "Cancel adding" (add box ×), "Board name, edit" (board name), "Colour: teal" and the other colours (each swatch).
- **Spoken only:** each badge reads the member's full name. A drag announces "Moved to [column], position N".

### 5. Contextual Action Placement
- The "+ Add a card" link sits at the foot of every column. The add box opens in that same place.
- The "⋯" menu sits at the right of each column header. Double-clicking the name renames the column inline.
- Rename, assign, describe and delete for a card all live inside its card window. "Delete card" sits at the bottom left of the window.
- Member add and remove live in the team panel. Each "×" sits on that member's row.
- The add-column tile always sits last in the row of lanes.

### 6. Visual Direction
**Feel:** A familiar Trello-style corkboard of index cards: a deep blue backdrop with grey lanes of white cards. It reads as calm and dense.

**Palette:**
- Backdrop: #0B5394.
- Top bar: black/25 over the backdrop. Board name: white, bold.
- Column: #EBECF0. Column name: #172B4D. Count: #5E6C84.
- Card: #FFFFFF. Card on hover: #F4F5F7. Card text: #172B4D.
- Drop slot and column gap: #C1C7D0.
- Add-card link text: #5E6C84. Add-card link on hover: #DFE1E6.
- Add-column tile: white/20 with white text.
- Accent: green #5AAC44 on the "Add card" and "Add column" buttons, with white text.
- Delete: red #EB5A46 with white text. Cancel: #EBECF0 with #172B4D text. Greyed menu items: #A5ADBA.
- Overlay dim: black/50.
- Badge colours: red-500, orange-500, amber-500, green-600, teal-600, blue-600, purple-600, pink-500, each with white initials.

**Type:** All text is font-sans. The largest text is the board name at 18px bold. Column names are 14px semibold, cards 14px regular, and badge initials 11px bold.

**First screen:** Below the 48px top bar, the lanes start at the left with 12px padding. The board itself fills the screen, with no intro above it.

**Form of the main view:**
- The familiar kanban form: lanes are all 272px wide and 12px apart. Each lane's height grows with its cards, up to the viewport height minus 80px, then the lane scrolls internally.
- Cards fill the lane width minus 16px and are as tall as their content. Badges are 28px with a 4px overlap gap.
- On narrow screens, the row of lanes scrolls sideways and lanes stay 272px wide.
- The card window is 768px wide and becomes full-width with 8px margins below 800px.

**Shape and rhythm:**
- Columns: 12px radius, no shadow.
- Cards: 8px radius, with shadow 0 1px 0 #091E4240.
- Dragged items: rotated 3°, with shadow 0 8px 16px rgba(0,0,0,.25). A dragged column is also at 80% opacity.
- Popovers and dialogs: 8px radius, with shadow 0 8px 24px rgba(0,0,0,.2).
- Cards sit 8px apart and columns have 8px inner padding. The page is dense.

LAYOUT columns=3 rows=auto
TOKENS background=#0B5394 surface=#EBECF0 text=#172B4D accent=#5AAC44 on_accent=#ffffff heading=sans