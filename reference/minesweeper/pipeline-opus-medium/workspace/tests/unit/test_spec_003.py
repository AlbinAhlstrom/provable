import pytest

from src.domain.game import Game


def _make_game(game_id, difficulty_id, width, height, mine_count):
    # Constructed with only its required fields: a newly created Game in
    # status Ready, no mines laid, timer 0, no flags.
    return Game(
        id=game_id,
        difficulty_id=difficulty_id,
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at="2024-01-01T10:00:00Z",
    )


@pytest.mark.parametrize(
    "start_difficulty, start_width, start_height, start_mines",
    [
        ("beginner", 9, 9, 10),
        ("expert", 30, 16, 99),
    ],
)
def test_choosing_intermediate_creates_16_by_16_game_with_40_mines(
    start_difficulty, start_width, start_height, start_mines
):
    # Given a Ready game of another difficulty (no cell opened, nothing ended)
    game = _make_game("game-1", start_difficulty, start_width, start_height, start_mines)

    # When the player chooses Intermediate from the menu. Width, height and
    # mine count are not given: a preset decides them itself.
    new_game = game.change_difficulty(
        difficulty_id="intermediate", width=None, height=None, mine_count=None
    )

    # Then: intermediate is a known preset, so no InvalidConfigurationError is
    # raised and a new Game is returned with difficulty_id "intermediate".
    assert isinstance(new_game, Game)
    assert new_game.difficulty_id == "intermediate"
    # The intermediate preset is 16x16 with 40 mines: exactly 16, not 15 or 17.
    assert new_game.width == 16
    assert new_game.height == 16
    # Exactly 40 mines, not 39 or 41.
    assert new_game.mine_count == 40
    # The new game has a new id.
    assert new_game.id != game.id
    # Starting state: Ready, no mines laid, counter = mine_count - 0 flags = 40,
    # timer 0, no flags, nothing struck, not started or ended.
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.remaining_mines == 40
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert new_game.started_at is None
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None
    # Board: 16 x 16 = 256 cells in row-major order, ids "row-column",
    # all Hidden with no mine and count 0 (mines are laid only on first open).
    assert len(new_game.cells) == 256
    expected_ids = [f"{r}-{c}" for r in range(16) for c in range(16)]
    assert [cell["id"] for cell in new_game.cells] == expected_ids
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    assert all(cell["has_mine"] is False for cell in new_game.cells)
    assert all(cell["adjacent_mine_count"] == 0 for cell in new_game.cells)
    # The previous game was Ready, so a valid choice abandons it.
    assert game.status == "Abandoned"
    assert game.ended_at is not None


def test_choosing_a_difficulty_just_beyond_intermediate_name_is_refused():
    # Given the same Ready beginner game as in the accepted case
    game = _make_game("game-1", "beginner", 9, 9, 10)

    # When the player submits an unknown difficulty id, one letter short of
    # "intermediate", with the same other arguments as the accepted case
    with pytest.raises(Exception) as exc_info:
        game.change_difficulty(
            difficulty_id="intermediat", width=None, height=None, mine_count=None
        )

    # Then: "intermediat" is not one of beginner/intermediate/expert/custom,
    # so the choice is refused with InvalidConfigurationError.
    assert type(exc_info.value).__name__ == "InvalidConfigurationError"
    # And the current game is left completely unchanged: still Ready beginner
    # 9x9 with 10 mines, counter 10, timer 0, 81 Hidden mine-free cells.
    assert game.id == "game-1"
    assert game.status == "Ready"
    assert game.difficulty_id == "beginner"
    assert game.width == 9
    assert game.height == 9
    assert game.mine_count == 10
    assert game.remaining_mines == 10
    assert game.elapsed_seconds == 0
    assert game.flags_placed == 0
    assert game.ended_at is None
    assert len(game.cells) == 81
    assert all(cell["state"] == "Hidden" for cell in game.cells)
    assert all(cell["has_mine"] is False for cell in game.cells)
