import copy

import pytest

from src.domain.game import Game

CREATED_AT = "2024-01-01T00:00:00Z"
STARTED_AT = "2024-01-01T00:00:05Z"


def _grid(width, height):
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


def _beginner_game(status):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at=CREATED_AT,
    )
    game.cells = _grid(9, 9)
    game.flags_placed = 0
    game.remaining_mines = 10
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.events = []
    if status == "Ready":
        game.status = "Ready"
        game.mines_laid = False
        game.elapsed_seconds = 0
    else:
        # Playing: 10 mines laid far from the top-left corner (whole bottom row
        # plus (7, 8)); cell (0, 0) has been opened and has no mine neighbours.
        game.status = "Playing"
        game.mines_laid = True
        game.started_at = STARTED_AT
        game.elapsed_seconds = 12
        mine_positions = [(8, c) for c in range(9)] + [(7, 8)]
        for cell in game.cells:
            if (cell["row"], cell["column"]) in mine_positions:
                cell["has_mine"] = True
        game.cells[0]["state"] = "Opened"
        game.cells[0]["adjacent_mine_count"] = 0
    return game


def _assert_fresh_ready_game(new_game, old_id, difficulty_id, width, height, mine_count):
    # A brand-new game: new id, chosen settings, starting state with all cells Hidden.
    assert isinstance(new_game, Game)
    assert new_game.id != old_id
    assert new_game.difficulty_id == difficulty_id
    assert new_game.width == width
    assert new_game.height == height
    assert new_game.mine_count == mine_count
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert new_game.remaining_mines == mine_count
    assert new_game.started_at is None
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None
    assert len(new_game.cells) == width * height
    expected_ids = [f"{r}-{c}" for r in range(height) for c in range(width)]
    assert [cell["id"] for cell in new_game.cells] == expected_ids
    for cell in new_game.cells:
        assert cell["state"] == "Hidden"
        assert cell["has_mine"] is False
        assert cell["adjacent_mine_count"] == 0


@pytest.mark.parametrize("status", ["Ready", "Playing"])
@pytest.mark.parametrize(
    "difficulty_id,width,height,mine_count",
    [
        ("intermediate", 16, 16, 40),
        ("expert", 30, 16, 99),
        ("custom", 9, 9, 10),
    ],
)
def test_change_difficulty_abandons_current_and_returns_new_ready_game(
    status, difficulty_id, width, height, mine_count
):
    game = _beginner_game(status)
    old_elapsed = game.elapsed_seconds

    new_game = game.change_difficulty(
        difficulty_id=difficulty_id, width=width, height=height, mine_count=mine_count
    )

    # The current game was Ready/Playing; a valid choice moves it Ready/Playing -> Abandoned.
    assert game.status == "Abandoned"
    # Abandoned games are never scored; the old game keeps its own settings and timer frozen.
    assert game.difficulty_id == "beginner"
    assert game.width == 9 and game.height == 9 and game.mine_count == 10
    assert game.elapsed_seconds == old_elapsed
    # The returned game uses exactly the chosen settings in its starting state.
    _assert_fresh_ready_game(new_game, "game-1", difficulty_id, width, height, mine_count)


@pytest.mark.parametrize("status", ["Ready", "Playing"])
def test_change_difficulty_with_custom_width_below_limit_is_refused_and_game_unchanged(status):
    game = _beginner_game(status)
    before = copy.deepcopy(game.to_dict())

    # Same request as the accepted custom 9x9/10 case, only width 8 (< 9) differs.
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(difficulty_id="custom", width=8, height=9, mine_count=10)

    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # Refusal leaves the current game completely unchanged (status, board, timer, counter).
    assert game.status == status
    assert game.to_dict() == before


def test_change_difficulty_with_unknown_difficulty_is_refused_and_game_unchanged():
    game = _beginner_game("Ready")
    before = copy.deepcopy(game.to_dict())

    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(difficulty_id="legendary", width=9, height=9, mine_count=10)

    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    assert game.status == "Ready"
    assert game.to_dict() == before
