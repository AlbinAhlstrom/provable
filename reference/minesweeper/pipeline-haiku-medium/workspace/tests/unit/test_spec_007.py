import pytest

from src.domain.game_session import GameSession


def _new_ready_session() -> GameSession:
    # Given a newly created beginner-shaped session: 9 rows, 9 columns, 10 mines.
    # Status is ready, no mines are placed yet, and all 81 cells are hidden.
    return GameSession(
        id="game-first-reveal",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )


def _cell(game: GameSession, row: int, column: int) -> dict:
    # Look up the cell record at the given position.
    return next(
        c for c in game.cells if c["row"] == row and c["column"] == column
    )


@pytest.mark.parametrize("row,column", [(0, 0), (0, 8), (4, 4), (8, 8)])
def test_first_revealed_cell_is_never_a_mine(row, column):
    # Placement is random, so the rule is checked over many fresh sessions.
    # Each session is a new Ready board where the first reveal is the chosen cell.
    for _ in range(50):
        game = _new_ready_session()

        # When the player reveals the cell first.
        game.reveal_cell(row=row, column=column)

        # The first reveal of a ready session starts the game, so status is in_progress.
        # The revealed cell is excluded from mine placement, so the game is not lost.
        assert game.status == "in_progress"

        # Expected: the revealed cell at (row, column) has has_mine false.
        # Mines are placed only on the other 80 cells, so this cell cannot hold one.
        assert _cell(game, row, column)["has_mine"] is False
