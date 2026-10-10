import pytest

from src.domain.game_session import GameSession


def make_session(mine_count):
    # Constructed with only the required fields. Cells are left as the
    # constructor creates them: 9 x 9 records, all hidden, no mine, count 0.
    return GameSession(
        id="session-adjacency",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=mine_count,
    )


def cell_at(session, row, column):
    # Look up the cell record for a board position.
    matches = [c for c in session.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


SAFE_ROW = 2
SAFE_COLUMN = 2

# The eight neighbours of (2, 2), all inside the 9 x 9 board.
EIGHT_NEIGHBOURS = [
    (1, 1), (1, 2), (1, 3),
    (2, 1),         (2, 3),
    (3, 1), (3, 2), (3, 3),
]


def test_safe_cell_with_all_eight_neighbours_mined_counts_eight():
    # Arrange: safe cell (2, 2) is not a mine. All eight neighbours are mines.
    # Total mines = 8, which matches mine_count = 8. Nothing else is mined.
    session = make_session(mine_count=8)
    session.place_mines(mine_positions=list(EIGHT_NEIGHBOURS))

    # Act: nothing further; the count is produced when mines are placed.

    # Assert.
    # Cell (2, 2) has has_mine False, so it is a safe cell.
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["has_mine"] is False
    # Its eight neighbours all exist (inside the 9 x 9 board) and all are mines,
    # so the number of mines among its eight neighbours is 8.
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["adjacent_mine_count"] == 8


def test_mine_outside_the_eight_neighbours_is_not_counted():
    # Arrange: same as the exactly-at-limit case, plus one extra mine at (0, 0).
    # (0, 0) is two rows and two columns away from (2, 2), so it is not a
    # neighbour. Total mines = 9, so mine_count = 9.
    session = make_session(mine_count=9)
    session.place_mines(mine_positions=list(EIGHT_NEIGHBOURS) + [(0, 0)])

    # Act: nothing further.

    # Assert.
    # The eight neighbours of (2, 2) are still all mines: 8 of them.
    # The extra mine at (0, 0) lies outside the neighbourhood, so it adds
    # nothing. A count of 9 would mean the rule was counting beyond the
    # eight neighbours, so the expected value is 8, not 9.
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["has_mine"] is False
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["adjacent_mine_count"] == 8


def test_safe_cell_with_no_mined_neighbours_counts_zero():
    # Arrange: safe cell (2, 2). The only mine is at (0, 0), which is outside
    # the eight neighbours of (2, 2). Total mines = 1, so mine_count = 1.
    session = make_session(mine_count=1)
    session.place_mines(mine_positions=[(0, 0)])

    # Act: nothing further.

    # Assert.
    # Cell (2, 2) is safe and none of its eight neighbours is a mine, so the
    # number of mines among its eight neighbours is 0.
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["has_mine"] is False
    assert cell_at(session, SAFE_ROW, SAFE_COLUMN)["adjacent_mine_count"] == 0
