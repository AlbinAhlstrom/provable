import React, { useState, useEffect } from 'react';
import { ComponentAddRequestDTO, ComponentDeleteRequestDTO } from '../types/api';

export interface ComponentItem {
  id: string;
  canonical_key: string;
  name: string;
  reqId: string;
  icon: string;
  desc: string;
  component_type: 'premade' | 'custom';
  sub_requirements?: any[];
}

export interface RequirementControlPanelProps {
  fullWidth?: boolean;
  onParamUpdated?: () => void;
}

export const RequirementControlPanel: React.FC<RequirementControlPanelProps> = ({ fullWidth = false, onParamUpdated }) => {
  const [components, setComponents] = useState<ComponentItem[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([
    "Flappy bird game",
    "Payment system",
    "Loyalty points & rewards"
  ]);
  const [newPrompt, setNewPrompt] = useState<string>("");
  const [addingComponent, setAddingComponent] = useState<boolean>(false);
  const [addingPromptText, setAddingPromptText] = useState<string>("");
  const [deletingKey, setDeletingKey] = useState<string | null>(null);
  const [statusToast, setStatusToast] = useState<string | null>(null);

  const hydrateData = async () => {
    try {
      // 1. Fetch requirements from SQLite store via backend API
      const reqRes = await fetch('/api/requirements');
      const reqs = await reqRes.json();

      if (Array.isArray(reqs)) {
        // Filter out brand/sla and disabled items, build active list
        const activeItems: ComponentItem[] = reqs
          .filter((r: any) => r.id && r.status !== 'Disabled' && !r.id.startsWith('REQ-BRAND') && !r.id.startsWith('REQ-DELIVERY') && !r.id.startsWith('REQ-SUB') && !r.parentId && !r.parent_id)
          .map((r: any) => {
            const canonicalKey = extractCanonicalKey(r);
            const compType = r.component_type || (['catalog', 'cart', 'tracking', 'kds', 'reviews', 'auth', 'calendar'].includes(canonicalKey) ? 'premade' : 'custom');
            return {
              id: canonicalKey,
              canonical_key: canonicalKey,
              name: formatComponentName(r.title || canonicalKey),
              reqId: r.id,
              icon: getComponentIcon(canonicalKey, r.title || ''),
              desc: r.description || 'Active application component',
              component_type: compType,
              sub_requirements: r.sub_requirements
            };
          });

        // Deduplicate by canonical_key
        const uniqueItems: ComponentItem[] = [];
        const seen = new Set<string>();
        for (const item of activeItems) {
          if (!seen.has(item.canonical_key)) {
            seen.add(item.canonical_key);
            uniqueItems.push(item);
          }
        }
        setComponents(uniqueItems);
      }

      // 2. Fetch dynamic suggestions
      const sugRes = await fetch('/api/components/suggestions');
      const sugData = await sugRes.json();
      if (sugData && Array.isArray(sugData.suggestions) && sugData.suggestions.length > 0) {
        setSuggestions(sugData.suggestions.slice(0, 3));
      }
    } catch (e) {
      console.error("Hydration error in RequirementControlPanel:", e);
    }
  };

  useEffect(() => {
    hydrateData();
  }, []);

  const handleAddComponent = async (promptToAdd?: string) => {
    const promptText = (promptToAdd || newPrompt).trim();
    if (!promptText) return;

    setAddingComponent(true);
    setAddingPromptText(promptText);
    setStatusToast(`⚡ Synthesizing component for "${promptText}"...`);

    const payload: ComponentAddRequestDTO = {
      prompt: promptText,
      component_type: 'custom'
    };

    try {
      const res = await fetch('/api/components/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`✨ Added component: "${promptText}"`);
        setNewPrompt("");
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        setStatusToast(`⚠️ Notice: ${data.error || 'Could not add component'}`);
      }
    } catch (err) {
      console.error("Error adding component:", err);
      setStatusToast(`❌ Network error adding component.`);
    } finally {
      setAddingComponent(false);
      setAddingPromptText("");
      setTimeout(() => setStatusToast(null), 3500);
    }
  };

  const handleDeleteComponent = async (canonicalKey: string, componentName: string) => {
    setDeletingKey(canonicalKey);
    setStatusToast(`🗑️ Deleting ${componentName}...`);

    const payload: ComponentDeleteRequestDTO = {
      canonical_key: canonicalKey
    };

    try {
      const res = await fetch('/api/components/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`✨ Deleted ${componentName}`);
        setComponents(prev => prev.filter(c => c.canonical_key !== canonicalKey));
        if (onParamUpdated) onParamUpdated();
      } else {
        setStatusToast(`⚠️ Notice: ${data.error || 'Could not delete component'}`);
      }
    } catch (err) {
      console.error("Error deleting component:", err);
      setStatusToast(`❌ Network error deleting component.`);
    } finally {
      setDeletingKey(null);
      setTimeout(() => setStatusToast(null), 3000);
    }
  };

  return (
    <div style={{
      background: fullWidth ? 'transparent' : '#1e293b',
      borderLeft: fullWidth ? 'none' : '1px solid #334155',
      width: fullWidth ? '100%' : '380px',
      height: '100%',
      overflowY: 'auto',
      padding: fullWidth ? '0' : '1.25rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem',
      color: '#f8fafc'
    }}>

      {/* Status Toast */}
      {statusToast && (
        <div style={{ background: 'rgba(2, 132, 199, 0.2)', border: '1px solid #0284c7', color: '#38bdf8', padding: '0.65rem 1rem', borderRadius: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}>
          {statusToast}
        </div>
      )}

      {/* ACTIVE COMPONENTS SECTION */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ margin: 0, fontSize: '0.9rem', color: '#cbd5e1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
            Active Components ({components.length})
          </h4>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Dynamic Canvas</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: fullWidth ? 'repeat(2, 1fr)' : '1fr', gap: '0.75rem' }}>
          {components.map((item) => (
            <div
              key={item.canonical_key}
              style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '0.75rem',
                padding: '0.85rem 1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.75rem',
                opacity: deletingKey === item.canonical_key ? 0.5 : 1
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                  <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                  <strong style={{ fontSize: '0.9rem', color: '#f8fafc' }}>{item.name}</strong>
                  {item.component_type === 'custom' && (
                    <span style={{ background: '#3b82f622', color: '#60a5fa', border: '1px solid #3b82f644', fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '9999px', fontWeight: 600 }}>
                      Custom
                    </span>
                  )}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', lineHeight: 1.3 }}>{item.desc}</div>

                {/* Dynamic Sub-Requirements List */}
                {item.sub_requirements && item.sub_requirements.length > 0 && (
                  <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #334155' }}>
                    <div style={{ fontSize: '0.7rem', color: '#cbd5e1', fontWeight: 700, marginBottom: '0.3rem', textTransform: 'uppercase' }}>
                      Child Sub-Requirements:
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {item.sub_requirements.map((sub: any, idx: number) => (
                        <div key={idx} style={{ background: '#0284c722', border: '1px solid #0284c744', borderRadius: '0.35rem', padding: '0.25rem 0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#38bdf8' }}>
                          <span>{sub.title || sub.name}</span>
                          <span style={{ fontSize: '0.65rem', opacity: 0.8 }}>Nested</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Permanent Delete Button */}
              <button
                onClick={() => handleDeleteComponent(item.canonical_key, item.name)}
                disabled={deletingKey === item.canonical_key}
                title="Permanently remove component"
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#f87171',
                  borderRadius: '0.5rem',
                  padding: '0.4rem 0.6rem',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  transition: 'all 0.2s ease'
                }}
              >
                {deletingKey === item.canonical_key ? '⏳' : '🗑️'}
              </button>
            </div>
          ))}

          {/* Progressive Feedback Loader Card when adding a component */}
          {addingComponent && (
            <div style={{
              background: '#0f172a',
              border: '1px dashed #0284c7',
              borderRadius: '0.75rem',
              padding: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              color: '#38bdf8'
            }}>
              <div style={{ fontSize: '1.5rem' }}>⚡</div>
              <div>
                <strong style={{ display: 'block', fontSize: '0.85rem', color: '#f8fafc' }}>
                  Generating "{addingPromptText}"...
                </strong>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Synthesizing code &amp; linking BDD test suite</span>
              </div>
            </div>
          )}
        </div>

        {components.length === 0 && !addingComponent && (
          <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.5rem', textAlign: 'center' }}>
            <p style={{ color: '#64748b', margin: 0, fontSize: '0.85rem' }}>
              No active components. Use the prompt field below to add standard or custom components.
            </p>
          </div>
        )}
      </div>

      {/* DYNAMIC PROMPT INPUT & DOMAIN SUGGESTIONS */}
      <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <h4 style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
          ➕ Add Dynamic Component
        </h4>

        {/* Input Form */}
        <form onSubmit={(e) => { e.preventDefault(); handleAddComponent(); }} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            value={newPrompt}
            onChange={(e) => setNewPrompt(e.target.value)}
            disabled={addingComponent}
            placeholder="e.g. Flappy bird game, payment system..."
            style={{
              flex: 1,
              background: '#1e293b',
              border: '1px solid #475569',
              color: '#ffffff',
              padding: '0.55rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={addingComponent || !newPrompt.trim()}
            style={{
              background: (addingComponent || !newPrompt.trim()) ? '#334155' : '#0284c7',
              color: (addingComponent || !newPrompt.trim()) ? '#94a3b8' : '#ffffff',
              border: 'none',
              padding: '0.55rem 0.9rem',
              borderRadius: '0.5rem',
              fontWeight: 700,
              fontSize: '0.85rem',
              cursor: (addingComponent || !newPrompt.trim()) ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            {addingComponent ? 'Building...' : 'Add'}
          </button>
        </form>

        {/* Domain Suggestions Chips */}
        {suggestions.length > 0 && (
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginBottom: '0.4rem', fontWeight: 600 }}>
              💡 Suggested Prompts:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {suggestions.map((chipText, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setNewPrompt(chipText);
                    handleAddComponent(chipText);
                  }}
                  disabled={addingComponent}
                  style={{
                    background: '#1e293b',
                    border: '1px solid #334155',
                    color: '#38bdf8',
                    borderRadius: '9999px',
                    padding: '0.25rem 0.65rem',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: addingComponent ? 'not-allowed' : 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  + {chipText}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

// Helper: Extract canonical key from requirement object or title
function extractCanonicalKey(r: any): string {
  const clean = (r.id || r.title || '').toLowerCase().replace(/[^a-z0-9]/g, '_');
  if (clean.includes('catalog') || clean.includes('menu')) return 'catalog';
  if (clean.includes('cart') || clean.includes('checkout')) return 'cart';
  if (clean.includes('track') || clean.includes('pipeline')) return 'tracking';
  if (clean.includes('dashboard') || clean.includes('admin') || clean.includes('kds')) return 'kds';
  if (clean.includes('review') || clean.includes('rating')) return 'reviews';
  if (clean.includes('auth') || clean.includes('user') || clean.includes('profile')) return 'auth';
  if (clean.includes('calendar') || clean.includes('booking') || clean.includes('schedule')) return 'calendar';
  
  // Custom requirement key extraction
  return clean.replace(/^req_cmp_/, '').replace(/^req_/, '').replace(/_001$/, '');
}

// Helper: Pick icon for component
function getComponentIcon(canonicalKey: string, title: string): string {
  const k = canonicalKey.toLowerCase();
  if (k.includes('calendar') || k.includes('booking')) return '📅';
  if (k.includes('catalog') || k.includes('menu')) return '📋';
  if (k.includes('cart') || k.includes('checkout')) return '🛒';
  if (k.includes('track') || k.includes('pipeline')) return '📦';
  if (k.includes('dashboard') || k.includes('admin') || k.includes('kds')) return '🏪';
  if (k.includes('review') || k.includes('rating')) return '⭐';
  if (k.includes('auth') || k.includes('user') || k.includes('profile')) return '👤';
  if (k.includes('game') || k.includes('bird')) return '🎮';
  if (k.includes('pay') || k.includes('payment')) return '💳';
  return '🧩';
}

// Helper: Format component name
function formatComponentName(rawName: string): string {
  const map: Record<string, string> = {
    'catalog': 'Product & Menu Catalog',
    'cart': 'Shopping Cart & Checkout',
    'tracking': 'Live Status Pipeline',
    'kds': 'Merchant Operations Dashboard',
    'reviews': 'Reviews & Ratings',
    'auth': 'Customer Auth & Profiles',
    'calendar': 'Appointment Calendar'
  };
  if (map[rawName]) return map[rawName];
  const clean = rawName.replace(/^Dynamic Component:\s*/i, '').replace(/^Capability Block\s*/i, '').replace(/\s*Active$/i, '');
  return clean.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
