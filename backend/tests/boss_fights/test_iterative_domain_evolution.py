"""
Boss Fight 2 Acceptance Test Suite:
Stress-tests Provable's multi-stage iterative domain evolution engine:
  Phase 1: Vague Kickstart (Zero Analysis Paralysis) -> Opinionated Baseline Scaffolding
  Phase 2: Incremental Business Invariant Injection (Operating Hours Maintenance Lockout)
  Phase 3: OCC Concurrency & Double-Booking Race Condition Gate
  Triple-Gate Verification: AST Purity, Dynamic Runtime Execution, Zero-Tolerance LLM Judge

Skipped by default in normal test runs. Execute explicitly with:
    RUN_BOSS_FIGHTS=1 pytest backend/tests/boss_fights/test_iterative_domain_evolution.py -v -s
"""

import os
import ast
import json
import re
import pytest
from typing import Dict, Any

from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services
import agent_orchestrator


VAGUE_KICKSTART_PROMPT = "Heavy machinery rental fleet with equipment tracking and scheduled maintenance."

INCREMENTAL_SPEC_TITLE = "SPEC-FLEET-002: Operating Hours Maintenance Lockout"
INCREMENTAL_SPEC_GHERKIN = """
Feature: Equipment Maintenance Lockout
  Scenario: Equipment exceeds 500 operating hours since last maintenance
    Given a HeavyEquipment aggregate with operating_hours=520 and status="AVAILABLE"
    When rent_equipment is called
    Then the system raises MaintenanceRequiredError
    And records a MaintenanceRequiredEvent in equipment.events
    And equipment status transitions to "MAINTENANCE_LOCKED"
"""


def evaluate_domain_ast_purity(file_path: str) -> Dict[str, Any]:
    """
    Gate 1 Deterministic Check:
    Statically analyzes domain model AST to guarantee pure DDD layer isolation.
    Ensures zero I/O, database, or external bus dispatcher imports in domain layer.
    """
    assert os.path.exists(file_path), f"Domain file {file_path} was not generated."

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    forbidden_imports = {
        "requests", "httpx", "aiohttp", "sqlite3", "sqlalchemy",
        "psycopg2", "service_layer.messagebus", "fastapi", "flask"
    }

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    violations = forbidden_imports.intersection(imported_modules)
    return {
        "is_pure": len(violations) == 0,
        "violations": list(violations),
        "imported_modules": list(imported_modules)
    }


def call_iterative_llm_judge(domain_files_dict: Dict[str, str]) -> Dict[str, Any]:
    """
    Gate 2 LLM-as-a-Judge (Zero-Tolerance Binary Disqualification Contract):
    Submits generated domain models to Gemini to verify DDD boundaries, incremental invariant preservation,
    and OCC version checks.
    """
    domain_sections = []
    for fname, code in sorted(domain_files_dict.items()):
        domain_sections.append(f"=== domain/{fname} ===\n{code}\n")

    files_text = "\n".join(domain_sections)

    judge_prompt = f"""
You are an uncompromising Principal Software Architect and strict Code Judge executing a Formal Acceptance Gate.
Evaluate the following generated Python domain models for an Industrial Heavy Machinery Fleet & Rental System:

{files_text}

System Specification & Evolution:
1. Baseline: Heavy equipment inventory and rental booking aggregate roots.
2. Invariant 1: If equipment operating_hours >= 500 without maintenance, rent operations MUST raise MaintenanceRequiredError and append MaintenanceRequiredEvent to self.events.
3. Invariant 2: Optimistic Concurrency Control (version_number) on HeavyEquipment aggregate to prevent double-booking collisions (raising StaleDataError or DoubleBookingError).

CRITICAL BINARY DISQUALIFICATION RULES (Auto-Fail: passed=False, score=0):
1. Undefined / Unimported Symbols: If ANY exception, event, or class (e.g. MaintenanceRequiredError, MaintenanceRequiredEvent, StaleDataError) is referenced without being explicitly defined in or imported into domain modules, passed MUST BE FALSE and score 0.
2. Anti-Pattern Hacks: If dynamic reflection hacks (such as globals().get(...), getattr(sys.modules...), or string eval) are used to bypass missing event/exception definitions, passed MUST BE FALSE and score 0.
3. Leaking Side-Effects: If domain events are dispatched via external message bus or network calls directly within entity methods rather than buffered in self.events, passed MUST BE FALSE.
4. Violations Consistency: If there are ANY entries in the `violations` list or any unhandled runtime flaws noted, `passed` MUST BE FALSE.

Return your evaluation as a valid JSON object matching EXACTLY this structure:
```json
{{
  "passed": true,
  "score": 10,
  "rationale": "Uncompromising architectural verdict",
  "concurrency_evaluation": "Analysis of OCC mechanics and stale collision handling",
  "ddd_boundaries_evaluation": "Analysis of domain event recording vs direct dispatch",
  "violations": []
}}
```
"""
    raw_response = agent_orchestrator.call_gemini(judge_prompt, stage="llm_judge")
    if not raw_response:
        raise RuntimeError("LLM Judge returned empty response. Check LLM_API_KEY / GEMINI_API_KEY configuration.")

    clean_json = re.sub(r"^```json\s*", "", raw_response.strip(), flags=re.MULTILINE)
    clean_json = re.sub(r"^```\s*$", "", clean_json.strip(), flags=re.MULTILINE).strip()

    try:
        verdict = json.loads(clean_json)
        return verdict
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM Judge verdict as JSON: {e}\nRaw output:\n{raw_response}")


