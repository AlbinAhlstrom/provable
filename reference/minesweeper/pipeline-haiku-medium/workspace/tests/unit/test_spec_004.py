import pytest

from src.domain.game_session import GameSession

EXPERT_ROWS = 16
EXPERT_COLUMNS = 30
EXPERT_MINES = 99

# 99 consecutive row-major indices (380..478). Index 479 is cell (15, 29),
# which stays safe. Its three neighbours (14, 28), (14, 29) and (15, 28)
# are mines, so it is a numbered cell with count 3 and does not spread.
MINE_INDICES = range(380, 479)


def _mine_positions():
    return {
        (index // EXPERT_COLUMNS, index % EXPERT_COLUMNS)
        for index in MINE_INDICES
    }


def _adjacent_count(mines, row, column):
    count = 0
    for d_row in (-1, 0, 1):
        for d_col in (-1, 0, 1):
            if (d_row, d_col) == (0, 0):
                continue
            if (row + d_row, column + d_col) in mines:
                count += 1
    return count


def _expert_session_in_progress():
    session = GameSession(
        id="session-expert",
        difficulty_id="expert",
        rows=EXPERT_ROWS,
        columns=EXPERT_COLUMNS,
        mine_count=EXPERT_MINES,
    )
    session.status = "in_progress"
    session.started_at = "2024-03-01T10:00:00"
    mines = _mine_positions()
    for cell in session.cells:
        position = (cell["row"], cell["column"])
        cell["has_mine"] = position in mines
        cell["adjacent_mine_count"] = _adjacent_count(
            mines, cell["row"], cell["column"]
        )
    return session


def _cell_at(session, row, column):
    return next(
        cell
        for cell in session.cells
        if cell["row"] == row and cell["column"] == column
    )


def _assert_expert_dimensions(session):
    assert session.rows == 16
    assert session.columns == 30
    assert session.mine_count == 99


def test_reveal_on_last_cell_keeps_expert_dimensions():
    session = _expert_session_in_progress()

    session.reveal_cell(row=15, column=29)

    # (15, 29) is inside the 16x30 board, hidden, unflagged and safe
    # (index 479 is not a mine), so the reveal is allowed. Its count is 3
    # from the mines at (14,28), (14,29) and (15,28), so nothing spreads and
    # the board is not won. The cell itself becomes revealed.
    assert _cell_at(session, 15, 29)["state"] == "revealed"
    # The reveal does not touch the board size or the mine count, so they
    # still read 16, 30 and 99.
    _assert_expert_dimensions(session)


def test_toggle_flag_on_last_cell_keeps_expert_dimensions():
    session = _expert_session_in_progress()

    session.toggle_flag(row=15, column=29)

    # (15, 29) is hidden and inside the board, so the flag is placed:
    # the cell becomes flagged and flag_count goes from 0 to 1. Nothing else
    # about the board changes.
    assert _cell_at(session, 15, 29)["state"] == "flagged"
    assert session.flag_count == 1
    # The flag does not change the board size or the mine count.
    _assert_expert_dimensions(session)


def test_abandon_game_keeps_expert_dimensions():
    session = _expert_session_in_progress()

    session.abandon_game()

    # The session is in_progress, which is a status abandon_game accepts,
    # so the game ends as abandoned with no win or loss result.
    assert session.status == "abandoned"
    # Ending the game does not change the board size or the mine count.
    _assert_expert_dimensions(session)


@pytest.mark.parametrize("row,column", [(16, 29), (15, 30)])
def test_reveal_beyond_expert_board_is_refused_and_dimensions_stay(row, column):
    session = _expert_session_in_progress()

    # Only one coordinate is moved past the last valid index (15 for rows,
    # 29 for columns). Row 16 or column 30 lies outside the 16x30 board,
    # so the reveal is refused with CellOutOfBoundsError.
    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=row, column=column)
    assert type(exc_info.value).__name__ == "CellOutOfBoundsError"

    # The refused action leaves the board size and the mine count unchanged.
    _assert_expert_dimensions(session)


@pytest.mark.parametrize("row,column", [(16, 29), (15, 30)])
def test_toggle_flag_beyond_expert_board_is_refused_and_dimensions_stay(row, column):
    session = _expert_session_in_progress()

    # Only one coordinate is moved past the last valid index. The flag
    # placement is refused with CellOutOfBoundsError because the cell lies
    # outside the 16x30 board.
    with pytest.raises(Exception) as exc_info:
        session.toggle_flag(row=row, column=column)
    assert type(exc_info.value).__name__ == "CellOutOfBoundsError"

    # The refused action leaves the board size and the mine count unchanged.
    _assert_expert_dimensions(session)
