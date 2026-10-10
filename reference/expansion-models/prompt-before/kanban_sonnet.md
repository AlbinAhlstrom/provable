# Kanban Board for a Small Team: Product & Behavioral Specification

## 1. Personas & Journeys
**Team member** (the only persona). Every member has the same abilities. Members need to:
- See at a glance what work exists, which stage it is in, and who has it.
- Add cards, edit them, assign them, and move them as work progresses.
- Spot their own cards quickly.

There are no admins, guests, or outside viewers.

## 2. Presentation & Interaction
The board looks like the familiar kanban board:
- Columns sit side by side, left to right, in workflow order. Each has a header with its name and card count, and the board scrolls horizontally if needed.
- Cards are light rounded tiles stacked vertically in each column on a soft neutral background. Each card shows its title and the assignee's initials or avatar circle.
- Each column ends with an "Add card" control.

Interactions:
- **Drag and drop:** drag a card within a column to reorder it, or to another column to change its stage. A visible gap shows where it will land.
- **Open card:** clicking a card opens a panel with an editable title, description, and assignee picker.
- **Column management:** add, rename, reorder, and remove columns from the column header menu.
- **Filter:** a "My cards" toggle highlights the member's own work.
- **Empty states:** an empty column shows a gentle hint; a new board starts with To Do, In Progress, and Done.

## 3. MVP Scope
This covers one board per team, with columns, cards, assignment, and movement. It excludes external access, billing, reporting, and integrations.

## 4. Core Concepts
- **Board:** the team's single board, holding ordered columns.
- **Column:** a named workflow stage with a position.
- **Card:** a work item with a title, an optional description, at most one assignee, one column, and a position within it.
- **Team member:** a person with a name who can be assigned cards.

Card life: created in a column, edited, reassigned, moved between columns or positions, and finally deleted. "Done" is just a column, not a locked state.

## 5. Business Rules
1. A team has exactly one board.
2. Column names are required and unique on the board, ignoring case and surrounding spaces.
3. Column order is a single, gap-free sequence. Reordering a column keeps all its cards.
4. The board must always keep at least one column.
5. A column containing cards cannot be removed until its cards are moved or deleted. The member is told why.
6. A card has a non-empty title (up to 120 characters). The description is optional.
7. Every card belongs to exactly one column and has a unique position within it. Moving a card closes the gap in its old column and opens one in the new column.
8. A card can only be moved to an existing column. If the target is gone, the card stays where it was.
9. A card has zero or one assignee, who must be a current team member. Removing a member unassigns their cards, and the cards stay.
10. A new card is added at the bottom of the column where it was created.
11. Deleting a card requires confirmation.
12. Any rejected action leaves the board unchanged and shows a plain message next to the field or card involved.
13. If two members change the same card at once, the latest change wins and both boards show the result.