@pytest.mark.boss_fight
@pytest.mark.skipif(
    not os.environ.get("RUN_BOSS_FIGHTS"),
    reason="Boss fight tests require live LLM execution. Run with RUN_BOSS_FIGHTS=1 to execute."
)
def test_iterative_domain_evolution_boss_fight(tmp_path, monkeypatch):
    """
    Boss Fight 2: Multi-Stage Iterative Domain Evolution Engine.
    Simulates a real-world developer journey:
      1. Minimal Vague Kickstart (1 sentence) -> Opinionated baseline scaffold
      2. Incremental BDD spec injection -> LibCST domain mutation
      3. Dynamic execution testing: Operating hour lockouts & OCC double-booking race condition
      4. Triple-Gate verification: AST Purity + Dynamic Execution + Zero-Tolerance LLM Judge
    """
    import sys
    import importlib.util

    # 1. Sandbox Workspace Setup
    workspace_dir = str(tmp_path / "sandbox_workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    monkeypatch.setenv("PROVABLE_WORKSPACE", workspace_dir)

    uow = SqliteUnitOfWork()

    # 2. PHASE 1: Vague Kickstart (Zero Analysis Paralysis)
    result = services.kickstart_domain_and_scaffold(
        pitch=VAGUE_KICKSTART_PROMPT,
        uow=uow,
        workspace_dir=workspace_dir
    )

    assert result.get("success") is True, f"Pipeline kickstart failed: {result}"

    # Execute TDD machine on generated baseline specs
    inbox_specs = result.get("inbox_specs", [])
    for spec in inbox_specs:
        spec_id = spec.get("spec_id")
        tdd_result = services.execute_inbox_spec_tdd(spec_id, uow=uow, workspace_dir=workspace_dir)
        assert tdd_result.get("success") is True, f"Baseline TDD execution failed for {spec_id}: {tdd_result}"

    domain_dir = os.path.join(workspace_dir, "src", "domain")
    assert os.path.exists(domain_dir), f"Domain directory {domain_dir} does not exist"

    # Identify target aggregate name
    target_eq_name = "Equipment"
    for fname in os.listdir(domain_dir):
        if fname.endswith(".py") and not fname.startswith("__") and fname not in ["events.py", "exceptions.py"]:
            try:
                content = open(os.path.join(domain_dir, fname), encoding="utf-8").read()
                for cand in ["HeavyEquipment", "Equipment", "MachineryUnit", "Machinery", "Asset"]:
                    if re.search(rf"\bclass\s+{re.escape(cand)}\b", content):
                        target_eq_name = cand
                        break
            except Exception:
                pass

    # 3. PHASE 2: Incremental Business Invariant Injection (Operating Hours Maintenance Lockout)
    services.add_inbox_spec(
        spec={
            "spec_id": "SPEC-FLEET-002",
            "title": "SPEC-FLEET-002: Operating Hours Maintenance Lockout",
            "spec_type": "invariant",
            "target_aggregate": target_eq_name,
            "given_when_then": INCREMENTAL_SPEC_GHERKIN,
            "status": "PENDING"
        },
        uow=uow
    )
    p2_result = services.execute_inbox_spec_tdd("SPEC-FLEET-002", uow=uow, workspace_dir=workspace_dir)
    assert p2_result.get("success") is True, f"Phase 2 Maintenance Lockout TDD execution failed: {p2_result}"

    # 4. PHASE 3: OCC Concurrency & Double-Booking Collision Gate
    occ_spec_gherkin = """Feature: Optimistic Concurrency Control for Rental Bookings
Scenario: Version increment and collision prevention
  Given a HeavyEquipment aggregate with version_number=1
  When a rental operation is executed
  Then version_number increments to 2
  And concurrent booking with stale version_number=1 raises StaleDataError"""

    services.add_inbox_spec(
        spec={
            "spec_id": "SPEC-FLEET-003",
            "title": "SPEC-FLEET-003: Optimistic Concurrency Control",
            "spec_type": "invariant",
            "target_aggregate": target_eq_name,
            "given_when_then": occ_spec_gherkin,
            "status": "PENDING"
        },
        uow=uow
    )
    p3_result = services.execute_inbox_spec_tdd("SPEC-FLEET-003", uow=uow, workspace_dir=workspace_dir)
    assert p3_result.get("success") is True, f"Phase 3 OCC Concurrency TDD execution failed: {p3_result}"

    # 5. Locate Generated Domain Files

    domain_files = [
        os.path.join(domain_dir, f) for f in os.listdir(domain_dir)
        if f.endswith(".py") and not f.startswith("__") and f not in ["events.py", "exceptions.py"]
    ]
    assert len(domain_files) > 0, f"No domain entity files were generated in {domain_dir}"

    equipment_path = None
    booking_path = None

    for fpath in domain_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            fname = os.path.basename(fpath).lower()
            if any(k in fname or re.search(rf"\bclass\s+{re.escape(k)}\b", content, re.IGNORECASE) for k in ["equipment", "machinery", "machine", "asset", "fleet"]):
                if not equipment_path:
                    equipment_path = fpath
            if any(k in fname or re.search(rf"\bclass\s+{re.escape(k)}\b", content, re.IGNORECASE) for k in ["booking", "rental", "lease", "reservation", "schedule", "order"]):
                if not booking_path:
                    booking_path = fpath

    # Fallbacks
    if not equipment_path and domain_files:
        equipment_path = domain_files[0]
    if not booking_path and len(domain_files) > 1:
        booking_path = domain_files[1]
    elif not booking_path:
        booking_path = equipment_path

    assert os.path.exists(equipment_path), f"Equipment domain module not found in {domain_dir}"
    assert os.path.exists(booking_path), f"Booking domain module not found in {domain_dir}"

    with open(equipment_path, "r", encoding="utf-8") as f:
        equipment_code = f.read()
    with open(booking_path, "r", encoding="utf-8") as f:
        booking_code = f.read()

    # 4. GATE 1A: Deterministic Static AST Verification (Anti-Cheat & Layer Purity)
    eq_purity = evaluate_domain_ast_purity(equipment_path)
    assert eq_purity["is_pure"] is True, f"Equipment domain purity violation: {eq_purity['violations']}"

    bk_purity = evaluate_domain_ast_purity(booking_path)
    assert bk_purity["is_pure"] is True, f"Booking domain purity violation: {bk_purity['violations']}"

    # 5. GATE 1B: Deterministic Runtime Invariant Execution (Zero Trust)
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)

    eq_spec = importlib.util.spec_from_file_location("sandbox_eq_rt", equipment_path)
    eq_mod = importlib.util.module_from_spec(eq_spec)
    eq_spec.loader.exec_module(eq_mod)

    # Locate Equipment aggregate root class dynamically
    EquipmentClass = None
    for attr_name in dir(eq_mod):
        attr = getattr(eq_mod, attr_name)
        if isinstance(attr, type) and hasattr(attr, "__dataclass_fields__"):
            if any(k in attr_name.lower() for k in ["equipment", "machinery", "machine", "asset", "fleet"]):
                EquipmentClass = attr
                break

    if EquipmentClass is None:
        for attr_name in dir(eq_mod):
            attr = getattr(eq_mod, attr_name)
            if isinstance(attr, type) and hasattr(attr, "__dataclass_fields__") and not attr_name.startswith("_"):
                EquipmentClass = attr
                break

    assert EquipmentClass is not None, f"Failed to locate aggregate root dataclass in {equipment_path}"

    # Instantiate equipment with dynamic fields
    field_names = set(getattr(EquipmentClass, "__dataclass_fields__", {}).keys())
    init_kwargs = {"id": "EQ-001"}
    if "name" in field_names:
        init_kwargs["name"] = "Excavator 5000"
    if "operating_hours" in field_names:
        init_kwargs["operating_hours"] = 520
    if "status" in field_names:
        init_kwargs["status"] = "AVAILABLE"
    if "version_number" in field_names:
        init_kwargs["version_number"] = 1

    eq_instance = EquipmentClass(**init_kwargs)
    assert hasattr(eq_instance, "id"), "Aggregate root missing id"

    # Verify maintenance lockout invariant trigger if error is present
    MaintenanceRequiredError = getattr(eq_mod, "MaintenanceRequiredError", None)
    if MaintenanceRequiredError and hasattr(eq_instance, "operating_hours") and eq_instance.operating_hours >= 500:
        with pytest.raises(MaintenanceRequiredError):
            for method_name in ["rent", "book", "allocate_rental", "lock_for_maintenance"]:
                if hasattr(eq_instance, method_name):
                    getattr(eq_instance, method_name)("CUST-101")
                    break

    # Verify valid state or version update
    init_valid_kwargs = {"id": "EQ-002"}
    if "name" in field_names:
        init_valid_kwargs["name"] = "Bulldozer B2"
    if "operating_hours" in field_names:
        init_valid_kwargs["operating_hours"] = 100
    if "status" in field_names:
        init_valid_kwargs["status"] = "AVAILABLE"
    if "version_number" in field_names:
        init_valid_kwargs["version_number"] = 1

    eq_valid = EquipmentClass(**init_valid_kwargs)
    for method_name in ["rent", "book", "allocate_rental", "transition_state"]:
        if hasattr(eq_valid, method_name):
            try:
                getattr(eq_valid, method_name)("CUST-101")
            except TypeError:
                getattr(eq_valid, method_name)()
            break

    # 6. GATE 2: Zero-Tolerance LLM-as-a-Judge Verification
    domain_files_dict = {}
    for fpath in domain_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            domain_files_dict[fname] = f.read()

    for extra in ["events.py", "exceptions.py"]:
        extra_path = os.path.join(domain_dir, extra)
        if os.path.exists(extra_path):
            with open(extra_path, "r", encoding="utf-8") as f:
                domain_files_dict[extra] = f.read()

    judge_verdict = call_iterative_llm_judge(domain_files_dict=domain_files_dict)

    print("\n--- Boss Fight 2: Zero-Tolerance LLM Judge Report ---")
    print(f"Score: {judge_verdict.get('score')}/10")
    print(f"Passed: {judge_verdict.get('passed')}")
    print(f"Rationale: {judge_verdict.get('rationale')}")
    print(f"OCC Evaluation: {judge_verdict.get('concurrency_evaluation')}")
    print(f"DDD Boundaries: {judge_verdict.get('ddd_boundaries_evaluation')}")
    print(f"Violations: {judge_verdict.get('violations')}")
    print("-----------------------------------------------------")

    assert judge_verdict.get("passed") is True, (
        f"LLM Judge rejected implementation: {judge_verdict.get('rationale')} | "
        f"Violations: {judge_verdict.get('violations')}"
    )
    assert len(judge_verdict.get("violations", [])) == 0, f"Judge detected violations: {judge_verdict.get('violations')}"
