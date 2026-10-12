# Team Kanban Board

## 1. People and their journey

**Team member** (the only role). A member of a small team who uses the shared board to see and update the team's work.
- Needs to see: every column in order, every card in each column, each card's title, assignee, and position.
- Decides: what work exists, which column a card is in, who is assigned to it.
- Path: opens the board, reads the columns left to right, creates a card in the first column, assigns it, moves it forward as work progresses, and edits its title or description as the work changes. The card is done when it sits in the last column.

## 2. How it looks

A plain, flat, board-style page like a physical kanban wall: a single white-grey surface with evenly spaced vertical columns of cards, readable at a glance.

- Page background: flat light grey (#F2F2F2), fills the whole window behind everything.
- Board header: flat white bar across the top, 56px tall, with the board name in dark charcoal (#222222) at left and a "Team members" avatar row at right.
- Team members row: small circular avatars, 28px, each showing the member's initials on a distinct colour; a member with no assignment shows in grey (#9E9E9E).
- Column area: horizontal row beneath the header, columns side by side with 16px gaps, scrolling sideways when they do not fit.
- Column: flat white panel with a 1px light border (#D9D9D9), 280px wide, column name in bold charcoal at top, card count in grey beside it.
- Column header while empty: same panel, with the text "No cards yet" centred in mid grey (#757575).
- Add-card control: a full-width text row at the foot of each column reading "+ Add card" in blue (#1565C0); on hover the row gains a light blue fill (#E3F2FD).
- Card: flat white rectangle with 1px border (#D9D9D9), 8px rounded corners, 12px padding, title in charcoal, assignee initials badge at lower right.
- Card when selected: border turns blue (#1565C0), 2px.
- Card while being dragged: lifted with a soft shadow, slightly translucent (90% opacity), follows the pointer.
- Drop target column while dragging a card over it: panel border turns dashed blue (#1565C0), a blue insertion line 3px tall appears at the drop position.
- Card with no assignee: badge shows a grey outlined circle with no initials.
- Card title field while editing: inline text box with blue (#1565C0) 1px border, white fill.
- Assignee picker: small popup list beneath the badge, white with shadow, each member name with avatar; the current assignee is marked with a blue check.
- Confirmation message: small dark bar (#333333) at the bottom centre, white text, shown for 3 seconds after a refused action, with the reason.

## 3. How it is used

- Click the "+ Add card" row in a column: a new card appears at the bottom of that column in edit mode.
- Type in a card's title box and press Enter: the title is saved; Escape cancels the change.
- Click a card: opens the card detail panel on the right with title, description, assignee, and column.
- Edit the description in the detail panel: text box that saves when you click outside it.
- Click the assignee badge on a card: opens the assignee picker; click a member name to assign; click "Unassigned" to clear.
- Drag a card (mouse) or press and hold then drag (touch): moves it to any position in any column; release to drop.
- Click the card's column name in the detail panel and choose another column: moves the card to the end of that column.
- Press Delete on a selected card (or choose "Delete card" in the detail panel) and confirm: removes the card.
- Scroll the board sideways with the scrollbar or a two-finger swipe (touch): reveals columns off-screen.
- Right-click (or long press on touch) a card: shows a menu with Open, Assign, Move to column, Delete.

## 4. Scope

The loop: a team member creates a card, describes it, assigns it to a member, and moves it across columns until it reaches the last column.

Left out: customers or outside users, billing, reports, integrations, multiple boards per team, column editing beyond the fixed set.

Forms ask only for a title (required), an optional description, and an optional assignee.

## 5. Things and their states

- **Board**: one per team; holds an ordered list of columns and cards. Created with the team; no states.
- **Column**: a named workflow stage with a fixed position. Holds cards in order. Columns are ordered and fixed for the board; they do not change state.
- **Card**: a work item with title (required, up to 200 characters), description (optional, up to 5000 characters), an optional assignee, a column, and a position within that column.
  - States: Open (in any column, not last) → Done (in the last column). A card moves from Open to Done when a member moves it into the last column, and back to Open when moved out of it.
  - Deleted: removed permanently by a member's delete action; no further states.
- **Team member**: a person on the team who can be assigned cards. Holds a name and initials. Membership is set up with the team and is not changed through the board.

## 6. Rules

- A card must have a non-empty title; an empty title on save is refused and the old title stays.
- A title longer than 200 characters is refused on entry.
- A description longer than 5000 characters is refused on entry.
- A card is always in exactly one column; it cannot exist outside a column.
- A new card is placed at the bottom of the first column.
- Moving a card to another position in the same column reorders the cards; the other cards keep their relative order.
- Moving a card to another column places it where it is dropped; if dropped without a position, it goes to the bottom of that column.
- A card can be assigned to at most one member; assigning a new member replaces the old assignment.
- A card can be unassigned; an unassigned card shows the grey badge.
- Only members of the team can be assigned; assigning anyone else is refused.
- Deleting a card asks for confirmation; cancelling the confirmation changes nothing.
- A card cannot be moved to a column that does not exist on the board; the drop is ignored and the card returns to its previous place.
- Changes to a card are saved as they are made; a change in progress is lost if the member leaves the card with Escape.
- Every change is shown to all members on the board when they next view it; no change is hidden.