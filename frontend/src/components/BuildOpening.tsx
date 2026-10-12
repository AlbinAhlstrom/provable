import React from 'react';
import { BuildProgress, StageProgress, StepMark } from './BuildProgressPanel';

interface OpeningStep {
  key: string;
  label: string;
  status: StageProgress['status'];
}

// The stages that have begun, a stage that names the parts of its work as one step per part
const openingSteps = (stages: StageProgress[]): OpeningStep[] =>
  stages.filter(stage => stage.status !== 'pending').flatMap(stage => {
    if (!stage.phases.length || stage.status === 'failed') return [{ key: stage.name, label: stage.label, status: stage.status }];
    return stage.phases.map((label, index): OpeningStep => ({
      key: `${stage.name}-${index}`,
      label,
      status: index < stage.phase ? 'ok' : index === stage.phase ? 'running' : 'pending',
    }));
  });

/** Shown in the live workspace in place of the app from the moment a build starts until it has a first draft to show: what was
 *  asked for, and the steps of the build's opening as they are worked through. */
export const BuildOpening: React.FC<{ pitch: string; progress: BuildProgress | null }> = ({ pitch, progress }) => {
  const steps = openingSteps(progress?.opening ?? []);
  return (
    <div className="build-opening" aria-live="polite">
      <h4 className="build-opening-title">Building your app</h4>
      <p className="build-opening-pitch">{pitch}</p>
      <ol className="build-opening-steps">
        {steps.length === 0 && (
          <li className="build-step build-step-running">
            <span className="build-step-mark"><StepMark status="running" /></span>
            <span>Starting</span>
          </li>
        )}
        {steps.map(step => (
          <li key={step.key} className={`build-step build-step-${step.status}`}>
            <span className="build-step-mark"><StepMark status={step.status} /></span>
            <span>{step.label}</span>
          </li>
        ))}
      </ol>
    </div>
  );
};
