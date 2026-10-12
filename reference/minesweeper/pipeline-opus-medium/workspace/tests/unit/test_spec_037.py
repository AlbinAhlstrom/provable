import pytest

from src.domain.best_time import BestTime


def _stored_best(difficulty_id: str) -> BestTime:
    # Given: a stored best time of 100 seconds for a standard difficulty,
    # recorded from game "game-first" at a fixed time, with no events.
    return BestTime(
        id="bt-1",
        difficulty_id=difficulty_id,
        game_id="game-first",
        best_seconds=100,
        achieved_at="2024-01-01T10:00:00Z",
    )


@pytest.mark.parametrize("stored_difficulty", ["beginner", "expert"])
def test_custom_win_does_not_change_best_time(stored_difficulty):
    best = _stored_best(stored_difficulty)

    # When: a game on Custom difficulty is won faster than the stored best.
    # The game is Won, so the "lost or abandoned" rule does not apply.
    best.record_win(
        game_id="game-custom",
        difficulty_id="custom",
        elapsed_seconds=50,
        achieved_at="2024-01-02T12:00:00Z",
    )

    # Then: custom difficulty changes nothing. 50 < 100 would beat the record
    # for a standard difficulty, so only the custom rule keeps it at 100.
    assert best.best_seconds == 100
    # The game that holds the record is still the first one.
    assert best.game_id == "game-first"
    # The time the record was achieved is unchanged.
    assert best.achieved_at == "2024-01-01T10:00:00Z"
    # The record still belongs to its standard difficulty, not "custom".
    assert best.difficulty_id == stored_difficulty
    # The record keeps its id.
    assert best.id == "bt-1"
    # Nothing happened, so no events are recorded.
    assert best.events == []


@pytest.mark.parametrize("stored_difficulty", ["beginner", "expert"])
def test_same_faster_win_on_standard_difficulty_does_update_best_time(stored_difficulty):
    best = _stored_best(stored_difficulty)

    # When: the identical win (same game, same time, same moment) is played on
    # the record's own standard difficulty instead of custom.
    best.record_win(
        game_id="game-custom",
        difficulty_id=stored_difficulty,
        elapsed_seconds=50,
        achieved_at="2024-01-02T12:00:00Z",
    )

    # Then: standard difficulty and 50 < 100, so the new best is 50.
    assert best.best_seconds == 50
    # The record now points at the game that set the new best.
    assert best.game_id == "game-custom"
    # The achievement time is that of the new best.
    assert best.achieved_at == "2024-01-02T12:00:00Z"
    # The difficulty stays the same standard difficulty.
    assert best.difficulty_id == stored_difficulty
