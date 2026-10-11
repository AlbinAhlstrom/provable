import pytest

from src.domain.best_time import BestTime


STANDARD_DIFFICULTIES = ["beginner", "intermediate", "expert"]


def _stored_best(difficulty_id: str, best_seconds: int) -> BestTime:
    # Given: a stored best time of B seconds for a standard difficulty,
    # recorded from an earlier game "game-old" at a fixed time.
    return BestTime(
        id="bt-1",
        difficulty_id=difficulty_id,
        game_id="game-old",
        best_seconds=best_seconds,
        achieved_at="2024-01-01T10:00:00Z",
    )


@pytest.mark.parametrize("difficulty_id", STANDARD_DIFFICULTIES)
def test_equal_win_keeps_stored_best(difficulty_id):
    best = _stored_best(difficulty_id, 100)

    # When: the player wins a game of the same difficulty in exactly B seconds.
    best.record_win(
        game_id="game-new",
        difficulty_id=difficulty_id,
        elapsed_seconds=100,
        achieved_at="2024-02-01T12:00:00Z",
    )

    # Stored best is 100 and the win took 100: 100 < 100 is false, so this is
    # not a new best. Difficulty is standard and matches the record, so the
    # custom rule does not apply; it is a win, so the lost/abandoned rule does
    # not apply. The best stays 100.
    assert best.best_seconds == 100
    # The best was not replaced, so it still belongs to the original game.
    assert best.game_id == "game-old"
    # The best was not replaced, so its achieved_at is the original one.
    assert best.achieved_at == "2024-01-01T10:00:00Z"
    # Difficulty of the record never changes.
    assert best.difficulty_id == difficulty_id


@pytest.mark.parametrize("difficulty_id", STANDARD_DIFFICULTIES)
def test_slower_win_keeps_stored_best(difficulty_id):
    best = _stored_best(difficulty_id, 100)

    # When: the player wins a game of the same difficulty in B + 1 seconds.
    best.record_win(
        game_id="game-new",
        difficulty_id=difficulty_id,
        elapsed_seconds=101,
        achieved_at="2024-02-01T12:00:00Z",
    )

    # Stored best is 100 and the win took 101: 101 < 100 is false, so the
    # slower time does not replace the best. The best stays 100.
    assert best.best_seconds == 100
    # Not replaced, so the original game remains the holder.
    assert best.game_id == "game-old"
    # Not replaced, so the original achieved_at remains.
    assert best.achieved_at == "2024-01-01T10:00:00Z"


@pytest.mark.parametrize("difficulty_id", STANDARD_DIFFICULTIES)
def test_win_just_faster_than_best_replaces_it(difficulty_id):
    best = _stored_best(difficulty_id, 100)

    # When: the player wins a game of the same difficulty in B - 1 seconds
    # (just beyond the limit of "not faster than the stored best").
    best.record_win(
        game_id="game-new",
        difficulty_id=difficulty_id,
        elapsed_seconds=99,
        achieved_at="2024-02-01T12:00:00Z",
    )

    # Stored best is 100 and the win took 99: 99 < 100 is true, standard
    # difficulty matching the record, a win: the new-best rule applies and
    # the best becomes 99.
    assert best.best_seconds == 99
    # The new best belongs to the game that achieved it.
    assert best.game_id == "game-new"
    # The new best carries the time it was achieved.
    assert best.achieved_at == "2024-02-01T12:00:00Z"
    # Difficulty of the record never changes.
    assert best.difficulty_id == difficulty_id
