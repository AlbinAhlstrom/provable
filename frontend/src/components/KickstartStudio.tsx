import React, { useState, useEffect } from 'react';
import { AppPreview } from './AppPreview';

export interface KickstartStudioProps {
  onAppSynthesized?: () => void;
}

export const KickstartStudio: React.FC<KickstartStudioProps> = ({ onAppSynthesized }) => {
  const [pitch, setPitch] = useState<string>('');



  const [building, setBuilding] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [synthesized, setSynthesized] = useState<boolean>(false);
  const [llmConfigured, setLlmConfigured] = useState<boolean>(true);

  useEffect(() => {
    const checkState = async () => {
      try {
        const res = await fetch('/api/kickstart/state');
        const state = await res.json();
        if (state) {
          if (state.business_pitch) setPitch(state.business_pitch);
          if (typeof state.synthesized === 'boolean') setSynthesized(state.synthesized);
          if (typeof state.llm_configured === 'boolean') setLlmConfigured(state.llm_configured);
        }
      } catch (err) {
        console.error("Failed to fetch kickstart state:", err);
      }
    };
    checkState();
  }, []);


  const handleInstantBuild = async () => {
    if (!pitch.trim()) return;
    setBuilding(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/kickstart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pitch: pitch.trim() })
      });
      let data: any = {};
      try {
        data = await res.json();
      } catch {
        data = { error: `Server returned HTTP ${res.status}` };
      }

      if (res.ok && data.success) {
        setSynthesized(true);
        setResetMessage("✨ Domain architecture synthesized successfully!");
        if (onAppSynthesized) onAppSynthesized();
      } else {
        const msg = data.error || data.detail || data.message || `Synthesis failed (HTTP ${res.status})`;
        setResetMessage(`⚠️ Synthesis error: ${msg}`);
      }
    } catch (err: any) {
      console.error("Instant build failed:", err);
      setResetMessage(`❌ Network error: ${err?.message || 'Could not connect to backend server on port 8000.'}`);
    } finally {
      setBuilding(false);
    }
  };


  const handleResetAllProjects = async () => {
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSynthesized(false);
        setResetMessage("✨ Active workspace wiped successfully.");
        if (onAppSynthesized) onAppSynthesized();
        setTimeout(() => setResetMessage(null), 3000);
      } else {
        setResetMessage("⚠️ Reset notice: " + (data.error || 'Unknown notice'));
      }
    } catch (err) {
      setResetMessage("❌ Network notice resetting projects.");
    } finally {
      setResetting(false);
    }
  };

  // ── VIEW 2: POST-GENERATION LIVE APP VIEW WITH RESET WORKSPACE ─────────────────
  if (synthesized) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
        <div style={{ flex: 1, minHeight: 0 }}>
          <AppPreview
            onResetWorkspace={handleResetAllProjects}
            resetting={resetting}
            resetMessage={resetMessage}
          />
        </div>
      </div>
    );
  }

  // ── VIEW 1: INITIAL 1-CLICK PROMPT FORM ────────────────────────────────────────
  return (
    <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1rem' }}>
      
      {/* Header Banner */}
      <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', border: '1px solid #334155', borderRadius: '1rem', padding: '2.5rem', marginBottom: '2rem', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '2rem' }}>⚡</span>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.75rem', color: '#f8fafc', fontWeight: 800 }}>Provable Architecture Synthesizer</h2>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#94a3b8' }}>Define your domain bounded context to synthesize verified DDD domain aggregates, OpenAPI contracts &amp; live preview.</p>
            </div>
          </div>
        </div>

        {/* Status Toast */}
        {resetMessage && (
          <div style={{ background: resetMessage.includes('failed') || resetMessage.includes('error') ? '#450a0a' : '#064e3b', border: `1px solid ${resetMessage.includes('failed') || resetMessage.includes('error') ? '#991b1b' : '#047857'}`, color: resetMessage.includes('failed') || resetMessage.includes('error') ? '#fca5a5' : '#a7f3d0', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontWeight: 600 }}>
            {resetMessage}
          </div>
        )}

        {/* API Key Missing Notice */}
        {!llmConfigured && (
          <div style={{ background: 'rgba(234, 179, 8, 0.1)', border: '1px solid #ca8a04', borderRadius: '0.5rem', padding: '0.75rem 1rem', color: '#fef08a', fontSize: '0.85rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.1rem' }}>🔑</span>
            <div>
              <strong>LLM API Key Not Configured:</strong> Set <code>GEMINI_API_KEY</code>, <code>OPENAI_API_KEY</code>, or <code>LLM_API_KEY</code> in your root <code>.env</code> file to enable live AI domain synthesis.
            </div>
          </div>
        )}


        {/* Prompt Input Area */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#f59e0b', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Define Bounded Context:
          </label>
          <textarea
            rows={4}
            value={pitch}
            onChange={e => setPitch(e.target.value)}
            disabled={building}
            placeholder="e.g., Describe your domain bounded context, aggregate roots, entities, and business invariant rules."
            style={{
              width: '100%',
              background: '#0f172a',
              border: '1px solid #475569',
              color: '#fff',
              padding: '1rem',
              borderRadius: '0.75rem',
              fontSize: '1rem',
              fontFamily: 'inherit',
              lineHeight: 1.5,
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Build Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={handleInstantBuild}
            disabled={building || !pitch.trim()}
            style={{
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              border: 'none',
              padding: '0.85rem 2rem',
              borderRadius: '9999px',
              fontWeight: 800,
              fontSize: '1.1rem',
              cursor: building ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem'
            }}
          >
            {building ? '⏳ Synthesizing Domain Architecture...' : '⚡ Synthesize Architecture'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default KickstartStudio;
