import copy

import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Mines on row 0 (all nine columns) and on cell 1-0: ten mines in total.
MINE_POSITIONS = {(0, c) for c in range(9)} | {(1, 0)}


def _adjacent(row, column):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in MINE_POSITIONS:
                count += 1
    return count


def _build_cells(status):
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            has_mine = (row, column) in MINE_POSITIONS
            if status == "Won":
                # Won: every safe cell Opened, every mine auto-flagged.
                state = "Flagged" if has_mine else "Opened"
            elif status == "Lost":
                # Lost: the struck mine 0-0 Detonated, one safe cell 8-8 Opened, rest Hidden.
                if (row, column) == (0, 0):
                    state = "Detonated"
                elif (row, column) == (8, 8):
                    state = "Opened"
                else:
                    state = "Hidden"
            else:
                # Playing: one safe cell 8-8 Opened, rest Hidden.
                state = "Opened" if (row, column) == (8, 8) else "Hidden"
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": has_mine,
                    "adjacent_mine_count": _adjacent(row, column),
                    "state": state,
                }
            )
    return cells


def _make_game(status):
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00Z",
    )
    game.cells = _build_cells(status)
    game.status = status
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05Z"
    game.elapsed_seconds = 42
    if status == "Won":
        game.flags_placed = MINE_COUNT
        game.remaining_mines = 0
        game.ended_at = "2024-01-01T10:00:47Z"
        game.struck_cell_id = None
    elif status == "Lost":
        game.flags_placed = 0
        game.remaining_mines = MINE_COUNT
        game.ended_at = "2024-01-01T10:00:47Z"
        game.struck_cell_id = "0-0"
    else:
        game.flags_placed = 0
        game.remaining_mines = MINE_COUNT
        game.ended_at = None
        game.struck_cell_id = None
    return game


def _assert_fresh_ready_game(new_game, old_game):
    assert isinstance(new_game, Game)
    # A new game has a new id but the same difficulty and dimensions.
    assert new_game.id != old_game.id
    assert new_game.difficulty_id == "beginner"
    assert new_game.width == 9
    assert new_game.height == 9
    assert new_game.mine_count == 10
    # Starting state: Ready, no mines laid, timer 0, counter = mine_count, nothing set.
    assert new_game.status == "Ready"
    assert new_game.mines_laid is False
    assert new_game.flags_placed == 0
    assert new_game.elapsed_seconds == 0
    assert new_game.remaining_mines == 10
    assert new_game.started_at is None
    assert new_game.ended_at is None
    assert new_game.struck_cell_id is None
    # 9x9 = 81 cells in row-major order, all Hidden, no mines, count 0.
    assert len(new_game.cells) == 81
    expected_ids = [f"{r}-{c}" for r in range(9) for c in range(9)]
    assert [cell["id"] for cell in new_game.cells] == expected_ids
    for cell in new_game.cells:
        assert cell["state"] == "Hidden"
        assert cell["has_mine"] is False
        assert cell["adjacent_mine_count"] == 0


@pytest.mark.parametrize("finished_status", ["Won", "Lost"])
def test_smiley_on_finished_game_keeps_outcome_and_creates_new_ready_game(finished_status):
    game = _make_game(finished_status)
    cells_before = copy.deepcopy(game.cells)

    new_game = game.restart_game()

    # Won/Lost is final: restart keeps the outcome (Won/Lost -> Abandoned is not allowed).
    assert game.status == finished_status
    # The finished game's end time, timer, counters and struck cell are untouched.
    assert game.ended_at == "2024-01-01T10:00:47Z"
    assert game.elapsed_seconds == 42
    assert game.started_at == "2024-01-01T10:00:05Z"
    if finished_status == "Won":
        assert game.flags_placed == 10
        assert game.remaining_mines == 0
        assert game.struck_cell_id is None
    else:
        assert game.flags_placed == 0
        assert game.remaining_mines == 10
        assert game.struck_cell_id == "0-0"
    # The finished board is not altered in any cell.
    assert game.cells == cells_before
    assert game.id == "game-1"

    # A brand-new Ready game of the same difficulty is returned.
    _assert_fresh_ready_game(new_game, game)


def test_smiley_on_playing_game_abandons_it_unlike_finished_game():
    # Same board shape and history as the finished cases, but the game is still Playing.
    game = _make_game("Playing")
    cells_before = copy.deepcopy(game.cells)

    new_game = game.restart_game()

    # Playing -> Abandoned is allowed, so a non-finished game does not keep its status.
    assert game.status == "Abandoned"
    # ended_at gets set when abandoning.
    assert game.ended_at is not None
    # Board is not altered.
    assert game.cells == cells_before

    _assert_fresh_ready_game(new_game, game)
