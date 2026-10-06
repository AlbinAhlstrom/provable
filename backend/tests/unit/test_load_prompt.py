"""Unit tests for agent_orchestrator.load_prompt: it must fail loudly instead of returning an empty prompt."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import agent_orchestrator


def test_load_prompt_substitutes_placeholders():
    """Verify placeholders are replaced and the BOM is not leaked.

    id: TST-LP-001
    Given: The router_decomposition.md template
    When: It is loaded with a business pitch
    Then: The pitch appears in the prompt, the placeholder is gone, and no BOM is present
    """
    prompt = agent_orchestrator.load_prompt("router_decomposition.md", {"business_pitch": "A pizza shop"})
    assert "A pizza shop" in prompt
    assert "{business_pitch}" not in prompt
    assert not prompt.startswith("﻿")


def test_load_prompt_missing_file_raises():
    """Verify a missing template raises instead of silently returning an empty prompt.

    id: TST-LP-002
    Given: A template name that does not exist
    When: load_prompt is called
    Then: FileNotFoundError is raised
    """
    with pytest.raises(FileNotFoundError):
        agent_orchestrator.load_prompt("does_not_exist.md")


def test_load_prompt_unknown_placeholder_raises():
    """Verify a placeholder missing from the template is reported (typo guard).

    id: TST-LP-003
    Given: The router_decomposition.md template
    When: It is loaded with a placeholder the template does not contain
    Then: KeyError is raised
    """
    with pytest.raises(KeyError):
        agent_orchestrator.load_prompt("router_decomposition.md", {"not_a_placeholder": "x"})


def test_load_prompt_is_single_pass():
    """Verify substituted values are not re-scanned for placeholders.

    id: TST-LP-004
    Given: A pitch that itself contains the text of another placeholder
    When: self_healing.md is loaded with that text in the pitch
    Then: The literal text survives instead of being replaced by the other value
    """
    prompt = agent_orchestrator.load_prompt(
        "self_healing.md",
        {"error_message": "E", "business_pitch": "uses {broken_code} literally", "broken_code": "CODE"},
    )
    assert "uses {broken_code} literally" in prompt


@pytest.mark.parametrize("template,placeholders", [
    ("component_planning.md", ["pitch", "noun", "category_id", "layout_name", "invariants_json"]),
    ("aesthetic_planning.md", ["pitch", "category_id", "archetype"]),
    ("app_assembly.md", ["pitch", "category_id", "layout_name", "brand_title", "archetype",
                         "css_variables", "seed_data_json", "components_json"]),
    ("pitch_component_analysis.md", ["business_pitch"]),
    ("domain_ontology.md", ["business_pitch"]),
    ("dynamic_requirements.md", ["schema_json"]),
    ("self_healing.md", ["error_message", "business_pitch", "broken_code"]),
    ("router_decomposition.md", ["business_pitch"]),
    ("green_class_repair.md", ["extracted_class_code", "spec_title", "spec_given_when_then",
                               "target_aggregate", "spec_type", "test_source", "failure_output", "target_class_name"]),
    ("red_test_generation.md", ["spec_title", "spec_description", "spec_given_when_then", "module_name",
                                "target_class_name", "class_api", "feedback_block"]),
])
def test_every_prompt_template_accepts_its_placeholders(template, placeholders):
    """Verify each prompt file contains exactly the placeholders its caller supplies.

    id: TST-LP-005
    Given: A prompt template and the placeholder names its caller passes
    When: The template is loaded with sentinel values
    Then: Every sentinel appears in the output and no placeholder is left unfilled
    """
    prompt = agent_orchestrator.load_prompt(template, {p: f"<<{p}>>" for p in placeholders})
    for p in placeholders:
        assert f"<<{p}>>" in prompt
        assert f"{{{p}}}" not in prompt
