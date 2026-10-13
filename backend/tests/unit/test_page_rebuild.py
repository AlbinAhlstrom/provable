"""Unit tests for rebuilding only the page of a generated app (backend/onboarding/page_rebuild.py, page_gates.py)."""

import os

import pytest

from adapters.repository import SqliteKickstartRepository
from domain.model import KickstartState
from onboarding.page_gates import PageGates, run_page_gates
from onboarding.page_rebuild import PageBrief, PageBriefError, rebuild_page
from onboarding.router_engine import BusinessSpec, DomainStructureSchema

STRUCTURE = {"domain_name": "Booking", "entities": [
    {"name": "Appointment", "is_aggregate_root": True, "audience_role": "created_by_audience",
     "attributes": [{"name": "id", "type": "str"}]}]}
SPEC = {"spec_id": "SPEC-001", "title": "No double booking", "description": "d", "given_when_then": "Given a When b Then c",
        "target_aggregate": "Appointment"}
PLAN = "### 1. Plan\n### 6. Visual Direction\nwarm cream, one amber accent"


def _state(**overrides):
    fields = dict(business_pitch="A booking page", synthesized=True, structure=STRUCTURE, inbox_specs=[SPEC],
                  intent={}, action_manifest={"actions": [{"name": "book"}]})
    fields.update(overrides)
    return KickstartState(**fields)


def _workspace(tmp_path):
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    (domain / "appointment.py").write_text("class Appointment:\n    pass\n", encoding="utf-8")
    return str(tmp_path)


def test_the_decomposition_is_kept_with_the_build_state():
    """Verify a later page rebuild can read what the page was first written from.

    id: TST-PAGE-001
    Given: A kickstart state holding the decomposed structure
    When: It is saved and read back
    Then: The structure is the same, with its audience roles
    """
    repository = SqliteKickstartRepository()
    repository.save(_state())
    assert repository.get().structure == STRUCTURE


def test_a_brief_is_typed_from_the_build_state():
    """
    id: TST-PAGE-002
    Given: The state of a finished kickstart
    When: The page brief is read from it
    Then: It holds the structure and specs as their own types, and the stored action manifest
    """
    brief = PageBrief.from_state(_state())
    assert isinstance(brief.structure, DomainStructureSchema) and brief.structure.master_entity().name == "Appointment"
    assert isinstance(brief.inbox_specs[0], BusinessSpec) and brief.pitch == "A booking page"
    assert brief.action_manifest == {"actions": [{"name": "book"}]}


@pytest.mark.parametrize("overrides, reason", [
    ({"structure": {}}, "no decomposition"),
    ({"action_manifest": {}}, "no action protocol"),
])
def test_a_build_that_cannot_be_rebuilt_says_why(overrides, reason):
    """
    id: TST-PAGE-003
    Given: A state without what the page is written from (no kickstart yet, or one from before this was kept)
    When: The page brief is read
    Then: It fails with the reason, and nothing is generated
    """
    with pytest.raises(PageBriefError, match=reason):
        PageBrief.from_state(_state(**overrides))


def test_a_rebuild_writes_the_page_again_and_nothing_else(tmp_path):
    """Verify a page-only run costs a page: it plans, writes and checks the page against the domain as it stands.

    id: TST-PAGE-004
    Given: A brief and a workspace whose domain is already written
    When: The page is rebuilt
    Then: The UX plan and the page writer run with the brief, the gates get what they wrote, and the result carries
          the gates' verdict
    """
    calls = []

    def ux(**kw):
        calls.append(("ux", kw["pitch"], kw["master_name"]))
        return PLAN

    def presentation(**kw):
        calls.append(("presentation", kw["ux_blueprint"], kw["action_manifest"]))
        return {"success": True, "files": ["src/App.tsx"]}

    def gates(**kw):
        calls.append(("gates", kw["presentation"]["files"], kw["ux_blueprint"]))
        return PageGates(qa={"passed": True, "verdict": "passed"}, timings={"6_qa_audit": 1.0})

    result = rebuild_page(PageBrief.from_state(_state()), _workspace(tmp_path), ux=ux, presentation=presentation, gates=gates)

    assert calls == [("ux", "A booking page", "Appointment"), ("presentation", PLAN, {"actions": [{"name": "book"}]}),
                     ("gates", ["src/App.tsx"], PLAN)]
    assert result["success"] and result["stage_failures"] == [] and result["qa"]["verdict"] == "passed"


def test_a_page_that_was_not_written_is_a_failure_of_the_rebuild(tmp_path):
    """
    id: TST-PAGE-005
    Given: A page writer that delivers nothing
    When: The page is rebuilt
    Then: The presentation stage is listed as failed with its reason
    """
    result = rebuild_page(PageBrief.from_state(_state()), _workspace(tmp_path), ux=lambda **kw: PLAN,
                          presentation=lambda **kw: {"success": False, "error": "the model answered nothing"},
                          gates=lambda **kw: PageGates())
    assert result["stage_failures"] == [{"stage": "presentation", "error": "the model answered nothing"}]


