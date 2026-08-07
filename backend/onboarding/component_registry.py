"""
Premade Component Library Registry for Provable Synthesis Engine.

Contains pre-baked, production-tested React TSX component blocks that can be safely
injected into page layout slots with high visual aesthetics.
"""

from typing import Dict, Any, List

COMPONENT_REGISTRY: Dict[str, Dict[str, Any]] = {
    "ecom_header": {
        "id": "ecom_header",
        "name": "Storefront Search Header",
        "category": "e_commerce",
        "slot": "header",
        "description": "Sticky navigation header with storefront title, search bar, and cart item counter badge.",
        "tsx_code": '''
const Header = ({ brandTitle, cartCount, onOpenCart, searchTerm, setSearchTerm }: any) => (
  <header style={{ position: 'sticky', top: 0, zIndex: 40, background: 'var(--bg-card)', borderBottom: '1px solid var(--border-color)', padding: '1rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: 'var(--shadow-card)' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, color: '#fff', fontSize: '1.2rem' }}>✨</div>
      <h1 style={{ fontSize: '1.4rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>{brandTitle}</h1>
    </div>
    <div style={{ flex: 1, maxWidth: '400px', margin: '0 2rem' }}>
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        style={{ width: '100%', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '9999px', padding: '0.5rem 1.25rem', color: 'var(--text-primary)', fontSize: '0.9rem', outline: 'none' }}
      />
    </div>
    <button onClick={onOpenCart} style={{ background: 'var(--color-primary)', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      🛒 Cart ({cartCount})
    </button>
  </header>
);
'''
    },

    "service_header": {
        "id": "service_header",
        "name": "Service Booking Navigation Header",
        "category": "service_booking",
        "slot": "header",
        "description": "Clean top navigation with brand title, quick booking status pill, and user profile badge.",
        "tsx_code": '''
const ServiceHeader = ({ brandTitle, activeBookingsCount }: any) => (
  <header style={{ position: 'sticky', top: 0, zIndex: 40, background: 'var(--bg-card)', borderBottom: '1px solid var(--border-color)', padding: '1rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: 'var(--shadow-card)' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
      <span style={{ fontSize: '1.5rem' }}>📅</span>
      <h1 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>{brandTitle}</h1>
    </div>
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <span style={{ background: 'var(--color-mint)', border: '1px solid var(--color-mint-text)', color: 'var(--color-mint-text)', fontSize: '0.8rem', padding: '0.35rem 0.85rem', borderRadius: '9999px', fontWeight: 700 }}>
        ● {activeBookingsCount} Active Reservation{activeBookingsCount === 1 ? '' : 's'}
      </span>
      <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-primary)', fontWeight: 700, fontSize: '0.9rem' }}>
        👤
      </div>
    </div>
  </header>
);
'''
    },

    "weekly_calendar_grid": {
        "id": "weekly_calendar_grid",
        "name": "Weekly Availability Slot Grid",
        "category": "service_booking",
        "slot": "main_content",
        "description": "Interactive weekly calendar matrix displaying available time slots per day.",
        "tsx_code": '''
const WeeklyCalendarGrid = ({ days, selectedSlot, onSelectSlot }: any) => (
  <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '1.25rem', padding: '1.5rem', marginBottom: '2rem', boxShadow: 'var(--shadow-card)' }}>
    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>🗓️ Weekly Available Slots</h3>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem' }}>
      {days.map((day: any) => (
        <div key={day.date} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '0.75rem', textAlign: 'center' }}>
          <div style={{ fontWeight: 700, color: 'var(--color-primary)', fontSize: '0.85rem' }}>{day.dayName}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{day.date}</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {day.slots.map((slot: string) => {
              const isSelected = selectedSlot === `${day.date}-${slot}`;
              return (
                <button
                  key={slot}
                  onClick={() => onSelectSlot(day.date, slot)}
                  style={{
                    background: isSelected ? 'var(--color-primary)' : 'var(--color-mint)',
                    border: `1px solid ${isSelected ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    color: isSelected ? '#fff' : 'var(--color-mint-text)',
                    padding: '0.4rem 0.5rem',
                    borderRadius: '0.5rem',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {slot}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  </div>
);
'''
    },

    "cart_drawer": {
        "id": "cart_drawer",
        "name": "Slide-out Cart & Checkout Drawer",
        "category": "e_commerce",
        "slot": "modal_drawer",
        "description": "Slide-over drawer for cart items, price calculations, and checkout confirmation.",
        "tsx_code": '''
const CartDrawer = ({ isOpen, onClose, items, total, onCheckout }: any) => {
  if (!isOpen) return null;
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 50, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'flex-end' }}>
      <div style={{ width: '100%', maxWidth: '420px', background: 'var(--bg-card)', borderLeft: '1px solid var(--border-color)', height: '100%', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>🛒 Your Order</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.5rem', cursor: 'pointer' }}>✕</button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0' }}>
          {items.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '3rem' }}>Your cart is empty.</p>
          ) : (
            items.map((item: any) => (
              <div key={item.id} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '0.85rem', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{item.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>${item.price} × {item.qty}</div>
                </div>
                <div style={{ fontWeight: 800, color: 'var(--color-primary)' }}>${(item.price * item.qty).toFixed(2)}</div>
              </div>
            ))
          )}
        </div>
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            <span>Total:</span>
            <span style={{ color: 'var(--color-primary)' }}>${total.toFixed(2)}</span>
          </div>
          <button onClick={onCheckout} disabled={items.length === 0} style={{ width: '100%', background: items.length === 0 ? 'var(--bg-secondary)' : 'var(--color-primary)', color: '#fff', border: 'none', padding: '0.85rem', borderRadius: '0.75rem', fontWeight: 800, fontSize: '1rem', cursor: items.length === 0 ? 'not-allowed' : 'pointer' }}>
            Confirm & Pay
          </button>
        </div>
      </div>
    </div>
  );
};
'''
    },

    "kpi_stat_bar": {
        "id": "kpi_stat_bar",
        "name": "KPI Metric Stat Bar",
        "category": "operations_dashboard",
        "slot": "kpi_bar",
        "description": "Horizontal grid of 4 key metric cards with status icons and percentage indicators.",
        "tsx_code": '''
const KpiStatBar = ({ stats }: any) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
    {stats.map((s: any) => (
      <div key={s.label} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '0.85rem', padding: '1.1rem', boxShadow: 'var(--shadow-card)' }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)', margin: '0.3rem 0', fontFamily: 'var(--font-heading)' }}>{s.value}</div>
        <div style={{ fontSize: '0.75rem', color: s.positive ? '#10b981' : '#ef4444', fontWeight: 600 }}>{s.change}</div>
      </div>
    ))}
  </div>
);
'''
    }
}


def get_component_block(block_id: str) -> Dict[str, Any]:
    """Retrieve component block by ID or None."""
    return COMPONENT_REGISTRY.get(block_id)


def is_valid_component(block_id: str) -> bool:
    """Check if block_id exists in registry."""
    return block_id in COMPONENT_REGISTRY
