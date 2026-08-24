import { useState, useEffect } from 'react';
import { RequirementControlPanel } from './RequirementControlPanel';
import { PageSelectorBar } from './PageSelectorBar';
import { PageDTO } from '../types/api';

export interface AppPreviewProps {
  onResetWorkspace?: () => void;
  resetting?: boolean;
  resetMessage?: string | null;
}

interface DomainClassField {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}

interface DomainClassModel {
  name: string;
  docstring: string;
  fields: DomainClassField[];
  invariants: string[];
  methods: string[];
}

const DEFAULT_WMS_DOMAIN_SCHEMA: DomainClassModel[] = [
  {
    name: 'Pallet',
    docstring: 'Pure aggregate root representing an inventory unit in the warehouse.',
    fields: [
      { name: 'id', type: 'str', required: true, description: 'Unique pallet tracking identifier' },
      { name: 'weight', type: 'float', required: true, description: 'Total pallet weight in kg' },
      { name: 'status', type: 'str', required: true, description: 'PENDING | STORED | QUARANTINED' },
      { name: 'zone_id', type: 'Optional[str]', required: false, description: 'Assigned storage zone' },
      { name: 'sku', type: 'str', required: true, description: 'Stock keeping unit identifier' }
    ],
    invariants: [
      'Weight must be strictly greater than 0.0 kg',
      'Cannot transition to STORED without an assigned zone_id',
      'Expired pallets transition to QUARANTINED state'
    ],
    methods: [
      'assign_zone(zone: Zone) -> None',
      'check_expiration(current_date: date) -> None',
      'quarantine(reason: str) -> None'
    ]
  },
  {
    name: 'Zone',
    docstring: 'Storage location with strict capacity and weight constraints.',
    fields: [
      { name: 'id', type: 'str', required: true, description: 'Zone code e.g. ZONE-A1' },
      { name: 'name', type: 'str', required: true, description: 'Human-readable zone label' },
      { name: 'max_capacity', type: 'int', required: true, description: 'Maximum allowable pallets' },
      { name: 'current_pallets', type: 'List[str]', required: true, description: 'List of pallet IDs currently stored' }
    ],
    invariants: [
      'len(current_pallets) <= max_capacity (raises CapacityExceededError)'
    ],
    methods: [
      'add_pallet(pallet_id: str) -> None',
      'remove_pallet(pallet_id: str) -> None',
      'is_full() -> bool'
    ]
  },
  {
    name: 'Operator',
    docstring: 'Forklift operator certified for designated storage zones.',
    fields: [
      { name: 'id', type: 'str', required: true, description: 'Operator badge ID' },
      { name: 'name', type: 'str', required: true, description: 'Full name' },
      { name: 'certified_zone', type: 'str', required: true, description: 'Zone authorization clearance' }
    ],
    invariants: [
      'Operator must be certified for the target zone before moving pallets'
    ],
    methods: [
      'move_pallet(pallet_id: str, from_zone: str, to_zone: str) -> None'
    ]
  }
];

