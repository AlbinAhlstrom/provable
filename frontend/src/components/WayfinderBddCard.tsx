import React, { useState } from 'react';
import { WayfinderTicket, BddClause, BddPreset } from '../types/wayfinder';

export interface WayfinderBddCardProps {
  ticket: WayfinderTicket;
  onLockTicket: (ticketId: string, bdd: BddClause) => void;
  isLocking?: boolean;
}

export const WayfinderBddCard: React.FC<WayfinderBddCardProps> = ({
  ticket,
  onLockTicket,
  isLocking = false
}) => {
  const initialBdd: BddClause = ticket.resolved_bdd || ticket.bdd_template || {
    given: '',
    when: '',
    then: '',
    unless: ''
  };

  const [currentBdd, setCurrentBdd] = useState<BddClause>(initialBdd);
  const [selectedPresetId, setSelectedPresetId] = useState<string | null>(
    ticket.presets && ticket.presets.length > 0 ? ticket.presets[0].id : null
  );
  const [hasUnless, setHasUnless] = useState<boolean>(Boolean(initialBdd.unless));
  const [isCustomEditing, setIsCustomEditing] = useState<boolean>(false);

  const handleSelectPreset = (preset: BddPreset) => {
    setSelectedPresetId(preset.id);
    setCurrentBdd({ ...preset.bdd });
    setHasUnless(Boolean(preset.bdd.unless));
  };

  const handleToggleUnless = () => {
    if (hasUnless) {
      setHasUnless(false);
      setCurrentBdd(prev => ({ ...prev, unless: '' }));
    } else {
      setHasUnless(true);
      setCurrentBdd(prev => ({ ...prev, unless: 'Precondition or quota check fails' }));
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'GRILL': return '🎯';
      case 'PROTOTYPE': return '📱';
      case 'RESEARCH': return '🔬';
      default: return '⚡';
    }
  };

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case 'GRILL': return { bg: 'rgba(56, 189, 248, 0.15)', text: '#38bdf8', border: '#0284c7' };
      case 'PROTOTYPE': return { bg: 'rgba(192, 132, 252, 0.15)', text: '#c084fc', border: '#9333ea' };
      case 'RESEARCH': return { bg: 'rgba(251, 191, 36, 0.15)', text: '#fbbf24', border: '#d97706' };
      default: return { bg: 'rgba(52, 211, 153, 0.15)', text: '#34d399', border: '#059669' };
    }
  };

  const badgeColor = getTypeBadgeColor(ticket.ticket_type);

  return (
    <div
      style={{
        background: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '0.85rem',
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)',
        transition: 'border-color 0.2s ease, transform 0.2s ease'
      }}
    >
      {/* Ticket Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              style={{
                fontSize: '0.7rem',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                background: badgeColor.bg,
                color: badgeColor.text,
                border: `1px solid ${badgeColor.border}`,
                padding: '0.2rem 0.6rem',
                borderRadius: '9999px',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              <span>{getTypeIcon(ticket.ticket_type)}</span>
              <span>{ticket.ticket_type} DECISION</span>
            </span>
            <span
              style={{
                fontSize: '0.7rem',
                fontWeight: 600,
                background: 'rgba(148, 163, 184, 0.1)',
                color: '#94a3b8',
                padding: '0.2rem 0.5rem',
                borderRadius: '0.35rem'
              }}
            >
              Target: {ticket.target_aggregate}
            </span>
          </div>
        </div>

        <h4 style={{ margin: '0 0 0.4rem 0', color: '#f8fafc', fontSize: '1.1rem', fontWeight: 700 }}>
          {ticket.title}
        </h4>
        <p style={{ margin: 0, fontSize: '0.82rem', color: '#94a3b8', lineHeight: 1.4 }}>
          💡 {ticket.rationale}
        </p>
      </div>

      {/* Preset Selector Chips */}
      {ticket.presets && ticket.presets.length > 0 && (
        <div>
          <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>
            Opinionated Architectural Presets
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {ticket.presets.map(preset => {
              const isSelected = selectedPresetId === preset.id;
              return (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => handleSelectPreset(preset)}
                  disabled={isLocking}
                  style={{
                    background: isSelected ? '#0369a1' : '#1e293b',
                    border: `1px solid ${isSelected ? '#38bdf8' : '#334155'}`,
                    color: isSelected ? '#ffffff' : '#cbd5e1',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '0.5rem',
                    fontSize: '0.78rem',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: isLocking ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    transition: 'all 0.15s ease'
                  }}
                  title={preset.description}
                >
                  <span>{isSelected ? '✓' : '○'}</span>
                  <span>{preset.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* The Mad-Libs BDD Interactive Template */}
      <div
        style={{
          background: '#030712',
          border: '1px solid #1e293b',
          borderRadius: '0.65rem',
          padding: '0.85rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1f2937', paddingBottom: '0.4rem' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8', letterSpacing: '0.05em' }}>
            ⚡ BEHAVIOR SPECIFICATION (BDD MAD-LIBS)
          </span>
          <button
            type="button"
            onClick={() => setIsCustomEditing(prev => !prev)}
            style={{
              background: 'transparent',
              border: 'none',
              color: isCustomEditing ? '#38bdf8' : '#64748b',
              fontSize: '0.72rem',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            {isCustomEditing ? '✓ Done Editing' : '✏️ Fine-tune wording'}
          </button>
        </div>

        {/* GIVEN Clause */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem' }}>
          <span
            style={{
              background: 'rgba(56, 189, 248, 0.2)',
              color: '#38bdf8',
              border: '1px solid #0284c7',
              padding: '0.15rem 0.5rem',
              borderRadius: '0.35rem',
              fontSize: '0.72rem',
              fontWeight: 800,
              minWidth: '55px',
              textAlign: 'center'
            }}
          >
            GIVEN
          </span>
          {isCustomEditing ? (
            <input
              type="text"
              value={currentBdd.given}
              onChange={e => setCurrentBdd({ ...currentBdd, given: e.target.value })}
              style={{
                flex: 1,
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#ffffff',
                padding: '0.25rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem'
              }}
            />
          ) : (
            <span style={{ color: '#e2e8f0', fontSize: '0.82rem', lineHeight: 1.4 }}>
              {currentBdd.given}
            </span>
          )}
        </div>

        {/* WHEN Clause */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem' }}>
          <span
            style={{
              background: 'rgba(251, 191, 36, 0.2)',
              color: '#fbbf24',
              border: '1px solid #d97706',
              padding: '0.15rem 0.5rem',
              borderRadius: '0.35rem',
              fontSize: '0.72rem',
              fontWeight: 800,
              minWidth: '55px',
              textAlign: 'center'
            }}
          >
            WHEN
          </span>
          {isCustomEditing ? (
            <input
              type="text"
              value={currentBdd.when}
              onChange={e => setCurrentBdd({ ...currentBdd, when: e.target.value })}
              style={{
                flex: 1,
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#ffffff',
                padding: '0.25rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem'
              }}
            />
          ) : (
            <span style={{ color: '#e2e8f0', fontSize: '0.82rem', lineHeight: 1.4 }}>
              {currentBdd.when}
            </span>
          )}
        </div>

        {/* THEN Clause */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem' }}>
          <span
            style={{
              background: 'rgba(52, 211, 153, 0.2)',
              color: '#34d399',
              border: '1px solid #059669',
              padding: '0.15rem 0.5rem',
              borderRadius: '0.35rem',
              fontSize: '0.72rem',
              fontWeight: 800,
              minWidth: '55px',
              textAlign: 'center'
            }}
          >
            THEN
          </span>
          {isCustomEditing ? (
            <input
              type="text"
              value={currentBdd.then}
              onChange={e => setCurrentBdd({ ...currentBdd, then: e.target.value })}
              style={{
                flex: 1,
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#ffffff',
                padding: '0.25rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem'
              }}
            />
          ) : (
            <span style={{ color: '#e2e8f0', fontSize: '0.82rem', lineHeight: 1.4 }}>
              {currentBdd.then}
            </span>
          )}
        </div>

        {/* UNLESS Clause (Optional Edge Case Shield) */}
        {hasUnless && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem' }}>
            <span
              style={{
                background: 'rgba(248, 113, 113, 0.2)',
                color: '#f87171',
                border: '1px solid #dc2626',
                padding: '0.15rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.72rem',
                fontWeight: 800,
                minWidth: '55px',
                textAlign: 'center'
              }}
            >
              UNLESS
            </span>
            {isCustomEditing ? (
              <input
                type="text"
                value={currentBdd.unless || ''}
                onChange={e => setCurrentBdd({ ...currentBdd, unless: e.target.value })}
                style={{
                  flex: 1,
                  background: '#1e293b',
                  border: '1px solid #334155',
                  color: '#ffffff',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '0.35rem',
                  fontSize: '0.8rem'
                }}
              />
            ) : (
              <span style={{ color: '#fca5a5', fontSize: '0.82rem', lineHeight: 1.4 }}>
                {currentBdd.unless}
              </span>
            )}
            <button
              type="button"
              onClick={handleToggleUnless}
              style={{
                background: 'none',
                border: 'none',
                color: '#64748b',
                cursor: 'pointer',
                fontSize: '0.75rem',
                padding: '0 0.3rem'
              }}
              title="Remove UNLESS edge-case rule"
            >
              ✕
            </button>
          </div>
        )}

        {!hasUnless && (
          <div style={{ textAlign: 'right' }}>
            <button
              type="button"
              onClick={handleToggleUnless}
              style={{
                background: 'transparent',
                border: '1px dashed #475569',
                color: '#94a3b8',
                fontSize: '0.7rem',
                padding: '0.2rem 0.5rem',
                borderRadius: '0.35rem',
                cursor: 'pointer'
              }}
            >
              + Add UNLESS Edge-Case Guard
            </button>
          </div>
        )}
      </div>

      {/* Prototype Schema Preview (if available) */}
      {ticket.ticket_type === 'PROTOTYPE' && ticket.schema_preview && (
        <div style={{ background: '#020617', border: '1px solid #1e293b', borderRadius: '0.5rem', padding: '0.75rem' }}>
          <span style={{ display: 'block', fontSize: '0.7rem', fontWeight: 700, color: '#c084fc', marginBottom: '0.4rem', textTransform: 'uppercase' }}>
            📱 Throwaway UI Schema Contract
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {Object.entries(ticket.schema_preview.properties || {}).map(([key, prop]: [string, any]) => (
              <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8' }}>
                <code>{key}</code>
                <span style={{ color: '#64748b' }}>({prop.type || 'string'})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lock Decision Action */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.25rem' }}>
        <button
          type="button"
          onClick={() => onLockTicket(ticket.id, currentBdd)}
          disabled={isLocking}
          style={{
            background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            color: '#ffffff',
            border: 'none',
            padding: '0.6rem 1.25rem',
            borderRadius: '0.5rem',
            fontWeight: 700,
            fontSize: '0.85rem',
            cursor: isLocking ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            transition: 'all 0.15s ease'
          }}
        >
          <span>{isLocking ? '⏳' : '🔒'}</span>
          <span>{isLocking ? 'Locking Invariant...' : 'Lock Decision & Advance Frontier'}</span>
        </button>
      </div>
    </div>
  );
};

export default WayfinderBddCard;
