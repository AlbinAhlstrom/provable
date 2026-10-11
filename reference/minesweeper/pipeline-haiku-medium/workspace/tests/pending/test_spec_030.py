import pytest

from src.domain.game_session import GameSession


def _cell(row, column, has_mine, adjacent_mine_count, state):
    return {
        "id": f"c{row}{column}",
        "row": row,
        "column": column,
        "has_mine": has_mine,
        "adjacent_mine_count": adjacent_mine_count,
        "state": state,
    }


def _finished_session(status):
    # 2x2 board with exactly one mine, at (0, 0). Every other cell has
    # adjacent_mine_count 1, because each of them touches (0, 0).
    session = GameSession(
        id="session-1",
        difficulty_id="beginner",
        rows=2,
        columns=2,
        mine_count=1,
    )
    if status == "won":
        # Every safe cell is revealed; the mine at (0, 0) stays hidden.
        session.cells = [
            _cell(0, 0, True, 0, "hidden"),
            _cell(0, 1, False, 1, "revealed"),
            _cell(1, 0, False, 1, "revealed"),
            _cell(1, 1, False, 1, "revealed"),
        ]
    else:
        # The mine at (0, 0) was revealed, which is what lost means here.
        # The other safe cells stay hidden.
        session.cells = [
            _cell(0, 0, True, 0, "revealed"),
            _cell(0, 1, False, 1, "hidden"),
            _cell(1, 0, False, 1, "hidden"),
            _cell(1, 1, False, 1, "hidden"),
        ]
    session.status = status
    session.flag_count = 0
    session.elapsed_seconds = 120
    session.started_at = "2024-01-01T10:00:00"
    session.ended_at = "2024-01-01T10:02:00"
    return session


@pytest.mark.parametrize("status", ["won", "lost"])
def test_timer_stops_on_win_or_loss(status):
    # Given a session that has just been won or lost with elapsed_seconds 120
    session = _finished_session(status)
    assert session.status == status
    assert session.elapsed_seconds == 120

    # When time passes
    session.advance_time(seconds=60)

    # Then elapsed_seconds remains 120.
    # The status is won or lost, which is terminal. The timer only runs
    # while the status is in_progress, so the 60 seconds are not added.
    assert session.elapsed_seconds == 120
