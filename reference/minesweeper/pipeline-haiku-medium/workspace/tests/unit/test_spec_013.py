import copy

import pytest

from src.domain.game_session import GameSession


def _beginner_session_with_flagged_cell(row: int, column: int) -> GameSession:
    # Given a new Beginner game (9 x 9, 10 mines) that has not been revealed yet.
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    # The board keeps one hidden cell per position; only the flagged cell is changed.
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            cell["state"] = "flagged"
    session.flag_count = 1
    return session


def test_flagged_cell_cannot_be_revealed():
    row, column = 4, 4
    session = _beginner_session_with_flagged_cell(row, column)

    # Snapshot everything the rule must leave untouched.
    cells_before = copy.deepcopy(session.cells)
    status_before = session.status
    flag_count_before = session.flag_count
    elapsed_before = session.elapsed_seconds
    started_before = session.started_at
    ended_before = session.ended_at

    # When the player attempts to reveal the flagged cell.
    # Expected: the flagged cell is refused by the rules, so ActionNotAllowedError is raised.
    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=row, column=column)
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # Then the target cell is still flagged.
    # Working: the reveal was refused, so the cell state is unchanged from "flagged".
    target = [c for c in session.cells if c["row"] == row and c["column"] == column][0]
    assert target["state"] == "flagged"

    # Then nothing else changes: every cell record is identical to before the attempt.
    # Working: no other cell was touched and no mines were placed, since the refusal
    # happens before any first-reveal processing.
    assert session.cells == cells_before

    # Then the session status is still ready.
    # Working: a refused reveal does not start the game, so status stays "ready".
    assert session.status == status_before == "ready"

    # Then the flag count is still 1.
    # Working: the refused reveal does not alter flags.
    assert session.flag_count == flag_count_before == 1

    # Then the timer is untouched: elapsed_seconds is 0, started_at and ended_at stay null.
    # Working: the game was never started, so no timer was begun or stopped.
    assert session.elapsed_seconds == elapsed_before == 0
    assert session.started_at == started_before is None
    assert session.ended_at == ended_before is None
