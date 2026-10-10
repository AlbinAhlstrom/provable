import pytest

from src.domain.game_session import GameSession


def make_cell(row, column, has_mine, adjacent_mine_count, state):
    return {
        "id": f"c{row}{column}",
        "row": row,
        "column": column,
        "has_mine": has_mine,
        "adjacent_mine_count": adjacent_mine_count,
        "state": state,
    }


def build_session_one_safe_cell_left():
    # 2x2 board, one mine at (1, 1). Safe cells: (0, 0), (0, 1), (1, 0).
    # (0, 0) and (0, 1) are already revealed; (1, 0) is the last hidden safe cell.
    # Every safe cell's count is 1 because its only mine neighbour is (1, 1).
    # The mine cell's count is 0 because it has no mine neighbours.
    session = GameSession(
        id="s1",
        difficulty_id="custom",
        rows=2,
        columns=2,
        mine_count=1,
    )
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.cells = [
        make_cell(0, 0, False, 1, "revealed"),
        make_cell(0, 1, False, 1, "revealed"),
        make_cell(1, 0, False, 1, "hidden"),
        make_cell(1, 1, True, 0, "hidden"),
    ]
    return session


def test_revealing_last_hidden_safe_cell_wins_game():
    session = build_session_one_safe_cell_left()

    session.reveal_cell(row=1, column=0)

    # Only safe cell (1, 0) was hidden; revealing it leaves no safe cell hidden,
    # so the game is won. Its count is 1 and it is not zero, so no spread occurs.
    assert session.status == "won"
    # The win is a terminal result, so the end time is recorded.
    assert session.ended_at is not None
    # The revealed cell is now open.
    assert session.cells[2]["state"] == "revealed"
    # The mine at (1, 1) stays hidden and does not block the win.
    assert session.cells[3]["state"] == "hidden"
    assert session.cells[3]["has_mine"] is True
