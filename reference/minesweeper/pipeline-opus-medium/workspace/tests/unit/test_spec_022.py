import pytest

from src.domain.game import Game


def _make_ready_game(mine_count, flagged_count):
    """Ready 9x9 game, no mines laid, with the first `flagged_count` cells
    (row-major) Flagged and all other cells Hidden."""
    width, height = 9, 9
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at="2024-01-01T10:00:00",
    )
    cells = []
    index = 0
    for row in range(height):
        for column in range(width):
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": False,
                    "adjacent_mine_count": 0,
                    "state": "Flagged" if index < flagged_count else "Hidden",
                }
            )
            index += 1
    game.cells = cells
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = flagged_count
    game.remaining_mines = mine_count - flagged_count
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    return game


def _cell(game, row, column):
    for c in game.cells:
        if c["row"] == row and c["column"] == column:
            return c
    raise AssertionError(f"cell {row}-{column} missing")


@pytest.mark.parametrize(
    "flags_before, expected_flags, expected_remaining",
    [
        # Exactly at the limit: F becomes M (10) -> counter 0.
        (9, 10, 0),
        # Just beyond the limit: F becomes M + 1 (11) -> counter -1 (negative allowed).
        (10, 11, -1),
    ],
)
def test_remaining_mines_equals_mines_minus_flags_at_and_beyond_limit(
    flags_before, expected_flags, expected_remaining
):
    mine_count = 10
    game = _make_ready_game(mine_count, flags_before)
    # Cell (8, 8) is the last cell in row-major order; flagged_count <= 10 only
    # covers rows 0-1, so it is Hidden. Game is Ready: flagging is allowed, no
    # mines are laid, no cell is opened, so no win/loss rule interferes.
    assert _cell(game, 8, 8)["state"] == "Hidden"

    game.toggle_flag(row=8, column=8)

    # Hidden -> Flagged adds one flag: flags_before + 1.
    assert _cell(game, 8, 8)["state"] == "Flagged"
    assert game.flags_placed == expected_flags
    # remaining_mines = mine_count - flags_placed = 10 - expected_flags.
    assert game.remaining_mines == mine_count - expected_flags
    assert game.remaining_mines == expected_remaining
    # Nothing else changed: still Ready, no mines laid.
    assert game.status == "Ready"
    assert game.mines_laid is False


def test_remaining_mines_returns_from_negative_when_flag_removed():
    mine_count = 10
    # 11 flags placed: counter starts at 10 - 11 = -1.
    game = _make_ready_game(mine_count, 11)
    # Cell (0, 0) is first in row-major order, so it is among the Flagged ones.
    assert _cell(game, 0, 0)["state"] == "Flagged"

    game.toggle_flag(row=0, column=0)

    # Flagged -> Hidden removes one flag: 11 - 1 = 10.
    assert _cell(game, 0, 0)["state"] == "Hidden"
    assert game.flags_placed == 10
    # remaining_mines = 10 - 10 = 0.
    assert game.remaining_mines == 0
    assert game.status == "Ready"
