from src.domain.game import Game

ROWS = 9
COLUMNS = 9
MINES = {(7, 7), (7, 8), (8, 7)}  # safe corner cell (8, 8) is walled in by mines


def _neighbours(row, column):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS:
                yield r, c


def _build_cells():
    cells = []
    for r in range(ROWS):
        for c in range(COLUMNS):
            count = sum(1 for n in _neighbours(r, c) if n in MINES)
            cells.append({
                "id": f"{r}-{c}",
                "row": r,
                "column": c,
                "has_mine": (r, c) in MINES,
                "adjacent_mine_count": count,
                "state": "hidden",
            })
    return cells


def _cell_at(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at {row},{column}")


def _in_progress_game():
    game = Game(id="zero-expansion-game")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.mine_count = len(MINES)
    game.flag_count = 0
    game.cells = _build_cells()
    return game


def test_zero_cell_reveal_expands_recursively_through_zero_region():
    # Given an in-progress 9x9 board with mines only at (7,7),(7,8),(8,7).
    # The target (0,0) has count 0, and every cell in the region rows/cols 0..6
    # not touching the mine block has count 0, so expansion flows from (0,0).
    game = _in_progress_game()
    assert _cell_at(game, 0, 0)["adjacent_mine_count"] == 0
    assert _cell_at(game, 0, 0)["state"] == "hidden"

    # When the player reveals the zero cell (0,0).
    game.reveal_cell(row=0, column=0)

    # Then its neighbours (0,1), (1,0), (1,1) are revealed:
    # they are hidden, unflagged, and adjacent to the zero cell (0,0).
    assert _cell_at(game, 0, 1)["state"] == "revealed"
    assert _cell_at(game, 1, 0)["state"] == "revealed"
    assert _cell_at(game, 1, 1)["state"] == "revealed"

    # And expansion continues recursively: (2,2) has count 0 and is reached
    # through zero cells, two steps from the target.
    assert _cell_at(game, 2, 2)["adjacent_mine_count"] == 0
    assert _cell_at(game, 2, 2)["state"] == "revealed"

    # And (5,5) (count 0, five steps away) is also revealed.
    assert _cell_at(game, 5, 5)["adjacent_mine_count"] == 0
    assert _cell_at(game, 5, 5)["state"] == "revealed"

    # And (6,6) touches the mine at (7,7), so it has count 1; it is revealed
    # as a neighbour of the zero cell (5,5), and expansion stops there.
    assert _cell_at(game, 6, 6)["adjacent_mine_count"] == 1
    assert _cell_at(game, 6, 6)["state"] == "revealed"

    # And the safe cell (8,8) is walled in by mines, so no zero cell touches it
    # and it stays hidden; the game is not won and remains in progress.
    assert _cell_at(game, 8, 8)["has_mine"] is False
    assert _cell_at(game, 8, 8)["state"] == "hidden"
    assert game.status == "in_progress"
