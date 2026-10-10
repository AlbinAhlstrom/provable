from src.domain.game import Game


ROWS = 9
COLUMNS = 9
MINE_POSITIONS = {(8, c) for c in range(9)} | {(7, 8)}  # 10 mines, all far from (0, 0)


def neighbours(row, column):
    result = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, column + dc
            if 0 <= r < ROWS and 0 <= c < COLUMNS:
                result.append((r, c))
    return result


def build_cells():
    cells = []
    for r in range(ROWS):
        for c in range(COLUMNS):
            has_mine = (r, c) in MINE_POSITIONS
            count = sum(1 for (nr, nc) in neighbours(r, c) if (nr, nc) in MINE_POSITIONS)
            cells.append({
                "id": f"c{r}-{c}",
                "row": r,
                "column": c,
                "has_mine": has_mine,
                "adjacent_mine_count": 0 if has_mine else count,
                "state": "hidden",
            })
    return cells


def cell_at(game, row, column):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at {row},{column}")


def make_in_progress_game_with_flag_at_origin():
    game = Game(id="game-1")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.mine_count = 10
    game.cells = build_cells()
    cell_at(game, 0, 0)["state"] = "flagged"
    game.flag_count = 1
    return game


def test_removing_flag_returns_cell_to_hidden_and_decreases_flag_count():
    # Given: in_progress game, 9x9 board, mines only in row 8 and at (7,8).
    # Cell (0,0) is flagged, flag_count is 1 (matches the one flag).
    game = make_in_progress_game_with_flag_at_origin()

    # When: the player toggles the flag off on (0,0).
    game.toggle_flag(row=0, column=0)

    # Then: (0,0) is hidden again. Its state was "flagged"; the toggle cycles
    # flagged -> hidden. The game is in_progress, so toggling is allowed.
    assert cell_at(game, 0, 0)["state"] == "hidden"
    # Then: flag_count goes from 1 to 0 (one flag removed).
    assert game.flag_count == 0
    # Then: the game remains in progress; no end condition is triggered by a flag change.
    assert game.status == "in_progress"


def test_flagged_cell_cannot_be_revealed_and_remains_flagged():
    # Given: same in_progress board, (0,0) flagged, flag_count 1.
    game = make_in_progress_game_with_flag_at_origin()

    # When: the player attempts to reveal the flagged cell (0,0).
    # Rules: revealing a flagged cell is refused. The board must be unchanged,
    # so the refusal may surface as InvalidActionError or be ignored.
    try:
        game.reveal_cell(row=0, column=0)
    except Exception as exc_info:
        assert type(exc_info).__name__ == "InvalidActionError"

    # Then: (0,0) is still flagged, not revealed.
    assert cell_at(game, 0, 0)["state"] == "flagged"
    # Then: flag_count is unchanged at 1.
    assert game.flag_count == 1
    # Then: the game is still in progress; a refused reveal ends nothing.
    assert game.status == "in_progress"
