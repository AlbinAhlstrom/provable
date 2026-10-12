import copy

import pytest

from src.domain.game import Game


MINES = {
    (3, 3), (3, 5),                          # the two mines next to the chorded cell (4,4)
    (6, 2), (6, 3), (6, 4), (6, 5), (6, 6),  # keep row 5 neighbours numbered (no cascade)
    (0, 0), (0, 8), (8, 8),                  # far away, to reach exactly mine_count = 10
}
TARGET = (4, 4)
HIDDEN_NEIGHBOURS = [(3, 4), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]


def _count(row, column, width, height):
    total = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < height and 0 <= c < width and (r, c) in MINES:
                total += 1
    return total


def _playing_game(flagged):
    game = Game(
        id="g1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T00:00:00Z",
    )
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T00:00:05Z"
    game.elapsed_seconds = 5
    cells = []
    for row in range(game.height):
        for column in range(game.width):
            state = "Hidden"
            if (row, column) == TARGET:
                state = "Opened"
            elif (row, column) in flagged:
                state = "Flagged"
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINES,
                    "adjacent_mine_count": _count(row, column, game.width, game.height),
                    "state": state,
                }
            )
    game.cells = cells
    game.flags_placed = len(flagged)
    game.remaining_mines = game.mine_count - len(flagged)
    return game


def _cell(game, row, column):
    return game.cells[row * game.width + column]


@pytest.mark.parametrize(
    "flagged",
    [
        # one flag fewer than N=2 (just below the limit)
        [(3, 3)],
        # one flag more than N=2 (just above the limit)
        [(3, 3), (3, 5), (3, 4)],
    ],
    ids=["one_flag_fewer_than_number", "one_flag_more_than_number"],
)
def test_chord_with_mismatched_flag_count_changes_nothing(flagged):
    game = _playing_game(flagged)
    # Cell (4,4) has mines at (3,3) and (3,5) among its neighbours, row 5 has none -> N = 2
    assert _cell(game, *TARGET)["adjacent_mine_count"] == 2
    before_cells = copy.deepcopy(game.cells)

    game.chord_cell(row=4, column=4)

    # Flag count around (4,4) is 1 or 3, which differs from N=2 -> chord has no effect:
    # every cell keeps exactly its state (no Hidden neighbour opened, no mine detonated).
    assert game.cells == before_cells
    # Nothing opened, nothing detonated -> status stays Playing, no struck cell.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    # Flags were not touched by the chord.
    assert game.flags_placed == len(flagged)
    assert game.remaining_mines == 10 - len(flagged)


def test_chord_with_flag_count_equal_to_number_opens_hidden_neighbours():
    game = _playing_game([(3, 3), (3, 5)])
    assert _cell(game, *TARGET)["adjacent_mine_count"] == 2

    game.chord_cell(row=4, column=4)

    # Exactly N=2 flags (both on the real mines) -> every Hidden neighbour is opened:
    # (3,4) count 2, (4,3) count 1, (4,5) count 1, (5,3),(5,4),(5,5) count 3 each,
    # all numbered, so no cascade spreads further; none holds a mine.
    for row, column in HIDDEN_NEIGHBOURS:
        assert _cell(game, row, column)["state"] == "Opened"
    # The flagged mines stay Flagged.
    assert _cell(game, 3, 3)["state"] == "Flagged"
    assert _cell(game, 3, 5)["state"] == "Flagged"
    # A cell outside the neighbourhood is not opened (no cascade from numbered cells).
    assert _cell(game, 2, 4)["state"] == "Hidden"
    # Many safe cells remain Hidden and no mine was opened -> still Playing, not Won or Lost.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 2
