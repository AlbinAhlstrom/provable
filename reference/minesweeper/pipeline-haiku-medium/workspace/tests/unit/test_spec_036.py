import pytest

from src.domain.game_session import GameSession

TARGET_ROW = 4
TARGET_COLUMN = 4
STARTED_AT = "2024-01-01T10:00:00"
ENDED_AT = "2024-01-01T10:02:00"
ELAPSED_AT_END = 120


def _make_finished_board(status: str) -> GameSession:
    """Beginner-sized 9x9 board with 10 mines, arranged as a finished game.

    Every cell is revealed and safe except the target cell (4, 4), which is a
    hidden mine. This is consistent with a won game (all safe cells open, the
    mine still covered) and with a lost game (the status is what matters here).
    """
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    cells = []
    for row in range(9):
        for column in range(9):
            if row == TARGET_ROW and column == TARGET_COLUMN:
                state, has_mine = "hidden", True
            else:
                state, has_mine = "revealed", False
            cells.append(
                {
                    "id": f"cell-{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": has_mine,
                    "adjacent_mine_count": 0,
                    "state": state,
                }
            )
    session.cells = cells
    session.status = status
    session.flag_count = 0
    session.elapsed_seconds = ELAPSED_AT_END
    session.started_at = STARTED_AT
    session.ended_at = ENDED_AT
    return session


def _cell_snapshot(session: GameSession):
    return [dict(cell) for cell in session.cells]


def _reveal(session: GameSession):
    return session.reveal_cell(row=TARGET_ROW, column=TARGET_COLUMN)


def _toggle_flag(session: GameSession):
    return session.toggle_flag(row=TARGET_ROW, column=TARGET_COLUMN)


@pytest.mark.parametrize("status", ["won", "lost"])
@pytest.mark.parametrize(
    "action",
    [_reveal, _toggle_flag],
    ids=["reveal_cell", "toggle_flag"],
)
def test_board_action_after_game_end_is_refused_and_changes_nothing(status, action):
    # Given a finished game (won or lost) on a 9x9 board with 10 mines.
    # The target cell (4, 4) is hidden and holds a mine, so it is a legal
    # target for both reveal and flag if the status did not block it.
    # Every other cell is revealed and safe; flag_count is 0; the timer
    # stands at 120 seconds; ended_at is recorded.
    session = _make_finished_board(status)
    cells_before = _cell_snapshot(session)

    # When the player reveals or flags the target cell.
    with pytest.raises(Exception) as exc_info:
        action(session)

    # Then the action is refused by the rules.
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # And no cell state changed: the target is still hidden because the
    # game is over, and every other cell is still revealed.
    assert _cell_snapshot(session) == cells_before

    # And the timer is unchanged: it stays at 120 seconds.
    assert session.elapsed_seconds == ELAPSED_AT_END

    # And the session status is still the terminal status it was.
    assert session.status == status


def test_same_board_flag_is_accepted_while_in_progress():
    # Given the same 9x9 board, arranged as in progress instead of finished.
    # The target cell (4, 4) is hidden and unflagged, and flag_count is 0.
    # Nothing else blocks a flag: the status is in_progress and the cell is
    # hidden, which are the rules for toggling a flag.
    session = _make_finished_board("in_progress")
    session.ended_at = None
    session.elapsed_seconds = ELAPSED_AT_END

    # When the player flags the target cell.
    _toggle_flag(session)

    # Then the target cell becomes flagged, because a hidden cell in an
    # in-progress game can be flagged.
    target = next(
        cell
        for cell in session.cells
        if cell["row"] == TARGET_ROW and cell["column"] == TARGET_COLUMN
    )
    assert target["state"] == "flagged"

    # And flag_count rises from 0 to 1, because one cell has been flagged.
    assert session.flag_count == 1

    # And the status is still in_progress, because flagging does not end
    # the game.
    assert session.status == "in_progress"
