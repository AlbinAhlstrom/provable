import pytest

from src.domain.best_time import BestTime


STORED_BEST = 100
STORED_GAME_ID = "game-old"
STORED_ACHIEVED_AT = "2024-01-01T10:00:00+00:00"
NEW_GAME_ID = "game-new"
NEW_ACHIEVED_AT = "2024-02-01T12:30:00+00:00"


def _stored_best(difficulty_id: str) -> BestTime:
    return BestTime(
        id="best-1",
        difficulty_id=difficulty_id,
        game_id=STORED_GAME_ID,
        best_seconds=STORED_BEST,
        achieved_at=STORED_ACHIEVED_AT,
    )


@pytest.mark.parametrize("difficulty_id", ["beginner", "expert"])
def test_win_just_faster_than_stored_best_replaces_it(difficulty_id):
    best = _stored_best(difficulty_id)

    best.record_win(
        game_id=NEW_GAME_ID,
        difficulty_id=difficulty_id,
        elapsed_seconds=STORED_BEST - 1,
        achieved_at=NEW_ACHIEVED_AT,
    )

    # The record's difficulty is standard (beginner or expert), so the
    # custom-difficulty rule does not apply. The win has the same difficulty_id
    # as the record, and the game was won, so the lost/abandoned rule does not
    # apply. Elapsed is 99 and the stored best is 100. Since 99 < 100, the
    # "slower or equal keeps best" rule does not apply. So the best time
    # becomes 99.
    assert best.best_seconds == STORED_BEST - 1
    # When the best time is replaced, the game_id is taken from the new win.
    assert best.game_id == NEW_GAME_ID
    # When the best time is replaced, achieved_at is taken from the new win.
    assert best.achieved_at == NEW_ACHIEVED_AT
    # The difficulty of the record is unchanged.
    assert best.difficulty_id == difficulty_id


@pytest.mark.parametrize("difficulty_id", ["beginner", "expert"])
def test_win_exactly_equal_to_stored_best_does_not_replace_it(difficulty_id):
    best = _stored_best(difficulty_id)

    best.record_win(
        game_id=NEW_GAME_ID,
        difficulty_id=difficulty_id,
        elapsed_seconds=STORED_BEST,
        achieved_at=NEW_ACHIEVED_AT,
    )

    # This case uses the same standard difficulty, the same matching
    # difficulty_id and the same won game as the accepted case. Only the
    # elapsed time differs. Elapsed is 100 and the stored best is 100. The
    # replacement needs elapsed < 100, which does not hold. The "slower or
    # equal keeps best" rule applies, so the best time stays 100.
    assert best.best_seconds == STORED_BEST
    # The stored best is kept, so game_id still refers to the old game.
    assert best.game_id == STORED_GAME_ID
    # The stored best is kept, so achieved_at keeps its old value.
    assert best.achieved_at == STORED_ACHIEVED_AT
    # The difficulty of the record is unchanged.
    assert best.difficulty_id == difficulty_id
