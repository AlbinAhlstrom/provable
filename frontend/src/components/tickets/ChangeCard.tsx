import React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import { ChangeCardDTO } from '../../types/api';

// Building from a planned change is not part of the engine yet (ADR-014, order of work)
const NOT_BUILT_YET = 'Building a planned change is not available yet.';

type PlannedRule = ChangeCardDTO['rules'][number];

const CLAUSES: { key: 'given' | 'when' | 'then'; label: string }[] = [
  { key: 'given', label: 'Given' },
  { key: 'when', label: 'When' },
  { key: 'then', label: 'Then' },
];

/** A rule's Given, When and Then, each on a line of its own; a rule not written that way is shown as its sentence. */
const RuleClauses: React.FC<{ rule: PlannedRule }> = ({ rule }) => {
  if (!rule.when || !rule.then) return <span className="change-card-rule-plain">{rule.plain}</span>;
  return (
    <dl className="change-card-clauses">
      {CLAUSES.filter(c => rule[c.key]).map(c => (
        <div key={c.key} className="change-card-clause">
          <dt>{c.label}</dt>
          <dd>{rule[c.key]}</dd>
        </div>
      ))}
    </dl>
  );
};

/** A planned change before it is built: what was understood in one sentence, the rules it would add, each under
 *  the feature of the app it belongs to, and what else is checked. Every piece is short and on a line of its own. */
export const ChangeCard: React.FC<{ card: ChangeCardDTO; onDiscard: () => void }> = ({ card, onDiscard }) => (
  <article className="change-card" aria-label="Planned change">
    <header className="change-card-head">
      <h4 className="change-card-title">{card.title}</h4>
      <button className="tool-btn" onClick={onDiscard} title="Discard the planned change" aria-label="Discard the planned change">
        <CloseIcon fontSize="inherit" />
      </button>
    </header>
    <p className="change-card-understood">{card.understood}</p>
    <section className="change-card-section">
      <h5 className="change-card-label">{card.rules.length === 1 ? '1 new rule' : `${card.rules.length} new rules`}</h5>
      <ul className="change-card-rules">
        {card.rules.map(rule => (
          <li key={rule.title}>
            <span className="change-card-label">{rule.feature}</span>
            <span className="change-card-rule-title">{rule.title}</span>
            <RuleClauses rule={rule} />
          </li>
        ))}
      </ul>
    </section>
    {card.adds.length > 0 && (
      <details className="change-card-advanced">
        <summary>Advanced</summary>
        <ul>
          {card.adds.map(added => <li key={`${added.kind}-${added.name}`}>{added.kind}: <code>{added.name}</code></li>)}
        </ul>
      </details>
    )}
    <footer className="change-card-foot">
      <span className="change-card-checked">
        {card.stays_green === 1 ? 'Your 1 other rule will be checked too.' : `Your ${card.stays_green} other rules will be checked too.`}
      </span>
      <span className="change-card-blocked" role="note">{card.problem || NOT_BUILT_YET}</span>
      <button className="tool-btn tool-btn-primary" disabled>Build</button>
    </footer>
  </article>
);

export default ChangeCard;
