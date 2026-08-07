"""
Kickstart Feature Block Catalog & AI Pitch Analyzer.

Maps natural language pitch prompts to pre-baked UX/UI feature blocks
(Shopping Cart, Product Catalog, Order Tracking, User Auth, Admin Dashboard, etc.)
and extracts custom domain business rules to seed into Provable's StrictDoc/SQLite requirements database.
"""

import re
import json
from typing import Dict, Any, List

FEATURE_BLOCK_CATALOG = [
    {
        "id": "catalog_grid",
        "name": "Product Catalog & Menu Grid",
        "icon": "📋",
        "category": "Customer Experience",
        "description": "Interactive grid view with category filters, product search, pricing, and detail modals.",
        "keywords": ["product", "menu", "item", "catalog", "pizza", "furniture", "book", "listing", "store", "shop"],
        "default_selected": True
    },
    {
        "id": "shopping_cart",
        "name": "Shopping Cart & Checkout",
        "icon": "🛒",
        "category": "E-Commerce",
        "description": "Slide-out cart drawer, quantity modifiers, price calculations, and checkout form.",
        "keywords": ["cart", "order", "buy", "checkout", "purchase", "pay", "pizza", "retail", "shop", "price"],
        "default_selected": True
    },
    {
        "id": "order_tracking",
        "name": "Live Order Tracking & Pipeline",
        "icon": "📦",
        "category": "Operations",
        "description": "Real-time visual status pipeline (Placed → Baking/Processing → Ready → Delivered).",
        "keywords": ["track", "status", "delivery", "dispatch", "order", "pipeline", "progress", "eta", "shipment"],
        "default_selected": True
    },
    {
        "id": "user_auth",
        "name": "Customer Profiles & Authentication",
        "icon": "👤",
        "category": "Security",
        "description": "User login/signup modals, saved addresses, and order history view.",
        "keywords": ["user", "customer", "account", "login", "profile", "auth", "member", "signup"],
        "default_selected": False
    },
    {
        "id": "booking_calendar",
        "name": "Appointment & Slot Booking",
        "icon": "📅",
        "category": "Services",
        "description": "Interactive date/time slot picker, staff selection, and reservation confirmation.",
        "keywords": ["book", "appointment", "reserve", "slot", "schedule", "calendar", "time", "date", "hospital", "clinic"],
        "default_selected": False
    },
    {
        "id": "admin_dashboard",
        "name": "Merchant & Operational Dashboard",
        "icon": "🏪",
        "category": "Management",
        "description": "Kitchen display system / admin metrics, status update toggles, and inventory counts.",
        "keywords": ["admin", "dashboard", "kitchen", "cook", "manage", "merchant", "staff", "inventory", "batch", "oven"],
        "default_selected": True
    },
    {
        "id": "reviews_ratings",
        "name": "Reviews & Rating System",
        "icon": "⭐",
        "category": "Engagement",
        "description": "Customer feedback collection, star rating components, and review list display.",
        "keywords": ["review", "rating", "star", "feedback", "comment", "score"],
        "default_selected": False
    }
]


def analyze_pitch_for_kickstart(pitch: str) -> Dict[str, Any]:
    """
    Analyzes a natural language business pitch to match recommended feature blocks
    and extract domain business requirements.
    """
    pitch_lower = pitch.lower()
    
    # 1. Match catalog blocks dynamically based on pitch relevance (no hardcoded default selection forcing)
    analyzed_blocks = []
    for block in FEATURE_BLOCK_CATALOG:
        match_count = sum(1 for kw in block["keywords"] if kw in pitch_lower)
        is_recommended = match_count > 0
        
        analyzed_blocks.append({
            "id": block["id"],
            "name": block["name"],
            "icon": block["icon"],
            "category": block["category"],
            "description": block["description"],
            "is_recommended": is_recommended,
            "selected": is_recommended,
            "relevance_score": match_count
        })
        
    # Sort blocks by relevance
    analyzed_blocks.sort(key=lambda x: (x["is_recommended"], x["relevance_score"]), reverse=True)
    
    # 2. Extract Business Rules / Invariants
    extracted_requirements = []
    
    sentences = [s.strip() for s in re.split(r'[.\n]', pitch) if len(s.strip()) > 15]
    rule_keywords = ["must", "only", "limit", "capacity", "when", "idempotent", "reduce", "assign", "status", "cancel", "allocate", "eta"]
    
    req_counter = 1
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(kw in s_lower for kw in rule_keywords):
            extracted_requirements.append({
                "id": f"REQ-BUS-{req_counter:03d}",
                "title": f"Business Rule: {sentence[:45]}...",
                "description": sentence,
                "type": "Domain Invariant",
                "priority": "High"
            })
            req_counter += 1
            
    # Fallback requirement if none detected
    if not extracted_requirements:
        extracted_requirements.append({
            "id": "REQ-BUS-001",
            "title": "Business Rule: Valid Order & State Transitions",
            "description": "The system shall validate order inputs and enforce state transitions across processing stages.",
            "type": "Domain Invariant",
            "priority": "High"
        })
        
    return {
        "pitch": pitch,
        "blocks": analyzed_blocks,
        "extracted_requirements": extracted_requirements
    }
