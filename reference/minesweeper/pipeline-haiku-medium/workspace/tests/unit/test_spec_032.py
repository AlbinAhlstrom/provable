import pytest

from src.domain.game_session import GameSession


ROWS = 9
COLUMNS = 9
MINE_COUNT = 10
TARGET_ROW = 4
TARGET_COLUMN = 4


def build_cells(rows, columns):
    """One hidden, mine-free record for every position, as a new session holds them."""
    return [
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


def make_session(status):
    """Beginner-sized session with a hidden board, in the given status.

    Timestamps are fixed ISO strings. elapsed_seconds is 120 so that any
    accidental timer change would be visible.
    """
    session = GameSession(
        id="session-1",
        difficulty_id="beginner",
        rows=ROWS,
        columns=COLUMNS,
        mine_count=MINE_COUNT,
    )
    session.cells = build_cells(ROWS, COLUMNS)
    session.status = status
    session.flag_count = 0
    session.elapsed_seconds = 120
    session.started_at = "2024-01-01T10:00:00"
    if status in ("won", "lost"):
        session.ended_at = "2024-01-01T10:02:00"
    else:
        session.ended_at = None
    return session


def cell_at(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def call_action(session, action):
    if action == "reveal_cell":
        session.reveal_cell(row=TARGET_ROW, column=TARGET_COLUMN)
    elif action == "toggle_flag":
        session.toggle_flag(row=TARGET_ROW, column=TARGET_COLUMN)
    elif action == "abandon_game":
        session.abandon_game()
    else:
        raise AssertionError(f"unknown action {action}")


@pytest.mark.parametrize("ended_status", ["won", "lost"])
@pytest.mark.parametrize("action", ["reveal_cell", "toggle_flag", "abandon_game"])
def test_actions_other_than_new_game_are_refused_and_status_remains_terminal(ended_status, action):
    session = make_session(ended_status)
    ended_at_before = session.ended_at

    with pytest.raises(Exception) as exc_info:
        call_action(session, action)

    # Rules: reveal and flag are allowed only while ready or in_progress, and
    # abandon is allowed only while ready or in_progress. The status is terminal,
    # so every one of these three actions is refused with ActionNotAllowedError.
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # The status stays at the terminal value it had before the attempt.
    assert session.status == ended_status

    # The refused action changed nothing else: the target cell is still hidden
    # (a reveal or flag would otherwise have changed it), no flag was added,
    # the end time is unchanged, and the elapsed timer is still 120.
    assert cell_at(session, TARGET_ROW, TARGET_COLUMN)["state"] == "hidden"
    assert session.flag_count == 0
    assert session.ended_at == ended_at_before
    assert session.elapsed_seconds == 120


def test_same_flag_action_succeeds_while_in_progress():
    # Control for the refused flag case above: identical board, identical target
    # cell, identical elapsed time, only the status differs. The status is
    # in_progress, which allows toggle_flag on a hidden cell. The flag is placed,
    # so the refusal above is decided by the terminal status alone.
    session = make_session("in_progress")

    session.toggle_flag(row=TARGET_ROW, column=TARGET_COLUMN)

    # The hidden target cell becomes flagged, and flag_count rises from 0 to 1.
    assert cell_at(session, TARGET_ROW, TARGET_COLUMN)["state"] == "flagged"
    assert session.flag_count == 1
    # Flagging does not end the game or change the timer.
    assert session.status == "in_progress"
    assert session.elapsed_seconds == 120


def test_same_abandon_action_succeeds_while_in_progress():
    # Control for the refused abandon case above: the same board, with status
    # in_progress. Abandon is allowed from in_progress, so it succeeds and
    # ends the game as abandoned. The refusal above is therefore decided by the
    # terminal status alone.
    session = make_session("in_progress")

    session.abandon_game()

    # The status becomes abandoned, and ended_at is recorded. Before the call
    # ended_at was None, so the recorded value is a new value and is not None.
    assert session.status == "abandoned"
    assert session.ended_at is not None
    # elapsed_seconds stops at its current value of 120.
    assert session.elapsed_seconds == 120
