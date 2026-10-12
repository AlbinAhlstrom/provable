from src.domain.game import Game


def _game_with(mine_count: int, flag_count: int) -> Game:
    # Given a new game, with the mine count and flag count set for this scenario.
    # The board is not laid out yet (cells is empty, status ready), and the
    # counter depends only on the two counts, so no other rule applies.
    game = Game(id="game-1")
    game.mine_count = mine_count
    game.flag_count = flag_count
    return game


def test_counter_is_zero_when_flags_exactly_equal_mines():
    # Given M = 10 mines and F = 10 flags.
    # Counter = M - F = 10 - 10 = 0. This is exactly at the limit (F == M).
    game = _game_with(mine_count=10, flag_count=10)

    # When the counter is displayed.
    value = game.mine_counter()

    # Then it shows 0.
    assert value == 0


def test_counter_is_negative_when_flags_exceed_mines_by_one():
    # Given M = 10 mines and F = 11 flags (one beyond the limit).
    # Counter = M - F = 10 - 11 = -1, which must be shown as a negative value.
    game = _game_with(mine_count=10, flag_count=11)

    # When the counter is displayed.
    value = game.mine_counter()

    # Then it shows -1.
    assert value == -1
