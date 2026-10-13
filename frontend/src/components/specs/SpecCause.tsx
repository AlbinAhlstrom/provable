import React from 'react';
import { RuleCauseDTO } from '../../types/api';

/** Where the fault of a red specification was found, in a person's words. */
export const CAUSE_LABELS: Record<RuleCauseDTO['fault'], string> = {
  page: 'The page is at fault',
  logic: 'What the app does is at fault',
  rules: 'These specifications disagree',
  test: 'The test is at fault',
};

/** What the named specifications are to this one: for a fault in what the app does, the ones a fix would break. */
const RULES_LABELS: Partial<Record<RuleCauseDTO['fault'], string>> = {
  logic: 'A fix would break',
};

/** What a fix found out about a specification it could not turn green: where the fault lies, why in one sentence,
 *  and the specifications that cannot hold together with it, each on a line of its own. */
export const SpecCause: React.FC<{ cause: RuleCauseDTO }> = ({ cause }) => (
  <div className="spec-cause">
    <span className="spec-section-label">Cause</span>
    <p className="spec-cause-where">{CAUSE_LABELS[cause.fault] || cause.fault}</p>
    {cause.rules.length > 0 && (
      <>
        {RULES_LABELS[cause.fault] && <span className="spec-section-label">{RULES_LABELS[cause.fault]}</span>}
        <ul className="spec-cause-rules">
          {cause.rules.map(title => <li key={title}>{title}</li>)}
        </ul>
      </>
    )}
    {cause.why && <p className="spec-cause-why">{cause.why}</p>}
  </div>
);

export default SpecCause;
