import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINES = 10
CREATED_AT = "2024-01-01T10:00:00+00:00"


def _make_ready_game():
    """A beginner game in Ready status, elapsed 0, no mines laid.

    Every cell except the corner (0, 0) is Flagged. Mines are laid at random
    on the first open, so the outcome of that open cannot be chosen directly.
    The flags keep it from ending the game:
    - The first open is safe, so (0, 0) can never be a mine.
    - A cascade from (0, 0) skips Flagged cells, so nothing else opens.
    - That leaves 80 - 10 = 70 safe cells unopened, so the game cannot be Won.
    The game therefore stays Playing and the timer rule alone decides
    elapsed_seconds.
    """
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINES,
        remaining_mines=MINES,
        created_at=CREATED_AT,
    )
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": False,
                    "adjacent_mine_count": 0,
                    "state": "Hidden" if (row, column) == (0, 0) else "Flagged",
                }
            )
    game.cells = cells
    game.status = "Ready"
    game.mines_laid = False
    game.elapsed_seconds = 0
    game.started_at = None
    game.ended_at = None
    game.struck_cell_id = None
    game.flags_placed = WIDTH * HEIGHT - 1  # 80 flags, flags are unlimited
    game.remaining_mines = MINES - (WIDTH * HEIGHT - 1)  # 10 - 80 = -70
    game.events = []
    return game


def test_timer_does_not_run_before_first_open():
    game = _make_ready_game()

    game.tick()
    game.tick()

    # Status is Ready and no cell has been opened. tick only counts while
    # Playing, so both ticks change nothing and elapsed reads 0.
    assert game.elapsed_seconds == 0
    # Nothing started the game, so it is still Ready with no start time.
    assert game.status == "Ready"
    assert game.started_at is None


def test_first_open_starts_timer_at_zero():
    game = _make_ready_game()

    game.open_cell(row=0, column=0)

    # The first open of a Ready game makes status Playing and sets started_at.
    # (0, 0) is safe on the first open. The cascade skips the 80 Flagged
    # cells, and 70 safe cells stay unopened, so the game is not Won.
    assert game.status == "Playing"
    assert game.started_at is not None
    # No tick has happened yet, so elapsed counts 0 whole seconds.
    assert game.elapsed_seconds == 0


@pytest.mark.parametrize("ticks, expected", [(1, 1), (2, 2), (5, 5)])
def test_timer_counts_one_per_second_after_first_open(ticks, expected):
    game = _make_ready_game()
    game.open_cell(row=0, column=0)
    # The game is now Playing (see the comments above), with elapsed 0.
    assert game.status == "Playing"
    assert game.elapsed_seconds == 0

    for _ in range(ticks):
        game.tick()

    # While Playing, each tick adds 1 second: 0 + ticks.
    # This stays far below the 999 cap.
    assert game.elapsed_seconds == expected
    # Ticking never changes the status, so the game is still Playing.
    assert game.status == "Playing"


def test_same_ticks_before_and_after_first_open_differ_only_by_the_open():
    before = _make_ready_game()
    after = _make_ready_game()
    after.open_cell(row=0, column=0)

    for _ in range(3):
        before.tick()
        after.tick()

    # Both games get the same 3 ticks.
    # The Ready game (never opened) ignores them: 0.
    assert before.elapsed_seconds == 0
    # The opened game is Playing, so it counts each one: 0 + 3 = 3.
    assert after.elapsed_seconds == 3
