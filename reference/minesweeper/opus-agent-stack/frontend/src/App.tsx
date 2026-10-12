import { useCallback, useEffect, useRef, useState } from 'react';
import type { CSSProperties } from 'react';
import { api, ApiError } from './api';
import type { Action, Difficulties, Difficulty, Game, GameSummary, NewGame, Stats } from './api';
import { Board } from './Board';
import { ClockIcon, FlagIcon } from './icons';
import { CustomForm, DifficultyPicker, RecentGames, StatsPanel } from './Panels';
import { DIFFICULTY_LABEL, formatDuration } from './format';

const GAME_KEY = 'minesweeper.gameId';
const CONFIG_KEY = 'minesweeper.lastConfig';

function remember(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // private mode: the game still works, it just will not resume after a reload
  }
}

function recall(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function recalledConfig(): NewGame {
  try {
    const parsed = JSON.parse(recall(CONFIG_KEY) ?? 'null') as NewGame | null;
    if (parsed && typeof parsed.difficulty === 'string') return parsed;
  } catch {
    // fall through
  }
  return { difficulty: 'beginner' };
}

function configOf(game: Game): NewGame {
  return game.difficulty === 'custom'
    ? { difficulty: 'custom', rows: game.rows, cols: game.cols, mines: game.mine_count }
    : { difficulty: game.difficulty };
}

const isOver = (game: Game) => game.status === 'won' || game.status === 'lost';

export default function App() {
  const [config, setConfig] = useState<Difficulties | null>(null);
  const [game, setGame] = useState<Game | null>(null);
  const [syncedAt, setSyncedAt] = useState(0);
  const [stats, setStats] = useState<Stats | null>(null);
  const [recent, setRecent] = useState<GameSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [flagMode, setFlagMode] = useState(false);
  const [customOpen, setCustomOpen] = useState(false);

  const gameRef = useRef<Game | null>(null);
  const queue = useRef<Promise<void>>(Promise.resolve());
  const booted = useRef(false);

  const show = useCallback((next: Game) => {
    gameRef.current = next;
    setGame(next);
    setSyncedAt(performance.now());
    remember(GAME_KEY, next.id);
  }, []);

  const refreshRecords = useCallback(async () => {
    const [nextStats, nextRecent] = await Promise.all([api.stats(), api.listGames(50)]);
    setStats(nextStats);
    setRecent(nextRecent);
  }, []);

  /** Run server calls one after another, so quick clicks are applied in the order made. */
  const enqueue = useCallback((job: () => Promise<void>) => {
    queue.current = queue.current.then(job).catch((problem: unknown) => {
      setError(problem instanceof Error ? problem.message : 'Something went wrong.');
    });
  }, []);

  const startGame = useCallback(
    (wanted: NewGame) => {
      enqueue(async () => {
        const created = await api.createGame(wanted);
        show(created);
        remember(CONFIG_KEY, JSON.stringify(configOf(created)));
        setError(null);
        setFlagMode(false);
        if (created.difficulty !== 'custom') setCustomOpen(false);
      });
    },
    [enqueue, show],
  );

  // First load: the presets, then the game this browser was playing (or a fresh one).
  useEffect(() => {
    if (booted.current) return;
    booted.current = true;
    enqueue(async () => {
      setConfig(await api.difficulties());
      const storedId = recall(GAME_KEY);
      let resumed: Game | null = null;
      if (storedId) {
        try {
          resumed = await api.getGame(storedId);
        } catch (problem) {
          if (!(problem instanceof ApiError) || problem.status !== 404) throw problem;
        }
      }
      if (resumed) {
        show(resumed);
        setCustomOpen(resumed.difficulty === 'custom');
      } else {
        const created = await api.createGame(recalledConfig());
        show(created);
      }
      await refreshRecords();
    });
  }, [enqueue, show, refreshRecords]);

  const act = useCallback(
    (action: Action, row: number, col: number) => {
      const clickedIn = gameRef.current;
      if (!clickedIn) return;
      enqueue(async () => {
        const before = gameRef.current;
        if (!before || before.id !== clickedIn.id || isOver(before)) return;
        let next: Game;
        try {
          next = await api.act(before.id, action, row, col);
        } catch (problem) {
          if (problem instanceof ApiError && problem.status === 409) {
            // the server says the game is over: show what it knows
            show(await api.getGame(before.id));
            await refreshRecords();
            return;
          }
          if (problem instanceof ApiError && problem.status === 404) {
            const created = await api.createGame(configOf(before));
            show(created);
            setError('That game was no longer on the server, so a new one was started.');
            return;
          }
          throw problem;
        }
        if (gameRef.current?.id !== next.id) return;
        show(next);
        setError(null);
        if (before.status !== next.status) await refreshRecords();
      });
    },
    [enqueue, show, refreshRecords],
  );

  const newGame = () => {
    const current = gameRef.current;
    if (!current) return startGame(recalledConfig());
    const untouched = current.status === 'ready' && !current.board.some((line) => line.includes('F'));
    if (untouched) return; // already a fresh board
    startGame(configOf(current));
  };

  const pickPreset = (difficulty: Exclude<Difficulty, 'custom'>) => {
    const current = gameRef.current;
    setCustomOpen(false);
    if (current && current.difficulty === difficulty && current.status === 'ready') return;
    startGame({ difficulty });
  };

  const resume = (id: string) => {
    enqueue(async () => {
      const loaded = await api.getGame(id);
      show(loaded);
      setCustomOpen(loaded.difficulty === 'custom');
      setError(null);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  };

  const best = game && stats ? stats[game.difficulty].best_seconds : null;
  const isNewBest = !!game && game.status === 'won' && best !== null && best === game.elapsed_seconds;

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-4 px-3 py-6 sm:px-6 sm:py-10">
      <header className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-3xl">Minesweeper</h1>
          <p className="mt-1 text-sm text-muted">Clear the field without touching a mine. The first click is always safe.</p>
        </div>
      </header>

      {config && (
        <div>
          <DifficultyPicker
            config={config}
            current={game?.difficulty ?? null}
            customOpen={customOpen}
            onPick={pickPreset}
            onToggleCustom={() => setCustomOpen((open) => !open)}
          />
          {customOpen && (
            <CustomForm
              limits={config.custom}
              initial={
                game?.difficulty === 'custom'
                  ? { rows: game.rows, cols: game.cols, mines: game.mine_count }
                  : { rows: 12, cols: 20, mines: 36 }
              }
              onStart={startGame}
            />
          )}
        </div>
      )}

      {error && (
        <div
          role="alert"
          className="flex items-start justify-between gap-3 rounded-xl border border-bad bg-panel px-4 py-3 text-sm text-bad"
        >
          <span>{error}</span>
          <button type="button" className="shrink-0 font-medium underline" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {game ? (
        <GameCard
          game={game}
          syncedAt={syncedAt}
          flagMode={flagMode}
          isNewBest={isNewBest}
          onToggleFlagMode={() => setFlagMode((on) => !on)}
          onNewGame={newGame}
          onAction={act}
        />
      ) : (
        !error && <p className="py-16 text-center text-sm text-muted">Setting up the board...</p>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <StatsPanel stats={stats} highlight={game?.difficulty ?? null} />
        <RecentGames games={recent} current={game} onResume={resume} />
      </div>

      <footer className="pb-2 text-center text-xs text-muted">
        Every move is checked by the server. Mine positions never reach your browser until the game is over.
      </footer>
    </div>
  );
}

// ---- the game card ----------------------------------------------------------

interface GameCardProps {
  game: Game;
  syncedAt: number;
  flagMode: boolean;
  isNewBest: boolean;
  onToggleFlagMode: () => void;
  onNewGame: () => void;
  onAction: (action: Action, row: number, col: number) => void;
}

function GameCard({ game, syncedAt, flagMode, isNewBest, onToggleFlagMode, onNewGame, onAction }: GameCardProps) {
  const over = isOver(game);
  // Cells shrink to fit the page column (at most 64rem wide, minus page and card padding)
  // down to a touchable 22px; below that the board scrolls sideways.
  const sizing = {
    '--cell': `clamp(22px, calc((min(100vw, 64rem) - 6rem) / ${game.cols} - 2px), 34px)`,
  } as CSSProperties;

  return (
    <section
      className="mx-auto w-fit max-w-full rounded-2xl border border-line bg-panel p-3 shadow-sm sm:p-4"
      style={sizing}
      aria-label={`${DIFFICULTY_LABEL[game.difficulty]} game`}
      data-status={game.status}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <div
          className="flex min-w-[4.75rem] items-center gap-1.5 rounded-lg bg-well px-2.5 py-1.5 text-ink"
          title="Mines left to flag"
        >
          <FlagIcon className="h-4 w-4" />
          <span className="font-mono text-lg font-semibold tabular-nums" data-testid="mines-remaining" aria-label={`${game.mines_remaining} mines left`}>
            {game.mines_remaining}
          </span>
        </div>

        <button
          type="button"
          onClick={onNewGame}
          className={`rounded-lg px-3 py-1.5 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
            over ? 'bg-accent text-accent-ink hover:opacity-90' : 'border border-line text-ink hover:bg-well'
          }`}
        >
          {over ? 'Play again' : 'New game'}
        </button>

        <div
          className="flex min-w-[4.75rem] items-center justify-end gap-1.5 rounded-lg bg-well px-2.5 py-1.5 text-ink"
          title="Seconds since your first click"
        >
          <ClockIcon className="h-4 w-4 text-muted" />
          <Timer game={game} syncedAt={syncedAt} />
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg bg-well p-1.5">
        <div className="mx-auto w-fit">
          <Board game={game} flagMode={flagMode} onAction={onAction} />
        </div>
      </div>

      <div className="mt-3 flex min-h-[2.25rem] w-0 min-w-full flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <StatusLine game={game} isNewBest={isNewBest} />
        {!over && (
          <button
            type="button"
            role="switch"
            aria-checked={flagMode}
            onClick={onToggleFlagMode}
            className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
              flagMode ? 'border-accent bg-accent text-accent-ink' : 'border-line text-ink hover:bg-well'
            }`}
            title="When on, a click or tap places a flag instead of revealing"
          >
            <FlagIcon className="h-3.5 w-3.5" />
            Flag mode {flagMode ? 'on' : 'off'}
          </button>
        )}
      </div>
    </section>
  );
}

function StatusLine({ game, isNewBest }: { game: Game; isNewBest: boolean }) {
  if (game.status === 'won') {
    return (
      <p className="text-sm font-semibold text-good" role="status" data-testid="status-line">
        Cleared in {formatDuration(game.elapsed_seconds)}.{isNewBest ? ` New best for ${DIFFICULTY_LABEL[game.difficulty]}.` : ''}
      </p>
    );
  }
  if (game.status === 'lost') {
    return (
      <p className="text-sm font-semibold text-bad" role="status" data-testid="status-line">
        You hit a mine after {formatDuration(game.elapsed_seconds)}.
      </p>
    );
  }
  return (
    <p className="max-w-[34rem] text-xs text-muted" role="status" data-testid="status-line">
      {game.status === 'ready' ? 'Click any cell to start. ' : ''}
      Click reveals, right-click or long-press flags, and clicking a number opens its neighbours once its flags are placed.
    </p>
  );
}

/** Display only: counts on from the server's elapsed time between answers. */
function Timer({ game, syncedAt }: { game: Game; syncedAt: number }) {
  const [, tick] = useState(0);
  const running = game.status === 'playing';
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => tick((n) => n + 1), 250);
    return () => window.clearInterval(timer);
  }, [running]);

  const seconds = running
    ? game.elapsed_seconds + (performance.now() - syncedAt) / 1000
    : game.elapsed_seconds;
  const shown = Math.min(999, Math.floor(seconds));
  return (
    <span className="font-mono text-lg font-semibold tabular-nums" data-testid="timer" aria-label={`${shown} seconds`}>
      {String(shown).padStart(3, '0')}
    </span>
  );
}
