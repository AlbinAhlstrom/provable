# Kanban Board for a Small Team: Product & Behavioral Specification

## 1. Personas & Value Journeys

**Team member (the only persona).** Needs to see at a glance what work exists, which stage each item is in, and who owns it. Accomplishes: creating a card, editing its title and description, assigning it to a teammate (or leaving it unassigned), and moving it to another column as work progresses.

There is no separate administrator or customer perspective in scope.

## 2. Presentation & Interaction

- **Look:** The familiar kanban layout: a horizontal row of side-by-side columns, each with a header naming the stage and a card count, and cards stacked vertically inside them. Cards are compact white tiles showing title, assignee initials or name, and a subtle position cue. Neutral background, calm accent colour for the active drag target.
- **Direct manipulation:** Drag a card within a column to reorder it, or across columns to change its stage. Dropping shows the new position immediately. Clicking a card opens it for viewing and editing in place.
- **Forms:** A simple "add card" control at the foot of each column. Fields: title (required), description (optional), assignee (optional, chosen from team members).
- **Assignment:** Shown as a small avatar or name chip on the card; changed through a single picker.

## 3. MVP Scope (Core Loop)

Create card → assign → move through columns → edit details → see the current state of the whole board.

Each team has exactly one board, made of ordered columns (workflow stages) that the team sets up. Cards live in exactly one column at a time.

## 4. Core Concepts & States

- **Board:** one per team; holds its ordered columns.
- **Column:** a named workflow stage with a fixed position on the board.
- **Card:** a work item with title, description, assignee, column, and position within that column.
- **Team member:** a person on the team who can be assigned cards.

Card lifecycle: *Created* (in a column) → *Moved* (any number of times between columns) → *Edited* (any time). Cards are not deleted in this MVP; they stay on the board in their last column.

## 5. Business Rules & Invariants

- **Title required:** a card cannot be saved with an empty or whitespace-only title.
- **One column per card:** a card is always in exactly one column.
- **Ordered positions:** cards within a column have a unique, continuous order; any move or reorder keeps it so.
- **Assignee must be a team member:** an assignee is either empty or a current member of the same team.
- **Column must exist:** a card can only be created in or moved to a column on its team's board.
- **Board has at least one column:** the last column cannot be removed.
- **Rejected operations change nothing:** an invalid save, move, or assignment shows a clear message explaining the problem and leaves the board exactly as it was.
- **Concurrent edits:** when two members change the same card, the later save shows the latest version first rather than silently overwriting it.