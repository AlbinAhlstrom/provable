import React, { useState } from 'react';

interface ComponentItem {
  id: string;
  name: string;
  reqId: string;
  icon: string;
  enabled: boolean;
  desc: string;
}

export interface RequirementControlPanelProps {
  fullWidth?: boolean;
  onParamUpdated?: () => void;
}

export const RequirementControlPanel: React.FC<RequirementControlPanelProps> = ({ fullWidth = false, onParamUpdated }) => {
  const [brandTitle, setBrandTitle] = useState<string>("");
  const [deliverySla, setDeliverySla] = useState<string>("");
  const [savingParam, setSavingParam] = useState<boolean>(false);
  const [statusToast, setStatusToast] = useState<string | null>(null);
  const [components, setComponents] = useState<ComponentItem[]>([]);
  const [hasBrandReq, setHasBrandReq] = useState(false);
  const [hasSlaReq, setHasSlaReq] = useState(false);

  React.useEffect(() => {
    const hydrateData = async () => {
      try {
        // Fetch kickstart state for active application component blocks
        const ksRes = await fetch('/api/kickstart/state');
        const ksState = await ksRes.json();
        
        const reqRes = await fetch('/api/requirements');
        const reqs = await reqRes.json();

        // Build UI Component items list
        let componentItems: ComponentItem[] = [];

        if (ksState && Array.isArray(ksState.blocks) && ksState.blocks.length > 0) {
          // Map blocks from active kickstart session
          componentItems = ksState.blocks.map((b: any) => {
            const rawId = typeof b === 'string' ? b : b.id;
            const canonicalKey = normalizeFeatureId(rawId);
            return {
              id: canonicalKey,
              name: typeof b === 'string' ? formatBlockName(b) : (b.name || formatBlockName(rawId)),
              reqId: `REQ-${canonicalKey.toUpperCase()}-001`,
              icon: getBlockIcon(rawId),
              enabled: checkFeatureEnabled(canonicalKey, reqs),
              desc: typeof b === 'object' ? (b.description || 'Active application component') : 'Synthesized UI component block'
            };
          });
        } else if (Array.isArray(reqs)) {
          // Fallback to domain requirements if kickstart state is empty
          componentItems = reqs
            .filter((r: any) => r.id && r.title && r.id !== 'REQ-BRAND-001' && r.id !== 'REQ-DELIVERY-001')
            .map((r: any) => {
              const canonicalKey = normalizeFeatureId(r.id);
              return {
                id: canonicalKey,
                name: formatReqTitleToComponentName(r.title || r.id),
                reqId: r.id,
                icon: getReqIcon(r.id, r.title || ''),
                enabled: r.status !== 'Disabled',
                desc: truncate(r.description || r.title || '', 60)
              };
            });
        }

        setComponents(componentItems);

        // Hydrate editable params if they exist
        if (Array.isArray(reqs)) {
          const brandReq = reqs.find((r: any) => r.id === 'REQ-BRAND-001');
          if (brandReq) {
            setHasBrandReq(true);
            const txt = brandReq.title || brandReq.description || '';
            const match = txt.match(/'([^']+)'/);
            if (match) setBrandTitle(match[1]);
            else setBrandTitle(txt.replace(/^Storefront brand title set to\s*/i, '').replace(/"/g, ''));
          }

          const slaReq = reqs.find((r: any) => r.id === 'REQ-DELIVERY-001');
          if (slaReq) {
            setHasSlaReq(true);
            const txt = slaReq.title || slaReq.description || '';
            const match = txt.match(/'([^']+)'/);
            if (match) setDeliverySla(match[1]);
            else setDeliverySla(txt.replace(/^Estimated delivery SLA set to\s*/i, '').replace(/"/g, ''));
          }
        }
      } catch (e) {
        console.error("Hydration error:", e);
      }
    };
    hydrateData();
  }, []);

  const handleUpdateParam = async (paramKey: string, val: string) => {
    setSavingParam(true);
    try {
      const res = await fetch('/api/requirements/update-param', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ param_key: paramKey, value: val })
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`✨ Updated parameter: ${paramKey} = "${val}"`);
        if (onParamUpdated) onParamUpdated();
        setTimeout(() => setStatusToast(null), 3000);
      }
    } catch (e) {
      console.error("Error updating parameter:", e);
    } finally {
      setSavingParam(false);
    }
  };

  const handleToggleComponent = async (idx: number) => {
    const target = components[idx];
    const newStatus = !target.enabled;

    setComponents(prev => prev.map((c, i) => i === idx ? { ...c, enabled: newStatus } : c));

    try {
      const res = await fetch('/api/requirements/toggle-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature_id: target.id, req_id: target.reqId, enabled: newStatus })
      });
      const data = await res.json();
      if (data.success) {
        setStatusToast(`🛡️ ${target.name} ${newStatus ? 'Activated' : 'Deactivated'}`);
        if (onParamUpdated) onParamUpdated();
        setTimeout(() => setStatusToast(null), 3000);
      }
    } catch (e) {
      console.error("Error toggling component:", e);
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

      {/* Toast Feedback */}
      {statusToast && (
        <div style={{ background: 'rgba(2, 132, 199, 0.2)', border: '1px solid #0284c7', color: '#38bdf8', padding: '0.65rem 1rem', borderRadius: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}>
          {statusToast}
        </div>
      )}

      {/* DOMAIN BRAND & SPEC PARAMETERS — only show if these requirement types exist */}
      {(hasBrandReq || hasSlaReq) && (
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h4 style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
            📌 Parameters
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: fullWidth ? '1fr 1fr' : '1fr', gap: '1rem' }}>
            {hasBrandReq && (
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem', fontWeight: 600 }}>
                  Storefront Brand Title
                </label>
                <input
                  type="text"
                  value={brandTitle}
                  onChange={e => {
                    const val = e.target.value;
                    setBrandTitle(val);
                    handleUpdateParam('brand_title', val);
                  }}
                  placeholder="e.g. My Business Name"
                  style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#fff', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.9rem' }}
                />
              </div>
            )}

            {hasSlaReq && (
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.35rem', fontWeight: 600 }}>
                  Estimated Delivery SLA
                </label>
                <input
                  type="text"
                  value={deliverySla}
                  onChange={e => {
                    const val = e.target.value;
                    setDeliverySla(val);
                    handleUpdateParam('delivery_sla', val);
                  }}
                  placeholder="e.g. 20-30 MINS"
                  style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#fff', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.9rem' }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* COMPONENTS SECTION */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        <h4 style={{ margin: 0, fontSize: '0.9rem', color: '#cbd5e1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 700 }}>
          COMPONENTS ({components.length})
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: fullWidth ? 'repeat(2, 1fr)' : '1fr', gap: '0.85rem' }}>
          {components.map((item, idx) => (
            <div
              key={item.id}
              style={{
                background: item.enabled ? '#0f172a' : 'rgba(15, 23, 42, 0.4)',
                border: `1px solid ${item.enabled ? '#334155' : '#1e293b'}`,
                borderRadius: '0.75rem',
                padding: '0.9rem 1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.75rem'
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                  <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                  <strong style={{ fontSize: '0.9rem', color: item.enabled ? '#f8fafc' : '#64748b' }}>{item.name}</strong>
                </div>
                <div style={{ fontSize: '0.75rem', color: item.enabled ? '#94a3b8' : '#475569', lineHeight: 1.3 }}>{item.desc}</div>
              </div>

              {/* Toggle Switch */}
              <input
                type="checkbox"
                checked={item.enabled}
                onChange={() => handleToggleComponent(idx)}
                style={{ width: '1.25rem', height: '1.25rem', cursor: 'pointer', accentColor: '#0284c7' }}
              />
            </div>
          ))}
        </div>
      </div>

      {components.length === 0 && (
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.5rem', textAlign: 'center' }}>
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.9rem' }}>
            No components active. Submit a pitch in the Kickstart tab to generate your application stack.
          </p>
        </div>
      )}

    </div>
  );
};

// Helper: Format block IDs to human readable component names
function formatBlockName(id: str): str {
  const map: Record<string, string> = {
    'booking_calendar': 'Weekly Availability Calendar',
    'catalog_grid': 'Product & Service Catalog Grid',
    'shopping_cart': 'Shopping Cart & Checkout',
    'order_tracking': 'Live Status Pipeline',
    'user_auth': 'Customer Auth & Profiles',
    'admin_dashboard': 'Merchant Operations Dashboard',
    'reviews_ratings': 'Reviews & Ratings System'
  };
  return map[id] || id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// Helper: Clean up internal DDD requirement titles into friendly component names
function formatReqTitleToComponentName(title: str): str {
  if (title.startsWith('Record Entity')) return 'Core Domain Model & Identity';
  if (title.startsWith('Domain Invariant')) return title.replace('Domain Invariant: ', '');
  if (title.startsWith('Domain Exception')) return title.replace('Domain Exception Protection ', '');
  if (title.startsWith('Application Service')) return title.replace('Application Service ', '') + ' Action Service';
  if (title.startsWith('Transactional')) return 'Persistence & Database Sync';
  return title;
}

// Helper: pick icon for component block
function getBlockIcon(id: str): str {
  if (id.includes('calendar') || id.includes('booking')) return '📅';
  if (id.includes('catalog') || id.includes('menu')) return '📋';
  if (id.includes('cart') || id.includes('checkout')) return '🛒';
  if (id.includes('track') || id.includes('pipeline')) return '📦';
  if (id.includes('dashboard') || id.includes('admin')) return '🏪';
  if (id.includes('review') || id.includes('rating')) return '⭐';
  if (id.includes('auth') || id.includes('user') || id.includes('profile')) return '👤';
  return '🧩';
}

// Helper: pick icon for requirement
function getReqIcon(reqId: str, title: str): str {
  return getBlockIcon((reqId + ' ' + title).toLowerCase());
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + '…' : s;
}

function normalizeFeatureId(id: string): string {
  const clean = id.toLowerCase().replace(/[^a-z0-9]/g, '_');
  if (clean.includes('catalog') || clean.includes('menu')) return 'catalog';
  if (clean.includes('cart') || clean.includes('checkout')) return 'cart';
  if (clean.includes('track') || clean.includes('pipeline')) return 'tracking';
  if (clean.includes('dashboard') || clean.includes('admin') || clean.includes('kds')) return 'kds';
  if (clean.includes('review') || clean.includes('rating')) return 'reviews';
  if (clean.includes('auth') || clean.includes('user') || clean.includes('profile')) return 'auth';
  if (clean.includes('calendar') || clean.includes('booking') || clean.includes('schedule')) return 'calendar';
  return clean;
}

function checkFeatureEnabled(featureId: string, reqs: any[]): boolean {
  if (!Array.isArray(reqs)) return true;
  const canonical = normalizeFeatureId(featureId);
  const matchingReq = reqs.find((r: any) => {
    if (!r || !r.id) return false;
    const normReq = normalizeFeatureId(r.id);
    return normReq === canonical;
  });
  if (!matchingReq) return false;
  return matchingReq.status !== 'Disabled';
}
