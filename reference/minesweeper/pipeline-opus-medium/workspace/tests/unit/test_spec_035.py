import pytest

from src.domain.best_time import BestTime


def _no_best_stored(difficulty_id):
    # Build the record as it is when newly created, then clear the stored best,
    # so that no best time is held for this difficulty.
    best = BestTime(
        id=f"best-{difficulty_id}",
        difficulty_id=difficulty_id,
        game_id="game-old",
        best_seconds=500,
        achieved_at="2024-01-01T00:00:00Z",
    )
    best.best_seconds = None
    best.game_id = None
    best.achieved_at = None
    return best


@pytest.mark.parametrize(
    "difficulty_id, game_id, elapsed_seconds, achieved_at",
    [
        ("beginner", "game-b-1", 42, "2024-03-01T10:15:00Z"),
        ("intermediate", "game-i-1", 137, "2024-03-02T11:20:00Z"),
        ("expert", "game-e-1", 389, "2024-03-03T12:25:00Z"),
    ],
)
def test_first_win_sets_best_time(difficulty_id, game_id, elapsed_seconds, achieved_at):
    # Given no best time stored for this standard difficulty
    best = _no_best_stored(difficulty_id)

    # When the player wins a game of that difficulty in T seconds
    best.record_win(
        game_id=game_id,
        difficulty_id=difficulty_id,
        elapsed_seconds=elapsed_seconds,
        achieved_at=achieved_at,
    )

    # Then a best time of T is recorded for that difficulty.
    # There is no stored best, so the "slower or equal" rule has nothing to
    # compare against. The difficulty is standard and matches this record, so
    # the custom rule and the different-difficulty rule do not apply. The game
    # was won, so the lost/abandoned rule does not apply.
    # Expected: best_seconds == T.
    assert best.best_seconds == elapsed_seconds

    # The winning game is credited with the best time.
    assert best.game_id == game_id

    # The moment of the winning game is recorded unchanged.
    assert best.achieved_at == achieved_at

    # Identity and difficulty of the record do not change.
    assert best.id == f"best-{difficulty_id}"
    assert best.difficulty_id == difficulty_id


@pytest.mark.parametrize(
    "record_difficulty, win_difficulty",
    [
        # Custom difficulty: custom games record no best time.
        ("beginner", "custom"),
        # A different standard difficulty: this record is not for that difficulty.
        ("beginner", "intermediate"),
    ],
)
def test_first_win_of_other_difficulty_sets_no_best_time(record_difficulty, win_difficulty):
    # Given no best time stored (same arrangement as the accepted case)
    best = _no_best_stored(record_difficulty)

    # When a win arrives whose difficulty is custom or differs from this record's
    best.record_win(
        game_id="game-b-1",
        difficulty_id=win_difficulty,
        elapsed_seconds=42,
        achieved_at="2024-03-01T10:15:00Z",
    )

    # Then nothing is created or changed: the custom rule / different-difficulty
    # rule decides alone, so the cleared best stays cleared.
    assert best.best_seconds is None
    assert best.game_id is None
    assert best.achieved_at is None

    # The record keeps its own difficulty.
    assert best.difficulty_id == record_difficulty
