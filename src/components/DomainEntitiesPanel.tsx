import React, { useState } from 'react';
import { DomainEntityDTO } from '../types/api';

export interface DomainEntitiesPanelProps {
  entities: DomainEntityDTO[];
  onAddEntityItem?: (entityName: string, newItem: Record<string, any>) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
}

export const DomainEntitiesPanel: React.FC<DomainEntitiesPanelProps> = ({
  entities,
  onAddEntityItem,
  isOpen,
  onToggleOpen,
}) => {
  const [selectedEntityName, setSelectedEntityName] = useState<string>(
    entities[0]?.name || 'MenuItem'
  );

  const activeEntity = entities.find((e) => e.name === selectedEntityName) || entities[0];
  const [newItemName, setNewItemName] = useState<string>('');
  const [newItemPrice, setNewItemPrice] = useState<string>('');

  const handleAddItem = () => {
    if (!newItemName.trim() || !activeEntity) return;
    const newItem = {
      name: newItemName.trim(),
      price: parseFloat(newItemPrice) || 14.99,
    };
    if (onAddEntityItem) {
      onAddEntityItem(activeEntity.name, newItem);
    }
    setNewItemName('');
    setNewItemPrice('');
  };

  if (!isOpen) {
    return (
      <button
        onClick={onToggleOpen}
        style={{
          position: 'fixed',
          bottom: '1.5rem',
          right: '1.5rem',
          background: '#0284c7',
          color: 'white',
          border: 'none',
          borderRadius: '9999px',
          padding: '0.65rem 1.25rem',
          fontWeight: 700,
          fontSize: '0.85rem',
          cursor: 'pointer',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}
      >
        🧬 Domain Entities ({entities.length})
      </button>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '1.5rem',
        right: '1.5rem',
        width: '380px',
        maxHeight: '520px',
        background: '#0f172a',
        border: '1px solid #0284c7',
        borderRadius: '1rem',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 1000,
        overflow: 'hidden',
      }}
    >
      {/* Panel Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#1e293b',
          padding: '0.75rem 1rem',
          borderBottom: '1px solid #334155',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.1rem' }}>🧬</span>
          <strong style={{ color: '#f8fafc', fontSize: '0.9rem' }}>Domain Entities &amp; Data</strong>
        </div>
        <button
          onClick={onToggleOpen}
          style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1rem' }}
        >
          ✕
        </button>
      </div>

      {/* Entity Selector Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #334155', background: '#090d16' }}>
        {entities.map((ent) => {
          const isActive = ent.name === selectedEntityName;
          return (
            <button
              key={ent.name}
              onClick={() => setSelectedEntityName(ent.name)}
              style={{
                flex: 1,
                background: isActive ? '#0f172a' : 'transparent',
                color: isActive ? '#38bdf8' : '#94a3b8',
                border: 'none',
                borderBottom: isActive ? '2px solid #38bdf8' : 'none',
                padding: '0.5rem',
                fontSize: '0.75rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              {ent.name}
            </button>
          );
        })}
      </div>

      {/* Active Entity Body */}
      {activeEntity && (
        <div style={{ padding: '0.85rem', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{activeEntity.description}</div>

          {/* Seed Data Items Table */}
          <div style={{ fontSize: '0.7rem', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>
            Entity Instances / Data Fixtures:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            {activeEntity.seed_items.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '0.4rem',
                  padding: '0.4rem 0.65rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.75rem',
                  color: '#f8fafc',
                }}
              >
                <span>{item.name || item.title || `Item #${idx + 1}`}</span>
                <span style={{ color: '#4ade80', fontWeight: 600 }}>${item.price || 14.99}</span>
              </div>
            ))}
          </div>

          {/* Quick Add Seed Item Form */}
          <div style={{ display: 'flex', gap: '0.35rem', marginTop: '0.5rem' }}>
            <input
              type="text"
              placeholder="Item name (e.g. Truffle Deluxe)"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              style={{
                flex: 2,
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#fff',
                padding: '0.3rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.75rem',
              }}
            />
            <input
              type="number"
              placeholder="Price ($)"
              value={newItemPrice}
              onChange={(e) => setNewItemPrice(e.target.value)}
              style={{
                flex: 1,
                background: '#1e293b',
                border: '1px solid #334155',
                color: '#fff',
                padding: '0.3rem 0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.75rem',
              }}
            />
            <button
              onClick={handleAddItem}
              style={{
                background: '#0284c7',
                color: 'white',
                border: 'none',
                padding: '0.3rem 0.65rem',
                borderRadius: '0.35rem',
                fontSize: '0.75rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Add
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
