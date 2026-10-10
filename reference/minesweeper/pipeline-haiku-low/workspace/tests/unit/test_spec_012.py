import pytest

from src.domain.game import Game


def _beginner_hidden_board():
    """Nine by nine board of hidden cells, the shape a Beginner game has.

    The mine layout is not fixed yet, so every cell has has_mine False and
    adjacent_mine_count 0. Only the state of each cell is relevant here.
    """
    cells = []
    for row in range(9):
        for column in range(9):
            cells.append({
                "id": f"c{row}-{column}",
                "row": row,
                "column": column,
                "has_mine": False,
                "adjacent_mine_count": 0,
                "state": "hidden",
            })
    return cells


def test_first_reveal_starts_timer():
    # Given a newly created game in ready status with no board laid out yet.
    # status "ready", started_at None, elapsed_seconds 0, cells empty.
    game = Game(id="game-1")
    assert game.status == "ready"
    assert game.started_at is None

    # When the first cell is revealed at the centre of the board.
    # The reveal is the first reveal of a ready game, so it lays out the mines
    # (avoiding the target and its neighbours), sets started_at, and moves the
    # game to in_progress. Then it reveals the target cell.
    game.reveal_cell(row=4, column=4)

    # Then started_at is set. The timer starts on the first reveal, so the
    # field holds a timestamp string rather than None.
    assert game.started_at is not None
    assert isinstance(game.started_at, str)

    # And the game moved to in_progress, since the first reveal has happened
    # and the session has not ended (no mine can be hit by the safe centre
    # cell, and a 9x9 board with 10 mines cannot be won by one reveal).
    assert game.status == "in_progress"

    # And no time has elapsed yet at the moment of the first reveal, so the
    # counter is still 0 and the clock is now running from started_at.
    assert game.elapsed_seconds == 0


def test_flag_does_not_start_timer():
    # Given a game in ready status with a Beginner board of hidden cells.
    # status "ready" and started_at None, so the timer is not running.
    game = Game(id="game-2")
    game.cells = _beginner_hidden_board()
    assert game.status == "ready"
    assert game.started_at is None

    # When a hidden cell at (0, 0) is flagged.
    # Flagging is allowed while the game is ready. It changes only that cell's
    # state to flagged and raises flag_count by one. It does not reveal a cell,
    # so it is not a first reveal and the timer must not start.
    game.toggle_flag(row=0, column=0)

    # Then the timer has not started: started_at stays None.
    assert game.started_at is None

    # And the game is still ready, because no cell has been revealed.
    assert game.status == "ready"

    # And no time has elapsed.
    assert game.elapsed_seconds == 0

    # And the flag itself was placed on the targeted hidden cell (the rule
    # for flagging hidden cells), with flag_count increased by one.
    flagged = [c for c in game.cells if c["state"] == "flagged"]
    assert len(flagged) == 1
    assert flagged[0]["row"] == 0
    assert flagged[0]["column"] == 0
    assert game.flag_count == 1
