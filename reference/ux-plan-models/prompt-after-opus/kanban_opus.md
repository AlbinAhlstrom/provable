### 1. Default Landing & Cold-Start Behavior
- The app opens straight onto the team's single board, `Board.name`. It is the only view and needs no choosing.
- A new board is created with three columns: "To do", "Doing" and "Done". Nobody ever arrives at an empty board.
- While the board loads, three column outlines in #E2E4E8 stand side by side, each 272px wide and 120px tall, with no text.
- If the load fails, the board area shows one centered line, "Couldn't load the board.", and a "Try again" button.
- Columns come from `Board.columns`, ordered by `Column.position`. Each shows `Column.name` and its card count.
- Cards come from Card records, grouped by `Card.column_id` and ordered by `Card.position`. Each shows `Card.title` and the assignee circle.
- The assignee circle shows `TeamMember.initials` on `TeamMember.colour`, found through `Card.team_member_id`.
- A column with no cards shows only "+ Add card", as the specification states. It carries no extra text.
- If every column is deleted, the board shows only the "+ Add column" panel at the left.

### 2. Primary Navigation & View Structure
- There is one view, the Board. It has no tabs and no navigation.
- The top bar shows `Board.name` at left and the team member selector at right.
- The card dialog opens over the Board and is the only overlay besides the confirmations.

### 3. Workflow Prerequisites & Form Ergonomics
- A card needs a column first. "+ Add card" exists only inside columns, so this needs no hint.
- Add-card field: a single-line text input, placeholder "Card title". Enter creates the card. Escape cancels.
- Add-card field with an empty title on Enter: the card is refused, the field gets a red outline and stays open. No message is shown.
- Dialog title field: a text input labelled "Title". If it is empty on blur, it outlines red and the previous title is kept.
- Dialog description field: a textarea labelled "Description", 6 rows tall. An empty description saves.
- Dialog assignee field: a select labelled "Assignee". The first option is "Unassigned", then `TeamMember.name` for each member.
- Add-column field: a text input, placeholder "Column name". Enter adds the column. Escape cancels. An empty name gets a red outline and nothing is added.
- Rename field: Enter saves. An empty name gets a red outline and is refused. Escape restores the old name.
- A card dropped outside every column glides back to its original place, with no message.
- Team member selector: a select of `TeamMember.name` options, showing the chosen member's circle. It sets who "You" is and adds no further UI.

### 4. Human Copy & Action Labeling
- **Seen**, top bar: `Board.name` and the selector label "You".
- **Seen**, column: `Column.name`, the count badge as a number, "+ Add card", and the "Card title" placeholder.
- **Seen**, add column: "+ Add column", the "Column name" placeholder, and the button "Add column".
- **Seen**, column menu: the item "Delete column".
- **Seen**, column confirmation: "Delete column "`Column.name`" and its N cards?" with the buttons "Delete" and "Cancel".
- **Seen**, column confirmation when the column holds no cards: "Delete column "`Column.name`"?"
- **Seen**, card dialog: the labels "Title", "Description" and "Assignee", the option "Unassigned", and the buttons "Delete" and "Close".
- **Seen**, card confirmation: "Delete this card?" with the buttons "Delete" and "Cancel".
- **Seen**, load error: "Couldn't load the board." and "Try again".
- **Spoken only**: the column menu button is "Column options".
- **Spoken only**: the assignee circle is "Assigned to `TeamMember.name`", or "Unassigned".
- **Spoken only**: a card is "`Card.title`, open card". The count badge is "N cards". The backdrop is "Close dialog".
- **Spoken only**: the loading outlines are "Loading board".

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of each column. The new-card field opens in that same spot.
- The "⋯" column menu sits at the right end of the column header, beside the count badge.
- Rename happens in place, on the column name itself.
- Card edit, assign and Delete all live in the card dialog. Delete is at bottom left; Close is at bottom right.
- "+ Add column" sits after the last column. Its field opens in that same panel.
- Confirmations are small centered panels over the backdrop, with "Delete" in red #C9372C at right.

### 6. Visual Direction
**Feel**: A Trello-style board, exactly as the specification describes it. It is calm, flat and instantly familiar.

**Palette**:
- Page background: #F1F2F4.
- Top bar: #1F2A44, with white text.
- Column: #E2E4E8. Column under a dragged card: #D6E4FF.
- Card: #FFFFFF.
- Text: #172B4D. Muted grey text for "+ Add card" and the count badge: #626F86.
- Count badge background: #D0D4DB.
- "+ Add card" hover background: #D0D4DB.
- Accent for focus outlines and the "Add column" button: #0C66E4, with white text on it.
- Error outline and Delete text: #C9372C.
- Dashed placeholder and empty assignee circle: #A5ADBA.
- "+ Add column" panel: rgba(255,255,255,0.5).
- Dialog backdrop: rgba(9,30,66,0.54).
- Initials: white, on `TeamMember.colour`.

**Type**:
- `font-sans` carries everything.
- The board name in the top bar is the largest text: 18px, bold.
- Column names are 14px semibold. Card titles are 14px regular. The dialog title field is 20px semibold.

**First screen**: The top bar, 48px tall, sits above the board area, which is ready to use. Columns start 12px from the left, with nothing written above them to introduce the board.

**Form of the main view**:
- Kanban columns stand side by side. Every column is a fixed 272px wide, with a 12px gap between columns, and grows to fit its cards.
- The column header is 40px tall.
- Cards are full column width minus 8px padding each side. Each card's height follows its title, with a minimum of 56px.
- The assignee circle is 24px.
- On narrow screens the board scrolls sideways and columns stay 272px. The dialog becomes full-width under 600px.

**Shape and rhythm**:
- Columns have 12px corner radius. Cards have 8px radius and a 0 1px 1px rgba(9,30,66,0.25) shadow, which deepens to 0 4px 8px on hover.
- A dragged card tilts 3°.
- Cards sit 8px apart. The dialog is 560px wide with 12px radius and 24px padding.
- The page is dense.

LAYOUT columns=3 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#172B4D accent=#0C66E4 on_accent=#ffffff heading=sans