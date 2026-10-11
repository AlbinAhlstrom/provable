# Kanban Board: Product & Behavioral Specification

## 1. Personas & Value Journeys
**Team Member** (the only role). Every member has equal rights on the team's board.
- **Sees:** all work, its stage, and who owns each card, at a glance.
- **Decides:** what to work on next and when work moves forward.
- **Accomplishes:** adds cards, edits details, assigns people, drags cards to the next stage, and reorders columns.

## 2. Presentation & Interaction
It looks like the familiar kanban board people know from sticky notes on a wall or from tools like Trello:
- **Board:** a light grey board surface. The board name sits at the top.
- **Columns:** rounded, slightly darker panels laid out left to right, with horizontal scrolling when they don't fit. Each column shows its name and a card count in its header.
- **Cards:** white, lightly shadowed rectangles stacked top to bottom. Each shows its title and the assignee's initials avatar in the corner.
- **Adding a card:** a "+ Add card" link sits at the foot of each column.
- **Editing a card:** clicking a card opens a detail panel with the title, description, and an assignee picker.
- **Moving cards:** drag a card within or across columns. A placeholder gap shows where it will land.
- **Reordering columns:** drag a column by its header.
- **Managing columns:** "+ Add column" sits at the far right. Columns can be renamed inline.
- **Tone:** calm, uncluttered, and practical.

## 3. MVP Scope
The core loop is: **create card → assign → move through columns → done.**
- A new board starts with three columns: To Do, In Progress, and Done.
- Card intake needs only a title. A description and an assignee are optional.

## 4. Core Concepts
- **Team:** a named group of members. It owns exactly one board.
- **Board:** an ordered list of columns.
- **Column:** a workflow stage with a name, a position, and an ordered list of cards.
- **Card:** a work item with a title, a description, an optional assignee, and a column and position.
- **Card lifecycle:** Created (in a column) → Moved between columns → Deleted.
  - A card's stage is simply the column it sits in.
  - There is no hidden status.

## 5. Business Rules
1. Each team has exactly one board.
2. A board must keep at least one column.
3. Column names are required, at most 50 characters, and unique within the board, ignoring case.
4. Columns have a continuous left-to-right order with no gaps or duplicates.
5. A column can only be deleted when it is empty. Otherwise the user is told to move its cards first.
6. Every card belongs to exactly one column at all times.
7. A card's title is required, has no leading or trailing blank space, and is at most 200 characters.
8. A card's description is optional and at most 5,000 characters.
9. A card has zero or one assignee, who must be a current member of the team.
10. When a member leaves the team, their cards become unassigned.
11. Cards within a column have a continuous top-to-bottom order.
12. Moving a card removes it from its old position and inserts it at the chosen position in the target column. Both columns are re-ordered together, or not at all.
13. A move to a column or position that does not exist is refused, and the card stays where it was.
14. If two members edit the same card at the same time, the later save is refused when the card has changed since it was opened. The user sees the latest version.
15. Only team members can view or change the board.
16. Any refused action leaves the board exactly as it was and shows a plain-language reason.