import pytest

from src.domain.game_session import GameSession


def count_mines(session):
    return sum(1 for cell in session.cells if cell["has_mine"])


# Preset difficulties: (difficulty_id, rows, columns, mine_count, reveal_row, reveal_column)
PRESETS = [
    ("beginner", 9, 9, 10, 4, 4),
    ("expert", 16, 30, 99, 8, 15),
]


@pytest.mark.parametrize(
    "difficulty_id, rows, columns, mine_count, reveal_row, reveal_column", PRESETS
)
def test_exact_mine_count_placed_after_first_reveal(
    difficulty_id, rows, columns, mine_count, reveal_row, reveal_column
):
    # Given a new session at the preset difficulty, in state ready, no mines placed.
    # The constructor gives rows*columns hidden cells, all has_mine false.
    session = GameSession(
        id="game-1",
        difficulty_id=difficulty_id,
        rows=rows,
        columns=columns,
        mine_count=mine_count,
    )
    assert session.status == "ready"
    assert count_mines(session) == 0

    # When the first cell is revealed (a safe cell in the middle of the board).
    # Mines are placed at random avoiding that cell; the cell is not a mine,
    # so the game is not lost. Spreading only reveals cells and cannot change has_mine.
    session.reveal_cell(row=reveal_row, column=reveal_column)

    # Then exactly mine_count cells have has_mine true.
    # The preset places exactly mine_count mines on distinct cells, and each
    # cell holds at most one mine flag, so the count of true flags equals mine_count.
    assert count_mines(session) == mine_count


def test_mine_count_one_beyond_preset_is_refused():
    # Given a session at beginner difficulty, whose preset is 9 rows, 9 columns, 10 mines.
    session = GameSession(
        id="game-2",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )

    # When a new game is started with mine_count 11, one beyond the preset of 10.
    # 11 does not match the beginner preset, so the start is refused by the rules.
    with pytest.raises(Exception) as exc_info:
        session.start_new_game(
            difficulty_id="beginner",
            rows=9,
            columns=9,
            mine_count=11,
        )

    # Then the refusal is InvalidDifficultyError.
    assert type(exc_info.value).__name__ == "InvalidDifficultyError"


def test_mine_count_exactly_at_preset_is_accepted_and_placed():
    # Given a session at beginner difficulty.
    session = GameSession(
        id="game-3",
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )

    # When a new game is started with mine_count 10, exactly the preset value.
    # 10 matches the beginner preset, so the start is accepted and the board is hidden, no mines.
    session.start_new_game(
        difficulty_id="beginner",
        rows=9,
        columns=9,
        mine_count=10,
    )
    assert session.status == "ready"
    assert count_mines(session) == 0

    # And when the first cell is revealed at (4, 4), a safe cell in the middle.
    # The game becomes in_progress; the reveal cannot lose or win the game
    # since 71 safe cells remain hidden after at most a small spread.
    session.reveal_cell(row=4, column=4)

    # Then exactly 10 cells have has_mine true: the accepted limit places all mines.
    assert count_mines(session) == 10
