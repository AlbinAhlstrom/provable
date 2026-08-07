import React, { useState, useEffect } from 'react';
import { RequirementControlPanel } from './RequirementControlPanel';
import { AppPreview } from './AppPreview';

export interface KickstartStudioProps {
  onAppSynthesized?: () => void;
}

export const KickstartStudio: React.FC<KickstartStudioProps> = ({ onAppSynthesized }) => {
  const [pitch, setPitch] = useState<string>(
    'We operate a pizzeria. Customers place orders specified by pizza name, size, quantity, and price. The customer will get an estimated pickup time based on how many other orders have been made recently. The order is then marked Ready for pickup'
  );

  const [building, setBuilding] = useState<boolean>(false);
  const [resetting, setResetting] = useState<boolean>(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [synthesized, setSynthesized] = useState<boolean>(false);

  useEffect(() => {
    const checkState = async () => {
      try {
        const res = await fetch('/api/kickstart/state');
        const state = await res.json();
        if (state) {
          if (state.business_pitch) setPitch(state.business_pitch);
          if (typeof state.synthesized === 'boolean') setSynthesized(state.synthesized);
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
      // Step 1: Analyze pitch & get recommended blocks
      const analyzeRes = await fetch('/api/kickstart/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ business_pitch: pitch })
      });
      const analyzeData = await analyzeRes.json();
      
      const blocks = analyzeData?.data?.blocks || [];
      const selectedBlockIds = blocks.filter((b: any) => b.is_recommended || b.selected).map((b: any) => b.id);
      const reqs = analyzeData?.data?.extracted_requirements || [];

      // Step 2: Immediately synthesize full app stack
      const synthRes = await fetch('/api/kickstart/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_pitch: pitch,
          pitch: pitch,
          selected_blocks: selectedBlockIds.length > 0 ? selectedBlockIds : ['catalog_grid', 'shopping_cart', 'order_tracking'],
          selected_block_ids: selectedBlockIds.length > 0 ? selectedBlockIds : ['catalog_grid', 'shopping_cart', 'order_tracking'],
          requirements: reqs,
          extracted_requirements: reqs
        })
      });
      const synthData = await synthRes.json();
      if (synthData.success) {
        setSynthesized(true);
        setResetMessage("✨ Application built successfully!");
      } else {
        setResetMessage("⚠️ Synthesis notice: " + (synthData.error || 'Check backend logs'));
      }
    } catch (err) {
      console.error("Instant build failed:", err);
      setResetMessage("❌ Error building application stack.");
    } finally {
      setBuilding(false);
    }
  };

  const handleResetAllProjects = async () => {
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await fetch('/api/projects/reset-all', { method: 'POST' });
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
              <h2 style={{ margin: 0, fontSize: '1.75rem', color: '#f8fafc', fontWeight: 800 }}>Provable Kickstart Studio</h2>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#94a3b8' }}>Describe your application concept to instantly synthesize a verified DDD stack &amp; live UI.</p>
            </div>
          </div>

          <button
            onClick={handleResetAllProjects}
            disabled={resetting}
            style={{
              background: '#450a0a',
              border: '1px solid #991b1b',
              color: '#fca5a5',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: resetting ? 'not-allowed' : 'pointer',
              opacity: resetting ? 0.6 : 1
            }}
          >
            {resetting ? '⏳ Resetting...' : '🗑️ Reset Workspace'}
          </button>
        </div>

        {/* Status Toast */}
        {resetMessage && (
          <div style={{ background: resetMessage.includes('failed') || resetMessage.includes('error') ? '#450a0a' : '#064e3b', border: `1px solid ${resetMessage.includes('failed') || resetMessage.includes('error') ? '#991b1b' : '#047857'}`, color: resetMessage.includes('failed') || resetMessage.includes('error') ? '#fca5a5' : '#a7f3d0', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontWeight: 600 }}>
            {resetMessage}
          </div>
        )}

        {/* Prompt Input Area */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#f59e0b', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Describe What You Want To Build:
          </label>
          <textarea
            rows={4}
            value={pitch}
            onChange={e => setPitch(e.target.value)}
            disabled={building}
            placeholder="e.g. We operate a pizza delivery website with live tracking..."
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
            {building ? '⏳ Building DDD Stack & Live UI...' : '⚡ Build App Stack'}
          </button>
        </div>
      </div>

      {/* Domain Examples Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
        <div 
          onClick={() => setPitch('We operate a wood-fired pizzeria. Customers order by pizza name, size, quantity, and price. They receive a live estimated pickup time based on queue volume and track status from baking to ready for pickup.')}
          style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem', cursor: 'pointer' }}
        >
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🍕</div>
          <strong style={{ display: 'block', color: '#f8fafc', marginBottom: '0.25rem' }}>Artisanal Pizzeria</strong>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Menu customizer, dynamic pickup queue &amp; live tracking.</span>
        </div>

        <div 
          onClick={() => setPitch('Build an online furniture store where customers browse sofa and table inventory, add items to cart, select delivery date, and place orders with real-time stock allocation.')}
          style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem', cursor: 'pointer' }}
        >
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🛋️</div>
          <strong style={{ display: 'block', color: '#f8fafc', marginBottom: '0.25rem' }}>Furniture Store</strong>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Product catalog, cart, stock batch allocation &amp; delivery date.</span>
        </div>

        <div 
          onClick={() => setPitch('Create a hospital bed management system where staff view ward capacity, assign patients to beds, track discharge status, and monitor emergency room queue metrics.')}
          style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem', cursor: 'pointer' }}
        >
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🏥</div>
          <strong style={{ display: 'block', color: '#f8fafc', marginBottom: '0.25rem' }}>Hospital Operations</strong>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Ward bed assignment, patient queue &amp; occupancy metrics.</span>
        </div>
      </div>

    </div>
  );
};

export default KickstartStudio;
