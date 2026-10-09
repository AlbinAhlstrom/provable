import React, { useState } from 'react';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RemoveIcon from '@mui/icons-material/Remove';
import { STACKED_LAYOUT } from './RequirementControlPanel';

export interface StageProgress {
  name: string;
  label: string;
  status: 'pending' | 'running' | 'ok' | 'failed' | 'skipped';
  error: string | null;
  weight: number;    // the stage's usual share of a build, 0..1
  fraction: number;  // how far the stage has come, 0..1
}

export interface BuildProgress {
  building: boolean;
  run_id: string;
  elapsed_s: number;
  draft_ready: boolean;
  page_ready: boolean;
  stages: StageProgress[];
  rules: { done: number; total: number; active: number; latest: string; waiting: string[] } | null;  // waiting: ids of the specs being worked on
  percent: number;
  ready: boolean;                // everything that builds the app has ended; only the final checks may still run
  final_checks: StageProgress[];
}

const elapsed = (seconds: number) => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;

const rulesText = (rules: BuildProgress['rules']) =>
  rules ? `${rules.active} of ${rules.total} rules active${rules.done > rules.active ? `, ${rules.done - rules.active} not enforced` : ''}` : null;

const StepMark: React.FC<{ status: StageProgress['status'] }> = ({ status }) => {
  if (status === 'ok') return <CheckIcon fontSize="inherit" />;
  if (status === 'failed') return <CloseIcon fontSize="inherit" />;
  if (status === 'skipped') return <RemoveIcon fontSize="inherit" />;
  return <span className="build-step-dot" />;
};

/** Shown above the live workspace once the app is built and only its final checks are running. */
const FinalChecksBanner: React.FC<{ progress: BuildProgress }> = ({ progress }) => {
  const running = progress.final_checks.filter(s => s.status === 'running').map(s => s.label);
  const failed = [...progress.stages, ...progress.final_checks].filter(s => s.status === 'failed');
  return (
    <div className="build-progress build-progress-ready">
      <div className="build-progress-head">
        <strong className="build-progress-title"><CheckIcon fontSize="inherit" /> Your app is ready</strong>
        <span className="build-progress-now build-progress-checks">
          Final checks{running.length ? `: ${running.join(' · ')}` : ''}
          {failed.map(stage => <span key={stage.name} className="build-progress-failed"> · {stage.label}: failed</span>)}
        </span>
      </div>
    </div>
  );
};

/** Shown above the live workspace while a build runs: one bar for the whole build, cut into its stages, each as long
 *  as its usual share of a build, and the stages by name below it. */
export const BuildProgressBanner: React.FC<{ progress: BuildProgress | null }> = ({ progress }) => {
  const [showSteps, setShowSteps] = useState<boolean>(() => !window.matchMedia(STACKED_LAYOUT).matches);
  const stages = progress?.stages ?? [];
  const running = stages.filter(s => s.status === 'running').map(s => s.label);
  const failed = stages.filter(s => s.status === 'failed');
  const rules = rulesText(progress?.rules ?? null);
  const percent = Math.floor(progress?.percent ?? 0);

  if (progress?.ready) return <FinalChecksBanner progress={progress} />;

  return (
    <div className="build-progress">
      <div className="build-progress-head">
        <strong className="build-progress-title">Building your app</strong>
        <span className="build-progress-figures">{percent}%{progress ? ` · ${elapsed(progress.elapsed_s)}` : ''}</span>
        <span className="build-progress-now">
          {running.length ? running.join(' · ') : 'Starting'}
          {failed.map(stage => <span key={stage.name} className="build-progress-failed"> · {stage.label}: failed</span>)}
        </span>
        <button className="tool-btn" onClick={() => setShowSteps(open => !open)} aria-expanded={showSteps}>
          {showSteps ? <ExpandLessIcon fontSize="inherit" /> : <ExpandMoreIcon fontSize="inherit" />} Steps
        </button>
      </div>

      <div className="build-bar" role="progressbar" aria-label="Build progress" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent}>
        {stages.map(stage => (
          <div key={stage.name} className={`build-bar-step build-bar-step-${stage.status}`} style={{ flexGrow: stage.weight }} title={stage.label}>
            <div className="build-bar-fill" style={{ width: `${stage.fraction * 100}%` }} />
          </div>
        ))}
      </div>

      {showSteps && (
        <ol className="build-steps">
          {stages.map(stage => (
            <li key={stage.name} className={`build-step build-step-${stage.status}`}>
              <span className="build-step-mark"><StepMark status={stage.status} /></span>
              <span>
                {stage.label}
                {stage.name === 'behaviour_specs' && rules && <span className="build-step-note"> · {rules}</span>}
                {stage.error && <span className="build-step-error">{stage.error}</span>}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
};
