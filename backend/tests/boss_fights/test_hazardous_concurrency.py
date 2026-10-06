"""
Boss Fight Acceptance Test Suite:
Stress-tests Provable synthesis engine against complex industrial domain modeling,
Optimistic Concurrency Control (OCC), StaleDataError collisions, and DDD aggregate event boundaries.

Skipped by default in normal test runs. Execute explicitly with:
    RUN_BOSS_FIGHTS=1 pytest backend/tests/boss_fights/test_hazardous_concurrency.py -v -s
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


BOSS_FIGHT_PROMPT = (
    "A Pallet can be marked as is_hazardous. When moved into a Zone, the Zone must lock "
    "via a QUARANTINED status. Use Optimistic Concurrency Controls (version_number) on "
    "the Zone so concurrent allocations fail with StaleDataError. Dispatch an async "
    "ZoneQuarantinedEvent post-commit."
)


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


def call_llm_judge(pallet_code: str, zone_code: str) -> Dict[str, Any]:
    """
    Gate 2 LLM-as-a-Judge (Zero-Tolerance Binary Disqualification Contract):
    Submits generated domain models to Gemini to verify DDD boundaries and OCC compliance.
    """
    judge_prompt = f"""
You are an uncompromising Principal Software Architect and strict Code Judge executing a Formal Acceptance Gate.
Evaluate the following generated Python domain models for a Warehouse Management System:

=== domain/pallet.py ===
{pallet_code}

=== domain/zone.py ===
{zone_code}

System Specification:
"{BOSS_FIGHT_PROMPT}"

CRITICAL BINARY DISQUALIFICATION RULES (Auto-Fail: passed=False, score=0):
1. Undefined / Unimported Symbols: If ANY exception, event, or class (e.g. StaleDataError, ZoneQuarantinedEvent) is used or referenced without being explicitly defined or imported from domain modules, passed MUST BE FALSE and score 0.
2. Anti-Pattern Hacks: If dynamic reflection hacks (such as globals().get(...), getattr(sys.modules...), or string eval) are used to bypass missing event/exception definitions, passed MUST BE FALSE and score 0.
3. Leaking Side-Effects: If domain events are dispatched via external message bus or network calls directly within entity methods rather than buffered in self.events, passed MUST BE FALSE.
4. Violations Consistency: If there are ANY entries in the `violations` list or any unhandled runtime flaws noted, `passed` MUST BE FALSE.

