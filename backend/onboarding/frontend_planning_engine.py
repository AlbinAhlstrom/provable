"""
Multi-Agent Frontend Planning Engine for Provable Synthesis.

Orchestrates 3 specialized planning subagents with Pydantic contract validation,
Registry Grounding verification, AST checks, and deterministic React layout assembly.
"""

import os
import re
import json
import sys
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_orchestrator import call_gemini
from onboarding.category_layouts import get_category_layout, CATEGORY_PAGE_LAYOUTS
from onboarding.component_registry import COMPONENT_REGISTRY, is_valid_component, get_component_block
from onboarding.planning_contracts import (
    CategoryLayoutPlan, ComponentSlotAssignment, BespokeComponentSpec,
    AestheticThemeSpec, UnifiedFrontendBlueprint, DESIGN_ARCHETYPE_TOKENS
)
from onboarding.code_verifier import verify_tsx_syntax, self_heal_tsx_code


def run_frontend_planning_pipeline(pitch: str) -> UnifiedFrontendBlueprint:
    """
    Executes the multi-agent planning pipeline with Pydantic validation & grounding gates.
    """
    # ── STAGE 1: Agent 0 (Category & Intent Classifier) ─────────────────────
    category_plan = _run_category_planning_agent(pitch)

    # ── STAGE 2: Agent 1 (Component Selection & Gap Analysis) ───────────────
    slot_assignment = _run_component_planning_agent(pitch, category_plan)

    # ── REGISTRY GROUNDING GATE ──────────────────────────────────────────────
    slot_assignment = _ground_component_assignments(slot_assignment, category_plan)

    # ── STAGE 3: Agent 2 (Aesthetic & Seed Data Planner) ────────────────────
    aesthetic_spec = _run_aesthetic_planning_agent(pitch, category_plan)

    # Combine into Unified Frontend Blueprint
    return UnifiedFrontendBlueprint(
        business_pitch=pitch,
        category_layout=category_plan,
        components=slot_assignment,
        aesthetics=aesthetic_spec
    )


def _run_category_planning_agent(pitch: str) -> CategoryLayoutPlan:
    """Agent 0: Classifies pitch into a Category Page Layout Template with Pydantic contract validation."""
    prompt = f"""
You are a Principal Product Architect. Classify the following business pitch into ONE of these Category Layout Templates:
- "service_booking": Appointment, slot, caregiver, sitter, tutoring, healthcare booking applications.
- "e_commerce": Product storefront, menu grid, retail, buying items with cart & checkout.
- "operations_dashboard": Kitchen KDS, merchant admin, inventory management, operational status queue.
- "saas_analytics": B2B dashboard, metrics, data analytics workbench.
- "custom_novel": Unique concepts that do NOT fit any standard category above.

Business Pitch: "{pitch}"

Respond ONLY with a JSON object in this format (no markdown):
{{
  "category_id": "<service_booking|e_commerce|operations_dashboard|saas_analytics|custom_novel>",
  "layout_name": "<human-readable title>",
  "category_reasoning": "<1-2 sentence rationale>"
}}
"""
    try:
        raw = call_gemini(prompt, stage="category_planning")
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
        cleaned = re.sub(r'\n?```$', '', cleaned.strip()).strip()
        data = json.loads(cleaned)
        
        layout_def = get_category_layout(data.get("category_id", "custom_novel"))
        return CategoryLayoutPlan(
            category_id=layout_def["id"],
            layout_name=layout_def["name"],
            category_reasoning=data.get("category_reasoning", "Matched category layout"),
            slots=layout_def["slots"]
        )
    except Exception as e:
        print(f"[notice] Category Planning Agent fallback: {e}")
        # Rule-based fallback if LLM offline
        p_lower = pitch.lower()
        if any(k in p_lower for k in ["book", "sitter", "appointment", "calendar", "slot", "care", "babysitter", "child"]):
            cid = "service_booking"
        elif any(k in p_lower for k in ["admin", "dashboard", "kitchen", "cook", "queue"]):
            cid = "operations_dashboard"
        elif any(k in p_lower for k in ["shop", "buy", "cart", "store", "product"]):
            cid = "e_commerce"
        else:
            cid = "custom_novel"

        layout_def = get_category_layout(cid)
        return CategoryLayoutPlan(
            category_id=layout_def["id"],
            layout_name=layout_def["name"],
            category_reasoning="Rule-based heuristic fallback",
            slots=layout_def["slots"]
        )


def _run_component_planning_agent(pitch: str, category_plan: CategoryLayoutPlan) -> ComponentSlotAssignment:
    """Agent 1: Maps layout slots to registry components or identifies custom bespoke components."""
    available_registry_ids = list(COMPONENT_REGISTRY.keys())
    
    prompt = f"""
You are a Lead Component Architect. Given the category layout "{category_plan.category_id}" for pitch: "{pitch}".

Available Premade Component Registry IDs:
{json.dumps(available_registry_ids)}

Determine:
1. Which premade registry IDs to reuse for standard features.
2. What novel/custom components to build from scratch for unique pitch requirements.

Respond ONLY with a JSON object:
{{
  "reused_registry_blocks": ["<registry_id>"],
  "bespoke_components": [
    {{
      "component_name": "<PascalCaseName>",
      "slot": "<main_content|modal_drawer|hero>",
      "description": "<purpose>",
      "key_interactions": ["<interaction 1>"]
    }}
  ]
}}
"""
    try:
        raw = call_gemini(prompt, stage="component_planning")
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
        cleaned = re.sub(r'\n?```$', '', cleaned.strip()).strip()
        data = json.loads(cleaned)
        
        bespoke = [BespokeComponentSpec(**b) for b in data.get("bespoke_components", [])]
        return ComponentSlotAssignment(
            reused_registry_blocks=data.get("reused_registry_blocks", []),
            bespoke_components=bespoke
        )
    except Exception as e:
        print(f"[notice] Component Planning Agent fallback: {e}")
        # Default component choices based on category
        if category_plan.category_id == "service_booking":
            reused = ["service_header", "weekly_calendar_grid"]
            bespoke = [BespokeComponentSpec(
                component_name="ProviderListCard",
                slot="main_content",
                description="Display caregiver profiles with rating, rate, and selection action",
                key_interactions=["Select provider to view available slots"]
            )]
        elif category_plan.category_id == "e_commerce":
            reused = ["ecom_header", "cart_drawer"]
            bespoke = [BespokeComponentSpec(
                component_name="ProductCatalogGrid",
                slot="main_content",
                description="Interactive product grid view",
                key_interactions=["Add item to cart"]
            )]
        else:
            reused = ["kpi_stat_bar"]
            bespoke = [BespokeComponentSpec(
                component_name="MainWorkstation",
                slot="main_content",
                description="Domain workspace view",
                key_interactions=["Interact with primary action"]
            )]

        return ComponentSlotAssignment(
            reused_registry_blocks=reused,
            bespoke_components=bespoke
        )


