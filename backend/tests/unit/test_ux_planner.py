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


def test_the_plan_decides_a_visual_direction_and_it_can_be_read_back():
    """Verify the look of the page is decided before it is written (it used to be discovered by a second full rewrite).

    id: TST-UX-DIRECTION
    Given: The UX planning prompt, and a blueprint with and without a visual direction section
    When: The prompt is read and the direction is extracted
    Then: The prompt asks for the section, and the extraction returns its text or nothing
    """
    from onboarding.ux_planner import visual_direction
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "ux_planning.md"))
    with open(prompt_path, "r", encoding="utf-8") as f:
        assert "### 6. Visual Direction" in f.read()
    assert visual_direction("### 5. Placement\nx\n### 6. Visual Direction\nwarm cream, one amber accent\n") == "warm cream, one amber accent"
    assert visual_direction("### 5. Placement\nx") == "" and visual_direction(None) == ""


def test_a_plan_made_before_the_action_protocol_is_given_the_products_rules():
    """Verify the planner still knows what the product does when it runs alongside the protocol design.

    id: TST-UX-RULES
    Given: A structure and a spec, and no action manifest
    When: The UX blueprint is planned
    Then: The prompt contains the spec's rule
    """
    from onboarding.router_engine import BusinessSpec
    structure = DomainStructureSchema(domain_name="Site", entities=[
        EntitySpec(name="Inquiry", is_aggregate_root=True, attributes=[AttributeSpec(name="name", type="string", required=True)])])
    spec = BusinessSpec(spec_id="S1", title="Future date", description="d",
                        given_when_then="Given a past date When submitted Then it is rejected", target_aggregate="Inquiry")
    prompts = []
    with patch("onboarding.ux_planner.call_gemini", lambda prompt, stage="general", **o: prompts.append(prompt) or ("plan " * 30)):
        plan_ux_blueprint(pitch="A site", structure=structure, master_name="Inquiry", inbox_specs=[spec])
    assert "Given a past date When submitted Then it is rejected" in prompts[0]


def test_the_plan_names_the_attribute_that_carries_a_fact_about_the_business():
    """Verify the plan writes wording, not facts: it is made before the records exist, and a plan that wrote
    "verified badges (CPR/First Aid)" put that claim on the page as fixed text.

    id: TST-UX-FACTS
    Given: The UX planning prompt
    When: It is read
    Then: It says a fact about the business is referred to by the attribute that carries it, as `Entity.attribute`
    """
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "ux_planning.md"))
    body = open(prompt_path, encoding="utf-8").read()
    assert "`Entity.attribute`" in body
    assert "you have not seen them" in body
    assert "badge" in body  # the first screen's badges and highlights are fields of records too
