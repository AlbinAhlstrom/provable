import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import type { Difficulties, Difficulty, Game, GameSummary, NewGame, Stats } from './api';
import { DIFFICULTY_LABEL, formatAgo, formatDuration, formatPercent } from './format';

const ORDER: Difficulty[] = ['beginner', 'intermediate', 'expert', 'custom'];

// ---- difficulty picker ------------------------------------------------------

interface PickerProps {
  config: Difficulties;
  current: Difficulty | null;
  customOpen: boolean;
  onPick: (difficulty: Exclude<Difficulty, 'custom'>) => void;
  onToggleCustom: () => void;
}

export function DifficultyPicker({ config, current, customOpen, onPick, onToggleCustom }: PickerProps) {
  const selected = customOpen ? 'custom' : current;
  const base =
    'rounded-lg px-3 py-2 text-left transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent';
  const on = 'bg-accent text-accent-ink shadow-sm';
  const off = 'text-ink hover:bg-well';
  return (
    <div
      role="radiogroup"
      aria-label="Difficulty"
      className="grid grid-cols-2 gap-1 rounded-xl border border-line bg-panel p-1 sm:grid-cols-4"
    >
      {config.presets.map((preset) => (
        <button
          key={preset.key}
          type="button"
          role="radio"
          aria-checked={selected === preset.key}
          className={`${base} ${selected === preset.key ? on : off}`}
          onClick={() => onPick(preset.key)}
        >
          <span className="block text-sm font-semibold">{DIFFICULTY_LABEL[preset.key]}</span>
          <span className="block text-xs opacity-75">
            {preset.cols} x {preset.rows} · {preset.mines} mines
          </span>
        </button>
      ))}
      <button
        type="button"
        role="radio"
        aria-checked={selected === 'custom'}
        aria-expanded={customOpen}
        className={`${base} ${selected === 'custom' ? on : off}`}
        onClick={onToggleCustom}
      >
        <span className="block text-sm font-semibold">Custom</span>
        <span className="block text-xs opacity-75">Your own board</span>
      </button>
    </div>
  );
}

// ---- custom board form ------------------------------------------------------

interface CustomFormProps {
  limits: Difficulties['custom'];
  initial: { rows: number; cols: number; mines: number };
  onStart: (config: NewGame) => void;
}

