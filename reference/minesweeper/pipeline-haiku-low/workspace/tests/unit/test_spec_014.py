from src.domain.game import Game


def _in_progress_game(elapsed_seconds: int) -> Game:
    # Given a game in progress whose timer has run for elapsed_seconds.
    # The timer display does not depend on the board, so cells stays empty
    # as it is for a newly created game.
    game = Game(id="game-timer-cap")
    game.status = "in_progress"
    game.started_at = "2024-01-01T10:00:00"
    game.elapsed_seconds = elapsed_seconds
    return game


def test_timer_display_shows_999_when_elapsed_is_just_beyond_cap():
    # Elapsed is 1000 seconds, one second beyond the 999 limit.
    # The cap is 999, so the displayed value is min(1000, 999) = 999.
    game = _in_progress_game(elapsed_seconds=1000)

    shown = game.timer_display()

    assert shown == 999


def test_timer_display_shows_999_when_elapsed_is_exactly_at_cap():
    # Elapsed is exactly 999 seconds, the limit itself.
    # The cap is 999, so min(999, 999) = 999 is shown.
    game = _in_progress_game(elapsed_seconds=999)

    shown = game.timer_display()

    assert shown == 999
