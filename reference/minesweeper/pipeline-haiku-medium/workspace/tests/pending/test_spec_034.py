import pytest

from src.domain.game_session import GameSession


def make_session_with_flags(mine_count, flagged_count):
    # Given a session of the Beginner preset (9 rows, 9 columns) with the given mine count.
    # The cell list keeps one record per position (81 records), all hidden with no mine.
    session = GameSession(
        id="session-1",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=mine_count,
    )
    # The game is under way, so the session is in an ordinary playable status.
    session.status = "in_progress"
    session.started_at = "2024-01-01T10:00:00"
    # Place `flagged_count` flags on the first cells in board order. The flag_count field
    # is kept consistent with the number of cells in the flagged state.
    for cell in session.cells[:flagged_count]:
        cell["state"] = "flagged"
    session.flag_count = flagged_count
    return session


@pytest.mark.parametrize(
    "mine_count, flagged_count, expected_counter",
    [
        # Scenario example: 10 mines, 3 flags. Counter = 10 - 3 = 7.
        (10, 3, 7),
        # Exactly at the limit: flags equal mines. Counter = 10 - 10 = 0.
        (10, 10, 0),
        # Just beyond the limit: one flag more than mines. Counter = 10 - 11 = -1.
        (10, 11, -1),
    ],
)
def test_mine_counter_equals_mines_minus_flags(mine_count, flagged_count, expected_counter):
    # Given a session with `mine_count` mines and `flagged_count` flagged cells.
    session = make_session_with_flags(mine_count, flagged_count)

    # When the mine counter is read.
    counter = session.mine_counter()

    # Then the counter equals mine_count minus flag_count:
    # mines = mine_count, flags = flagged_count, so the expected value is the one
    # worked out in the parametrization above for this exact state.
    assert counter == expected_counter
