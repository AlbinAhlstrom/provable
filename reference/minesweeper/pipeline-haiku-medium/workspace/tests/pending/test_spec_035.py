import pytest

from src.domain.game_session import GameSession

ROWS = 4
COLUMNS = 4
MINE_COUNT = 10


def make_session_with_flags(flag_count):
    """Newly created 4x4 session with 10 mines and `flag_count` flagged cells.

    The cells list is left as the constructor creates it (16 hidden records).
    Only the first `flag_count` cells (row-major order) are changed to flagged,
    and flag_count is set to match, so the board and the counter agree.
    """
    session = GameSession(
        id="session-counter",
        difficulty_id="custom",
        rows=ROWS,
        columns=COLUMNS,
        mine_count=MINE_COUNT,
    )
    for cell in session.cells[:flag_count]:
        cell["state"] = "flagged"
    session.flag_count = flag_count
    return session


@pytest.mark.parametrize(
    "flag_count, expected_counter",
    [
        # Exactly at the zero limit: 10 mines - 10 flags = 0.
        pytest.param(10, 0, id="exactly-at-zero-limit"),
        # Just beyond the zero limit: 10 mines - 11 flags = -1.
        pytest.param(11, -1, id="just-beyond-zero-limit"),
        # The scenario itself: 10 mines - 12 flags = -2.
        pytest.param(12, -2, id="scenario-twelve-flags"),
    ],
)
def test_mine_counter_is_not_clamped_at_zero(flag_count, expected_counter):
    # Given a session with 10 mines and the given number of flagged cells
    session = make_session_with_flags(flag_count)

    # When the mine counter is read
    counter = session.mine_counter()

    # Then the counter equals mines minus flags, with no clamping at zero.
    # Working: mine_count = 10, flags = flag_count, counter = 10 - flag_count.
    # 10 flags -> 0; 11 flags -> -1; 12 flags -> -2.
    assert counter == expected_counter
