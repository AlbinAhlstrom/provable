import pytest

from src.domain.game_session import GameSession


def _cell(session, row, column):
    return next(c for c in session.cells if c["row"] == row and c["column"] == column)


def _lost_two_by_two_session():
    # Given a 2x2 board with mines on the diagonal (0,0) and (1,1).
    # Safe cells (0,1) and (1,0) each touch both mines, so adjacent_mine_count is 2.
    # The board keeps its four hidden cell records; only the mine layout is set.
    session = GameSession(
        id="game-loss-1",
        difficulty_id="beginner",
        rows=2,
        columns=2,
        mine_count=2,
    )
    for cell in session.cells:
        cell["has_mine"] = (cell["row"] == cell["column"])  # (0,0) and (1,1)
        cell["adjacent_mine_count"] = 0 if cell["has_mine"] else 2
        cell["state"] = "hidden"

    # The session has just been lost by revealing a mine earlier.
    # Status is lost, the timer has stopped and ended_at is recorded.
    session.status = "lost"
    session.started_at = "2024-01-01T10:00:00"
    session.ended_at = "2024-01-01T10:05:00"
    session.elapsed_seconds = 300
    return session


def test_loss_exposes_every_mine_when_board_is_finalised():
    session = _lost_two_by_two_session()

    # Sanity check of the arranged Given: exactly the two diagonal cells hold mines.
    assert _cell(session, 0, 0)["has_mine"] is True
    assert _cell(session, 1, 1)["has_mine"] is True

    # When the board is finalised after the loss.
    session.finalise_board()

    # Then (0,0) has a mine, is hidden before finalisation, so it must now be exposed.
    # Expected state: "revealed", because the mine is open on screen.
    assert _cell(session, 0, 0)["state"] == "revealed"

    # Then (1,1) has a mine, is hidden before finalisation, so it must now be exposed.
    # Expected state: "revealed", for the same reason as above.
    assert _cell(session, 1, 1)["state"] == "revealed"
