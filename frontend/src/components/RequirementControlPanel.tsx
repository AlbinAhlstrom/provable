import React, { useState, useEffect } from 'react';
import { ComponentAddRequestDTO, ComponentDeleteRequestDTO, DomainEntitySchemaDTO, EntityAttributeDTO } from '../types/api';


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

const getTestPlaceholder = (_key?: string) => {
  return 'e.g. GIVEN active view, WHEN action triggered, THEN assert expected state transition, UNLESS invariant fails...';
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

  // Entity Data State
  const [dataFixturesByComponent, setDataFixturesByComponent] = useState<Record<string, Array<{ id: string, name: string, price: number, quantity?: number, status?: string, catalog_id?: string, item?: string, ingredients?: string[] }>>>({});
  const [entitySchemasByComponent, setEntitySchemasByComponent] = useState<Record<string, DomainEntitySchemaDTO>>({});

  // Schema Editor Modal State
  const [editingSchemaKey, setEditingSchemaKey] = useState<string | null>(null);
  const [schemaEntityName, setSchemaEntityName] = useState<string>('');
  const [schemaAttributes, setSchemaAttributes] = useState<EntityAttributeDTO[]>([]);
  const [newAttrName, setNewAttrName] = useState<string>('');
  const [newAttrType, setNewAttrType] = useState<'string' | 'currency' | 'number' | 'tags' | 'boolean'>('tags');
  const [newAttrDisplayMode, setNewAttrDisplayMode] = useState<'visible' | 'tag_chips' | 'badge' | 'subtitle' | 'hidden'>('tag_chips');

  // Role-Aware Entity Form State
  const [selectedCatalogItem, setSelectedCatalogItem] = useState<Record<string, string>>({});
  const [selectedQuantity, setSelectedQuantity] = useState<Record<string, number>>({});
  const [selectedOrderStatus, setSelectedOrderStatus] = useState<Record<string, string>>({});

  // Dynamic Entity Inline Editing State
  const [editingFixtureId, setEditingFixtureId] = useState<string | null>(null);
  const [editFixtureData, setEditFixtureData] = useState<Record<string, any>>({});
  const [newFixtureDataByComponent, setNewFixtureDataByComponent] = useState<Record<string, Record<string, any>>>({});

  const toggleComponentTab = (key: string, tab: 'tests' | 'data') => {
    setActiveTabByComponent(prev => ({ ...prev, [key]: tab }));
  };

  const handleOpenSchemaEditor = (canonicalKey: string) => {
    const existing = entitySchemasByComponent[canonicalKey];
    setEditingSchemaKey(canonicalKey);
    setSchemaEntityName(existing?.entity_name || (canonicalKey === 'cart' ? 'CartItem' : canonicalKey === 'tracking' ? 'Order' : 'Item'));
    setSchemaAttributes(existing?.attributes || [
      { name: 'name', type: 'string', required: true, display_mode: 'visible' },
      { name: 'price', type: 'currency', required: true, display_mode: 'visible' }
    ]);
    setNewAttrName('');
    setNewAttrType('tags');
    setNewAttrDisplayMode('tag_chips');
  };

  const handleAddAttributeToSchema = () => {
    const cleanName = newAttrName.trim().toLowerCase().replace(/\s+/g, '_');
    if (!cleanName) return;
    if (schemaAttributes.some(a => a.name === cleanName)) {
      setStatusToast(`⚠️ Attribute "${cleanName}" already exists`);
      setTimeout(() => setStatusToast(null), 2500);
      return;
    }
    setSchemaAttributes(prev => [
      ...prev,
      { name: cleanName, type: newAttrType, required: false, display_mode: newAttrDisplayMode }
    ]);
    setNewAttrName('');
    setNewAttrDisplayMode('visible');
  };

  const handleRemoveAttributeFromSchema = (attrName: string) => {
    setSchemaAttributes(prev => prev.filter(a => a.name !== attrName));
  };

  const handleUpdateAttributeDisplayMode = (attrName: string, mode: 'visible' | 'tag_chips' | 'badge' | 'subtitle' | 'hidden') => {
    setSchemaAttributes(prev => prev.map(a => a.name === attrName ? { ...a, display_mode: mode } : a));
  };

  const handleUpdateAttributeType = (attrName: string, type: 'string' | 'currency' | 'number' | 'tags' | 'boolean') => {
    setSchemaAttributes(prev => prev.map(a => a.name === attrName ? { ...a, type } : a));
  };

  const handleSaveSchema = async () => {
    if (!editingSchemaKey) return;
    try {
      const payload = {
        canonical_key: editingSchemaKey,
        entity_name: schemaEntityName.trim() || 'Item',
        attributes: schemaAttributes
      };
      const res = await fetch('/api/components/entities/schema/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setEntitySchemasByComponent(prev => ({
          ...prev,
          [editingSchemaKey]: {
            canonical_key: editingSchemaKey,
            entity_name: payload.entity_name,
            attributes: schemaAttributes
          }
        }));
        setStatusToast(`✨ Updated schema for ${payload.entity_name}`);
        setEditingSchemaKey(null);
        
        // Re-hydrate fixtures to catch normalized defaults and broadcast to iframe
        const fixRes = await fetch('/api/components/fixtures');
        const fixData = await fixRes.json();
        if (fixData && fixData.success && fixData.fixtures) {
          setDataFixturesByComponent(fixData.fixtures);
          const updatedFixtures = fixData.fixtures[editingSchemaKey] || [];
          window.postMessage({ type: 'FIXTURES_UPDATED', canonical_key: editingSchemaKey, fixtures: updatedFixtures }, '*');
          const iframes = document.querySelectorAll('iframe');
          iframes.forEach(iframe => {
            iframe.contentWindow?.postMessage({ type: 'FIXTURES_UPDATED', canonical_key: editingSchemaKey, fixtures: updatedFixtures }, '*');
          });
        }
        if (onParamUpdated) onParamUpdated();
      } else {
        setStatusToast(`❌ Failed to update schema: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error("Error updating entity schema:", err);
      setStatusToast(`❌ Network error updating schema`);
    }
    setTimeout(() => setStatusToast(null), 3000);
  };

  // Helper to discover master catalog items across domains
  const getAvailableCatalogItems = () => {
    if (dataFixturesByComponent['catalog'] && dataFixturesByComponent['catalog'].length > 0) {
      return dataFixturesByComponent['catalog'];
    }
    if (dataFixturesByComponent['menu'] && dataFixturesByComponent['menu'].length > 0) {
      return dataFixturesByComponent['menu'];
    }
    if (dataFixturesByComponent['services'] && dataFixturesByComponent['services'].length > 0) {
      return dataFixturesByComponent['services'];
    }
    if (dataFixturesByComponent['products'] && dataFixturesByComponent['products'].length > 0) {
      return dataFixturesByComponent['products'];
    }
    for (const [key, items] of Object.entries(dataFixturesByComponent)) {
      if (!['cart', 'tracking', 'orders', 'kds', 'status'].includes(key.toLowerCase()) && Array.isArray(items) && items.length > 0) {
        return items;
      }
    }
    return [];
  };

  const persistFixtureUpdate = async (canonicalKey: string, updatedList: any[]) => {
    try {
      setDataFixturesByComponent(prev => ({ ...prev, [canonicalKey]: updatedList }));
      
      // Broadcast live to window and all iframe previews
      window.postMessage({ type: 'FIXTURES_UPDATED', canonical_key: canonicalKey, fixtures: updatedList }, '*');
      const iframes = document.querySelectorAll('iframe');
      iframes.forEach(iframe => {
        iframe.contentWindow?.postMessage({ type: 'FIXTURES_UPDATED', canonical_key: canonicalKey, fixtures: updatedList }, '*');
      });

      const res = await fetch('/api/components/fixtures/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ canonical_key: canonicalKey, fixtures: updatedList })
      });
      const data = await res.json();
      if (data.success && onParamUpdated) {
        onParamUpdated();
      }
    } catch (err) {
      console.error("Error updating domain entities:", err);
    }
  };

  const handleStartEditFixture = (fix: Record<string, any>) => {
    setEditingFixtureId(fix.id);
    setEditFixtureData({ ...fix });
  };

  const handleSaveFixtureEdit = (canonicalKey: string, fixId: string) => {
    const schema = entitySchemasByComponent[canonicalKey];
    const attrs = schema?.attributes || [
      { name: 'name', type: 'string', display_mode: 'visible', required: true },
      { name: 'price', type: 'currency', display_mode: 'visible', required: true }
    ];

    const updatedList = (dataFixturesByComponent[canonicalKey] || []).map(item => {
      if (item.id === fixId) {
        const merged: Record<string, any> = { ...item, ...editFixtureData };
        attrs.forEach(attr => {
          if (editFixtureData[attr.name] !== undefined) {
            const val = editFixtureData[attr.name];
            if (attr.type === 'currency' || attr.type === 'number') {
              merged[attr.name] = val !== '' && !isNaN(parseFloat(val)) ? parseFloat(val) : (attr.default_value ?? 0);
            } else if (attr.type === 'tags' || attr.display_mode === 'tag_chips') {
              merged[attr.name] = typeof val === 'string' ? val.split(',').map((s: string) => s.trim()).filter(Boolean) : (Array.isArray(val) ? val : []);
            } else if (attr.type === 'boolean') {
              merged[attr.name] = Boolean(val);
            } else {
              merged[attr.name] = val !== undefined ? String(val).trim() : (attr.default_value ?? '');
            }
          }
        });
        return merged;
      }
      return item;
    });

    persistFixtureUpdate(canonicalKey, updatedList);
    setEditingFixtureId(null);
    setEditFixtureData({});
    setStatusToast(`✨ Updated entity attributes`);
    setTimeout(() => setStatusToast(null), 2000);
  };

  const handleAddFixture = (canonicalKey: string) => {
    const schema = entitySchemasByComponent[canonicalKey];
    const attrs = schema?.attributes || [
      { name: 'name', type: 'string', display_mode: 'visible', required: true },
      { name: 'price', type: 'currency', display_mode: 'visible', required: true }
    ];

    const formVals = newFixtureDataByComponent[canonicalKey] || {};
    const newItem: Record<string, any> = {
      id: `fix-${Date.now()}`
    };

    attrs.forEach(attr => {
      const val = formVals[attr.name];
      if (attr.type === 'currency' || attr.type === 'number') {
        newItem[attr.name] = (val !== undefined && val !== '' && !isNaN(parseFloat(val))) ? parseFloat(val) : (attr.default_value ?? 14.99);
      } else if (attr.type === 'tags' || attr.display_mode === 'tag_chips') {
        newItem[attr.name] = typeof val === 'string' ? val.split(',').map((s: string) => s.trim()).filter(Boolean) : (Array.isArray(val) ? val : []);
      } else if (attr.type === 'boolean') {
        newItem[attr.name] = Boolean(val);
      } else {
        newItem[attr.name] = val !== undefined && String(val).trim() ? String(val).trim() : (attr.default_value ?? (attr.name === 'name' ? 'New Item' : ''));
      }
    });

    if (!newItem.name && !newItem.title && !newItem.item) {
      newItem.name = `Item #${(dataFixturesByComponent[canonicalKey] || []).length + 1}`;
    }
    if (newItem.price === undefined) {
      newItem.price = 14.99;
    }

    const updatedList = [...(dataFixturesByComponent[canonicalKey] || []), newItem];
    persistFixtureUpdate(canonicalKey, updatedList);

    setNewFixtureDataByComponent(prev => ({ ...prev, [canonicalKey]: {} }));
    setStatusToast(`✨ Added entity "${newItem.name || newItem.title || newItem.item}"`);
    setTimeout(() => setStatusToast(null), 2500);
  };

  const handleAddCartEntity = (canonicalKey: string) => {
    const catalogItems = getAvailableCatalogItems();
    const selectedId = selectedCatalogItem[canonicalKey] || (catalogItems[0] ? catalogItems[0].id : '');
    const catalogItem = catalogItems.find(c => c.id === selectedId) || catalogItems[0];
    if (!catalogItem) return;

    const qty = selectedQuantity[canonicalKey] || 1;
    const newItem = {
      id: `fix-cart-${Date.now()}`,
      name: catalogItem.name,
      price: catalogItem.price,
      quantity: qty,
      catalog_id: catalogItem.id
    };

    const updatedList = [...(dataFixturesByComponent[canonicalKey] || []), newItem];
    persistFixtureUpdate(canonicalKey, updatedList);
    setStatusToast(`🛒 Added ${catalogItem.name} (x${qty}) to cart`);
    setTimeout(() => setStatusToast(null), 2500);
  };

  const handleAddTrackingEntity = (canonicalKey: string) => {
    const catalogItems = getAvailableCatalogItems();
    const selectedId = selectedCatalogItem[canonicalKey] || (catalogItems[0] ? catalogItems[0].id : '');
    const catalogItem = catalogItems.find(c => c.id === selectedId) || catalogItems[0];
    const statusVal = selectedOrderStatus[canonicalKey] || 'Received';
    const orderNum = Math.floor(1000 + Math.random() * 9000);
    const itemName = catalogItem ? catalogItem.name : 'Domain Item';
    const itemPrice = catalogItem ? catalogItem.price : 14.99;

    const newOrder = {
      id: `ORD-${orderNum}`,
      name: `Order #${orderNum} (${itemName})`,
      price: itemPrice,
      status: statusVal,
      item: itemName
    };

    const updatedList = [...(dataFixturesByComponent[canonicalKey] || []), newOrder];
    persistFixtureUpdate(canonicalKey, updatedList);
    setStatusToast(`📦 Created order ORD-${orderNum} [${statusVal}]`);
    setTimeout(() => setStatusToast(null), 2500);
  };

  const handleDeleteFixture = (canonicalKey: string, fixId: string) => {
    const updatedList = (dataFixturesByComponent[canonicalKey] || []).filter(item => item.id !== fixId);
    persistFixtureUpdate(canonicalKey, updatedList);

    setStatusToast(`🗑️ Deleted entity`);
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
          .filter((r: any) => r.id && r.status !== 'Disabled' && !r.parentId && !r.parent_id && (r.layer === 'PRESENTATION' || r.id.startsWith('REQ-UI') || r.id.startsWith('REQ-COMP')))
          .map((r: any) => {
            const canonicalKey = extractCanonicalKey(r);
            const compType = r.component_type || 'domain_capability';
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

      // 3. Fetch active domain schemas and data fixtures from backend API
      const entRes = await fetch('/api/components/entities');
      const entData = await entRes.json();
      if (entData && entData.success) {
        if (entData.schemas) {
          setEntitySchemasByComponent(entData.schemas);
        }
        if (entData.fixtures) {
          setDataFixturesByComponent(entData.fixtures);
        }
      }
    } catch (e) {
      console.error("Hydration error in RequirementControlPanel:", e);
    }
  };

  useEffect(() => {
    hydrateData();

    const handleWindowMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'FIXTURES_UPDATED' && event.data.canonical_key && event.data.fixtures) {
        setDataFixturesByComponent(prev => ({
          ...prev,
          [event.data.canonical_key]: event.data.fixtures
        }));
      }
    };
    window.addEventListener('message', handleWindowMessage);
    return () => window.removeEventListener('message', handleWindowMessage);
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
                        🧬 Entities ({(dataFixturesByComponent[item.canonical_key] || []).length})
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
                            <button
                              type="button"
                              onClick={() => {
                                const cur = subPromptByComponent[item.canonical_key] || '';
                                setSubPromptByComponent({ ...subPromptByComponent, [item.canonical_key]: cur ? `${cur} Unless ` : 'Unless ' });
                              }}
                              style={{ background: '#0f172a', border: '1px solid #334155', color: '#f43f5e', fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 700 }}
                            >
                              + UNLESS
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

                    {/* TAB 2: DOMAIN ENTITIES CRUD */}
                    {activeTabByComponent[item.canonical_key] === 'data' && (() => {
                      const isCart = ['cart', 'basket'].includes(item.canonical_key.toLowerCase());
                      const isTracking = ['tracking', 'orders', 'kds', 'status'].includes(item.canonical_key.toLowerCase());
                      const catalogItems = getAvailableCatalogItems();
                      const currentFixtures = dataFixturesByComponent[item.canonical_key] || [];

                      const schema = entitySchemasByComponent[item.canonical_key];
                      const entityClassName = schema?.entity_name || (isCart ? 'CartItem' : isTracking ? 'Order' : 'CatalogItem');
                      const attrSummary = schema?.attributes?.map(a => `${a.name} (${a.type})`).join(' • ') || 'name (str) • price ($)';

                      return (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
                          {/* Entity Class Header */}
                          <div style={{
                            background: '#0b1329',
                            border: '1px solid #1e3a8a',
                            borderRadius: '0.45rem',
                            padding: '0.45rem 0.65rem',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '0.2rem'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                              <span style={{ fontSize: '0.9rem' }}>📦</span>
                              <div>
                                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#38bdf8' }}>
                                  {entityClassName} <span style={{ fontSize: '0.65rem', color: '#94a3b8', fontWeight: 500 }}>(Entity Class)</span>
                                </div>
                                <div style={{ fontSize: '0.62rem', color: '#64748b' }}>
                                  Attributes: {attrSummary}
                                </div>
                              </div>
                            </div>
                            <button
                              onClick={() => handleOpenSchemaEditor(item.canonical_key)}
                              style={{
                                background: '#1e293b',
                                border: '1px solid #334155',
                                color: '#93c5fd',
                                borderRadius: '0.35rem',
                                padding: '0.2rem 0.45rem',
                                fontSize: '0.68rem',
                                fontWeight: 700,
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}
                              title="Edit Entity Class Schema & Attributes"
                            >
                              ⚙️ Edit Schema
                            </button>
                          </div>

                          {/* Domain Entities List */}
                          {currentFixtures.length === 0 ? (
                            <div style={{ fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic', padding: '0.2rem 0' }}>
                              {isCart
                                ? 'Cart is empty. Select an item from the catalog below to add to cart.'
                                : isTracking
                                ? 'No active orders. Create a test order from the catalog below.'
                                : 'No entity items defined for this component. Use the form below to add data.'}
                            </div>
                          ) : (
                            currentFixtures.map((fix) => {
                              const isEditingThis = editingFixtureId === fix.id;

                              if (isEditingThis) {
                                return (
                                  <div key={fix.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', background: '#1e293b', padding: '0.65rem', borderRadius: '0.5rem', border: '1px solid #0284c7' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '0.35rem' }}>
                                      <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38bdf8' }}>✏️ Edit {entityClassName}</span>
                                      <div style={{ display: 'flex', gap: '0.35rem' }}>
                                        <button
                                          onClick={() => handleSaveFixtureEdit(item.canonical_key, fix.id)}
                                          style={{ background: '#166534', color: '#4ade80', border: 'none', padding: '0.2rem 0.55rem', borderRadius: '0.3rem', fontSize: '0.72rem', fontWeight: 700, cursor: 'pointer' }}
                                        >
                                          💾 Save
                                        </button>
                                        <button
                                          onClick={() => { setEditingFixtureId(null); setEditFixtureData({}); }}
                                          style={{ background: '#334155', color: '#94a3b8', border: 'none', padding: '0.2rem 0.45rem', borderRadius: '0.3rem', fontSize: '0.72rem', cursor: 'pointer' }}
                                        >
                                          ✕
                                        </button>
                                      </div>
                                    </div>

                                    {/* Grid of All Editable Schema Attributes */}
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.4rem' }}>
                                      {(schema?.attributes || [{ name: 'name', type: 'string' }, { name: 'price', type: 'currency' }]).map(attr => {
                                        const val = editFixtureData[attr.name];
                                        const isTag = attr.type === 'tags' || attr.display_mode === 'tag_chips';
                                        const isNum = attr.type === 'number' || attr.type === 'currency';
                                        const isBool = attr.type === 'boolean';

                                        return (
                                          <div key={attr.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                                            <label style={{ fontSize: '0.62rem', fontWeight: 700, color: '#94a3b8', textTransform: 'capitalize' }}>
                                              {attr.name} {isTag ? '(tags)' : isNum ? '($/num)' : ''}
                                            </label>
                                            {isBool ? (
                                              <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.72rem', color: '#f8fafc', cursor: 'pointer', padding: '0.2rem 0' }}>
                                                <input
                                                  type="checkbox"
                                                  checked={Boolean(val)}
                                                  onChange={e => setEditFixtureData(prev => ({ ...prev, [attr.name]: e.target.checked }))}
                                                />
                                                {attr.name}
                                              </label>
                                            ) : (
                                              <input
                                                type={isNum ? 'number' : 'text'}
                                                value={isTag ? (Array.isArray(val) ? val.join(', ') : (val || '')) : (val !== undefined ? val : '')}
                                                onChange={e => {
                                                  const raw = e.target.value;
                                                  if (isTag) {
                                                    setEditFixtureData(prev => ({ ...prev, [attr.name]: raw.split(',').map((s: string) => s.trim()).filter(Boolean) }));
                                                  } else if (isNum) {
                                                    setEditFixtureData(prev => ({ ...prev, [attr.name]: raw === '' ? '' : parseFloat(raw) }));
                                                  } else {
                                                    setEditFixtureData(prev => ({ ...prev, [attr.name]: raw }));
                                                  }
                                                }}
                                                placeholder={isTag ? 'Comma-separated tags' : attr.name}
                                                style={{
                                                  background: '#0f172a',
                                                  border: '1px solid #334155',
                                                  color: '#fff',
                                                  padding: '0.25rem 0.45rem',
                                                  borderRadius: '0.3rem',
                                                  fontSize: '0.72rem'
                                                }}
                                              />
                                            )}
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                );
                              }

                              if (isCart) {
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
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                      <span>{fix.name}</span>
                                      {fix.quantity && fix.quantity > 1 && (
                                        <span style={{ fontSize: '0.65rem', background: '#0284c7', color: '#fff', padding: '0.1rem 0.35rem', borderRadius: '4px', fontWeight: 700 }}>
                                          x{fix.quantity}
                                        </span>
                                      )}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      <span style={{ color: '#4ade80', fontWeight: 600 }}>
                                        ${((fix.price || 0) * (fix.quantity || 1)).toFixed(2)}
                                      </span>
                                      <button
                                        onClick={() => handleDeleteFixture(item.canonical_key, fix.id)}
                                        title="Remove from cart"
                                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem', padding: '0 0.15rem' }}
                                      >
                                        🗑️
                                      </button>
                                    </div>
                                  </div>
                                );
                              }

                              if (isTracking) {
                                const statusColor = fix.status === 'Delivered' ? '#4ade80' : fix.status === 'Preparing' ? '#f59e0b' : '#38bdf8';
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
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                                      <span style={{ fontWeight: 600 }}>{fix.name || fix.item || `Order #${fix.id}`}</span>
                                      {fix.status && (
                                        <span style={{ fontSize: '0.65rem', color: statusColor, fontWeight: 700 }}>
                                          ● {fix.status}
                                        </span>
                                      )}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                      <span style={{ color: '#4ade80', fontWeight: 600 }}>${(fix.price || 0).toFixed(2)}</span>
                                      <button
                                        onClick={() => handleDeleteFixture(item.canonical_key, fix.id)}
                                        title="Delete order"
                                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem', padding: '0 0.15rem' }}
                                      >
                                        🗑️
                                      </button>
                                    </div>
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
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', flex: 1, minWidth: 0 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                                      <span style={{ fontWeight: 700, color: '#f8fafc' }}>{fix.name || (fix as Record<string, any>).title || fix.item || `Item #${fix.id}`}</span>
                                      
                                      {/* Render badges */}
                                      {schema?.attributes?.filter(a => a.display_mode === 'badge' && (fix as Record<string, any>)[a.name] !== undefined && (fix as Record<string, any>)[a.name] !== '').map(a => (
                                        <span key={a.name} style={{ fontSize: '0.62rem', background: '#0284c7', color: '#e0f2fe', padding: '0.05rem 0.35rem', borderRadius: '4px', fontWeight: 700 }}>
                                          {String((fix as Record<string, any>)[a.name])}
                                        </span>
                                      ))}
                                    </div>

                                    {/* Render subtitles */}
                                    {schema?.attributes?.filter(a => a.display_mode === 'subtitle' && (fix as Record<string, any>)[a.name]).map(a => (
                                      <span key={a.name} style={{ fontSize: '0.68rem', color: '#94a3b8' }}>
                                        {String((fix as Record<string, any>)[a.name])}
                                      </span>
                                    ))}

                                    {/* Render tag chips */}
                                    {schema?.attributes?.filter(a => (a.display_mode === 'tag_chips' || a.type === 'tags') && (fix as Record<string, any>)[a.name]).map(a => {
                                      const rawVal = (fix as Record<string, any>)[a.name];
                                      const tags = Array.isArray(rawVal) ? rawVal : String(rawVal).split(',').map((s: string) => s.trim()).filter(Boolean);
                                      if (tags.length === 0) return null;
                                      return (
                                        <div key={a.name} style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                          {tags.map((tag: string, i: number) => (
                                            <span key={i} style={{ fontSize: '0.62rem', background: '#0f172a', color: '#38bdf8', padding: '0.05rem 0.35rem', borderRadius: '4px', border: '1px solid #334155' }}>
                                              {tag}
                                            </span>
                                          ))}
                                        </div>
                                      );
                                    })}

                                    {/* Render other custom visible attributes */}
                                    {schema?.attributes?.filter(a => a.display_mode === 'visible' && !['name', 'title', 'item', 'price'].includes(a.name) && (fix as Record<string, any>)[a.name] !== undefined && (fix as Record<string, any>)[a.name] !== '').map(a => (
                                      <span key={a.name} style={{ fontSize: '0.65rem', color: '#cbd5e1' }}>
                                        <strong style={{ color: '#94a3b8' }}>{a.name}:</strong> {String((fix as Record<string, any>)[a.name])}
                                      </span>
                                    ))}
                                  </div>

                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    {fix.price !== undefined && (
                                      <span style={{ color: '#4ade80', fontWeight: 700 }}>
                                        ${typeof fix.price === 'number' ? fix.price.toFixed(2) : String(fix.price).replace('$', '')}
                                      </span>
                                    )}
                                    <button
                                      onClick={() => handleStartEditFixture(fix)}
                                      title="Edit entity attributes"
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

                          {/* Role-Aware Add Entity Form */}
                          {isCart ? (
                            catalogItems.length > 0 ? (
                              <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.35rem', alignItems: 'center' }}>
                                <select
                                  value={selectedCatalogItem[item.canonical_key] || catalogItems[0]?.id || ''}
                                  onChange={e => setSelectedCatalogItem({ ...selectedCatalogItem, [item.canonical_key]: e.target.value })}
                                  style={{ flex: 2, background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                                >
                                  {catalogItems.map(c => (
                                    <option key={c.id} value={c.id}>
                                      {c.name} (${c.price.toFixed(2)})
                                    </option>
                                  ))}
                                </select>
                                <input
                                  type="number"
                                  min="1"
                                  value={selectedQuantity[item.canonical_key] || 1}
                                  onChange={e => setSelectedQuantity({ ...selectedQuantity, [item.canonical_key]: Math.max(1, parseInt(e.target.value) || 1) })}
                                  style={{ width: '45px', background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.35rem', borderRadius: '0.35rem', fontSize: '0.75rem', textAlign: 'center' }}
                                  title="Quantity"
                                />
                                <button
                                  onClick={() => handleAddCartEntity(item.canonical_key)}
                                  style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '0.35rem', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap' }}
                                >
                                  🛒 Add
                                </button>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: '#f59e0b', fontStyle: 'italic', marginTop: '0.2rem' }}>
                                ⚠️ Add items to the Catalog component first to populate the cart dropdown.
                              </div>
                            )
                          ) : isTracking ? (
                            catalogItems.length > 0 ? (
                              <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.35rem', alignItems: 'center' }}>
                                <select
                                  value={selectedCatalogItem[item.canonical_key] || catalogItems[0]?.id || ''}
                                  onChange={e => setSelectedCatalogItem({ ...selectedCatalogItem, [item.canonical_key]: e.target.value })}
                                  style={{ flex: 2, background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                                >
                                  {catalogItems.map(c => (
                                    <option key={c.id} value={c.id}>
                                      {c.name} (${c.price.toFixed(2)})
                                    </option>
                                  ))}
                                </select>
                                <select
                                  value={selectedOrderStatus[item.canonical_key] || 'Received'}
                                  onChange={e => setSelectedOrderStatus({ ...selectedOrderStatus, [item.canonical_key]: e.target.value })}
                                  style={{ flex: 1, background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.3rem 0.35rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                                >
                                  <option value="Received">Received</option>
                                  <option value="Preparing">Preparing</option>
                                  <option value="Out for Delivery">Out for Delivery</option>
                                  <option value="Delivered">Delivered</option>
                                </select>
                                <button
                                  onClick={() => handleAddTrackingEntity(item.canonical_key)}
                                  style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '0.35rem', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap' }}
                                >
                                  📦 Order
                                </button>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: '#f59e0b', fontStyle: 'italic', marginTop: '0.2rem' }}>
                                ⚠️ Add items to the Catalog component first to create test orders.
                              </div>
                            )
                          ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', marginTop: '0.45rem', background: '#0b1329', border: '1px solid #1e3a8a', borderRadius: '0.5rem', padding: '0.65rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8' }}>
                                  ➕ Add New {entityClassName}:
                                </span>
                                <button
                                  onClick={() => handleAddFixture(item.canonical_key)}
                                  style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.25rem 0.65rem', borderRadius: '0.35rem', fontSize: '0.72rem', fontWeight: 700, cursor: 'pointer' }}
                                >
                                  ➕ Add Entity
                                </button>
                              </div>

                              {/* Dynamic inputs for each attribute defined in the schema */}
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.35rem' }}>
                                {(schema?.attributes || [{ name: 'name', type: 'string' }, { name: 'price', type: 'currency' }]).map(attr => {
                                  const formVals = newFixtureDataByComponent[item.canonical_key] || {};
                                  const val = formVals[attr.name];
                                  const isTag = attr.type === 'tags' || attr.display_mode === 'tag_chips';
                                  const isNum = attr.type === 'number' || attr.type === 'currency';
                                  const isBool = attr.type === 'boolean';

                                  return (
                                    <div key={attr.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                                      <label style={{ fontSize: '0.62rem', fontWeight: 700, color: '#94a3b8', textTransform: 'capitalize' }}>
                                        {attr.name} {isTag ? '(tags)' : isNum ? '($/num)' : ''}
                                      </label>
                                      {isBool ? (
                                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.72rem', color: '#f8fafc', cursor: 'pointer', padding: '0.2rem 0' }}>
                                          <input
                                            type="checkbox"
                                            checked={Boolean(val)}
                                            onChange={e => setNewFixtureDataByComponent(prev => ({
                                              ...prev,
                                              [item.canonical_key]: { ...(prev[item.canonical_key] || {}), [attr.name]: e.target.checked }
                                            }))}
                                          />
                                          {attr.name}
                                        </label>
                                      ) : (
                                        <input
                                          type={isNum ? 'number' : 'text'}
                                          value={isTag ? (Array.isArray(val) ? val.join(', ') : (val || '')) : (val !== undefined ? val : '')}
                                          onChange={e => {
                                            const raw = e.target.value;
                                            setNewFixtureDataByComponent(prev => ({
                                              ...prev,
                                              [item.canonical_key]: {
                                                ...(prev[item.canonical_key] || {}),
                                                [attr.name]: isTag ? raw.split(',').map((s: string) => s.trim()).filter(Boolean) : (isNum ? (raw === '' ? '' : parseFloat(raw)) : raw)
                                              }
                                            }));
                                          }}
                                          placeholder={isTag ? 'e.g. Tomato, Basil' : `Enter ${attr.name}`}
                                          style={{
                                            background: '#1e293b',
                                            border: '1px solid #334155',
                                            color: '#fff',
                                            padding: '0.25rem 0.45rem',
                                            borderRadius: '0.3rem',
                                            fontSize: '0.72rem'
                                          }}
                                        />
                                      )}
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })()}
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

      {/* SCHEMA EDITOR MODAL */}
      {editingSchemaKey && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div style={{
            background: '#0f172a',
            border: '1px solid #0284c7',
            borderRadius: '1rem',
            width: '100%',
            maxWidth: '460px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            {/* Modal Header */}
            <div style={{
              background: '#1e293b',
              padding: '0.85rem 1.25rem',
              borderBottom: '1px solid #334155',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '1.1rem' }}>⚙️</span>
                <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>
                  Edit Entity Schema ({editingSchemaKey})
                </strong>
              </div>
              <button
                onClick={() => setEditingSchemaKey(null)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.1rem' }}
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {/* Entity Name Field */}
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.35rem' }}>
                  ENTITY CLASS NAME:
                </label>
                <input
                  type="text"
                  value={schemaEntityName}
                  onChange={e => setSchemaEntityName(e.target.value)}
                  placeholder="e.g. CatalogItem, ServiceOffering, Package"
                  style={{
                    width: '100%',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    color: '#fff',
                    padding: '0.45rem 0.65rem',
                    borderRadius: '0.4rem',
                    fontSize: '0.85rem',
                    fontWeight: 700
                  }}
                />
              </div>

              {/* Attributes List */}
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.45rem' }}>
                  SCHEMA ATTRIBUTES ({schemaAttributes.length}):
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '220px', overflowY: 'auto' }}>
                  {schemaAttributes.map((attr) => {
                    return (
                      <div
                        key={attr.name}
                        style={{
                          background: '#1e293b',
                          border: '1px solid #334155',
                          borderRadius: '0.4rem',
                          padding: '0.45rem 0.65rem',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          gap: '0.5rem',
                          fontSize: '0.8rem'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flex: 1, minWidth: 0 }}>
                          <span style={{ fontWeight: 700, color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{attr.name}</span>
                          
                          <select
                            value={attr.type}
                            onChange={e => handleUpdateAttributeType(attr.name, e.target.value as any)}
                            style={{
                              background: '#0f172a',
                              border: '1px solid #334155',
                              color: '#93c5fd',
                              padding: '0.15rem 0.35rem',
                              borderRadius: '4px',
                              fontSize: '0.68rem',
                              fontWeight: 600
                            }}
                          >
                            <option value="string">string</option>
                            <option value="currency">currency ($)</option>
                            <option value="number">number</option>
                            <option value="tags">tags</option>
                            <option value="boolean">boolean</option>
                          </select>

                          <select
                            value={attr.display_mode || 'visible'}
                            onChange={e => handleUpdateAttributeDisplayMode(attr.name, e.target.value as any)}
                            style={{
                              background: '#0f172a',
                              border: '1px solid #334155',
                              color: '#34d399',
                              padding: '0.15rem 0.35rem',
                              borderRadius: '4px',
                              fontSize: '0.68rem',
                              fontWeight: 600
                            }}
                          >
                            <option value="tag_chips">Pills (tag_chips)</option>
                            <option value="badge">Badge (badge)</option>
                            <option value="subtitle">Subtitle (subtitle)</option>
                            <option value="visible">Visible (visible)</option>
                            <option value="hidden">Hidden (hidden)</option>
                          </select>
                        </div>

                        <button
                          onClick={() => handleRemoveAttributeFromSchema(attr.name)}
                          style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.85rem', padding: '0.1rem' }}
                          title="Remove attribute"
                        >
                          🗑️
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Add New Attribute Row */}
              <div style={{ background: '#0b1329', border: '1px solid #1e3a8a', borderRadius: '0.5rem', padding: '0.65rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#38bdf8' }}>
                  ➕ Add New Attribute:
                </span>
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    placeholder="Field name (e.g. ingredients, badge, sku)"
                    value={newAttrName}
                    onChange={e => setNewAttrName(e.target.value)}
                    style={{
                      flex: 2,
                      minWidth: '130px',
                      background: '#1e293b',
                      border: '1px solid #334155',
                      color: '#fff',
                      padding: '0.35rem 0.5rem',
                      borderRadius: '0.35rem',
                      fontSize: '0.75rem'
                    }}
                  />
                  <select
                    value={newAttrType}
                    onChange={e => setNewAttrType(e.target.value as any)}
                    style={{
                      flex: 1,
                      minWidth: '90px',
                      background: '#1e293b',
                      border: '1px solid #334155',
                      color: '#fff',
                      padding: '0.35rem 0.4rem',
                      borderRadius: '0.35rem',
                      fontSize: '0.75rem'
                    }}
                  >
                    <option value="tags">Tag List (tags)</option>
                    <option value="string">Text (string)</option>
                    <option value="number">Number (number)</option>
                    <option value="currency">Currency ($)</option>
                    <option value="boolean">Boolean (toggle)</option>
                  </select>
                  <select
                    value={newAttrDisplayMode}
                    onChange={e => setNewAttrDisplayMode(e.target.value as any)}
                    style={{
                      flex: 1,
                      minWidth: '100px',
                      background: '#1e293b',
                      border: '1px solid #334155',
                      color: '#34d399',
                      padding: '0.35rem 0.4rem',
                      borderRadius: '0.35rem',
                      fontSize: '0.75rem'
                    }}
                  >
                    <option value="tag_chips">Pills (tag_chips)</option>
                    <option value="badge">Badge (badge)</option>
                    <option value="subtitle">Subtitle (subtitle)</option>
                    <option value="visible">Visible (visible)</option>
                    <option value="hidden">Hidden (hidden)</option>
                  </select>
                  <button
                    onClick={handleAddAttributeToSchema}
                    style={{
                      background: '#0284c7',
                      color: 'white',
                      border: 'none',
                      padding: '0.35rem 0.65rem',
                      borderRadius: '0.35rem',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{
              background: '#1e293b',
              padding: '0.75rem 1.25rem',
              borderTop: '1px solid #334155',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.5rem'
            }}>
              <button
                onClick={() => setEditingSchemaKey(null)}
                style={{
                  background: 'transparent',
                  border: '1px solid #475569',
                  color: '#cbd5e1',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '0.4rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveSchema}
                style={{
                  background: '#0284c7',
                  color: '#fff',
                  border: 'none',
                  padding: '0.45rem 1rem',
                  borderRadius: '0.4rem',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                💾 Save &amp; Sync Model
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

// Helper: Extract canonical key from requirement object or title
function extractCanonicalKey(r: any): string {
  const clean = (r.id || r.title || '').toLowerCase().replace(/[^a-z0-9]/g, '_');
  return clean.replace(/^req_ui_/, '').replace(/^req_cmp_/, '').replace(/^req_/, '').replace(/_001$/, '').replace(/^_+|_+$/g, '') || 'main';
}

// Helper: Pick icon for component
function getComponentIcon(canonicalKey: string, _title?: string): string {
  const k = canonicalKey.toLowerCase();
  if (k.includes('calendar') || k.includes('booking') || k.includes('schedule')) return '📅';
  if (k.includes('catalog') || k.includes('menu') || k.includes('directory')) return '📋';
  if (k.includes('cart') || k.includes('checkout') || k.includes('order')) return '🛒';
  if (k.includes('track') || k.includes('pipeline') || k.includes('queue')) return '📦';
  if (k.includes('dashboard') || k.includes('admin') || k.includes('kpi') || k.includes('analytics')) return '📊';
  if (k.includes('review') || k.includes('rating')) return '⭐';
  if (k.includes('auth') || k.includes('user') || k.includes('profile')) return '👤';
  if (k.includes('workbench') || k.includes('simulator') || k.includes('tool') || k.includes('widget')) return '⚡';
  return '🧩';
}

// Helper: Format component name
function formatComponentName(rawName: string): string {
  const clean = rawName.replace(/^Dynamic Component:\s*/i, '').replace(/^Component:\s*/i, '').replace(/^Capability Block\s*/i, '').replace(/\s*Active$/i, '');
  return clean.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
