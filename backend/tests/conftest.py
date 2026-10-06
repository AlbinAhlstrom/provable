import atexit
import json
import os
import re
import shutil
import sys
import tempfile

import pytest

# ── Hermetic workspace ────────────────────────────────────────────────────────
# Several tests drive the real API (TestClient), including /api/onboarding/kickstart and /reset.
# Without isolation they overwrite or wipe the live `workspace/` and its database, which
# desynchronizes a running app from its files. Point the whole session at a throwaway
# workspace + database BEFORE any backend module reads its configuration.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
_TEST_WORKSPACE = tempfile.mkdtemp(prefix="provable-test-ws-")
os.makedirs(os.path.join(_TEST_WORKSPACE, "requirements"), exist_ok=True)
os.environ["PROVABLE_WORKSPACE"] = _TEST_WORKSPACE
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_TEST_WORKSPACE, "requirements", "provable.db")
atexit.register(shutil.rmtree, _TEST_WORKSPACE, ignore_errors=True)
from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold  # noqa: E402
create_default_workspace_scaffold(_TEST_WORKSPACE)


@pytest.fixture(autouse=True)
def mock_allure_client_network_calls(monkeypatch):
    """
    Autouse fixture ensuring unit tests never block on external network I/O or timeouts.
    """
    try:
        from integrations import allure_client
        monkeypatch.setattr(
            allure_client,
            "load_allure_config",
            lambda: {"enabled": False, "server_url": "http://localhost:5050", "project_id": "default"}
        )
        monkeypatch.setattr(allure_client, "trigger_allure_generation", lambda: None)
    except ImportError:
        pass


