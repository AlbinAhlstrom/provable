import { useEffect, useRef, useState } from 'react';
import type { GameState } from '../api/gameClient';
import type { DifficultySettingState } from '../api/difficulty_settingClient';
import GameControls from '../components/Controls/GameControls';

type Props = {
  game: GameState;
  settings: DifficultySettingState[];
  error: string | null;
  onAction: (actionType: string, params?: Record<string, unknown>) => void;
};

const NUMBER_COLOUR: Record<number, string> = {
  1: 'text-blue-700',
  2: 'text-green-700',
  3: 'text-red-600',
  4: 'text-blue-950',
  5: 'text-red-900',
  6: 'text-teal-700',
  7: 'text-black',
  8: 'text-stone-500',
};

const MINE = '●\uFE0E';
const FLAG = '⚑\uFE0E';
const WRONG = '✖\uFE0E';

const counterText = (v: number) =>
  v < 0
    ? `-${String(Math.min(-v, 99)).padStart(2, '0')}`
    : String(Math.min(v, 999)).padStart(3, '0');

const faceFor = (status: string) =>
  status === 'won' ? '★\uFE0E' : status === 'lost' ? '☹\uFE0E' : '☺\uFE0E';

const Lcd = ({ label, value }: { label: string; value: string }) => (
  <div className="flex flex-col items-center">
    <span className="font-sans text-[10px] text-stone-900">{label}</span>
    <span className="rounded-sm bg-black px-1.5 font-mono text-2xl font-bold tabular-nums text-red-500">
      {value}
    </span>
  </div>
);

export default function GameView({ game, settings, error, onAction }: Props) {
  const [now, setNow] = useState(() => Date.now());
  const pressTimer = useRef<number | undefined>(undefined);
  const longPressed = useRef(false);

  useEffect(() => {
    if (game.status !== 'in_progress') return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [game.status]);

  const ended = game.status === 'won' || game.status === 'lost';
  const cells = game.cells ?? [];
  const byPos = new Map(cells.map((c) => [`${c.row}-${c.column}`, c]));
  const setting = settings.find((s) => s.name === game.difficulty);
  const rows = cells.length
    ? Math.max(...cells.map((c) => c.row)) + 1
    : setting?.rows ?? 0;
  const columns = cells.length
    ? Math.max(...cells.map((c) => c.column)) + 1
    : setting?.columns ?? 0;

  const started = game.started_at ? Date.parse(game.started_at) : NaN;
  const live =
    game.status === 'in_progress' && !Number.isNaN(started)
      ? Math.floor((now - started) / 1000)
      : game.elapsed_seconds ?? 0;
  const timer = Math.min(Math.max(live, 0), 999);

  const stateAt = (row: number, column: number): string =>
    byPos.get(`${row}-${column}`)?.state ?? 'hidden';

  const tap = (row: number, column: number) => {
    if (longPressed.current || ended || stateAt(row, column) !== 'hidden') return;
    onAction('reveal_cell', { row, column });
  };

  const flag = (row: number, column: number) => {
    if (ended || !['hidden', 'flagged'].includes(stateAt(row, column))) return;
    onAction('toggle_flag', { row, column });
  };

  const clearPress = () => window.clearTimeout(pressTimer.current);

  const renderTile = (row: number, column: number) => {
    const cell = byPos.get(`${row}-${column}`);
    const state = cell?.state ?? 'hidden';
    const revealed = state === 'revealed';
    let content: string | null = null;
    let colour = '';
    if (revealed && cell) {
      if (cell.has_mine) {
        content = MINE;
        colour = 'text-black';
      } else if (cell.adjacent_mine_count > 0) {
        content = String(cell.adjacent_mine_count);
        colour = NUMBER_COLOUR[cell.adjacent_mine_count] ?? '';
      }
    } else if (state === 'flagged') {
      content = FLAG;
      colour = 'text-red-700';
    } else if (state === 'wrong') {
      content = WRONG;
      colour = 'text-red-700';
    }
    const tileClass = revealed
      ? 'bg-[#d0d0d0] border border-[#9e9e9e]'
      : `bg-[#a8a8a8] border-2 border-t-white border-l-white border-b-[#6b6b6b] border-r-[#6b6b6b] ${
          ended ? '' : 'hover:bg-[#b8b8b8]'
        }`;
    return (
      <button
        key={`${row}-${column}`}
        type="button"
        aria-label={`Row ${row + 1}, column ${column + 1}, ${state}`}
        onClick={() => tap(row, column)}
        onContextMenu={(e) => {
          e.preventDefault();
          if (longPressed.current) {
            longPressed.current = false;
            return;
          }
          flag(row, column);
        }}
        onPointerDown={(e) => {
          if (e.button !== 0 && e.pointerType !== 'touch') return;
          longPressed.current = false;
          clearPress();
          pressTimer.current = window.setTimeout(() => {
            longPressed.current = true;
            flag(row, column);
          }, 500);
        }}
        onPointerUp={clearPress}
        onPointerLeave={clearPress}
        className={`flex h-7 w-7 shrink-0 select-none items-center justify-center font-mono text-sm font-bold ${
          ended ? 'cursor-default' : 'cursor-pointer'
        } ${tileClass} ${colour}`}
      >
        {content}
      </button>
    );
  };

  const resultText =
    game.status === 'won'
      ? `You cleared the field in ${timer} seconds.`
      : game.status === 'lost'
        ? 'You hit a mine. Press the face to try again.'
        : '';

  return (
    <section className="flex w-fit max-w-full flex-col gap-2">
      <div className="flex items-center justify-between gap-3 border-2 border-t-white border-l-white border-b-[#6b6b6b] border-r-[#6b6b6b] p-2">
        <Lcd label="Mines" value={counterText((game.mine_count ?? 0) - (game.flag_count ?? 0))} />
        <button
          type="button"
          aria-label="New game"
          onClick={() => onAction('start_game', { difficulty: game.difficulty })}
          className="flex h-10 w-10 items-center justify-center border-2 border-t-white border-l-white border-b-[#6b6b6b] border-r-[#6b6b6b] bg-[#bdbdbd] text-xl text-stone-900 hover:bg-[#c8c8c8]"
        >
          {faceFor(game.status)}
        </button>
        <Lcd label="Time" value={counterText(timer)} />
      </div>

      <GameControls
        difficulty={game.difficulty}
        settings={settings}
        onChoose={(d) => onAction('start_game', { difficulty: d })}
      />

      {game.status === 'ready' && (
        <div className="space-y-0.5">
          <p className="text-sm">Click any square to start. The first click is always safe.</p>
          <p className="text-xs">Right-click or long-press a square to flag a suspected mine.</p>
        </div>
      )}

      <div className="w-fit max-w-full overflow-x-auto border-2 border-t-[#6b6b6b] border-l-[#6b6b6b] border-b-white border-r-white p-1">
        <div
          className="w-max"
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${columns}, 1.75rem)`,
            gridTemplateRows: `repeat(${rows}, 1.75rem)`,
          }}
        >
          {Array.from({ length: rows * columns }, (_, i) =>
            renderTile(Math.floor(i / columns), i % columns),
          )}
        </div>
      </div>

      <p className="text-center text-sm font-bold break-words">{resultText}</p>
      {error && (
        <p role="alert" className="break-words text-sm text-red-700">
          {error}
        </p>
      )}
    </section>
  );
}
