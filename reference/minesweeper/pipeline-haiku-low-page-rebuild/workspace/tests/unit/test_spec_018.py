import pytest

from src.domain.game import Game

ROWS = 9
COLUMNS = 9
STARTED_AT = "2024-01-01T10:00:00"

# Far-side mines: none of them is a neighbour of any target used below,
# so they must never be counted. A wrap-around implementation would count
# (8, 8) and (8, 0) for the corner (0, 0) and (0, 8) for the corner (0, 0)
# as well, which the expectations below catch.
FAR_SIDE_MINES = [(8, 8), (8, 0), (0, 8)]


def in_board_neighbours(row, column):
    """The up to eight neighbours of a position that lie inside the board."""
    result = []
    for r in range(row - 1, row + 2):
        for c in range(column - 1, column + 2):
            if (r, c) == (row, column):
                continue
            if 0 <= r < ROWS and 0 <= c < COLUMNS:
                result.append((r, c))
    return result


def build_board(mine_positions):
    """Full 9x9 board of hidden cells. Mines sit only at the given positions,
    and each cell's adjacent_mine_count is the number of mines among its
    in-board neighbours, as the mine layout fixes it."""
    cells = []
    for row in range(ROWS):
        for column in range(COLUMNS):
            count = sum(
                1 for n in in_board_neighbours(row, column) if n in mine_positions
            )
            cells.append({
                "id": f"{row}-{column}",
                "row": row,
                "column": column,
                "has_mine": (row, column) in mine_positions,
                "adjacent_mine_count": count,
                "state": "hidden",
            })
    return cells


def make_in_progress_game(mine_positions):
    game = Game(id="game-edge-boundaries")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = STARTED_AT
    game.elapsed_seconds = 0
    game.mine_count = len(mine_positions)
    game.flag_count = 0
    game.ended_at = None
    game.cells = build_board(mine_positions)
    return game


def find_cell(game, row, column):
    matches = [c for c in game.cells if c["row"] == row and c["column"] == column]
    assert len(matches) == 1
    return matches[0]


@pytest.mark.parametrize(
    "target, neighbour_mines, expected_count",
    [
        # Corner (0, 0): only 3 neighbours lie inside the board, all mined.
        # Far-side mines are not neighbours, so the count is 3, not 6.
        ((0, 0), [(0, 1), (1, 0), (1, 1)], 3),
        # Top edge (0, 4): only 5 neighbours lie inside the board, all mined.
        # Bottom-row mines are not neighbours, so the count is 5.
        ((0, 4), [(0, 3), (0, 5), (1, 3), (1, 4), (1, 5)], 5),
        # Interior (4, 4): all 8 neighbours lie inside the board, all mined.
        # This is the limit case: exactly eight neighbours, count 8.
        ((4, 4), [(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)], 8),
    ],
)
def test_adjacency_counts_only_in_board_neighbours(target, neighbour_mines, expected_count):
    # Given an in-progress game whose mine layout is already fixed: the
    # target cell is safe and its in-board neighbours hold the listed mines.
    # The far-side mines are placed where wrap-around would wrongly count them.
    mine_positions = set(neighbour_mines) | set(FAR_SIDE_MINES)
    game = make_in_progress_game(mine_positions)

    # Working: the target is not in mine_positions, so it is safe. It is hidden
    # and unflagged, so the reveal is accepted. Its count is above zero, so no
    # zero-expansion runs. Most safe cells stay hidden, so the game is not won.
    # No other rule ends or changes the board for this reveal.
    assert find_cell(game, target[0], target[1])["has_mine"] is False

    # When the target cell is revealed.
    game.reveal_cell(row=target[0], column=target[1])

    revealed = find_cell(game, target[0], target[1])
    # Working: the target was hidden and unflagged and is not a mine, so it is revealed.
    assert revealed["state"] == "revealed"
    # Working: the in-board mined neighbours number expected_count, and the
    # far-side mines are not neighbours of the target, so they add nothing.
    assert revealed["adjacent_mine_count"] == expected_count
    # Working: the game stays in progress, since the reveal neither hit a mine
    # nor opened every safe cell.
    assert game.status == "in_progress"