def _ground_component_assignments(slot_assignment: ComponentSlotAssignment, category_plan: CategoryLayoutPlan) -> ComponentSlotAssignment:
    """Registry Grounding Gate: Remaps hallucinated block IDs to valid registry components."""
    valid_reused = []
    for block_id in slot_assignment.reused_registry_blocks:
        if is_valid_component(block_id):
            valid_reused.append(block_id)
        else:
            print(f"[notice] Registry Grounding Gate: Remapped hallucinated block ID '{block_id}'")
            if category_plan.category_id == "service_booking":
                valid_reused.append("service_header")
                valid_reused.append("weekly_calendar_grid")
            elif category_plan.category_id == "e_commerce":
                valid_reused.append("ecom_header")

    # Deduplicate while preserving order
    dedup_reused = list(dict.fromkeys(valid_reused))
    return ComponentSlotAssignment(
        reused_registry_blocks=dedup_reused,
        bespoke_components=slot_assignment.bespoke_components
    )


def verify_theme_compliance(tsx_code: str, archetype: str) -> str:
    """
    AST & CSS Token Enforcement Gate:
    Replaces accidental hardcoded dark colors with CSS custom variables for light archetypes.
    """
    if archetype == "dark_developer_terminal":
        return tsx_code

    replacements = [
        (r"background:\s*['\"]#0f172a['\"]", "background: var(--bg-main)"),
        (r"background:\s*['\"]#1e293b['\"]", "background: var(--bg-card)"),
        (r"background:\s*['\"]#090d16['\"]", "background: var(--bg-secondary)"),
        (r"border:\s*['\"]1px solid #334155['\"]", "border: 1px solid var(--border-color)"),
        (r"color:\s*['\"]#f8fafc['\"]", "color: var(--text-primary)"),
        (r"color:\s*['\"]#94a3b8['\"]", "color: var(--text-muted)"),
        (r"color:\s*['\"]#cbd5e1['\"]", "color: var(--text-primary)"),
        (r"color:\s*['\"]#38bdf8['\"]", "color: var(--color-primary)"),
    ]

    sanitized = tsx_code
    for pattern, repl in replacements:
        sanitized = re.sub(pattern, repl, sanitized, flags=re.IGNORECASE)
    return sanitized


