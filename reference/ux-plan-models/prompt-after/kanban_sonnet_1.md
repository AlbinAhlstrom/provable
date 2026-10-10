### 1. Default Landing & Cold-Start Behavior

- Arrival opens the team's single board directly: top bar, columns and cards, ready to use. No welcome screen, no introduction text.
- Entities shown to audience: Board (name, columns) and TeamMember (name, initials, colour). Cards and columns are records loaded from the API.
- While loading: top bar shows with the board area holding three grey column-shaped placeholders (#E2E4E8, 288px wide) with pale bars for cards. No text.
- Load failed: the board area shows "Couldn't load the board." with a "Try again" button; the top bar stays.
- Board with no columns: board area shows only the "+ Add column" panel. No extra guidance line.
- Empty column: shows only the "+ Add card" control, as specified.
- Team member selector with no TeamMember records: it lists nothing; the assignee dropdown offers only "Unassigned".
- Team member selector loading: shows an empty pale placeholder pill in the top bar; failed load shows "Members unavailable".

### 2. Primary Navigation & View Structure

- One view: the board, named by Board.name in the top bar at left. No tabs, no side navigation.
- Card dialog is an overlay on the board, not a view; Close returns to the board unchanged.
- Team member selector sits at the right of the top bar, as specified.
- Column menu (a "⋯" button in the column header) holds "Delete column".

### 3. Workflow Prerequisites & Form Ergonomics

- No step needs another first; every control is available as soon as the board shows.
- Assignee dropdown is only meaningful with members; it lists TeamMember.name entries, so non-members cannot be chosen.
- Empty card title (new or edited): refused, field outlined red (#DC2626), no message text. On edit blur the previous title is restored after the outline shows.
- Empty column name (new or rename): refused with a red outline; the column is not added or renamed. Escape cancels either.
- New card title: single-line text input at column bottom, label for screen readers "Card title", placeholder "Card title". Enter creates, Escape cancels.
- Card dialog title: text input, label "Title". Description: textarea of 5 rows, label "Description". Both save on blur.
- Assignee: select labelled "Assignee", first option "Unassigned", then each TeamMember.name.
- New column name: text input, placeholder "Column name", Enter adds, Escape cancels.
- Delete actions open a confirmation; Cancel changes nothing, and a drop outside any column silently returns the card.

### 4. Human Copy & Action Labeling

- **Seen**
- "+ Add card": button at the bottom of each column.
- "Card title": placeholder in the new card field.
- "+ Add column": panel after the last column.
- "Column name": placeholder in the new column field.
- "Title", "Description", "Assignee": dialog field labels.
- "Unassigned": first option in the assignee dropdown.
- "Delete": red text in the card dialog.
- "Close": button in the card dialog.
- "Delete this card?" with "Delete" and "Cancel": card confirmation.
- "Delete column": item in the column menu.
- "Delete this column and its cards?" with "Delete" and "Cancel": column confirmation. Wording for an empty column: "Delete this column?"
- "Couldn't load the board." and "Try again": load failure.
- "Members unavailable": member selector load failure.
- Board.name: top bar title. Column.name: column header. Card count: badge number.
- **Spoken only**
- "Column menu": the "⋯" button.
- "Unassigned card": the empty dashed circle.
- "Assigned to" followed by TeamMember.name: the assignee circle.
- "Drag column": the column header grip.
- "Team member": the top bar selector.
- Dialog closes via "Close"; backdrop click does the same.

### 5. Contextual Action Placement

- Add card: bottom of its column. Add column: after the last column.
- Rename column: click the name in the header. Reorder: drag the header sideways.
- Delete column: the column's "⋯" menu in the header.
- Edit, assign and delete a card: in the card dialog, opened by clicking the card.
- Delete and Close: at the bottom of the dialog, Delete at left and Close at right.
- Move a card: drag the card itself.

### 6. Visual Direction

- **Feel**: A Trello-style kanban board: light grey page, mid-grey columns, white raised cards, navy top bar.
- **Palette**: page #F1F2F4; top bar #1F2A44 with white text; column #E2E4E8; card surface #FFFFFF; text #1F2937; secondary grey text #6B7280; count badge #CBD0D6 with #374151 text; drag-over column #D6E4FF; accent blue #2563EB for the editing outline and focus; add-card hover #CBD0D6; add-column panel white at 40% opacity (hover 60%); error and Delete red #DC2626; dashed outlines #9CA3AF; dialog backdrop black at 50%. Member colours come from TeamMember.colour with white initials.
- **Shared surfaces**: Member colours sit on white cards only, so no middle-tone surface is needed.
- **Type**: font-sans throughout. Board name 20px semibold. Column names 14px bold. Card titles 14px regular. Initials 11px bold.
- **First screen**: a 56px navy top bar with Board.name at left and the team member selector at right. Below it the columns sit side by side on the grey page, followed by the "+ Add column" panel. Nothing is written above the board.
- **Form of the main view**: the familiar Trello board. Columns are a fixed 288px wide with 12px gaps, as tall as their content with a maximum of the window height minus the bar. Cards are full column width, each as tall as its content. The board scrolls sideways when columns overflow. Columns scroll vertically inside themselves. The dialog is 560px wide and narrows to fit small screens.
- **Shape and rhythm**: columns have 12px radius and 8px padding. Cards have 8px radius, shadow-sm (hover shadow-md), 8px gap and 12px padding. The assignee circle is 28px. The page is dense and compact, with 16px outer padding.

LAYOUT columns=3 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2937 accent=#2563EB on_accent=#FFFFFF heading=sans