def test_a_rebuild_needs_the_domain_the_page_is_written_against(tmp_path):
    """
    id: TST-PAGE-006
    Given: A workspace with no domain code (it was reset since the kickstart)
    When: The page is rebuilt
    Then: It fails before any model is asked
    """
    with pytest.raises(PageBriefError, match="no domain code"):
        rebuild_page(PageBrief.from_state(_state()), str(tmp_path), ux=lambda **kw: pytest.fail("the UX plan ran"),
                     presentation=lambda **kw: {}, gates=lambda **kw: PageGates())


def _gates(tmp_path, qa, review=None):
    seen = {}

    def gate(audit, rework):
        return qa

    def look(**kw):
        seen.update(kw)
        return review or {"verdict": "fine", "problems": [], "edits": [], "not_repaired": [], "claims": [],
                          "attempts": 1, "error": None}

    outcome = run_page_gates(workspace_dir=str(tmp_path), pitch="p", presentation={"files": ["src/App.tsx"]},
                             ux_blueprint=PLAN, gate=gate, review=look)
    return outcome, seen


def test_a_page_that_passed_qa_is_looked_at_once(tmp_path):
    """
    id: TST-PAGE-007
    Given: A page that passed QA after a rework
    When: The gates run
    Then: The visual review is given the page's files and what QA had repaired, and nothing is reported as failed
    """
    outcome, seen = _gates(tmp_path, {"passed": True, "verdict": "passed_after_rework", "attempts": 1, "defects": [],
                                      "reworked": ["[Contrast] white on cream"]})
    assert seen["component_files"] == ["src/App.tsx"] and seen["settled"] == ["[Contrast] white on cream"]
    assert outcome.failures == [] and outcome.qa["passed"]


def test_a_page_that_failed_qa_is_not_reviewed(tmp_path):
    """
    id: TST-PAGE-008
    Given: A page with defects left after the rework
    When: The gates run
    Then: The visual review does not run, and the verdict says the defects remain
    """
    outcome, seen = _gates(tmp_path, {"passed": False, "verdict": "defects_remain", "attempts": 1, "defects": ["x"]})
    assert seen == {} and outcome.qa["verdict"] == "defects_remain"


def test_a_remark_the_review_could_not_repair_is_a_note_not_a_failed_build(tmp_path):
    """Verify a matter of looks on a page that passed QA does not mark the build as one with problems.

    id: TST-PAGE-009
    Given: A visual review that saw a problem and could not repair it, on a page that passed QA
    When: The gates run
    Then: Nothing is reported as failed, and the remark is kept with the review for whoever reads the run
    """
    outcome, _ = _gates(tmp_path, {"passed": True, "verdict": "passed", "attempts": 0, "defects": []},
                        review={"verdict": "unrepaired", "problems": ["labels overlap"], "edits": [],
                                "not_repaired": ["labels overlap: no such class"], "claims": [], "attempts": 1, "error": None})
    assert outcome.failures == []
    assert outcome.remarks == ["labels overlap: no such class"]


def test_a_review_that_could_not_look_fails_the_build(tmp_path):
    """Verify a review that never happened is not read as a page that looks fine.

    id: TST-PAGE-010
    Given: A visual review that ended in a provider error
    When: The gates run
    Then: The visual review is listed as failed with the reason
    """
    outcome, _ = _gates(tmp_path, {"passed": True, "verdict": "passed", "attempts": 0, "defects": []},
                        review={"verdict": "error", "problems": [], "edits": [], "not_repaired": [], "claims": [],
                                "attempts": 1, "error": "quota exceeded"})
    assert outcome.failures == [{"stage": "visual_review", "error": "quota exceeded"}]



def test_a_rebuild_writes_the_page_from_the_plan_the_product_was_built_from(tmp_path, monkeypatch):
    """Verify a rebuilt page has the parts the product's plan names, the ones its tests look for, and that no
    model is asked for another plan.

    id: TST-PAGE-PLAN
    Given: A build state that kept the contract the product was built from, and a planner that must not be asked
    When: The brief is read and the page is rebuilt
    Then: The brief carries the contract's page plan, and the page writer and the gates are handed exactly it
    """
    from onboarding import product_contract, ux_planner

    class Kept:
        def blueprint(self):
            return PLAN

    def never(**_):
        raise AssertionError("a product built from a contract has its page plan: none is written again")

    monkeypatch.setattr(product_contract, "stored_contract", lambda state: Kept() if state.contract else None)
    monkeypatch.setattr(ux_planner, "plan_ux_blueprint", never)
    handed = []

    def presentation(**kw):
        handed.append(kw["ux_blueprint"])
        return {"success": True, "files": ["src/App.tsx"]}

    def gates(**kw):
        handed.append(kw["ux_blueprint"])
        return PageGates(qa={"passed": True, "verdict": "passed"})

    brief = PageBrief.from_state(_state(contract={"product": {}}))
    result = rebuild_page(brief, _workspace(tmp_path), presentation=presentation, gates=gates)

    assert brief.plan == PLAN and PageBrief.from_state(_state()).plan == ""
    assert handed == [PLAN, PLAN] and result["success"]
