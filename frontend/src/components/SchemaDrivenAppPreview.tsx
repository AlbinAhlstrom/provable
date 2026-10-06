import { useState, useEffect, useCallback } from 'react';
import Form from '@rjsf/mui';
import validator from '@rjsf/validator-ajv8';
import { RJSFSchema } from '@rjsf/utils';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { fetchWorkspaceEntities, createWorkspaceEntity } from '../hooks/useWorkspaceDomainData';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
    primary: {
      main: '#0284c7',
      contrastText: '#ffffff',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
    divider: '#334155',
  },
  typography: {
    fontFamily: "'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    fontSize: 13,
  },
  components: {
    MuiTextField: {
      defaultProps: {
        size: 'small',
        variant: 'outlined',
        fullWidth: true,
      },
    },
    MuiFormControl: {
      defaultProps: {
        margin: 'dense',
        fullWidth: true,
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          backgroundColor: '#0f172a',
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: '#334155',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#64748b',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#0284c7',
          },
          '& input': {
            color: '#f8fafc',
          }
        }
      }
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#94a3b8',
          '&.Mui-focused': {
            color: '#38bdf8',
          }
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: 'transparent',
          backgroundImage: 'none',
          boxShadow: 'none',
        }
      }
    }
  }
});

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
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (domainClasses.length > 0) {
      if (!selectedEntity || !domainClasses.find(c => c.name === selectedEntity)) {
        setSelectedEntity(domainClasses[0].name);
      }
    }
  }, [domainClasses, selectedEntity]);

  const activeClass = domainClasses.find(c => c.name === selectedEntity) || domainClasses[0];

  const fetchLiveRecords = useCallback(async (entityName: string) => {
    if (!entityName) return;
    setLoading(true);
    const res = await fetchWorkspaceEntities(entityName);
    if (res.success) {
      setRecords(prev => ({ ...prev, [entityName]: res.data }));
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (activeClass?.name) {
      fetchLiveRecords(activeClass.name);
    }
  }, [activeClass?.name, fetchLiveRecords]);

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

  const handleSubmit = async (data: { formData?: any }) => {
    if (!activeClass) return;
    setSubmitting(true);
    setNotification(null);
    const submittedData = data.formData || {};
    const entityName = activeClass.name;

    const res = await createWorkspaceEntity(entityName, submittedData);
    if (res.success) {
      setNotification({
        type: 'success',
        message: `✅ Created new ${entityName} record in Workspace API (:8001)`
      });
      setFormData({});
      await fetchLiveRecords(entityName);
    } else {
      setNotification({
        type: 'error',
        message: `❌ Domain / Validation Error: ${res.error}`
      });
    }
    setSubmitting(false);
    setTimeout(() => setNotification(null), 6000);
  };

  const generateSampleDataForClass = (cls: DomainClassModel, variant = 0): Record<string, any> => {
    const sample: Record<string, any> = {};
    cls.fields.forEach((f, idx) => {
      const name = f.name.toLowerCase();
      const type = mapFieldTypeToSchemaType(f.type);
      const prefix = cls.name.slice(0, 4).toUpperCase();

      if (idx === 0 || name.endsWith('_id') || name === 'id') {
        sample[f.name] = `${prefix}-${100 + variant}`;
      } else if (type === 'integer') {
        sample[f.name] = 100 + variant * 10;
      } else if (type === 'number') {
        sample[f.name] = 150.0 + variant * 50.0;
      } else if (type === 'boolean') {
        sample[f.name] = true;
      } else if (name.includes('date') || name.includes('time')) {
        sample[f.name] = '2026-09-15';
      } else if (name.includes('mail')) {
        sample[f.name] = `contact_${variant + 1}@example.com`;
      } else if (name.includes('phone') || name.includes('tel')) {
        sample[f.name] = `+4670100000${variant}`;
      } else if (name.includes('status') || name.includes('state')) {
        sample[f.name] = variant === 0 ? 'ACTIVE' : 'READY';
      } else {
        sample[f.name] = `Value_${variant + 1}`;
      }
    });
    return sample;
  };

  const handleAutofill = () => {
    if (!activeClass) return;
    const sample = generateSampleDataForClass(activeClass, records[activeClass.name]?.length || 0);
    setFormData(sample);
  };

  const handleSeedAllEntities = async () => {
    if (domainClasses.length === 0) return;
    setSubmitting(true);
    setNotification(null);
    let createdCount = 0;
    for (const cls of domainClasses) {
      const sample1 = generateSampleDataForClass(cls, 0);
      const sample2 = generateSampleDataForClass(cls, 1);
      const res1 = await createWorkspaceEntity(cls.name, sample1);
      const res2 = await createWorkspaceEntity(cls.name, sample2);
      if (res1.success) createdCount++;
      if (res2.success) createdCount++;
    }
    if (activeClass) {
      await fetchLiveRecords(activeClass.name);
    }
    setSubmitting(false);
    setNotification({
      type: 'success',
      message: `🌱 Seeded ${createdCount} sample records across all aggregates in Workspace API (:8001)!`
    });
    setTimeout(() => setNotification(null), 5000);
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
          ⚡ Schema-Driven (@rjsf/mui)
        </span>
      </div>

      {notification && (
        <div style={{
          background: notification.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
          border: `1px solid ${notification.type === 'error' ? '#ef4444' : '#22c55e'}`,
          color: notification.type === 'error' ? '#fca5a5' : '#4ade80',
          padding: '0.75rem 1rem',
          borderRadius: '0.5rem',
          fontSize: '0.85rem',
          fontWeight: 700,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
        }}>
          {notification.message}
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <button
                type="button"
                onClick={handleAutofill}
                style={{
                  background: 'rgba(56, 189, 248, 0.15)',
                  border: '1px solid #0284c7',
                  color: '#38bdf8',
                  padding: '0.2rem 0.55rem',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                ✨ Auto-fill Exempel
              </button>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                {activeClass?.fields.length || 0} fält
              </span>
            </div>
          </div>

          <div className="rjsf-dark-container" style={{ fontSize: '0.85rem' }}>
            <ThemeProvider theme={darkTheme}>
              <Form
                schema={currentSchema}
                validator={validator}
                formData={formData}
                onChange={e => setFormData(e.formData)}
                onSubmit={handleSubmit}
              >
                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                  <button
                    type="submit"
                    disabled={submitting}
                    style={{
                      background: submitting ? '#0369a1' : '#0284c7',
                      color: '#ffffff',
                      border: 'none',
                      padding: '0.65rem 1.25rem',
                      borderRadius: '0.4rem',
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      cursor: submitting ? 'not-allowed' : 'pointer',
                      flex: 1,
                      boxShadow: '0 4px 12px rgba(2, 132, 199, 0.3)',
                      transition: 'background 0.2s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    {submitting ? '⏳ Executing on Workspace API (:8001)...' : `🚀 Skapa ${activeClass?.name}`}
                  </button>
                </div>
              </Form>
            </ThemeProvider>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 700 }}>
              📊 Live Entity Records ({currentRecords.length})
            </h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                onClick={handleSeedAllEntities}
                disabled={submitting || loading}
                style={{
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  border: 'none',
                  color: '#ffffff',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: submitting || loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  boxShadow: '0 2px 6px rgba(5, 150, 105, 0.3)'
                }}
              >
                🌱 Seed Demo Data (:8001)
              </button>
              <button
                onClick={() => activeClass?.name && fetchLiveRecords(activeClass.name)}
                disabled={loading}
                style={{
                  background: '#0f172a',
                  border: '1px solid #475569',
                  color: '#f8fafc',
                  padding: '0.25rem 0.6rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem'
                }}
              >
                {loading ? '⏳ Laddar...' : '🔄 Ladda om (:8001)'}
              </button>
            </div>
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
              <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600 }}>Inga poster skapade ännu i Workspace API.</p>
              <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.75rem' }}>
                Fyll i formuläret till vänster eller kör ett POST-anrop i Swagger (:8001) för att skapa {activeClass?.name}-instanser.
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
                  </tr>
                </thead>
                <tbody>
                  {currentRecords.map((rec, idx) => (
                    <tr key={rec.id || idx} style={{ background: idx % 2 === 0 ? '#1e293b' : '#0f172a', borderBottom: '1px solid #334155' }}>
                      {activeClass?.fields.map(f => (
                        <td key={f.name} style={{ padding: '0.45rem 0.65rem', color: '#f8fafc', fontFamily: 'monospace' }}>
                          {String(rec[f.name] !== undefined ? rec[f.name] : '—')}
                        </td>
                      ))}
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
