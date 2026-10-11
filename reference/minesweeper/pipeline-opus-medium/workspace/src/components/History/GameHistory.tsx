import { createBestTime, type BestTimeState } from '../../api/best_timeClient';
import type { DifficultyState } from '../../api/difficultyClient';
import type { GameState } from '../../api/gameClient';

const STANDARD = ['beginner', 'intermediate', 'expert'];
export const BTN = 'min-w-[4.5rem] px-3 py-0.5 bg-[#c0c0c0] border-2 border-t-white border-l-white border-b-gray-600 border-r-gray-600 active:border-t-gray-600 active:border-l-gray-600 active:border-b-white active:border-r-white';

export const fastest = (bests: BestTimeState[], id: string): number | null => {
  const times = bests.filter((b) => b.difficulty_id === id).map((b) => b.best_seconds);
  return times.length ? Math.min(...times) : null;
};

export async function recordBest(game: GameState, bests: BestTimeState[], seconds: number): Promise<{ list: BestTimeState[]; improved: boolean }> {
  if (!STANDARD.includes(game.difficulty_id)) return { list: bests, improved: false };
  const best = fastest(bests, game.difficulty_id);
  if (best !== null && seconds >= best) return { list: bests, improved: false };
  const created = await createBestTime({
    difficulty_id: game.difficulty_id, game_id: game.id, best_seconds: seconds, achieved_at: new Date().toISOString(),
  });
  return { list: [...bests, created], improved: true };
}

export function Dialog({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center p-4 bg-black/20">
      <div role="dialog" aria-label={title} className="max-w-full bg-[#c0c0c0] p-[3px] text-[13px] text-black border-2 border-t-white border-l-white border-b-gray-600 border-r-gray-600">
        <div className="bg-[#000080] text-white font-bold px-2 py-0.5">{title}</div>
        <div className="p-3">{children}</div>
      </div>
    </div>
  );
}

type HistoryProps = { difficulties: DifficultyState[]; bests: BestTimeState[]; onClose: () => void };

export function GameHistory({ difficulties, bests, onClose }: HistoryProps) {
  const rows = difficulties.filter((d) => d.is_standard);
  const none = rows.every((d) => fastest(bests, d.id) === null);
  return (
    <Dialog title="Best Times">
      <table className="w-full">
        <tbody>
          {rows.map((d) => {
            const t = fastest(bests, d.id);
            return (
              <tr key={d.id}>
                <td className="pr-6 py-0.5">{d.name}</td>
                <td className="text-right py-0.5">{t === null ? '—' : `${t} seconds`}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {none && <p className="mt-2 text-[12px] text-gray-700 break-words">No wins yet. Your fastest time appears here.</p>}
      <div className="flex justify-end pt-3">
        <button type="button" className={BTN} onClick={onClose}>Close</button>
      </div>
    </Dialog>
  );
}

export function NewBestDialog({ name, seconds, onClose }: { name?: string; seconds: number; onClose: () => void }) {
  return (
    <Dialog title="Best Times">
      <p className="break-words">{`New best time${name ? ` for ${name}` : ''}: ${seconds} seconds.`}</p>
      <div className="flex justify-end pt-3">
        <button type="button" className={BTN} onClick={onClose}>OK</button>
      </div>
    </Dialog>
  );
}

export default GameHistory;
