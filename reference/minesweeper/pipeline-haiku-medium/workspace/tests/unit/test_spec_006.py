from src.domain.game_session import GameSession


def make_expert_ready_session() -> GameSession:
    # Expert preset: 16 rows, 30 columns, 99 mines. The constructor creates
    # 16 * 30 = 480 hidden cell records, all with has_mine False.
    # A large board with many mines means one reveal cannot reach every safe
    # cell, so the reveal cannot also end the game as a win.
    return GameSession(
        id="session-1",
        difficulty_id="expert",
        rows=16,
        columns=30,
        mine_count=99,
    )


def test_mines_placed_at_random_and_status_in_progress_after_first_reveal():
    # Given a session in Ready state with no mines placed.
    session = make_expert_ready_session()
    assert session.status == "ready"
    # Before the first reveal, no cell holds a mine (constructor state).
    assert sum(1 for cell in session.cells if cell["has_mine"]) == 0

    # When the player reveals a hidden cell for the first time.
    session.reveal_cell(row=8, column=15)

    # Then the session status becomes in_progress.
    # Working: the session is in ready, the cell (8, 15) is hidden and unflagged,
    # so the reveal is allowed. It is the first reveal, so mines are placed and
    # the status moves to in_progress. Only 1 cell was revealed among 1381 safe
    # cells, so the game is not won and not lost (the cell is safe, a first
    # reveal never hits a mine).
    assert session.status == "in_progress"

    # And mines are placed at random: exactly 99 cells have has_mine true.
    # Working: mine_count is 99 for this board, and placement happens once on the
    # first reveal, so the count of has_mine true cells equals 99.
    mines_placed = sum(1 for cell in session.cells if cell["has_mine"])
    assert mines_placed == 99
