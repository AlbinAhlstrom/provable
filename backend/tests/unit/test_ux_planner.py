"""
Hermetic offline unit tests for UX Planner (Step 5b.1).
Ensures zero hardcoded domain keywords and proper blueprint fallback behavior.
"""

import os
from unittest.mock import patch
from onboarding.ux_planner import plan_ux_blueprint
from onboarding.router_engine import DomainStructureSchema, EntitySpec, AttributeSpec


def test_ux_planner_has_zero_hardcoded_domain_keywords():
    ux_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "onboarding", "ux_planner.py"))
    with open(ux_py, "r", encoding="utf-8") as f:
        code = f.read()

    forbidden = ["babysitter", "childcare", "chess", "minesweeper", "pizza", "flappy", "warehouse"]
    for word in forbidden:
        assert word not in code.lower(), f"Forbidden domain keyword '{word}' hardcoded in ux_planner.py"


def test_ux_planning_prompt_has_zero_hardcoded_domain_keywords():
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "ux_planning.md"))
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    forbidden = ["babysitter", "childcare", "chess", "minesweeper", "pizza", "flappy", "warehouse"]
    for word in forbidden:
        assert word not in prompt_text.lower(), f"Forbidden domain keyword '{word}' hardcoded in ux_planning.md"


def test_ux_planner_fallback_on_error():
    structure = DomainStructureSchema(
        domain_name="TestDomain",
        entities=[
            EntitySpec(
                name="Item",
                is_aggregate_root=True,
                attributes=[AttributeSpec(name="title", type="string", required=True)]
            )
        ]
    )

    with patch("onboarding.ux_planner.call_gemini", side_effect=Exception("API error")):
        blueprint = plan_ux_blueprint(
            pitch="A test application",
            structure=structure,
            master_name="Item",
            master_slug="item"
        )
        assert "Default Landing & Cold-Start Behavior" in blueprint
        assert "Primary Navigation & View Structure" in blueprint


def test_the_ux_planner_is_told_which_content_is_served_as_records():
    """Verify the plan cannot call published content "static" (a plan that did made the page hard-code credentials).

    id: TST-UX-ROLES
    Given: A structure with an entity that is shown to the audience and one the audience creates
    When: The UX blueprint is planned
    Then: The prompt marks each entity's role and says published content is loaded from the API
    """
    from onboarding.router_engine import AudienceRole
    structure = DomainStructureSchema(domain_name="Site", entities=[
        EntitySpec(name="Offering", audience_role=AudienceRole.SHOWN,
                   attributes=[AttributeSpec(name="title", type="string", required=True)]),
        EntitySpec(name="Inquiry", is_aggregate_root=True, audience_role=AudienceRole.CREATED,
                   attributes=[AttributeSpec(name="name", type="string", required=True)]),
    ])
    prompts = []

    def fake(prompt, stage="general", **options):
        prompts.append(prompt)
        return "### 1. Default Landing & Cold-Start Behavior\n" + "plan " * 30

    with patch("onboarding.ux_planner.call_gemini", fake):
        plan_ux_blueprint(pitch="A site", structure=structure, master_name="Inquiry", master_slug="inquiry")
    prompt = prompts[0]
    assert "**Offering** (shown to audience)" in prompt and "**Inquiry** (created by audience)" in prompt
    assert "loaded from the API as records" in prompt
