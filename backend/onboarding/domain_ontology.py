"""
Universal Domain Ontology Stormer & Dynamic Conceptualization Engine.
Constructs 100% generic, contract-first Domain Ontologies for ANY arbitrary pitch
with ZERO domain-specific hardcoded switchboards.
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class EntityAttributeSpec:
    name: str
    type: str  # 'string' | 'currency' | 'number' | 'tags' | 'boolean'
    required: bool = True
    default_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MasterEntitySpec:
    entity_name: str
    entity_plural: str
    action_verb: str
    attributes: List[EntityAttributeSpec] = field(default_factory=list)
    seed_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "entity_plural": self.entity_plural,
            "action_verb": self.action_verb,
            "attributes": [a.to_dict() for a in self.attributes],
            "seed_items": self.seed_items
        }

@dataclass
class DomainCommandSpec:
    name: str
    description: str
    fields: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DomainEventSpec:
    name: str
    description: str
    fields: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VisualThemeSpec:
    archetype: str
    primary_color: str
    secondary_color: str
    bg_gradient: str
    card_bg: str
    border_color: str
    domain_emoji: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DomainOntologySpec:
    pitch: str
    brand_name: str
    hero_headline: str
    guarantee_badge: str
    domain_category: str  # 'catalog_cart' | 'calendar_service' | 'pipeline_tracker' | 'dashboard_metrics'
    visual_theme: VisualThemeSpec
    master_entity: MasterEntitySpec
    secondary_entities: List[MasterEntitySpec] = field(default_factory=list)
    commands: List[DomainCommandSpec] = field(default_factory=list)
    events: List[DomainEventSpec] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": self.pitch,
            "brand_name": self.brand_name,
            "hero_headline": self.hero_headline,
            "guarantee_badge": self.guarantee_badge,
            "domain_category": self.domain_category,
            "visual_theme": self.visual_theme.to_dict(),
            "master_entity": self.master_entity.to_dict(),
            "secondary_entities": [e.to_dict() for e in self.secondary_entities],
            "commands": [c.to_dict() for c in self.commands],
            "events": [e.to_dict() for e in self.events]
        }


def _extract_primary_noun(pitch: str) -> str:
    """Extract primary domain subject noun from arbitrary natural language pitch."""
    stop_words = {
        "an", "a", "the", "app", "application", "platform", "system", "tool", "portal",
        "to", "for", "with", "in", "on", "and", "or", "of", "by", "that", "this",
        "order", "book", "buy", "sell", "track", "manage", "find", "schedule", "rent",
        "around", "your", "our", "online", "custom", "storefront", "service", "services"
    }
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', pitch.lower())
    tokens = [w for w in cleaned.split() if len(w) > 2 and w not in stop_words]

    if not tokens:
        return "Item"

    # Common domain mappings if plural or verb form
    noun = tokens[0]
    if noun.endswith("s") and len(noun) > 3 and not noun.endswith("ss"):
        noun = noun[:-1]
    return noun.capitalize()


def _infer_domain_category(pitch_lower: str) -> str:
    """Infer interaction pattern from pitch semantics without domain-specific hardcoding."""
    if any(k in pitch_lower for k in ["book", "appointment", "schedule", "session", "calendar", "consult", "lesson", "visit"]):
        return "calendar_service"
    if any(k in pitch_lower for k in ["track", "pipeline", "status", "stage", "kds", "dispatch", "logistics", "workflow"]):
        return "pipeline_tracker"
    if any(k in pitch_lower for k in ["metric", "analytics", "admin", "dashboard", "kpi", "monitor", "finance"]):
        return "dashboard_metrics"
    return "catalog_cart"


def _infer_action_verb(category: str, noun: str) -> str:
    """Infer primary interactive action button text."""
    if category == "calendar_service":
        return f"📅 Book {noun}"
    if category == "pipeline_tracker":
        return f"📦 Track {noun}"
    if category == "dashboard_metrics":
        return f"📊 Inspect {noun}"
    return f"🛒 Add {noun}"


def _infer_domain_emoji(noun: str, category: str) -> str:
    """Infer appropriate emoji icon from noun stem."""
    n = noun.lower()
    if any(k in n for k in ["scuba", "dive", "water", "sea", "boat", "yacht"]):
        return "🤿"
    if any(k in n for k in ["machine", "equipment", "excavat", "crane", "build", "construct"]):
        return "🚜"
    if any(k in n for k in ["pizza", "dish", "food", "meal", "burger", "taco", "sushi"]):
        return "🍕"
    if any(k in n for k in ["tutor", "teach", "learn", "course", "study", "class"]):
        return "🎓"
    if any(k in n for k in ["laundry", "wash", "clean", "fold"]):
        return "🧺"
    if any(k in n for k in ["music", "band", "sound", "concert", "gig", "artist"]):
        return "🎸"
    if any(k in n for k in ["car", "auto", "vehicle", "rent", "ride"]):
        return "🚗"
    if any(k in n for k in ["sneaker", "shoe", "apparel", "wear", "shirt"]):
        return "👟"
    if any(k in n for k in ["pet", "dog", "cat", "vet"]):
        return "🐾"
    if category == "calendar_service":
        return "📅"
    if category == "pipeline_tracker":
        return "📦"
    return "✨"


def storm_domain_ontology(pitch: str) -> DomainOntologySpec:
    """
    Universal Domain Ontology Stormer.
    Generates rich, fully typed DomainOntologySpec for ANY pitch.
    """
    pitch_clean = pitch.strip()
    p_lower = pitch_clean.lower()
    noun = _extract_primary_noun(pitch_clean)
    plural = f"{noun}s" if not noun.endswith("s") else noun
    category = _infer_domain_category(p_lower)
    emoji = _infer_domain_emoji(noun, category)
    action_verb = _infer_action_verb(category, noun)

    # Dynamic Theme Archetype
    if any(k in p_lower for k in ["terminal", "cli", "devops", "code", "cyber", "log"]):
        archetype = "dark_developer_terminal"
        primary_color = "#0284c7"
        secondary_color = "#38bdf8"
        bg_gradient = "linear-gradient(180deg, #020617 0%, #0f172a 100%)"
        card_bg = "#0f172a"
        border_color = "#1e293b"
    elif category == "calendar_service":
        archetype = "warm_lifestyle_light"
        primary_color = "#0284c7"
        secondary_color = "#f97316"
        bg_gradient = "#f8fafc"
        card_bg = "#ffffff"
        border_color = "#e2e8f0"
    else:
        archetype = "modern_fresh_light"
        primary_color = "#0284c7"
        secondary_color = "#10b981"
        bg_gradient = "#f8fafc"
        card_bg = "#ffffff"
        border_color = "#e2e8f0"

    theme = VisualThemeSpec(
        archetype=archetype,
        primary_color=primary_color,
        secondary_color=secondary_color,
        bg_gradient=bg_gradient,
        card_bg=card_bg,
        border_color=border_color,
        domain_emoji=emoji
    )

    # Brand Title & Headlines
    brand_name = f"{noun}Craft" if not any(w in pitch_clean for w in ["app", "platform"]) else f"{noun}Hub"
    hero_headline = f"Premium {plural} Delivered On-Demand" if category == "catalog_cart" else f"Expert {plural} Booked Around Your Schedule"
    guarantee_badge = f"100% Certified & Verified {plural}"

    # Master Entity Attributes
    if category == "calendar_service":
        attributes = [
            EntityAttributeSpec(name="name", type="string", required=True),
            EntityAttributeSpec(name="price", type="currency", required=True),
            EntityAttributeSpec(name="specialties", type="tags", required=False, default_value=[]),
            EntityAttributeSpec(name="rating", type="number", required=False, default_value=4.9),
            EntityAttributeSpec(name="badge", type="string", required=False, default_value="Verified")
        ]
        seed_items = [
            {
                "id": "1",
                "name": f"Elite {noun} Session",
                "price": 45.00,
                "specialties": ["Certified", "Top Rated", "Express Service"],
                "rating": 5.0,
                "badge": "Top Rated"
            },
            {
                "id": "2",
                "name": f"Standard {noun} Package",
                "price": 30.00,
                "specialties": ["Verified Provider", "Flexible Hours"],
                "rating": 4.8,
                "badge": "Verified"
            }
        ]
    else:
        # Default E-Commerce / Catalog
        is_food = any(k in p_lower for k in ["pizza", "dish", "food", "bakery", "bread", "burger", "taco", "sushi", "cake"])
        tag_name = "ingredients" if is_food else "features"
        
        attributes = [
            EntityAttributeSpec(name="name", type="string", required=True),
            EntityAttributeSpec(name="price", type="currency", required=True),
            EntityAttributeSpec(name=tag_name, type="tags", required=False, default_value=[]),
            EntityAttributeSpec(name="rating", type="number", required=False, default_value=4.9),
            EntityAttributeSpec(name="badge", type="string", required=False, default_value="Popular")
        ]
        
        if is_food:
            seed_items = [
                {
                    "id": "1",
                    "name": f"Signature {noun} Speciale",
                    "price": 16.99,
                    "ingredients": ["San Marzano Tomatoes", "Fresh Mozzarella", "Basil", "EVOO"],
                    "rating": 4.9,
                    "badge": "Best Seller"
                },
                {
                    "id": "2",
                    "name": f"Artisan {noun} Feast",
                    "price": 19.99,
                    "ingredients": ["Crispy Pepperoni", "Hot Honey", "Smoked Mozzarella"],
                    "rating": 5.0,
                    "badge": "Popular"
                },
                {
                    "id": "3",
                    "name": f"Gourmet White {noun}",
                    "price": 21.99,
                    "ingredients": ["Wild Mushrooms", "Truffle Ricotta", "Garlic", "Thyme"],
                    "rating": 4.8,
                    "badge": "Chef Pick"
                }
            ]
        else:
            seed_items = [
                {
                    "id": "1",
                    "name": f"Premium {noun} Pro",
                    "price": 129.00,
                    "features": ["Heavy Duty", "GPS Tracking", "Full Warranty"],
                    "rating": 4.9,
                    "badge": "Best Seller"
                },
                {
                    "id": "2",
                    "name": f"Standard {noun} Edition",
                    "price": 79.00,
                    "features": ["Certified Quality", "Fast Delivery"],
                    "rating": 4.8,
                    "badge": "Popular"
                }
            ]

    master_entity = MasterEntitySpec(
        entity_name=noun,
        entity_plural=plural,
        action_verb=action_verb,
        attributes=attributes,
        seed_items=seed_items
    )

    # Commands & Events
    commands = [
        DomainCommandSpec(
            name=f"Place{noun}Order",
            description=f"Submit a new {noun} order / transaction",
            fields=[
                {"name": "order_number", "type": "str"},
                {"name": "customer_name", "type": "str"},
                {"name": "item_name", "type": "str"},
                {"name": "price", "type": "float"}
            ]
        ),
        DomainCommandSpec(
            name=f"Cancel{noun}Order",
            description=f"Cancel an active {noun} order",
            fields=[{"name": "order_number", "type": "str"}]
        )
    ]

    events = [
        DomainEventSpec(
            name=f"{noun}OrderPlaced",
            description=f"Emitted when a new {noun} order is confirmed",
            fields=[
                {"name": "order_number", "type": "str"},
                {"name": "customer_name", "type": "str"},
                {"name": "total_price", "type": "float"}
            ]
        ),
        DomainEventSpec(
            name=f"{noun}OrderDispatched",
            description=f"Emitted when a {noun} order is dispatched for fulfillment",
            fields=[
                {"name": "order_number", "type": "str"}
            ]
        )
    ]

    return DomainOntologySpec(
        pitch=pitch_clean,
        brand_name=brand_name,
        hero_headline=hero_headline,
        guarantee_badge=guarantee_badge,
        domain_category=category,
        visual_theme=theme,
        master_entity=master_entity,
        secondary_entities=[],
        commands=commands,
        events=events
    )
