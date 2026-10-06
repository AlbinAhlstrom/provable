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

  const triggerSynthesis = async () => {
    if (!pitch.trim()) return;
    setBuilding(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/kickstart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pitch: pitch.trim(),
          mode: 'fast'
        })
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
      console.error("Build failed:", err);
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

  // ── VIEW 1: EXECUTIVE KICKSTART (0-QUESTION INSTANT GENERATION) ────────────────
  return (
    <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1rem' }}>
      {/* Header Banner */}
      <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', border: '1px solid #334155', borderRadius: '1rem', padding: '2.5rem', marginBottom: '2rem', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '2rem' }}>⚡</span>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.75rem', color: '#f8fafc', fontWeight: 800 }}>Provable Architecture Synthesizer</h2>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#94a3b8' }}>
                Beskriv din appidé. Vår pipeline delegerar uppgiften genom hela organisationen och bygger en fullstack-app direkt.
              </p>
            </div>
          </div>
        </div>

        {/* Status Toast */}
        {resetMessage && (
          <div style={{
            background: resetMessage.includes('❌') || resetMessage.includes('⚠️') ? '#450a0a' : '#064e3b',
            border: `1px solid ${resetMessage.includes('❌') || resetMessage.includes('⚠️') ? '#991b1b' : '#047857'}`,
            color: resetMessage.includes('❌') || resetMessage.includes('⚠️') ? '#fca5a5' : '#a7f3d0',
            padding: '0.75rem 1rem',
            borderRadius: '0.5rem',
            marginBottom: '1rem',
            fontWeight: 600,
            fontSize: '0.9rem'
          }}>
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

        {/* Pitch Input Box */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Affärsidé &amp; Verksamhetskrav
          </label>
          <textarea
            value={pitch}
            onChange={e => setPitch(e.target.value)}
            placeholder="T.ex: Hotellbokningssystem för ett boutiquehotell med rumshantering, städstatus och rumsbokningar..."
            rows={3}
            style={{
              width: '100%',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '0.5rem',
              padding: '0.85rem',
              color: '#ffffff',
              fontSize: '1rem',
              fontFamily: 'inherit',
              resize: 'vertical',
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Action Button */}
        <div>
          <button
            onClick={triggerSynthesis}
            disabled={building || !pitch.trim()}
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              border: '1px solid #38bdf8',
              padding: '1.1rem 1.5rem',
              borderRadius: '0.75rem',
              fontWeight: 800,
              fontSize: '1.1rem',
              cursor: building || !pitch.trim() ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 16px rgba(2, 132, 199, 0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              opacity: !pitch.trim() ? 0.6 : 1,
              transition: 'transform 0.1s ease'
            }}
          >
            <span style={{ fontSize: '1.3rem' }}>{building ? '⏳' : '🚀'}</span>
            <span>{building ? 'Syntetiserar fullstack-arkitektur...' : 'Starta Generering (0 frågor)'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default KickstartStudio;
