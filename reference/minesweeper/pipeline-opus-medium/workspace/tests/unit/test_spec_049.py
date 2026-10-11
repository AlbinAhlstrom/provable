from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Ten mines: the whole bottom row (row 8, columns 0..8) plus (7, 0).
MINES = {(8, c) for c in range(WIDTH)} | {(7, 0)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _playing_game():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    cells = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": (r, c) in MINES,
                    "adjacent_mine_count": sum(
                        1 for n in _neighbours(r, c) if n in MINES
                    ),
                    "state": "Hidden",
                }
            )
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 5
    game.flags_placed = 0
    game.remaining_mines = MINE_COUNT
    return game


def test_hidden_to_flagged_and_back_to_hidden():
    game = _playing_game()
    # (0,0) is a safe Hidden cell far from the mines; game is Playing.
    game.toggle_flag(row=0, column=0)
    # Hidden -> Flagged is allowed; flags_placed 0 -> 1, counter 10 - 1 = 9.
    assert _cell(game, 0, 0)["state"] == "Flagged"
    assert game.flags_placed == 1
    assert game.remaining_mines == 9

    game.toggle_flag(row=0, column=0)
    # Flagged -> Hidden is allowed; flags_placed 1 -> 0, counter back to 10.
    assert _cell(game, 0, 0)["state"] == "Hidden"
    assert game.flags_placed == 0
    assert game.remaining_mines == 10


def test_hidden_safe_cell_becomes_opened():
    game = _playing_game()
    # (7,4) is safe; its neighbours (8,3),(8,4),(8,5) are mines, so count 3:
    # no cascade. Many other safe cells stay Hidden, so no win.
    game.open_cell(row=7, column=4)
    # Hidden -> Opened is allowed for a safe cell.
    assert _cell(game, 7, 4)["state"] == "Opened"
    assert _cell(game, 7, 4)["adjacent_mine_count"] == 3
    assert game.status == "Playing"
    # Its neighbours are not touched (numbered cell, no cascade).
    assert _cell(game, 6, 4)["state"] == "Hidden"


def test_hidden_mine_cell_becomes_detonated():
    game = _playing_game()
    # (8,4) holds a mine and is Hidden; game is Playing.
    game.open_cell(row=8, column=4)
    # Hidden -> Detonated is allowed for a mine; game is lost on it.
    assert _cell(game, 8, 4)["state"] == "Detonated"
    assert game.struck_cell_id == "8-4"
    assert game.status == "Lost"


def test_opened_cell_never_becomes_flagged_or_hidden():
    game = _playing_game()
    _cell(game, 7, 4)["state"] = "Opened"
    # Same cell as the accepted Hidden->Flagged case, only its state differs.
    game.toggle_flag(row=7, column=4)
    # Opened -> Flagged is not allowed: ignored, no error, no flag counted.
    assert _cell(game, 7, 4)["state"] == "Opened"
    assert game.flags_placed == 0
    assert game.remaining_mines == 10

    game.open_cell(row=7, column=4)
    # Opening an Opened cell is ignored: stays Opened, game still Playing.
    assert _cell(game, 7, 4)["state"] == "Opened"
    assert game.status == "Playing"


def test_detonated_cell_never_becomes_flagged_or_hidden():
    game = _playing_game()
    _cell(game, 8, 4)["state"] = "Detonated"
    game.status = "Lost"
    game.struck_cell_id = "8-4"
    game.ended_at = "2024-01-01T10:00:10"
    # Detonated is final: toggling it is ignored with no error.
    game.toggle_flag(row=8, column=4)
    assert _cell(game, 8, 4)["state"] == "Detonated"
    assert game.flags_placed == 0

    game.open_cell(row=8, column=4)
    # Opening it again is ignored too: still Detonated, still Lost.
    assert _cell(game, 8, 4)["state"] == "Detonated"
    assert game.status == "Lost"


def test_flagged_cell_cannot_become_opened_directly():
    game = _playing_game()
    _cell(game, 7, 4)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = 9
    # Same cell and action as the accepted Hidden->Opened case, but Flagged:
    # Flagged -> Opened is not an allowed change, so the open is ignored.
    game.open_cell(row=7, column=4)
    assert _cell(game, 7, 4)["state"] == "Flagged"
    assert game.flags_placed == 1
    assert game.status == "Playing"


def test_flagged_mine_cell_cannot_become_detonated_directly():
    game = _playing_game()
    _cell(game, 8, 4)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = 9
    # Same cell and action as the accepted Hidden->Detonated case, but Flagged:
    # Flagged -> Detonated is not allowed, so nothing changes and no loss.
    game.open_cell(row=8, column=4)
    assert _cell(game, 8, 4)["state"] == "Flagged"
    assert game.status == "Playing"
    assert game.struck_cell_id is None
