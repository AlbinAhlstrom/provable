### 1. Default Landing & Cold-Start Behavior

- Arrival shows the team's single board directly: top bar, then columns with cards. No welcome screen, no introduction, no sign-in.
- Active view is the Board. Columns load from `Board.columns`, cards from Card records, circles from `Board.team_members`.
- Loading: the top bar shows at once; the board area shows three grey (#E2E4E8) column-shaped placeholders with pulsing white card blocks. No text.
- Board name in the top bar comes from `Board.name`.
- Failed load: one line in the board area, "Couldn't load the board.", with a "Try again" button.
- Board with no columns: only the translucent "+ Add column" panel is shown, so the first column can be added at once.
- Empty column: shows only the "+ Add card" control, with no extra text.
- Team member selector with no members: it is still shown, and its list reads "No team members".
- Assignee dropdown with no members: it lists only "Unassigned".

### 2. Primary Navigation & View Structure

- One view: "Board". No tabs, no sidebar and no other pages.
- Top bar: `Board.name` in white at left, team member selector at right.
- Card dialog is a layer over the board, not a view. Closing it returns to the same scroll position.
- The board area scrolls sideways when columns overflow. On narrow screens columns keep their fixed width and the area scrolls.

### 3. Workflow Prerequisites & Form Ergonomics

- A card needs a column first. Columns always show "+ Add card", so nothing is shown before it can be used.
- Assigning needs team members. The dropdown lists only members and "Unassigned".
- New card title: text input, placeholder "Card title", Enter creates, Escape cancels. Empty Enter is refused and the field gets a red outline.
- Card dialog title: text input labelled "Title". An empty title is not saved, the field gets a red outline, and the previous title returns on close.
- Description: textarea labelled "Description", may be empty, saves on blur.
- Assignee: select labelled "Assignee", options are the members' names plus "Unassigned". It saves on choosing.
- New column name: text input, placeholder "Column name", Enter adds it, Escape cancels. An empty name is refused with a red outline, and duplicates are allowed.
- Column rename: the name becomes a text input with a blue outline. Enter saves, Escape restores. An empty name is refused with a red outline.
- Dropping a card outside any column does nothing and the card returns to its place.
- Deleting a card or a column asks for confirmation. Cancel changes nothing.
- Refusal is shown by the red outline alone, with no sentence.

### 4. Human Copy & Action Labeling

- **Seen**:
- "+ Add card": bottom of each column.
- "Card title": new card field placeholder.
- "+ Add column": panel after the last column.
- "Column name": new column field placeholder.
- "Title", "Description", "Assignee": card dialog labels.
- "Unassigned": first dropdown option.
- "Delete": card dialog, red text.
- "Close": card dialog.
- "Delete this card?": card confirmation heading.
- "Delete this column and its cards?": column confirmation heading, shown when the column holds cards.
- "Delete this column?": column confirmation heading, shown when the column is empty.
- "Delete" and "Cancel": confirmation buttons.
- "Delete column": item in the column menu.
- "Couldn't load the board.", "Try again": load failure.
- "No team members": empty member list.
- Column name, card count, card title, member names and initials come from records.
- **Spoken only**:
- "Column menu": the menu button on the column header.
- "Assigned to" followed by the member's name: assignee circle. "Unassigned": empty dashed circle.
- "Cards in column": count badge.
- "Drag column": column header drag area.
- "Team member": top bar selector.

### 5. Contextual Action Placement

- Add card: bottom of its column.
- Add column: after the last column.
- Rename column: click the name in the header.
- Column menu: a "⋯" button at the right of the column header, holding "Delete column".
- Reorder columns: drag the header.
- Move card: drag the card itself.
- Edit, assign and delete a card: in the card dialog, opened by clicking the card.
- Delete and Close sit at the dialog bottom, Delete at left and Close at right.
- The team member selector stays in the top bar.

### 6. Visual Direction

- **Feel**: Trello-style kanban board: a light grey page, tall grey columns, white raised cards, a quiet working tool.
- **Palette**: page #F1F2F4. Top bar #1F2A44 with white text. Column #E2E4E8. Card surface #FFFFFF. Text #1F2937. Count badge #CBD0D8 with text #4B5563. Accent blue #2563EB, used for the rename outline and focus. Drag-over column #D6E4FF. Add-card text #6B7280, hover background #CBD0D8. Add-column panel white at 40% opacity. Error red #DC2626. Unassigned dashed circle #9CA3AF. Dialog backdrop black at 50%. Member colours come from `TeamMember.colour`, with white initials.
- **Type**: `font-sans` for headings and body. Board name is 20px semibold in white. Column names are 14px bold. Card titles are 14px regular. Initials are 11px bold.
- **First screen**: the top bar is 48px high. Below it, columns sit side by side with 12px gaps and 12px padding, followed by the "+ Add column" panel. No hero and no intro text.
- **Form of the main view**: a horizontal kanban board. Columns are a fixed 272px wide and as tall as their content. Cards fill the column width and are as tall as their content. Assignee circles are 28px. The board scrolls sideways on narrow screens.
- **Shape and rhythm**: columns have 12px radius and cards 8px. Cards have a shadow of `0 1px 2px rgba(0,0,0,.2)`, deepening on hover. The dragged card tilts 3° and its original spot shows a 2px dashed grey outline. Cards are 8px apart and column padding is 8px. The dialog is 480px wide with 12px radius and a large shadow. Density is compact.

LAYOUT columns=1 rows=auto
TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2937 accent=#2563EB on_accent=#FFFFFF heading=sans