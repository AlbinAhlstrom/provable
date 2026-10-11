import pytest

from src.domain.game_session import GameSession


BEGINNER_MINES = [(8, c) for c in range(9)] + [(7, 8)]  # 10 mines, all far from (0, 0)


def _index(session):
    return {(cell["row"], cell["column"]): cell for cell in session.cells}


def _neighbours(row, column, rows, columns):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (dr, dc) == (0, 0):
                continue
            r, c = row + dr, column + dc
            if 0 <= r < rows and 0 <= c < columns:
                result.append((r, c))
    return result


def _place_mines(session, positions):
    """Set has_mine on the existing cells and recompute adjacent_mine_count."""
    index = _index(session)
    mine_set = set(positions)
    for (r, c), cell in index.items():
        cell["has_mine"] = (r, c) in mine_set
    for (r, c), cell in index.items():
        cell["adjacent_mine_count"] = sum(
            1 for nb in _neighbours(r, c, session.rows, session.columns) if nb in mine_set
        )


def _states(session):
    return {(cell["row"], cell["column"]): cell["state"] for cell in session.cells}


def test_constructor_creates_ready_hidden_board():
    # Given: a session created with only its required fields and nothing called on it
    session = GameSession(id="s1", difficulty_id="beginner", rows=9, columns=9, mine_count=10)

    # When: nothing is called (construction only)

    # Then: a new session starts in the "ready" status
    assert session.status == "ready"
    # Then: no flags have been placed, so flag_count is 0
    assert session.flag_count == 0
    # Then: the timer has not run, so elapsed_seconds is 0
    assert session.elapsed_seconds == 0
    # Then: no timer start was recorded, so started_at is null
    assert session.started_at is None
    # Then: no game has ended, so ended_at is null
    assert session.ended_at is None
    # Then: rows, columns and mine_count come straight from the 9x9 beginner preset
    assert session.rows == 9
    assert session.columns == 9
    assert session.mine_count == 10
    # Then: 9 * 9 = 81 cell records exist, one per position
    assert len(session.cells) == 81
    # Then: the records cover exactly the positions 0..8 by 0..8, each once
    positions = {(cell["row"], cell["column"]) for cell in session.cells}
    assert positions == {(r, c) for r in range(9) for c in range(9)}
    for cell in session.cells:
        # Then: each cell is hidden, since nothing has been revealed or flagged
        assert cell["state"] == "hidden"
        # Then: no mine is placed until the first reveal
        assert cell["has_mine"] is False
        # Then: no adjacency is computed until mines are placed
        assert cell["adjacent_mine_count"] == 0


def test_start_new_game_replaces_board_with_fresh_hidden_expert_board():
    # Given: a won expert game with a timer and a recorded end, one revealed cell and one mine
    session = GameSession(id="s1", difficulty_id="expert", rows=16, columns=30, mine_count=99)
    session.status = "won"
    session.elapsed_seconds = 120
    session.started_at = "2025-01-01T10:00:00"
    session.ended_at = "2025-01-01T10:02:00"
    session.flag_count = 0
    _index(session)[(0, 0)]["state"] = "revealed"
    _place_mines(session, [(5, 5)])

    # Given: a second identical game, used for the refused call
    refused = GameSession(id="s2", difficulty_id="expert", rows=16, columns=30, mine_count=99)
    refused.status = "won"
    refused.elapsed_seconds = 120
    refused.started_at = "2025-01-01T10:00:00"
    refused.ended_at = "2025-01-01T10:02:00"
    _index(refused)[(0, 0)]["state"] = "revealed"
    _place_mines(refused, [(5, 5)])

    # When: a start with mine_count 98, which does not match the expert preset
    with pytest.raises(Exception) as exc_info:
        refused.start_new_game(difficulty_id="expert", rows=16, columns=30, mine_count=98)

    # Then: the refusal is an InvalidDifficultyError
    assert type(exc_info.value).__name__ == "InvalidDifficultyError"
    # Then: the refused game keeps its won status
    assert refused.status == "won"

    # When: the valid expert start, which matches the preset 16 x 30 with 99 mines
    session.start_new_game(difficulty_id="expert", rows=16, columns=30, mine_count=99)

    # Then: the status becomes ready
    assert session.status == "ready"
    # Then: flag_count and elapsed_seconds are reset to 0
    assert session.flag_count == 0
    assert session.elapsed_seconds == 0
    # Then: started_at and ended_at are cleared
    assert session.started_at is None
    assert session.ended_at is None
    # Then: the object's fields show the expert preset
    assert session.rows == 16
    assert session.columns == 30
    assert session.mine_count == 99
    # Then: the board has 16 * 30 = 480 cells
    assert len(session.cells) == 480
    for cell in session.cells:
        # Then: every cell is hidden, including the one that was revealed before
        assert cell["state"] == "hidden"
        # Then: no mine is placed on the new board
        assert cell["has_mine"] is False


