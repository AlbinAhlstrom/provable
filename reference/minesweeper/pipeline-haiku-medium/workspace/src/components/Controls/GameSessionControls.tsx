import type { DifficultyState } from '../../api/difficultyClient';
import type { GameSessionState } from '../../api/game_sessionClient';

interface Props {
  difficulties: DifficultyState[];
  session: GameSessionState;
  busy: boolean;
  onAction: (actionType: string, params: Record<string, unknown>) => void;
}

const SEGMENT = 'rounded-sm border-2 border-t-white border-l-white border-b-[#808080] border-r-[#808080] px-2 py-1 text-sm font-semibold text-[#111111] disabled:opacity-60';

export function GameSessionControls({ difficulties, session, busy, onAction }: Props) {
  if (difficulties.length === 0) {
    return <p className="text-center text-sm">No difficulty levels are available yet.</p>;
  }
  return (
    <div role="radiogroup" aria-label="Difficulty" className="grid w-full grid-cols-1 gap-1 sm:grid-cols-3">
      {difficulties.map((d, i) => {
        const active = d.id === session.difficulty_id;
        return (
          <button
            key={d.id ?? i}
            type="button"
            role="radio"
            aria-checked={active}
            disabled={busy}
            onClick={() =>
              onAction('start_new_game', {
                difficulty_id: d.id,
                rows: d.rows,
                columns: d.columns,
                mine_count: d.mine_count,
              })
            }
            className={`${SEGMENT} ${active ? 'bg-[#d6d6d6]' : 'bg-[#bdbdbd]'}`}
          >
            {`${d.name ?? ''} · ${d.columns ?? 0} × ${d.rows ?? 0} · ${d.mine_count ?? 0} mines`}
          </button>
        );
      })}
    </div>
  );
}
