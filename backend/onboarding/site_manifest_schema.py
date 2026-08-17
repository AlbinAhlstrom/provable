"""
Pydantic Schema Definitions for Unified Site Manifest AST Pipeline.
Defines contracts for Stages 1 through 5 of the frontend synthesis pipeline.
"""

import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DomainIntentSpec(BaseModel):
    """Stage 1: Intent & Domain Deconstruction AST Node."""
    business_pitch: str = Field(..., description="Raw user business pitch or prompt")
    brand_name: str = Field(default="Provable Application", description="Extracted brand display name")
    domain_category: str = Field(default="e_commerce", description="Category ID e.g. e_commerce, service_booking, etc.")
    primary_workflow: str = Field(default="ordering", description="Primary workflow e.g. ordering, booking, tracking")
    target_audience: Optional[str] = Field(default="Customers & Users", description="Target user persona")
    entity_models: List[str] = Field(default_factory=lambda: ["Product", "Order", "Review"])


class SubRequirementAST(BaseModel):
    """Sub-requirement nested under a parent component."""
    id: str = Field(..., description="Unique sub-requirement ID e.g. REQ-SUB-PIZZA_BUILDER-001")
    canonical_key: str = Field(..., description="Sub-feature key e.g. custom_item_builder")
    name: str = Field(..., description="Sub-requirement title")
    description: str = Field(default="", description="Summary description")
    enabled: bool = Field(default=True, description="Whether active")


class ComponentNodeAST(BaseModel):
    """Stage 2: Component Topology Node."""
    id: str = Field(..., description="Unique component identifier e.g. catalog, cart, REQ-CMP-PAYMENT_SYSTEM-001")
    canonical_key: str = Field(..., description="Normalized key e.g. catalog, payment_system, flappy_bird_game")
    name: str = Field(..., description="Human-readable title")
    component_type: str = Field(default="custom", description="'premade' or 'custom'")
    icon: str = Field(default="⚡", description="Emoji icon")
    description: str = Field(default="Active application component module", description="Summary description")
    enabled: bool = Field(default=True, description="Whether component is active in preview")
    placement_slot: str = Field(default="primary_tab", description="UI slot: 'primary_tab' | 'embedded_view' | 'action_drawer' | 'post_action_screen' | 'modal_dialog' | 'admin_panel'")
    visibility_trigger: str = Field(default="always", description="Visibility trigger: 'always' | 'user_action' | 'post_workflow_event'")
    is_visible: bool = Field(default=True, description="Relevance Decision: True if component adds value to app primary goal")
    relevance_reason: str = Field(default="", description="LLM Reasoning justification for inclusion or pruning")
    sub_requirements: List[SubRequirementAST] = Field(default_factory=list, description="Nested child sub-requirements")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")


class NavigationRouteAST(BaseModel):
    """Stage 3: Navigation Route AST Node."""
    key: str = Field(..., description="Route active tab key")
    label: str = Field(..., description="Navigation tab label text")
    component_ref: str = Field(..., description="ID or key of target component")
    icon: str = Field(default="⚡", description="Tab icon")


class HeroBannerAST(BaseModel):
    """Stage 3: Hero Banner AST Node."""
    headline: str = Field(default="", description="Hero headline banner text")
    subtitle: str = Field(default="", description="Hero subtitle paragraph")
    badges: List[str] = Field(default_factory=list, description="Value proposition badges")


class HeaderSpecAST(BaseModel):
    """Stage 3: Header AST Node."""
    brand_title: str = Field(default="Application", description="Top nav brand title")


class ThemeTokensAST(BaseModel):
    """Stage 3: Theme Token Spec."""
    primary_color: str = Field(default="#0284c7")
    bg_color: str = Field(default="#f8fafc")
    card_bg: str = Field(default="#ffffff")
    text_color: str = Field(default="#0f172a")
    font_family: str = Field(default="system-ui, sans-serif")


class SiteNavigationAST(BaseModel):
    """Stage 3: Page Routing & Layout Spec."""
    theme: ThemeTokensAST = Field(default_factory=ThemeTokensAST)
    header: HeaderSpecAST = Field(default_factory=HeaderSpecAST)
    hero_banner: HeroBannerAST = Field(default_factory=HeroBannerAST)
    show_hero_banner: bool = Field(default=True)
    navigation_routes: List[NavigationRouteAST] = Field(default_factory=list)
    default_route: str = Field(default="menu")


class ComponentContentAST(BaseModel):
    """Stage 4: Component Content & Mock Seed Data Spec."""
    catalog_items: List[Dict[str, Any]] = Field(default_factory=list)
    review_items: List[Dict[str, Any]] = Field(default_factory=list)
    mock_seed_data: Dict[str, Any] = Field(default_factory=dict)


class UnifiedSiteManifestAST(BaseModel):
    """Stage 5: Unified Site Manifest AST Root Document."""
    version: str = Field(default="2.0.0", description="AST Manifest Schema Version")
    business_pitch: str = Field(..., description="Active business pitch string")
    intent: DomainIntentSpec
    components: List[ComponentNodeAST] = Field(default_factory=list)
    layout: SiteNavigationAST = Field(default_factory=SiteNavigationAST)
    content: ComponentContentAST = Field(default_factory=ComponentContentAST)

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if item in ["brand_name", "brand_title"]:
            return getattr(self.intent, "brand_name", "")
        if item == "hero_headline":
            return getattr(self.layout.hero_banner, "headline", "")
        if item == "hero_subtitle":
            return getattr(self.layout.hero_banner, "subtitle", "")
        if item == "badges":
            return getattr(self.layout.hero_banner, "badges", [])
        if item == "domain_category":
            return getattr(self.intent, "domain_category", "e_commerce")
        raise KeyError(item)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item) or item in ["brand_title", "brand_name", "hero_headline", "hero_subtitle", "badges", "domain_category"]

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "UnifiedSiteManifestAST":
        data = json.loads(json_str)
        return cls(**data)
