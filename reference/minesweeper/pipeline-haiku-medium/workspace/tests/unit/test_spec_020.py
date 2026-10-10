import pytest

from src.domain.game_session import GameSession


def _build_session_in_progress():
    # Beginner preset: 9 rows, 9 columns, 10 mines.
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    # The game is already running, so flag refusal can only come from the cell state.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.elapsed_seconds = 0
    session.flag_count = 0
    # Ten mines in the first ten cells in row-major order: row 0 and the first cell of row 1.
    # The target cell (4, 4) is at index 40, so it is never a mine and no win is possible.
    for cell in session.cells[:10]:
        cell["has_mine"] = True
    return session


def _cell_at(session, row, column):
    return next(c for c in session.cells if c["row"] == row and c["column"] == column)


def test_revealed_cell_cannot_be_flagged():
    # Given a revealed cell in an in-progress game.
    session = _build_session_in_progress()
    target = _cell_at(session, 4, 4)
    target["state"] = "revealed"
    flags_before = session.flag_count

    # When the player toggles a flag on the revealed cell.
    with pytest.raises(Exception) as exc_info:
        session.toggle_flag(row=4, column=4)

    # Then the action is refused by the rules.
    # Flagging applies only to hidden or flagged cells; (4, 4) is revealed, so it is refused.
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # And the cell state remains revealed.
    # The refusal changes nothing, so the state is still "revealed".
    assert _cell_at(session, 4, 4)["state"] == "revealed"

    # And the flag count is unchanged.
    # No flag was added, so flag_count is still 0.
    assert session.flag_count == flags_before


def test_hidden_cell_in_same_session_can_be_flagged():
    # Given the same in-progress game, with the target cell hidden instead of revealed.
    session = _build_session_in_progress()
    target = _cell_at(session, 4, 4)
    target["state"] = "hidden"
    flags_before = session.flag_count

    # When the player toggles a flag on the hidden cell.
    session.toggle_flag(row=4, column=4)

    # Then the cell becomes flagged.
    # A hidden cell may be flagged while the game is in progress, so (4, 4) becomes "flagged".
    assert _cell_at(session, 4, 4)["state"] == "flagged"

    # And the flag count rises by one.
    # One flag was added to the board, so flag_count goes from 0 to 1.
    assert session.flag_count == flags_before + 1
