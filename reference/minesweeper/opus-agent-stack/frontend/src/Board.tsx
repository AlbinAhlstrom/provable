import { memo, useCallback, useEffect, useRef, useState } from 'react';
import type { CSSProperties, KeyboardEvent, MouseEvent, PointerEvent } from 'react';
import type { Action, CellSymbol, Game } from './api';
import { FlagIcon, MineIcon, WrongFlagIcon } from './icons';

const LONG_PRESS_MS = 420;

interface Props {
  game: Game;
  flagMode: boolean;
  onAction: (action: Action, row: number, col: number) => void;
}

/**
 * Renders the board the server sent and turns gestures into one of the three actions.
 * It decides nothing about the outcome: which cells open is the server's answer.
 */
export function Board({ game, flagMode, onAction }: Props) {
  const live = game.status === 'ready' || game.status === 'playing';
  const [focus, setFocus] = useState<[number, number]>([0, 0]);
  const gridRef = useRef<HTMLDivElement>(null);
  const pressTimer = useRef<number | null>(null);
  const pressStart = useRef<[number, number]>([0, 0]);
  const longPressAt = useRef(0);
  const swallowClick = useRef(false);

  useEffect(() => setFocus([0, 0]), [game.id]);

  const cellOf = (target: EventTarget): { row: number; col: number; symbol: CellSymbol } | null => {
    const el = (target as HTMLElement).closest<HTMLElement>('[data-row]');
    if (!el) return null;
    const row = Number(el.dataset.row);
    const col = Number(el.dataset.col);
    const symbol = game.board[row]?.[col] as CellSymbol | undefined;
    return symbol ? { row, col, symbol } : null;
  };

  const isNumber = (symbol: CellSymbol) => symbol >= '1' && symbol <= '8';

  const flagGesture = (row: number, col: number, symbol: CellSymbol) => {
    if (symbol === 'H' || symbol === 'F') onAction('flag', row, col);
  };

  const mainGesture = (row: number, col: number, symbol: CellSymbol) => {
    if (isNumber(symbol)) onAction('chord', row, col);
    else if (flagMode) flagGesture(row, col, symbol);
    else if (symbol === 'H') onAction('reveal', row, col);
  };

  const onClick = (event: MouseEvent) => {
    if (swallowClick.current) {
      swallowClick.current = false;
      return;
    }
    const cell = live ? cellOf(event.target) : null;
    if (!cell) return;
    setFocus([cell.row, cell.col]);
    mainGesture(cell.row, cell.col, cell.symbol);
  };

  const onContextMenu = (event: MouseEvent) => {
    event.preventDefault();
    // a touch long-press already flagged this cell; some browsers then also fire contextmenu
    if (Date.now() - longPressAt.current < 900) return;
    const cell = live ? cellOf(event.target) : null;
    if (!cell) return;
    setFocus([cell.row, cell.col]);
    flagGesture(cell.row, cell.col, cell.symbol);
  };

  const cancelPress = () => {
    if (pressTimer.current !== null) {
      window.clearTimeout(pressTimer.current);
      pressTimer.current = null;
    }
  };

  const onPointerDown = (event: PointerEvent) => {
    swallowClick.current = false;
    if (event.pointerType === 'mouse' || !live) return;
    const cell = cellOf(event.target);
    if (!cell || isNumber(cell.symbol)) return;
    pressStart.current = [event.clientX, event.clientY];
    cancelPress();
    pressTimer.current = window.setTimeout(() => {
      pressTimer.current = null;
      longPressAt.current = Date.now();
      swallowClick.current = true;
      navigator.vibrate?.(12);
      flagGesture(cell.row, cell.col, cell.symbol);
    }, LONG_PRESS_MS);
  };

  const onPointerMove = (event: PointerEvent) => {
    if (pressTimer.current === null) return;
    const [x, y] = pressStart.current;
    if (Math.hypot(event.clientX - x, event.clientY - y) > 10) cancelPress();
  };

  useEffect(() => cancelPress, []);

  const focusCell = useCallback((row: number, col: number) => {
    setFocus([row, col]);
    gridRef.current
      ?.querySelector<HTMLElement>(`[data-row="${row}"][data-col="${col}"]`)
      ?.focus();
  }, []);

  const onKeyDown = (event: KeyboardEvent) => {
    const cell = cellOf(event.target);
    if (!cell) return;
    const moves: Record<string, [number, number]> = {
      ArrowUp: [-1, 0],
      ArrowDown: [1, 0],
      ArrowLeft: [0, -1],
      ArrowRight: [0, 1],
    };
    const move = moves[event.key];
    if (move) {
      event.preventDefault();
      const row = Math.min(game.rows - 1, Math.max(0, cell.row + move[0]));
      const col = Math.min(game.cols - 1, Math.max(0, cell.col + move[1]));
      focusCell(row, col);
    } else if ((event.key === 'f' || event.key === 'F') && live) {
      event.preventDefault();
      flagGesture(cell.row, cell.col, cell.symbol);
    }
  };

  const style = { '--cols': game.cols } as CSSProperties;

  return (
    <div
      ref={gridRef}
      role="grid"
      aria-label={`Minefield, ${game.rows} rows by ${game.cols} columns`}
      className="board"
      data-live={live}
      style={style}
      onClick={onClick}
      onContextMenu={onContextMenu}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={cancelPress}
      onPointerCancel={cancelPress}
      onPointerLeave={cancelPress}
      onKeyDown={onKeyDown}
    >
      {game.board.map((line, row) => (
        <div role="row" className="contents" key={row}>
          {Array.from(line).map((symbol, col) => (
            <Cell
              key={col}
              row={row}
              col={col}
              symbol={symbol as CellSymbol}
              tabbable={focus[0] === row && focus[1] === col}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

const DESCRIPTION: Record<string, string> = {
  H: 'hidden',
  F: 'flagged',
  M: 'mine',
  X: 'the mine you hit',
  W: 'wrong flag, no mine here',
  '0': 'empty',
};

interface CellProps {
  row: number;
  col: number;
  symbol: CellSymbol;
  tabbable: boolean;
}

const Cell = memo(function Cell({ row, col, symbol, tabbable }: CellProps) {
  const revealed = symbol >= '0' && symbol <= '8';
  const kind =
    symbol === 'X'
      ? 'cell-boom'
      : revealed || symbol === 'M'
        ? `cell-open${symbol >= '1' && symbol <= '8' ? ' cell-number' : ''}`
        : 'cell-hidden';
  const label = `Row ${row + 1}, column ${col + 1}: ${
    DESCRIPTION[symbol] ?? `${symbol} mine${symbol === '1' ? '' : 's'} nearby`
  }`;

  let content: JSX.Element | string | null = null;
  if (symbol === 'F') content = <FlagIcon />;
  else if (symbol === 'M' || symbol === 'X') content = <MineIcon />;
  else if (symbol === 'W') content = <WrongFlagIcon />;
  else if (symbol >= '1' && symbol <= '8') content = symbol;

  return (
    <button
      type="button"
      role="gridcell"
      data-row={row}
      data-col={col}
      data-symbol={symbol}
      tabIndex={tabbable ? 0 : -1}
      aria-label={label}
      className={`cell ${kind}`}
      style={
        symbol >= '1' && symbol <= '8'
          ? { color: `var(--n${symbol})` }
          : symbol === 'M'
            ? { color: 'var(--mine)' }
            : undefined
      }
    >
      {content}
    </button>
  );
});
