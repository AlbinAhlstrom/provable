import React, { useState, useEffect } from 'react';
import { BusinessSpecItemDTO } from '../types/api';

export interface DomainAggregateItem {
  id: string;
  name: string;
  canonical_key: string;
  icon: string;
  desc: string;
  attributes: Array<{ name: string; type: string; required?: boolean }>;
}

export interface RequirementControlPanelProps {
  fullWidth?: boolean;
  onParamUpdated?: () => void;
}

export const RequirementControlPanel: React.FC<RequirementControlPanelProps> = ({ fullWidth = false, onParamUpdated }) => {
  const [aggregates, setAggregates] = useState<DomainAggregateItem[]>([]);
  const [specs, setSpecs] = useState<BusinessSpecItemDTO[]>([]);
  const [expandedAggregates, setExpandedAggregates] = useState<Set<string>>(new Set());
  const [activeTabByAggregate, setActiveTabByAggregate] = useState<Record<string, 'specs' | 'data'>>({});
  const [statusToast, setStatusToast] = useState<string | null>(null);

  // New Spec Form State by Aggregate
  const [addingSpecForAggregate, setAddingSpecForAggregate] = useState<string | null>(null);
  const [newSpecTitle, setNewSpecTitle] = useState<string>('');
  const [newSpecType, setNewSpecType] = useState<string>('DOMAIN_INVARIANT');
  const [newGiven, setNewGiven] = useState<string>('');
  const [newWhen, setNewWhen] = useState<string>('');
  const [newThen, setNewThen] = useState<string>('');
  const [newUnless, setNewUnless] = useState<string>('');
  const [isMathBoundary, setIsMathBoundary] = useState<boolean>(false);
  const [submittingSpec, setSubmittingSpec] = useState<boolean>(false);

  // Entity Data Fixtures State
  const [dataFixturesByAggregate, setDataFixturesByAggregate] = useState<Record<string, Array<Record<string, any>>>>({});

  const toggleAggregateExpand = (key: string) => {
    setExpandedAggregates(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const toggleAggregateTab = (key: string, tab: 'specs' | 'data') => {
    setActiveTabByAggregate(prev => ({ ...prev, [key]: tab }));
  };

  const hydrateData = async () => {
    try {
      // 0. Fetch active domain aggregates dynamically from backend
      const aggRes = await fetch('/api/onboarding/aggregates');
      if (aggRes.ok) {
        const aggData = await aggRes.json();
        if (aggData && Array.isArray(aggData.aggregates) && aggData.aggregates.length > 0) {
          const loadedAggs = aggData.aggregates.map((a: any) => ({
            id: a.key || a.canonical_key || a.name.toLowerCase(),
            name: a.name,
            canonical_key: a.key || a.canonical_key || a.name.toLowerCase(),
            icon: a.icon || '📦',
            desc: a.description || `${a.name} Aggregate Root`,
            attributes: (a.fields || a.attributes || []).map((f: any) => ({
              name: f.name,
              type: f.type || 'string',
              required: f.required !== false
            }))
          }));
          setAggregates(loadedAggs);
          setExpandedAggregates(prev => prev.size === 0 ? new Set(loadedAggs.map((a: any) => a.id)) : prev);
        }
      }

      // 1. Fetch active specs from Behavior Inbox
      const specRes = await fetch('/api/specs/inbox');
      if (specRes.ok) {
        const specData = await specRes.json();
        if (Array.isArray(specData)) {
          setSpecs(specData);
        }
      }

      // 2. Fetch active domain schemas & data fixtures
      const entRes = await fetch('/api/components/entities');
      if (entRes.ok) {
        const entData = await entRes.json();
        if (entData && entData.success) {
          if (entData.fixtures && Object.keys(entData.fixtures).length > 0) {
            setDataFixturesByAggregate(prev => ({ ...prev, ...entData.fixtures }));
          }
        }
      }
    } catch (e) {
      console.error("Hydration error in RequirementControlPanel:", e);
    }
  };

  useEffect(() => {
    hydrateData();
    const interval = setInterval(hydrateData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleAddSpecSubmit = async (aggregateName: string) => {
    if (!newSpecTitle.trim()) return;

    setSubmittingSpec(true);
    try {
      const gwtParts = [];
      if (newGiven.trim()) gwtParts.push(`Given ${newGiven.trim().replace(/^Given\s*/i, '')}`);
      if (newWhen.trim()) gwtParts.push(`When ${newWhen.trim().replace(/^When\s*/i, '')}`);
      if (newThen.trim()) gwtParts.push(`Then ${newThen.trim().replace(/^Then\s*/i, '')}`);
      if (newUnless.trim()) gwtParts.push(`Unless ${newUnless.trim().replace(/^Unless\s*/i, '')}`);
      
      const gwtText = gwtParts.join(', ') || `Given valid ${aggregateName}, When action executed, Then state transitions cleanly`;

      const payload = {
        title: newSpecTitle.trim(),
        description: newSpecTitle.trim(),
        given_when_then: gwtText,
        target_aggregate: aggregateName,
        spec_type: newSpecType,
        is_mathematical_boundary: isMathBoundary,
        priority: 'High'
      };

      const res = await fetch('/api/specs/inbox/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setStatusToast(`✨ Added specification for ${aggregateName}`);
        setAddingSpecForAggregate(null);
        setNewSpecTitle('');
        setNewGiven('');
        setNewWhen('');
        setNewThen('');
        setNewUnless('');
        setIsMathBoundary(false);
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        const data = await res.json();
        setStatusToast(`❌ Failed to add spec: ${data.error || 'Check server logs'}`);
      }
    } catch (err) {
      console.error("Error adding spec:", err);
      setStatusToast(`❌ Network error adding spec`);
    } finally {
      setSubmittingSpec(false);
      setTimeout(() => setStatusToast(null), 3000);
    }
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'FULFILLED':
        return <span style={{ background: '#059669', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>🟢 FULFILLED</span>;
      case 'IN_PROGRESS':
        return <span style={{ background: '#d97706', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>⚡ TDD RUNNING</span>;
      case 'REQUIRES_HUMAN_INTERVENTION':
        return <span style={{ background: '#dc2626', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>🔴 NEEDS REVIEW</span>;
      default:
        return <span style={{ background: '#475569', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>⏳ PENDING</span>;
    }
  };

  const getSpecTypeBadge = (specType?: string) => {
    switch (specType) {
      case 'ATTRIBUTE_EXPANSION':
        return <span style={{ background: '#1e3a8a', color: '#93c5fd', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 600 }}>🏷️ ATTRIBUTE</span>;
      case 'STATE_TRANSITION':
        return <span style={{ background: '#581c87', color: '#d8b4fe', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 600 }}>🔄 STATE</span>;
      case 'API_CONTRACT':
        return <span style={{ background: '#064e3b', color: '#6ee7b7', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 600 }}>🔌 API</span>;
      default:
        return <span style={{ background: '#14532d', color: '#86efac', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 600 }}>🛡️ INVARIANT</span>;
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: fullWidth ? '100%' : 'auto',
      background: '#090d16',
      border: '1px solid #1e293b',
      borderRadius: '0.75rem',
      padding: '0.85rem',
      gap: '0.85rem',
      overflow: 'hidden',
      boxSizing: 'border-box'
    }}>
      {/* Panel Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '0.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>🧬</span>
          <div>
            <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 800, letterSpacing: '0.02em' }}>
              DOMAIN AGGREGATES
            </h3>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
              Aggregate Roots driving contract-first BDD specifications &amp; TDD states.
            </p>
          </div>
        </div>
        <span style={{ background: '#0284c7', color: '#fff', fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '9999px' }}>
          {aggregates.length} Aggregates
        </span>
      </div>

      {/* Toast Notification */}
      {statusToast && (
        <div style={{
          background: statusToast.includes('❌') ? '#450a0a' : '#064e3b',
          border: `1px solid ${statusToast.includes('❌') ? '#991b1b' : '#047857'}`,
          color: statusToast.includes('❌') ? '#fca5a5' : '#a7f3d0',
          padding: '0.45rem 0.75rem',
          borderRadius: '0.4rem',
          fontSize: '0.8rem',
          fontWeight: 600
        }}>
          {statusToast}
        </div>
      )}

      {/* Aggregates List */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {aggregates.map(agg => {
          const isExpanded = expandedAggregates.has(agg.canonical_key);
          const aggSpecs = specs.filter(s => (s.target_aggregate || '').toLowerCase() === agg.name.toLowerCase());
          const fixtures = dataFixturesByAggregate[agg.canonical_key] || [];
          const activeTab = activeTabByAggregate[agg.canonical_key] || 'specs';

          return (
            <div
              key={agg.id}
              style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '0.75rem',
                padding: '0.75rem 0.85rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.65rem'
              }}
            >
              {/* Accordion Header */}
              <div
                onClick={() => toggleAggregateExpand(agg.canonical_key)}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span style={{ fontSize: '1.2rem' }}>{agg.icon}</span>
                  <div>
                    <strong style={{ fontSize: '0.9rem', color: '#f8fafc' }}>{agg.name}</strong>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '0.5rem', fontFamily: 'monospace' }}>
                      ({agg.canonical_key})
                    </span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ fontSize: '0.7rem', background: '#1e293b', border: '1px solid #334155', color: '#38bdf8', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 600 }}>
                    {aggSpecs.length} Specs
                  </span>
                  <span style={{ fontSize: '0.7rem', background: '#1e293b', border: '1px solid #334155', color: '#34d399', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 600 }}>
                    {fixtures.length} Entities
                  </span>
                </div>
              </div>

              {/* Accordion Body */}
              {isExpanded && (
                <div style={{ marginTop: '0.25rem', paddingTop: '0.5rem', borderTop: '1px solid #1e293b', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.4 }}>
                    {agg.desc}
                  </p>

                  {/* 2-Tab Switcher: 🧪 BDD Specs vs 📦 Entity Data */}
                  <div style={{ display: 'flex', background: '#090d16', border: '1px solid #334155', borderRadius: '0.4rem', padding: '0.15rem' }}>
                    <button
                      onClick={() => toggleAggregateTab(agg.canonical_key, 'specs')}
                      style={{
                        flex: 1,
                        background: activeTab === 'specs' ? '#0284c7' : 'transparent',
                        color: activeTab === 'specs' ? '#ffffff' : '#94a3b8',
                        border: 'none',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.3rem',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        cursor: 'pointer'
                      }}
                    >
                      🧪 BDD Specs ({aggSpecs.length})
                    </button>
                    <button
                      onClick={() => toggleAggregateTab(agg.canonical_key, 'data')}
                      style={{
                        flex: 1,
                        background: activeTab === 'data' ? '#0284c7' : 'transparent',
                        color: activeTab === 'data' ? '#ffffff' : '#94a3b8',
                        border: 'none',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.3rem',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        cursor: 'pointer'
                      }}
                    >
                      🧬 Entity Data ({fixtures.length})
                    </button>
                  </div>

                  {/* TAB 1: BDD SPECS */}
                  {activeTab === 'specs' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {aggSpecs.length === 0 ? (
                        <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic', padding: '0.4rem 0' }}>
                          No specifications registered for {agg.name}. Add a BDD rule below to trigger deterministic TDD synthesis.
                        </div>
                      ) : (
                        aggSpecs.map((s, idx) => (
                          <div
                            key={s.spec_id || idx}
                            style={{
                              background: '#1e293b',
                              border: '1px solid #334155',
                              borderRadius: '0.5rem',
                              padding: '0.5rem 0.75rem',
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '0.35rem'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                                {getStatusBadge(s.status)}
                                {getSpecTypeBadge(s.spec_type)}
                                <strong style={{ fontSize: '0.8rem', color: '#f8fafc' }}>{s.title}</strong>
                              </div>
                              <span style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace' }}>
                                {s.spec_id}
                              </span>
                            </div>

                            {/* GIVEN / WHEN / THEN / UNLESS pill breakdown */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.2rem' }}>
                              <span style={{ fontSize: '0.72rem', background: '#0f172a', border: '1px solid #334155', color: '#cbd5e1', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                                📋 {s.given_when_then}
                              </span>
                            </div>

                            {/* Generated test + attempt history, so a human can review what "verified" actually means */}
                            {s.tdd && (s.tdd.test_source || s.tdd.error) && (
                              <details style={{ marginTop: '0.2rem' }}>
                                <summary style={{ cursor: 'pointer', fontSize: '0.72rem', color: '#38bdf8' }}>
                                  🧪 Generated test &amp; TDD attempts
                                  {s.tdd.test_location ? ` (${s.tdd.test_location})` : ''}
                                </summary>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', marginTop: '0.3rem' }}>
                                  {[...s.tdd.red_attempts.map(a => ({ ...a, stage: 'RED' })), ...s.tdd.attempts.map(a => ({ ...a, stage: 'GREEN' }))].map((a, i) => (
                                    <span key={i} style={{ fontSize: '0.7rem', color: a.approved ? '#86efac' : '#fca5a5' }}>
                                      {a.approved ? '✔' : '✖'} {a.stage} attempt {a.attempt}{a.reason ? `: ${a.reason}` : ''}
                                    </span>
                                  ))}
                                  {s.tdd.error && (
                                    <span style={{ fontSize: '0.7rem', color: '#fca5a5' }}>
                                      ⚠ {s.tdd.error}{s.tdd.rolled_back ? ' (domain code rolled back)' : ''}
                                    </span>
                                  )}
                                  {s.tdd.test_source && (
                                    <pre style={{ margin: 0, fontSize: '0.68rem', background: '#0b1220', border: '1px solid #334155', borderRadius: '4px', padding: '0.4rem', color: '#cbd5e1', overflowX: 'auto', maxHeight: '16rem' }}>
                                      {s.tdd.test_source}
                                    </pre>
                                  )}
                                </div>
                              </details>
                            )}
                          </div>
                        ))
                      )}

                      {/* Add Spec Action Button / Form */}
                      {addingSpecForAggregate === agg.name ? (
                        <div style={{ background: '#0b1329', border: '1px solid #1e3a8a', borderRadius: '0.5rem', padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.35rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#38bdf8' }}>
                              ➕ Add Specification for {agg.name}
                            </strong>
                            <button
                              onClick={() => setAddingSpecForAggregate(null)}
                              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '0.8rem' }}
                            >
                              ✕
                            </button>
                          </div>

                          <input
                            type="text"
                            placeholder="Spec title (e.g., Enforce Aggregate Boundary Invariant)"
                            value={newSpecTitle}
                            onChange={e => setNewSpecTitle(e.target.value)}
                            style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.4rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem' }}
                          />

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
                            <select
                              value={newSpecType}
                              onChange={e => setNewSpecType(e.target.value)}
                              style={{ background: '#1e293b', border: '1px solid #334155', color: '#93c5fd', padding: '0.35rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem', fontWeight: 600 }}
                            >
                              <option value="DOMAIN_INVARIANT">🛡️ Invariant Check</option>
                              <option value="ATTRIBUTE_EXPANSION">🏷️ Attribute Expansion</option>
                              <option value="STATE_TRANSITION">🔄 State Transition</option>
                              <option value="API_CONTRACT">🔌 API Contract</option>
                            </select>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.72rem', color: '#cbd5e1', cursor: 'pointer' }}>
                              <input
                                type="checkbox"
                                checked={isMathBoundary}
                                onChange={e => setIsMathBoundary(e.target.checked)}
                              />
                              Mathematical Boundary
                            </label>
                          </div>

                          <input
                            type="text"
                            placeholder="GIVEN precondition (e.g., Entity is in active state)"
                            value={newGiven}
                            onChange={e => setNewGiven(e.target.value)}
                            style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                          />

                          <input
                            type="text"
                            placeholder="WHEN action triggered (e.g., State transition or event occurs)"
                            value={newWhen}
                            onChange={e => setNewWhen(e.target.value)}
                            style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                          />

                          <input
                            type="text"
                            placeholder="THEN assertion (e.g., Target state or invariant is validated)"
                            value={newThen}
                            onChange={e => setNewThen(e.target.value)}
                            style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                          />

                          <button
                            onClick={() => handleAddSpecSubmit(agg.name)}
                            disabled={submittingSpec || !newSpecTitle.trim()}
                            style={{
                              background: '#0284c7',
                              color: '#fff',
                              border: 'none',
                              padding: '0.45rem',
                              borderRadius: '0.35rem',
                              fontSize: '0.8rem',
                              fontWeight: 700,
                              cursor: submittingSpec || !newSpecTitle.trim() ? 'not-allowed' : 'pointer'
                            }}
                          >
                            {submittingSpec ? '⏳ Registering Spec...' : '💾 Register BDD Specification'}
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setAddingSpecForAggregate(agg.name)}
                          style={{
                            background: 'rgba(2, 132, 199, 0.1)',
                            border: '1px dashed #0284c7',
                            color: '#38bdf8',
                            padding: '0.45rem',
                            borderRadius: '0.4rem',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            marginTop: '0.25rem'
                          }}
                        >
                          ➕ Add BDD Spec for {agg.name}
                        </button>
                      )}
                    </div>
                  )}

                  {/* TAB 2: ENTITY DATA FIXTURES */}
                  {activeTab === 'data' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        {fixtures.length === 0 ? (
                          <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
                            No entity records populated for {agg.name}.
                          </div>
                        ) : (
                          fixtures.map((item, idx) => (
                            <div
                              key={item.id || idx}
                              style={{
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '0.4rem',
                                padding: '0.45rem 0.65rem',
                                fontSize: '0.75rem',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '0.25rem'
                              }}
                            >
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <strong style={{ color: '#f8fafc' }}>
                                  {item.id || item.sku || item.name || `Record #${idx + 1}`}
                                </strong>
                                {item.status && (
                                  <span style={{ fontSize: '0.65rem', background: '#0284c7', color: '#fff', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 600 }}>
                                    {item.status}
                                  </span>
                                )}
                              </div>
                              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', color: '#94a3b8', fontSize: '0.72rem' }}>
                                {Object.entries(item).filter(([k]) => k !== 'id' && k !== 'status').map(([k, v]) => (
                                  <span key={k} style={{ background: '#0f172a', padding: '0.1rem 0.35rem', borderRadius: '3px' }}>
                                    <strong style={{ color: '#cbd5e1' }}>{k}:</strong> {Array.isArray(v) ? v.join(', ') : String(v)}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
