import pytest

from src.domain.game_session import GameSession


def _new_session() -> GameSession:
    # Beginner preset, freshly created: status ready, every cell hidden,
    # no mines placed, flag_count 0.
    return GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )


def _cell(session: GameSession, row: int, column: int) -> dict:
    return next(
        c for c in session.cells if c["row"] == row and c["column"] == column
    )


@pytest.mark.parametrize("row, column", [(2, 3), (8, 8)])
def test_toggling_flag_on_hidden_cell_flags_it_then_returns_it_to_hidden(row, column):
    # Given a hidden cell: a newly created session holds every cell as "hidden",
    # the status is "ready" (flagging is allowed in ready), and flag_count is 0.
    session = _new_session()
    assert _cell(session, row, column)["state"] == "hidden"
    assert session.flag_count == 0

    # When the player toggles the flag on that cell.
    session.toggle_flag(row=row, column=column)

    # Then the cell is hidden and unflagged before, so it becomes "flagged".
    # Flagging raises flag_count from 0 to 1.
    assert _cell(session, row, column)["state"] == "flagged"
    assert session.flag_count == 1

    # When the player toggles the flag again.
    session.toggle_flag(row=row, column=column)

    # Then the cell is flagged, so it returns to "hidden".
    # Unflagging lowers flag_count from 1 back to 0.
    assert _cell(session, row, column)["state"] == "hidden"
    assert session.flag_count == 0


def test_toggling_flag_on_revealed_cell_is_refused_and_changes_nothing():
    # Given the same fresh session as the accepted case, except that the
    # target cell (2, 3) is already "revealed" (the one thing that differs).
    session = _new_session()
    _cell(session, 2, 3)["state"] = "revealed"

    # When the player toggles the flag on that revealed cell.
    with pytest.raises(Exception) as exc_info:
        session.toggle_flag(row=2, column=3)

    # Then the action is refused by the rules: a revealed cell cannot be flagged.
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # And nothing changes: the cell stays "revealed" and flag_count stays 0.
    assert _cell(session, 2, 3)["state"] == "revealed"
    assert session.flag_count == 0
