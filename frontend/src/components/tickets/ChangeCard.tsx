import React from 'react';
import CloseIcon from '@mui/icons-material/Close';
import { ChangeCardDTO } from '../../types/api';

// Building from a planned change is not part of the engine yet (ADR-014, order of work)
const NOT_BUILT_YET = 'Building a planned change is not available yet.';

/** A planned change before it is built: what was understood, the rules it would add, and what else is checked. */
export const ChangeCard: React.FC<{ card: ChangeCardDTO; onDiscard: () => void }> = ({ card, onDiscard }) => (
  <article className="change-card" aria-label="Planned change">
    <header className="change-card-head">
      <h4 className="change-card-title">{card.title}</h4>
      <button className="tool-btn" onClick={onDiscard} title="Discard the planned change" aria-label="Discard the planned change">
        <CloseIcon fontSize="inherit" />
      </button>
    </header>
    <p className="change-card-understood">{card.understood}</p>
    <ul className="change-card-rules">
      {card.rules.map(rule => (
        <li key={rule.title}>
          <span className="change-card-rule-title">{rule.title}</span>
          <span className="change-card-rule-plain">{rule.plain}</span>
        </li>
      ))}
    </ul>
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
