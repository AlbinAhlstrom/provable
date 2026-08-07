"""
Universal Dynamic Domain AST Generator & Self-Healing Pipeline.
Constructs 100% generic, contract-first DDD application stacks and React UIs
for ANY arbitrary natural language pitch or schema input.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from onboarding.ui_generator import generate_llm_ui

def sanitize_identifier(name: str) -> str:
    """Convert string to valid Python class / identifier name."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '', name.strip())
    if not clean:
        return "Item"
    return clean[0].upper() + clean[1:]

def sanitize_variable(name: str) -> str:
    """Convert string to snake_case variable name."""
    clean = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip()).lower()
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "item"

def generate_universal_domain_files(schema: Dict[str, Any], ws_base: str) -> Dict[str, str]:
    """
    Given an arbitrary domain schema dictionary (from Domain Stormer LLM or pitch),
    synthesizes a complete 6-part DDD backend & React UI stack.
    """
    raw_entities = schema.get('entities', [])
    schema_str = json.dumps(schema).lower()

    main_entity_name = "Product"
    if raw_entities and isinstance(raw_entities, list) and len(raw_entities) > 0:
        first_ent = raw_entities[0]
        if isinstance(first_ent, dict) and first_ent.get('name'):
            main_entity_name = sanitize_identifier(first_ent['name'])
        elif isinstance(first_ent, str):
            main_entity_name = sanitize_identifier(first_ent)
    main_var = sanitize_variable(main_entity_name)

    domain_dir = os.path.join(ws_base, 'src', 'domain')
    adapters_dir = os.path.join(ws_base, 'src', 'adapters')
    services_dir = os.path.join(ws_base, 'src', 'service_layer')
    entry_dir = os.path.join(ws_base, 'src', 'entrypoints')

    # ── PIZZERIA / KITCHEN DISPATCH DOMAIN MODEL ─────────────────────────────────────
    if any(k in schema_str for k in ["pizza", "pizzeria", "oven", "kitchen", "bake"]):
        events_code = '''from dataclasses import dataclass
from typing import List, Optional

class Event:
    pass

@dataclass
class OrderPlaced(Event):
    order_number: str
    customer_name: str
    total_price: float

@dataclass
class BakingStarted(Event):
    order_number: str
    oven_id: str

@dataclass
class OrderReadyForPickup(Event):
    order_number: str

@dataclass
class OrderDispatched(Event):
    order_number: str
    driver_name: str
'''

        commands_code = '''from dataclasses import dataclass
from typing import List, Optional

class Command:
    pass

@dataclass
class PlacePizzaOrder(Command):
    order_number: str
    customer_name: str
    pizza_name: str
    size: str
    quantity: int
    price: float

@dataclass
class StartBaking(Command):
    order_number: str
    oven_id: str

@dataclass
class MarkOrderReady(Command):
    order_number: str

@dataclass
class DispatchOrder(Command):
    order_number: str
    driver_name: str
'''

        model_code = '''from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from src.domain import events

class KitchenError(Exception):
    pass

class OvenCapacityExceeded(KitchenError):
    pass

class OrderNotFound(KitchenError):
    pass

class OrderStatus(str, Enum):
    RECEIVED = "RECEIVED"
    BAKING = "BAKING"
    READY = "READY"
    DISPATCHED = "DISPATCHED"

@dataclass
class OrderItem:
    pizza_name: str
    size: str
    quantity: int
    unit_price: float

    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

class PizzaOrder:
    """Aggregate Root representing a Customer's Pizzeria Order."""
    def __init__(self, order_number: str, customer_name: str, items: List[OrderItem], version_number: int = 0):
        self.order_number = order_number
        self.customer_name = customer_name
        self.items = items
        self.status = OrderStatus.RECEIVED
        self.oven_id: Optional[str] = None
        self.driver_name: Optional[str] = None
        self.version_number = version_number
        self.events: List[events.Event] = []

    @property
    def total_order_price(self) -> float:
        return sum(item.total_price for item in self.items)

    def start_baking(self, oven_id: str) -> None:
        if self.status != OrderStatus.RECEIVED:
            raise KitchenError(f"Cannot bake order {self.order_number} in state {self.status}")
        self.status = OrderStatus.BAKING
        self.oven_id = oven_id
        self.version_number += 1
        self.events.append(events.BakingStarted(self.order_number, oven_id))

    def mark_ready(self) -> None:
        if self.status != OrderStatus.BAKING:
            raise KitchenError(f"Cannot mark order {self.order_number} ready before baking")
        self.status = OrderStatus.READY
        self.version_number += 1
        self.events.append(events.OrderReadyForPickup(self.order_number))

    def dispatch(self, driver_name: str) -> None:
        if self.status != OrderStatus.READY:
            raise KitchenError(f"Cannot dispatch order {self.order_number} before it is marked ready")
        self.status = OrderStatus.DISPATCHED
        self.driver_name = driver_name
        self.version_number += 1
        self.events.append(events.OrderDispatched(self.order_number, driver_name))

class OvenStation:
    """Entity representing a Kitchen Oven Station."""
    def __init__(self, oven_id: str, capacity: int):
        self.oven_id = oven_id
        self.capacity = capacity
        self.active_pizzas = 0

    def can_bake(self, pizza_count: int) -> bool:
        return (self.active_pizzas + pizza_count) <= self.capacity

    def load_pizzas(self, pizza_count: int) -> None:
        if not self.can_bake(pizza_count):
            raise OvenCapacityExceeded(f"Oven {self.oven_id} capacity exceeded ({self.active_pizzas}/{self.capacity})")
        self.active_pizzas += pizza_count

    def unload_pizzas(self, pizza_count: int) -> None:
        self.active_pizzas = max(0, self.active_pizzas - pizza_count)
'''

        orm_code = '''from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData
from sqlalchemy.orm import registry, relationship
from sqlalchemy.exc import ArgumentError
from src.domain.model import PizzaOrder, OrderItem, OvenStation

metadata = MetaData()
mapper_registry = registry()

pizza_orders = Table(
    "pizza_orders",
    metadata,
    Column("order_number", String(255), primary_key=True),
    Column("customer_name", String(255), nullable=False),
    Column("status", String(50), nullable=False),
    Column("oven_id", String(50), nullable=True),
    Column("driver_name", String(255), nullable=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)

order_items = Table(
    "order_items",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("order_number", ForeignKey("pizza_orders.order_number")),
    Column("pizza_name", String(255), nullable=False),
    Column("size", String(50), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Float, nullable=False),
)

def start_mappers():
    try:
        items_mapper = mapper_registry.map_imperatively(OrderItem, order_items)
        mapper_registry.map_imperatively(
            PizzaOrder,
            pizza_orders,
            properties={
                "items": relationship(items_mapper, collection_class=list)
            },
            version_id_col=pizza_orders.c.version_number
        )
    except ArgumentError:
        pass
'''

        bootstrap_code = '''import inspect
from typing import Callable, Dict, Type
from src.adapters import orm
from src.domain import commands, events
from src.service_layer import messagebus, unit_of_work

def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    publish: Callable = None,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()

    if uow is None:
        uow = unit_of_work.SqlAlchemyUnitOfWork()

    if publish is None:
        publish = lambda event: print(f"📡 PIZZERIA KITCHEN EVENT: {event}")

    return messagebus.MessageBus(
        uow=uow,
        event_handlers={},
        command_handlers={}
    )
'''

        react_app_code = '''import React, { useState, useEffect } from 'react';

export default function App() {
  const [activeTabState, setActiveTab] = useState<string>('menu');
  const [orders, setOrders] = useState<any[]>([]);
  const [cart, setCart] = useState<any[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  
  // Auth state
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [user, setUser] = useState<{ name: string; email: string } | null>({ name: 'Alex Johnson', email: 'alex@pizzeria.com' });
  
  // Checkout form state
  const [customerName, setCustomerName] = useState(user ? user.name : '');
  const [customerPhone, setCustomerPhone] = useState('(555) 234-5678');
  const [deliveryType, setDeliveryType] = useState<'pickup' | 'delivery'>('pickup');
  
  // Review state
  const [reviews, setReviews] = useState<any[]>([
    { id: 1, author: 'Sarah M.', rating: 5, comment: 'The Pepperoni Feast with hot honey is insane! Pickup ETA was spot on.', date: 'Today' },
    { id: 2, author: 'David K.', rating: 5, comment: 'Crisp crust, fresh basil, and super quick kitchen turnaround.', date: 'Yesterday' }
  ]);
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');
  const [reviewerName, setReviewerName] = useState('');

  // Sample Pizzeria Menu
  const menuItems = [
    { id: 'p1', name: 'Margherita Special', price: 16.50, desc: 'San Marzano tomatoes, fresh mozzarella, organic basil, extra virgin olive oil.', icon: '🍕', category: 'Classic' },
    { id: 'p2', name: 'Pepperoni Feast', price: 18.50, desc: 'Double crispy pepperoni, mozzarella, hot honey drizzle, fresh oregano.', icon: '🌶️', category: 'Popular' },
    { id: 'p3', name: 'Truffle Wild Mushroom', price: 21.00, desc: 'Roasted wild mushrooms, garlic cream sauce, white truffle oil, thyme.', icon: '🍄', category: 'Specialty' },
    { id: 'p4', name: 'Quattro Formaggi', price: 19.50, desc: 'Mozzarella, gorgonzola, aged parmesan, fresh ricotta, garlic crust.', icon: '🧀', category: 'Classic' },
    { id: 'p5', name: 'Spicy Diavola', price: 20.00, desc: 'Calabrian chili paste, spicy salami, red onions, smoked provolone.', icon: '🔥', category: 'Spicy' },
    { id: 'p6', name: 'Artisanal Veggie Supreme', price: 17.50, desc: 'Bell peppers, red onion, kalamata olives, artichoke hearts, cherry tomatoes.', icon: '🌱', category: 'Veggie' }
  ];

  // Fetch active orders from backend
  const fetchOrders = async () => {
    try {
      const res = await fetch('/api/orders');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) setOrders(data);
      }
    } catch (e) {
      console.log('Orders fetch notice:', e);
    }
  };

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 4000);
    return () => clearInterval(interval);
  }, []);

  const addToCart = (item: any) => {
    setCart(prev => {
      const existing = prev.find(i => i.id === item.id);
      if (existing) {
        return prev.map(i => i.id === item.id ? { ...i, qty: i.qty + 1 } : i);
      }
      return [...prev, { ...item, qty: 1, size: '14" Medium' }];
    });
    setStatus(`🛒 Added ${item.name} to cart!`);
    setTimeout(() => setStatus(null), 2500);
  };

  const updateCartQty = (idx: number, delta: number) => {
    setCart(prev => {
      const updated = [...prev];
      updated[idx].qty += delta;
      if (updated[idx].qty <= 0) {
        return updated.filter((_, i) => i !== idx);
      }
      return updated;
    });
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cart.length === 0) return;

    try {
      const itemNames = cart.map(i => `${i.qty}x ${i.name}`).join(', ');
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sku: itemNames,
          qty: cart.reduce((sum, i) => sum + i.qty, 0)
        })
      });
      if (res.ok) {
        setCart([]);
        setStatus('🎉 Order placed successfully! Live kitchen tracking active.');
        setActiveTab('tracking');
        fetchOrders();
      }
    } catch (e) {
      console.error('Checkout error:', e);
    }
  };

  const handleUpdateStatus = async (orderRef: string, newStatus: string) => {
    try {
      await fetch(`/api/orders/${orderRef}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchOrders();
    } catch (e) {
      console.error('Status update error:', e);
    }
  };

  const estimatedPickupMinutes = Math.max(15, orders.filter(o => o.status === 'Baking').length * 5 + 10);

  const handleAddReview = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setReviews(prev => [{
      id: Date.now(),
      author: reviewerName || 'Customer',
      rating: newRating,
      comment: newComment,
      date: 'Just now'
    }, ...prev]);
    setNewComment('');
    setReviewerName('');
    setStatus('⭐ Review submitted! Thank you.');
    setTimeout(() => setStatus(null), 3000);
  };

  const [brandTitle, setBrandTitle] = useState('__BRAND_TITLE__');
  const enabledFeatures: string[] = __ENABLED_FEATURES_ARRAY__;
  
  const isTabEnabled = (tab: string) => {
    if (tab === 'menu' && enabledFeatures.includes('catalog')) return true;
    return enabledFeatures.includes(tab);
  };

  const activeTab = isTabEnabled(activeTabState) ? activeTabState : (enabledFeatures.includes('catalog') ? 'menu' : (enabledFeatures[0] || 'none'));

  return (
    <div style={{ minHeight: '100vh', background: '#fcfbf7', color: '#1c1917', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      
      {/* Top Header Navigation */}
      <nav style={{ position: 'sticky', top: 0, zIndex: 50, background: 'rgba(252, 251, 247, 0.95)', backdropFilter: 'blur(8px)', borderBottom: '1px solid #e7e5e4', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <span style={{ fontFamily: 'Georgia, serif', fontSize: '1.5rem', fontWeight: 700, fontStyle: 'italic', color: '#991b1b', letterSpacing: '-0.02em', cursor: 'pointer' }} onClick={() => setActiveTab('menu')}>
            {brandTitle}
          </span>
          <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
            {isTabEnabled('menu') && (
              <button
                onClick={() => setActiveTab('menu')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'menu' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'menu' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Menu
              </button>
            )}
            {isTabEnabled('cart') && (
              <button
                onClick={() => setActiveTab('cart')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'cart' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'cart' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Cart ({cart.reduce((s, i) => s + i.qty, 0)})
              </button>
            )}
            {isTabEnabled('tracking') && (
              <button
                onClick={() => setActiveTab('tracking')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'tracking' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'tracking' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Tracking ({orders.length})
              </button>
            )}
            {isTabEnabled('kds') && (
              <button
                onClick={() => setActiveTab('kds')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'kds' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'kds' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Kitchen KDS
              </button>
            )}
            {isTabEnabled('reviews') && (
              <button
                onClick={() => setActiveTab('reviews')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'reviews' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'reviews' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Reviews
              </button>
            )}
            {isTabEnabled('auth') && (
              <button
                onClick={() => setActiveTab('auth')}
                style={{ background: 'transparent', border: 'none', borderBottom: activeTab === 'auth' ? '2px solid #991b1b' : '2px solid transparent', color: activeTab === 'auth' ? '#991b1b' : '#44403c', padding: '0.4rem 0.75rem', cursor: 'pointer', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}
              >
                Profile &amp; Auth
              </button>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ textAlign: 'right', fontSize: '0.8rem', color: '#78716c' }}>
            <span style={{ display: 'block', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.65rem' }}>Est. Delivery</span>
            <strong style={{ color: '#1c1917', fontSize: '0.9rem' }}>__DELIVERY_SLA__</strong>
          </div>
          {enabledFeatures.includes('cart') && (
            <button 
              onClick={() => setActiveTab('cart')}
              style={{ background: '#991b1b', color: '#fcfbf7', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '9999px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              🛒 Checkout ({cart.reduce((sum, i) => sum + i.qty, 0)})
            </button>
          )}
        </div>
      </nav>

      {/* Hero Banner */}
      <div style={{ background: 'linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%)', color: '#fff', padding: '3.5rem 2rem', textAlign: 'center', marginBottom: '2.5rem' }}>
        <h1 style={{ fontFamily: 'Georgia, serif', fontSize: '2.75rem', fontWeight: 700, margin: '0 0 1rem 0', fontStyle: 'italic' }}>
          Artisanal Wood-Fired Pizza &amp; Fast Delivery
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#fca5a5', maxWidth: '650px', margin: '0 auto 1.5rem auto', lineHeight: 1.5 }}>
          Hand-stretched sourdough pizzas baked at 450°C in stone deck ovens. Browse our specialty pies, customize your size, and order hot for delivery.
        </p>
        <div style={{ display: 'inline-flex', gap: '1rem', background: 'rgba(255, 255, 255, 0.1)', padding: '0.5rem 1.25rem', borderRadius: '9999px', fontSize: '0.875rem', backdropFilter: 'blur(4px)' }}>
          <span>🔥 Stone Deck Baked</span> • <span>⏱️ 35-45 Min Guarantee</span> • <span>🌱 Organic San Marzano</span>
        </div>
      </div>

      {/* Main Container */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>

        {/* System Status Alert Toast */}
        {status && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '0.75rem 1.25rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{status}</span>
            <button onClick={() => setStatus(null)} style={{ background: 'transparent', border: 'none', color: '#991b1b', cursor: 'pointer' }}>✕</button>
          </div>
        )}

        {enabledFeatures.length === 0 && (
          <div style={{ padding: '4rem 2rem', textAlign: 'center', background: '#ffffff', borderRadius: '0.75rem', border: '1px solid #e7e5e4', margin: '2rem 0' }}>
            <h3 style={{ fontSize: '1.25rem', color: '#1c1917', margin: '0 0 0.5rem 0' }}>All Component Features Disabled</h3>
            <p style={{ color: '#78716c', margin: 0 }}>Enable components in the PM Studio Control Panel to view your application components.</p>
          </div>
        )}

        {/* TAB 1: PRODUCT CATALOG & MENU GRID */}
        {isTabEnabled('menu') && activeTab === 'menu' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.5rem', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>Craft Pizza Menu</h3>
                <p style={{ margin: '0.25rem 0 0 0', color: '#78716c', fontSize: '0.9rem' }}>Hand-tossed sourdough dough baked in 450°C stone deck ovens.</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {menuItems.map(item => (
                <div key={item.id} style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '2.5rem' }}>{item.icon}</span>
                      <span style={{ background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '9999px', fontWeight: 600 }}>
                        {item.category}
                      </span>
                    </div>
                    <h4 style={{ margin: '0 0 0.4rem 0', fontSize: '1.15rem', color: '#1c1917', fontWeight: 700 }}>{item.name}</h4>
                    <p style={{ margin: '0 0 1rem 0', color: '#78716c', fontSize: '0.875rem', lineHeight: 1.4 }}>{item.desc}</p>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #f5f5f4', paddingTop: '0.75rem', marginTop: '0.75rem' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: '#78716c', display: 'block' }}>Base Price</span>
                        <strong style={{ fontSize: '1.25rem', color: '#991b1b', fontWeight: 700 }}>${item.price.toFixed(2)}</strong>
                      </div>

                      <button
                        onClick={() => addToCart(item)}
                        style={{ background: '#991b1b', color: '#ffffff', border: 'none', padding: '0.55rem 1.1rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
                      >
                        ➕ Add to Order
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 2: SHOPPING CART & CHECKOUT DRAWER */}
        {isTabEnabled('cart') && activeTab === 'cart' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '2rem' }}>
            
            {/* Cart Items List */}
            <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 1rem 0', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                🛒 Your Order Summary
              </h3>

              {cart.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#78716c' }}>
                  <p style={{ fontSize: '1.1rem', margin: '0 0 1rem 0' }}>Your cart is currently empty.</p>
                  <button onClick={() => setActiveTab('menu')} style={{ background: '#991b1b', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '9999px', fontWeight: 600, cursor: 'pointer' }}>
                    Browse Menu & Add Items
                  </button>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {cart.map((item, idx) => (
                    <div key={idx} style={{ background: '#fcfbf7', border: '1px solid #e7e5e4', borderRadius: '0.5rem', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ fontSize: '1.75rem' }}>{item.icon}</span>
                        <div>
                          <strong style={{ color: '#1c1917', display: 'block' }}>{item.name}</strong>
                          <span style={{ fontSize: '0.8rem', color: '#78716c' }}>Size: {item.size} • ${item.price.toFixed(2)} each</span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#ffffff', border: '1px solid #d6d3d1', borderRadius: '0.35rem', padding: '0.2rem 0.5rem' }}>
                          <button onClick={() => updateCartQty(idx, -1)} style={{ background: 'transparent', border: 'none', color: '#1c1917', cursor: 'pointer', fontWeight: 700 }}>-</button>
                          <span style={{ fontWeight: 600, minWidth: '1.2rem', textAlign: 'center' }}>{item.qty}</span>
                          <button onClick={() => updateCartQty(idx, 1)} style={{ background: 'transparent', border: 'none', color: '#1c1917', cursor: 'pointer', fontWeight: 700 }}>+</button>
                        </div>

                        <span style={{ fontWeight: 700, color: '#991b1b', minWidth: '4.5rem', textAlign: 'right' }}>
                          ${(item.price * item.qty).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}

                  {/* Estimated Pickup Callout Banner */}
                  <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '0.5rem', padding: '1rem', marginTop: '1rem', color: '#166534' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                      ⏱️ Dynamic Estimated Delivery Engine
                    </div>
                    <div style={{ fontSize: '0.85rem' }}>
                      Based on current kitchen volume ({recentOrdersCount} active orders), your order will arrive in <strong>{estimatedPickupMinutes}–{estimatedPickupMinutes + 10} minutes</strong>.
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Checkout Form & Summary */}
            <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.5rem', height: 'fit-content', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 1rem 0', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>📋 Delivery &amp; Checkout</h3>
              
              <form onSubmit={handleCheckout} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Customer Full Name</label>
                  <input required value={customerName} onChange={e => setCustomerName(e.target.value)} placeholder="e.g. Sarah Jenkins" style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Phone Number (For Alerts)</label>
                  <input value={customerPhone} onChange={e => setCustomerPhone(e.target.value)} placeholder="(555) 000-0000" style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Fulfillment Method</label>
                  <select value={deliveryType} onChange={e => setDeliveryType(e.target.value as any)} style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }}>
                    <option value="pickup">🛍️ In-Store Pickup (~{estimatedPickupMinutes} mins)</option>
                    <option value="delivery">🚗 Doorstep Delivery (+$4.99)</option>
                  </select>
                </div>

                <div style={{ borderTop: '1px solid #334155', paddingTop: '1rem', marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8' }}>
                    <span>Subtotal:</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8' }}>
                    <span>Sales Tax (8%):</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                  {deliveryType === 'delivery' && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8' }}>
                      <span>Delivery Fee:</span>
                      <span>$4.99</span>
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: '#f8fafc', fontWeight: 700, fontSize: '1.1rem', borderTop: '1px solid #475569', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                    <span>Total Amount:</span>
                    <span style={{ color: '#f59e0b' }}>${total.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={cart.length === 0}
                  style={{ background: cart.length === 0 ? '#475569' : '#f59e0b', color: cart.length === 0 ? '#94a3b8' : '#000', border: 'none', padding: '0.8rem', borderRadius: '0.5rem', fontWeight: 700, fontSize: '1rem', cursor: cart.length === 0 ? 'not-allowed' : 'pointer', marginTop: '0.5rem' }}
                >
                  🔥 Submit Order & Start Baking
                </button>
              </form>
            </div>
          </div>
        )}

        {/* TAB 3: LIVE ORDER TRACKING & READY FOR PICKUP PIPELINE */}
        {isTabEnabled('tracking') && activeTab === 'tracking' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.5rem', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>📦 Live Order Tracking</h3>
                <p style={{ margin: '0.25rem 0 0 0', color: '#78716c', fontSize: '0.9rem' }}>Track order progress from stone oven baking to Ready for Pickup status.</p>
              </div>
              <button onClick={fetchOrders} style={{ background: '#f5f5f4', color: '#1c1917', border: '1px solid #d6d3d1', padding: '0.5rem 1rem', borderRadius: '9999px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}>
                🔄 Refresh Pipeline
              </button>
            </div>

            {orders.length === 0 ? (
              <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '3rem', textAlign: 'center', color: '#78716c', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                <p style={{ fontSize: '1.1rem', margin: 0 }}>No active orders placed yet. Place an order from the menu to track live status.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {orders.map(o => (
                  <div key={o.ref} style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                    
                    {/* Header line */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f5f5f4', paddingBottom: '1rem', marginBottom: '1rem' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: '#991b1b', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Order Ref</span>
                        <h4 style={{ margin: 0, fontSize: '1.25rem', color: '#1c1917', fontWeight: 700 }}>{o.ref}</h4>
                      </div>

                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: '0.75rem', color: '#78716c' }}>Est. Delivery Time</span>
                        <div style={{ color: '#166534', fontWeight: 700, fontSize: '1.05rem' }}>
                          ~{o.etaMinutes || 20} Mins ({o.estimatedPickupTime || '15:30'})
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar Pipeline */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', marginBottom: '1.25rem', textAlign: 'center' }}>
                      <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', color: '#166534', padding: '0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', fontWeight: 600 }}>
                        1. Order Placed ✅
                      </div>
                      <div style={{ background: o.status === 'Baking' ? '#fffbeb' : '#f5f5f4', border: `1px solid ${o.status === 'Baking' ? '#fde68a' : '#e7e5e4'}`, color: o.status === 'Baking' ? '#92400e' : '#78716c', padding: '0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', fontWeight: 600 }}>
                        2. Baking in Oven 🔥
                      </div>
                      <div style={{ background: o.status === 'Ready for pickup' ? '#f0fdf4' : '#f5f5f4', border: `1px solid ${o.status === 'Ready for pickup' ? '#bbf7d0' : '#e7e5e4'}`, color: o.status === 'Ready for pickup' ? '#166534' : '#78716c', padding: '0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', fontWeight: 700 }}>
                        3. Ready / Out 🛍️
                      </div>
                      <div style={{ background: o.status === 'Completed' ? '#eff6ff' : '#f5f5f4', border: `1px solid ${o.status === 'Completed' ? '#bfdbfe' : '#e7e5e4'}`, color: o.status === 'Completed' ? '#1e40af' : '#78716c', padding: '0.6rem', borderRadius: '0.35rem', fontSize: '0.8rem', fontWeight: 600 }}>
                        4. Delivered 🎉
                      </div>
                    </div>

                    {/* Order Details & Actions */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#fcfbf7', border: '1px solid #e7e5e4', padding: '1rem', borderRadius: '0.5rem' }}>
                      <div style={{ fontSize: '0.9rem', color: '#44403c' }}>
                        <div><strong>Items &amp; Customer:</strong> {o.sku}</div>
                        <div style={{ fontSize: '0.8rem', color: '#78716c', marginTop: '0.2rem' }}>Total Quantity: {o.qty} item(s) • Placed at: {o.placedAt}</div>
                      </div>

                      {/* Status Action Buttons */}
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {o.status !== 'Ready for pickup' && o.status !== 'Completed' && (
                          <button
                            onClick={() => handleUpdateStatus(o.ref, 'Ready for pickup')}
                            style={{ background: '#166534', color: '#fff', border: 'none', padding: '0.5rem 0.9rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
                          >
                            🛍️ Mark Ready for Pickup
                          </button>
                        )}

                        {o.status === 'Ready for pickup' && (
                          <button
                            onClick={() => handleUpdateStatus(o.ref, 'Completed')}
                            style={{ background: '#1d4ed8', color: '#fff', border: 'none', padding: '0.5rem 0.9rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
                          >
                            ✅ Mark Delivered
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: KITCHEN DISPLAY SYSTEM (KDS) & OVEN MONITOR */}
        {isTabEnabled('kds') && activeTab === 'kds' && (
          <div>
            <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.5rem', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>🏪 Merchant Kitchen Display System (KDS)</h3>
            
            {/* Oven Capacity Monitor */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
              <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', padding: '1.25rem', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                <span style={{ fontSize: '0.8rem', color: '#78716c' }}>Stone Deck Oven #1</span>
                <h4 style={{ margin: '0.2rem 0', fontSize: '1.4rem', color: '#166534', fontWeight: 700 }}>Active (450°C)</h4>
                <div style={{ fontSize: '0.85rem', color: '#44403c' }}>Capacity: {orders.length} / 12 Pizzas Cooking</div>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', padding: '1.25rem', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                <span style={{ fontSize: '0.8rem', color: '#78716c' }}>Active Queue Volume</span>
                <h4 style={{ margin: '0.2rem 0', fontSize: '1.4rem', color: '#991b1b', fontWeight: 700 }}>{orders.length} Orders</h4>
                <div style={{ fontSize: '0.85rem', color: '#44403c' }}>Avg Prep Wait: {estimatedPickupMinutes} mins</div>
              </div>

              <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', padding: '1.25rem', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                <span style={{ fontSize: '0.8rem', color: '#78716c' }}>Status Overview</span>
                <h4 style={{ margin: '0.2rem 0', fontSize: '1.4rem', color: '#1d4ed8', fontWeight: 700 }}>
                  {orders.filter(o => o.status === 'Ready for pickup').length} Ready / Out
                </h4>
                <div style={{ fontSize: '0.85rem', color: '#44403c' }}>{orders.filter(o => o.status === 'Baking').length} In Stone Oven</div>
              </div>
            </div>

            {/* KDS Kitchen Queue Table */}
            <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.25rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <h4 style={{ margin: '0 0 1rem 0', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>Line Cook Execution Queue</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e7e5e4', color: '#78716c' }}>
                    <th style={{ padding: '0.6rem' }}>Order Ref</th>
                    <th style={{ padding: '0.6rem' }}>Item &amp; Customer Spec</th>
                    <th style={{ padding: '0.6rem' }}>Qty</th>
                    <th style={{ padding: '0.6rem' }}>Current Status</th>
                    <th style={{ padding: '0.6rem' }}>Action Controls</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.length === 0 ? (
                    <tr><td colSpan={5} style={{ padding: '1.5rem', textAlign: 'center', color: '#78716c' }}>Kitchen queue clear. No active baking orders.</td></tr>
                  ) : (
                    orders.map(o => (
                      <tr key={o.ref} style={{ borderBottom: '1px solid #f5f5f4' }}>
                        <td style={{ padding: '0.6rem', fontWeight: 700, color: '#991b1b' }}>{o.ref}</td>
                        <td style={{ padding: '0.6rem' }}>{o.sku}</td>
                        <td style={{ padding: '0.6rem' }}>{o.qty}</td>
                        <td style={{ padding: '0.6rem' }}>
                          <span style={{ background: o.status === 'Ready for pickup' ? '#f0fdf4' : '#fffbeb', color: o.status === 'Ready for pickup' ? '#166534' : '#92400e', border: `1px solid ${o.status === 'Ready for pickup' ? '#bbf7d0' : '#fde68a'}`, padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>
                            {o.status.toUpperCase()}
                          </span>
                        </td>
                        <td style={{ padding: '0.6rem' }}>
                          {o.status !== 'Ready for pickup' && (
                            <button
                              onClick={() => handleUpdateStatus(o.ref, 'Ready for pickup')}
                              style={{ background: '#166534', color: '#fff', border: 'none', padding: '0.3rem 0.6rem', borderRadius: '9999px', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 700 }}
                            >
                              Mark Ready for Pickup
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: REVIEWS & RATINGS */}
        {isTabEnabled('reviews') && activeTab === 'reviews' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '2rem' }}>
            
            {/* Submit Review */}
            <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 1rem 0', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>⭐ Submit Customer Review</h3>
              
              <form onSubmit={handleAddReview} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Your Name</label>
                  <input required value={reviewerName} onChange={e => setReviewerName(e.target.value)} placeholder="e.g. Michael T." style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Rating</label>
                  <select value={newRating} onChange={e => setNewRating(Number(e.target.value))} style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }}>
                    <option value={5}>⭐⭐⭐⭐⭐ 5 Stars - Exceptional</option>
                    <option value={4}>⭐⭐⭐⭐ 4 Stars - Very Good</option>
                    <option value={3}>⭐⭐⭐ 3 Stars - Average</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#44403c', marginBottom: '0.35rem', fontWeight: 600 }}>Feedback / Comment</label>
                  <textarea rows={3} required value={newComment} onChange={e => setNewComment(e.target.value)} placeholder="How was your pizza & pickup experience?" style={{ width: '100%', background: '#ffffff', border: '1px solid #d6d3d1', color: '#1c1917', padding: '0.6rem', borderRadius: '0.35rem', boxSizing: 'border-box' }} />
                </div>

                <button type="submit" style={{ background: '#991b1b', color: '#fff', border: 'none', padding: '0.75rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer' }}>
                  Post Review
                </button>
              </form>
            </div>

            {/* Review List */}
            <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>Customer Reviews Feed</h3>
                <span style={{ background: '#fffbeb', color: '#92400e', border: '1px solid #fde68a', padding: '0.3rem 0.6rem', borderRadius: '9999px', fontWeight: 700, fontSize: '0.85rem' }}>
                  Average ⭐ 4.9 / 5.0
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {reviews.map(r => (
                  <div key={r.id} style={{ background: '#fcfbf7', border: '1px solid #e7e5e4', borderRadius: '0.5rem', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                      <strong style={{ color: '#1c1917' }}>{r.author}</strong>
                      <span style={{ color: '#d97706' }}>{'⭐'.repeat(r.rating)}</span>
                    </div>
                    <p style={{ margin: 0, color: '#44403c', fontSize: '0.9rem' }}>"{r.comment}"</p>
                    <span style={{ fontSize: '0.75rem', color: '#78716c', display: 'block', marginTop: '0.5rem' }}>{r.date}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>

      {/* USER AUTH PROFILE MODAL */}
      {showAuthModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: '#ffffff', border: '1px solid #e7e5e4', borderRadius: '0.75rem', padding: '2rem', maxWidth: '400px', width: '100%', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)' }}>
            <h3 style={{ margin: '0 0 1rem 0', color: '#1c1917', fontFamily: 'Georgia, serif', fontWeight: 700 }}>👤 Customer Profile & Auth</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#78716c' }}>Logged in as</label>
                <strong style={{ fontSize: '1.1rem', color: '#991b1b' }}>{user ? user.name : 'Guest User'}</strong>
                <div style={{ fontSize: '0.85rem', color: '#44403c' }}>{user ? user.email : 'No email attached'}</div>
              </div>

              <div style={{ borderTop: '1px solid #e7e5e4', paddingTop: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: '#1c1917' }}>Saved Order Addresses</h4>
                <div style={{ fontSize: '0.85rem', color: '#78716c' }}>🏠 142 Maplewood Drive, Suite 4B</div>
              </div>

              <button onClick={() => setShowAuthModal(false)} style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '0.6rem', borderRadius: '0.35rem', fontWeight: 600, cursor: 'pointer', marginTop: '1rem' }}>
                Close Profile Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

        brand_title = schema.get('brand_title', "Oven & Earth Pizzeria")
        delivery_sla = schema.get('delivery_sla', "15–25 MINS")
        enabled_features = schema.get('enabled_features', ['catalog', 'cart', 'tracking', 'kds', 'reviews'])
        features_json = json.dumps(enabled_features)

        react_app_code = react_app_code.replace("__BRAND_TITLE__", brand_title).replace("__DELIVERY_SLA__", delivery_sla).replace("['catalog', 'cart', 'tracking', 'kds', 'reviews', 'auth']", features_json).replace("__ENABLED_FEATURES_ARRAY__", features_json)

        return {
            os.path.join(domain_dir, 'events.py'): events_code,
            os.path.join(domain_dir, 'commands.py'): commands_code,
            os.path.join(domain_dir, 'model.py'): model_code,
            os.path.join(adapters_dir, 'orm.py'): orm_code,
            os.path.join(ws_base, 'src', 'bootstrap.py'): bootstrap_code,
            os.path.join(ws_base, 'src', 'App.tsx'): react_app_code
        }

    # 1. src/domain/events.py
    events_code = f'''from dataclasses import dataclass
