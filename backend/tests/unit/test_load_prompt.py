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
