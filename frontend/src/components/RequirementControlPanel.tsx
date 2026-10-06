import React, { useState, useEffect } from 'react';
import { RuleCardDTO, LivingDeckDTO } from '../types/api';

export interface RequirementControlPanelProps {
  fullWidth?: boolean;
  onParamUpdated?: () => void;
}

export const RequirementControlPanel: React.FC<RequirementControlPanelProps> = ({ fullWidth = false, onParamUpdated }) => {
  const [livingDeck, setLivingDeck] = useState<LivingDeckDTO | null>(null);
  const [deckFilter, setDeckFilter] = useState<'all' | 'logic' | 'views'>('all');
  const [statusToast, setStatusToast] = useState<string | null>(null);

  // New Card Form State
  const [showAddCardModal, setShowAddCardModal] = useState<boolean>(false);
  const [newCardTitle, setNewCardTitle] = useState<string>('');
  const [newCardType, setNewCardType] = useState<'LOGIC' | 'VIEW'>('LOGIC');
  const [newCardTarget, setNewCardTarget] = useState<string>('global');
  const [newGiven, setNewGiven] = useState<string>('');
  const [newWhen, setNewWhen] = useState<string>('');
  const [newThen, setNewThen] = useState<string>('');
  const [newUnless, setNewUnless] = useState<string>('');
  const [newCardChapter, setNewCardChapter] = useState<string>('General');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [collapsedChapters, setCollapsedChapters] = useState<Record<string, boolean>>({});
  const [submittingCard, setSubmittingCard] = useState<boolean>(false);
  const [executingSpecId, setExecutingSpecId] = useState<string | null>(null);
  const [editingCardId, setEditingCardId] = useState<string | null>(null);
  const [selectedCard, setSelectedCard] = useState<RuleCardDTO | null>(null);

  const resetForm = () => {
    setNewCardTitle('');
    setNewCardChapter('General');
    setNewCardTarget('global');
    setNewGiven('');
    setNewWhen('');
    setNewThen('');
    setNewUnless('');
    setEditingCardId(null);
  };

  const handleOpenEditModal = (card: RuleCardDTO) => {
    setEditingCardId(card.id);
    setNewCardTitle(card.title);
    setNewCardChapter(card.chapter || 'General');
    setNewCardType(card.card_type as 'LOGIC' | 'VIEW');
    setNewCardTarget(card.target || 'global');
    setNewGiven(card.given_clause || '');
    setNewWhen(card.when_clause || '');
    setNewThen(card.then_clause || '');
    setNewUnless(card.unless_clause || '');
    setShowAddCardModal(true);
  };


  const handleDeleteCard = async (cardId: string, title: string) => {
    if (!window.confirm(`Delete rule card "${title}"?`)) return;
    try {
      const res = await fetch(`/api/specs/deck/${cardId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setStatusToast(`🗑️ Removed card: ${title}`);
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        const data = await res.json();
        setStatusToast(`❌ Failed to delete: ${data.detail || 'Error'}`);
      }
    } catch (err) {
      console.error("Error deleting card:", err);
      setStatusToast(`❌ Network error deleting card`);
    } finally {
      setTimeout(() => setStatusToast(null), 3000);
    }
  };

  const hydrateData = async () => {
    try {
      const deckRes = await fetch('/api/specs/deck');
      if (deckRes.ok) {
        const deckData = await deckRes.json();
        setLivingDeck(deckData);
        // Sync selected card or select the first available card
        const cards: RuleCardDTO[] = deckData.all_cards && deckData.all_cards.length > 0
          ? deckData.all_cards
          : [
              ...(deckData.logic_cards?.global || []),
              ...Object.values(deckData.logic_cards?.entities || {}).flat(),
              ...(deckData.view_cards?.global_theme || []),
              ...Object.values(deckData.view_cards?.components || {}).flat()
            ];
        setSelectedCard(prev => {
          if (!prev && cards.length > 0) return cards[0];
          if (prev) {
            const updated = cards.find(c => c.id === prev.id);
            return updated || (cards.length > 0 ? cards[0] : null);
          }
          return null;
        });
      }
    } catch (e) {
      console.error("Hydration error in RequirementControlPanel:", e);
    }
  };

  useEffect(() => {
    hydrateData();
    const interval = setInterval(hydrateData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleAddCardSubmit = async () => {
    if (!newCardTitle.trim()) return;

    setSubmittingCard(true);
    try {
      const payload = {
        title: newCardTitle.trim(),
        chapter: newCardChapter.trim() || 'General',
        card_type: newCardType,
        target: newCardTarget.trim() || 'global',
        given_clause: newGiven.trim(),
        when_clause: newWhen.trim(),
        then_clause: newThen.trim(),
        unless_clause: newUnless.trim(),
        is_active: true
      };


      let res: Response;
      if (editingCardId) {
        res = await fetch(`/api/specs/deck/${editingCardId}/update`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch('/api/specs/deck/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (res.ok) {
        setStatusToast(editingCardId ? `✏️ Updated card: ${newCardTitle}` : `✨ Added ${newCardType} card: ${newCardTitle}`);
        setShowAddCardModal(false);
        resetForm();
        await hydrateData();
        if (onParamUpdated) onParamUpdated();
      } else {
        const data = await res.json();
        setStatusToast(`❌ Failed to save card: ${data.error || data.detail || 'Check server logs'}`);
      }
    } catch (err) {
      console.error("Error saving card:", err);
      setStatusToast(`❌ Network error saving card`);
    } finally {
      setSubmittingCard(false);
      setTimeout(() => setStatusToast(null), 3000);
    }
  };

  const handleExecuteSpec = async (cardId: string) => {
    setExecutingSpecId(cardId);
    setStatusToast(`⚡ Running TDD loop for ${cardId}...`);
    try {
      const res = await fetch(`/api/specs/inbox/${cardId}/execute`, { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.success) {
        setStatusToast(`🟢 Card ${cardId} verified successfully!`);
      } else {
        setStatusToast(`🔴 Card ${cardId} needs review: ${data.tdd_result?.reason || data.error || 'Test failed'}`);
      }
      await hydrateData();
      if (onParamUpdated) onParamUpdated();
    } catch (err) {
      console.error("Error executing card spec:", err);
      setStatusToast(`❌ Network error executing card`);
    } finally {
      setExecutingSpecId(null);
      setTimeout(() => setStatusToast(null), 4000);
    }
  };

  const getStatusBadge = (status?: string, isActive?: boolean) => {
    if (isActive === false || status === 'PAUSED') {
      return <span style={{ background: '#334155', color: '#cbd5e1', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>⏸️ PAUSED</span>;
    }
    switch (status) {
      case 'FULFILLED':
        return <span style={{ background: '#059669', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>🟢 VERIFIED</span>;
      case 'IN_PROGRESS':
        return <span style={{ background: '#d97706', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>⚡ RUNNING</span>;
      case 'CONFLICT':
      case 'REQUIRES_HUMAN_INTERVENTION':
        return <span style={{ background: '#dc2626', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>🔴 CONFLICT</span>;
      default:
        return <span style={{ background: '#0284c7', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>⏳ ACTIVE</span>;
    }
  };

  const getChapterIcon = (chapterName: string): string => {
    const lower = chapterName.toLowerCase();
    if (lower.includes('setup') || lower.includes('initial') || lower.includes('config') || lower.includes('start')) return '🏁';
    if (lower.includes('move') || lower.includes('action') || lower.includes('operation') || lower.includes('step')) return '🎯';
    if (lower.includes('completion') || lower.includes('outcome') || lower.includes('resolution') || lower.includes('result') || lower.includes('finish')) return '🏆';
    if (lower.includes('timing') || lower.includes('clock') || lower.includes('timer') || lower.includes('state')) return '⏳';
    if (lower.includes('interface') || lower.includes('ui') || lower.includes('canvas') || lower.includes('theme') || lower.includes('view') || lower.includes('visual') || lower.includes('responsiveness')) return '🖼️';
    if (lower.includes('telemetry') || lower.includes('status') || lower.includes('score') || lower.includes('stats') || lower.includes('counter')) return '📊';
    if (lower.includes('safety') || lower.includes('guard') || lower.includes('security') || lower.includes('boundary') || lower.includes('invariant')) return '🛡️';
    return '📁';
  };

  // Collect cards based on filter
  const allCardsList: RuleCardDTO[] = livingDeck ? (
    livingDeck.all_cards && livingDeck.all_cards.length > 0
      ? livingDeck.all_cards
      : [
          ...(livingDeck.logic_cards?.global || []),
          ...Object.values(livingDeck.logic_cards?.entities || {}).flat(),
          ...(livingDeck.view_cards?.global_theme || []),
          ...Object.values(livingDeck.view_cards?.components || {}).flat()
        ]
  ) : [];

  const allLogicCards: RuleCardDTO[] = allCardsList.filter(c => c.card_type === 'LOGIC');
  const allViewCards: RuleCardDTO[] = allCardsList.filter(c => c.card_type === 'VIEW');

  const visibleCards: RuleCardDTO[] = deckFilter === 'logic' 
    ? allLogicCards 
    : deckFilter === 'views' 
      ? allViewCards 
      : allCardsList;

  const query = searchQuery.trim().toLowerCase();
  const filteredCards = visibleCards.filter(card => {
    if (!query) return true;
    return (
      (card.title && card.title.toLowerCase().includes(query)) ||
      (card.chapter && card.chapter.toLowerCase().includes(query)) ||
      (card.category && card.category.toLowerCase().includes(query)) ||
      (card.target && card.target.toLowerCase().includes(query)) ||
      (card.given_clause && card.given_clause.toLowerCase().includes(query)) ||
      (card.when_clause && card.when_clause.toLowerCase().includes(query)) ||
      (card.then_clause && card.then_clause.toLowerCase().includes(query)) ||
      (card.unless_clause && card.unless_clause.toLowerCase().includes(query)) ||
      (card.description && card.description.toLowerCase().includes(query))
    );
  });

  const knownChapterNames = livingDeck?.chapters ? Object.keys(livingDeck.chapters) : [];

  const groupedByChapter: Record<string, RuleCardDTO[]> = {};
  for (const name of knownChapterNames) {
    groupedByChapter[name] = [];
  }
  for (const card of filteredCards) {
    const ch = card.chapter || 'General Rules';
    if (!groupedByChapter[ch]) {
      groupedByChapter[ch] = [];
    }
    groupedByChapter[ch].push(card);
  }

  const activeChapterEntries = Object.entries(groupedByChapter).filter(([_, cards]) => cards.length > 0);

  const toggleAllChapters = (collapse: boolean) => {
    const nextCollapsed: Record<string, boolean> = {};
    for (const [chName] of activeChapterEntries) {
      nextCollapsed[chName] = collapse;
    }
    setCollapsedChapters(nextCollapsed);
  };

  const toggleChapter = (chName: string) => {
    setCollapsedChapters(prev => ({
      ...prev,
      [chName]: !prev[chName]
    }));
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      width: fullWidth ? '100%' : 'auto',
      background: '#090d16',
      border: '1px solid #1e293b',
      borderRadius: '0.75rem',
      padding: '0.85rem',
      gap: '0.85rem',
      overflow: 'hidden',
      boxSizing: 'border-box'
    }}>
      {/* Panel Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '0.65rem', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>📋</span>
          <div>
            <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#f8fafc', fontWeight: 800, letterSpacing: '0.02em' }}>
              DOMAIN SPECIFICATIONS
            </h3>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8' }}>
              Behavioral Invariants &amp; View Specifications (BDD)
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowAddCardModal(true)}
          style={{
            background: '#0284c7',
            color: '#fff',
            border: 'none',
            padding: '0.35rem 0.75rem',
            borderRadius: '0.4rem',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}
        >
          ➕ Add Specification
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.4rem', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem', flexShrink: 0 }}>
        <button
          onClick={() => setDeckFilter('all')}
          style={{
            background: deckFilter === 'all' ? '#1e293b' : 'transparent',
            border: '1px solid ' + (deckFilter === 'all' ? '#38bdf8' : '#334155'),
            color: deckFilter === 'all' ? '#38bdf8' : '#94a3b8',
            padding: '0.3rem 0.6rem',
            borderRadius: '0.35rem',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          📋 All Specs ({visibleCards.length})
        </button>
        <button
          onClick={() => setDeckFilter('logic')}
          style={{
            background: deckFilter === 'logic' ? '#1e293b' : 'transparent',
            border: '1px solid ' + (deckFilter === 'logic' ? '#4ade80' : '#334155'),
            color: deckFilter === 'logic' ? '#4ade80' : '#94a3b8',
            padding: '0.3rem 0.6rem',
            borderRadius: '0.35rem',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          ⚡ Logic ({allLogicCards.length})
        </button>
        <button
          onClick={() => setDeckFilter('views')}
          style={{
            background: deckFilter === 'views' ? '#1e293b' : 'transparent',
            border: '1px solid ' + (deckFilter === 'views' ? '#c084fc' : '#334155'),
            color: deckFilter === 'views' ? '#c084fc' : '#94a3b8',
            padding: '0.3rem 0.6rem',
            borderRadius: '0.35rem',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer'
          }}
        >
          🖼️ Views &amp; Theme ({allViewCards.length})
        </button>
      </div>

      {/* Search & Overview Toolbar */}
      <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', flexShrink: 0 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            type="text"
            placeholder="🔍 Search specifications, chapters, clauses..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              background: '#0f172a',
              border: '1px solid #334155',
              color: '#f8fafc',
              borderRadius: '0.4rem',
              padding: '0.35rem 1.8rem 0.35rem 0.65rem',
              fontSize: '0.75rem',
              boxSizing: 'border-box',
              outline: 'none'
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              style={{
                position: 'absolute',
                right: '0.4rem',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        <button
          onClick={() => toggleAllChapters(true)}
          style={{
            background: 'transparent',
            border: '1px solid #334155',
            color: '#94a3b8',
            borderRadius: '0.35rem',
            padding: '0.3rem 0.5rem',
            fontSize: '0.7rem',
            cursor: 'pointer',
            whiteSpace: 'nowrap'
          }}
          title="Fold all chapters"
        >
          Fold All
        </button>
        <button
          onClick={() => toggleAllChapters(false)}
          style={{
            background: 'transparent',
            border: '1px solid #334155',
            color: '#94a3b8',
            borderRadius: '0.35rem',
            padding: '0.3rem 0.5rem',
            fontSize: '0.7rem',
            cursor: 'pointer',
            whiteSpace: 'nowrap'
          }}
          title="Expand all chapters"
        >
          Expand All
        </button>
      </div>

      {/* Toast Notification */}
      {statusToast && (
        <div style={{
          background: statusToast.includes('❌') ? '#450a0a' : '#064e3b',
          border: `1px solid ${statusToast.includes('❌') ? '#991b1b' : '#047857'}`,
          color: statusToast.includes('❌') ? '#fca5a5' : '#a7f3d0',
          padding: '0.45rem 0.75rem',
          borderRadius: '0.4rem',
          fontSize: '0.8rem',
          fontWeight: 600,
          flexShrink: 0
        }}>
          {statusToast}
        </div>
      )}

      {/* Cockpit Master-Detail Section: Outline on Left, Inspector on Right */}
      <div style={{ flex: 1, display: 'flex', minHeight: 0, gap: '0.75rem', overflow: 'hidden' }}>
        {/* Left: Scannable Chapters and Specification Titles List */}
        <div style={{
          flex: '0 0 45%',
          minWidth: '220px',
          maxWidth: '50%',
          overflowY: 'auto',
          overflowX: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.65rem',
          paddingRight: '0.4rem',
          paddingBottom: '1rem',
          borderRight: '1px solid #1e293b'
        }}>
          {filteredCards.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: '#64748b', fontSize: '0.8rem' }}>
              {searchQuery
                ? `No specifications found matching "${searchQuery}".`
                : 'No specifications in this category yet. Click ➕ Add Specification to define rules or views.'}
            </div>
          ) : (
            activeChapterEntries.map(([chapterName, chapterCards]) => {
              const isCollapsed = !!collapsedChapters[chapterName];
              return (
                <div
                  key={chapterName}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    background: '#090d16',
                    border: '1px solid #1e293b',
                    borderRadius: '0.5rem',
                    overflow: 'hidden',
                    flexShrink: 0
                  }}
                >
                  {/* Chapter Header Accordion Toggle */}
                  <button
                    onClick={() => toggleChapter(chapterName)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      background: '#0f172a',
                      border: 'none',
                      borderBottom: isCollapsed ? 'none' : '1px solid #1e293b',
                      padding: '0.45rem 0.65rem',
                      cursor: 'pointer',
                      width: '100%',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', minWidth: 0, overflow: 'hidden' }}>
                      <span style={{ fontSize: '0.85rem' }}>{getChapterIcon(chapterName)}</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {chapterName}
                      </span>
                      <span style={{
                        background: '#1e293b',
                        color: '#94a3b8',
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        padding: '0.1rem 0.35rem',
                        borderRadius: '0.25rem',
                        flexShrink: 0
                      }}>
                        {chapterCards.length}
                      </span>
                    </div>
                    <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>
                      {isCollapsed ? '▶' : '▼'}
                    </span>
                  </button>

                  {/* Chapter Cards List (Master Item) */}
                  {!isCollapsed && (
                    <div style={{ padding: '0.4rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      {chapterCards.map(card => {
                        const isSelected = selectedCard?.id === card.id;
                        const isLogic = card.card_type === 'LOGIC';

                        return (
                          <div
                            key={card.id}
                            onClick={() => setSelectedCard(card)}
                            style={{
                              background: isSelected ? 'rgba(2, 132, 199, 0.2)' : '#0f172a',
                              border: `1px solid ${isSelected ? '#0284c7' : '#1e293b'}`,
                              borderRadius: '0.4rem',
                              padding: '0.45rem 0.6rem',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              cursor: 'pointer',
                              transition: 'all 0.15s ease',
                              boxSizing: 'border-box'
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', minWidth: 0, overflow: 'hidden' }}>
                              <span style={{
                                width: '6px',
                                height: '6px',
                                borderRadius: '50%',
                                background: isLogic ? '#38bdf8' : '#c084fc',
                                flexShrink: 0
                              }} />
                              <span style={{
                                fontSize: '0.78rem',
                                color: isSelected ? '#38bdf8' : '#f1f5f9',
                                fontWeight: isSelected ? 700 : 500,
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                              }}>
                                {card.title}
                              </span>
                            </div>
                            <span style={{ fontSize: '0.7rem', color: isSelected ? '#38bdf8' : '#64748b' }}>
                              ›
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Right: Focused Specification Detail Inspector */}
        <div style={{
          flex: 1,
          minWidth: 0,
          background: '#0a0f1d',
          border: '1px solid #1e293b',
          borderRadius: '0.5rem',
          padding: '0.85rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
          overflowY: 'auto'
        }}>
          {selectedCard ? (
            <>
              {/* Detail Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #1e293b', paddingBottom: '0.65rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                    <span style={{
                      background: selectedCard.card_type === 'LOGIC' ? '#1e3a8a' : '#581c87',
                      color: selectedCard.card_type === 'LOGIC' ? '#93c5fd' : '#e9d5ff',
                      fontSize: '0.68rem',
                      fontWeight: 800,
                      padding: '0.15rem 0.45rem',
                      borderRadius: '0.3rem'
                    }}>
                      {selectedCard.card_type === 'LOGIC' ? '⚡ LOGIC' : '🖼️ VIEW'}
                    </span>
                    <span style={{
                      background: '#1e293b',
                      color: '#cbd5e1',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      padding: '0.15rem 0.45rem',
                      borderRadius: '0.3rem'
                    }}>
                      📁 {selectedCard.chapter || 'General Specifications'}
                    </span>
                    {selectedCard.target && selectedCard.target !== 'global' && (
                      <span style={{
                        background: '#334155',
                        color: '#94a3b8',
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        padding: '0.15rem 0.45rem',
                        borderRadius: '0.3rem'
                      }}>
                        🧬 {selectedCard.target}
                      </span>
                    )}
                  </div>
                  <h4 style={{ margin: '0.2rem 0 0 0', fontSize: '1rem', color: '#f8fafc', fontWeight: 800 }}>
                    {selectedCard.title}
                  </h4>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexShrink: 0 }}>
                  <button
                    onClick={() => handleOpenEditModal(selectedCard)}
                    style={{
                      background: '#1e293b',
                      border: '1px solid #475569',
                      color: '#cbd5e1',
                      borderRadius: '0.35rem',
                      padding: '0.25rem 0.6rem',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem'
                    }}
                    title="Edit Specification"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleDeleteCard(selectedCard.id, selectedCard.title)}
                    style={{
                      background: 'rgba(153, 27, 27, 0.2)',
                      border: '1px solid #dc2626',
                      color: '#f87171',
                      borderRadius: '0.35rem',
                      padding: '0.25rem 0.6rem',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem'
                    }}
                    title="Delete Specification"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>

              {/* BDD Specification Inspection Box */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Behavioral Specification (BDD)
                </span>

                {(selectedCard.given_clause || selectedCard.when_clause || selectedCard.then_clause) ? (
                  <div style={{
                    background: '#020617',
                    border: '1px solid #1e293b',
                    padding: '0.85rem',
                    borderRadius: '0.5rem',
                    fontSize: '0.82rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.6rem',
                    lineHeight: 1.5
                  }}>
                    {selectedCard.given_clause && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                        <span style={{ color: '#38bdf8', fontWeight: 800, fontSize: '0.75rem' }}>GIVEN</span>
                        <span style={{ color: '#e2e8f0', paddingLeft: '0.5rem', borderLeft: '2px solid #0284c7' }}>
                          {selectedCard.given_clause}
                        </span>
                      </div>
                    )}
                    {selectedCard.when_clause && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                        <span style={{ color: '#fbbf24', fontWeight: 800, fontSize: '0.75rem' }}>WHEN</span>
                        <span style={{ color: '#e2e8f0', paddingLeft: '0.5rem', borderLeft: '2px solid #d97706' }}>
                          {selectedCard.when_clause}
                        </span>
                      </div>
                    )}
                    {selectedCard.then_clause && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                        <span style={{ color: '#4ade80', fontWeight: 800, fontSize: '0.75rem' }}>THEN</span>
                        <span style={{ color: '#e2e8f0', paddingLeft: '0.5rem', borderLeft: '2px solid #059669' }}>
                          {selectedCard.then_clause}
                        </span>
                      </div>
                    )}
                    {selectedCard.unless_clause && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                        <span style={{ color: '#f87171', fontWeight: 800, fontSize: '0.75rem' }}>UNLESS</span>
                        <span style={{ color: '#e2e8f0', paddingLeft: '0.5rem', borderLeft: '2px solid #dc2626' }}>
                          {selectedCard.unless_clause}
                        </span>
                      </div>
                    )}
                  </div>
                ) : selectedCard.description ? (
                  <div style={{ background: '#020617', border: '1px solid #1e293b', padding: '0.85rem', borderRadius: '0.5rem', fontSize: '0.8rem', color: '#cbd5e1' }}>
                    {selectedCard.description}
                  </div>
                ) : (
                  <div style={{ background: '#020617', border: '1px dashed #334155', padding: '1rem', borderRadius: '0.5rem', fontSize: '0.8rem', color: '#64748b', textAlign: 'center' }}>
                    No BDD clauses defined for this specification yet. Click ✏️ Edit to define Given / When / Then specifications.
                  </div>
                )}
              </div>

              {/* Execution / Verification Details */}
              {selectedCard.card_type === 'LOGIC' && (
                <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    Deterministic Verification Status:
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {getStatusBadge(selectedCard.status, true)}
                    <button
                      onClick={() => handleExecuteSpec(selectedCard.id)}
                      disabled={executingSpecId === selectedCard.id}
                      style={{
                        background: '#0284c7',
                        border: 'none',
                        color: '#fff',
                        borderRadius: '0.35rem',
                        padding: '0.3rem 0.65rem',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        cursor: executingSpecId === selectedCard.id ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {executingSpecId === selectedCard.id ? '⏳ Verifying...' : '⚡ Verify Invariant'}
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b', gap: '0.5rem' }}>
              <span style={{ fontSize: '2rem' }}>👈</span>
              <p style={{ margin: 0, fontSize: '0.85rem' }}>Select any specification from the chapter outline on the left to inspect its BDD criteria.</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Specification Modal */}
      {showAddCardModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '0.75rem',
            padding: '1.25rem',
            width: '450px',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4 style={{ margin: 0, color: '#f8fafc', fontSize: '0.95rem' }}>
                {editingCardId ? '✏️ Edit Specification' : '📋 Add Specification'}
              </h4>
              <button onClick={() => { setShowAddCardModal(false); resetForm(); }} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div>
                <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Specification Type</label>
                <select
                  value={newCardType}
                  onChange={e => setNewCardType(e.target.value as 'LOGIC' | 'VIEW')}
                  style={{ width: '100%', background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.4rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
                >
                  <option value="LOGIC">⚡ LOGIC (Rule / Invariant)</option>
                  <option value="VIEW">🖼️ VIEW (Screen / Theme)</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Target Scope</label>
                <input
                  type="text"
                  placeholder="e.g. global, Bishop, ChessBoard"
                  value={newCardTarget}
                  onChange={e => setNewCardTarget(e.target.value)}
                  style={{ width: '100%', background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.4rem', borderRadius: '0.35rem', fontSize: '0.75rem', boxSizing: 'border-box' }}
                />
              </div>
            </div>

            <input
              type="text"
              placeholder="Specification Title (e.g., First Click Safety Guarantee)"
              value={newCardTitle}
              onChange={e => setNewCardTitle(e.target.value)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.4rem', borderRadius: '0.35rem', fontSize: '0.8rem' }}
            />

            <div>
              <label style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Functional Chapter</label>
              <input
                type="text"
                placeholder="e.g. Board Setup & Initialization, Player Movement"
                value={newCardChapter}
                onChange={e => setNewCardChapter(e.target.value)}
                list="chapter-suggestions"
                style={{ width: '100%', background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.4rem', borderRadius: '0.35rem', fontSize: '0.75rem', boxSizing: 'border-box' }}
              />
              <datalist id="chapter-suggestions">
                {knownChapterNames.map(ch => (
                  <option key={ch} value={ch} />
                ))}
              </datalist>
            </div>

            <input
              type="text"
              placeholder="GIVEN (Precondition)"
              value={newGiven}
              onChange={e => setNewGiven(e.target.value)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
            />
            <input
              type="text"
              placeholder="WHEN (Trigger action)"
              value={newWhen}
              onChange={e => setNewWhen(e.target.value)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
            />
            <input
              type="text"
              placeholder="THEN (Assertion)"
              value={newThen}
              onChange={e => setNewThen(e.target.value)}
              style={{ background: '#1e293b', border: '1px solid #334155', color: '#fff', padding: '0.35rem', borderRadius: '0.35rem', fontSize: '0.75rem' }}
            />

            <button
              onClick={handleAddCardSubmit}
              disabled={submittingCard || !newCardTitle.trim()}
              style={{
                background: '#0284c7',
                color: '#fff',
                border: 'none',
                padding: '0.5rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: submittingCard || !newCardTitle.trim() ? 'not-allowed' : 'pointer'
              }}
            >
              {submittingCard ? '⏳ Saving...' : (editingCardId ? '💾 Save Changes' : '✨ Add Specification')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
