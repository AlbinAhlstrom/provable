from src.domain.game import Game

WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Mines: the whole bottom row (row 8, columns 0..8) plus (7, 0) -> 10 mines.
MINE_POSITIONS = {(8, c) for c in range(WIDTH)} | {(7, 0)}


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                yield r, c


def _build_cells():
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            count = sum(1 for n in _neighbours(row, column) if n in MINE_POSITIONS)
            cells.append(
                {
                    "id": f"{row}-{column}",
                    "row": row,
                    "column": column,
                    "has_mine": (row, column) in MINE_POSITIONS,
                    "adjacent_mine_count": count,
                    "state": "Hidden",
                }
            )
    return cells


def _cell(game, row, column):
    return game.cells[row * WIDTH + column]


def _playing_game_with_opened_cell():
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    game.cells = _build_cells()
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 7
    # (0, 0) is a safe corner cell already opened; its neighbours (0,1),(1,0),(1,1)
    # hold no mine, so its count is 0.
    _cell(game, 0, 0)["state"] = "Opened"
    # One flag placed on the mine at (8, 8): flags_placed 1, remaining_mines 10 - 1 = 9.
    _cell(game, 8, 8)["state"] = "Flagged"
    game.flags_placed = 1
    game.remaining_mines = 9
    game.events = []
    return game


def test_toggling_flag_on_opened_cell_changes_nothing():
    game = _playing_game_with_opened_cell()
    cells_before = [dict(c) for c in game.cells]

    # Status is Playing (flagging allowed in principle); (0,0) is Opened, and the
    # rule says toggling an Opened cell changes nothing and raises no error.
    game.toggle_flag(row=0, column=0)

    # (0,0) was Opened; Opened never returns to Hidden or Flagged -> stays Opened.
    assert _cell(game, 0, 0)["state"] == "Opened"
    # No flag was added or removed: flags_placed stays 1.
    assert game.flags_placed == 1
    # remaining_mines = 10 - 1 = 9, unchanged.
    assert game.remaining_mines == 9
    # No other cell is touched by an ignored action.
    assert game.cells == cells_before
    # The game is not ended or otherwise altered; timer is untouched.
    assert game.status == "Playing"
    assert game.elapsed_seconds == 7
    assert game.ended_at is None
    # No message/event is produced.
    assert game.events == []


def test_toggling_flag_on_hidden_cell_in_same_game_does_flag_it():
    # Contrast case: same arrangement, only the target cell differs (Hidden instead of Opened).
    game = _playing_game_with_opened_cell()

    # (0,1) is Hidden and safe; toggling flags it: flags_placed 1 -> 2,
    # remaining_mines = 10 - 2 = 8.
    game.toggle_flag(row=0, column=1)

    assert _cell(game, 0, 1)["state"] == "Flagged"
    assert game.flags_placed == 2
    assert game.remaining_mines == 8
    # The Opened cell is unaffected.
    assert _cell(game, 0, 0)["state"] == "Opened"
    assert game.status == "Playing"
