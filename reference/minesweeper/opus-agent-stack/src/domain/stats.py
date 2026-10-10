"""Statistics derived from finished games. Nothing here is stored."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Optional

from src.domain.game import DIFFICULTIES, WON, Game


@dataclass(frozen=True)
class DifficultyStats:
    played: int = 0
    won: int = 0
    best_seconds: Optional[float] = None

    @property
    def win_rate(self) -> float:
        return self.won / self.played if self.played else 0

    def as_dict(self) -> dict[str, Any]:
        return {**asdict(self), "win_rate": self.win_rate}


def summarize(games: Iterable[Game]) -> dict[str, DifficultyStats]:
    """Per difficulty: finished games, wins and the fastest win."""
    stats = {difficulty: DifficultyStats() for difficulty in DIFFICULTIES}
    for game in games:
        if not game.is_over:
            continue
        current = stats[game.difficulty]
        won = game.status == WON
        best = current.best_seconds
        if won:
            seconds = game.elapsed(game.finished_at)
            best = seconds if best is None else min(best, seconds)
        stats[game.difficulty] = DifficultyStats(
            played=current.played + 1, won=current.won + int(won), best_seconds=best
        )
    return stats
