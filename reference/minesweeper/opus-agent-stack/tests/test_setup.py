"""R1-R3: creating a game."""
import pytest

from src.domain.game import Game, InvalidConfiguration, PRESETS


@pytest.mark.parametrize(
    "difficulty, rows, cols, mines",
    [("beginner", 9, 9, 10), ("intermediate", 16, 16, 40), ("expert", 16, 30, 99)],
)
def test_r1_presets_fix_the_board(difficulty, rows, cols, mines):
    game = Game.new(id="g", difficulty=difficulty, seed=1, now=5.0)
    assert (game.rows, game.cols, game.mine_count) == (rows, cols, mines)
    assert game.difficulty == difficulty
    assert PRESETS[difficulty] == (rows, cols, mines)


def test_r1_a_preset_ignores_custom_numbers():
    game = Game.new(id="g", difficulty="beginner", seed=1, now=0.0, rows=20, cols=20, mines=5)
    assert (game.rows, game.cols, game.mine_count) == (9, 9, 10)


def test_r1_unknown_difficulty_is_rejected():
    with pytest.raises(InvalidConfiguration):
        Game.new(id="g", difficulty="nightmare", seed=1, now=0.0)


def test_r2_custom_board_takes_its_numbers():
    game = Game.new(id="g", difficulty="custom", seed=1, now=0.0, rows=12, cols=20, mines=30)
    assert (game.rows, game.cols, game.mine_count) == (12, 20, 30)
    assert game.difficulty == "custom"


@pytest.mark.parametrize(
    "rows, cols, mines",
    [
        (4, 9, 5),      # too few rows
        (25, 9, 5),     # too many rows
        (9, 4, 5),      # too few columns
        (9, 31, 5),     # too many columns
        (9, 9, 0),      # no mines
        (9, 9, 73),     # 81 cells - 9 safe = 72 is the most that fits
        (None, 9, 5),   # missing number
    ],
)
def test_r2_custom_board_outside_limits_is_rejected(rows, cols, mines):
    with pytest.raises(InvalidConfiguration):
        Game.new(id="g", difficulty="custom", seed=1, now=0.0, rows=rows, cols=cols, mines=mines)


def test_r2_custom_board_at_the_limits_is_accepted():
    Game.new(id="g", difficulty="custom", seed=1, now=0.0, rows=5, cols=5, mines=16)
    Game.new(id="g", difficulty="custom", seed=1, now=0.0, rows=24, cols=30, mines=1)


def test_r3_new_game_is_ready_and_untouched():
    game = Game.new(id="g", difficulty="beginner", seed=1, now=5.0)
    assert game.status == "ready"
    assert game.mines is None
    assert game.revealed == set()
    assert game.flags == set()
    assert game.created_at == 5.0
    assert game.started_at is None and game.finished_at is None
    assert game.elapsed(now=99.0) == 0
    assert game.mines_remaining == 10
