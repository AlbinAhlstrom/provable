# A kanban board for a small team

## 1. People and their journey

**Team member** (the only role). Everyone on the team has the same abilities.
- Needs to see: which work exists, which column each card is in, who is assigned.
- Decides: what to add, who does it, when it moves on.
- Path: open the board, scan the columns, create or open a card, assign it, drag it onward, and finish when the card reaches the last column.

## 2. How it looks

A kanban board as people know it from Trello-style tools: a full-width row of tall, side-by-side column lanes holding stacked white cards, on a soft coloured backdrop.

- **Page background**: flat pale blue-grey (#E9EEF3), filling the window behind everything.
- **Top bar**: flat dark navy (#1F2A44) strip across the top, with the board name in white at left and the current member's name at right.
- **Board area**: sits below the top bar and scrolls sideways when columns overflow. It holds the columns in order, left to right.
- **Column**: sunken light-grey (#DCE2E9) lane with rounded corners and a fixed width. It shows a header and its cards. While a card is dragged over it, it turns pale blue (#CFE3FA) with a dashed blue outline.
- **Column header**: top of each column, with the bold dark-grey column name and a count of its cards. Clicking the name turns it into a text field.
- **Card**: raised white rectangle with a soft shadow, showing the title in dark text and the assignee's initials in a coloured circle at bottom right. Hovering deepens the shadow. While dragged it tilts slightly, with a stronger shadow. Its original spot shows a faint grey (#C5CDD6) placeholder.
- **Unassigned card**: shows a dashed grey empty circle in place of initials.
- **Assignee circle**: one fixed colour per member, from this list in order of joining: blue #3B82F6, green #22A06B, orange #F28C28, purple #8B5CF6, red #E5484D, teal #0EA5A4, pink #DB4F9A, brown #A0714F.
- **Add-card control**: at the foot of each column, a flat text button reading "+ Add card". Clicking it opens an inline title field with "Add" and "Cancel" buttons.
- **Add-column control**: a flat dashed-outline lane after the last column reading "+ Add column". Clicking it opens an inline name field.
- **Card detail panel**: white panel sliding in from the right over a dimmed backdrop (50% black). It has a title field, a description area, an assignee dropdown, a column dropdown, and "Delete card" in red text. A "Close" cross sits at its top right.
- **Empty column**: shows light grey italic text "No cards" in its body.
- **Confirmation dialog**: centred white raised box on the dimmed backdrop, with a message, a grey "Cancel" button and a red "Delete" button.
- **Validation message**: small red (#C62828) text under a field that has an error.

## 3. How it is used

- Click "+ Add card" in a column, type a title, press Enter or click "Add": a card appears at the bottom of that column.
- Press Escape or click "Cancel" in the inline form: the form closes and nothing is created.
- Click a card: the detail panel opens.
- Edit the title or description in the panel: changes save as you leave the field.
- Choose a member in the assignee dropdown: the card shows their initials; choose "Unassigned" to clear it.
- Drag a card with the mouse to another column or position: it drops there and the others shift.
- On touch, press and hold a card briefly, then drag it; releasing drops it.
- Choose a column in the panel's column dropdown: the card moves to the bottom of that column. This is the alternative to dragging.
- Click a column name, type, and press Enter: the column is renamed.
- Click "+ Add column", type a name, and press Enter: a column is added at the far right.
- Drag a column header sideways: the column changes place among the others.
- Click "Delete card" and confirm: the card is removed.
- Delete a column via the "×" shown on hover at its header's right, then confirm: the column and its cards are removed.
- Click the backdrop, the "Close" cross, or press Escape: the panel closes.

## 4. Scope

Loop: open the team's single board, add cards to columns, describe and assign them, drag them through the stages until done. New teams start with columns "To do", "In progress", "Done". Left out: outside access, billing, reports, integrations, comments, due dates, labels.

## 5. Things and their states

- **Board**: name; ordered columns. One per team.
- **Column**: name; position; cards. Exists until deleted.
- **Card**: title, description, assignee (optional), column, position. Its state is its column; moving changes it.
- **Member**: name, initials, colour. Active members can be assigned.

## 6. Rules

- A card title is required, 1–120 characters; an empty title is refused with a validation message.
- A description is optional, up to 2000 characters; extra text is refused.
- A column name is required, 1–40 characters, and unique on the board; otherwise it is refused with a message.
- A card has at most one assignee; assignees must be team members.
- A card is in exactly one column at a time.
- Dropping a card outside any column returns it to its original place.
- Within a column, card order is kept exactly as dropped.
- Deleting a card or column needs confirmation; cancelling changes nothing.
- Deleting a column deletes its cards, and the dialog states how many.
- The last remaining column cannot be deleted; the delete control is hidden.
- Reordering a column keeps all its cards.
- Editing a card to empty its title reverts to the previous title.
- Any team member can perform any action; there are no restrictions between members.