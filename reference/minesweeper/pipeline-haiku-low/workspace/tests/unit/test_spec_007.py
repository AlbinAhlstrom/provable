from src.domain.game import Game


def make_board(rows: int = 9, columns: int = 9, target_state: str = "hidden"):
    """Build a full grid of cells, all hidden and safe, with the target at (4, 4)."""
    cells = []
    for r in range(rows):
        for c in range(columns):
            cells.append(
                {
                    "id": f"{r}-{c}",
                    "row": r,
                    "column": c,
                    "has_mine": False,
                    "adjacent_mine_count": 0,
                    "state": target_state if (r, c) == (4, 4) else "hidden",
                }
            )
    return cells


def make_game(target_state: str = "hidden", flag_count: int = 0) -> Game:
    game = Game(id="game-right-click")
    game.difficulty = "Beginner"
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.elapsed_seconds = 0
    game.mine_count = 10
    game.flag_count = flag_count
    game.cells = make_board(target_state=target_state)
    return game


def cell_at(game: Game, row: int, column: int):
    for cell in game.cells:
        if cell["row"] == row and cell["column"] == column:
            return cell
    raise AssertionError(f"no cell at {row},{column}")


def test_right_click_hidden_cell_becomes_flagged():
    # Given: in-progress 9x9 board, target (4,4) is hidden, flag_count 0.
    # No mines, no other flags, so nothing else in the rules interferes.
    game = make_game(target_state="hidden", flag_count=0)

    # When: the player right-clicks (4,4).
    game.toggle_flag(row=4, column=4)

    # Then: hidden -> flagged, and flag_count rises from 0 to 1.
    assert cell_at(game, 4, 4)["state"] == "flagged"
    assert game.flag_count == 1


def test_right_click_flagged_cell_becomes_hidden():
    # Given: in-progress board, target (4,4) is flagged, flag_count 1 (consistent with one flag).
    game = make_game(target_state="flagged", flag_count=1)

    # When: the player right-clicks (4,4) again.
    game.toggle_flag(row=4, column=4)

    # Then: flagged -> hidden (no question mark state), and flag_count falls from 1 to 0.
    assert cell_at(game, 4, 4)["state"] == "hidden"
    assert game.flag_count == 0


def test_right_click_revealed_cell_is_unchanged():
    # Given: in-progress board, target (4,4) is revealed, flag_count 0.
    # Same board and same flag_count as the hidden case; only the target state differs.
    game = make_game(target_state="revealed", flag_count=0)

    # When: the player right-clicks (4,4).
    game.toggle_flag(row=4, column=4)

    # Then: a revealed cell cannot be flagged, so its state stays revealed and flag_count stays 0.
    assert cell_at(game, 4, 4)["state"] == "revealed"
    assert game.flag_count == 0