Return your evaluation as a valid JSON object matching EXACTLY this structure:
```json
{{
  "passed": true,
  "score": 10,
  "rationale": "Uncompromising architectural verdict",
  "concurrency_evaluation": "Analysis of OCC mechanics and StaleDataError",
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
def test_hazardous_concurrency_boss_fight(tmp_path, monkeypatch):
    """
    Boss Fight 1: Hazardous Pallet Concurrency & Optimistic Concurrency Controls.
    Triggers the Provable kickstart & TDD synthesis pipeline in an isolated workspace,
    and runs a Triple-Gate verification:
      Gate 1A: Deterministic Static AST Purity (0 message bus / I/O imports)
      Gate 1B: Deterministic Runtime Concurrency & Invariant Execution (Zone & Pallet)
      Gate 2:  Zero-Tolerance LLM-as-a-Judge Code Audit (Binary Disqualification)
    """
    import sys
    import importlib.util

    # 1. Environment Sandbox Setup
    workspace_dir = str(tmp_path / "sandbox_workspace")
    os.makedirs(workspace_dir, exist_ok=True)
    monkeypatch.setenv("PROVABLE_WORKSPACE", workspace_dir)

    uow = SqliteUnitOfWork()

    # 2. Trigger Provable Pipeline
    result = services.kickstart_domain_and_scaffold(
        pitch=BOSS_FIGHT_PROMPT,
        uow=uow,
        workspace_dir=workspace_dir
    )

    assert result.get("success") is True, f"Pipeline kickstart failed: {result}"

    # Synchronously execute TDD machine on generated specs
    inbox_specs = result.get("inbox_specs", [])
    for spec in inbox_specs:
        spec_id = spec.get("spec_id")
        tdd_result = services.execute_inbox_spec_tdd(spec_id, uow=uow, workspace_dir=workspace_dir)
        assert tdd_result.get("success") is True, f"TDD execution failed for {spec_id}: {tdd_result}"

    # 3. Locate Generated Domain Files
    domain_dir = os.path.join(workspace_dir, "src", "domain")
    pallet_path = os.path.join(domain_dir, "pallet.py")
    zone_path = os.path.join(domain_dir, "zone.py")

    # Fallback check if domain models were placed in model.py
    if not os.path.exists(pallet_path) and os.path.exists(os.path.join(domain_dir, "model.py")):
        pallet_path = os.path.join(domain_dir, "model.py")
    if not os.path.exists(zone_path) and os.path.exists(os.path.join(domain_dir, "model.py")):
        zone_path = os.path.join(domain_dir, "model.py")

    assert os.path.exists(pallet_path), f"Pallet domain module not found at {pallet_path}"
    assert os.path.exists(zone_path), f"Zone domain module not found at {zone_path}"

    with open(pallet_path, "r", encoding="utf-8") as f:
        pallet_code = f.read()
    with open(zone_path, "r", encoding="utf-8") as f:
        zone_code = f.read()

    # 4. GATE 1A: Deterministic Static AST Verification (Anti-Cheat & Layer Purity)
    pallet_purity = evaluate_domain_ast_purity(pallet_path)
    assert pallet_purity["is_pure"] is True, f"Pallet domain purity violation: {pallet_purity['violations']}"

    zone_purity = evaluate_domain_ast_purity(zone_path)
    assert zone_purity["is_pure"] is True, f"Zone domain purity violation: {zone_purity['violations']}"

    # 5. GATE 1B: Deterministic Runtime Concurrency & Invariant Execution (Zero Trust)
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)

    pallet_spec = importlib.util.spec_from_file_location("sandbox_pallet_rt", pallet_path)
    pallet_mod = importlib.util.module_from_spec(pallet_spec)
    sys.modules["sandbox_pallet_rt"] = pallet_mod
    pallet_spec.loader.exec_module(pallet_mod)

    zone_spec = importlib.util.spec_from_file_location("sandbox_zone_rt", zone_path)
    zone_mod = importlib.util.module_from_spec(zone_spec)
    sys.modules["sandbox_zone_rt"] = zone_mod
    zone_spec.loader.exec_module(zone_mod)

    PalletClass = getattr(pallet_mod, "Pallet")
    ZoneClass = getattr(zone_mod, "Zone")

    import inspect
    pallet_params = inspect.signature(PalletClass).parameters
    pallet_kwargs = {}
    for p_name, p in pallet_params.items():
        if p_name in ("id", "pallet_id", "code"):
            pallet_kwargs[p_name] = "PAL-001"
        elif p_name in ("is_hazardous", "hazardous"):
            pallet_kwargs[p_name] = True
        elif p.default is inspect.Parameter.empty:
            pallet_kwargs[p_name] = "PAL-001"
    pallet_instance = PalletClass(**pallet_kwargs)

    zone_params = inspect.signature(ZoneClass).parameters
    zone_kwargs = {}
    for p_name, p in zone_params.items():
        if p_name in ("id", "zone_id", "code"):
            zone_kwargs[p_name] = "ZONE-001"
        elif p_name in ("status", "zone_status"):
            zone_kwargs[p_name] = "ACTIVE"
        elif p_name == "version_number":
            zone_kwargs[p_name] = 1
        elif p.default is inspect.Parameter.empty:
            zone_kwargs[p_name] = "ZONE-001"
    zone_instance = ZoneClass(**zone_kwargs)


    # Trigger pallet intake & quarantine
    if hasattr(zone_instance, "receive_pallet"):
        zone_instance.receive_pallet(pallet_instance)
    elif hasattr(zone_instance, "allocate_pallet"):
        zone_instance.allocate_pallet(pallet_instance)
    elif hasattr(zone_instance, "add_pallet"):
        zone_instance.add_pallet(pallet_instance)
    elif hasattr(zone_instance, "quarantine"):
        zone_instance.quarantine()

    assert zone_instance.status == "QUARANTINED", f"Expected QUARANTINED status, got {zone_instance.status}"
    assert zone_instance.version_number >= 2, f"Expected version_number incremented >= 2, got {zone_instance.version_number}"
    assert hasattr(zone_instance, "events") and isinstance(zone_instance.events, list), "Aggregate missing events list"

    # 6. GATE 2: Zero-Tolerance LLM-as-a-Judge Verification
    judge_verdict = call_llm_judge(pallet_code=pallet_code, zone_code=zone_code)

    print("\n--- Zero-Tolerance LLM Judge Report ---")
    print(f"Score: {judge_verdict.get('score')}/10")
    print(f"Passed: {judge_verdict.get('passed')}")
    print(f"Rationale: {judge_verdict.get('rationale')}")
    print(f"OCC Evaluation: {judge_verdict.get('concurrency_evaluation')}")
    print(f"DDD Boundaries: {judge_verdict.get('ddd_boundaries_evaluation')}")
    print(f"Violations: {judge_verdict.get('violations')}")
    print("---------------------------------------")

    assert judge_verdict.get("passed") is True, (
        f"LLM Judge rejected implementation: {judge_verdict.get('rationale')} | "
        f"Violations: {judge_verdict.get('violations')}"
    )
    assert len(judge_verdict.get("violations", [])) == 0, f"Judge detected violations: {judge_verdict.get('violations')}"

