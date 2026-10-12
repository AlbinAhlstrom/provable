"""Build exact boards for rule tests: `*` is a mine, `.` is safe."""
from src.domain.game import Game


def board(art: str, now: float = 0.0) -> Game:
    lines = [line.strip() for line in art.strip().splitlines()]
    mines = {
        (r, c)
        for r, line in enumerate(lines)
        for c, ch in enumerate(line)
        if ch == "*"
    }
    return Game.with_mines(rows=len(lines), cols=len(lines[0]), mines=mines, now=now)
