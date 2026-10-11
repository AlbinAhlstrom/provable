import pytest

from src.domain.best_time import BestTime


ACHIEVED_FIRST = "2024-01-10T09:00:00+00:00"
ACHIEVED_LATER = "2024-02-20T18:30:00+00:00"


def _make(difficulty_id, best_seconds=100):
    return BestTime(
        id="bt-1",
        difficulty_id=difficulty_id,
        game_id="game-first",
        best_seconds=best_seconds,
        achieved_at=ACHIEVED_FIRST,
    )


@pytest.mark.parametrize("difficulty_id", ["beginner", "intermediate", "expert"])
def test_new_best_time_holds_exactly_constructed_values(difficulty_id):
    bt = BestTime(
        id="bt-1",
        difficulty_id=difficulty_id,
        game_id="game-first",
        best_seconds=100,
        achieved_at=ACHIEVED_FIRST,
    )

    # Constructed from the first win: the values passed in are kept as-is.
    assert bt.id == "bt-1"
    assert bt.difficulty_id == difficulty_id
    assert bt.game_id == "game-first"
    assert bt.best_seconds == 100
    assert bt.achieved_at == ACHIEVED_FIRST
    # Nothing has been called, so no events were raised.
    assert bt.events == []


@pytest.mark.parametrize(
    "record_difficulty, win_difficulty, elapsed, expect_update",
    [
        # Standard difficulty, faster by one second (just inside the < boundary): update.
        ("beginner", "beginner", 99, True),
        # Same rule for another standard difficulty (each kind is covered).
        ("expert", "expert", 99, True),
        ("intermediate", "intermediate", 99, True),
        # Equal time (exactly at the boundary): elapsed < best is false, best kept.
        ("beginner", "beginner", 100, False),
        ("expert", "expert", 100, False),
        # Slower time: best kept.
        ("beginner", "beginner", 101, False),
        # Custom difficulty with a faster time: changes nothing.
        ("beginner", "custom", 99, False),
        # Different standard difficulty with a faster time: changes nothing.
        ("beginner", "intermediate", 99, False),
    ],
)
def test_record_win(record_difficulty, win_difficulty, elapsed, expect_update):
    # Given: a stored best of 100 seconds from game-first at ACHIEVED_FIRST.
    bt = _make(record_difficulty, best_seconds=100)

    # When
    bt.record_win(
        game_id="game-second",
        difficulty_id=win_difficulty,
        elapsed_seconds=elapsed,
        achieved_at=ACHIEVED_LATER,
    )

    # Identity and difficulty of the record never change.
    assert bt.id == "bt-1"
    assert bt.difficulty_id == record_difficulty

    if expect_update:
        # Same standard difficulty and 99 < 100: best becomes 99,
        # game_id and achieved_at come from the new win.
        assert bt.best_seconds == elapsed
        assert bt.game_id == "game-second"
        assert bt.achieved_at == ACHIEVED_LATER
    else:
        # Either elapsed >= 100, or the win's difficulty is custom / differs
        # from this record's: the stored best from game-first stays.
        assert bt.best_seconds == 100
        assert bt.game_id == "game-first"
        assert bt.achieved_at == ACHIEVED_FIRST
