import { useState, useEffect } from 'react';
import { RequirementControlPanel } from './RequirementControlPanel';
import { SchemaDrivenAppPreview } from './SchemaDrivenAppPreview';

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

export function AppPreview({ onResetWorkspace, resetting, resetMessage }: AppPreviewProps = {}) {
  const [activeTab, setActiveTab] = useState<'preview' | 'api' | 'domain'>('domain');
  const [key, setKey] = useState(0);
  const [isSynthesized, setIsSynthesized] = useState<boolean>(false);
  const [internalResetting, setInternalResetting] = useState<boolean>(false);
  const [internalResetMessage, setInternalResetMessage] = useState<string | null>(null);
  const [domainClasses, setDomainClasses] = useState<DomainClassModel[]>([]);

  const previewUrl = activeTab === 'preview' 
    ? 'http://localhost:5174' 
    : 'http://localhost:8001/docs';

  useEffect(() => {
    const fetchDomainAggs = async () => {
      try {
        const res = await fetch('/api/onboarding/aggregates');
        if (res.ok) {
          const data = await res.json();
          if (data && Array.isArray(data.aggregates) && data.aggregates.length > 0) {
            const loaded: DomainClassModel[] = data.aggregates.map((a: any) => ({
              name: a.name,
              docstring: a.description || `Pure aggregate root representing ${a.name} in the domain context.`,
              fields: (a.fields || a.attributes || []).map((f: any) => ({
                name: f.name,
                type: f.type || 'str',
                required: f.required !== false,
                description: `${f.name} attribute`
              })),
              invariants: a.invariants && a.invariants.length > 0 ? a.invariants : [`Strict invariant validation enforced for ${a.name}`],
              methods: [`validate_invariants() -> bool`]
            }));
            setDomainClasses(loaded);
          }
        }
      } catch (err) {
        console.error("Failed to load domain classes:", err);
      }
    };
    fetchDomainAggs();

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
      const res = await fetch('/api/onboarding/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setDomainClasses([]);
        setIsSynthesized(false);
        setKey(prev => prev + 1);
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
        {/* Status Indicator & Single Prominent Reset Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', background: 'rgba(5, 150, 105, 0.2)', border: '1px solid #059669', color: '#34d399', padding: '0.25rem 0.65rem', borderRadius: '9999px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            🟢 FastAPI Sync Active
          </span>
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

        {/* View Mode Selectors */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* 3-View System Selector: Domain ("The Engine Room"), Preview, API (Swagger) */}
          <div style={{ display: 'flex', background: '#0f172a', border: '1px solid #334155', borderRadius: '0.5rem', padding: '0.2rem' }}>
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
              🧬 Domain (The Engine Room)
            </button>
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
          </div>

          <button
            onClick={() => window.open(previewUrl, '_blank')}
            style={{ background: '#0284c7', color: 'white', border: 'none', padding: '0.45rem 0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
          >
            ↗ Open in New Tab
          </button>
        </div>
      </div>

      {/* Main View Container: Full Width & Full Height per Active Tab */}
      <div 
        className="app-preview-container"
        style={{ flex: 1, display: 'flex', minHeight: 0, overflow: 'hidden', width: '100%', borderRadius: '0.75rem', border: '1px solid #334155', background: '#090d16', boxSizing: 'border-box' }}
      >
        {activeTab === 'domain' && (
          <div style={{ flex: 1, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
            <RequirementControlPanel fullWidth={true} onParamUpdated={() => setKey(k => k + 1)} />
          </div>
        )}

        {activeTab === 'preview' && (
          <div style={{ flex: 1, width: '100%', height: '100%', display: 'flex', minHeight: 0, overflow: 'hidden' }}>
            <SchemaDrivenAppPreview
              domainClasses={domainClasses}
              isSynthesized={isSynthesized}
            />
          </div>
        )}

        {activeTab === 'api' && (
          <div style={{ flex: 1, width: '100%', height: '100%', display: 'flex', minHeight: 0, overflow: 'hidden' }}>
            <iframe
              key={key}
              src="http://localhost:8001/docs"
              title="FastAPI Swagger Documentation"
              style={{
                width: '100%',
                height: '100%',
                border: 'none',
                borderRadius: '0.5rem',
                background: '#ffffff'
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default AppPreview;