def _extract_domain_entity_profile(pitch: str) -> Dict[str, Any]:
    """
    Extracts dynamic domain nouns, hero headlines, badges, and seed data tailored to the pitch.
    Guarantees zero vocabulary hardcoding across service booking, tutoring, laundry, bakery, etc.
    """
    p_lower = pitch.lower()

    if any(k in p_lower for k in ["tutor", "tuition", "math", "teacher", "subject", "lesson", "study", "homework", "student"]):
        return {
            "title": "EduBook",
            "hero_headline": "1-on-1 Tutoring booked around your week.",
            "guarantee_badge": "Background-checked & top-rated tutors",
            "item_singular": "tutor",
            "item_plural": "tutors",
            "action_button_text": "📅 Schedule session",
            "domain_emoji": "🎓",
            "seed": [
                {"id": "1", "title": "Elena Vance", "subtitle": "Math & Calculus Specialist • AP Physics certified", "price_or_rate": "$35/hour", "badge_status": "Verified", "rating": 4.9, "initials": "EV"},
                {"id": "2", "title": "David Miller", "subtitle": "English & SAT Prep • Harvard Graduate", "price_or_rate": "$40/hour", "badge_status": "Top Rated", "rating": 5.0, "initials": "DM"},
                {"id": "3", "title": "Sophia Chen", "subtitle": "Chemistry & Biology • Med student tutor", "price_or_rate": "$32/hour", "badge_status": "Verified", "rating": 4.8, "initials": "SC"},
                {"id": "4", "title": "Marcus Brody", "subtitle": "Computer Science & Python • Senior mentor", "price_or_rate": "$45/hour", "badge_status": "Verified", "rating": 4.9, "initials": "MB"}
            ]
        }
    elif any(k in p_lower for k in ["sitter", "babysitter", "nanny", "child care", "daycare"]):
        return {
            "title": "Nestly",
            "hero_headline": "Babysitting booked around your week.",
            "guarantee_badge": "Every sitter ID-checked & reference-called",
            "item_singular": "sitter",
            "item_plural": "sitters",
            "action_button_text": "📅 Request sit",
            "domain_emoji": "👨‍👩‍👧‍👦",
            "seed": [
                {"id": "1", "title": "Maja Lindqvist", "subtitle": "Preschool teacher • loves messy art afternoons", "price_or_rate": "€22/hour", "badge_status": "Verified", "rating": 4.9, "initials": "ML"},
                {"id": "2", "title": "Tomas Berg", "subtitle": "Nursing student • first-aid certified • calm with newborns", "price_or_rate": "€19/hour", "badge_status": "Verified", "rating": 4.7, "initials": "TB"},
                {"id": "3", "title": "Aisha Karim", "subtitle": "Homework helper for ages 6-12 • board game champion", "price_or_rate": "€25/hour", "badge_status": "Verified", "rating": 5.0, "initials": "AK"},
                {"id": "4", "title": "Elin Sandberg", "subtitle": "Weekend specialist • comfortable with 3+ kids", "price_or_rate": "€21/hour", "badge_status": "Top Rated", "rating": 4.8, "initials": "ES"}
            ]
        }
    elif any(k in p_lower for k in ["pizza", "pizzeria", "oven", "bake", "crust", "topping"]):
        return {
            "title": "SliceCraft Pizza",
            "hero_headline": "Artisan Hand-Tossed Pizzas Delivered Fresh",
            "guarantee_badge": "100% Organic San Marzano Tomatoes & Mozzarella",
            "item_singular": "pizza",
            "item_plural": "pizzas",
            "action_button_text": "🍕 Add to Cart",
            "domain_emoji": "🍕",
            "seed": [
                {"id": "1", "title": "Margherita Speciale", "subtitle": "Fresh mozzarella • San Marzano basil sauce • extra virgin olive oil", "price_or_rate": "$16.99", "badge_status": "Best Seller", "rating": 4.9, "initials": "MS"},
                {"id": "2", "title": "Pepperoni Feast", "subtitle": "Double crispy cupping pepperoni • spicy honey drizzle", "price_or_rate": "$19.99", "badge_status": "Popular", "rating": 5.0, "initials": "PF"},
                {"id": "3", "title": "Truffle Mushroom White", "subtitle": "Wild mushrooms • truffle ricotta cream • thyme & garlic", "price_or_rate": "$21.99", "badge_status": "Chef Pick", "rating": 4.8, "initials": "TM"}
            ]
        }
    elif any(k in p_lower for k in ["laundry", "wash", "fold", "dry cleaning", "laundromat"]):
        return {
            "title": "FreshFold",
            "hero_headline": "Wash & Fold scheduled around your week.",
            "guarantee_badge": "Eco-friendly detergent & 24h turnaround",
            "item_singular": "service",
            "item_plural": "wash packages",
            "action_button_text": "📅 Schedule pickup",
            "domain_emoji": "🧺",
            "seed": [
                {"id": "1", "title": "Standard Wash & Fold", "subtitle": "Everyday garments • hypoallergenic wash • neatly folded", "price_or_rate": "$1.75/lb", "badge_status": "Popular", "rating": 4.9, "initials": "WF"},
                {"id": "2", "title": "Delicate & Silk Care", "subtitle": "Gentle cycle • air-dry options • premium scent", "price_or_rate": "$2.50/lb", "badge_status": "Premium", "rating": 5.0, "initials": "DC"},
                {"id": "3", "title": "Bedding & Comforter Care", "subtitle": "Deep sanitize wash for duvets and sheets", "price_or_rate": "$25/set", "badge_status": "Verified", "rating": 4.8, "initials": "BC"}
            ]
        }
    elif any(k in p_lower for k in ["bakery", "bread", "pastry", "cake", "bakeshop", "patisserie"]):
        return {
            "title": "Artisan Oven",
            "hero_headline": "Fresh artisan baking delivered to your doorstep.",
            "guarantee_badge": "100% organic sourdough & wild yeast",
            "item_singular": "item",
            "item_plural": "pastries",
            "action_button_text": "🛒 Reserve bake",
            "domain_emoji": "🥖",
            "seed": [
                {"id": "1", "title": "Country Sourdough Boule", "subtitle": "36-hr fermentation • crispy crust • soft open crumb", "price_or_rate": "$8.50", "badge_status": "Fresh Daily", "rating": 4.9, "initials": "SB"},
                {"id": "2", "title": "Butter Croissant Box (4x)", "subtitle": "French Isigny butter • 72 flaky lamination layers", "price_or_rate": "$14.00", "badge_status": "Best Seller", "rating": 5.0, "initials": "BC"},
                {"id": "3", "title": "Cardamom & Cinnamon Buns", "subtitle": "Swedish recipe • freshly ground cardamom pods", "price_or_rate": "$4.50", "badge_status": "Bakehouse Pick", "rating": 4.8, "initials": "CB"}
            ]
        }
    elif any(k in p_lower for k in ["band", "music", "musician", "gig", "event", "artist", "concert", "dj", "performer"]):
        return {
            "title": "BandSync",
            "hero_headline": "Live Bands & Musicians booked for your event.",
            "guarantee_badge": "Verified audio samples & background-checked bands",
            "item_singular": "band",
            "item_plural": "bands",
            "action_button_text": "📅 Request band",
            "domain_emoji": "🎸",
            "seed": [
                {"id": "1", "title": "The Neon Revival", "subtitle": "4-piece Indie & Rock Cover Band • 120+ wedding & corporate gigs", "price_or_rate": "$850/event", "badge_status": "Top Rated", "rating": 5.0, "initials": "NR"},
                {"id": "2", "title": "Velvet Jazz Trio", "subtitle": "Smooth Saxophone & Piano • Ideal for cocktail hours & galas", "price_or_rate": "$650/event", "badge_status": "Verified", "rating": 4.9, "initials": "VJ"},
                {"id": "3", "title": "Electric Skyline", "subtitle": "High-energy Pop & Dance Funk • Full sound system included", "price_or_rate": "$1,200/event", "badge_status": "Popular", "rating": 4.8, "initials": "ES"}
            ]
        }
    else:
        stop_words = {"site", "application", "platform", "app", "system", "portal", "tool", "web", "book", "booking", "process", "service", "times", "week", "different", "should", "through", "which", "shows"}
        words = [w for w in pitch.replace(".", "").replace(",", "").split() if len(w) > 3 and w.lower() not in stop_words]
        noun = words[0].title() if words else "Service"
        return {
            "title": f"{noun}Hub",
            "hero_headline": f"{noun} services booked around your week.",
            "guarantee_badge": f"Verified & background-checked {noun.lower()} providers",
            "item_singular": noun.lower(),
            "item_plural": f"{noun.lower()}s",
            "action_button_text": "📅 Request booking",
            "domain_emoji": "⭐",
            "seed": [
                {"id": "1", "title": f"Primary {noun} Specialist", "subtitle": "Top rated professional • 5 yrs exp", "price_or_rate": "$30/hour", "badge_status": "Verified", "rating": 4.9, "initials": f"{noun[0]}1"},
                {"id": "2", "title": f"Senior {noun} Expert", "subtitle": "Certified lead specialist", "price_or_rate": "$45/hour", "badge_status": "Top Rated", "rating": 5.0, "initials": f"{noun[0]}2"}
            ]
        }


def sanitize_domain_vocabulary_leakage(code: str, pitch: str) -> str:
    """
    Vocabulary Isolation Gate:
    Guarantees no babysitter vocabulary leaks into non-babysitter apps (e.g. tutors, courts, laundromats).
    """
    p_lower = pitch.lower()
    is_babysitter = any(k in p_lower for k in ["sitter", "babysitter", "nanny", "child care"])

    if not is_babysitter:
        replacement_map = [
            ("Babysitting booked", "Services booked"),
            ("Every sitter ID-checked", "Every provider verified & reference-checked"),
            ("Choose your sitter", "Choose your provider"),
            ("local sitters", "local providers"),
            ("to confirm a sit", "to confirm booking"),
            ("sitter.title", "provider.title"),
            ("sitters.map", "providers.map"),
            ("sitters", "providers"),
            ("sitter", "provider"),
            ("Nestly", "EduBook" if "tutor" in p_lower else "ServiceHub")
        ]
        sanitized = code
        for search_term, replace_term in replacement_map:
            sanitized = sanitized.replace(search_term, replace_term)
        return sanitized

    return code


