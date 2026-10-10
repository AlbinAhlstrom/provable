import pytest

from src.domain.game import Game


CREATED_AT = "2024-01-15T10:00:00+00:00"
STARTED_AT = "2024-01-15T10:00:05+00:00"
ENDED_AT = "2024-01-15T10:03:00+00:00"

DIFFICULTIES = [
    ("beginner", 9, 9, 10),
    ("intermediate", 16, 16, 40),
]


def make_game(difficulty_id, width, height, mine_count, game_id="game-1"):
    game = Game(
        id=game_id,
        difficulty_id=difficulty_id,
        width=width,
        height=height,
        mine_count=mine_count,
        remaining_mines=mine_count,
        created_at=CREATED_AT,
    )
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
            "id": f"{r}-{c}",
            "row": r,
            "column": c,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for r in range(height)
        for c in range(width)
    ]
    return game


def cell_at(game, row, column):
    return game.cells[row * game.width + column]


def put_in_playing(game):
    # Mines laid along the last row (from column 0), far from the opened cell at 0-0.
    for c in range(game.mine_count):
        r = game.height - 1 - (c // game.width)
        col = c % game.width
        cell_at(game, r, col)["has_mine"] = True
    game.mines_laid = True
    game.status = "Playing"
    game.started_at = STARTED_AT
    game.elapsed_seconds = 42
    # One safe cell opened (no mines near the top-left corner).
    cell_at(game, 0, 0)["state"] = "Opened"
    cell_at(game, 0, 0)["adjacent_mine_count"] = 0
    # One flag placed on a hidden cell.
    cell_at(game, 2, 2)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = game.mine_count - 1


def assert_fresh_game(new_game, old_id, difficulty_id, width, height, mine_count):
    # New game: a different id, the same configuration as the old one.
    assert new_game is not None
    assert new_game.id != old_id
    assert new_game.difficulty_id == difficulty_id
    assert new_game.width == width
    assert new_game.height == height
    assert new_game.mine_count == mine_count
    # Starting state: Ready, no mines laid yet, timer 0, counter = mine count, no flags.
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.elapsed_seconds == 0
    assert new_game.flags_placed == 0
    assert new_game.remaining_mines == mine_count
    assert new_game.started_at is None
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None
    # Board: one cell per position, every one Hidden and mine-free (mines laid on first open).
    assert len(new_game.cells) == width * height
    assert all(cell["state"] == "Hidden" for cell in new_game.cells)
    assert all(cell["has_mine"] is False for cell in new_game.cells)


@pytest.mark.parametrize("difficulty_id,width,height,mine_count", DIFFICULTIES)
def test_restart_from_ready_abandons_and_deals_fresh_board(
    difficulty_id, width, height, mine_count
):
    game = make_game(difficulty_id, width, height, mine_count)

    new_game = game.restart_game()

    # Old game was Ready: Ready→Abandoned is allowed, so it becomes Abandoned with ended_at set.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    # Its timer never ran: it stays at 0.
    assert game.elapsed_seconds == 0
    assert_fresh_game(new_game, "game-1", difficulty_id, width, height, mine_count)


@pytest.mark.parametrize("difficulty_id,width,height,mine_count", DIFFICULTIES)
def test_restart_from_playing_abandons_and_deals_fresh_board(
    difficulty_id, width, height, mine_count
):
    game = make_game(difficulty_id, width, height, mine_count)
    put_in_playing(game)

    new_game = game.restart_game()

    # Old game was Playing: Playing→Abandoned is allowed, so it becomes Abandoned with ended_at set.
    assert game.status == "Abandoned"
    assert game.ended_at is not None
    # The abandoned game's timer freezes at its value (42); restart does not tick it.
    assert game.elapsed_seconds == 42
    # The new game does not inherit the flag, the opened cell or the mines of the old one.
    assert_fresh_game(new_game, "game-1", difficulty_id, width, height, mine_count)


@pytest.mark.parametrize("finished_status", ["Won", "Lost"])
def test_restart_from_finished_game_keeps_outcome(finished_status):
    game = make_game("beginner", 9, 9, 10)
    put_in_playing(game)
    game.status = finished_status
    game.ended_at = ENDED_AT

    new_game = game.restart_game()

    # Won/Lost→Abandoned is not an allowed transition: the outcome is kept, ended_at untouched.
    assert game.status == finished_status
    assert game.ended_at == ENDED_AT
    assert game.elapsed_seconds == 42
    # A fresh Ready game of the same difficulty is still dealt.
    assert_fresh_game(new_game, "game-1", "beginner", 9, 9, 10)
