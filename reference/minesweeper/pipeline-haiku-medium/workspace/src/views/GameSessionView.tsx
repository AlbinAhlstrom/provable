import { useRef, type MouseEvent, type PointerEvent, type ReactNode } from 'react';
import type { GameSessionState } from '../api/game_sessionClient';

type Cell = NonNullable<GameSessionState['cells']>[number];

const NUMBER_COLOURS = ['', '#0000ff', '#008000', '#ff0000', '#000080', '#800000', '#008080', '#111111', '#808080'];
const RAISED = 'bg-[#bdbdbd] border-2 border-t-white border-l-white border-b-[#808080] border-r-[#808080]';
const FLAT = 'bg-[#d6d6d6] border border-[#9e9e9e]';

interface Props {
  session: GameSessionState;
  busy: boolean;
  error: string | null;
  onReveal: (row: number, column: number) => void;
  onFlag: (row: number, column: number) => void;
  onFace: () => void;
  children?: ReactNode;
}

function statusText(s: GameSessionState): string {
  switch (s.status) {
    case 'in_progress':
      return 'Right-click or long-press to flag a suspected mine.';
    case 'won':
      return `Cleared in ${s.elapsed_seconds ?? 0} seconds. Press the face to play again.`;
    case 'lost':
      return 'You hit a mine. Press the face to try again.';
    default:
      return 'Click any cell to start. Your first click is always safe.';
  }
}

function Face({ status }: { status: string }) {
  const lost = status === 'lost';
  const won = status === 'won';
  return (
    <svg viewBox="0 0 24 24" className="h-7 w-7" aria-hidden="true">
      <circle cx="12" cy="12" r="11" fill="#facc15" stroke="#111111" strokeWidth="1" />
      {lost ? (
        <>
          <path d="M6 7l3 3M9 7l-3 3M15 7l3 3M18 7l-3 3" stroke="#111111" strokeWidth="1.4" />
          <path d="M7 17q5-5 10 0" fill="none" stroke="#111111" strokeWidth="1.6" />
        </>
      ) : won ? (
        <>
          <rect x="5" y="8" width="6" height="3.5" fill="#111111" />
          <rect x="13" y="8" width="6" height="3.5" fill="#111111" />
          <path d="M7 14q5 5 10 0" fill="none" stroke="#111111" strokeWidth="1.6" />
        </>
      ) : (
        <>
          <circle cx="9" cy="9" r="1.4" fill="#111111" />
          <circle cx="15" cy="9" r="1.4" fill="#111111" />
          <path d="M7 13q5 5 10 0" fill="none" stroke="#111111" strokeWidth="1.6" />
        </>
      )}
    </svg>
  );
}

function Lcd({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center gap-0.5">
      <span className="min-w-[3.5rem] rounded-sm bg-[#111111] px-1.5 py-0.5 text-right font-mono text-2xl font-bold leading-none tabular-nums text-[#ff2a2a]">
        {value}
      </span>
      <span className="text-xs leading-tight text-[#111111]">{label}</span>
    </div>
  );
}

interface CellProps {
  cell: Cell;
  lost: boolean;
  live: boolean;
  size: string;
  onReveal: (row: number, column: number) => void;
  onFlag: (row: number, column: number) => void;
}