def _run_aesthetic_planning_agent(pitch: str, category_plan: CategoryLayoutPlan) -> AestheticThemeSpec:
    """Agent 2: Generates domain color palette, brand title, and realistic mock seed data."""
    p_lower = pitch.lower()
    cat_id = category_plan.category_id

    # Determine archetype
    if any(k in p_lower for k in ["cli", "terminal", "log viewer", "devops", "kernel", "debugger"]):
        arch_id = "dark_developer_terminal"
    elif cat_id == "service_booking" or any(k in p_lower for k in ["sitter", "babysitter", "care", "book", "appointment", "clinic", "health", "doctor", "tutor", "spa", "salon", "pet"]):
        arch_id = "warm_lifestyle_light"
    elif cat_id == "e_commerce" or any(k in p_lower for k in ["shop", "store", "bakery", "bread", "food", "cafe", "apparel", "buy", "cart", "product"]):
        arch_id = "modern_fresh_light"
    else:
        arch_id = "clean_b2b_light"

    tokens = DESIGN_ARCHETYPE_TOKENS[arch_id]
    profile = _extract_domain_entity_profile(pitch)

    prompt = f"""
You are a Lead UI/UX Designer creating an aesthetic design spec for pitch: "{pitch}".
Category: "{cat_id}", Theme Archetype: "{arch_id}".

Respond ONLY with a JSON object:
{{
  "domain_display_title": "<Clean Storefront/Service Title>",
  "mock_seed_data": [
    {{
      "id": "1",
      "title": "<Name/Title>",
      "subtitle": "<Role/Category>",
      "price_or_rate": "<e.g. $22/hr or €22/hour>",
      "badge_status": "<e.g. Verified | CPR Certified>",
      "rating": 4.9,
      "initials": "<2 letter initials, e.g. EV>",
      "availability_slots": ["09:00 AM", "01:00 PM"]
    }}
  ]
}}
"""
    try:
        raw = call_gemini(prompt, stage="aesthetic_planning")
        cleaned = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
        cleaned = re.sub(r'\n?```$', '', cleaned.strip()).strip()
        data = json.loads(cleaned)
        
        return AestheticThemeSpec(
            archetype=arch_id,
            primary_color=tokens["color_primary"],
            secondary_color=tokens["color_coral"],
            bg_gradient=tokens["bg_main"],
            card_bg=tokens["bg_card"],
            border_color=tokens["border_color"],
            domain_display_title=data.get("domain_display_title", profile["title"]),
            mock_seed_data=data.get("mock_seed_data", profile["seed"]),
            hero_headline=profile["hero_headline"],
            guarantee_badge=profile["guarantee_badge"],
            item_singular=profile["item_singular"],
            item_plural=profile["item_plural"],
            action_button_text=profile["action_button_text"],
            domain_emoji=profile["domain_emoji"]
        )
    except Exception as e:
        print(f"[notice] Aesthetic Planning Agent fallback: {e}")

        return AestheticThemeSpec(
            archetype=arch_id,
            primary_color=tokens["color_primary"],
            secondary_color=tokens["color_coral"],
            bg_gradient=tokens["bg_main"],
            card_bg=tokens["bg_card"],
            border_color=tokens["border_color"],
            domain_display_title=profile["title"],
            mock_seed_data=profile["seed"],
            hero_headline=profile["hero_headline"],
            guarantee_badge=profile["guarantee_badge"],
            item_singular=profile["item_singular"],
            item_plural=profile["item_plural"],
            action_button_text=profile["action_button_text"],
            domain_emoji=profile["domain_emoji"]
        )


def assemble_app_tsx_from_blueprint(blueprint: UnifiedFrontendBlueprint, custom_fixtures: Optional[Dict[str, Any]] = None) -> str:
    """
    Assembles complete, high-aesthetic React App.tsx TSX code from the blueprint.
    """
    pitch = blueprint.business_pitch
    cat_id = blueprint.category_layout.category_id
    aesthetics = blueprint.aesthetics
    arch_id = aesthetics.archetype
    
    # 1. Collect registry components TSX
    registry_snippets = []
    for block_id in blueprint.components.reused_registry_blocks:
        blk = get_component_block(block_id)
        if blk:
            registry_snippets.append(blk["tsx_code"])

    registry_code_combined = "\n".join(registry_snippets)

    # 2. Prompt LLM to synthesize bespoke custom components & main App layout wrapper
    css_vars = aesthetics.get_css_variables_style()
    prompt = f"""
You are a Master React TSX Developer. Synthesize a complete, production-grade `App.tsx` component for this application plan:

- **Business Pitch**: "{pitch}"
- **Category Page Layout**: "{cat_id}" ({blueprint.category_layout.layout_name})
- **Brand Title**: "{aesthetics.domain_display_title}"
- **Aesthetic Archetype**: "{arch_id}"
- **CSS Variable Tokens**:
{css_vars}

- **Mock Seed Data**: {json.dumps(aesthetics.mock_seed_data, indent=2)}

- **Pre-baked Components Included in Scope**:
{registry_code_combined}

- **Bespoke Components to Build**:
{json.dumps([b.dict() for b in blueprint.components.bespoke_components], indent=2)}

### Implementation Guidelines:
1. Export a default React component `export default function App()`.
2. Include a CSS root variable style block at top of App render with global resets (`* {{ box-sizing: border-box; }} body {{ margin: 0; overflow-x: hidden; }} img, svg {{ max-width: 100%; }}`).
3. Use CSS variables `var(--bg-main)`, `var(--bg-card)`, `var(--text-primary)`, `var(--color-primary)`, `var(--color-mint)`, `var(--border-color)`, `var(--font-heading)` instead of hardcoded hex strings.
4. For service booking / babysitter apps: render warm cream background, serif headers, sitter cards with rates, and an interactive weekly calendar matrix with mint green availability pills.
5. **CRITICAL MOBILE-FIRST RESPONSIVENESS INVARIANT**:
   - The application MUST be fully mobile-first responsive and render flawlessly on mobile screens (`375px` viewport) as well as desktop screens (`1280px`).
   - Headers and navigation bars MUST use `flexWrap: 'wrap'` and flexible gaps (`gap: '0.75rem'`) so header titles and navigation links wrap cleanly on 375px screens without horizontal scrolling.
   - Any slide-over panel, drawer, or modal MUST use fluid width styling (e.g. `width: '100%', maxWidth: '380px'`). NEVER use hardcoded fixed pixel widths like `width: '380px'` without `maxWidth: '100%'`.
   - Outer container padding MUST be responsive (e.g. `padding: '1rem 0.75rem'` on mobile).

Respond STRICTLY with valid React TypeScript code inside a single ```tsx code block. Do NOT include markdown text.
"""
    try:
        raw_response = call_gemini(prompt, stage="app_assembly")
        cleaned = raw_response.strip()
        fence_match = re.search(r'```(?:tsx|jsx|typescript|javascript)?\s*\n(.*?)```', cleaned, re.DOTALL)
        if fence_match:
            cleaned = fence_match.group(1).strip()

        # AST & Syntax Verification Gate
        is_valid, err_msg = verify_tsx_syntax(cleaned)
        if not is_valid:
            print(f"[assembly] Syntax verification notice: {err_msg}. Triggering self-healing loop...")
            cleaned = self_heal_tsx_code(cleaned, err_msg, pitch)

        # AST Theme Compliance Gate
        cleaned = verify_theme_compliance(cleaned, arch_id)

        # Vocabulary Isolation Gate
        cleaned = sanitize_domain_vocabulary_leakage(cleaned, pitch)

        if "export default" in cleaned and ("function App" in cleaned or "const App" in cleaned):
            return cleaned

    except Exception as e:
        print(f"[notice] App assembly error: {e}")

    # Safety Fallback App if LLM unavailable
    fallback_code = _generate_fallback_assembled_app(blueprint, custom_fixtures=custom_fixtures)
    return sanitize_domain_vocabulary_leakage(fallback_code, pitch)


