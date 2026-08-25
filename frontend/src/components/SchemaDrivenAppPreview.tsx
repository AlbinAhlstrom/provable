import { useState, useEffect } from 'react';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { RJSFSchema } from '@rjsf/utils';

export interface DomainClassField {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}

export interface DomainClassModel {
  name: string;
  docstring: string;
  fields: DomainClassField[];
  invariants: string[];
  methods: string[];
}

export interface SchemaDrivenAppPreviewProps {
  domainClasses: DomainClassModel[];
  isSynthesized?: boolean;
}

export function SchemaDrivenAppPreview({ domainClasses }: SchemaDrivenAppPreviewProps) {
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [records, setRecords] = useState<Record<string, any[]>>({});
  const [formData, setFormData] = useState<any>({});
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    if (domainClasses.length > 0) {
      if (!selectedEntity || !domainClasses.find(c => c.name === selectedEntity)) {
        setSelectedEntity(domainClasses[0].name);
      }
    }
  }, [domainClasses, selectedEntity]);

  const activeClass = domainClasses.find(c => c.name === selectedEntity) || domainClasses[0];

  const mapFieldTypeToSchemaType = (pyType: string): string => {
    const t = pyType.toLowerCase();
    if (t.includes('int')) return 'integer';
    if (t.includes('float') || t.includes('number') || t.includes('decimal')) return 'number';
    if (t.includes('bool')) return 'boolean';
    return 'string';
  };

  const generateSchema = (cls?: DomainClassModel): RJSFSchema => {
    if (!cls) {
      return {
        type: 'object',
        title: 'Empty Entity Schema',
        properties: {}
      };
    }

    const properties: Record<string, any> = {};
    const required: string[] = [];

    cls.fields.forEach(f => {
      properties[f.name] = {
        type: mapFieldTypeToSchemaType(f.type),
        title: f.name.charAt(0).toUpperCase() + f.name.slice(1).replace(/_/g, ' '),
        description: f.description || `Field ${f.name} of type ${f.type}`
      };
      if (f.required) {
        required.push(f.name);
      }
    });

    return {
      type: 'object',
      title: `Projected Entity: ${cls.name}`,
      description: cls.docstring,
      required: required.length > 0 ? required : undefined,
      properties
    };
  };

  const currentSchema = generateSchema(activeClass);

  const handleSubmit = (data: { formData?: any }) => {
    if (!activeClass) return;
    const submittedData = data.formData || {};
    const entityName = activeClass.name;
    const newRecord = {
      ...submittedData,
      _id: submittedData.id || `REC-${Date.now().toString().slice(-4)}`,
      _created_at: new Date().toLocaleTimeString()
    };

    setRecords(prev => ({
      ...prev,
      [entityName]: [...(prev[entityName] || []), newRecord]
    }));

    setFormData({});
    setNotification(`✅ Created new ${entityName} record successfully.`);
    setTimeout(() => setNotification(null), 3000);
  };

  const currentRecords = activeClass ? (records[activeClass.name] || []) : [];

  if (domainClasses.length === 0) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        width: '100%',
        padding: '2rem',
        color: '#94a3b8',
        textAlign: 'center',
        background: '#0b1120',
        borderRadius: '0.5rem',
        boxSizing: 'border-box'
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔮</div>
        <h3 style={{ margin: '0 0 0.5rem 0', color: '#38bdf8', fontSize: '1.2rem', fontWeight: 700 }}>
          Pure Schema-Driven Dynamic Projection
        </h3>
        <p style={{ margin: 0, maxWidth: '480px', fontSize: '0.85rem', lineHeight: '1.5' }}>
          No static templates or hardcoded UIs. As soon as you kickstart or synthesize a domain,
          this viewport dynamically projects reactive forms and live tables directly from backend
          FastAPI OpenAPI specifications.
        </p>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      width: '100%',
      height: '100%',
      background: '#0b1120',
      borderRadius: '0.5rem',
      overflowY: 'auto',
      padding: '1.25rem',
      boxSizing: 'border-box',
      gap: '1.25rem'
    }}>
      {/* Entity Tabs Selector */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #1e293b',
        paddingBottom: '0.75rem',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>Active Aggregates:</span>
          {domainClasses.map(cls => (
            <button
              key={cls.name}
              onClick={() => {
                setSelectedEntity(cls.name);
                setFormData({});
              }}
              style={{
                background: selectedEntity === cls.name ? '#0284c7' : '#1e293b',
                color: selectedEntity === cls.name ? '#ffffff' : '#cbd5e1',
                border: '1px solid #334155',
                padding: '0.35rem 0.85rem',
                borderRadius: '0.4rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              🏛️ {cls.name}
            </button>
          ))}
        </div>

        <span style={{
          fontSize: '0.75rem',
          background: 'rgba(56, 189, 248, 0.15)',
          color: '#38bdf8',
          border: '1px solid #0284c7',
          padding: '0.2rem 0.6rem',
          borderRadius: '9999px',
          fontWeight: 700
        }}>
          ⚡ Schema-Driven (@rjsf/core)
        </span>
      </div>

      {notification && (
        <div style={{
          background: 'rgba(34, 197, 94, 0.15)',
          border: '1px solid #22c55e',
          color: '#4ade80',
          padding: '0.5rem 1rem',
          borderRadius: '0.4rem',
          fontSize: '0.8rem',
          fontWeight: 600
        }}>
          {notification}
        </div>
      )}

      {/* Main Grid: Reactive Dynamic Form & Live Projected Data Table */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '1.25rem',
        alignItems: 'start'
      }}>
        {/* Schema Form Container */}
        <div style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '0.75rem',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 700 }}>
              📝 Schema Form: {activeClass?.name}
            </h4>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              {activeClass?.fields.length || 0} fields
            </span>
          </div>

          <div className="rjsf-dark-container" style={{ fontSize: '0.85rem' }}>
            <Form
              schema={currentSchema}
              validator={validator}
              formData={formData}
              onChange={e => setFormData(e.formData)}
              onSubmit={handleSubmit}
            >
              <div style={{ marginTop: '1rem' }}>
                <button
                  type="submit"
                  style={{
                    background: '#0284c7',
                    color: '#ffffff',
                    border: 'none',
                    padding: '0.5rem 1.25rem',
                    borderRadius: '0.4rem',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    width: '100%'
                  }}
                >
                  🚀 Submit &amp; Project Entity
                </button>
              </div>
            </Form>
          </div>
        </div>

        {/* Live Data Projection Table */}
        <div style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '0.75rem',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 700 }}>
              📊 Live Entity Records ({currentRecords.length})
            </h4>
            <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontFamily: 'monospace' }}>
              Projection State: Active
            </span>
          </div>

          {currentRecords.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '2.5rem 1rem',
              color: '#64748b',
              background: '#0f172a',
              borderRadius: '0.5rem',
              border: '1px dashed #334155'
            }}>
              <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600 }}>No records created yet.</p>
              <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.75rem' }}>
                Use the schema form on the left to submit a new {activeClass?.name} instance.
              </p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #334155', borderRadius: '0.4rem' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#0f172a', borderBottom: '1px solid #334155' }}>
                    {activeClass?.fields.map(f => (
                      <th key={f.name} style={{ padding: '0.45rem 0.65rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>
                        {f.name}
                      </th>
                    ))}
                    <th style={{ padding: '0.45rem 0.65rem', color: '#94a3b8', fontWeight: 600 }}>TIME</th>
                  </tr>
                </thead>
                <tbody>
                  {currentRecords.map((rec, idx) => (
                    <tr key={idx} style={{ background: idx % 2 === 0 ? '#1e293b' : '#0f172a', borderBottom: '1px solid #334155' }}>
                      {activeClass?.fields.map(f => (
                        <td key={f.name} style={{ padding: '0.45rem 0.65rem', color: '#f8fafc', fontFamily: 'monospace' }}>
                          {String(rec[f.name] !== undefined ? rec[f.name] : '—')}
                        </td>
                      ))}
                      <td style={{ padding: '0.45rem 0.65rem', color: '#64748b', fontSize: '0.75rem' }}>
                        {rec._created_at || 'now'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
