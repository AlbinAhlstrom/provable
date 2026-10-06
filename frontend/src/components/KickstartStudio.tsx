import React, { useState, useEffect } from 'react';
import { AppPreview } from './AppPreview';
import { WayfinderCanvas } from './WayfinderCanvas';

export interface KickstartStudioProps {
  onAppSynthesized?: () => void;
}

export interface ClarificationQuestion {
  id: string;
  question: string;
  category: string;
  options: string[];
  default_choice: string;
  impact_rationale: string;
}

export const KickstartStudio: React.FC<KickstartStudioProps> = ({ onAppSynthesized }) => {
  const [pitch, setPitch] = useState<string>('');
  const [mode, setMode] = useState<'fast' | 'guided'>('fast');
  const [activeStep, setActiveStep] = useState<'input' | 'clarify' | 'wayfinder'>('input');
  const [questions, setQuestions] = useState<ClarificationQuestion[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});

  const [building, setBuilding] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
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

  const triggerSynthesis = async (chosenAnswers?: Record<string, string>) => {
    setBuilding(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/kickstart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pitch: pitch.trim(),
          mode: mode,
          answers: chosenAnswers || selectedAnswers
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

  const handleLaunchWithMode = async (selectedMode: 'fast' | 'guided') => {
    if (!pitch.trim()) return;
    setMode(selectedMode);
    setAnalyzing(true);
    setResetMessage(null);

    try {
      const res = await fetch('/api/kickstart/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_pitch: pitch.trim(),
          mode: selectedMode
        })
      });
      const data = await res.json();

      const qList: ClarificationQuestion[] = data.clarification_questions || data?.data?.clarification_questions || [];

      if (qList.length > 0) {
        setQuestions(qList);
        const defaults: Record<string, string> = {};
        qList.forEach(q => {
          defaults[q.id] = q.default_choice || q.options[0] || '';
        });
        setSelectedAnswers(defaults);
        setActiveStep('clarify');
      } else {
        // Zero questions needed, proceed directly
        await triggerSynthesis();
      }
    } catch (err: any) {
      console.error("Analysis failed, falling back to direct synthesis:", err);
      await triggerSynthesis();
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectOption = (questionId: string, option: string) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: option
    }));
  };

  const handleResetAllProjects = async () => {
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/onboarding/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSynthesized(false);
        setActiveStep('input');
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

  // ── VIEW 1C: WAYFINDER ARCHITECTURAL RADAR STEP ─────────────────────────────
  if (activeStep === 'wayfinder') {
    return (
      <WayfinderCanvas
        pitch={pitch}
        onAppSynthesized={() => {
          setSynthesized(true);
          if (onAppSynthesized) onAppSynthesized();
        }}
        onBackToPitch={() => setActiveStep('input')}
      />
    );
  }

  // ── VIEW 1B: CLARIFICATION QUESTIONS STEP (ZERO FATIGUE) ───────────────────────
  if (activeStep === 'clarify') {
    return (
      <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1rem' }}>
        <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', border: '1px solid #334155', borderRadius: '1rem', padding: '2.5rem', marginBottom: '2rem', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '2rem' }}>🎯</span>
              <div>
                <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#f8fafc', fontWeight: 800 }}>
                  {mode === 'fast' ? '⚡ Snabbvalidering av Arkitektur' : '🎯 Guidad Arkitekturkonfiguration'}
                </h2>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#94a3b8' }}>
                  Ställningstaganden vid viktiga domän-vägskäl. Standardval är förmarkerade.
                </p>
              </div>
            </div>
            <button
              onClick={() => setActiveStep('input')}
              disabled={building}
              style={{
                background: 'transparent',
                border: '1px solid #475569',
                color: '#94a3b8',
                padding: '0.4rem 0.8rem',
                borderRadius: '0.5rem',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              ⬅ Ändra Pitch
            </button>
          </div>

          {/* Question Cards */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
            {questions.map((q, idx) => (
              <div
                key={q.id}
                style={{
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.75rem',
                  padding: '1.25rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '0.2rem 0.6rem', borderRadius: '9999px' }}>
                    {q.category || `Fråga ${idx + 1}`}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    Fråga {idx + 1} av {questions.length}
                  </span>
                </div>

                <h4 style={{ margin: '0.25rem 0 0.5rem 0', color: '#f8fafc', fontSize: '1.05rem', fontWeight: 600 }}>
                  {q.question}
                </h4>

                {q.impact_rationale && (
                  <p style={{ margin: '0 0 0.85rem 0', fontSize: '0.8rem', color: '#94a3b8', fontStyle: 'italic' }}>
                    💡 {q.impact_rationale}
                  </p>
                )}

                {/* Option Chips */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {q.options.map(opt => {
                    const isSelected = selectedAnswers[q.id] === opt;
                    const isDefault = q.default_choice === opt;
                    return (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => handleSelectOption(q.id, opt)}
                        disabled={building}
                        style={{
                          background: isSelected ? '#0284c7' : '#1e293b',
                          border: `1px solid ${isSelected ? '#38bdf8' : (isDefault ? '#475569' : '#334155')}`,
                          color: isSelected ? '#ffffff' : '#cbd5e1',
                          padding: '0.5rem 0.9rem',
                          borderRadius: '0.5rem',
                          fontSize: '0.85rem',
                          fontWeight: isSelected ? 700 : 500,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <span>{isSelected ? '✓' : (isDefault ? '⭐' : '○')}</span>
                        <span>{opt}</span>
                        {isDefault && !isSelected && (
                          <span style={{ fontSize: '0.7rem', color: '#94a3b8', marginLeft: '0.2rem' }}>(Standard)</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Action Row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <button
              onClick={() => setActiveStep('input')}
              disabled={building}
              style={{
                background: '#1e293b',
                color: '#94a3b8',
                border: '1px solid #475569',
                padding: '0.75rem 1.5rem',
                borderRadius: '9999px',
                fontWeight: 600,
                fontSize: '0.95rem',
                cursor: building ? 'not-allowed' : 'pointer'
              }}
            >
              ← Tillbaka till prompt
            </button>

            <button
              onClick={() => triggerSynthesis(selectedAnswers)}
              disabled={building}
              style={{
                background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
                color: '#ffffff',
                border: 'none',
                padding: '0.85rem 2rem',
                borderRadius: '9999px',
                fontWeight: 800,
                fontSize: '1.05rem',
                cursor: building ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem'
              }}
            >
              {building ? '⏳ Syntetiserar Domänarkitektur...' : '🚀 Syntetisera med valda inställningar'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── VIEW 1A: INITIAL DUAL-MODE PROMPT FORM ─────────────────────────────────────
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
                Beskriv helheten i 1–2 meningar. Välj snabbstart eller guidad arkitektur.
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

        {/* 3-Mode Action Buttons (Including Wayfinder Studio) */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.15fr 1fr', gap: '1rem' }}>
          {/* Quick Launch Button */}
          <button
            onClick={() => handleLaunchWithMode('fast')}
            disabled={building || analyzing || !pitch.trim()}
            style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              color: '#cbd5e1',
              border: '1px solid #334155',
              padding: '1rem 1.15rem',
              borderRadius: '0.75rem',
              fontWeight: 700,
              fontSize: '0.95rem',
              cursor: building || analyzing || !pitch.trim() ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              textAlign: 'left',
              gap: '0.25rem',
              opacity: !pitch.trim() ? 0.6 : 1,
              transition: 'transform 0.1s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 800, color: '#f8fafc' }}>
              <span>⚡</span>
              <span>Snabbstart</span>
              <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.1)', padding: '0.1rem 0.45rem', borderRadius: '9999px' }}>0 frågor</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 400 }}>
              {analyzing && mode === 'fast' ? 'Analyserar domän...' : (building ? 'Syntetiserar...' : 'Bygg direkt med intelligenta standardval')}
            </span>
          </button>

          {/* Wayfinder Studio Button (Flagship) */}
          <button
            onClick={() => setActiveStep('wayfinder')}
            disabled={building || analyzing || !pitch.trim()}
            style={{
              background: 'linear-gradient(135deg, #0284c7 0%, #1e1b4b 60%, #4338ca 100%)',
              color: '#ffffff',
              border: '1px solid #818cf8',
              padding: '1rem 1.15rem',
              borderRadius: '0.75rem',
              fontWeight: 700,
              fontSize: '0.95rem',
              cursor: building || analyzing || !pitch.trim() ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.35)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              textAlign: 'left',
              gap: '0.25rem',
              opacity: !pitch.trim() ? 0.6 : 1,
              transition: 'transform 0.1s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 800 }}>
              <span>🗺️</span>
              <span>Wayfinder Studio</span>
              <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.25)', padding: '0.1rem 0.45rem', borderRadius: '9999px', fontWeight: 800 }}>⭐ BDD Radar</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: '#e0e7ff', fontWeight: 400 }}>
              Kartlägg domänens vägskäl med Mad-Libs BDD innan kod genereras
            </span>
          </button>

          {/* Guided Co-Design Button */}
          <button
            onClick={() => handleLaunchWithMode('guided')}
            disabled={building || analyzing || !pitch.trim()}
            style={{
              background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
              color: '#f8fafc',
              border: '1px solid #334155',
              padding: '1rem 1.15rem',
              borderRadius: '0.75rem',
              fontWeight: 700,
              fontSize: '0.95rem',
              cursor: building || analyzing || !pitch.trim() ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-start',
              textAlign: 'left',
              gap: '0.25rem',
              opacity: !pitch.trim() ? 0.6 : 1,
              transition: 'transform 0.1s ease'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 800, color: '#38bdf8' }}>
              <span>🎯</span>
              <span>Guidad Arkitektur</span>
              <span style={{ fontSize: '0.7rem', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '0.1rem 0.45rem', borderRadius: '9999px' }}>Klassiskt formulär</span>
            </div>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontWeight: 400 }}>
              {analyzing && mode === 'guided' ? 'Genererar vägskäl...' : (building ? 'Syntetiserar...' : 'Frågeformulär före generering')}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default KickstartStudio;