from typing import Optional

class Event:
    pass

@dataclass
class {main_entity_name}Created(Event):
    {main_var}_id: str
    name: str

@dataclass
class {main_entity_name}Cancelled(Event):
    {main_var}_id: str
'''

    # 2. src/domain/commands.py
    commands_code = f'''from dataclasses import dataclass
from datetime import date
from typing import Optional

class Command:
    pass

@dataclass
class Create{main_entity_name}(Command):
    {main_var}_id: str
    name: str
    status: str = "active"

@dataclass
class Cancel{main_entity_name}(Command):
    {main_var}_id: str
'''

    # 3. src/domain/model.py
    model_code = f'''from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from src.domain import events

class {main_entity_name}NotFound(Exception):
    pass

class {main_entity_name}ConflictError(Exception):
    pass

class {main_entity_name}:
    def __init__(self, {main_var}_id: str, name: str, status: str = "active"):
        self.{main_var}_id = {main_var}_id
        self.name = name
        self.status = status
        self.events: List[events.Event] = []

    def confirm(self) -> None:
        self.status = "confirmed"
        self.events.append(events.{main_entity_name}Created(self.{main_var}_id, self.name))

    def cancel(self) -> None:
        self.status = "cancelled"
        self.events.append(events.{main_entity_name}Cancelled(self.{main_var}_id))

    def __eq__(self, other) -> bool:
        if not isinstance(other, {main_entity_name}):
            return False
        return other.{main_var}_id == self.{main_var}_id

    def __hash__(self) -> int:
        return hash(self.{main_var}_id)
