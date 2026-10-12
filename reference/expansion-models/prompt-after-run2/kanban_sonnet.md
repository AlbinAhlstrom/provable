# A kanban board for a small team

## 1. People and their journey

**Team member** (the only role). Needs to see what work exists, its stage, and who is doing it. Arrives at the board, scans the columns, opens or creates a card, assigns it, drags it to the next column, and leaves once the board matches reality.

## 2. How it looks

A kanban board as people know it from Trello: a pale-grey page with a row of tall, rounded, side-by-side columns, each holding a vertical stack of white cards.

- **Page background**: fills the whole window, flat light grey (#EEF0F3); the board scrolls sideways when columns overflow.
- **Top bar**: fixed across the top, flat dark blue (#1F3A5F), white text; shows the board name at left and the member's name at right.
- **Column**: rounded panel, flat mid-grey (#DFE3E8), fixed width. Highlights blue-outlined while a card is dragged over it as a drop target.
- **Column header**: top of a column, bold dark-grey title with a card count at right. Title becomes an editable text box when clicked.
- **Column menu button**: three dots in the header, grey; darkens on hover and opens a menu with Rename and Delete.
- **Card**: white raised rectangle with a faint shadow, showing title, and below it an assignee circle. Hover deepens the shadow. While dragged it tilts slightly, with a strong shadow, and its original slot shows a dashed grey outline.
- **Assignee circle**: small round badge at the card's bottom right showing the member's initials. Each member has their own fixed colour: blue, green, orange, purple, red, teal. Unassigned shows an empty dashed grey circle.
- **Add card button**: flat text button at the foot of each column, "+ Add card", grey; darkens on hover. Opens an inline title box with Add and Cancel.
- **Add column**: a dashed-outline column-sized button at the right end of the row, reading "+ Add column".
- **Card detail panel**: centred white overlay over a dimmed page, with editable title, description box, assignee picker, Delete card button (red) and Close button.
- **Delete confirmation**: small white dialog with a red Delete button and a grey Cancel.

## 3. How it is used

- Click "+ Add card": type a title, press Enter or click Add; the card appears at the column's bottom. Escape cancels.
- Click a card: opens the detail panel.
- Edit title or description in the panel: saves when focus leaves the field.
- Choose a member in the assignee picker: the card shows their badge. Choose "Unassigned" to clear it.
- Drag a card (mouse, or touch after a long press) to another column or position: it drops there and the counts update.
- Drag a card within its column: reorders it.
- Click a column title: rename it; Enter saves, Escape cancels.
- Click "+ Add column": a new column is added at the right end, with its title ready to type.
- Drag a column header sideways: reorders columns.
- Column menu, Delete: asks for confirmation, then removes the column and its cards.
- Panel Delete card: asks for confirmation, then removes the card.
- Click outside the panel, press Escape, or click Close: closes the panel.

## 4. Scope

One board per team. A member opens it, creates columns for stages, adds cards, assigns them, edits them, and moves them across columns until done. There are no external users, billing, reports or integrations.

## 5. Things and their states

- **Board**: name, ordered columns. Always exists.
- **Column**: title, position, cards. States: normal, being renamed, being dragged.
- **Card**: title, description, assignee (optional), column, position. States: resting, being dragged, open in panel.
- **Team member**: name, initials, colour. Fixed list; can be assigned to cards.

## 6. Rules

- A card title is required; an empty title is refused and the card is not created.
- A column title is required; an empty rename reverts to the old title.
- A card belongs to exactly one column.
- A card has at most one assignee; only team members can be chosen.
- A dropped card keeps the exact position where it was released.
- Dropping outside any column returns the card to its original place.
- Deleting a column or card requires confirmation; Cancel changes nothing.
- Deleting a column deletes its cards.
- The last remaining column cannot be deleted; the option is greyed out.
- Titles are limited to 100 characters; extra typing is ignored.
- Description may be empty.