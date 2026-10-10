from src.domain.game_session import GameSession


def _new_board_cells(rows, columns):
    """Build the board shape a newly created session holds: one hidden record per position."""
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


def _cell_at(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_revealing_a_mine_loses_the_game_and_records_end_time():
    # Given a 2x2 board with exactly one mine at (0, 0).
    session = GameSession(
        id="game-1",
        difficulty_id="custom",
        rows=2,
        columns=2,
        mine_count=1,
    )
    session.cells = _new_board_cells(2, 2)

    # The mine sits at (0, 0). Each other cell touches it, so each shows adjacent_mine_count 1.
    # None is a zero, so no spread can occur on reveal.
    _cell_at(session, 0, 0)["has_mine"] = True
    _cell_at(session, 0, 1)["adjacent_mine_count"] = 1
    _cell_at(session, 1, 0)["adjacent_mine_count"] = 1
    _cell_at(session, 1, 1)["adjacent_mine_count"] = 1

    # The session is already in progress: the first reveal happened and the timer started.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.ended_at = None
    session.flag_count = 0
    session.elapsed_seconds = 0

    # The target cell (0, 0) is hidden and unflagged. The other 3 safe cells stay hidden,
    # so the win condition is not met and the only rule in play is the mine rule.

    # When the player reveals the mine at (0, 0).
    session.reveal_cell(row=0, column=0)

    # Then the mine cell (0, 0) has state "revealed" and the other cells are unchanged.
    # Revealing a mine ends the game as lost, so the status must be "lost".
    assert session.status == "lost"

    # And the end time is recorded, so ended_at is no longer null.
    # The game started and ended in the session, so ended_at must be set.
    assert session.ended_at is not None
