import type { DifficultySettingState } from '../../api/difficulty_settingClient';

type Props = {
  difficulty: string;
  settings: DifficultySettingState[];
  onChoose: (difficulty: string) => void;
};

export default function GameControls({ difficulty, settings, onChoose }: Props) {
  return (
    <div role="radiogroup" aria-label="Difficulty" className="grid grid-cols-1 gap-1 sm:grid-cols-3">
      {settings.map((s) => {
        const active = s.name === difficulty;
        return (
          <button
            key={s.id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChoose(s.name ?? '')}
            className={`rounded-sm border-2 px-2 py-1 font-sans text-sm text-stone-900 break-words ${
              active
                ? 'bg-[#d0d0d0] border-t-[#6b6b6b] border-l-[#6b6b6b] border-b-white border-r-white font-bold'
                : 'bg-[#bdbdbd] border-t-white border-l-white border-b-[#6b6b6b] border-r-[#6b6b6b]'
            }`}
          >
            {`${s.name ?? ''} (${s.columns ?? 0}×${s.rows ?? 0}, ${s.mine_count ?? 0} mines)`}
          </button>
        );
      })}
    </div>
  );
}