export function CustomForm({ limits, initial, onStart }: CustomFormProps) {
  const [rows, setRows] = useState(String(initial.rows));
  const [cols, setCols] = useState(String(initial.cols));
  const [mines, setMines] = useState(String(initial.mines));

  // Only a hint for the input; the server decides what is valid.
  const cells = Number(rows) * Number(cols);
  const mostMines = Number.isFinite(cells) && cells > limits.first_area ? cells - limits.first_area : null;

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onStart({ difficulty: 'custom', rows: Number(rows), cols: Number(cols), mines: Number(mines) });
  };

  const field =
    'mt-1 w-full rounded-lg border border-line bg-well px-3 py-2 text-sm text-ink focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent';

  return (
    <form
      onSubmit={submit}
      className="mt-2 grid grid-cols-3 items-end gap-3 rounded-xl border border-line bg-panel p-3 sm:grid-cols-[1fr_1fr_1fr_auto]"
    >
      <label className="text-xs font-medium text-muted">
        Columns ({limits.min_side}-{limits.max_cols})
        <input
          className={field}
          type="number"
          inputMode="numeric"
          required
          min={limits.min_side}
          max={limits.max_cols}
          value={cols}
          onChange={(e) => setCols(e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-muted">
        Rows ({limits.min_side}-{limits.max_rows})
        <input
          className={field}
          type="number"
          inputMode="numeric"
          required
          min={limits.min_side}
          max={limits.max_rows}
          value={rows}
          onChange={(e) => setRows(e.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-muted">
        Mines {mostMines ? `(1-${mostMines})` : ''}
        <input
          className={field}
          type="number"
          inputMode="numeric"
          required
          min={1}
          value={mines}
          onChange={(e) => setMines(e.target.value)}
        />
      </label>
      <button
        type="submit"
        className="col-span-3 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-ink hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent sm:col-span-1"
      >
        Start custom game
      </button>
    </form>
  );
}

// ---- statistics -------------------------------------------------------------

export function StatsPanel({ stats, highlight }: { stats: Stats | null; highlight: Difficulty | null }) {
  return (
    <section className="rounded-2xl border border-line bg-panel p-4" aria-labelledby="stats-title">
      <h2 id="stats-title" className="text-sm font-semibold text-ink">
        Best times
      </h2>
      {!stats ? (
        <p className="mt-3 text-sm text-muted">Loading...</p>
      ) : (
        <table className="mt-2 w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted">
              <th className="py-1 font-medium">Difficulty</th>
              <th className="py-1 text-right font-medium">Best</th>
              <th className="py-1 text-right font-medium">Won</th>
              <th className="py-1 text-right font-medium">Win rate</th>
            </tr>
          </thead>
          <tbody>
            {ORDER.map((key) => {
              const row = stats[key];
              return (
                <tr key={key} className="border-t border-line" data-stat={key}>
                  <td className={`py-2 ${highlight === key ? 'font-semibold text-accent' : 'text-ink'}`}>
                    {DIFFICULTY_LABEL[key]}
                  </td>
                  <td className="py-2 text-right font-mono tabular-nums text-ink">
                    {row.best_seconds === null ? <span className="text-muted">-</span> : formatDuration(row.best_seconds)}
                  </td>
                  <td className="py-2 text-right tabular-nums text-ink">
                    {row.won}
                    <span className="text-muted"> / {row.played}</span>
                  </td>
                  <td className="py-2 text-right tabular-nums text-ink">
                    {row.played ? formatPercent(row.win_rate) : <span className="text-muted">-</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}

// ---- recent games -----------------------------------------------------------

interface RecentProps {
  games: GameSummary[];
  current: Game | null;
  onResume: (id: string) => void;
}

export function RecentGames({ games, current, onResume }: RecentProps) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(timer);
  }, []);
  useEffect(() => setNow(Date.now()), [games]);

  const started = games.filter((g) => g.status !== 'ready').slice(0, 8);

  return (
    <section className="rounded-2xl border border-line bg-panel p-4" aria-labelledby="recent-title">
      <h2 id="recent-title" className="text-sm font-semibold text-ink">
        Recent games
      </h2>
      {started.length === 0 ? (
        <p className="mt-3 text-sm text-muted">No games played yet. Your results will show up here.</p>
      ) : (
        <ul className="mt-2">
          {started.map((g) => {
            const outcome =
              g.status === 'won'
                ? { text: `Won in ${formatDuration(g.elapsed_seconds)}`, tone: 'text-good', dot: 'bg-good' }
                : g.status === 'lost'
                  ? { text: `Lost after ${formatDuration(g.elapsed_seconds)}`, tone: 'text-bad', dot: 'bg-bad' }
                  : { text: 'In progress', tone: 'text-muted', dot: 'bg-accent' };
            const resumable = g.status === 'playing' && g.id !== current?.id;
            return (
              <li key={g.id} className="flex items-center gap-3 border-t border-line py-2 text-sm" data-recent={g.status}>
                <span className={`h-2 w-2 shrink-0 rounded-full ${outcome.dot}`} aria-hidden="true" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-ink">
                    {DIFFICULTY_LABEL[g.difficulty]}
                    <span className="text-muted">
                      {' '}
                      · {g.cols} x {g.rows}, {g.mine_count} mines
                    </span>
                  </span>
                  <span className={`block text-xs ${outcome.tone}`}>
                    {outcome.text}
                    {g.id === current?.id && g.status === 'playing' ? ' (this game)' : ''}
                  </span>
                </span>
                {resumable ? (
                  <button
                    type="button"
                    className="rounded-md border border-line px-2 py-1 text-xs font-medium text-ink hover:bg-well"
                    onClick={() => onResume(g.id)}
                  >
                    Resume
                  </button>
                ) : (
                  <span className="shrink-0 text-xs text-muted">{formatAgo(g.created_at, now)}</span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
