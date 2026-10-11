import pytest

from src.domain.game_session import GameSession

ROWS = 9
COLUMNS = 9
MINE_POSITIONS = [(8, c) for c in range(COLUMNS)] + [(7, 8)]  # 10 mines, none near (0, 0)


def make_cells(rows, columns):
    return [
        {
            "id": f"cell-{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "hidden",
        }
        for r in range(rows)
        for c in range(columns)
    ]


def place_mines_and_count(cells, rows, columns, mine_positions):
    mines = set(mine_positions)
    for cell in cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in mines
    for cell in cells:
        r, c = cell["row"], cell["column"]
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < columns and (nr, nc) in mines:
                    count += 1
        cell["adjacent_mine_count"] = count


def cell_at(session, row, column):
    return next(
        cell for cell in session.cells
        if cell["row"] == row and cell["column"] == column
    )


def in_progress_session():
    session = GameSession(
        id="game-1",
        difficulty_id="beginner",
        rows=ROWS,
        columns=COLUMNS,
        mine_count=10,
    )
    session.cells = make_cells(ROWS, COLUMNS)
    place_mines_and_count(session.cells, ROWS, COLUMNS, MINE_POSITIONS)
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.elapsed_seconds = 0
    return session


def test_flagged_cell_reveal_is_refused_and_cell_stays_flagged():
    session = in_progress_session()
    # Cell (0, 0) is flagged: it is safe (no mine), adjacency 0, and it is
    # the only flagged cell, so flag_count is 1. The game is in progress,
    # so the only thing that can refuse the reveal is the flag on the cell.
    cell_at(session, 0, 0)["state"] = "flagged"
    session.flag_count = 1

    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=0, column=0)
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # The refused reveal must not move the cell: it is still flagged.
    assert cell_at(session, 0, 0)["state"] == "flagged"
    # Nothing else changes: status stays in_progress, the flag count stays 1,
    # and the timer stays at 0.
    assert session.status == "in_progress"
    assert session.flag_count == 1
    assert session.elapsed_seconds == 0


def test_revealed_cell_flag_toggle_is_refused_and_cell_stays_revealed():
    session = in_progress_session()
    # Cell (0, 0) is revealed: it is safe, adjacency 0, and no flags exist,
    # so flag_count is 0. The game is in progress, so the only thing that
    # can refuse the flag action is the revealed state of the cell.
    cell_at(session, 0, 0)["state"] = "revealed"
    session.flag_count = 0

    with pytest.raises(Exception) as exc_info:
        session.toggle_flag(row=0, column=0)
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"

    # The refused flag action must not move the cell: it is still revealed,
    # not flagged.
    assert cell_at(session, 0, 0)["state"] == "revealed"
    # Nothing else changes: status stays in_progress, the flag count stays 0,
    # and the timer stays at 0.
    assert session.status == "in_progress"
    assert session.flag_count == 0
    assert session.elapsed_seconds == 0
