"""The rules of Minesweeper. Plain Python: no framework, no I/O, no clock, no hidden randomness.

Time is handed in as `now` (seconds); the mine layout follows from the stored seed.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable, Optional

from src.domain.minefield import Cell, neighbours, place_mines

# difficulty -> (rows, cols, mines)
PRESETS: dict[str, tuple[int, int, int]] = {
    "beginner": (9, 9, 10),
    "intermediate": (16, 16, 40),
    "expert": (16, 30, 99),
}
CUSTOM = "custom"
DIFFICULTIES = (*PRESETS, CUSTOM)

MIN_SIDE = 5
MAX_ROWS = 24
MAX_COLS = 30
FIRST_AREA = 9  # the first cell and its neighbours never hold a mine

READY, PLAYING, WON, LOST = "ready", "playing", "won", "lost"


class GameError(Exception):
    """A request the rules refuse."""


class InvalidConfiguration(GameError):
    pass


class OutOfBounds(GameError):
    pass


class GameOver(GameError):
    pass


def max_mines(rows: int, cols: int) -> int:
    return rows * cols - FIRST_AREA


@dataclass(frozen=True)
class GameView:
    """What a player is allowed to see. Never carries the seed or an unrevealed mine."""

    id: str
    difficulty: str
    rows: int
    cols: int
    mine_count: int
    status: str
    mines_remaining: int
    elapsed_seconds: float
    created_at: float
    board: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Game:
    id: str
    difficulty: str
    rows: int
    cols: int
    mine_count: int
    seed: int
    created_at: float
    status: str = READY
    mines: Optional[frozenset[Cell]] = None  # None until the first reveal
    revealed: set[Cell] = field(default_factory=set)
    flags: set[Cell] = field(default_factory=set)
    exploded: Optional[Cell] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

    # ---- creation ---------------------------------------------------------

    @classmethod
    def new(
        cls,
        id: str,
        difficulty: str,
        seed: int,
        now: float,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        mines: Optional[int] = None,
    ) -> "Game":
        if difficulty in PRESETS:
            rows, cols, mines = PRESETS[difficulty]
        elif difficulty == CUSTOM:
            _check_custom(rows, cols, mines)
        else:
            raise InvalidConfiguration(
                f"Unknown difficulty '{difficulty}'. Choose one of: {', '.join(DIFFICULTIES)}."
            )
        return cls(
            id=id, difficulty=difficulty, rows=rows, cols=cols, mine_count=mines,
            seed=seed, created_at=now,
        )

    @classmethod
    def with_mines(
        cls,
        rows: int,
        cols: int,
        mines: Iterable[Cell],
        id: str = "fixed",
        difficulty: str = CUSTOM,
        now: float = 0.0,
    ) -> "Game":
        """A game whose mines are already laid, for exact scenarios (tests, puzzles)."""
        layout = frozenset(mines)
        if any(not (0 <= r < rows and 0 <= c < cols) for r, c in layout):
            raise InvalidConfiguration("A mine lies outside the board.")
        return cls(
            id=id, difficulty=difficulty, rows=rows, cols=cols, mine_count=len(layout),
            seed=0, created_at=now, mines=layout,
        )

    # ---- actions ----------------------------------------------------------

    def reveal(self, row: int, col: int, now: float) -> None:
        cell = self._playable_cell(row, col)
        if cell in self.revealed or cell in self.flags:
            return
        self._begin(cell, now)
        self._open([cell], now)

    def toggle_flag(self, row: int, col: int) -> None:
        cell = self._playable_cell(row, col)
        if cell in self.revealed:
            return
        self.flags ^= {cell}

    def chord(self, row: int, col: int, now: float) -> None:
        cell = self._playable_cell(row, col)
        if cell not in self.revealed:
            return
        number = self.adjacent_mines(row, col)
        around = neighbours(self.rows, self.cols, cell)
        if number == 0 or sum(1 for n in around if n in self.flags) != number:
            return
        self._open([n for n in around if n not in self.flags and n not in self.revealed], now)

    # ---- queries ----------------------------------------------------------

    @property
    def is_over(self) -> bool:
        return self.status in (WON, LOST)

    @property
    def mines_remaining(self) -> int:
        return self.mine_count - len(self.flags)

    def adjacent_mines(self, row: int, col: int) -> int:
        mines = self.mines or frozenset()
        return sum(1 for n in neighbours(self.rows, self.cols, (row, col)) if n in mines)

    def elapsed(self, now: float) -> float:
        if self.started_at is None:
            return 0
        end = self.finished_at if self.finished_at is not None else now
        return max(0, end - self.started_at)

    def board(self) -> list[str]:
        """One string per row. H hidden, F flag, 0-8 revealed; after a loss also
        M unflagged mine, X the mine that exploded, W a flag on a safe cell."""
        return [
            "".join(self._symbol((r, c)) for c in range(self.cols))
            for r in range(self.rows)
        ]

    def view(self, now: float) -> GameView:
        return GameView(
            id=self.id,
            difficulty=self.difficulty,
            rows=self.rows,
            cols=self.cols,
            mine_count=self.mine_count,
            status=self.status,
            mines_remaining=self.mines_remaining,
            elapsed_seconds=self.elapsed(now),
            created_at=self.created_at,
            board=self.board(),
        )

    # ---- storage form -----------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "difficulty": self.difficulty,
            "rows": self.rows,
            "cols": self.cols,
            "mine_count": self.mine_count,
            "seed": self.seed,
            "created_at": self.created_at,
            "status": self.status,
            "mines": None if self.mines is None else sorted(map(list, self.mines)),
            "revealed": sorted(map(list, self.revealed)),
            "flags": sorted(map(list, self.flags)),
            "exploded": None if self.exploded is None else list(self.exploded),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Game":
        def cells(items: Iterable[Iterable[int]]) -> set[Cell]:
            return {(int(r), int(c)) for r, c in items}

        return cls(
            id=data["id"],
            difficulty=data["difficulty"],
            rows=data["rows"],
            cols=data["cols"],
            mine_count=data["mine_count"],
            seed=data["seed"],
            created_at=data["created_at"],
            status=data["status"],
            mines=None if data["mines"] is None else frozenset(cells(data["mines"])),
            revealed=cells(data["revealed"]),
            flags=cells(data["flags"]),
            exploded=None if data["exploded"] is None else tuple(data["exploded"]),
            started_at=data["started_at"],
            finished_at=data["finished_at"],
        )

    # ---- internals --------------------------------------------------------

    def _playable_cell(self, row: int, col: int) -> Cell:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise OutOfBounds(
                f"Row {row + 1}, column {col + 1} is outside the board "
                f"({self.rows} rows, {self.cols} columns)."
            )
        if self.is_over:
            raise GameOver(f"This game is already {self.status}. Start a new one.")
        return (row, col)

    def _begin(self, first: Cell, now: float) -> None:
        """The first reveal lays the mines around the chosen cell and starts the clock."""
        if self.status != READY:
            return
        if self.mines is None:
            self.mines = place_mines(self.rows, self.cols, self.mine_count, first, self.seed)
        self.status = PLAYING
        self.started_at = now

    def _open(self, cells: list[Cell], now: float) -> None:
        """Reveal the cells, spreading through zeros; settle win or loss."""
        assert self.mines is not None
        hit = [c for c in cells if c in self.mines]
        if hit:
            self.revealed.update(c for c in cells if c not in self.mines)
            self.exploded = hit[0]
            self._finish(LOST, now)
            return

        pending = list(cells)
        while pending:
            cell = pending.pop()
            if cell in self.revealed or cell in self.flags:
                continue
            self.revealed.add(cell)
            if self.adjacent_mines(*cell) == 0:
                pending.extend(neighbours(self.rows, self.cols, cell))

        if len(self.revealed) == self.rows * self.cols - len(self.mines):
            self.flags = set(self.mines)
            self._finish(WON, now)

    def _finish(self, status: str, now: float) -> None:
        self.status = status
        self.finished_at = now

    def _symbol(self, cell: Cell) -> str:
        if cell in self.revealed:
            return str(self.adjacent_mines(*cell))
        is_mine = self.mines is not None and cell in self.mines
        if self.status == LOST:
            if cell == self.exploded:
                return "X"
            if cell in self.flags:
                return "F" if is_mine else "W"
            return "M" if is_mine else "H"
        return "F" if cell in self.flags else "H"


def _check_custom(rows: Optional[int], cols: Optional[int], mines: Optional[int]) -> None:
    if rows is None or cols is None or mines is None:
        raise InvalidConfiguration("A custom board needs rows, columns and mines.")
    if not MIN_SIDE <= rows <= MAX_ROWS:
        raise InvalidConfiguration(f"Rows must be between {MIN_SIDE} and {MAX_ROWS}.")
    if not MIN_SIDE <= cols <= MAX_COLS:
        raise InvalidConfiguration(f"Columns must be between {MIN_SIDE} and {MAX_COLS}.")
    if not 1 <= mines <= max_mines(rows, cols):
        raise InvalidConfiguration(
            f"A board of {rows} rows and {cols} columns holds between 1 and "
            f"{max_mines(rows, cols)} mines."
        )
