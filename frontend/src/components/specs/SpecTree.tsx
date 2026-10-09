import React, { useState } from 'react';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { RuleCardDTO } from '../../types/api';
import { SpecStatusLight } from './SpecStatusLight';

export interface SpecTreeProps {
  chapters: [string, RuleCardDTO[]][];
  selectedId: string | null;
  onSelect: (card: RuleCardDTO) => void;
}

/** The specifications grouped by chapter; each row carries the light of its last test run. */
export const SpecTree: React.FC<SpecTreeProps> = ({ chapters, selectedId, onSelect }) => {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  if (chapters.length === 0) {
    return <div className="spec-tree"><p className="spec-empty">No specifications yet.</p></div>;
  }

  return (
    <div className="spec-tree">
      {chapters.map(([chapter, cards]) => (
        <div key={chapter} className="spec-chapter">
          <button
            className="spec-chapter-header"
            onClick={() => setCollapsed(prev => ({ ...prev, [chapter]: !prev[chapter] }))}
            aria-expanded={!collapsed[chapter]}
          >
            {collapsed[chapter] ? <ChevronRightIcon fontSize="inherit" /> : <ExpandMoreIcon fontSize="inherit" />}
            <span className="spec-chapter-name">{chapter}</span>
            <span className="spec-chapter-count">{cards.length}</span>
          </button>
          {!collapsed[chapter] && cards.map(card => (
            <button
              key={card.id}
              className={`spec-row${card.id === selectedId ? ' selected' : ''}`}
              onClick={() => onSelect(card)}
            >
              <SpecStatusLight status={card.test_status} />
              <span className="spec-row-title">{card.title}</span>
            </button>
          ))}
        </div>
      ))}
    </div>
  );
};
