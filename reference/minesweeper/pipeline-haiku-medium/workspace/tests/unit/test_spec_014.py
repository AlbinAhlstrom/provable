import copy

import pytest

from src.domain.game_session import GameSession


def build_session_with_revealed_number_cell():
    """3x3 board, one mine at (2, 2). The revealed cell (1, 1) is a numbered
    cell with adjacent_mine_count 1, so it is consistent with the rules: a
    numbered cell does not spread, so its hidden neighbours are valid."""
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=3,
        columns=3,
        mine_count=1,
    )
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.ended_at = None
    session.elapsed_seconds = 42
    session.flag_count = 0

    # Keep one record per position, each with every key; change only the contents.
    for cell in session.cells:
        cell["state"] = "hidden"
        cell["has_mine"] = False
        cell["adjacent_mine_count"] = 0

    # Mine at (2, 2) and its neighbours carry the correct counts.
    for cell in session.cells:
        if (cell["row"], cell["column"]) == (2, 2):
            cell["has_mine"] = True
        if (cell["row"], cell["column"]) in {(1, 1), (1, 2), (2, 1)}:
            cell["adjacent_mine_count"] = 1

    # The already revealed cell.
    for cell in session.cells:
        if (cell["row"], cell["column"]) == (1, 1):
            cell["state"] = "revealed"

    return session


def find_cell(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_revealed_cell_cannot_be_revealed_again():
    # Given a revealed cell (1, 1) with adjacent_mine_count 1 in an in_progress game,
    # elapsed_seconds 42, started_at recorded, no ended_at.
    session = build_session_with_revealed_number_cell()
    cells_before = copy.deepcopy(session.cells)

    # When the player attempts to reveal the same cell again.
    # Then the action is refused by the rules.
    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=1, column=1)
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # Then the cell state remains revealed.
    # Working: the refused action changes nothing, so (1, 1) was revealed and stays revealed.
    assert find_cell(session, 1, 1)["state"] == "revealed"

    # Then the timer is unaffected: elapsed_seconds still 42.
    # Working: the refusal does not touch the clock, which was 42 before the action.
    assert session.elapsed_seconds == 42

    # Then the session stays in_progress and has not ended.
    # Working: the game is still running, so no win, loss or end time is recorded.
    assert session.status == "in_progress"
    assert session.ended_at is None
    assert session.started_at == "2024-01-01T10:00:00"

    # Then no other cell changes state, mine placement or count.
    # Working: a refused action leaves every cell record exactly as it was.
    assert session.cells == cells_before
