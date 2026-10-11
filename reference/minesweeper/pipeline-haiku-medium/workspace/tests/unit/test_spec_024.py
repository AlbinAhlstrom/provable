from src.domain.game_session import GameSession


def _cell_at(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def test_win_does_not_require_flags():
    # Given a 2x2 board at "beginner" difficulty (the 2x2 size is set on the
    # instance, the constructor does not validate presets).
    # The constructor creates 4 hidden cells with has_mine false and count 0.
    session = GameSession(
        id="session-win-flags",
        difficulty_id="beginner",
        rows=2,
        columns=2,
        mine_count=1,
    )

    # The session is already in progress, so no random placement happens on reveal.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.elapsed_seconds = 0

    # Mine at (1, 1), still hidden and not flagged.
    mine = _cell_at(session, 1, 1)
    mine["has_mine"] = True
    mine["adjacent_mine_count"] = 0
    mine["state"] = "hidden"

    # Safe cells (0, 1) and (1, 0) are already revealed.
    # Each touches the mine, so each has adjacent_mine_count 1 and is numbered.
    for row, column in [(0, 1), (1, 0)]:
        cell = _cell_at(session, row, column)
        cell["has_mine"] = False
        cell["adjacent_mine_count"] = 1
        cell["state"] = "revealed"

    # The last safe cell (0, 0) is hidden. Its neighbours are (0, 1), (1, 0)
    # and the mine (1, 1), so its adjacent_mine_count is 1. It is numbered,
    # so revealing it spreads nothing.
    last_safe = _cell_at(session, 0, 0)
    last_safe["has_mine"] = False
    last_safe["adjacent_mine_count"] = 1
    last_safe["state"] = "hidden"

    # No cell is flagged and flag_count is 0, so the mine is not flagged.
    session.flag_count = 0

    # When the last safe cell is revealed.
    session.reveal_cell(row=0, column=0)

    # Then every safe cell is revealed, the mine is never revealed, and no flags
    # are needed, so the session is won.
    # Comment: all three safe cells are revealed and the mine stays hidden.
    assert session.status == "won"