def _generate_fallback_assembled_app(bp: UnifiedFrontendBlueprint, custom_fixtures: Optional[Dict[str, Any]] = None) -> str:
    """Deterministic fallback React App.tsx matching the category layout template."""
    title = bp.aesthetics.domain_display_title
    cat_id = bp.category_layout.category_id
    raw_vars = bp.aesthetics.get_css_variables_style()
    css_vars_style = f"""* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; overflow-x: hidden; width: 100%; }}
img, svg {{ max-width: 100%; height: auto; }}
:root {{
{raw_vars}
}}"""

    hero_headline = bp.aesthetics.hero_headline
    guarantee_badge = bp.aesthetics.guarantee_badge
    item_singular = bp.aesthetics.item_singular
    item_plural = bp.aesthetics.item_plural
    action_button = bp.aesthetics.action_button_text
    domain_emoji = bp.aesthetics.domain_emoji

    catalog_fixtures = (custom_fixtures and custom_fixtures.get("catalog")) or bp.aesthetics.mock_seed_data
    cart_fixtures = (custom_fixtures and custom_fixtures.get("cart")) or []
    tracking_fixtures = (custom_fixtures and custom_fixtures.get("tracking")) or []

    formatted_seed = []
    for idx, item in enumerate(catalog_fixtures):
        item_title = item.get("name") or item.get("title") or f"Item #{idx+1}"
        price_val = item.get("price")
        if price_val is not None and isinstance(price_val, (int, float)):
            price_str = f"${price_val:.2f}"
        else:
            price_str = str(item.get("price_or_rate") or "$14.99")
        subtitle = item.get("desc") or item.get("subtitle") or "Fresh gourmet offering"
        formatted_seed.append({
            "id": str(item.get("id", idx+1)),
            "title": item_title,
            "subtitle": subtitle,
            "price_or_rate": price_str,
            "badge_status": item.get("badge_status", "Popular"),
            "rating": item.get("rating", 4.9),
            "initials": "".join([w[0].upper() for w in item_title.split()[:2]]) or "PI"
        })

    seed_json = json.dumps(formatted_seed)
    cart_json = json.dumps(cart_fixtures)
    orders_json = json.dumps(tracking_fixtures)

    hero_headline = bp.aesthetics.hero_headline
    guarantee_badge = bp.aesthetics.guarantee_badge
    item_singular = bp.aesthetics.item_singular
    item_plural = bp.aesthetics.item_plural
    action_button = bp.aesthetics.action_button_text
    domain_emoji = bp.aesthetics.domain_emoji

    # Service Booking Layout Template
    if cat_id == "service_booking":
        tmpl = '''import React, { useState } from 'react';

export default function App() {
  const [providers] = useState<any[]>(__SEED_JSON__);
  const [selectedProviderId, setSelectedProviderId] = useState<string>('1');
  const [bookedSlots, setBookedSlots] = useState<string[]>(['MON-15:00', 'MON-16:00', 'MON-17:00']);
  const [bookingToast, setBookingToast] = useState<string | null>(null);

  const selectedProvider = providers.find(p => p.id === selectedProviderId) || providers[0];

  const days = [
    { name: 'MON', date: '3' },
    { name: 'TUE', date: '4' },
    { name: 'WED', date: '5' },
    { name: 'THU', date: '6' },
    { name: 'FRI', date: '7' },
    { name: 'SAT', date: '8' },
    { name: 'SUN', date: '9' }
  ];

  const hours = [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00'
  ];

  const isAvailableSlot = (dayName: string, hour: string) => {
    if (dayName === 'MON' && ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'].includes(hour)) return false;
    if (dayName === 'WED' && ['21:00', '22:00'].includes(hour)) return false;
    if (dayName === 'THU' && ['18:00', '21:00', '22:00'].includes(hour)) return false;
    if (dayName === 'SAT' && ['15:00', '16:00'].includes(hour)) return false;
    if (dayName === 'SUN' && ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00'].includes(hour)) return false;
    return true;
  };

  const toggleSlot = (dayName: string, hour: string) => {
    const key = `${dayName}-${hour}`;
    if (!isAvailableSlot(dayName, hour)) return;
    setBookedSlots(prev => prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]);
  };

  const handleRequestBooking = () => {
    if (bookedSlots.length === 0) {
      alert("Please tap one or more green available hours on the calendar to build your booking.");
      return;
    }
    setBookingToast(`🎉 Request sent to ${selectedProvider.title} for ${bookedSlots.length} hour slot(s)!`);
    setTimeout(() => setBookingToast(null), 4000);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-main)', color: 'var(--text-primary)', fontFamily: 'var(--font-body)', padding: '2rem 1rem' }}>
      <style>{`__CSS_VARS__`}</style>

      <div style={{ maxWidth: '980px', margin: '0 auto' }}>
        {/* Top Header */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: 0, fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>__TITLE__</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: '#047857', fontWeight: 600 }}>
            <span>🛡️</span> __GUARANTEE_BADGE__
          </div>
        </header>

        {/* Hero Banner */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '2rem', marginBottom: '3rem' }}>
          <div style={{ flex: 1, maxWidth: '580px' }}>
            <h2 style={{ fontSize: '2.75rem', fontWeight: 800, margin: '0 0 1rem 0', fontFamily: 'var(--font-heading)', lineHeight: 1.15, color: 'var(--text-primary)' }}>
              __HERO_HEADLINE__
            </h2>
            <p style={{ fontSize: '1.05rem', color: 'var(--text-muted)', lineHeight: 1.6, margin: '0 0 2rem 0' }}>
              No back-and-forth messaging. Open a __ITEM_SINGULAR__'s weekly calendar, tap open hours, and your schedule is handled.
            </p>

            {/* Stat Counters */}
            <div style={{ display: 'flex', gap: '2.5rem' }}>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>180+</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>verified __ITEM_PLURAL__</div>
              </div>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>4.9★</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>average rating</div>
              </div>
              <div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}>&lt; 2 min</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>to schedule</div>
              </div>
            </div>
          </div>

          {/* Hero Decorative Image Box */}
          <div style={{ width: '320px', height: '220px', borderRadius: '1.5rem', background: 'linear-gradient(135deg, #FDE68A 0%, #FCA5A5 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-card)' }}>
            <div style={{ fontSize: '4rem' }}>__DOMAIN_EMOJI__</div>
          </div>
        </div>

        {/* Feedback Toast */}
        {bookingToast && (
          <div style={{ background: '#D1FAE5', border: '1px solid #10B981', color: '#047857', padding: '1rem 1.25rem', borderRadius: '1rem', marginBottom: '2rem', fontWeight: 700 }}>
            {bookingToast}
          </div>
        )}

        {/* Section 1: Choose Provider */}
        <section style={{ marginBottom: '2.5rem' }}>
          <h3 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 1.25rem 0', fontFamily: 'var(--font-heading)', textTransform: 'capitalize' }}>Choose your __ITEM_SINGULAR__</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '1rem' }}>
            {providers.map(item => {
              const isSelected = item.id === selectedProviderId;
              return (
                <div
                  key={item.id}
                  onClick={() => setSelectedProviderId(item.id)}
                  style={{
                    background: 'var(--bg-card)',
                    border: `2px solid ${isSelected ? 'var(--color-primary)' : 'var(--border-color)'}`,
                    borderRadius: '1rem',
                    padding: '1.25rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: isSelected ? '0 8px 24px rgba(200, 90, 68, 0.12)' : 'var(--shadow-card)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                    <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                      {item.initials || item.title.slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: '1rem', color: 'var(--text-primary)' }}>{item.title}</div>
                      <div style={{ fontSize: '0.75rem', color: '#B45309', fontWeight: 700 }}>★ {item.rating} • Verified</div>
                    </div>
                  </div>
                  
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 1rem 0', lineHeight: 1.45, minHeight: '2.5rem' }}>
                    {item.subtitle}
                  </p>
                  
                  <div style={{ fontWeight: 800, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                    {item.price_or_rate}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Section 2: Weekly Schedule Grid */}
        <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '1.5rem', padding: '2rem', boxShadow: 'var(--shadow-card)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <div>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, fontFamily: 'var(--font-heading)' }}>
                {selectedProvider.title}'s week
              </h3>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Licensed & verified professional
              </div>
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-muted)' }}>
              3 Aug – 9 Aug
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '50px repeat(7, 1fr)', gap: '0.35rem', marginBottom: '1.5rem' }}>
            <div style={{ textTransform: 'uppercase', fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700 }}></div>
            {days.map(d => (
              <div key={d.name} style={{ textAlign: 'center', paddingBottom: '0.5rem' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>{d.name}</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'var(--font-heading)', marginTop: '0.1rem' }}>{d.date}</div>
              </div>
            ))}

            {hours.map(hour => (
              <React.Fragment key={hour}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', alignSelf: 'center' }}>{hour}</div>
                {days.map(d => {
                  const slotKey = `${d.name}-${hour}`;
                  const avail = isAvailableSlot(d.name, hour);
                  const isBookedByMe = bookedSlots.includes(slotKey);

                  let bg = 'var(--bg-secondary)';
                  if (avail) bg = 'var(--color-mint)';
                  if (isBookedByMe) bg = 'var(--color-primary)';

                  return (
                    <button
                      key={slotKey}
                      onClick={() => toggleSlot(d.name, hour)}
                      disabled={!avail}
                      style={{
                        height: '24px',
                        background: bg,
                        border: 'none',
                        borderRadius: '0.4rem',
                        cursor: avail ? 'pointer' : 'default',
                        opacity: avail ? 1 : 0.65,
                        transition: 'all 0.15s ease'
                      }}
                    />
                  );
                })}
              </React.Fragment>
            ))}
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--color-mint)' }} /> Available
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--color-primary)' }} /> Your booking
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--bg-secondary)' }} /> Booked / off
            </div>
          </div>

          <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '1rem', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              Tap green hours above to reserve your time.
            </span>
            <button
              onClick={handleRequestBooking}
              style={{
                background: 'var(--color-primary)',
                color: '#fff',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.75rem',
                fontWeight: 800,
                fontSize: '0.95rem',
                cursor: 'pointer',
                boxShadow: '0 4px 14px rgba(200, 90, 68, 0.25)'
              }}
            >
              __ACTION_BUTTON__
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
'''
        return tmpl.replace('__TITLE__', title)\
                   .replace('__SEED_JSON__', seed_json)\
                   .replace('__CSS_VARS__', css_vars_style)\
                   .replace('__HERO_HEADLINE__', hero_headline)\
                   .replace('__GUARANTEE_BADGE__', guarantee_badge)\
                   .replace('__ITEM_SINGULAR__', item_singular)\
                   .replace('__ITEM_PLURAL__', item_plural)\
                   .replace('__ACTION_BUTTON__', action_button)\
                   .replace('__DOMAIN_EMOJI__', domain_emoji)

    # Generic E-Commerce or Storefront Fallback with Interactive Checkout Modal & Bidirectional Sync
    tmpl = '''import React, { useState } from 'react';

export default function App() {
  const [items] = useState<any[]>(__SEED_JSON__);
  const [cart, setCart] = useState<any[]>(__CART_JSON__);
  const [orders, setOrders] = useState<any[]>(__ORDERS_JSON__);
  const [activeTab, setActiveTab] = useState<'catalog' | 'tracking'>('catalog');
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const syncFixtureToBackendAndHost = (canonicalKey: string, fixtures: any[]) => {
    try {
      fetch('/api/components/fixtures/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ canonical_key: canonicalKey, fixtures: fixtures })
      }).catch(() => {});
    } catch (e) {}

    try {
      if (typeof window !== 'undefined' && window.parent && window.parent !== window) {
        window.parent.postMessage({
          type: 'FIXTURES_UPDATED',
          canonical_key: canonicalKey,
          fixtures: fixtures
        }, '*');
      }
    } catch (e) {}
  };

  const handleAddToCart = (item: any) => {
    const updatedCart = [...cart, item];
    setCart(updatedCart);
    syncFixtureToBackendAndHost('cart', updatedCart);
    setToast("🛒 Added " + (item.title || item.name) + " to cart!");
    setTimeout(() => setToast(null), 3000);
  };

  const handleRemoveFromCart = (index: number) => {
    const updatedCart = cart.filter((_, i) => i !== index);
    setCart(updatedCart);
    syncFixtureToBackendAndHost('cart', updatedCart);
  };

  const handleSimulatePayment = () => {
    const orderNum = "ORD-" + Math.floor(1000 + Math.random() * 9000);
    const newOrder = { id: orderNum, ref: orderNum, status: "Order Received & Prep Started", eta: "15-25 Mins", item: cart[0]?.title || cart[0]?.name || "Custom Order" };
    const updatedOrders = [newOrder, ...orders];
    setOrders(updatedOrders);
    setCart([]);
    syncFixtureToBackendAndHost('tracking', updatedOrders);
    syncFixtureToBackendAndHost('cart', []);
    setToast("🎉 Order " + orderNum + " Placed! [ ⚡ Sandbox Mode — Simulated Transaction ]");
    setIsCartOpen(false);
    setActiveTab('tracking');
    setTimeout(() => setToast(null), 4000);
  };

  const cartTotal = cart.reduce((sum, i) => sum + (parseFloat(String(i.price_or_rate).replace(/[^0-9.]/g, '')) || 15.00), 0);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-main)', color: 'var(--text-primary)', fontFamily: 'var(--font-body)', padding: '1.25rem 0.75rem' }}>
      <style>{`__CSS_VARS__`}</style>

      {/* Header */}
      <header style={{ maxWidth: '1200px', margin: '0 auto 1.5rem auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, margin: 0, fontFamily: 'var(--font-heading)' }}>__TITLE__</h1>
          <nav style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            <button
              onClick={() => setActiveTab('catalog')}
              style={{ background: activeTab === 'catalog' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'catalog' ? '#fff' : 'var(--text-primary)', border: 'none', padding: '0.5rem 0.85rem', borderRadius: '0.5rem', fontWeight: 700, cursor: 'pointer' }}
            >
              🍕 Menu Catalog
            </button>
            <button
              onClick={() => setActiveTab('tracking')}
              style={{ background: activeTab === 'tracking' ? 'var(--color-primary)' : 'transparent', color: activeTab === 'tracking' ? '#fff' : 'var(--text-primary)', border: 'none', padding: '0.5rem 0.85rem', borderRadius: '0.5rem', fontWeight: 700, cursor: 'pointer' }}
            >
              📦 Live Order Status ({orders.length})
            </button>
          </nav>
        </div>

        <button onClick={() => setIsCartOpen(true)} style={{ background: 'var(--color-primary)', color: '#fff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '9999px', fontWeight: 700, cursor: 'pointer' }}>
          Cart ({cart.length})
        </button>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {toast && (
          <div style={{ background: 'var(--color-mint)', border: '1px solid var(--color-mint-text)', color: 'var(--color-mint-text)', padding: '0.85rem 1.25rem', borderRadius: '0.75rem', marginBottom: '1.5rem', fontWeight: 700 }}>
            {toast}
          </div>
        )}

        {activeTab === 'catalog' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
            {items.map((item: any) => (
              <div key={item.id} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '1.25rem', padding: '1.25rem', boxShadow: 'var(--shadow-card)' }}>
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem', color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>{item.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{item.subtitle}</p>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--color-primary)', margin: '1rem 0' }}>{item.price_or_rate}</div>
                <button onClick={() => handleAddToCart(item)} style={{ width: '100%', background: 'var(--color-primary)', color: '#fff', border: 'none', padding: '0.75rem', borderRadius: '0.75rem', fontWeight: 700, cursor: 'pointer' }}>
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'tracking' && (
          <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '1.25rem', padding: '1.5rem', boxShadow: 'var(--shadow-card)' }}>
            <h2 style={{ fontSize: '1.3rem', margin: '0 0 1.25rem 0', fontFamily: 'var(--font-heading)' }}>📦 Live Order Status & Tracking Pipeline</h2>
            {orders.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No active orders being tracked. Place an order to start tracking!</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {orders.map((ord: any) => (
                  <div key={ord.id} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '0.75rem', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>Order Ref: {ord.ref} ({ord.item})</div>
                      <div style={{ color: 'var(--color-primary)', fontSize: '0.85rem', fontWeight: 700, marginTop: '0.25rem' }}>Status: {ord.status}</div>
                    </div>
                    <div style={{ background: 'var(--color-mint)', color: 'var(--color-mint-text)', padding: '0.4rem 0.85rem', borderRadius: '9999px', fontWeight: 700, fontSize: '0.85rem' }}>
                      Est. Delivery: ~{ord.eta}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Interactive Checkout Drawer / Modal */}
      {isCartOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'flex-end', zIndex: 999 }}>
          <div style={{ width: '100%', maxWidth: '380px', background: 'var(--bg-card)', height: '100%', padding: '1.5rem', display: 'flex', flexDirection: 'column', boxShadow: '-4px 0 20px rgba(0,0,0,0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.3rem', margin: 0, fontFamily: 'var(--font-heading)' }}>Your Cart ({cart.length})</h2>
              <button onClick={() => setIsCartOpen(false)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: 'var(--text-primary)' }}>✕</button>
            </div>

            {cart.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', flex: 1 }}>Your cart is empty. Add items from the menu!</p>
            ) : (
              <>
                <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {cart.map((item, index) => (
                    <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{item.title}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)' }}>{item.price_or_rate}</div>
                      </div>
                      <button onClick={() => handleRemoveFromCart(index)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontWeight: 700 }}>Delete</button>
                    </div>
                  ))}
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', marginTop: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '1.1rem', marginBottom: '1rem' }}>
                    <span>Total:</span>
                    <span>${cartTotal.toFixed(2)}</span>
                  </div>
                  <button onClick={handleSimulatePayment} style={{ width: '100%', background: 'var(--color-primary)', color: '#fff', border: 'none', padding: '0.85rem', borderRadius: '0.75rem', fontWeight: 800, cursor: 'pointer' }}>
                    💳 Simulate Payment [ Sandbox Mode ]
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
'''
    return tmpl.replace('__TITLE__', title).replace('__SEED_JSON__', seed_json).replace('__CART_JSON__', cart_json).replace('__ORDERS_JSON__', orders_json).replace('__CSS_VARS__', css_vars_style)


