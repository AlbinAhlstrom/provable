"""R4-R6: mine placement and the first reveal."""
import pytest

from src.domain.game import Game
from src.domain.minefield import neighbours, place_mines


def test_neighbours_in_the_middle_corner_and_edge():
    assert len(neighbours(5, 5, (2, 2))) == 8
    assert sorted(neighbours(5, 5, (0, 0))) == [(0, 1), (1, 0), (1, 1)]
    assert len(neighbours(5, 5, (0, 2))) == 5
    assert (2, 2) not in neighbours(5, 5, (2, 2))


@pytest.mark.parametrize("seed", range(25))
def test_r4_no_mine_on_first_cell_or_its_neighbours(seed):
    first = (4, 4)
    mines = place_mines(rows=9, cols=9, count=10, safe_cell=first, seed=seed)
    assert len(mines) == 10
    assert first not in mines
    assert not mines & set(neighbours(9, 9, first))
    assert all(0 <= r < 9 and 0 <= c < 9 for r, c in mines)


def test_r4_densest_allowed_board_still_keeps_the_first_area_clear():
    mines = place_mines(rows=5, cols=5, count=16, safe_cell=(2, 2), seed=3)
    assert len(mines) == 16
    assert not mines & ({(2, 2)} | set(neighbours(5, 5, (2, 2))))


def test_r4_corner_first_click_is_safe_too():
    mines = place_mines(rows=5, cols=5, count=16, safe_cell=(0, 0), seed=3)
    assert len(mines) == 16
    assert not mines & {(0, 0), (0, 1), (1, 0), (1, 1)}


def test_r5_same_inputs_same_board():
    a = place_mines(rows=16, cols=30, count=99, safe_cell=(3, 7), seed=42)
    b = place_mines(rows=16, cols=30, count=99, safe_cell=(3, 7), seed=42)
    assert a == b


def test_r5_different_seeds_give_different_boards():
    layouts = {place_mines(rows=9, cols=9, count=10, safe_cell=(0, 0), seed=s) for s in range(10)}
    assert len(layouts) > 1


def test_r5_two_games_with_the_same_seed_and_first_click_are_the_same_game():
    a = Game.new(id="a", difficulty="beginner", seed=7, now=0.0)
    b = Game.new(id="b", difficulty="beginner", seed=7, now=0.0)
    a.reveal(4, 4, now=1.0)
    b.reveal(4, 4, now=1.0)
    assert a.mines == b.mines
    assert a.revealed == b.revealed


@pytest.mark.parametrize("seed", range(10))
def test_r4_first_reveal_always_opens_an_area(seed):
    game = Game.new(id="g", difficulty="beginner", seed=seed, now=0.0)
    game.reveal(0, 0, now=1.0)
    assert len(game.mines) == 10
    # the first cell is a zero, so at least it and its three neighbours are open
    assert {(0, 0), (0, 1), (1, 0), (1, 1)} <= game.revealed
    assert game.status in ("playing", "won")


def test_r6_first_reveal_starts_the_game_and_the_timer():
    game = Game.new(id="g", difficulty="expert", seed=1, now=10.0)
    game.reveal(8, 15, now=12.5)
    assert game.status == "playing"
    assert game.started_at == 12.5


def test_r6_flagging_does_not_start_the_game():
    game = Game.new(id="g", difficulty="beginner", seed=1, now=0.0)
    game.toggle_flag(0, 0)
    assert game.status == "ready"
    assert game.mines is None
    assert game.started_at is None
