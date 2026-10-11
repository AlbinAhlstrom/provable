import copy

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10


def _make_game():
    return Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )


def _fresh_cells():
    return [
        {
            "id": f"{row}-{column}",
            "row": row,
            "column": column,
            "has_mine": False,
            "adjacent_mine_count": 0,
            "state": "Hidden",
        }
        for row in range(HEIGHT)
        for column in range(WIDTH)
    ]


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"cell {row}-{column} missing")


def _arrange_playing_game_with_flag_on_0_0():
    game = _make_game()
    cells = _fresh_cells()
    # Mines: (0,1) plus the whole bottom row (8,0)..(8,8) -> exactly 10 mines.
    mine_positions = {(0, 1)} | {(8, c) for c in range(WIDTH)}
    for cell in cells:
        cell["has_mine"] = (cell["row"], cell["column"]) in mine_positions
    for cell in cells:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = cell["row"] + dr, cell["column"] + dc
                if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in mine_positions:
                    count += 1
        cell["adjacent_mine_count"] = count
    game.cells = cells
    _cell(game, 0, 0)["state"] = "Flagged"
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 5
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    return game


def test_flagged_cell_cannot_be_opened_until_unflagged_in_playing_game():
    game = _arrange_playing_game_with_flag_on_0_0()
    cells_before = copy.deepcopy(game.cells)

    game.open_cell(row=0, column=0)

    # (0,0) is Flagged; opening a Flagged cell changes nothing and raises no error.
    assert _cell(game, 0, 0)["state"] == "Flagged"
    # Nothing is revealed: every cell is exactly as before (no cascade, no detonation).
    assert game.cells == cells_before
    # Game stays Playing, no struck cell, counters untouched.
    assert game.status == "Playing"
    assert game.struck_cell_id is None
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1
    assert game.elapsed_seconds == 5

    game.toggle_flag(row=0, column=0)

    # Flagged -> Hidden, flags_placed 1 -> 0, remaining = 10 - 0 = 10.
    assert _cell(game, 0, 0)["state"] == "Hidden"
    assert game.flags_placed == 0
    assert game.remaining_mines == MINE_COUNT

    game.open_cell(row=0, column=0)

    # (0,0) has no mine; its neighbours (0,1),(1,0),(1,1) contain one mine (0,1),
    # so it becomes Opened with count 1 and does not cascade.
    opened = _cell(game, 0, 0)
    assert opened["state"] == "Opened"
    assert opened["adjacent_mine_count"] == 1
    # No other cell changed: count 1 stops any cascade.
    for before in cells_before:
        if (before["row"], before["column"]) == (0, 0):
            continue
        assert _cell(game, before["row"], before["column"])["state"] == "Hidden"
    # Many safe cells remain hidden, so not Won; no mine opened, so not Lost.
    assert game.status == "Playing"
    assert game.struck_cell_id is None


def test_flagged_cell_cannot_be_opened_until_unflagged_in_ready_game():
    game = _make_game()
    game.cells = _fresh_cells()
    _cell(game, 4, 4)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    cells_before = copy.deepcopy(game.cells)

    game.open_cell(row=4, column=4)

    # Opening a Flagged cell is ignored: it is not a first open, so no mines are laid
    # and the game stays Ready with the timer not started.
    assert _cell(game, 4, 4)["state"] == "Flagged"
    assert game.cells == cells_before
    assert game.status == "Ready"
    assert game.mines_laid is False
    assert game.started_at is None
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1

    game.toggle_flag(row=4, column=4)

    # Flagged -> Hidden, flags_placed back to 0, remaining 10.
    assert _cell(game, 4, 4)["state"] == "Hidden"
    assert game.flags_placed == 0
    assert game.remaining_mines == MINE_COUNT

    game.open_cell(row=4, column=4)

    # First open of a Ready game: mines laid elsewhere (first click safe),
    # the cell becomes Opened and the game becomes Playing.
    opened = _cell(game, 4, 4)
    assert opened["state"] == "Opened"
    assert opened["has_mine"] is False
    assert game.mines_laid is True
    assert sum(1 for c in game.cells if c["has_mine"]) == MINE_COUNT
    assert game.status == "Playing"
    assert game.started_at is not None