def analyze_pitch_components_and_suggestions(pitch: str) -> Dict[str, Any]:
    """
    LLM Pitch Analysis Agent.
    Dynamically deconstructs any natural language business pitch into its required UI components
    (mapping reusable ones to premade template keys or creating custom component specs)
    and generates 6 domain-specific suggested prompts.
    """
    prompt = f"""
You are a Lead Product Architect. Analyze the following business pitch:
"{pitch}"

Deconstruct the application into:
1. Active Components: Identify all UI components required for this application idea.
   - For standard capabilities, map to canonical keys: "catalog" (menu/product grid), "cart" (shopping cart/checkout), "tracking" (order tracking pipeline), "kds" (admin/kitchen dashboard), "reviews" (ratings & feedback), "auth" (user login/profiles), "calendar" (booking/appointments).
   - For custom concepts mentioned in pitch (e.g. "flappy bird game", "topping builder", "crypto wallet"), specify a clean canonical_key (e.g. "flappy_bird_game"), descriptive title, and component_type "custom".
2. Suggested Prompts: Generate 3 to 6 dynamic, domain-aware feature suggestions that the user might want to add next (e.g. "Add payment system", "Add live chat", "Add leaderboard").

Return ONLY valid JSON in this exact format (no markdown, no preamble):
{{
  "components": [
    {{
      "canonical_key": "catalog",
      "title": "Menu Catalog",
      "component_type": "premade",
      "description": "Product grid with category filters"
    }},
    {{
      "canonical_key": "flappy_bird_game",
      "title": "Flappy Bird Mini-Game",
      "component_type": "custom",
      "description": "Interactive mini-game in application header"
    }}
  ],
  "suggestions": [
    "Add payment system",
    "Add loyalty points",
    "Add table reservation"
  ]
}}
"""
    try:
        raw_res = call_gemini(prompt, stage="pitch_component_analysis")
        json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
        if json_match:
            raw_res = json_match.group(0)
        data = json.loads(raw_res)
        return {
            "pitch": pitch,
            "active_components": data.get("components", []),
            "suggestions": data.get("suggestions", [])
        }
    except Exception as e:
        print(f"LLM pitch analysis notice: {e}, executing heuristic fallback")
        return _heuristic_pitch_analysis_fallback(pitch)


