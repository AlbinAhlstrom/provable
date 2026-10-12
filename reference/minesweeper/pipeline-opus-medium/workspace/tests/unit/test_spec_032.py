import pytest

from src.domain.game import Game


WIDTH = 9
HEIGHT = 9
MINE_COUNT = 10
# Mines: the whole top row (0,0)..(0,8) plus (1,0) -> exactly 10 mines.
MINES = {(0, c) for c in range(WIDTH)} | {(1, 0)}


def _adjacent(row, column):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < HEIGHT and 0 <= c < WIDTH and (r, c) in MINES:
                count += 1
    return count


def _make_playing_game(hidden_safe_cells):
    """A Playing beginner game, mines laid, where every safe cell is Opened
    except the given hidden_safe_cells. Mine (0,0) is Flagged, the other 9
    mines are Hidden."""
    game = Game(
        id="g1",
        difficulty_id="beginner",
        width=WIDTH,
        height=HEIGHT,
        mine_count=MINE_COUNT,
        remaining_mines=MINE_COUNT,
        created_at="2024-01-01T10:00:00",
    )
    cells = []
    for row in range(HEIGHT):
        for column in range(WIDTH):
            has_mine = (row, column) in MINES
            if has_mine:
                state = "Flagged" if (row, column) == (0, 0) else "Hidden"
            elif (row, column) in hidden_safe_cells:
                state = "Hidden"
            else:
                state = "Opened"
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
    game.cells = cells
    game.status = "Playing"
    game.mines_laid = True
    game.started_at = "2024-01-01T10:00:05"
    game.elapsed_seconds = 42
    game.flags_placed = 1
    game.remaining_mines = MINE_COUNT - 1
    return game


def _cell(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"cell {row}-{column} missing")


def test_opening_last_safe_cell_wins_and_auto_flags_every_mine():
    # Exactly at the limit: (2,0) is the only unopened non-mine cell.
    game = _make_playing_game(hidden_safe_cells={(2, 0)})

    game.open_cell(row=2, column=0)

    # (2,0) is safe; neighbours (1,0) mine, (1,1),(2,1),(3,0),(3,1) safe -> count 1,
    # so it becomes Opened with no cascade.
    assert _cell(game, 2, 0)["state"] == "Opened"
    # After opening (2,0) every one of the 71 safe cells is Opened -> Won.
    assert game.status == "Won"
    # Win records the end time.
    assert game.ended_at is not None
    # Each of the 10 mine cells: (0,0) was already Flagged, the other 9 Hidden
    # mines get auto-flagged -> all 10 are Flagged.
    for (row, column) in MINES:
        assert _cell(game, row, column)["state"] == "Flagged"
    # No safe cell is flagged; every safe cell is Opened.
    for cell in game.cells:
        if not cell["has_mine"]:
            assert cell["state"] == "Opened"
    # flags placed equals the mine count (10), not 1 + something else.
    assert game.flags_placed == MINE_COUNT
    # remaining mines counter is 10 - 10 = 0.
    assert game.remaining_mines == 0
    # Timer freezes on end: still 42.
    assert game.elapsed_seconds == 42


def test_opening_a_safe_cell_with_another_still_hidden_does_not_auto_flag():
    # Just beyond the limit: same board, but (8,8) is also still Hidden.
    game = _make_playing_game(hidden_safe_cells={(2, 0), (8, 8)})

    game.open_cell(row=2, column=0)

    # (2,0) has count 1 -> Opened, no cascade, so (8,8) is not reached.
    assert _cell(game, 2, 0)["state"] == "Opened"
    # (8,8) is a non-mine cell still Hidden -> the game is not Won.
    assert _cell(game, 8, 8)["state"] == "Hidden"
    assert game.status == "Playing"
    assert game.ended_at is None
    # No auto-flagging: (0,0) stays Flagged, the other 9 mines stay Hidden.
    assert _cell(game, 0, 0)["state"] == "Flagged"
    for (row, column) in MINES - {(0, 0)}:
        assert _cell(game, row, column)["state"] == "Hidden"
    # Counters unchanged: 1 flag, remaining 10 - 1 = 9.
    assert game.flags_placed == 1
    assert game.remaining_mines == MINE_COUNT - 1
