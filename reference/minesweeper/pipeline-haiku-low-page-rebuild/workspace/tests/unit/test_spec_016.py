import pytest

from src.domain.game import Game


def _game_in_status(status):
    """Build an existing game in the given status, holding an old board and timer."""
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = status
    game.mine_count = 10
    game.flag_count = 0
    if status == "ready":
        game.started_at = None
        game.ended_at = None
        game.elapsed_seconds = 0
        cell_state = "hidden"
    elif status == "in_progress":
        game.started_at = "2024-01-01T10:00:00"
        game.ended_at = None
        game.elapsed_seconds = 42
        cell_state = "revealed"
    else:  # "won" or "lost"
        game.started_at = "2024-01-01T10:00:00"
        game.ended_at = "2024-01-01T10:01:37"
        game.elapsed_seconds = 97
        cell_state = "revealed"
    # One old cell that carries a mine layout, which the restart must discard.
    game.cells = [
        {
            "id": "c-0-0",
            "row": 0,
            "column": 0,
            "has_mine": True,
            "adjacent_mine_count": 0,
            "state": cell_state,
        }
    ]
    return game


@pytest.mark.parametrize("status", ["ready", "in_progress", "won", "lost"])
def test_restart_resets_session(status):
    # Given a game in the given status, on Beginner, with 42 or 97 elapsed seconds
    # (or 0 when ready), a started_at/ended_at matching its status, and one old cell
    # that holds a mine.
    game = _game_in_status(status)

    # When the player starts a new game at Expert difficulty.
    game.start_game(difficulty="Expert")

    # Then the difficulty is the chosen one.
    # Expert is listed in the rules as 16 rows by 30 columns with 99 mines, and the
    # board is rebuilt from that difficulty, so mine_count is 99.
    assert game.difficulty == "Expert"
    assert game.mine_count == 99

    # Then the status is ready.
    # start_game sets status to ready in any prior status, so the game is ready.
    assert game.status == "ready"

    # Then the elapsed time is zero.
    # start_game resets the timer, so elapsed_seconds is 0 regardless of the old value.
    assert game.elapsed_seconds == 0

    # Then the timer has not started and has not ended.
    # A new ready game has no first reveal yet, so started_at and ended_at are None.
    assert game.started_at is None
    assert game.ended_at is None

    # Then no flags are placed on the new board.
    # flag_count is 0 for a new board, so the old board's flag count is discarded.
    assert game.flag_count == 0

    # Then no mine layout is fixed.
    # The mine layout is only fixed on the first reveal, so no cell in the new board
    # holds a mine: the board either is empty or has no has_mine True entries.
    assert not any(cell["has_mine"] for cell in game.cells)
