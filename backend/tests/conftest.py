import os
import sys
import json
import re
import pytest

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass


@pytest.fixture(autouse=True)
def mock_external_network_gateways(monkeypatch, request):
    """
    Autouse fixture ensuring unit tests never block on external network I/O, Allure, or OpenCode probes.
    """
    if "boss_fight" in request.keywords and os.environ.get("RUN_BOSS_FIGHTS"):
        return

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
def isolate_test_workspace(monkeypatch, tmp_path_factory, request):
    """
    Hermetic Workspace Isolation Fixture:
    Redirects config_loader.get_workspace_base and PROVABLE_WORKSPACE to a temporary directory
    for all unit and integration tests.
    Strictly protects the user's active live workspace from being wiped, mutated, or overwritten
    by tests running kickstart or reset endpoints.
    Bypassed only when running live boss fight tests with RUN_BOSS_FIGHTS=1.
    """
    if "boss_fight" in request.keywords and os.environ.get("RUN_BOSS_FIGHTS"):
        return

    test_ws = tmp_path_factory.mktemp("hermetic_workspace")
    test_ws_str = str(test_ws)

    # Initialize minimal workspace scaffold structure
    from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold
    create_default_workspace_scaffold(test_ws_str)

    # Set default environment variable
    monkeypatch.setenv("PROVABLE_WORKSPACE", test_ws_str)

    def _get_test_ws():
        env_ws = os.environ.get("PROVABLE_WORKSPACE")
        if env_ws and os.path.exists(env_ws):
            return os.path.abspath(env_ws)
        return test_ws_str

    # Monkeypatch config_loader.get_workspace_base
    import config_loader
    monkeypatch.setattr(config_loader, "get_workspace_base", _get_test_ws)

    # Monkeypatch get_workspace_base across all loaded modules
    import sys
    for mod in list(sys.modules.values()):
        if mod and hasattr(mod, "get_workspace_base"):
            try:
                monkeypatch.setattr(mod, "get_workspace_base", _get_test_ws)
            except Exception:
                pass


@pytest.fixture(autouse=True)
def mock_llm_for_unit_tests(monkeypatch, request):
    """
    Hermetic Unit Test Mock for LLM calls:
    Returns structured, schema-compliant JSON payloads for unit tests
    so that production code has ZERO keyword tokenizers or mock heuristics.
    Bypassed when running live boss fight tests with RUN_BOSS_FIGHTS=1.
    """
    if "boss_fight" in request.keywords and os.environ.get("RUN_BOSS_FIGHTS"):
        return

    try:

        import agent_orchestrator

        def fake_call_gemini(prompt: str, stage: str = "general") -> str:
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
                                "priority": "High",
                                "status": "PENDING"
                            }
                        ]
                    }
                })
            elif stage == "red_test_generation":
                m_spec = re.search(r"Specification ID\*\*:\s*([A-Za-z0-9_\-]+)", prompt)
                s_id = m_spec.group(1).lower().replace("-", "_") if m_spec else "spec_001"
                m_mod = re.search(r"Module Name\*\*:\s*([A-Za-z0-9_\-]+)", prompt)
                mod_name = m_mod.group(1) if m_mod else "pallet"
                m_cls = re.search(r"Target Aggregate\*\*:\s*([A-Za-z0-9_\-]+)", prompt)
                cls_name = m_cls.group(1) if m_cls else "Pallet"
                return f"""```python
import pytest
from src.domain.{mod_name} import {cls_name}

def test_{s_id}():
    instance = {cls_name}(id="TEST-001")
    assert getattr(instance, "status", None) == "AVAILABLE"
```"""
            elif stage == "green_code_repair":
                m_cls = re.search(r"Target Aggregate\*\*:\s*([A-Za-z0-9_]+)", prompt) or re.search(r"class definition for `?([A-Za-z0-9_]+)`?", prompt) or re.search(r"class\s+([A-Za-z0-9_]+)\s*:", prompt)
                cls_name = m_cls.group(1) if m_cls else "Pallet"
                return f"""```python
@dataclass
class {cls_name}:
    id: str
    name: str = "Standard {cls_name}"
    status: str = "AVAILABLE"
    events: List[Any] = field(default_factory=list)

    def validate_invariants(self) -> bool:
        return True
```"""
            elif stage == "domain_engine_synthesis":
                return json.dumps({
                    "domain_rules_py": "# Pure Python Domain Rules\ndef validate_state(state): return True",
                    "domain_state_py": "from dataclasses import dataclass\n@dataclass\nclass DomainState:\n    id: str = 'default'",
                    "domain_aggregate_py": "from dataclasses import dataclass\n@dataclass\nclass DomainAggregate:\n    id: str = 'default'",
                    "router_py": "from fastapi import APIRouter\nrouter = APIRouter(prefix='/api/test', tags=['Test'])\n@router.get('')\ndef get_items(): return []"
                })
            elif stage == "presentation_projection_synthesis":
                return json.dumps({
                    "client_ts": "export async function fetchItems() { return []; }",
                    "view_tsx": "import React from 'react';\nexport const View: React.FC = () => <div>Interactive Canvas</div>;",
                    "controls_tsx": "import React from 'react';\nexport const Controls: React.FC = () => <div>Controls</div>;",
                    "history_tsx": "import React from 'react';\nexport const History: React.FC = () => <div>History</div>;",
                    "app_tsx": "import React from 'react';\nexport const App: React.FC = () => <div>App Shell</div>;"
                })
            elif stage == "prompt_expansion":
                return "Expanded interactive full-stack specification: Canvas grid with tactile interactions, domain state transitions, reset controls, and event log."

            return "{}"

        import sys
        monkeypatch.setattr(agent_orchestrator, "call_gemini", fake_call_gemini)
        modules_to_patch = [
            "agent_orchestrator",
            "onboarding.frontend_planning_engine",
            "onboarding.requirement_generator",
            "onboarding.code_verifier",
            "onboarding.test_importer",
            "onboarding.domain_ontology",
            "onboarding.router_engine",
            "onboarding.domain_engine_synthesizer",
            "onboarding.presentation_projection_synthesizer",
            "onboarding.prompt_expander",
            "onboarding.ui_generator",
            "service_layer.tdd_machine",
        ]
        for mod_name in modules_to_patch:
            try:
                mod = sys.modules.get(mod_name) or __import__(mod_name, fromlist=["call_gemini"])
                if hasattr(mod, "call_gemini"):
                    monkeypatch.setattr(mod, "call_gemini", fake_call_gemini)
            except Exception:
                pass

        for mod in list(sys.modules.values()):
            if mod and hasattr(mod, "call_gemini"):
                try:
                    monkeypatch.setattr(mod, "call_gemini", fake_call_gemini)
                except Exception:
                    pass
    except ImportError:
        pass