export function AppPreview({ onResetWorkspace, resetting, resetMessage }: AppPreviewProps = {}) {
  const [activeTab, setActiveTab] = useState<'preview' | 'api' | 'domain'>('preview');
  const [deviceMode, setDeviceMode] = useState<'desktop' | 'tablet' | 'mobile'>('mobile');
  const [key, setKey] = useState(0);
  const [isSynthesized, setIsSynthesized] = useState<boolean>(false);
  const [internalResetting, setInternalResetting] = useState<boolean>(false);
  const [internalResetMessage, setInternalResetMessage] = useState<string | null>(null);

  // Pages & Views Navigation State (Single Dynamic Dashboard View)
  const [pages, setPages] = useState<PageDTO[]>([
    { id: 'dashboard', name: 'Dashboard View', route: '/', icon: '📊', is_home: true }
  ]);
  const [activePageId, setActivePageId] = useState<string>('dashboard');

  const previewUrl = activeTab === 'preview' 
    ? 'http://localhost:5174' 
    : 'http://localhost:8000/docs';

  const handleAddPage = (name: string, route: string) => {
    const newPage: PageDTO = {
      id: name.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
      name,
      route,
      icon: '📄'
    };
    setPages(prev => [...prev, newPage]);
    setActivePageId(newPage.id);
  };

  const handleDeletePage = (pageId: string) => {
    setPages(prev => prev.filter(p => p.id !== pageId));
    if (activePageId === pageId) {
      setActivePageId('dashboard');
    }
  };

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await fetch('/api/kickstart/state');
        const data = await res.json();
        if (data && typeof data.synthesized === 'boolean') {
          setIsSynthesized(data.synthesized);
        }
      } catch (err) {
        console.error("Failed to fetch kickstart state in AppPreview:", err);
      }
    };
    fetchState();
    const interval = setInterval(fetchState, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    if (onResetWorkspace) {
      onResetWorkspace();
      return;
    }
    setInternalResetting(true);
    setInternalResetMessage(null);
    try {
      const res = await fetch('/api/projects/reset-all', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setInternalResetMessage("✨ Active workspace wiped successfully.");
        setTimeout(() => setInternalResetMessage(null), 3000);
      } else {
        setInternalResetMessage("⚠️ Reset notice: " + (data.error || 'Unknown notice'));
      }
    } catch (err) {
      setInternalResetMessage("❌ Network notice resetting projects.");
    } finally {
      setInternalResetting(false);
    }
  };

  const isResettingState = resetting !== undefined ? resetting : internalResetting;
  const activeResetMessage = resetMessage !== undefined ? resetMessage : internalResetMessage;

  const getWidth = () => {
    switch (deviceMode) {
      case 'mobile': return '375px';
      case 'tablet': return '768px';
      default: return '100%';
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', flex: 1, boxSizing: 'border-box' }}>
      {/* Workspace Control Bar */}
      <div 
        className="app-preview-controls-bar"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#0f172a',
          border: '1px solid #334155',
          borderRadius: '0.75rem',
          padding: '0.5rem 1rem',
          marginBottom: '1rem',
          gap: '1rem',
          flexWrap: 'wrap'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {activeResetMessage && (
            <span style={{ fontSize: '0.8rem', color: activeResetMessage.includes('✨') ? '#4ade80' : '#f87171' }}>
              {activeResetMessage}
            </span>
          )}
          <button
            onClick={handleReset}
            disabled={isResettingState}
            style={{
              background: '#991b1b',
              color: '#fca5a5',
              border: '1px solid #dc2626',
              padding: '0.4rem 0.85rem',
              borderRadius: '0.5rem',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: isResettingState ? 'not-allowed' : 'pointer',
              opacity: isResettingState ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            {isResettingState ? '⏳ Resetting...' : '🗑️ Reset Workspace'}
          </button>
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* 3-View System Selector: Preview, API (Swagger), Domain */}
          <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.2rem' }}>
            <button
              onClick={() => setActiveTab('preview')}
              style={{
                background: activeTab === 'preview' ? '#0284c7' : 'transparent',
                color: '#f8fafc',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              📱 Preview
            </button>
            <button
              onClick={() => setActiveTab('api')}
              style={{
                background: activeTab === 'api' ? '#0284c7' : 'transparent',
                color: '#f8fafc',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              ⚡ API (Swagger)
            </button>
            <button
              onClick={() => setActiveTab('domain')}
              style={{
                background: activeTab === 'domain' ? '#0284c7' : 'transparent',
                color: '#f8fafc',
                border: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              🧬 Domain
            </button>
          </div>

          {/* Device Frame Selector (Enabled in Preview Mode) */}
          {activeTab === 'preview' && (
            <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.2rem' }}>
              <button
                onClick={() => setDeviceMode('desktop')}
                style={{ background: deviceMode === 'desktop' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
                title="Desktop View"
              >
                🖥️
              </button>
              <button
                onClick={() => setDeviceMode('tablet')}
                style={{ background: deviceMode === 'tablet' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
                title="Tablet View"
              >
                📱
              </button>
              <button
                onClick={() => setDeviceMode('mobile')}
                style={{ background: deviceMode === 'mobile' ? '#334155' : 'transparent', color: '#f8fafc', border: 'none', padding: '0.35rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', cursor: 'pointer' }}
                title="Mobile View"
              >
                📲
              </button>
            </div>
          )}

          {/* Action Buttons */}
          <button
            onClick={() => setKey(k => k + 1)}
            style={{ background: '#334155', color: '#f8fafc', border: 'none', padding: '0.45rem 0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
            title="Refresh View"
          >
            🔄
          </button>
          {activeTab !== 'domain' && (
            <button
              onClick={() => window.open(previewUrl, '_blank')}
              style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.45rem 0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
            >
              ↗ Open in New Tab
            </button>
          )}
        </div>
      </div>

      {/* Pillar 1: Top Pages & Views Selector Bar */}
      {isSynthesized && activeTab === 'preview' && (
        <PageSelectorBar
          pages={pages}
          activePageId={activePageId}
          onSelectPage={setActivePageId}
          onAddPage={handleAddPage}
          onDeletePage={handleDeletePage}
        />
      )}

      {/* Main Container: Live Preview Iframe / Domain Visualizer + Side Domain Aggregates Control Panel */}
      <div 
        className="app-preview-split"
        style={{ flex: 1, display: 'flex', gap: '1rem', minHeight: 0, overflow: 'hidden', width: '100%' }}
      >
        {/* Main Content Area */}
        <div 
          className="app-preview-frame-container"
          style={{
            width: activeTab === 'preview' ? (deviceMode === 'desktop' ? '100%' : getWidth()) : '100%',
            flex: activeTab === 'preview' ? (deviceMode === 'desktop' ? 1 : `0 0 ${getWidth()}`) : 1,
            maxWidth: activeTab === 'preview' ? (deviceMode === 'desktop' ? '100%' : getWidth()) : '100%',
            display: 'flex',
            justifyContent: 'center',
            background: '#090d16',
            borderRadius: '0.75rem',
            border: '1px solid #334155',
            padding: '0.5rem',
            overflow: 'hidden',
            transition: 'all 0.3s ease',
            boxSizing: 'border-box'
          }}
        >
          {activeTab === 'domain' ? (
            /* Domain Model JSON-driven Visualizer */
            <div style={{ width: '100%', height: '100%', overflowY: 'auto', padding: '1.25rem', boxSizing: 'border-box', background: '#0b1120', borderRadius: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.75rem' }}>
                <span style={{ fontSize: '1.4rem' }}>🧬</span>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#38bdf8', fontWeight: 700 }}>Domain Aggregates &amp; Schema Inspector</h3>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#94a3b8' }}>Abstract representation of backend Python dataclasses, invariants, and aggregate boundaries.</p>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                {DEFAULT_WMS_DOMAIN_SCHEMA.map(cls => (
                  <div key={cls.name} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <code style={{ fontSize: '1rem', color: '#a78bfa', fontWeight: 700 }}>@dataclass class {cls.name}</code>
                      <span style={{ fontSize: '0.75rem', background: '#0284c7', color: '#fff', padding: '0.15rem 0.5rem', borderRadius: '9999px', fontWeight: 600 }}>Aggregate Root</span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '0 0 0.75rem 0', fontStyle: 'italic' }}>{cls.docstring}</p>

                    {/* Attributes */}
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong style={{ fontSize: '0.75rem', color: '#f59e0b', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.35rem' }}>
                        Attributes ({cls.fields.length})
                      </strong>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {cls.fields.map(f => (
                          <div key={f.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#0f172a', padding: '0.3rem 0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem' }}>
                            <span style={{ color: '#f8fafc', fontWeight: 600 }}>{f.name}</span>
                            <span style={{ color: '#38bdf8', fontFamily: 'monospace', fontSize: '0.75rem' }}>{f.type}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Invariants */}
                    <div style={{ marginBottom: '0.75rem' }}>
                      <strong style={{ fontSize: '0.75rem', color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.35rem' }}>
                        Domain Invariants
                      </strong>
                      <ul style={{ margin: 0, paddingLeft: '1.1rem', fontSize: '0.75rem', color: '#cbd5e1' }}>
                        {cls.invariants.map((inv, idx) => (
                          <li key={idx} style={{ marginBottom: '0.2rem' }}>{inv}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Methods */}
                    <div>
                      <strong style={{ fontSize: '0.75rem', color: '#ec4899', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: '0.35rem' }}>
                        Domain Methods
                      </strong>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        {cls.methods.map((m, idx) => (
                          <code key={idx} style={{ background: '#0f172a', padding: '0.25rem 0.5rem', borderRadius: '0.35rem', fontSize: '0.75rem', color: '#f472b6' }}>
                            def {m}
                          </code>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <iframe
              key={key}
              src={previewUrl}
              title={activeTab === 'preview' ? "Live Application Preview" : "FastAPI Swagger Documentation"}
              style={{
                width: '100%',
                height: '100%',
                border: '1px solid #334155',
                borderRadius: '0.5rem',
                background: '#0f172a'
              }}
            />
          )}
        </div>

        {/* Side Domain Aggregates Control Panel */}
        {isSynthesized && (
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <RequirementControlPanel onParamUpdated={() => setKey(k => k + 1)} />
          </div>
        )}
      </div>
    </div>
  );
}


