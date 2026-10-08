import React from 'react';

export interface StageProgress {
  name: string;
  label: string;
  status: 'running' | 'ok' | 'failed' | 'skipped';
  error: string | null;
}

export interface BuildProgress {
  building: boolean;
  run_id: string;
  elapsed_s: number;
  page_ready: boolean;
  stages: StageProgress[];
  rules: { done: number; total: number; active: number } | null;
}

const STATUS_MARK: Record<StageProgress['status'], { mark: string; color: string }> = {
  running: { mark: '●', color: '#38bdf8' },
  ok: { mark: '✓', color: '#4ade80' },
  failed: { mark: '✕', color: '#f87171' },
  skipped: { mark: '–', color: '#64748b' },
};

const elapsed = (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

const rulesText = (rules: BuildProgress['rules']) =>
  rules ? `${rules.active} of ${rules.total} rules active${rules.done > rules.active ? `, ${rules.done - rules.active} not enforced` : ''}` : null;

/** Shown in place of the app until its page has been written: every stage of the running build and its status. */
export const BuildProgressScreen: React.FC<{ progress: BuildProgress | null }> = ({ progress }) => (
  <div style={{ maxWidth: '640px', margin: '3rem auto', padding: '0 1rem' }}>
    <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '1rem', padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '1.25rem' }}>
        <h2 style={{ margin: 0, fontSize: '1.35rem', color: '#f8fafc', fontWeight: 800 }}>Building your app</h2>
        {progress?.building && <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontVariantNumeric: 'tabular-nums' }}>{elapsed(progress.elapsed_s)}</span>}
      </div>
      <p style={{ margin: '0 0 1.25rem', color: '#94a3b8', fontSize: '0.9rem' }}>
        The app appears here as soon as its page is written. Rules and checks continue after that.
      </p>
      {!progress?.stages.length && <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Starting…</div>}
      <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {progress?.stages.map((stage, index) => (
          <li key={`${stage.name}-${index}`} style={{ display: 'flex', gap: '0.75rem', alignItems: 'baseline', fontSize: '0.92rem' }}>
            <span style={{ color: STATUS_MARK[stage.status].color, width: '1rem', textAlign: 'center', fontWeight: 700 }}>{STATUS_MARK[stage.status].mark}</span>
            <span style={{ color: stage.status === 'running' ? '#f8fafc' : '#cbd5e1', fontWeight: stage.status === 'running' ? 700 : 400 }}>
              {stage.label}
              {stage.name === 'behaviour_specs' && progress.rules && <span style={{ color: '#94a3b8', fontWeight: 400 }}> · {rulesText(progress.rules)}</span>}
              {stage.error && <span style={{ display: 'block', color: '#fca5a5', fontSize: '0.8rem', fontWeight: 400 }}>{stage.error}</span>}
            </span>
          </li>
        ))}
      </ul>
    </div>
  </div>
);

/** Shown above the app while the build continues behind it: what is still being worked on. */
export const BuildProgressStrip: React.FC<{ progress: BuildProgress }> = ({ progress }) => {
  const running = progress.stages.filter(s => s.status === 'running').map(s => s.label);
  const failed = progress.stages.filter(s => s.status === 'failed');
  const rules = rulesText(progress.rules);
  return (
    <div style={{ background: '#172554', border: '1px solid #1d4ed8', borderRadius: '0.6rem', padding: '0.55rem 0.9rem', marginBottom: '0.6rem', color: '#dbeafe', fontSize: '0.82rem', display: 'flex', flexWrap: 'wrap', gap: '0.4rem 1.25rem', alignItems: 'baseline' }}>
      <strong style={{ color: '#ffffff' }}>Still building · {elapsed(progress.elapsed_s)}</strong>
      {running.length > 0 && <span>{running.join(' · ')}</span>}
      {rules && <span>{rules}</span>}
      {failed.map(stage => <span key={stage.name} style={{ color: '#fca5a5' }}>{stage.label}: failed</span>)}
      <span style={{ color: '#93c5fd' }}>Records you add now are cleared each time a rule lands.</span>
    </div>
  );
};
