import copy

import pytest

from src.domain.game import Game


MINE = (7, 7)


def make_cells(mines, revealed=(), flagged=()):
    """Full 9x9 Beginner grid: one record per position, adjacency counts computed from mines."""
    cells = []
    for r in range(9):
        for c in range(9):
            count = sum(
                1
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and (r + dr, c + dc) in mines
            )
            if (r, c) in revealed:
                state = "revealed"
            elif (r, c) in flagged:
                state = "flagged"
            else:
                state = "hidden"
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in mines,
                    "adjacent_mine_count": count,
                    "state": state,
                }
            )
    return cells


def in_progress_game(revealed=((4, 4),)):
    """In-progress Beginner game: single mine at (7,7), (4,4) revealed, nothing else touched."""
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.elapsed_seconds = 5
    game.mine_count = 10
    game.flag_count = 0
    game.cells = make_cells({MINE}, revealed=set(revealed))
    return game


def test_reveal_of_revealed_cell_is_ignored():
    game = in_progress_game(revealed=((4, 4),))
    before = copy.deepcopy(game.to_dict())

    # Cell (4,4) is already revealed: the reveal is ignored, nothing changes.
    game.reveal_cell(row=4, column=4)

    assert game.to_dict() == before


def test_reveal_of_last_inside_row_is_accepted_and_reveals_only_that_cell():
    game = in_progress_game(revealed=((4, 4),))

    # (8,8) is the last row and last column inside the 9x9 board. It is hidden,
    # unflagged, and touches the mine at (7,7), so its count is 1 and no expansion occurs.
    game.reveal_cell(row=8, column=8)

    target = next(c for c in game.cells if c["row"] == 8 and c["column"] == 8)
    # The target was hidden and unflagged, so it is now revealed.
    assert target["state"] == "revealed"
    # Its count is 1 (only (7,7) is a neighbour mine), so it is not zero and nothing expands.
    assert target["adjacent_mine_count"] == 1
    # One safe cell opened out of 80 safe cells: the game is still in progress.
    assert game.status == "in_progress"
    # The previously revealed (4,4) is untouched.
    assert next(c for c in game.cells if c["row"] == 4 and c["column"] == 4)["state"] == "revealed"


@pytest.mark.parametrize("row, column", [(9, 8), (8, 9), (-1, 0)])
def test_reveal_outside_board_is_ignored(row, column):
    game = in_progress_game(revealed=((4, 4),))
    before = copy.deepcopy(game.to_dict())

    # Same board as the accepted case, but the target lies one step outside the 9x9 grid.
    # No cell matches the position, so no state can change.
    game.reveal_cell(row=row, column=column)

    # Board and session are exactly as before.
    assert game.to_dict() == before


def test_reveal_after_loss_is_refused_and_state_unchanged():
    # Lost game: the mine at (7,7) has been revealed; (0,0) is a hidden safe cell with count 0.
    game = in_progress_game(revealed=((7, 7),))
    game.status = "lost"
    game.ended_at = "2024-01-01T10:05:00"
    game.elapsed_seconds = 300
    before = copy.deepcopy(game.to_dict())

    # The game has ended, so the reveal is refused and must not expand the zero-count cell (0,0).
    with pytest.raises(Exception) as exc_info:
        game.reveal_cell(row=0, column=0)

    # The interface names the refusal InvalidActionError for acting after the game is lost.
    assert type(exc_info.value).__name__ == "InvalidActionError"
    # Board and session are left unchanged: status, ended_at, timer and cells all match.
    assert game.to_dict() == before


def test_toggle_flag_after_win_is_refused_and_state_unchanged():
    # Won game: every safe cell is revealed; the mine at (7,7) is flagged as the win rule requires.
    all_safe = {(r, c) for r in range(9) for c in range(9)} - {MINE}
    game = in_progress_game()
    game.status = "won"
    game.ended_at = "2024-01-01T10:08:00"
    game.elapsed_seconds = 480
    game.flag_count = 1
    game.cells = make_cells({MINE}, revealed=all_safe, flagged={MINE})
    before = copy.deepcopy(game.to_dict())

    # The game has ended, so removing the flag is refused.
    with pytest.raises(Exception) as exc_info:
        game.toggle_flag(row=7, column=7)

    # The interface names the refusal InvalidActionError for acting after the game is won.
    assert type(exc_info.value).__name__ == "InvalidActionError"
    # Board and session are unchanged: the whole object matches its prior state.
    assert game.to_dict() == before
    # The mine stays flagged, because the win rule flagged it and the refused toggle changed nothing.
    assert next(c for c in game.cells if c["row"] == 7 and c["column"] == 7)["state"] == "flagged"
    # flag_count stays 1, matching the one flagged mine.
    assert game.flag_count == 1