function CellView({ cell, lost, live, size, onReveal, onFlag }: CellProps) {
  const timer = useRef<number | null>(null);
  const held = useRef(false);
  const cancel = () => {
    if (timer.current !== null) window.clearTimeout(timer.current);
    timer.current = null;
  };
  const onDown = (e: PointerEvent<HTMLButtonElement>) => {
    if (!live || e.pointerType === 'mouse') return;
    held.current = false;
    cancel();
    timer.current = window.setTimeout(() => {
      held.current = true;
      onFlag(cell.row, cell.column);
    }, 450);
  };
  const onClick = () => {
    if (held.current) {
      held.current = false;
      return;
    }
    if (live && cell.state === 'hidden') onReveal(cell.row, cell.column);
  };
  const onMenu = (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (live) onFlag(cell.row, cell.column);
  };

  const count = cell.adjacent_mine_count ?? 0;
  const revealed = cell.state === 'revealed';
  const tone = revealed ? (cell.has_mine ? 'bg-[#ff0000] border border-[#9e9e9e]' : FLAT) : RAISED;

  let face: ReactNode = null;
  if (cell.state === 'flagged') {
    face = lost && !cell.has_mine
      ? <span className="font-bold text-[#ff0000]">{'✖\uFE0E'}</span>
      : <span className="text-[#ff0000]">{'⚑\uFE0E'}</span>;
  } else if (lost && cell.has_mine) {
    face = <span className="block h-1/2 w-1/2 rounded-full bg-[#111111]" />;
  } else if (revealed && count > 0) {
    face = (
      <span className="font-bold" style={{ color: NUMBER_COLOURS[Math.min(count, 8)] }}>
        {count}
      </span>
    );
  }

  return (
    <button
      type="button"
      aria-label={`Row ${cell.row + 1}, column ${cell.column + 1}`}
      onClick={onClick}
      onContextMenu={onMenu}
      onPointerDown={onDown}
      onPointerUp={cancel}
      onPointerLeave={cancel}
      onPointerCancel={cancel}
      style={{ fontSize: `calc(${size} * 0.6)`, touchAction: 'manipulation' }}
      className={`flex h-full w-full select-none items-center justify-center leading-none ${tone}`}
    >
      {face}
    </button>
  );
}

export function GameSessionView({ session, busy, error, onReveal, onFlag, onFace, children }: Props) {
  const rows = session.rows ?? 1;
  const cols = session.columns ?? 1;
  const cellSize = `min(2rem, calc((100vw - 4rem) / ${cols}))`;
  const cells = session.cells ?? [];
  const ended = session.status === 'won' || session.status === 'lost' || session.status === 'abandoned';
  const lost = session.status === 'lost';
  const inProgress = session.status === 'in_progress';

  return (
    <div className="flex w-full max-w-full flex-col items-center gap-2">
      <section aria-label="Minesweeper" className={`${RAISED} flex w-max max-w-full flex-col gap-2 p-3`}>
        <div className="flex items-center justify-between gap-2">
          <Lcd label="Mines left" value={(session.mine_count ?? 0) - (session.flag_count ?? 0)} />
          <button
            type="button"
            onClick={onFace}
            disabled={busy}
            aria-label="New game"
            title={inProgress ? 'New game (ends this game with no result)' : 'New game'}
            className={`${RAISED} flex h-10 w-10 items-center justify-center rounded-sm p-0.5`}
          >
            <Face status={session.status ?? ''} />
          </button>
          <Lcd label="Time" value={session.elapsed_seconds ?? 0} />
        </div>
        <div className="self-center border-2 border-t-[#808080] border-l-[#808080] border-b-white border-r-white p-0.5">
          <div
            className="grid"
            style={{
              gridTemplateColumns: `repeat(${cols}, ${cellSize})`,
              gridTemplateRows: `repeat(${rows}, ${cellSize})`,
            }}
          >
            {cells.map((c) => (
              <div
                key={`${c.row}-${c.column}`}
                className="h-full w-full"
                style={{ gridRowStart: c.row + 1, gridColumnStart: c.column + 1 }}
              >
                <CellView
                  cell={c}
                  lost={lost}
                  live={!ended && c.state !== 'revealed'}
                  size={cellSize}
                  onReveal={onReveal}
                  onFlag={onFlag}
                />
              </div>
            ))}
          </div>
        </div>
        {children}
      </section>
      <p role="status" aria-live="polite" className="max-w-full break-words text-center text-sm min-h-[1.25rem]">
        {error ?? statusText(session)}
      </p>
    </div>
  );
}