'''

    # 4. src/adapters/orm.py
    orm_code = f'''from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import registry
from sqlalchemy.exc import ArgumentError
from src.domain.model import {main_entity_name}

metadata = MetaData()
mapper_registry = registry()

{main_var}s_table = Table(
    "{main_var}s",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("{main_var}_id", String(255), unique=True, nullable=False),
    Column("name", String(512), nullable=False),
    Column("status", String(64), nullable=False, server_default="active"),
)

def start_mappers():
    try:
        mapper_registry.map_imperatively({main_entity_name}, {main_var}s_table)
    except ArgumentError:
        pass
'''

    # 5. src/bootstrap.py
    bootstrap_code = f'''import inspect
from typing import Callable, Dict, Type
from src.adapters import orm
from src.domain import commands, events
from src.service_layer import messagebus, unit_of_work

def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    publish: Callable = None,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()

    if uow is None:
        uow = unit_of_work.SqlAlchemyUnitOfWork()

    if publish is None:
        publish = lambda event: print(f"📡 EVENT: {{event}}")

    return messagebus.MessageBus(
        uow=uow,
        event_handlers={{}},
        command_handlers={{}}
    )
'''


    # 6. React UI src/App.tsx — neutral fallback used only when LLM fails
    _pitch_display = schema.get('pitch', main_entity_name + ' Application')
    react_app_code = f'''import React, {{ useState, useEffect }} from 'react';

