import copy

import pytest

from src.domain.game import Game


def _make_ready_beginner_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T10:00:00Z",
    )
    # Starting state of a newly created game: Ready, no mines laid, every cell Hidden.
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
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


def test_choosing_expert_creates_30_by_16_game_with_99_mines():
    game = _make_ready_beginner_game()

    new_game = game.change_difficulty(
        difficulty_id="expert", width=None, height=None, mine_count=None
    )

    # "expert" is a known preset: its size comes from the preset (30 wide x 16 high,
    # 99 mines), not from the custom arguments, which are all None here.
    assert new_game.difficulty_id == "expert"
    assert new_game.width == 30
    assert new_game.height == 16
    assert new_game.mine_count == 99

    # The new game is a different game, in its starting state.
    assert new_game.id != game.id
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    # Counter starts equal to the mine count: 99 - 0 flags = 99.
    assert new_game.remaining_mines == 99
    assert new_game.started_at is None
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None

    # Board: 30 x 16 = 480 cells, row-major, all Hidden, no mines before first open.
    assert len(new_game.cells) == 480
    expected_positions = [(r, c) for r in range(16) for c in range(30)]
    assert [(cell["row"], cell["column"]) for cell in new_game.cells] == expected_positions
    assert [cell["id"] for cell in new_game.cells] == [
        f"{r}-{c}" for r, c in expected_positions
    ]
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    assert all(cell["has_mine"] is False for cell in new_game.cells)
    assert all(cell["adjacent_mine_count"] == 0 for cell in new_game.cells)

    # The previous game was Ready, so a valid difficulty choice abandons it.
    assert game.status == "Abandoned"
    assert game.ended_at is not None


def test_unknown_difficulty_next_to_expert_is_refused_and_game_unchanged():
    game = _make_ready_beginner_game()
    before = copy.deepcopy(game.to_dict())

    # "Expert" (capitalised) is not one of the known ids
    # beginner / intermediate / expert / custom, so it is refused.
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="Expert", width=None, height=None, mine_count=None
        )

    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # A refused choice leaves the current game completely unchanged:
    # still Ready, same board, timer and counter.
    assert game.status == "Ready"
    assert game.difficulty_id == "beginner"
    assert game.width == 9
    assert game.height == 9
    assert game.mine_count == 10
    assert game.remaining_mines == 10
    assert game.elapsed_seconds == 0
    assert game.ended_at is None
    assert game.to_dict() == before
