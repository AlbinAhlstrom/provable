import pytest

from src.domain.game import Game


def make_game(status):
    # A beginner game (9x9, 10 mines) constructed with only its required fields.
    # Only the status differs between cases, so the transition rule alone
    # decides each outcome.
    game = Game(
        id="game-1",
        difficulty_id="beginner",
        width=9,
        height=9,
        mine_count=10,
        remaining_mines=10,
        created_at="2024-01-01T10:00:00Z",
    )
    game.status = status
    return game


@pytest.mark.parametrize(
    "from_status, to_status",
    [
        ("Ready", "Playing"),
        ("Playing", "Won"),
        ("Playing", "Lost"),
        ("Ready", "Abandoned"),
        ("Playing", "Abandoned"),
    ],
)
def test_allowed_status_transitions_are_applied(from_status, to_status):
    game = make_game(from_status)

    game.transition_to(status=to_status)

    # The allowed set is Ready->Playing, Playing->Won, Playing->Lost and
    # Ready/Playing->Abandoned. (from_status, to_status) is in that set,
    # so no error is raised and the status becomes the requested one.
    assert game.status == to_status


@pytest.mark.parametrize(
    "from_status, to_status",
    [
        # Nearest to Playing->Won / Playing->Lost: same target, but from Ready.
        ("Ready", "Won"),
        ("Ready", "Lost"),
        # Reverse of Ready->Playing.
        ("Playing", "Ready"),
        # Nearest to Ready/Playing->Abandoned: same target, from a finished game.
        ("Won", "Abandoned"),
        ("Lost", "Abandoned"),
        # Between the two end states.
        ("Won", "Lost"),
        ("Lost", "Won"),
        # Leaving an end state back to play.
        ("Won", "Playing"),
        ("Lost", "Playing"),
        ("Abandoned", "Playing"),
        ("Abandoned", "Ready"),
    ],
)
def test_other_status_transitions_are_refused(from_status, to_status):
    game = make_game(from_status)

    with pytest.raises(Exception) as exc_info:
        game.transition_to(status=to_status)

    # (from_status, to_status) is not one of Ready->Playing, Playing->Won,
    # Playing->Lost, Ready->Abandoned or Playing->Abandoned, so the change
    # is refused with InvalidTransitionError.
    assert type(exc_info.value).__name__ == "InvalidTransitionError"
    # A refused transition leaves the status as it was.
    assert game.status == from_status


@pytest.mark.parametrize("from_status", ["Ready", "Playing"])
def test_abandon_game_from_ready_or_playing_becomes_abandoned(from_status):
    game = make_game(from_status)

    game.abandon_game()

    # Ready->Abandoned and Playing->Abandoned are allowed, so abandon_game
    # moves the game to Abandoned.
    assert game.status == "Abandoned"


@pytest.mark.parametrize("from_status", ["Won", "Lost"])
def test_abandon_game_from_finished_game_keeps_outcome_without_error(from_status):
    game = make_game(from_status)

    # abandon_game is an ignored player action for a finished game: the
    # Won/Lost->Abandoned transition is not allowed, and ignored player
    # actions never raise, so no error and the outcome is kept.
    game.abandon_game()

    assert game.status == from_status
