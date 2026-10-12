import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00+00:00"


def make_ready_beginner_game():
    # A fresh Ready beginner game: 9x9, 10 mines, nothing opened, no flags.
    return Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at=CREATED_AT,
    )


@pytest.mark.parametrize("width", [9, 30])
def test_custom_width_at_limits_is_accepted(width):
    game = make_ready_beginner_game()

    # Height 9 is inside 9..24. Mine count 10 is inside 10..(W-1)*(H-1):
    # for W=9: 8*8=64, for W=30: 29*8=232, so 10 is valid in both cases.
    # Only the width decides the outcome.
    new_game = game.change_difficulty(
        difficulty_id="custom", width=width, height=9, mine_count=10
    )

    # Width 9 and 30 are exactly at the inclusive limits -> accepted,
    # a new game is returned with the chosen configuration.
    assert new_game.width == width
    assert new_game.height == 9
    assert new_game.mine_count == 10
    assert new_game.difficulty_id == "custom"
    # The new game is in its starting state.
    assert new_game.status == "Ready"
    assert new_game.remaining_mines == 10
    assert new_game.id != game.id
    # The current game was Ready, a valid change abandons it.
    assert game.status == "Abandoned"


@pytest.mark.parametrize("width", [8, 31])
def test_custom_width_just_outside_limits_is_refused(width):
    game = make_ready_beginner_game()
    before = game.to_dict()

    # Same height (9) and mine count (10) as the accepted case; only the
    # width changes: 8 is just below 9, 31 is just above 30 -> refused.
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="custom", width=width, height=9, mine_count=10
        )

    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # A refused configuration leaves the current game completely unchanged:
    # still Ready, still 9x9 beginner with 10 mines.
    assert game.status == "Ready"
    assert game.width == 9
    assert game.difficulty_id == "beginner"
    assert game.to_dict() == before