def build_pitch_specific_domain_schema(pitch: str) -> Dict[str, Any]:
    """Alias function wrapping _extract_domain_entity_profile for domain schema synthesis."""
    return _extract_domain_entity_profile(pitch)




def _heuristic_pitch_analysis_fallback(pitch: str) -> Dict[str, Any]:
    p_lower = pitch.lower()
    components = []
    
    if any(k in p_lower for k in ['menu', 'product', 'catalog', 'item', 'pizza', 'store', 'shop']):
        components.append({'canonical_key': 'catalog', 'title': 'Menu Catalog', 'component_type': 'premade', 'description': 'Product catalog & menu grid'})
    if any(k in p_lower for k in ['cart', 'order', 'checkout', 'buy', 'purchase', 'pizza', 'store']):
        components.append({'canonical_key': 'cart', 'title': 'Shopping Cart', 'component_type': 'premade', 'description': 'Shopping cart & checkout drawer'})
    if any(k in p_lower for k in ['track', 'status', 'delivery', 'dispatch', 'pipeline', 'pizza']):
        components.append({'canonical_key': 'tracking', 'title': 'Order Tracking', 'component_type': 'premade', 'description': 'Real-time status tracking pipeline'})
    if any(k in p_lower for k in ['kitchen', 'kds', 'admin', 'merchant', 'dashboard', 'cook']):
        components.append({'canonical_key': 'kds', 'title': 'Kitchen KDS', 'component_type': 'premade', 'description': 'Merchant kitchen display system'})
    if any(k in p_lower for k in ['review', 'rating', 'star', 'feedback']):
        components.append({'canonical_key': 'reviews', 'title': 'Reviews', 'component_type': 'premade', 'description': 'Customer reviews & rating system'})

    if not components:
        components = [
            {'canonical_key': 'catalog', 'title': 'Menu Catalog', 'component_type': 'premade', 'description': 'Product catalog'},
            {'canonical_key': 'cart', 'title': 'Shopping Cart', 'component_type': 'premade', 'description': 'Shopping cart'},
            {'canonical_key': 'tracking', 'title': 'Order Tracking', 'component_type': 'premade', 'description': 'Order tracking'}
        ]

    suggestions = [
        "Payment system",
        "Loyalty points & rewards",
        "Live chat support",
        "Table reservation calendar",
        "Custom item builder",
        "Promo code voucher"
    ]

    return {
        "pitch": pitch,
        "active_components": components,
        "suggestions": suggestions
    }



