import pytest

from src.domain.game import Game


def _cells(width, height):
    return [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(height)
        for column in range(width)
    ]


def _ready_beginner_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T10:00:00Z",
    )
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.cells = _cells(9, 9)
    game.events = []
    return game


@pytest.mark.parametrize("height", [9, 24])
def test_custom_height_at_limits_is_accepted(height):
    game = _ready_beginner_game()

    new_game = game.change_difficulty(
        difficulty_id="custom", width=9, height=height, mine_count=10
    )

    # Width 9 is within 9-30; mine_count 10 is within 10..(9-1)*(height-1)
    # (64 for height 9, 184 for height 24); height is exactly at a limit of 9-24,
    # so the configuration is valid and a new custom game is returned.
    assert new_game.difficulty_id == "custom"
    assert new_game.width == 9
    assert new_game.height == height
    assert new_game.mine_count == 10
    # The new game is in its starting state: Ready, counter equals mine_count,
    # one cell per position (9 wide x height high).
    assert new_game.status == "Ready"
    assert new_game.remaining_mines == 10
    assert len(new_game.cells) == 9 * height
    assert new_game.id != game.id
    # The valid choice abandons the current Ready game.
    assert game.status == "Abandoned"


@pytest.mark.parametrize("height", [8, 25])
def test_custom_height_just_beyond_limits_is_refused(height):
    game = _ready_beginner_game()
    before = game.to_dict()

    # Same width 9 and mine_count 10 as the accepted cases; mine_count 10 stays
    # within 10..(9-1)*(height-1) (56 for height 8, 192 for height 25), so only
    # the height (just outside 9-24) makes the configuration invalid.
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="custom", width=9, height=height, mine_count=10
        )

    # Out-of-range Custom height raises InvalidConfigurationError.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # The refusal leaves the current game completely unchanged: still Ready,
    # same board, counter and timer.
    assert game.status == "Ready"
    assert game.difficulty_id == "beginner"
    assert game.height == 9
    assert game.to_dict() == before
