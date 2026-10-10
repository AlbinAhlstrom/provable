import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-01T10:00:00+00:00"


def _make_ready_game(game_id, difficulty_id, width, height, mine_count):
    game = Game(
        id=game_id,
        difficulty_id=difficulty_id,
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at=CREATED_AT,
    )
    # Starting state of a newly created game: Ready, no mines laid, all cells Hidden.
    game.status = "Ready"
    game.mines_laid = False
    game.flags_placed = 0
    game.elapsed_seconds = 0
    game.remaining_mines = mine_count
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
        for row in range(height)
        for column in range(width)
    ]
    return game


@pytest.mark.parametrize(
    "start_difficulty, start_width, start_height, start_mines",
    [
        ("intermediate", 16, 16, 40),
        ("expert", 30, 16, 99),
    ],
)
@pytest.mark.parametrize(
    "given_width, given_height, given_mines",
    [
        # exactly the Beginner values
        (9, 9, 10),
        # one beyond each Beginner value: the preset ignores them and stays 9x9 with 10
        (10, 10, 11),
    ],
)
def test_choosing_beginner_creates_9_by_9_game_with_10_mines(
    start_difficulty,
    start_width,
    start_height,
    start_mines,
    given_width,
    given_height,
    given_mines,
):
    game = _make_ready_game("game-1", start_difficulty, start_width, start_height, start_mines)

    new_game = game.change_difficulty(
        difficulty_id="beginner",
        width=given_width,
        height=given_height,
        mine_count=given_mines,
    )

    # Beginner preset: difficulty_id 'beginner', 9 wide, 9 high, 10 mines, whatever
    # width/height/mine_count were passed (those are used only for Custom).
    assert new_game.difficulty_id == "beginner"
    assert new_game.width == 9
    assert new_game.height == 9
    assert new_game.mine_count == 10

    # The new game is in its starting state: Ready, counter = mine_count = 10,
    # nothing flagged, timer 0, no mines laid.
    assert new_game.status == "Ready"
    assert new_game.remaining_mines == 10
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert new_game.mines_laid is False

    # 9 x 9 = 81 cells in row-major order, all Hidden and mine-free before the first open.
    assert len(new_game.cells) == 81
    assert new_game.cells[0]["id"] == "0-0"
    assert new_game.cells[-1]["id"] == "8-8"
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    assert all(cell["has_mine"] is False for cell in new_game.cells)

    # It is a new game with a new id.
    assert new_game.id != "game-1"

    # The previous game was Ready, so a valid difficulty choice abandons it.
    assert game.status == "Abandoned"
    assert game.ended_at is not None


@pytest.mark.parametrize(
    "start_difficulty, start_width, start_height, start_mines",
    [
        ("intermediate", 16, 16, 40),
        ("expert", 30, 16, 99),
    ],
)
def test_misspelled_beginner_is_refused_and_game_unchanged(
    start_difficulty, start_width, start_height, start_mines
):
    game = _make_ready_game("game-1", start_difficulty, start_width, start_height, start_mines)
    before = game.to_dict()

    # 'beginners' is not one of beginner/intermediate/expert/custom: an unknown
    # difficulty_id is refused with InvalidConfigurationError, same values otherwise.
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="beginners",
            width=9,
            height=9,
            mine_count=10,
        )
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"

    # A refused choice leaves the current game completely unchanged: still Ready,
    # same size, mines, counter, timer and cells.
    assert game.status == "Ready"
    assert game.difficulty_id == start_difficulty
    assert game.width == start_width
    assert game.height == start_height
    assert game.mine_count == start_mines
    assert game.to_dict() == before