@pytest.fixture(autouse=True)
def mock_llm_for_unit_tests(monkeypatch):
    """
    Hermetic Unit Test Mock for LLM calls:
    Returns structured, schema-compliant JSON payloads for unit tests
    so that production code has ZERO keyword tokenizers or mock heuristics.
    """
    try:
        import agent_orchestrator

        def fake_call_gemini(prompt: str, stage: str = "general", **_options) -> str:
            if stage == "domain_ontology":
                m = re.search(r'"([^"\n]+)"', prompt)
                pitch = m.group(1) if m else "Generic Application"

                # Extract domain noun from pitch
                clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', pitch).strip()
                tokens = [w.capitalize() for w in clean.split() if len(w) > 2 and w.lower() not in {"an", "a", "the", "app", "application", "platform", "system", "tool", "portal", "site", "online", "for", "with", "order", "book", "buy", "sell", "track", "manage", "find", "schedule", "rent"}]
                raw_noun = tokens[0] if tokens else "Item"
                noun = raw_noun[:-1] if raw_noun.endswith("s") and len(raw_noun) > 3 and not raw_noun.endswith("ss") else raw_noun
                plural = f"{noun}s" if not noun.endswith("s") else noun

                return json.dumps({
                    "brand_name": f"{noun}Craft",
                    "hero_headline": f"Premium {plural} Platform",
                    "guarantee_badge": f"100% Certified {plural}",
                    "domain_category": "custom_domain",
                    "visual_theme": {
                        "archetype": "modern_fresh_light",
                        "primary_color": "#0284c7",
                        "secondary_color": "#10b981",
                        "bg_gradient": "#f8fafc",
                        "card_bg": "#ffffff",
                        "border_color": "#e2e8f0",
                        "domain_emoji": "✨"
                    },
                    "master_entity": {
                        "entity_name": noun,
                        "entity_plural": plural,
                        "action_verb": f"Select {noun}",
                        "attributes": [
                            {"name": "name", "type": "string", "required": True, "display_mode": "visible"},
                            {"name": "price", "type": "currency", "required": True, "display_mode": "visible"},
                            {"name": "specs", "type": "tags", "required": False, "default_value": [], "display_mode": "tag_chips"},
                            {"name": "rating", "type": "number", "required": False, "default_value": 5.0, "display_mode": "badge"},
                            {"name": "badge", "type": "string", "required": False, "default_value": "Popular", "display_mode": "badge"}
                        ],
                        "seed_items": [
                            {"id": "1", "name": f"Signature {noun}", "price": 19.99, "specs": ["Quality"], "rating": 5.0, "badge": "Best"},
                            {"id": "2", "name": f"Deluxe {noun}", "price": 29.99, "specs": ["Deluxe"], "rating": 4.9, "badge": "Popular"}
                        ]
                    },
                    "capabilities": [
                        {"key": "catalog", "name": f"{noun} Catalog", "icon": "📋", "description": f"Browse {noun.lower()} items", "target_entities": [noun], "primary_actions": [f"Select {noun}"]},
                        {"key": "cart", "name": "Order Drawer & Checkout", "icon": "🛒", "description": "Review and order", "target_entities": [noun], "primary_actions": ["Place Order"]},
                        {"key": "tracking", "name": "Status Pipeline", "icon": "📦", "description": "Status progression", "target_entities": [noun], "primary_actions": ["Track Status"]}
                    ],
                    "commands": [{"name": f"Place{noun}Order", "description": "Order command", "fields": [{"name": "id", "type": "str"}]}],
                    "events": [{"name": f"{noun}OrderPlaced", "description": "Order event", "fields": [{"name": "id", "type": "str"}]}],
                    "invariants": [f"Valid non-negative pricing for {noun.lower()} transactions"]
                })
            elif stage == "category_planning":
                return json.dumps({
                    "category_id": "custom_domain",
                    "layout_name": "Application Workspace",
                    "category_reasoning": "Standard layout"
                })
            elif stage == "component_planning":
                return json.dumps({
                    "reused_registry_blocks": [],
                    "bespoke_components": [
                        {"component_name": "HeaderView", "slot": "header", "description": "Header", "key_interactions": []},
                        {"component_name": "MainContentView", "slot": "main_content", "description": "Content", "key_interactions": []}
                    ]
                })
            elif stage == "aesthetic_planning":
                return json.dumps({
                    "domain_display_title": "AppCraft",
                    "theme_archetype": "modern_fresh_light",
                    "primary_color": "#0284c7",
                    "seed_catalog": [
                        {"id": "1", "title": "Item 1", "price_or_rate": "$19.99"}
                    ]
                })
            elif stage == "ui_generation":
                return "import React from 'react'; export default function App() { return <div>App Shell</div>; }"
            elif stage == "pitch_component_analysis":
                return json.dumps({
                    "domain_name": "DynamicDomain",
                    "components": [{"key": "catalog", "name": "Catalog View", "target_entities": ["Item"]}],
                    "suggestions": ["Smart Allocation Engine", "Telemetry Live Stream", "Realtime Security Monitor"]
                })
            elif stage == "intent_classification":
                return json.dumps({
                    "product_type": "customer_app",
                    "audience": "end customers",
                    "primary_goal": "Let customers use the product described in the pitch.",
                    "scope_summary": "A customer-facing application for the pitch's domain.",
                    "model_focus": ["the pitch's core entities", "the rules customers experience"],
                    "out_of_scope": [],
                    "assumptions": []
                })
            elif stage == "red_test_generation":
                # Hermetic RED test: behavioral shape, fails with AttributeError until GREEN adds the method.
                m = re.search(r"from src\.domain\.(\w+) import (\w+)", prompt)
                mod, cls = (m.group(1), m.group(2)) if m else ("model", "Entity")
                return (
                    "```python\nimport pytest\n"
                    f"from src.domain.{mod} import {cls}\n\n"
                    "def test_mock_rejected_beyond_boundary():\n"
                    f"    instance = {cls}(id=\"MOCK-1\")\n"
                    "    assert instance.validate_invariants() is True\n\n"
                    "def test_mock_accepted_at_boundary():\n"
                    f"    instance = {cls}(id=\"MOCK-2\")\n"
                    "    assert instance.validate_invariants() is True\n```"
                )
            elif stage == "green_code_repair":
                m = re.search(r"`(\w+)` containing ONLY", prompt)
                cls = m.group(1) if m else "Entity"
                return (
                    "```python\n@dataclass\n"
                    f"class {cls}:\n"
                    "    id: str\n"
                    f"    name: str = \"Standard {cls}\"\n\n"
                    "    def validate_invariants(self) -> bool:\n"
                    "        return True\n```"
                )
            elif stage == "router_decomposition":

                m = re.search(r'BUSINESS PITCH:\s*[\'"]([^\'"]+)[\'"]', prompt, re.IGNORECASE) or re.search(r'"([^"\n]+)"', prompt)
                pitch = m.group(1) if m else "Generic Application"
                clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', pitch).strip()
                is_wms = any(kw in pitch.lower() for kw in ["pallet", "zone", "operator", "warehouse", "fifo"])
                is_math = any(kw in pitch.lower() for kw in ["fifo", "shelf-life", "expire", "multiplier", "limit", "kg", "threshold", "minimum", "discount", "capacity", "30 days", "500kg", "$15"])

                if is_wms:
                    return json.dumps({
                        "structure": {
                            "domain_name": "WarehouseDomain",
                            "entities": [
                                {
                                    "name": "Pallet",
                                    "is_aggregate_root": True,
                                    "attributes": [
                                        {"name": "id", "type": "str", "required": True, "default_value": None},
                                        {"name": "name", "type": "str", "required": True, "default_value": "Standard Pallet"}
                                    ],
                                    "relationships": []
                                },
                                {
                                    "name": "Zone",
                                    "is_aggregate_root": True,
                                    "attributes": [
                                        {"name": "id", "type": "str", "required": True, "default_value": None},
                                        {"name": "name", "type": "str", "required": True, "default_value": "Default Zone"}
                                    ],
                                    "relationships": []
                                },
                                {
                                    "name": "Operator",
                                    "is_aggregate_root": True,
                                    "attributes": [
                                        {"name": "id", "type": "str", "required": True, "default_value": None},
                                        {"name": "name", "type": "str", "required": True, "default_value": "Main Operator"}
                                    ],
                                    "relationships": []
                                }
                            ],
                            "value_objects": [],
                            "enums": []
                        },
                        "inbox": {
                            "domain_name": "WarehouseDomain",
                            "specs": [
                                {
                                    "spec_id": "SPEC-WMS-001",
                                    "title": "Enforce Pallet Creation",
                                    "description": "Pallets must be initialized with valid identifiers.",
                                    "given_when_then": "Given valid pallet parameters When instantiating Pallet Then pallet is created successfully",
                                    "target_aggregate": "Pallet",
                                    "spec_type": "ATTRIBUTE_EXPANSION",
                                    "is_mathematical_boundary": False,
                                    "priority": "High",
                                    "status": "PENDING"
                                },
                                {
                                    "spec_id": "SPEC-WMS-002",
                                    "title": "Enforce Storage Zone Capacity Boundary" if is_math else "Enforce Storage Zone Allocation",
                                    "description": "Validates capacity and allocation rules for warehouse storage zones.",
                                    "given_when_then": "Given a storage Zone When allocating Pallets Then total weight complies with capacity limits",
                                    "target_aggregate": "Zone",
                                    "spec_type": "DOMAIN_INVARIANT",
                                    "is_mathematical_boundary": is_math,
                                    "priority": "High",
                                    "status": "PENDING"
                                }
                            ]
                        }
                    })

                tokens = [w.capitalize() for w in clean.split() if len(w) > 2 and w.lower() not in {"an", "a", "the", "app", "application", "platform", "system", "tool", "portal", "site", "online", "for", "with", "order", "book", "buy", "sell", "track", "manage", "find", "schedule", "rent", "where", "customers"}]
                raw_noun = tokens[0] if tokens else "Item"
                if raw_noun.lower() in ("pizzeria", "pizzas"):
                    raw_noun = "Pizza"
                noun = raw_noun[:-1] if raw_noun.endswith("s") and len(raw_noun) > 3 and not raw_noun.endswith("ss") else raw_noun
                
                return json.dumps({
                    "structure": {
                        "domain_name": f"{noun}Domain",
                        "entities": [
                            {
                                "name": f"{noun}Order" if "order" in pitch.lower() or "pizza" in pitch.lower() else noun,
                                "is_aggregate_root": True,
                                "attributes": [
                                    {"name": "id", "type": "str", "required": True, "default_value": None},
                                    {"name": "status", "type": "str", "required": True, "default_value": "PENDING"},
                                    {"name": "total_amount", "type": "float", "required": True, "default_value": 0.0}
                                ],
                                "relationships": [
                                    {"target": f"{noun}Item", "relation_type": "one_to_many"}
                                ]
                            }
                        ],
                        "value_objects": [
                            {
                                "name": f"{noun}Item",
                                "is_aggregate_root": False,
                                "attributes": [
                                    {"name": "name", "type": "str", "required": True, "default_value": None},
                                    {"name": "price", "type": "float", "required": True, "default_value": 0.0}
                                ]
                            }
                        ]
                    },
                    "inbox": {
                        "domain_name": f"{noun}Domain",
                        "specs": [
                            {
                                "spec_id": "SPEC-001",
                                "title": f"Enforce {noun} Creation Invariant",
                                "description": f"Validates {noun.lower()} attributes upon initialization.",
                                "given_when_then": f"Given a new {noun} When instantiating with valid attributes Then object is created successfully",
                                "target_aggregate": f"{noun}Order" if "order" in pitch.lower() or "pizza" in pitch.lower() else noun,
                                "spec_type": "ATTRIBUTE_EXPANSION",
                                "is_mathematical_boundary": False,
                                "priority": "High",
                                "status": "PENDING"
                            },
                            {
                                "spec_id": "SPEC-002",
                                "title": f"Enforce {noun} Custom Topping & Multiplier Rules" if ("topping" in pitch.lower() or "multiplier" in pitch.lower()) else (f"Enforce {noun} Boundary Rules" if is_math else f"Enforce {noun} Domain Calculation Rules"),
                                "description": f"Calculates rates or applies boundary thresholds for {noun.lower()}.",
                                "given_when_then": f"Given an active {noun} When applying size multipliers or boundary limits Then total amount conforms to rules",
                                "target_aggregate": f"{noun}Order" if "order" in pitch.lower() or "pizza" in pitch.lower() else noun,
                                "spec_type": "DOMAIN_INVARIANT",
                                "is_mathematical_boundary": is_math,
                                "priority": "High",
                                "status": "PENDING"
                            }
                        ]
                    }
                })

            return "{}"

        import sys
        monkeypatch.setattr(agent_orchestrator, "call_gemini", fake_call_gemini)
        for mod_name in [
            "onboarding.frontend_planning_engine",
            "onboarding.requirement_generator",
            "onboarding.code_verifier",
            "onboarding.test_importer",
            "onboarding.domain_ontology",
            "onboarding.router_engine",
            "service_layer.tdd_machine"
        ]:
            try:
                mod = sys.modules.get(mod_name) or __import__(mod_name, fromlist=["call_gemini"])
                if hasattr(mod, "call_gemini"):
                    monkeypatch.setattr(mod, "call_gemini", fake_call_gemini)
            except Exception:
                pass
    except ImportError:
        pass

