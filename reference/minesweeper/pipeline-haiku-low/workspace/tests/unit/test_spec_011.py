import copy

import pytest

from src.domain.game import Game


def build_terminal_game(status):
    """Beginner-sized 9x9 board in a terminal status.

    One mine at (0, 0), already flagged by the player (flag_count 1), so the
    board is consistent with a finished game. Every other cell is hidden with
    its correct adjacency count. The target cell (4, 4) is hidden and safe.
    """
    cells = []
    for r in range(9):
        for c in range(9):
            is_mine = (r, c) == (0, 0)
            # Neighbours of the mine at (0, 0) are (0,1), (1,0) and (1,1): count 1.
            adjacent = 1 if max(r, c) == 1 else 0
            cells.append({
                "id": f"cell-{r}-{c}",
                "row": r,
                "column": c,
                "has_mine": is_mine,
                "adjacent_mine_count": adjacent,
                "state": "flagged" if is_mine else "hidden",
            })
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = status
    game.started_at = "2024-01-01T10:00:00"
    game.ended_at = "2024-01-01T10:05:00"
    game.elapsed_seconds = 300
    game.mine_count = 10
    game.flag_count = 1
    game.cells = cells
    return game


@pytest.mark.parametrize("status", ["won", "lost"])
def test_reveal_after_end_is_refused_and_board_unchanged(status):
    # Given a game that has already ended (won or lost), with one flagged mine
    # at (0, 0) and the hidden safe cell (4, 4).
    game = build_terminal_game(status)
    before = copy.deepcopy(game.to_dict())

    # When the player reveals the hidden safe cell (4, 4).
    with pytest.raises(Exception) as exc_info:
        game.reveal_cell(row=4, column=4)

    # Then the action is refused, because the terminal state rejects changes.
    assert type(exc_info.value).__name__ == "InvalidActionError"
    # And the board and status are unchanged: (4, 4) is still hidden,
    # status is still the terminal one, and flag_count is still 1.
    assert game.to_dict() == before
    assert game.status == status


@pytest.mark.parametrize("status", ["won", "lost"])
def test_flag_after_end_is_refused_and_board_unchanged(status):
    # Given a game that has already ended (won or lost), with flag_count 1
    # and the hidden cell (4, 4).
    game = build_terminal_game(status)
    before = copy.deepcopy(game.to_dict())

    # When the player flags the hidden cell (4, 4).
    with pytest.raises(Exception) as exc_info:
        game.toggle_flag(row=4, column=4)

    # Then the action is refused, because flagging is only allowed while
    # the game is ready or in_progress.
    assert type(exc_info.value).__name__ == "InvalidActionError"
    # And the board and status are unchanged: (4, 4) is still hidden,
    # flag_count is still 1, and status is still the terminal one.
    assert game.to_dict() == before
    assert game.status == status


@pytest.mark.parametrize("status", ["won", "lost"])
def test_restart_after_end_creates_new_game(status):
    # Given a game that has already ended (won or lost), with flag_count 1,
    # elapsed_seconds 300 and started_at/ended_at set.
    game = build_terminal_game(status)

    # When the player restarts at the Beginner difficulty.
    game.start_game(difficulty="Beginner")

    # Then a new game is created: status is ready again.
    # The timer is reset: elapsed_seconds is 0, started_at and ended_at are None.
    # The flag count is reset to 0, since the old flagged mine is gone.
    # The difficulty is Beginner, as chosen.
    assert game.status == "ready"
    assert game.difficulty == "Beginner"
    assert game.elapsed_seconds == 0
    assert game.started_at is None
    assert game.ended_at is None
    assert game.flag_count == 0