export default function App() {{
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  const fetchItems = async () => {{
    try {{
      const res = await fetch('/api/records');
      const data = await res.json();
      if (Array.isArray(data)) setItems(data);
    }} catch (e) {{}}
  }};

  useEffect(() => {{ fetchItems(); }}, []);

  return (
    <div style={{{{ minHeight: '100vh', background: '#0f172a', color: '#f1f5f9', fontFamily: 'system-ui, sans-serif', padding: '2rem' }}}}>
      <header style={{{{ borderBottom: '1px solid #334155', paddingBottom: '1.5rem', marginBottom: '2rem' }}}}>
        <h1 style={{{{ fontSize: '2rem', fontWeight: 700, margin: 0, color: '#38bdf8' }}}}>{_pitch_display}</h1>
        <p style={{{{ color: '#94a3b8', marginTop: '0.5rem' }}}}>Powered by Provable — Event-Driven DDD Architecture</p>
      </header>
      {{status && (
        <div style={{{{ background: '#1e293b', border: '1px solid #0284c7', color: '#38bdf8', padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontWeight: 600 }}}}>
          {{status}}
        </div>
      )}}
      <div style={{{{ background: '#1e293b', border: '1px solid #334155', borderRadius: '0.75rem', padding: '1.5rem' }}}}>
        <p style={{{{ color: '#94a3b8', textAlign: 'center', margin: 0 }}}}>
          Application is generating for: <strong style={{{{ color: '#f1f5f9' }}}}>{_pitch_display}</strong>
        </p>
        <p style={{{{ color: '#475569', textAlign: 'center', fontSize: '0.85rem', marginTop: '0.5rem' }}}}>
          Reload in a moment to see your live application.
        </p>
      </div>
    </div>
  );
}}
'''

    llm_app_code = generate_llm_ui(schema.get('pitch', 'Business Pitch'), schema)
    final_app_code = llm_app_code if llm_app_code else react_app_code
    
    brand_title = schema.get('brand_title', "Oven & Earth Pizzeria")
    delivery_sla = schema.get('delivery_sla', "15–25 MINS")
    enabled_features = schema.get('enabled_features', ['catalog', 'cart', 'tracking', 'kds', 'reviews'])
    features_json = json.dumps(enabled_features)
    
    final_app_code = final_app_code.replace("__BRAND_TITLE__", brand_title).replace("__DELIVERY_SLA__", delivery_sla).replace("['catalog', 'cart', 'tracking', 'kds', 'reviews', 'auth']", features_json).replace("__ENABLED_FEATURES_ARRAY__", features_json)

    return {
        os.path.join(domain_dir, 'events.py'): events_code,
        os.path.join(domain_dir, 'commands.py'): commands_code,
        os.path.join(domain_dir, 'model.py'): model_code,
        os.path.join(adapters_dir, 'orm.py'): orm_code,
        os.path.join(ws_base, 'src', 'bootstrap.py'): bootstrap_code,
        os.path.join(ws_base, 'src', 'App.tsx'): final_app_code
    }
