import pytest

from src.domain.game_session import GameSession


def make_ready_session() -> GameSession:
    """A newly created 9x9 beginner-sized board in the Ready state.

    Every position holds one cell record with all six keys; no mines are placed yet.
    """
    rows, columns = 9, 9
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=rows,
        columns=columns,
        mine_count=10,
    )
    session.cells = [
        {
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "hidden",
        }
        for r in range(rows)
        for c in range(columns)
    ]
    return session


def test_first_reveal_records_start_time_and_starts_timer():
    # Given a session in Ready state: status "ready", started_at null,
    # elapsed_seconds 0, no mines placed, all 81 cells hidden.
    session = make_ready_session()
    assert session.status == "ready"
    assert session.started_at is None
    assert session.elapsed_seconds == 0

    # When the player reveals the centre cell (4, 4), which is the first reveal.
    # Mines are placed at random avoiding (4, 4), so the centre is safe and the
    # game cannot be lost or won by this single reveal (10 mines on 81 cells).
    session.reveal_cell(row=4, column=4)

    # Then the session is now in progress, because the first reveal of a ready
    # session moves it out of Ready and the timer is running.
    assert session.status == "in_progress"

    # And started_at is recorded: it is a non-empty string set at the first reveal.
    assert isinstance(session.started_at, str)
    assert session.started_at != ""

    # And the game has not ended, so ended_at stays null and the timer has just
    # started, so no seconds have accumulated yet.
    assert session.ended_at is None
    assert session.elapsed_seconds == 0


def test_placing_a_flag_does_not_start_the_timer():
    # Given a session in Ready state: no cell revealed, started_at null.
    session = make_ready_session()
    assert session.status == "ready"
    assert session.started_at is None

    # When the player flags the hidden cell (0, 0). Flagging reveals nothing
    # and must not start the timer.
    session.toggle_flag(row=0, column=0)

    # Then the cell at (0, 0) is flagged, which is the only change.
    flagged = [c for c in session.cells if c["state"] == "flagged"]
    assert len(flagged) == 1
    assert flagged[0]["row"] == 0 and flagged[0]["column"] == 0

    # And the session is still Ready with no start time and no elapsed time.
    assert session.status == "ready"
    assert session.started_at is None
    assert session.elapsed_seconds == 0
