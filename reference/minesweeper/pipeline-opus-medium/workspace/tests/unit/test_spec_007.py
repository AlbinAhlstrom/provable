import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00Z"


def _ready_beginner_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at=CREATED_AT,
    )
    # Arrange the starting state explicitly: Ready, no mines laid, 81 hidden cells.
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.remaining_mines = 10
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    game.cells = [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(9)
        for column in range(9)
    ]
    return game


# Accepted cases: exactly at the lower limit (10) and exactly at the upper limit
# (W-1)*(H-1), for two different valid sizes.
@pytest.mark.parametrize(
    "width, height, mine_count",
    [
        (9, 9, 10),    # lower limit exactly: 10
        (9, 9, 64),    # upper limit exactly: (9-1)*(9-1) = 64
        (12, 10, 10),  # lower limit exactly: 10
        (12, 10, 99),  # upper limit exactly: (12-1)*(10-1) = 99
    ],
)
def test_custom_mine_count_at_limit_is_accepted(width, height, mine_count):
    game = _ready_beginner_game()

    new_game = game.change_difficulty(
        difficulty_id="custom", width=width, height=height, mine_count=mine_count
    )

    # Width 9 or 12 is within 9-30 and height 9 or 10 within 9-24, so only the
    # mine count rule decides; mine_count is exactly at a limit, so it is accepted
    # and a new custom game is returned with exactly the chosen values.
    assert new_game.id != game.id
    assert new_game.difficulty_id == "custom"
    assert new_game.width == width
    assert new_game.height == height
    assert new_game.mine_count == mine_count
    # The new game is in its starting state: Ready, no mines, counter = mine_count.
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.remaining_mines == mine_count
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert len(new_game.cells) == width * height
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    assert all(cell["has_mine"] is False for cell in new_game.cells)
    # The old game was Ready, and a valid choice abandons a Ready game.
    assert game.status == "Abandoned"


# Refused cases: one just beyond each limit, built from the accepted cases by
# changing only mine_count by one.
@pytest.mark.parametrize(
    "width, height, mine_count",
    [
        (9, 9, 9),     # just below the lower limit 10
        (9, 9, 65),    # just above the upper limit 64
        (12, 10, 9),   # just below the lower limit 10
        (12, 10, 100), # just above the upper limit 99
    ],
)
def test_custom_mine_count_beyond_limit_is_refused(width, height, mine_count):
    game = _ready_beginner_game()
    before = game.to_dict()

    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="custom", width=width, height=height, mine_count=mine_count
        )

    # Width and height are valid, so the refusal comes from mine_count lying one
    # outside 10..(W-1)*(H-1): InvalidConfigurationError is raised.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # A refused configuration leaves the current game completely unchanged:
    # still Ready, same board, timer and counter.
    assert game.status == "Ready"
    assert game.difficulty_id == "beginner"
    assert game.width == 9
    assert game.height == 9
    assert game.mine_count == 10
    assert game.remaining_mines == 10
    assert game.elapsed_seconds == 0
    assert game.to_dict() == before
