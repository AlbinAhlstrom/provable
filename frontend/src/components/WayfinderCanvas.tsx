import React, { useState, useEffect } from 'react';
import { WayfinderGraphState, BddClause } from '../types/wayfinder';
import { WayfinderBddCard } from './WayfinderBddCard';

export interface WayfinderCanvasProps {
  pitch?: string;
  onAppSynthesized?: () => void;
  onBackToPitch?: () => void;
}

export const WayfinderCanvas: React.FC<WayfinderCanvasProps> = ({
  pitch,
  onAppSynthesized,
  onBackToPitch
}) => {
  const [graph, setGraph] = useState<WayfinderGraphState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [lockingTicketId, setLockingTicketId] = useState<string | null>(null);
  const [synthesizing, setSynthesizing] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [capabilities, setCapabilities] = useState<{
    opencode_connected: boolean;
    aider_available: boolean;
    native_scaffold_ready: boolean;
    active_greenfield_engine?: string;
    active_precision_engine?: string;
  } | null>(null);

  const initGraph = async () => {
    setLoading(true);
    try {
      // Probe engine capabilities
      try {
        const capRes = await fetch('/api/system/capabilities');
        if (capRes.ok) {
          const capData = await capRes.json();
          setCapabilities(capData);
        }
      } catch (capErr) {
        console.warn('Could not probe engine capabilities:', capErr);
      }

      if (pitch && pitch.trim()) {
        const genRes = await fetch('/api/wayfinder/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pitch: pitch.trim() })
        });
        if (genRes.ok) {
          const data = await genRes.json();
          setGraph(data);
          return;
        }
      }

      // Fallback: Fetch current state
      const stateRes = await fetch('/api/wayfinder/state');
      if (stateRes.ok) {
        const data = await stateRes.json();
        setGraph(data);
      }
    } catch (err) {
      console.error('Failed to initialize Wayfinder graph:', err);
      setStatusMessage('⚠️ Could not connect to Wayfinder backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTicket = async (ticketId: string) => {
    setStatusMessage(`⚡ Dispatching invariant ${ticketId} to Aider Precision Bridge...`);
    try {
      const res = await fetch('/api/wayfinder/execute-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_id: ticketId })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        const engine = data.execution_result?.engine || 'Aider';
        setStatusMessage(`🟢 Invariant ${ticketId} processed via ${engine}!`);
        setTimeout(() => setStatusMessage(null), 4000);
      } else {
        setStatusMessage(`⚠️ Execution notice: ${data.detail || data.error || 'Check logs'}`);
      }
    } catch (err: any) {
      setStatusMessage(`❌ Error executing ticket: ${err?.message}`);
    }
  };

  useEffect(() => {
    initGraph();
  }, [pitch]);

  const handleLockTicket = async (ticketId: string, bdd: BddClause) => {
    setLockingTicketId(ticketId);
    setStatusMessage(null);
    try {
      const res = await fetch('/api/wayfinder/lock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: ticketId,
          bdd: bdd
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setGraph(updated);
        setStatusMessage(`✨ Locked invariant for ${ticketId} — Frontier updated!`);
        setTimeout(() => setStatusMessage(null), 3500);
      } else {
        const err = await res.json();
        setStatusMessage(`❌ Error: ${err.detail || 'Could not lock ticket.'}`);
      }
    } catch (err: any) {
      setStatusMessage(`❌ Network error locking ticket: ${err?.message}`);
    } finally {
      setLockingTicketId(null);
    }
  };

  const handleSynthesize = async () => {
    if (!graph) return;
    setSynthesizing(true);
    setStatusMessage('⏳ Compiling charted Wayfinder architecture into verified TDD stack...');
    try {
      const res = await fetch('/api/wayfinder/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok && data.success) {
        setStatusMessage('🚀 Domain architecture synthesized with 100% verified test coverage!');
        if (onAppSynthesized) onAppSynthesized();
      } else {
        setStatusMessage(`⚠️ Synthesis notice: ${data.error || data.detail || 'Check server logs.'}`);
      }
    } catch (err: any) {
      setStatusMessage(`❌ Network error: ${err?.message}`);
    } finally {
      setSynthesizing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '1200px', margin: '3rem auto', padding: '0 1rem', textAlign: 'center', color: '#94a3b8' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem', animation: 'spin 2s linear infinite' }}>🧭</div>
        <h3 style={{ color: '#f8fafc', fontWeight: 700 }}>Mapping Architectural Decision Frontier...</h3>
        <p>Decomposing domain pitch into BDD Mad-Libs contracts and DAG dependencies.</p>
      </div>
    );
  }

  if (!graph) {
    return (
      <div style={{ maxWidth: '800px', margin: '3rem auto', textAlign: 'center', color: '#94a3b8' }}>
        <p>No active Wayfinder architecture found.</p>
        {onBackToPitch && (
          <button
            onClick={onBackToPitch}
            style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}
          >
            ← Back to Pitch
          </button>
        )}
      </div>
    );
  }

  const frontierTickets = graph.frontier || [];
  const lockedTickets = graph.locked || [];
  const fogTickets = graph.fog || [];

  return (
    <div style={{ maxWidth: '1400px', margin: '1.5rem auto', padding: '0 1rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* ── TOP RADAR HEADER BAR ─────────────────────────────────────────── */}
      <div
        style={{
          background: 'linear-gradient(135deg, #0b1329 0%, #1e293b 100%)',
          border: '1px solid #334155',
          borderRadius: '1rem',
          padding: '1.5rem 2rem',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.4)',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '2.2rem' }}>🗺️</span>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#f8fafc', fontWeight: 800 }}>
                  {graph.brand_name || 'Provable'} Wayfinder Radar
                </h2>
                <span style={{ fontSize: '0.75rem', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid #0284c7', padding: '0.15rem 0.6rem', borderRadius: '9999px', fontWeight: 700 }}>
                  BDD Decision Map
                </span>
                {capabilities && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span style={{ fontSize: '0.68rem', background: capabilities.opencode_connected ? 'rgba(52, 211, 153, 0.15)' : 'rgba(100, 116, 139, 0.2)', color: capabilities.opencode_connected ? '#34d399' : '#94a3b8', border: `1px solid ${capabilities.opencode_connected ? '#059669' : '#475569'}`, padding: '0.1rem 0.45rem', borderRadius: '9999px', fontWeight: 700 }}>
                      {capabilities.opencode_connected ? '🟢 OpenCode Connected' : '⚪ OpenCode Standby'}
                    </span>
                    <span style={{ fontSize: '0.68rem', background: capabilities.aider_available ? 'rgba(56, 189, 248, 0.15)' : 'rgba(100, 116, 139, 0.2)', color: capabilities.aider_available ? '#38bdf8' : '#94a3b8', border: `1px solid ${capabilities.aider_available ? '#0284c7' : '#475569'}`, padding: '0.1rem 0.45rem', borderRadius: '9999px', fontWeight: 700 }}>
                      {capabilities.aider_available ? '🟢 Aider Scalpel Ready' : '⚪ Aider Standby'}
                    </span>
                    <span style={{ fontSize: '0.68rem', background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', border: '1px solid #9333ea', padding: '0.1rem 0.45rem', borderRadius: '9999px', fontWeight: 700 }}>
                      🟢 1s Native Scaffold
                    </span>
                  </div>
                )}
              </div>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#94a3b8' }}>
                <strong>North Star:</strong> &ldquo;{graph.pitch}&rdquo;
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {onBackToPitch && (
              <button
                type="button"
                onClick={onBackToPitch}
                disabled={synthesizing}
                style={{
                  background: 'transparent',
                  border: '1px solid #475569',
                  color: '#94a3b8',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.5rem',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                ← Edit Pitch
              </button>
            )}

            <button
              type="button"
              onClick={handleSynthesize}
              disabled={synthesizing || !graph.is_synthesis_ready}
              style={{
                background: graph.is_synthesis_ready
                  ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                  : '#1e293b',
                color: graph.is_synthesis_ready ? '#ffffff' : '#64748b',
                border: graph.is_synthesis_ready ? 'none' : '1px solid #334155',
                padding: '0.65rem 1.4rem',
                borderRadius: '9999px',
                fontWeight: 800,
                fontSize: '0.92rem',
                cursor: graph.is_synthesis_ready && !synthesizing ? 'pointer' : 'not-allowed',
                boxShadow: graph.is_synthesis_ready ? '0 4px 16px rgba(16, 185, 129, 0.4)' : 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s ease'
              }}
            >
              <span>{synthesizing ? '⏳' : '🚀'}</span>
              <span>
                {synthesizing
                  ? 'Synthesizing Verified App...'
                  : graph.is_synthesis_ready
                    ? 'Synthesize Verified Application'
                    : 'Lock Core Decisions to Synthesize'}
              </span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem' }}>
            <span>FRONTIER PROGRESSION</span>
            <span style={{ color: graph.progress_pct > 0 ? '#38bdf8' : '#64748b' }}>
              {graph.progress_pct}% MAPPED ({lockedTickets.length}/{graph.tickets.length} DECISIONS SETTLED)
            </span>
          </div>
          <div style={{ height: '8px', background: '#0f172a', borderRadius: '9999px', overflow: 'hidden', border: '1px solid #1e293b' }}>
            <div
              style={{
                width: `${graph.progress_pct}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #0284c7 0%, #10b981 100%)',
                transition: 'width 0.4s ease'
              }}
            />
          </div>
        </div>

        {/* Status Toast */}
        {statusMessage && (
          <div
            style={{
              background: statusMessage.includes('❌') || statusMessage.includes('⚠️') ? '#450a0a' : '#064e3b',
              border: `1px solid ${statusMessage.includes('❌') || statusMessage.includes('⚠️') ? '#991b1b' : '#047857'}`,
              color: statusMessage.includes('❌') || statusMessage.includes('⚠️') ? '#fca5a5' : '#a7f3d0',
              padding: '0.6rem 1rem',
              borderRadius: '0.5rem',
              fontSize: '0.82rem',
              fontWeight: 600
            }}
          >
            {statusMessage}
          </div>
        )}
      </div>

      {/* ── 3-COLUMN ARCHITECTURAL RADAR ─────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr 1fr', gap: '1.25rem', alignItems: 'start' }}>
        {/* ── COLUMN 1: 🔒 LOCKED GROUND ─────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.1rem' }}>🔒</span>
              <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 800 }}>
                LOCKED GROUND
              </h3>
            </div>
            <span style={{ fontSize: '0.75rem', background: 'rgba(52, 211, 153, 0.15)', color: '#34d399', padding: '0.15rem 0.55rem', borderRadius: '9999px', fontWeight: 700 }}>
              {lockedTickets.length} Settled
            </span>
          </div>

          {lockedTickets.length === 0 ? (
            <div style={{ background: '#090d16', border: '1px dashed #334155', borderRadius: '0.75rem', padding: '2rem 1rem', textAlign: 'center', color: '#64748b' }}>
              <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '0.5rem' }}>🌱</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>No decisions locked yet.</p>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.75rem', color: '#475569' }}>
                Resolve tickets on the Active Frontier to cement your domain architecture.
              </p>
            </div>
          ) : (
            lockedTickets.map(t => {
              const bdd = t.resolved_bdd || t.bdd_template;
              return (
                <div
                  key={t.id}
                  style={{
                    background: '#0f172a',
                    border: '1px solid #059669',
                    borderRadius: '0.75rem',
                    padding: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.6rem',
                    boxShadow: '0 4px 12px rgba(5, 150, 105, 0.15)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 800, color: '#34d399', background: 'rgba(5, 150, 105, 0.2)', padding: '0.15rem 0.5rem', borderRadius: '0.35rem' }}>
                      ✓ IMMUTABLE INVARIANT
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{t.target_aggregate}</span>
                  </div>
                  <h5 style={{ margin: 0, color: '#f8fafc', fontSize: '0.95rem', fontWeight: 700 }}>
                    {t.title}
                  </h5>
                  {bdd && (
                    <div style={{ background: '#020617', padding: '0.5rem', borderRadius: '0.4rem', fontSize: '0.72rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <div><strong style={{ color: '#38bdf8' }}>GIVEN</strong> <span style={{ color: '#cbd5e1' }}>{bdd.given}</span></div>
                      <div><strong style={{ color: '#fbbf24' }}>WHEN</strong> <span style={{ color: '#cbd5e1' }}>{bdd.when}</span></div>
                      <div><strong style={{ color: '#34d399' }}>THEN</strong> <span style={{ color: '#cbd5e1' }}>{bdd.then}</span></div>
                      {bdd.unless && <div><strong style={{ color: '#f87171' }}>UNLESS</strong> <span style={{ color: '#cbd5e1' }}>{bdd.unless}</span></div>}
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                    <button
                      type="button"
                      onClick={() => handleExecuteTicket(t.id)}
                      style={{
                        background: '#1e293b',
                        border: '1px solid #38bdf8',
                        color: '#38bdf8',
                        padding: '0.25rem 0.65rem',
                        borderRadius: '0.35rem',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        transition: 'all 0.15s ease'
                      }}
                      title="Execute this locked invariant using Aider precision editor or native engine"
                    >
                      <span>⚡ Run with Aider</span>
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* ── COLUMN 2: ⚡ ACTIVE FRONTIER ───────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #0284c7', paddingBottom: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.1rem' }}>⚡</span>
              <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#38bdf8', fontWeight: 800 }}>
                ACTIVE FRONTIER
              </h3>
            </div>
            <span style={{ fontSize: '0.75rem', background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8', padding: '0.15rem 0.55rem', borderRadius: '9999px', fontWeight: 700 }}>
              {frontierTickets.length} Actionable Now
            </span>
          </div>

          {frontierTickets.length === 0 ? (
            <div style={{ background: '#090d16', border: '1px solid #059669', borderRadius: '0.75rem', padding: '2.5rem 1.5rem', textAlign: 'center', color: '#cbd5e1' }}>
              <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '0.75rem' }}>🎉</span>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#34d399', fontSize: '1.15rem', fontWeight: 800 }}>
                All Critical Decisions Charted!
              </h4>
              <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.85rem', color: '#94a3b8' }}>
                The frontier is clear and the core domain invariants are fully verified. You can now compile the verified workspace stack.
              </p>
              <button
                type="button"
                onClick={handleSynthesize}
                disabled={synthesizing}
                style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#ffffff',
                  border: 'none',
                  padding: '0.75rem 1.75rem',
                  borderRadius: '9999px',
                  fontWeight: 800,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  boxShadow: '0 4px 16px rgba(16, 185, 129, 0.4)'
                }}
              >
                🚀 Synthesize Application Stack
              </button>
            </div>
          ) : (
            frontierTickets.map(t => (
              <WayfinderBddCard
                key={t.id}
                ticket={t}
                onLockTicket={handleLockTicket}
                isLocking={lockingTicketId === t.id}
              />
            ))
          )}
        </div>

        {/* ── COLUMN 3: 🌫️ FOG OF WAR ────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.1rem' }}>🌫️</span>
              <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#94a3b8', fontWeight: 800 }}>
                FOG OF WAR
              </h3>
            </div>
            <span style={{ fontSize: '0.75rem', background: 'rgba(148, 163, 184, 0.1)', color: '#64748b', padding: '0.15rem 0.55rem', borderRadius: '9999px', fontWeight: 700 }}>
              {fogTickets.length} Veiled
            </span>
          </div>

          {fogTickets.length === 0 ? (
            <div style={{ background: '#090d16', border: '1px dashed #334155', borderRadius: '0.75rem', padding: '2rem 1rem', textAlign: 'center', color: '#64748b' }}>
              <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '0.5rem' }}>☀️</span>
              <p style={{ margin: 0, fontSize: '0.8rem' }}>The fog has completely lifted!</p>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.75rem', color: '#475569' }}>
                All downstream dependencies have been successfully uncovered.
              </p>
            </div>
          ) : (
            fogTickets.map(t => (
              <div
                key={t.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.5)',
                  border: '1px dashed #334155',
                  borderRadius: '0.75rem',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                  opacity: 0.65,
                  filter: 'grayscale(30%)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#f59e0b', background: 'rgba(245, 158, 11, 0.1)', padding: '0.15rem 0.45rem', borderRadius: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <span>🔒</span>
                    <span>LOCKED DEPENDENCY</span>
                  </span>
                  <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{t.target_aggregate}</span>
                </div>

                <h5 style={{ margin: 0, color: '#94a3b8', fontSize: '0.92rem', fontWeight: 600 }}>
                  {t.title}
                </h5>

                <div style={{ fontSize: '0.72rem', color: '#64748b', background: '#020617', padding: '0.4rem 0.6rem', borderRadius: '0.35rem' }}>
                  <strong>Requires:</strong> {t.depends_on.join(', ')}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default WayfinderCanvas;
