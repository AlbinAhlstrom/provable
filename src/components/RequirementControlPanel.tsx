// PM Studio Requirement Control Panel — Component Inspector & Spec Tree
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

const getTestPlaceholder = (key: string) => {
  const k = key.toLowerCase();
  if (k.includes('cart')) return 'e.g. When item added, update subtotal & badge count...';
  if (k.includes('catalog') || k.includes('menu')) return 'e.g. Given item selected, add to shopping cart...';
  if (k.includes('track') || k.includes('status')) return 'e.g. Given active order, display live pickup ETA...';
  if (k.includes('check')) return 'e.g. When payment submitted, clear cart & show receipt...';
  return 'e.g. Given user action, when event occurs, then update state...';
};

const handleInsertBddPrefix = (value: string) => {
  const prefixes = ['Given', 'When', 'Then'];
  const words = value.trim().split(' ');
  if (words.length > 0 && prefixes.includes(words[0])) return value;
  return `Given ${value}`;
};

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
  const [expandedComponents, setExpandedComponents] = useState<Set<string>>(new Set());
  const [subPromptByComponent, setSubPromptByComponent] = useState<Record<string, string>>({});
  const [addingSubKey, setAddingSubKey] = useState<string | null>(null);

  // 2-Tab Component Inspector State ('tests' | 'data')
  const [activeTabByComponent, setActiveTabByComponent] = useState<Record<string, 'tests' | 'data'>>({});

  // Entity Data Fixtures State with default seed items
  const [dataFixturesByComponent, setDataFixturesByComponent] = useState<Record<string, Array<{ id: string, name: string, price: number }>>>({
    catalog: [
      { id: 'item-1', name: 'Margherita Pizza', price: 14.99 },
      { id: 'item-2', name: 'Pepperoni Supreme', price: 16.99 },
      { id: 'item-3', name: 'Truffle Mushroom Deluxe', price: 18.99 }
    ],
    cart: [
      { id: 'cart-1', name: 'Standard Delivery Tax', price: 2.99 }
    ],
    tracking: [
      { id: 'track-1', name: 'Order ORD-9021 (Baking)', price: 31.98 }
    ]
  });

  // Entity Fixture Inline Editing State
  const [editingFixtureId, setEditingFixtureId] = useState<string | null>(null);
  const [editFixtureName, setEditFixtureName] = useState<string>('');
  const [editFixturePrice, setEditFixturePrice] = useState<string>('');
  const [newFixtureName, setNewFixtureName] = useState<Record<string, string>>({});
  const [newFixturePrice, setNewFixturePrice] = useState<Record<string, string>>({});

  const toggleComponentTab = (key: string, tab: 'tests' | 'data') => {
    setActiveTabByComponent(prev => ({ ...prev, [key]: tab }));
  };

  const handleAddFixture = (canonicalKey: string) => {
    const name = (newFixtureName[canonicalKey] || '').trim();
    const priceVal = parseFloat(newFixturePrice[canonicalKey] || '14.99');
    if (!name) return;

    const newItem = {
      id: `fix-${Date.now()}`,
      name,
      price: isNaN(priceVal) ? 14.99 : priceVal
    };

    setDataFixturesByComponent(prev => ({
      ...prev,
      [canonicalKey]: [...(prev[canonicalKey] || []), newItem]
    }));

    setNewFixtureName(prev => ({ ...prev, [canonicalKey]: '' }));
    setNewFixturePrice(prev => ({ ...prev, [canonicalKey]: '' }));
    setStatusToast(`✨ Added entity item "${name}" to ${canonicalKey}`);
    setTimeout(() => setStatusToast(null), 2500);
  };

  const handleSaveFixtureEdit = (canonicalKey: string, fixId: string) => {
    if (!editFixtureName.trim()) return;
    const priceVal = parseFloat(editFixturePrice);

    setDataFixturesByComponent(prev => ({
      ...prev,
      [canonicalKey]: (prev[canonicalKey] || []).map(item =>
        item.id === fixId
          ? { ...item, name: editFixtureName.trim(), price: isNaN(priceVal) ? item.price : priceVal }
          : item
      )
    }));

    setEditingFixtureId(null);
    setStatusToast(`✨ Updated entity item`);
    setTimeout(() => setStatusToast(null), 2000);
  };

  const handleDeleteFixture = (canonicalKey: string, fixId: string) => {
    setDataFixturesByComponent(prev => ({
      ...prev,
      [canonicalKey]: (prev[canonicalKey] || []).filter(item => item.id !== fixId)
    }));
    setStatusToast(`🗑️ Deleted entity item`);
    setTimeout(() => setStatusToast(null), 2000);
  };


  const toggleComponentExpand = (key: string) => {
    setExpandedComponents(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const hydrateData = async () => {
    try {
      // 1. Fetch requirements from SQLite store via backend API
      const reqRes = await fetch('/api/requirements');
      const reqs = await reqRes.json();

      if (Array.isArray(reqs)) {
        // Filter out non-UI items (like DB persistence rules or domain invariants), build active presentation list
        const activeItems: ComponentItem[] = reqs
          .filter((r: any) => r.id && r.status !== 'Disabled' && !r.parentId && !r.parent_id && (r.layer === 'PRESENTATION' || r.id.startsWith('REQ-UI') || r.id.startsWith('REQ-COMP') || ['catalog', 'cart', 'tracking', 'menu', 'customizer'].includes(extractCanonicalKey(r))))
          .map((r: any) => {
            const canonicalKey = extractCanonicalKey(r);
            const compType = r.component_type || (['catalog', 'cart', 'tracking', 'kds', 'reviews', 'auth', 'calendar'].includes(canonicalKey) ? 'premade' : 'custom');
            const subReqs = reqs.filter((child: any) => {
              const pId = child.parentId || child.parent_id;
              if (!pId) return false;
              return pId === r.id || pId === canonicalKey || pId.toLowerCase().includes(canonicalKey);
            });
            return {
              id: canonicalKey,
              canonical_key: canonicalKey,
              name: formatComponentName(r.title || canonicalKey),
              reqId: r.id,
              icon: getComponentIcon(canonicalKey, r.title || ''),
              desc: r.description || 'Active application component',
              component_type: compType,
              sub_requirements: subReqs.length > 0 ? subReqs : (r.sub_requirements || [])
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

        // Auto-expand all component nodes by default
        if (expandedComponents.size === 0 && uniqueItems.length > 0) {
          setExpandedComponents(new Set(uniqueItems.map(i => i.canonical_key)));
        }
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

  const handleAddSubRequirement = async (canonicalKey: string) => {
    const text = (subPromptByComponent[canonicalKey] || '').trim();
    if (!text) return;

    setAddingSubKey(canonicalKey);
    setStatusToast(`➕ Adding sub-requirement to ${canonicalKey}...`);

    try {
      const res = await fetch('/api/components/sub-requirements/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_canonical_key: canonicalKey,
          prompt: text
        })
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`✨ Added sub-requirement to ${canonicalKey}`);
        setSubPromptByComponent(prev => ({ ...prev, [canonicalKey]: '' }));
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        setStatusToast(`⚠️ Notice: ${data.error || 'Could not add sub-requirement'}`);
      }
    } catch (err) {
      console.error("Error adding sub-requirement:", err);
      setStatusToast(`❌ Network error adding sub-requirement.`);
    } finally {
      setAddingSubKey(null);
      setTimeout(() => setStatusToast(null), 3500);
    }
  };

  const handleDeleteSubRequirement = async (canonicalKey: string, subId: string) => {
    setStatusToast(`🗑️ Deleting sub-requirement...`);
    try {
      const res = await fetch('/api/components/sub-requirements/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_canonical_key: canonicalKey,
          sub_id: subId
        })
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`✨ Deleted sub-requirement`);
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        setStatusToast(`⚠️ Notice: ${data.error || 'Could not delete sub-requirement'}`);
      }
    } catch (err) {
      console.error("Error deleting sub-requirement:", err);
      setStatusToast(`❌ Network error deleting sub-requirement.`);
    } finally {
      setTimeout(() => setStatusToast(null), 3000);
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
      flex: 1,
      minWidth: 0,
      width: '100%',
      height: '100%',
      overflowY: 'auto',
      overflowX: 'hidden',
      padding: fullWidth ? '0' : '1.25rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem',
      color: '#f8fafc',
      boxSizing: 'border-box'
    }}>

      {/* Status Toast */}
      {statusToast && (
        <div style={{ background: 'rgba(2, 132, 199, 0.2)', border: '1px solid #0284c7', color: '#38bdf8', padding: '0.65rem 1rem', borderRadius: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}>
          {statusToast}
        </div>
      )}

      {/* COMPONENTS SECTION */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ margin: 0, fontSize: '0.9rem', color: '#cbd5e1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
            Components
          </h4>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: fullWidth ? 'repeat(2, 1fr)' : '1fr', gap: '0.75rem' }}>
          {components.map((item) => {
            const isExpanded = expandedComponents.has(item.canonical_key);
            const subCount = (item.sub_requirements || []).length;

            return (
              <div
                key={item.canonical_key}
                style={{
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '0.75rem',
                  padding: '0.85rem 1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.65rem',
                  opacity: deletingKey === item.canonical_key ? 0.5 : 1
                }}
              >
                {/* Node Header Bar */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                  <div 
                    onClick={() => toggleComponentExpand(item.canonical_key)} 
                    style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}
                  >
                    <span style={{ fontSize: '0.8rem', color: '#94a3b8', width: '16px' }}>
                      {isExpanded ? '▼' : '▶'}
                    </span>
                    <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                    <strong style={{ fontSize: '0.9rem', color: '#f8fafc' }}>{item.name}</strong>
                  </div>

                  {/* Component Delete Button */}
                  <button
                    onClick={() => handleDeleteComponent(item.canonical_key, item.name)}
                    disabled={deletingKey === item.canonical_key}
                    title="Permanently remove component"
                    style={{
                      background: 'rgba(239, 68, 68, 0.1)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#f87171',
                      borderRadius: '0.5rem',
                      padding: '0.3rem 0.5rem',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {deletingKey === item.canonical_key ? '⏳' : '🗑️'}
                  </button>
                </div>

                {/* Collapsible Node Body */}
                {isExpanded && (
                  <div style={{ marginTop: '0.25rem', paddingTop: '0.5rem', borderTop: '1px solid #1e293b', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8', lineHeight: 1.35 }}>{item.desc}</div>

                      {/* 2-TAB INSPECTOR SWITCHER: 🧪 Tests vs 📦 Data Fixtures */}
                      <div style={{ display: 'flex', background: '#090d16', border: '1px solid #334155', borderRadius: '0.4rem', padding: '0.15rem' }}>
                        <button
                          onClick={() => toggleComponentTab(item.canonical_key, 'tests')}
                          style={{
                            flex: 1,
                            background: (activeTabByComponent[item.canonical_key] || 'tests') === 'tests' ? '#0284c7' : 'transparent',
                            color: (activeTabByComponent[item.canonical_key] || 'tests') === 'tests' ? '#ffffff' : '#94a3b8',
                            border: 'none',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '0.3rem',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          🧪 Executable Tests ({subCount})
                        </button>

                      <button
                        onClick={() => toggleComponentTab(item.canonical_key, 'data')}
                        style={{
                          flex: 1,
                          background: activeTabByComponent[item.canonical_key] === 'data' ? '#0284c7' : 'transparent',
                          color: activeTabByComponent[item.canonical_key] === 'data' ? '#ffffff' : '#94a3b8',
                          border: 'none',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.3rem',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        📦 Data Fixtures ({(dataFixturesByComponent[item.canonical_key] || []).length})
                      </button>
                    </div>

                    {/* TAB 1: EXECUTABLE TESTS */}
                    {(activeTabByComponent[item.canonical_key] || 'tests') === 'tests' && (
                      <>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                          {(!item.sub_requirements || item.sub_requirements.length === 0) ? (
                            <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
                              No test specs defined yet. Use the field below to add a test assertion.
                            </div>
                          ) : (
                            item.sub_requirements.map((sub: any, idx: number) => {
                              const subId = sub.id || sub.canonical_key || `sub-${idx}`;
                              const subTitle = sub.title || sub.name || sub.description || 'Test Spec';
                              const status = sub.status === 'fail' ? 'fail' : 'pass';
                              const testBadge = status === 'pass' ? '🟢 PASS' : '🔴 FAIL';
                              const testsArr = sub.tests || [];
                              const firstTest = testsArr[0] || {};
                              const givenText = firstTest.given || sub.given_text;
                              const whenText = firstTest.when || sub.when_text;
                              const thenText = firstTest.then || sub.then_text;

                              return (
                                <div 
                                  key={subId} 
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
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flex: 1 }}>
                                      <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '4px', background: status === 'pass' ? '#166534' : '#991b1b', color: status === 'pass' ? '#4ade80' : '#fca5a5', fontWeight: 700 }}>
                                        {testBadge}
                                      </span>
                                      <strong style={{ fontSize: '0.8rem', color: '#f8fafc' }}>{subTitle}</strong>
                                    </div>
                                    <button
                                      onClick={() => handleDeleteSubRequirement(item.canonical_key, subId)}
                                      title="Delete test spec"
                                      style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem', padding: '0.1rem' }}
                                    >
                                      🗑️
                                    </button>
                                  </div>

                                  {(givenText || whenText || thenText) ? (
                                    <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.2rem' }}>
                                      {givenText && (
                                        <span style={{ fontSize: '0.68rem', background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                                          <strong style={{ color: '#38bdf8' }}>GIVEN</strong> {givenText.replace(/^Given\s*/i, '')}
                                        </span>
                                      )}
                                      {whenText && (
                                        <span style={{ fontSize: '0.68rem', background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                                          <strong style={{ color: '#f59e0b' }}>WHEN</strong> {whenText.replace(/^When\s*/i, '')}
                                        </span>
                                      )}
                                      {thenText && (
                                        <span style={{ fontSize: '0.68rem', background: '#0f172a', border: '1px solid #334155', color: '#94a3b8', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                                          <strong style={{ color: '#4ade80' }}>THEN</strong> {thenText.replace(/^Then\s*/i, '')}
                                        </span>
                                      )}
                                    </div>
                                  ) : sub.description && sub.description !== subTitle && (
                                    <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>{sub.description}</div>
                                  )}
                                </div>
                              );
                            })
                          )}
                        </div>

                        {/* BDD Quick Action Chips & Input Form */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.35rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 600 }}>Insert step:</span>
                            <button
                              type="button"
                              onClick={() => {
                                const cur = subPromptByComponent[item.canonical_key] || '';
                                setSubPromptByComponent({ ...subPromptByComponent, [item.canonical_key]: cur ? `${cur} Given ` : 'Given ' });
                              }}
                              style={{ background: '#0f172a', border: '1px solid #334155', color: '#38bdf8', fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 700 }}
                            >
                              + GIVEN
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                const cur = subPromptByComponent[item.canonical_key] || '';
                                setSubPromptByComponent({ ...subPromptByComponent, [item.canonical_key]: cur ? `${cur} When ` : 'When ' });
                              }}
                              style={{ background: '#0f172a', border: '1px solid #334155', color: '#f59e0b', fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 700 }}
                            >
                              + WHEN
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                const cur = subPromptByComponent[item.canonical_key] || '';
                                setSubPromptByComponent({ ...subPromptByComponent, [item.canonical_key]: cur ? `${cur} Then ` : 'Then ' });
                              }}
                              style={{ background: '#0f172a', border: '1px solid #334155', color: '#4ade80', fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 700 }}
                            >
                              + THEN
                            </button>
                          </div>

                          <div style={{ display: 'flex', gap: '0.35rem' }}>
                            <input
                              type="text"
                              placeholder={getTestPlaceholder(item.canonical_key)}
                              value={subPromptByComponent[item.canonical_key] || ''}
                              onChange={e => setSubPromptByComponent({ ...subPromptByComponent, [item.canonical_key]: e.target.value })}
                              onKeyDown={e => { if (e.key === 'Enter') handleAddSubRequirement(item.canonical_key); }}
                              disabled={addingSubKey === item.canonical_key}
                              style={{
                                flex: 1,
                                background: '#1e293b',
                                border: '1px solid #334155',
                                borderRadius: '0.4rem',
                                padding: '0.35rem 0.6rem',
                                fontSize: '0.75rem',
                                color: '#f8fafc',
                                outline: 'none'
                              }}
                            />
                            <button
                              onClick={() => handleAddSubRequirement(item.canonical_key)}
                              disabled={addingSubKey === item.canonical_key || !(subPromptByComponent[item.canonical_key] || '').trim()}
                              style={{
                                background: (subPromptByComponent[item.canonical_key] || '').trim() ? '#0284c7' : '#334155',
                                color: 'white',
                                border: 'none',
                                padding: '0.35rem 0.65rem',
                                borderRadius: '0.4rem',
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                cursor: (subPromptByComponent[item.canonical_key] || '').trim() ? 'pointer' : 'not-allowed',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {addingSubKey === item.canonical_key ? '⏳' : '➕ Add Test'}
                            </button>
                          </div>
                        </div>
                      </>
                    )}

                    {/* TAB 2: DATA FIXTURES & ENTITIES CRUD */}
                    {activeTabByComponent[item.canonical_key] === 'data' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                        {/* Data Fixtures List */}
                        {(!dataFixturesByComponent[item.canonical_key] || dataFixturesByComponent[item.canonical_key].length === 0) ? (
                          <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
                            No entity items defined for this component. Use the form below to add data.
                          </div>
                        ) : (
                          dataFixturesByComponent[item.canonical_key].map((fix) => {
                            const isEditingThis = editingFixtureId === fix.id;

                            if (isEditingThis) {
                              return (
                                <div key={fix.id} style={{ display: 'flex', gap: '0.35rem', background: '#1e293b', padding: '0.4rem', borderRadius: '0.4rem', border: '1px solid #0284c7' }}>
                                  <input
                                    type="text"
                                    value={editFixtureName}
                                    onChange={e => setEditFixtureName(e.target.value)}
                                    style={{ flex: 2, background: '#0f172a', border: '1px solid #334155', color: '#fff', padding: '0.2rem 0.4rem', borderRadius: '0.3rem', fontSize: '0.75rem' }}
                                  />
                                  <input
                                    type="number"
                                    value={editFixturePrice}
                                    onChange={e => setEditFixturePrice(e.target.value)}
                                    style={{ flex: 1, background: '#0f172a', border: '1px solid #334155', color: '#fff', padding: '0.2rem 0.4rem', borderRadius: '0.3rem', fontSize: '0.75rem' }}
                                  />
                                  <button
                                    onClick={() => handleSaveFixtureEdit(item.canonical_key, fix.id)}
                                    style={{ background: '#166534', color: '#4ade80', border: 'none', padding: '0.2rem 0.4rem', borderRadius: '0.3rem', fontSize: '0.75rem', cursor: 'pointer' }}
                                  >
                                    Save
                                  </button>
                                  <button
                                    onClick={() => setEditingFixtureId(null)}
                                    style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '0.75rem', cursor: 'pointer' }}
                                  >
                                    ✕
                                  </button>
                                </div>
                              );
                            }

                            return (
                              <div
                                key={fix.id}
                                style={{
                                  background: '#1e293b',
                                  border: '1px solid #334155',
                                  borderRadius: '0.4rem',
                                  padding: '0.4rem 0.65rem',
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'center',
                                  fontSize: '0.75rem',
                                  color: '#f8fafc'
                                }}
                              >
                                <span>{fix.name}</span>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <span style={{ color: '#4ade80', fontWeight: 600 }}>${fix.price.toFixed(2)}</span>
                                  <button
                                    onClick={() => {
                                      setEditingFixtureId(fix.id);
                                      setEditFixtureName(fix.name);
                                      setEditFixturePrice(fix.price.toString());
                                    }}
                                    title="Edit entity item"
                                    style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', fontSize: '0.75rem', padding: '0 0.15rem' }}
                                  >
                                    ✏️
                                  </button>
                                  <button
                                    onClick={() => handleDeleteFixture(item.canonical_key, fix.id)}
                                    title="Delete entity item"
                                    style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem', padding: '0 0.15rem' }}
                                  >
                                    🗑️
                                  </button>
                                </div>
                              </div>
                            );
                          })
                        )}

                        {/* Form to Add New Entity Item */}
                        <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.35rem' }}>
                          <input
                            type="text"
                            placeholder="New Item Name..."
                            value={newFixtureName[item.canonical_key] || ''}
                            onChange={e => setNewFixtureName({ ...newFixtureName, [item.canonical_key]: e.target.value })}
                            style={{ flex: 2, background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                          />
                          <input
                            type="number"
                            placeholder="Price ($)"
                            value={newFixturePrice[item.canonical_key] || ''}
                            onChange={e => setNewFixturePrice({ ...newFixturePrice, [item.canonical_key]: e.target.value })}
                            style={{ flex: 1, background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                          />
                          <button
                            onClick={() => handleAddFixture(item.canonical_key)}
                            style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '0.35rem', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}
                          >
                            ➕ Add
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

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
