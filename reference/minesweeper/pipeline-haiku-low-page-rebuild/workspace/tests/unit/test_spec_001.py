import pytest

from src.domain.game import Game

ROWS = 9
COLUMNS = 9
TARGET = (4, 4)
STARTED = "2024-01-01T10:00:00+00:00"


def neighbours_of(row, column):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS:
                result.append((r, c))
    return result


def build_board(mine_positions):
    """One record per position, every key present.

    The mine layout is fixed, so each cell's adjacent_mine_count is the number
    of mines among its on-board neighbours. Only has_mine and the counts are
    set from the layout; every cell starts hidden.
    """
    cells = []
    for row in range(ROWS):
        for column in range(COLUMNS):
            count = sum(
                1 for (r, c) in neighbours_of(row, column) if (r, c) in mine_positions
            )
            cells.append(
                {
                    "id": f"r{row}c{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in mine_positions,
                    "adjacent_mine_count": count,
                    "state": "hidden",
                }
            )
    return cells


def cell_at(game, row, column):
    matches = [c for c in game.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


def make_in_progress_game(mine_positions):
    game = Game(id="game-adjacency")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = STARTED
    game.mine_count = len(mine_positions)
    game.cells = build_board(mine_positions)
    return game


# Target (4,4) is interior with exactly eight on-board neighbours:
# (3,3), (3,4), (3,5), (4,3), (4,5), (5,3), (5,4), (5,5).
#
# At the limit: all eight neighbours are mines -> count 8.
# Just beyond: (3,3) is clear, so seven neighbours are mines -> count 7.
# The extra mine at (2,4) is two steps from (4,4), outside the neighbourhood,
# and must not be counted.
AT_LIMIT_MINES = {
    (3, 3), (3, 4), (3, 5),
    (4, 3), (4, 5),
    (5, 3), (5, 4), (5, 5),
}
BEYOND_LIMIT_MINES = {
    (3, 4), (3, 5),
    (4, 3), (4, 5),
    (5, 3), (5, 4), (5, 5),
    (2, 4),
}


@pytest.mark.parametrize(
    "mine_positions, expected_count",
    [
        pytest.param(AT_LIMIT_MINES, 8, id="exactly_at_eight_neighbour_limit"),
        pytest.param(BEYOND_LIMIT_MINES, 7, id="just_beyond_limit_outside_mine_ignored"),
    ],
)
def test_safe_cell_adjacent_mine_count_equals_mines_among_neighbours(mine_positions, expected_count):
    # Given: a fixed mine layout on a 9x9 board with an in-progress game.
    # Every cell's adjacent_mine_count is set from that layout.
    game = make_in_progress_game(mine_positions)
    target_row, target_column = TARGET

    # The target (4,4) is hidden and holds no mine, so it is a safe cell.
    assert cell_at(game, target_row, target_column)["has_mine"] is False
    assert cell_at(game, target_row, target_column)["state"] == "hidden"

    # Expected count from the layout: mines among the on-board neighbours of (4,4).
    # Walk-through: at the limit all 8 neighbours are mines -> 8.
    # Beyond the limit, (3,3) is clear -> 7; (2,4) is not a neighbour -> not counted.
    expected_from_layout = sum(
        1 for (r, c) in neighbours_of(target_row, target_column) if (r, c) in mine_positions
    )
    assert expected_from_layout == expected_count

    # When: the safe target cell is revealed.
    # Walk-through: the target is hidden, unflagged and not a mine, and the game
    # is in_progress, so the reveal is accepted. Its count is nonzero, so no
    # region expands. Many safe cells stay hidden, so the game is not won, and
    # no mine is hit, so it is not lost.
    game.reveal_cell(row=target_row, column=target_column)

    # Then: the revealed cell shows the number of mines among its neighbours.
    revealed = cell_at(game, target_row, target_column)
    # Walk-through: the target went hidden -> revealed; its count stays at the
    # layout value (8 or 7).
    assert revealed["state"] == "revealed"
    assert revealed["adjacent_mine_count"] == expected_count
    # Walk-through: the game stays in_progress because it neither hit a mine
    # nor revealed all safe cells.
    assert game.status == "in_progress"
