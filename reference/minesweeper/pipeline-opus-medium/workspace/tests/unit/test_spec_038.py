import pytest

from src.domain.best_time import BestTime


def _stored_best(difficulty_id):
    # Given: a stored best time of 100 seconds for a standard difficulty,
    # set by an earlier win (game "g-old").
    best = BestTime(
        id="bt-1",
        difficulty_id=difficulty_id,
        game_id="g-old",
        best_seconds=100,
        achieved_at="2024-01-01T10:00:00Z",
    )
    best.events = []
    return best


@pytest.mark.parametrize("outcome", ["lost", "abandoned"])
@pytest.mark.parametrize("difficulty_id", ["beginner", "expert"])
def test_lost_or_abandoned_game_does_not_change_best_time(outcome, difficulty_id):
    best = _stored_best(difficulty_id)
    before = best.to_dict()

    # When: a game of the same standard difficulty ends lost/abandoned after
    # 50 seconds, which is faster than the stored 100. Had it been a win, the
    # "new best time" rule would apply (50 < 100). Because it is not a win,
    # only wins can produce a best time, so nothing changes.
    best.record_game_end(
        game_id="g-new",
        difficulty_id=difficulty_id,
        outcome=outcome,
        elapsed_seconds=50,
        ended_at="2024-02-01T12:00:00Z",
    )

    # best_seconds: stored 100; a non-win cannot lower it -> still 100
    assert best.best_seconds == 100
    # game_id: still the game that set the stored best -> "g-old"
    assert best.game_id == "g-old"
    # achieved_at: still the time of the earlier win
    assert best.achieved_at == "2024-01-01T10:00:00Z"
    # difficulty_id: unchanged
    assert best.difficulty_id == difficulty_id
    # no new best was created or changed -> no events recorded
    assert best.events == []
    # the whole record is identical to before
    assert best.to_dict() == before


@pytest.mark.parametrize("difficulty_id", ["beginner", "expert"])
def test_won_game_end_with_same_inputs_does_set_new_best(difficulty_id):
    best = _stored_best(difficulty_id)

    # When: identical inputs to the lost/abandoned case, except the outcome
    # is "won". Standard difficulty, same difficulty_id, 50 < 100, so the
    # "new best time" rule applies: best becomes 50, game and time updated.
    best.record_game_end(
        game_id="g-new",
        difficulty_id=difficulty_id,
        outcome="won",
        elapsed_seconds=50,
        ended_at="2024-02-01T12:00:00Z",
    )

    # best_seconds: 50 < 100 -> 50
    assert best.best_seconds == 50
    # game_id: updated to the winning game
    assert best.game_id == "g-new"
    # achieved_at: updated to when the win ended
    assert best.achieved_at == "2024-02-01T12:00:00Z"
    # difficulty_id: unchanged
    assert best.difficulty_id == difficulty_id
