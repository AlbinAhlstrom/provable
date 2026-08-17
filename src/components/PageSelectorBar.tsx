import React, { useState } from 'react';
import { PageDTO } from '../types/api';

export interface PageSelectorBarProps {
  pages: PageDTO[];
  activePageId: string;
  onSelectPage: (pageId: string) => void;
  onAddPage: (name: string, route: string) => void;
  onDeletePage: (pageId: string) => void;
}

export const PageSelectorBar: React.FC<PageSelectorBarProps> = ({
  pages,
  activePageId,
  onSelectPage,
  onAddPage,
  onDeletePage,
}) => {
  const [isAdding, setIsAdding] = useState<boolean>(false);
  const [newName, setNewName] = useState<string>('');
  const [newRoute, setNewRoute] = useState<string>('');

  const handleCreate = () => {
    if (!newName.trim() || !newRoute.trim()) return;
    const formattedRoute = newRoute.startsWith('/') ? newRoute : `/${newRoute}`;
    onAddPage(newName.trim(), formattedRoute);
    setNewName('');
    setNewRoute('');
    setIsAdding(false);
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '0.75rem',
        padding: '0.5rem 1rem',
        marginBottom: '1rem',
        gap: '1rem',
        flexWrap: 'wrap',
      }}
    >
      {/* Active Pages Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase', marginRight: '0.25rem' }}>
          📄 Pages / Views:
        </span>
        {pages.map((p) => {
          const isActive = p.id === activePageId;
          return (
            <div
              key={p.id}
              onClick={() => onSelectPage(p.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                background: isActive ? '#0284c7' : '#1e293b',
                color: isActive ? '#ffffff' : '#cbd5e1',
                border: `1px solid ${isActive ? '#38bdf8' : '#334155'}`,
                padding: '0.35rem 0.85rem',
                borderRadius: '0.5rem',
                fontSize: '0.85rem',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <span>{p.icon || '📄'}</span>
              <span>{p.name}</span>
              <span style={{ fontSize: '0.7rem', opacity: 0.75 }}>({p.route})</span>

              {!p.is_home && pages.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePage(p.id);
                  }}
                  title="Delete page"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: isActive ? '#fca5a5' : '#ef4444',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    padding: '0 0.15rem',
                    marginLeft: '0.25rem',
                  }}
                >
                  ✕
                </button>
              )}
            </div>
          );
        })}

        {/* Add Page Toggle Button */}
        {!isAdding && (
          <button
            onClick={() => setIsAdding(true)}
            style={{
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px border-dashed #0284c7',
              color: '#38bdf8',
              padding: '0.35rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
            }}
          >
            ➕ Add Page
          </button>
        )}
      </div>

      {/* Inline Form to Add New Page */}
      {isAdding && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#1e293b', padding: '0.35rem 0.75rem', borderRadius: '0.5rem', border: '1px solid #0284c7' }}>
          <input
            type="text"
            placeholder="Page Name (e.g. Checkout)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              color: '#fff',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.35rem',
              fontSize: '0.8rem',
              width: '140px',
            }}
          />
          <input
            type="text"
            placeholder="Route (e.g. /checkout)"
            value={newRoute}
            onChange={(e) => setNewRoute(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              color: '#fff',
              padding: '0.25rem 0.5rem',
              borderRadius: '0.35rem',
              fontSize: '0.8rem',
              width: '120px',
            }}
          />
          <button
            onClick={handleCreate}
            style={{
              background: '#0284c7',
              color: 'white',
              border: 'none',
              padding: '0.25rem 0.65rem',
              borderRadius: '0.35rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Create
          </button>
          <button
            onClick={() => setIsAdding(false)}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.8rem',
            }}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};
