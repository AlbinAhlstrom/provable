### 1. Default Landing & Cold-Start Behavior
- Opening the app shows the team's single board directly, with its columns and cards visible; no splash, no login, no landing page.
- Board name appears in the top bar at left; team member selector sits at right.
- Board.name fills the top-bar title; while loading, the title area shows a grey placeholder bar.
- Board.columns render as ordered columns; while loading, three grey placeholder columns with no cards are shown.
- Empty board (no columns): the board area shows one line "Add a column to start your board." beside the "+ Add column" panel.
- Empty column: shows only the "+ Add card" control; no message.
- Column count badge shows 0 when a column holds no cards.
- Team member list (TeamMember.name, initials, colour) fills the selector; while loading, the selector shows an empty grey circle.
- Team with no members: the selector reads "No team members yet" and the assignee dropdown shows only "Unassigned".
- Load failure: a single line in the board area reads "The board could not be loaded." with a "Try again" button.
- Card load failure is covered by the same board-level message; no partial state is shown.

### 2. Primary Navigation & View Structure
- One view only: the board. No tabs, no menus, no separate pages.
- The card dialog is a modal over the board, opened by clicking a card.
- The column menu (⋯ on the column header) holds one item, "Delete column".
- Board area scrolls sideways when columns overflow; the top bar stays fixed.
- On narrow screens, columns keep their fixed width and the board area scrolls sideways; the top bar stays fixed.
- Team member selector opens a list of team members; choosing one sets the active member for "creator" context only, shown in the selector.

### 3. Workflow Prerequisites & Form Ergonomics
- Card creation: the "+ Add card" control opens a single-line title field at the column bottom; no other fields are needed first.
- Assignee dropdown is available only in the card dialog, after the card exists; it lists "Unassigned" first, then each TeamMember.name.
- Column rename: clicking the column name switches it to an input with a blue outline; Enter saves, Escape restores the old name.
- Column add: "+ Add column" opens a name input in the panel; Enter adds the column at the end.
- Card title field: text input labelled "Title"; error message none beyond red outline on empty submission.
- Card description: textarea labelled "Description", optional, may be empty.
- Assignee field: select labelled "Assignee", options from TeamMember.name, default "Unassigned".
- Delete actions do not open until the confirmation step is shown; cancelling changes nothing.
- A button that cannot act (e.g. "+ Add card" in no-column state) is not shown; no disabled-state explanations are needed.

### 4. Human Copy & Action Labeling
**Seen:**
- "+ Add card" — column bottom, add control.
- "+ Add column" — panel after last column.
- "Add card" (submit button in the card title field row) — beside the title input.
- "Title" — card dialog label.
- "Description" — card dialog label.
- "Assignee" — card dialog label.
- "Unassigned" — first option in the assignee select.
- "Delete" — card dialog, red text.
- "Close" — card dialog footer.
- "Delete card?" with "This card will be removed." and buttons "Delete" and "Cancel" — confirmation for card deletion.
- "Delete column?" with "This column and its N cards will be removed." and buttons "Delete" and "Cancel" — column deletion confirmation.
- "Delete column" — column menu item.
- "Add a column to start your board." — empty-board line.
- "The board could not be loaded." with "Try again" — load failure.
- "No team members yet" — selector when empty.

**Spoken only:**
- Column menu button: "Column options".
- Assignee circle: "Assigned to [TeamMember.name]" or "Unassigned".
- Board card: "[Title], in [column name]".
- Column header: "Column [name], [N] cards".
- Team member selector: "Team member".
- Close icon controls: "Close".

### 5. Contextual Action Placement
- "+ Add card" sits at the bottom of each column.
- Card title input opens in place at the column bottom, replacing the add control until Enter or Escape.
- Column menu (⋯) sits at the right of the column header.
- Column name edit happens in place in the header.
- Card dialog holds Title, Description, Assignee, Delete and Close.
- Card deletion confirmation appears inside the card dialog.
- Column deletion confirmation appears over the board, centred.
- "+ Add column" sits after the last column.
- Team member selector sits at the top bar right.

### 6. Visual Direction
- **Feel**: a familiar Trello-style kanban board: light, calm, flat, with raised white cards.
- **Palette**: page background #F1F2F4; surface (cards) #FFFFFF; column surface #E2E4E8; text #1F2A44; accent #1F2A44 for top bar and primary buttons; drop highlight #D6E4FF; delete text #DC2626; error outline #DC2626; dashed empty assignee and drag placeholder #9CA3AF; badge background #CBD5E1 with text #1F2A44; add-card hover background #CDD1D8; Add column panel background rgba(255,255,255,0.4); primary text on accent #FFFFFF.
- **Type**: `font-sans` for headings and body; column names 14px bold; board name 18px bold white; card titles 14px regular.
- **First screen**: top bar across the full width, then the board with columns side by side starting at the top-left; no text introduces it.
- **Form of the main view**: Trello-style columns of equal fixed width (272px), each a vertical stack of cards with 8px gaps; columns separated by 12px gaps. Repeated parts are fixed size: columns 272px wide, cards 272px wide, height by content. Whole board keeps no fixed proportions; it scrolls sideways. On narrow screens, columns keep 272px width and the board scrolls horizontally.
- **Shape and rhythm**: columns radius 12px, cards radius 8px with shadow `0 1px 2px rgba(0,0,0,0.12)` deepening to `0 4px 8px rgba(0,0,0,0.16)` on hover; column padding 8px; card padding 8px 12px; section spacing 12px; assignee circle 24px diameter; medium density.

LAYOUT columns=4 rows=auto

TOKENS background=#F1F2F4 surface=#FFFFFF text=#1F2A44 accent=#1F2A44 on_accent=#FFFFFF heading=sans