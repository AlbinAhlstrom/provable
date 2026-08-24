"""
Kickstart Feature Block Catalog & AI Pitch Analyzer.

Maps natural language pitch prompts to pre-baked UX/UI feature blocks
(Shopping Cart, Product Catalog, Order Tracking, User Auth, Admin Dashboard, etc.)
and extracts custom domain business rules to seed into Provable's StrictDoc/SQLite requirements database.
"""

import re
import json
from typing import Dict, Any, List, Optional

FEATURE_BLOCK_CATALOG = [
    {
        "id": "catalog_grid",
        "name": "Product Catalog & Menu Grid",
        "icon": "📋",
        "category": "Customer Experience",
        "description": "Interactive grid view with category filters, product search, pricing, and detail modals.",
        "keywords": ["product", "menu", "item", "catalog", "goods", "listing", "store", "shop", "inventory", "merchandise", "wares", "items", "order"],
        "default_selected": False
    },
    {
        "id": "shopping_cart",
        "name": "Shopping Cart & Checkout",
        "icon": "🛒",
        "category": "E-Commerce",
        "description": "Slide-out cart drawer, quantity modifiers, price calculations, and checkout form.",
        "keywords": ["cart", "order", "buy", "checkout", "purchase", "pay", "retail", "shop", "price"],
        "default_selected": False
    },
    {
        "id": "order_tracking",
        "name": "Live Order Tracking & Pipeline",
        "icon": "📦",
        "category": "Operations",
        "description": "Real-time visual status pipeline (Placed → Processing → Ready → Delivered).",
        "keywords": ["track", "status", "delivery", "dispatch", "order", "pipeline", "progress", "eta", "shipment"],
        "default_selected": False
    },
    {
        "id": "user_auth",
        "name": "Customer Profiles & Authentication",
        "icon": "👤",
        "category": "Security",
        "description": "User login/signup modals, saved addresses, and order history view.",
        "keywords": ["login", "signup", "user_auth", "authentication", "account_login", "sign_in"],
        "default_selected": False
    },
    {
        "id": "booking_calendar",
        "name": "Appointment & Slot Booking",
        "icon": "📅",
        "category": "Services",
        "description": "Interactive date/time slot picker, staff selection, and reservation confirmation.",
        "keywords": ["book", "appointment", "reserve", "slot", "schedule", "calendar", "time", "date", "session", "service", "booking", "consultation"],
        "default_selected": False
    },
    {
        "id": "admin_dashboard",
        "name": "Merchant & Operational Dashboard",
        "icon": "🏪",
        "category": "Management",
        "description": "Operations queue / admin metrics, status update toggles, and inventory counts.",
        "keywords": ["admin", "dashboard", "operations", "queue", "manage", "merchant", "staff", "inventory", "batch", "metrics"],
        "default_selected": False
    },
    {
        "id": "reviews_ratings",
        "name": "Reviews & Rating System",
        "icon": "⭐",
        "category": "Engagement",
        "description": "Customer feedback collection, star rating components, and review list display.",
        "keywords": ["review", "rating", "star", "feedback", "comment", "score", "testimonial"],
        "default_selected": False
    },
    {
        "id": "interactive_widget",
        "name": "Interactive Custom Tool / Widget",
        "icon": "⚡",
        "category": "Custom Tools",
        "description": "Interactive mini-game, widget, custom configurator, or domain-specific utility.",
        "keywords": ["widget", "tool", "configurator", "calculator", "custom", "game", "interactive", "arcade", "simulator"],
        "default_selected": False
    }
]


def extract_brand_name_from_pitch(pitch: str) -> Optional[str]:
    """
    Extracts explicit brand title from pitch prompts matching patterns like 'called X' or 'named X'.
    Prevents hardcoded brand overrides.
    """
    match = re.search(r'\b(?:called|named)\s+([^,.\n]+?)(?:\s+(?:with|that|for|and|\.|,|$))', pitch, re.IGNORECASE)
    if match:
        raw_name = match.group(1).strip()
        # Strip quotes if present
        clean_name = raw_name.strip('\'" ')
        if clean_name and len(clean_name) <= 50:
            return clean_name
    return None


def analyze_pitch_for_kickstart(pitch: str) -> Dict[str, Any]:
    """
    Analyzes a natural language business pitch to match recommended feature blocks
    and extract domain business requirements.
    """
    pitch_lower = pitch.lower()
    pitch_words = [w.strip('s.,!?') for w in pitch_lower.split()]
    pitch_text_clean = " ".join(pitch_words) + " " + pitch_lower
    
    # Check pitch domain intent keywords
    is_game_or_tool_pitch = any(k in pitch_text_clean for k in ["game", "arcade", "puzzle", "calculator", "tool", "widget"])
    is_service_booking_pitch = any(k in pitch_text_clean for k in ["appointment", "book", "calendar", "schedule", "slot", "session", "reserve"])
    is_dashboard_pitch = any(k in pitch_text_clean for k in ["admin", "dashboard", "metrics", "analytics", "queue", "monitor"])
    
    is_explicit_ecom_pitch = any(k in pitch_text_clean for k in ["shop", "buy", "cart", "store", "product", "item", "retail", "checkout", "menu"])

    # 1. Match catalog blocks dynamically based on pitch relevance
    analyzed_blocks = []
    for block in FEATURE_BLOCK_CATALOG:
        match_count = sum(1 for kw in block["keywords"] if kw in pitch_text_clean)
        
        # Only apply default_selected e-commerce blocks if pitch is an e-commerce pitch or has no specific domain intent
        if is_game_or_tool_pitch or is_service_booking_pitch or is_dashboard_pitch:
            if is_explicit_ecom_pitch:
                is_recommended = match_count > 0 or block.get("default_selected", False)
            else:
                is_recommended = match_count > 0
        else:
            is_recommended = match_count > 0 or block.get("default_selected", False)
        
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
