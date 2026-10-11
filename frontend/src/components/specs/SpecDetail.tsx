import React from 'react';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import BuildOutlinedIcon from '@mui/icons-material/BuildOutlined';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ReplayIcon from '@mui/icons-material/Replay';
import { RuleCardDTO } from '../../types/api';
import { SpecStatusLight, testStatusLabel } from './SpecStatusLight';

export interface SpecDetailProps {
  card: RuleCardDTO | null;
  running: boolean;
  testing?: boolean;  // a running build is working on this spec
  onEdit: (card: RuleCardDTO) => void;
  onDelete: (card: RuleCardDTO) => void;
  onRunTest: (card: RuleCardDTO) => void;
  onRewriteTest: (card: RuleCardDTO) => void;  // the stored test is itself wrong: write a new one and run it
  onFix: (card: RuleCardDTO) => void;  // the test is right and the app is wrong: change the page until the test passes
}

const CLAUSES: { key: 'given_clause' | 'when_clause' | 'then_clause' | 'unless_clause'; label: string }[] = [
  { key: 'given_clause', label: 'Given' },
  { key: 'when_clause', label: 'When' },
  { key: 'then_clause', label: 'Then' },
  { key: 'unless_clause', label: 'Unless' },
];

/** One specification: its test light, why the last run did not pass, its behaviour, its test, and the actions on it. */
export const SpecDetail = React.forwardRef<HTMLDivElement, SpecDetailProps>(({ card, running, testing = false, onEdit, onDelete, onRunTest, onRewriteTest, onFix }, ref) => {
  if (!card) {
    return <div className="spec-detail" ref={ref}><p className="spec-empty">Select a specification.</p></div>;
  }
  const clauses = CLAUSES.filter(c => card[c.key]);
  const didNotPass = card.test_status === 'fail' || card.test_status === 'broken';

  return (
    <div className="spec-detail" ref={ref}>
      <div className="spec-detail-header">
        <div className="spec-detail-heading">
          <h4 className="spec-detail-title">
            <SpecStatusLight status={card.test_status} large testing={testing} />
            <span>{card.title}</span>
          </h4>
          {didNotPass && (
            <p className={`spec-reason spec-reason-${card.test_status}`}>
              {testStatusLabel(card.test_status)}{card.test_reason ? `: ${card.test_reason}` : ''}
            </p>
          )}
        </div>
        <div className="spec-detail-actions">
          <button className="tool-btn" onClick={() => onEdit(card)}>
            <EditOutlinedIcon fontSize="inherit" /> Edit
          </button>
          <button className="tool-btn tool-btn-danger" onClick={() => onDelete(card)}>
            <DeleteOutlineIcon fontSize="inherit" /> Delete
          </button>
        </div>
      </div>

      <span className="spec-section-label">Behaviour</span>
      {clauses.length > 0 ? (
        <dl className="spec-clauses">
          {clauses.map(c => (
            <div key={c.key} className="spec-clause">
              <dt>{c.label}</dt>
              <dd>{card[c.key]}</dd>
            </div>
          ))}
        </dl>
      ) : card.description ? (
        <p className="spec-clauses">{card.description}</p>
      ) : (
        <p className="spec-empty">No behaviour written yet. Use Edit to add it.</p>
      )}

      {card.page_test?.source && (
        <details className="spec-test">
          <summary className="spec-section-label">Page test</summary>
          {didNotPass && card.page_test.evidence && <pre className="spec-test-evidence">{card.page_test.evidence}</pre>}
          <pre className="spec-test-source">{card.page_test.source}</pre>
        </details>
      )}

      <div className="spec-detail-footer">
        {card.page_test?.source && (
          <button className="tool-btn" onClick={() => onRewriteTest(card)} disabled={running} title="Write a new page test for this specification and run it">
            <ReplayIcon fontSize="inherit" /> Write test again
          </button>
        )}
        {card.test_status === 'fail' && (
          <button className="tool-btn" onClick={() => onFix(card)} disabled={running} title="Change the page until this test passes; the change is kept only if every passing specification still passes">
            <BuildOutlinedIcon fontSize="inherit" /> Fix
          </button>
        )}
        <button className="tool-btn tool-btn-primary" onClick={() => onRunTest(card)} disabled={running}>
          {running ? <span className="spinner" /> : <PlayArrowIcon fontSize="inherit" />}
          {running ? 'Running…' : 'Run Test'}
        </button>
      </div>
    </div>
  );
});
SpecDetail.displayName = 'SpecDetail';
