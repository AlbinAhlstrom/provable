import pytest

from src.domain.game_session import GameSession


ROWS = 9
COLUMNS = 9
MINE_COUNT = 10
DIFFICULTY_ID = "beginner"


def build_cells(rows, columns, revealed, flagged, mines):
    """One record per board position, every key present, state and has_mine set per arrangement."""
    cells = []
    for row in range(rows):
        for column in range(columns):
            position = (row, column)
            if position in revealed:
                state = "revealed"
            elif position in flagged:
                state = "flagged"
            else:
                state = "hidden"
            cells.append(
                {
                    "id": f"cell-{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": position in mines,
                    "adjacent_mine_count": 0,
                    "state": state,
                }
            )
    return cells


@pytest.mark.parametrize("terminal_status", ["won", "lost", "abandoned"])
def test_new_game_returns_to_ready(terminal_status):
    # Given a 9x9 beginner session that has ended with the given terminal status.
    session = GameSession(
        id="game-1",
        difficulty_id=DIFFICULTY_ID,
        rows=ROWS,
        columns=COLUMNS,
        mine_count=MINE_COUNT,
    )
    # Board: 81 cells, one per position. Cell (0,0) is revealed, cell (0,1) is flagged,
    # and ten mines sit in the bottom two rows (first ten positions of rows 7 and 8).
    # The flag count matches the single flagged cell.
    mines = {(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, 0)}
    session.cells = build_cells(
        ROWS,
        COLUMNS,
        revealed={(0, 0)},
        flagged={(0, 1)},
        mines=mines,
    )
    session.status = terminal_status
    session.flag_count = 1
    session.elapsed_seconds = 120
    session.started_at = "2025-01-01T10:00:00"
    session.ended_at = "2025-01-01T10:02:00"

    # When the player starts a new game at the same difficulty.
    session.start_new_game(
        difficulty_id=DIFFICULTY_ID,
        rows=ROWS,
        columns=COLUMNS,
        mine_count=MINE_COUNT,
    )

    # Then the status is ready.
    # Rule: start_new_game is allowed from any status and sets status to ready.
    assert session.status == "ready"

    # Then the board still has one record per position: 9 * 9 = 81 cells.
    # Rule: the board is replaced, not shrunk or grown, for the same difficulty.
    assert len(session.cells) == ROWS * COLUMNS

    # Then every cell is hidden.
    # Rule: start_new_game makes every cell hidden; the revealed cell (0,0)
    # and the flagged cell (0,1) from the old game are reset as well.
    assert all(cell["state"] == "hidden" for cell in session.cells)

    # Then no mine is placed on the new board.
    # Rule: mines are placed only after the first reveal, so has_mine is false everywhere.
    assert all(cell["has_mine"] is False for cell in session.cells)

    # Then flag_count is 0.
    # Rule: start_new_game sets flag_count to 0; the old single flag is cleared.
    assert session.flag_count == 0

    # Then elapsed_seconds is 0.
    # Rule: start_new_game resets the timer; the old 120 seconds are cleared.
    assert session.elapsed_seconds == 0
