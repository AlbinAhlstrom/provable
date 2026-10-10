import pytest

from src.domain.game_session import GameSession


def cell_at(session, row, column):
    for cell in session.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at ({row}, {column})")


def build_session_with_flag_next_to_zero():
    # Constructed fresh: a 3x3 board with 9 hidden cells, no mines placed yet.
    session = GameSession(
        id="session-spread-skips-flag",
        difficulty_id="beginner",
        rows=3,
        columns=3,
        mine_count=1,
    )
    # Arrange the board by hand so no random placement happens on reveal.
    # Mine at (2,2). Numbers come from its neighbours:
    #   (1,1), (1,2), (2,1) touch the mine and show 1.
    #   every other safe cell touches no mine and shows 0.
    counts = {
        (0, 0): 0, (0, 1): 0, (0, 2): 0,
        (1, 0): 0, (1, 1): 1, (1, 2): 1,
        (2, 0): 0, (2, 1): 1, (2, 2): 0,
    }
    for cell in session.cells:
        key = (cell["row"], cell["column"])
        cell["has_mine"] = key == (2, 2)
        cell["adjacent_mine_count"] = counts[key]
        cell["state"] = "hidden"

    # The player has flagged the safe cell (1,2), which borders the zero cell (0,1).
    cell_at(session, 1, 2)["state"] = "flagged"
    session.flag_count = 1

    # The game is already running, so the first-reveal placement does not happen.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    session.elapsed_seconds = 0
    return session


def test_spread_leaves_flagged_neighbour_flagged_and_hidden():
    # Given a zero-count cell (0,0) next to the flagged cell (1,2) via the zero cell (0,1)
    session = build_session_with_flag_next_to_zero()

    # When the zero-count cell (0,0) is revealed
    session.reveal_cell(row=0, column=0)

    # Then the flagged cell (1,2) remains flagged:
    # (0,0) is zero, so the spread reaches (0,1), (1,0), (1,1).
    # (0,1) is zero and would reach (1,2), but (1,2) is flagged, so the spread skips it.
    assert cell_at(session, 1, 2)["state"] == "flagged"

    # And the flag count is unchanged, since a reveal does not touch flags.
    assert session.flag_count == 1

    # And the zero cell that was revealed is open.
    assert cell_at(session, 0, 0)["state"] == "revealed"

    # And the game is not won, because the safe cell (1,2) is still not revealed.
    assert session.status == "in_progress"


def test_reveal_of_flagged_cell_next_to_zero_is_refused():
    # Given the same board, where the flagged cell (1,2) is the target of a direct reveal
    session = build_session_with_flag_next_to_zero()

    # When the player attempts to reveal the flagged cell directly
    # Then the rules refuse it and the flag stays in place
    with pytest.raises(Exception) as exc_info:
        session.reveal_cell(row=1, column=2)
    assert type(exc_info.value).__name__ == "ActionNotAllowedError"
    assert cell_at(session, 1, 2)["state"] == "flagged"
