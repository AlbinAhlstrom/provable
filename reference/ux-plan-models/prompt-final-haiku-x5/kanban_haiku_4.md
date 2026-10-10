### 1. Default Landing & Cold-Start Behavior
- The application opens directly on the team's single board; no landing page, login splash or welcome screen.
- The board is the only view, shown with its columns and cards as they exist, never an empty screen with nothing to act on.
- Board.name fills the top bar at left; the loaded board shows its columns in Column.position order.
- While the board loads, the board area shows three grey skeleton columns (#E2E4E8) with no text.
- If the board fails to load, the board area shows "Couldn't load the board." with a "Try again" button beside it.
- If the board has no columns, the board area shows "No columns yet." and the "+ Add column" panel, which is the only control there.
- A column with no cards shows only the "+ Add card" control; no placeholder sentence is added.
- Team member records fill the team member selector in the top bar from TeamMember.name and TeamMember.initials.
- If team members fail to load, the selector shows "Members unavailable" and assignment is disabled with the same wording in the dropdown.
- If no team members exist, the selector reads "No members" and the assignee dropdown lists only "Unassigned".
- Cards with no assignee show the empty grey dashed circle; no text is added.

### 2. Primary Navigation & View Structure
- One view: the board. There are no tabs, menus across pages or secondary screens.
- The top bar holds the board name at left and the team member selector at right; nothing else.
- Columns sit left to right in Column.position order; the board area scrolls sideways when they overflow.
- Clicking a card opens the card dialog over the board; Close or Escape returns to the board unchanged.
- The card dialog shows Card.title, Card.description, the assignee dropdown, Delete and Close, in that order.
- Deleting a column is reached from the column's menu, which holds only "Delete column".
- Dragging is the only way to reorder cards and columns; no separate reorder screen exists.
- On a screen narrower than the board, the board keeps its column width and scrolls sideways; the top bar stays fixed.

### 3. Workflow Prerequisites & Form Ergonomics
- Adding a card needs a column; the "+ Add card" control appears in every column, so no prerequisite is hidden.
- Assignment needs a team member; with none, the assignee dropdown shows only "Unassigned" and no further hint is added.
- Card title is a required text input labelled "Title"; an empty value on save shows a red outline and the message "Enter a title."
- Card description is a textarea labelled "Description"; it may be empty and never shows an error.
- Assignee is a dropdown labelled "Assignee" listing "Unassigned" then each TeamMember.name.
- Column name is a required text input; an empty name is refused and its field shows a red outline with "Enter a column name."
- Renaming a column to an empty name restores the previous name and keeps the field in edit mode with the red outline.
- Card title and description save on blur; the dialog shows no save button.
- Pressing Escape in the add-card field creates nothing and closes the field.
- Dropping a card outside every column returns it to its original column and position without a message.
- Dragging a column header to a new place is refused with no message if dropped outside the column row.
- Duplicate column names are accepted without warning.

### 4. Human Copy & Action Labeling
**Seen**
- "+ Add card" — add-card control at the bottom of each column.
- "+ Add column" — panel after the last column.
- "Enter a title." — red-outlined card title field message.
- "Enter a column name." — red-outlined column name field message.
- "Unassigned" — first option in the assignee dropdown and clears the assignee.
- "Assignee" — label of the dropdown in the card dialog.
- "Title" — label of the card title field.
- "Description" — label of the description textarea.
- "Delete" — red text button in the card dialog.
- "Close" — button in the card dialog.
- "Delete card?" — confirmation heading; body "This card will be removed from the board." with "Cancel" and "Delete" buttons.
- "Delete column?" — confirmation heading; body "This column and its N cards will be removed." with "Cancel" and "Delete" buttons.
- "Delete column" — only item in the column menu.
- "Couldn't load the board." and "Try again" — load failure.
- "No columns yet." — empty board message beside "+ Add column".
- "Members unavailable" — team member selector when members fail to load.
- "No members" — team member selector when no members exist.

**Spoken only**
- "Team member selector" — name of the top bar control.
- "Column menu" — name of each column's menu button.
- "Card, [Card.title], assigned to [TeamMember.name]" or "Card, [Card.title], unassigned" — name of each card.
- "Assignee, [TeamMember.name]" or "Unassigned" — name of the assignee circle.
- "Column count, N cards" — name of the card-count badge.
- "Edit column name" — name of a column header in its editable state.

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of its own column, in the column it adds to.
- The add-card field appears in place of the "+ Add card" control at the column bottom.
- "+ Add column" sits after the last column, in the board area.
- The column menu sits at the top right of its column header and holds "Delete column".
- Renaming is triggered by clicking the column name in its header, in place.
- Delete and Close sit in the card dialog footer; Delete is left, Close right.
- The assignee dropdown sits in the card dialog beneath the description.
- The card title and description are edited in the card dialog only; cards on the board show title and assignee circle only.
- Card confirmation dialogs sit centred over the dimmed backdrop, beside the card dialog that triggered them.

### 6. Visual Direction
- **Feel**: A familiar Trello-style kanban board: calm, light and airy, with tall grey columns and white cards.
- **Palette**: Page background #F1F2F4; top bar and primary text on navy #1F2A44; column surface #E2E4E8; card surface #FFFFFF; secondary text #5B6478; accent blue #1F6FEB for focus outlines and the primary dialog button; drop-target highlight #D6E4FF; error red #D92D20; delete red text #D92D20; assignee circle colours come from TeamMember.colour; empty assignee circle border #9AA3B2; dashed drag outline #9AA3B2.
- **Type**: Sans-serif throughout (font-sans) for headings and body; column names and board name are bold at 16px; card titles are regular at 14px.
- **First screen**: The board itself fills the window below a 56px navy top bar; columns start at the top with 16px inner padding, so the first screen is the working board with no introductory text.
- **Form of the main view**: A Trello-style row of fixed-width columns. Each column is 272px wide, with 12px gaps between columns and 12px inner padding; columns grow in height to their content up to the window height and scroll inside. Each card is full column width minus padding, with an auto height. Columns keep their fixed 272px width at every window width and the board scrolls sideways when they overflow. An empty column keeps its full height and shows only "+ Add card" at its bottom.
- **Shape and rhythm**: Columns use 12px corner radius with no border; cards use 8px corner radius with a shadow of 0 1px 2px rgba(9,30,66,0.25), deepening to 0 4px 8px rgba(9,30,66,0.25) on hover; 8px spacing between cards; 16px between header and first card; the card dialog uses 12px radius and a 24px inner padding; assignee circles are 24px diameter; the density is comfortable, with 8px vertical rhythm.

LAYOUT columns=1 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#1F6FEB on_accent=#FFFFFF heading=sans