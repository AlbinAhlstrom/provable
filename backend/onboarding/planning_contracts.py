"""
Pydantic Contracts for Multi-Agent Frontend Planning Pipeline.

Ensures strict schema validation, zero-hallucination contracts, and automated repair
loops across all planning agent stages.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LayoutSlotSpec(BaseModel):
    name: str = Field(description="Name of the layout slot (e.g. header, main_content, modal_drawer)")
    purpose: str = Field(description="Functional purpose of this slot in the page layout")


class CategoryLayoutPlan(BaseModel):
    category_id: str = Field(description="Matching category layout ID (service_booking, e_commerce, operations_dashboard, saas_analytics, custom_novel)")
    layout_name: str = Field(description="Human-readable title of the selected category layout")
    category_reasoning: str = Field(description="Explanation of why this pitch matches the category layout")
    slots: List[LayoutSlotSpec] = Field(default_factory=list, description="Defined slots for this layout")


class BespokeComponentSpec(BaseModel):
    component_name: str = Field(description="PascalCase React component name to build from scratch")
    slot: str = Field(description="Layout slot where this custom component will be rendered")
    description: str = Field(description="Purpose and functionality of this custom component")
    key_interactions: List[str] = Field(default_factory=list, description="Interactive features required")


class ComponentSlotAssignment(BaseModel):
    reused_registry_blocks: List[str] = Field(default_factory=list, description="IDs of valid blocks selected from component registry")
    bespoke_components: List[BespokeComponentSpec] = Field(default_factory=list, description="Custom components to generate from scratch")


class SeedDataItem(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    price_or_rate: Optional[str] = None
    badge_status: Optional[str] = None
    rating: Optional[float] = None
    availability_slots: Optional[List[str]] = None


from enum import Enum

class AestheticArchetype(str, Enum):
    WARM_LIFESTYLE_LIGHT = "warm_lifestyle_light"
    MODERN_FRESH_LIGHT = "modern_fresh_light"
    CLEAN_B2B_LIGHT = "clean_b2b_light"
    DARK_DEVELOPER_TERMINAL = "dark_developer_terminal"


DESIGN_ARCHETYPE_TOKENS: Dict[str, Dict[str, str]] = {
    "warm_lifestyle_light": {
        "bg_main": "#FAF7F2",
        "bg_card": "#FFFFFF",
        "bg_secondary": "#F4EFE6",
        "text_primary": "#2C2A29",
        "text_muted": "#78716C",
        "color_primary": "#C85A44",
        "color_primary_hover": "#B04B37",
        "color_mint": "#E2F6ED",
        "color_mint_text": "#059669",
        "color_coral": "#E07A5F",
        "border_color": "#EBE4D8",
        "font_heading": "'Outfit', 'Plus Jakarta Sans', sans-serif",
        "font_body": "'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "shadow_card": "0 10px 30px rgba(44, 42, 41, 0.04)"
    },
    "modern_fresh_light": {
        "bg_main": "#FAFAFA",
        "bg_card": "#FFFFFF",
        "bg_secondary": "#F3F4F6",
        "text_primary": "#0F172A",
        "text_muted": "#64748B",
        "color_primary": "#059669",
        "color_primary_hover": "#047857",
        "color_mint": "#D1FAE5",
        "color_mint_text": "#047857",
        "color_coral": "#F97316",
        "border_color": "#E5E7EB",
        "font_heading": "'Outfit', 'Plus Jakarta Sans', sans-serif",
        "font_body": "'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "shadow_card": "0 4px 20px rgba(0, 0, 0, 0.05)"
    },
    "clean_b2b_light": {
        "bg_main": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "bg_secondary": "#F1F5F9",
        "text_primary": "#0F172A",
        "text_muted": "#64748B",
        "color_primary": "#2563EB",
        "color_primary_hover": "#1D4ED8",
        "color_mint": "#DBEAFE",
        "color_mint_text": "#1E40AF",
        "color_coral": "#EA580C",
        "border_color": "#E2E8F0",
        "font_heading": "'Outfit', 'Inter', system-ui, sans-serif",
        "font_body": "'Outfit', 'Inter', system-ui, sans-serif",
        "shadow_card": "0 2px 8px rgba(0, 0, 0, 0.04)"
    },
    "dark_developer_terminal": {
        "bg_main": "#0F172A",
        "bg_card": "#1E293B",
        "bg_secondary": "#090D16",
        "text_primary": "#F8FAFC",
        "text_muted": "#94A3B8",
        "color_primary": "#38BDF8",
        "color_primary_hover": "#0284C7",
        "color_mint": "rgba(16, 185, 129, 0.15)",
        "color_mint_text": "#10B981",
        "color_coral": "#F87171",
        "border_color": "#334155",
        "font_heading": "'Outfit', system-ui, sans-serif",
        "font_body": "'Outfit', system-ui, sans-serif",
        "shadow_card": "none"
    }
}


class AestheticThemeSpec(BaseModel):
    archetype: str = Field(default="warm_lifestyle_light", description="Theme archetype name")
    primary_color: str = Field(default="#C85A44", description="Hex or HSL primary brand color")
    secondary_color: str = Field(default="#E07A5F", description="Hex or HSL secondary accent color")
    bg_gradient: str = Field(default="#FAF7F2", description="Background CSS gradient or color")
    card_bg: str = Field(default="#FFFFFF", description="Card background color")
    border_color: str = Field(default="#EBE4D8", description="Border color")
    domain_display_title: str = Field(description="Clean brand title for storefront/header")
    mock_seed_data: List[Dict[str, Any]] = Field(default_factory=list, description="Realistic mock data items")
    hero_headline: str = Field(default="Booked around your week.", description="Dynamic hero headline")
    guarantee_badge: str = Field(default="Verified & reference-checked", description="Dynamic badge text")
    item_singular: str = Field(default="provider", description="Domain item singular noun")
    item_plural: str = Field(default="providers", description="Domain item plural noun")
    action_button_text: str = Field(default="📅 Request booking", description="CTA button text")
    domain_emoji: str = Field(default="⭐", description="Domain icon emoji for hero banner")

    def get_tokens(self) -> Dict[str, str]:
        return DESIGN_ARCHETYPE_TOKENS.get(self.archetype, DESIGN_ARCHETYPE_TOKENS["warm_lifestyle_light"])

    def get_css_variables_style(self) -> str:
        tokens = self.get_tokens()
        return "\n".join([f"  --{k.replace('_', '-')}: {v};" for k, v in tokens.items()])


class UnifiedFrontendBlueprint(BaseModel):
    business_pitch: str
    category_layout: CategoryLayoutPlan
    components: ComponentSlotAssignment
    aesthetics: AestheticThemeSpec

