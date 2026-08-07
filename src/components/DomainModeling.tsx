import React, { useState, useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface DomainModelingProps {
  onDomainSynthesized?: () => void;
}

  const [pitch, setPitch] = useState<string>(
    'An app to order pizzas'
  );

  const [loading, setLoading] = useState<boolean>(false);
  const [schema, setSchema] = useState<any>(null);
  const [diagramTab, setDiagramTab] = useState<'class' | 'sequence'>('class');
  const [synthesizing, setSynthesizing] = useState<boolean>(false);
  const [synthesizeResult, setSynthesizeResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const mermaidContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });
  }, []);

  useEffect(() => {
    if (!schema || !mermaidContainerRef.current) return;
    
    const diagramText = diagramTab === 'sequence' 
      ? (schema.mermaid_sequence_diagram || schema.mermaid_diagram)
      : (schema.mermaid_class_diagram || schema.mermaid_diagram);

    if (diagramText) {
      mermaidContainerRef.current.removeAttribute('data-processed');
      mermaidContainerRef.current.innerHTML = '';
      const id = 'mermaid-svg-' + Math.round(Math.random() * 10000);
      try {
        mermaid.render(id, diagramText).then(({ svg }) => {
          if (mermaidContainerRef.current) {
            mermaidContainerRef.current.innerHTML = svg;
          }
        }).catch(err => {
          console.error("Mermaid render error:", err);
          if (mermaidContainerRef.current) {
            mermaidContainerRef.current.innerHTML = `<pre class="mermaid-fallback">${diagramText}</pre>`;
          }
        });
      } catch (e) {
        console.error("Mermaid error:", e);
      }
    }
  }, [schema, diagramTab]);

  const handleSynthesize = async (targetSchema?: any) => {
    const s = targetSchema || schema;
    if (!s) return;
    setSynthesizing(true);
    setError(null);
    try {
      const res = await fetch('/api/domain/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain_schema: s })
      });
      const data = await res.json().catch(() => ({ success: false, error: `HTTP ${res.status} ${res.statusText}` }));
      if (data.success) {
        setSynthesizeResult(data);
        if (onDomainSynthesized) onDomainSynthesized();
      } else {
        setError(data.error || "Failed to synthesize domain code.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "Network error synthesizing domain code.");
    } finally {
      setSynthesizing(false);
    }
  };

  const handleDiscover = async () => {
    if (!pitch.trim()) return;
    setLoading(true);
    setError(null);
    setSynthesizeResult(null);
    try {
      const res = await fetch('/api/domain/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ business_pitch: pitch })
      });
      const data = await res.json().catch(() => ({ success: false, error: `HTTP ${res.status} ${res.statusText}` }));
      if (data.success) {
        setSchema(data.data);
        await handleSynthesize(data.data);
      } else {
        setError(data.error || data.raw || "Failed to analyze domain pitch.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "Network error running domain discovery.");
    } finally {
      setLoading(false);
    }
  };

  const [resetting, setResetting] = useState<boolean>(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  const handleResetAllProjects = async () => {
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/projects/reset-all', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setSchema(null);
        setSynthesizeResult(null);
        if (onDomainSynthesized) await onDomainSynthesized();
        setResetMessage("✨ Active projects and workspace wiped successfully.");
        setTimeout(() => setResetMessage(null), 3000);
      } else {
        setResetMessage("⚠️ Reset failed: " + data.error);
      }
    } catch (err) {
      console.error(err);
      setResetMessage("❌ Network error resetting projects.");
    } finally {
      setResetting(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem', maxWidth: '1250px', margin: '0 auto', color: '#e2e8f0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: 0, color: '#38bdf8' }}>
            🌌 Universal Domain Discovery Engine (DDD)
          </h1>
          <p style={{ margin: '0.25rem 0 0 0', color: '#94a3b8', fontSize: '0.9rem' }}>
            Transform natural language business pitches into complete 6-part DDD Domain Models, interactive UML & Sequence diagrams, and Low-Gear TDD test suites.
          </p>
        </div>
        <button
          onClick={handleResetAllProjects}
          disabled={resetting}
          className="btn btn-outline"
          style={{ borderColor: '#ef4444', color: '#f87171', fontSize: '0.85rem', opacity: resetting ? 0.6 : 1 }}
        >
          {resetting ? '⏳ Resetting Workspace...' : '🗑️ Reset All Active Projects'}
        </button>
      </div>

      {resetMessage && (
        <div style={{ background: resetMessage.includes('failed') || resetMessage.includes('error') ? '#450a0a' : '#064e3b', border: `1px solid ${resetMessage.includes('failed') || resetMessage.includes('error') ? '#991b1b' : '#047857'}`, color: resetMessage.includes('failed') || resetMessage.includes('error') ? '#fca5a5' : '#a7f3d0', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontWeight: 600 }}>
          {resetMessage}
        </div>
      )}

      {error && (
        <div style={{ background: '#450a0a', border: '1px solid #991b1b', color: '#fca5a5', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1.5rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Raw Business Pitch Input Area */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.25rem', marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', fontWeight: 600, marginBottom: '0.5rem', color: '#f1f5f9' }}>
          Raw Business Description / Domain Pitch:
        </label>
        <textarea
          rows={4}
          disabled={!!schema || loading || synthesizing}
          style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.95rem', fontFamily: 'inherit', resize: 'vertical', opacity: schema ? 0.7 : 1 }}
          value={pitch}
          onChange={e => setPitch(e.target.value)}
          placeholder="Describe your application domain in natural language..."
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.75rem', alignItems: 'center' }}>
          <button
            type="button"
            onClick={() => setPitch('An app to order pizzas')}
          >
            📋 Load Pizzeria Benchmark Pitch

          </button>
          <button
            onClick={handleDiscover}
            disabled={loading || synthesizing || !!schema}
            style={{ background: schema ? '#16a34a' : '#0284c7', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '0.5rem', fontWeight: 600, cursor: (loading || synthesizing || !!schema) ? 'not-allowed' : 'pointer', fontSize: '0.95rem', opacity: (loading || synthesizing) ? 0.7 : 1 }}
          >
            {loading ? '⚡ Discovering Domain Model...' : synthesizing ? '⚙️ Synthesizing Stack & Tests...' : schema ? '✅ Domain & Stack Synthesized' : '⚡ Discover & Synthesize Application Stack'}
          </button>
        </div>
      </div>

      {/* Synthesis Completion Banner */}
      {synthesizeResult && (
        <div style={{ marginBottom: '1.5rem', background: '#064e3b', border: '1px solid #059669', padding: '1rem 1.25rem', borderRadius: '0.75rem', color: '#a7f3d0' }}>
          <strong style={{ fontSize: '1rem' }}>✅ Domain & Application Stack Synthesized!</strong>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.9rem', color: '#6ee7b7' }}>
            Synthesized pure domain code in <code>src/domain/model.py</code>, SQLAlchemy ORM & Unit of Work, FastAPI REST endpoints, and live React UI application preview on port 5174. To synthesize a new pitch, click <strong>🗑️ Reset All Active Projects</strong> above.
          </p>
        </div>
      )}

      {/* Discovered Domain Specification Canvas */}
      {schema && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
          {/* Left Column: Mermaid Class & Sequence Diagram Canvas with Tab Toggle */}
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.25rem', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 600, margin: 0, color: '#38bdf8' }}>
                📊 Visual Diagram Studio
              </h2>
              <div style={{ display: 'flex', gap: '0.5rem', background: '#0f172a', padding: '0.2rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
                <button
                  style={{ background: diagramTab === 'class' ? '#0284c7' : 'transparent', color: '#fff', border: 'none', padding: '0.3rem 0.75rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600 }}
                  onClick={() => setDiagramTab('class')}
                >
                  📊 Class Diagram (UML)
                </button>
                <button
                  style={{ background: diagramTab === 'sequence' ? '#0284c7' : 'transparent', color: '#fff', border: 'none', padding: '0.3rem 0.75rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 600 }}
                  onClick={() => setDiagramTab('sequence')}
                >
                  🔄 Sequence Diagram (Flow)
                </button>
              </div>
            </div>

            <div
              ref={mermaidContainerRef}
              style={{ background: '#0f172a', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #334155', minHeight: '350px', flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'auto' }}
            />
          </div>

          {/* Right Column: 6-Part DDD Domain Specification */}
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '550px', overflowY: 'auto' }}>
            
            {/* 1. Ubiquitous Language Glossary */}
            {schema.ubiquitous_language && (
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#c084fc' }}>
                  📖 Ubiquitous Language Glossary
                </h3>
                <div style={{ background: '#0f172a', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #334155', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  {Object.entries(schema.ubiquitous_language).map(([term, def]: any, i: number) => (
                    <div key={i}>
                      <strong style={{ color: '#e9d5ff' }}>{term}:</strong> <span style={{ color: '#cbd5e1' }}>{def}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 2. Value Objects */}
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#67e8f9' }}>
                💎 Value Objects (Immutable)
              </h3>
              <div style={{ background: '#0f172a', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #334155', fontSize: '0.8rem' }}>
                {schema.value_objects?.map((vo: any, i: number) => (
                  <div key={i} style={{ marginBottom: '0.25rem' }}>
                    <strong style={{ color: '#22d3ee' }}>{vo.name}</strong>: <code>{JSON.stringify(vo.fields)}</code>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. Entities */}
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#fef08a' }}>
                🏛️ Entities (Identity-Based)
              </h3>
              <div style={{ background: '#0f172a', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #334155', fontSize: '0.8rem' }}>
                {schema.entities?.map((ent: any, i: number) => (
                  <div key={i} style={{ marginBottom: '0.35rem' }}>
                    <strong style={{ color: '#fde047' }}>{ent.name}</strong> (Identity: <code>{ent.identity_key}</code>)
                    <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
                      Methods: {ent.methods?.map((m: any) => m.name).join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Domain Services */}
            {schema.domain_services && (
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#fb923c' }}>
                  ⚡ Domain Services & Functions
                </h3>
                <div style={{ background: '#0f172a', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #334155', fontSize: '0.8rem' }}>
                  {schema.domain_services.map((ds: any, i: number) => (
                    <div key={i} style={{ marginBottom: '0.25rem' }}>
                      <strong style={{ color: '#fdba74' }}>{ds.name}</strong>(<code>{JSON.stringify(ds.params)}</code>) &rarr; <code>{ds.return_type}</code>
                      <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{ds.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 5. Domain Exceptions */}
            {schema.domain_exceptions && (
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#f87171' }}>
                  🚨 Domain Exceptions
                </h3>
                <div style={{ background: '#0f172a', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #334155', fontSize: '0.8rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {schema.domain_exceptions.map((ex: any, i: number) => (
                    <span key={i} style={{ background: '#450a0a', border: '1px solid #991b1b', color: '#fca5a5', padding: '0.2rem 0.5rem', borderRadius: '0.35rem' }}>
                      <code>{ex.name}</code>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 6. Business Invariants */}
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: '0 0 0.4rem 0', color: '#a7f3d0' }}>
                🛡️ Business Invariants
              </h3>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.8rem', color: '#cbd5e1' }}>
                {schema.invariants?.map((inv: any, i: number) => (
                  <li key={i} style={{ marginBottom: '0.25rem' }}>
                    <strong style={{ color: '#4ade80' }}>{inv.id}:</strong> {inv.rule}
                  </li>
                ))}
              </ul>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default DomainModeling;