def test_reveal_cell_refuses_flagged_cell_then_places_mines_on_first_safe_reveal():
    # Given: a ready 9x9 beginner session where cell (0, 0) is flagged (so flag_count is 1)
    session = GameSession(id="s1", difficulty_id="beginner", rows=9, columns=9, mine_count=10)
    _index(session)[(0, 0)]["state"] = "flagged"
    session.flag_count = 1

    # When: the player reveals the flagged cell (0, 0)
    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=0, column=0)

    # Then: the refusal is an ActionNotAllowedError
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"
    # Then: the cell stays flagged
    assert _index(session)[(0, 0)]["state"] == "flagged"
    # Then: the session stays ready and the flag count is unchanged
    assert session.status == "ready"
    assert session.flag_count == 1
    # Then: no mines are placed, because the refused reveal was not a first reveal
    assert all(cell["has_mine"] is False for cell in session.cells)
    # Then: the timer has not started
    assert session.started_at is None

    # When: the player reveals the hidden, unflagged cell (4, 4), the first reveal
    session.reveal_cell(row=4, column=4)

    # Then: the session status becomes in_progress
    assert session.status == "in_progress"
    # Then: the start time is recorded (a value, not null)
    assert session.started_at is not None
    # Then: the game has not ended
    assert session.ended_at is None
    # Then: cell (4, 4) is now revealed
    assert _index(session)[(4, 4)]["state"] == "revealed"
    # Then: the first revealed cell is never a mine
    assert _index(session)[(4, 4)]["has_mine"] is False
    # Then: exactly mine_count (10) cells carry a mine
    assert sum(1 for cell in session.cells if cell["has_mine"]) == 10
    # Then: the flag on (0, 0) is still there, since flags are left alone
    assert _index(session)[(0, 0)]["state"] == "flagged"
    # Then: the flag count is unchanged by the reveal
    assert session.flag_count == 1
    # Then: each cell's adjacent_mine_count equals the number of mine neighbours it has
    index = _index(session)
    for (r, c), cell in index.items():
        expected = sum(
            1 for nb in _neighbours(r, c, 9, 9) if index[nb]["has_mine"]
        )
        assert cell["adjacent_mine_count"] == expected


def test_toggle_flag_refuses_revealed_cell_then_flags_and_unflags_hidden_cell():
    # Given: an in-progress 9x9 beginner game with 10 mines in row 8 and at (7, 8)
    session = GameSession(id="s1", difficulty_id="beginner", rows=9, columns=9, mine_count=10)
    session.status = "in_progress"
    session.elapsed_seconds = 30
    session.started_at = "2025-01-01T10:00:00"
    _place_mines(session, BEGINNER_MINES)
    # Given: cell (0, 1) is revealed, which is the refused case
    _index(session)[(0, 1)]["state"] = "revealed"

    # When: the player flags the revealed cell (0, 1)
    with pytest.raises(Exception) as exc_info:
        session.toggle_flag(row=0, column=1)

    # Then: the refusal is an ActionNotAllowedError
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"
    # Then: the revealed cell stays revealed
    assert _index(session)[(0, 1)]["state"] == "revealed"
    # Then: the flag count is unchanged
    assert session.flag_count == 0

    # Given: a snapshot of every cell state before the accepted toggle
    before = _states(session)

    # When: the player flags the hidden cell (0, 0)
    session.toggle_flag(row=0, column=0)

    # Then: cell (0, 0) becomes flagged
    assert _index(session)[(0, 0)]["state"] == "flagged"
    # Then: flag_count rises by one
    assert session.flag_count == 1
    # Then: no other cell changes state, since flags never reveal
    after = _states(session)
    for pos, state in before.items():
        if pos != (0, 0):
            assert after[pos] == state
    # Then: the status stays in_progress and the timer is untouched
    assert session.status == "in_progress"
    assert session.elapsed_seconds == 30
    assert session.started_at == "2025-01-01T10:00:00"

    # When: the player toggles the flag on (0, 0) again
    session.toggle_flag(row=0, column=0)

    # Then: the cell returns to hidden
    assert _index(session)[(0, 0)]["state"] == "hidden"
    # Then: flag_count falls back to 0
    assert session.flag_count == 0


def test_abandon_game_refuses_won_game_then_abandons_in_progress_game():
    # Given: an in-progress 9x9 beginner game, elapsed 75 seconds, started at a fixed time
    session = GameSession(id="s1", difficulty_id="beginner", rows=9, columns=9, mine_count=10)
    session.status = "in_progress"
    session.elapsed_seconds = 75
    session.started_at = "2025-01-01T10:00:00"
    _place_mines(session, BEGINNER_MINES)

    # Given: an identical game that is already won, used for the refused call
    refused = GameSession(id="s2", difficulty_id="beginner", rows=9, columns=9, mine_count=10)
    refused.status = "won"
    refused.elapsed_seconds = 75
    refused.started_at = "2025-01-01T10:00:00"
    _place_mines(refused, BEGINNER_MINES)

    # When: the player abandons the won game
    with pytest.raises(Exception) as exc_info:
        refused.abandon_game()

    # Then: the refusal is an ActionNotAllowedError
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"
    # Then: the won game keeps its status
    assert refused.status == "won"
    # Then: no end is recorded and the timer is unchanged
    assert refused.ended_at is None
    assert refused.elapsed_seconds == 75

    # When: the player abandons the in-progress game
    session.abandon_game()

    # Then: the status becomes abandoned, with no win or loss result
    assert session.status == "abandoned"
    # Then: ended_at is recorded (a value, not null)
    assert session.ended_at is not None
    # Then: elapsed_seconds stops at its current value of 75
    assert session.elapsed_seconds == 75
    # Then: the recorded start time is unchanged
    assert session.started_at == "2025-01-01T10:00:00"
