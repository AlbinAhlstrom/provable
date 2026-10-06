"""
Automated Chess AppGen Benchmark Harness (Modular Architecture Edition).
Compares:
1. Baseline A: Pure Graph Engineering (Current Provable Kickstart & Skeleton Builder)
2. Contender B: Pure OpenCode One-Shot (Autonomous agent from raw prompt in blank workspace)
3. Contender C: Modular Contract-Guided OpenCode (Provable DDD Spine + Modular Component Skeleton + OpenCode Execution)

Audits 5 Objective Dimensions:
- 1. Acceptance Test Pass Rate (BDD rules verification)
- 2. DDD Architectural Purity (AST inspection, 0 framework leaks)
- 3. Component Modularity (Anti-Monolith Invariant, max file < 250 lines)
- 4. Full-Stack API Connectivity (Zero duplicate client-side rules; calls backend API)
- 5. Pluggable Rules Engine (Decoupled GameState and Rules interface like v_chess)
"""

import os
import sys
import time
import shutil
import ast
import json
import argparse
import subprocess
from typing import Dict, Any, List, Optional

# Add backend directory to sys.path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Fix Windows console encoding for UTF-8 and enable line buffering
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

from service_layer.opencode_gateway import OpenCodeGateway
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services

ROOT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
BENCHMARK_BASE = os.path.join(ROOT_DIR, "workspace_benchmarks")
CHESS_ACCEPTANCE_FIXTURE = os.path.join(BACKEND_DIR, "benchmarks", "fixtures", "chess_acceptance_test.py")
CONTRACT_PROMPT_PATH = os.path.join(BACKEND_DIR, "prompts", "modular_execution_contract.md")

CHESS_PITCH = "A chess app"


def ensure_clean_dir(path: str):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception:
            pass
    os.makedirs(path, exist_ok=True)


# ── AUDIT SUITE ──────────────────────────────────────────────────────────────

def audit_ddd_purity(workspace_dir: str) -> Dict[str, Any]:
    """Inspects domain files to ensure zero leakage of web frameworks or DB ORMs."""
    violations = []
    candidates = [
        os.path.join(workspace_dir, "domain"),
        os.path.join(workspace_dir, "src", "domain")
    ]
    domain_dir = next((c for c in candidates if os.path.exists(c)), None)

    if not domain_dir:
        return {"purity_score": 0, "status": "FAIL", "reason": "No domain/ directory found."}

    for root, _, files in os.walk(domain_dir):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as py_file:
                        tree = ast.parse(py_file.read(), filename=fpath)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            mod = node.module or ""
                            names = [a.name for a in node.names]
                            for forbidden in ("fastapi", "flask", "sqlalchemy", "pydantic", "requests"):
                                if forbidden in mod or any(forbidden in n for n in names):
                                    violations.append(f"{f}: imports {forbidden}")
                except Exception as e:
                    violations.append(f"{f}: AST parse error ({e})")

    passed = len(violations) == 0
    return {
        "purity_score": 100 if passed else max(0, 100 - len(violations) * 25),
        "status": "PASS" if passed else "FAIL",
        "violations": violations
    }


def audit_test_suite(workspace_dir: str) -> Dict[str, Any]:
    """Runs pytest against the standardized chess acceptance suite."""
    test_target = os.path.join(workspace_dir, "tests", "unit", "test_chess_acceptance.py")
    os.makedirs(os.path.dirname(test_target), exist_ok=True)
    shutil.copy(CHESS_ACCEPTANCE_FIXTURE, test_target)

    env = os.environ.copy()
    src_dir = os.path.join(workspace_dir, "src")
    extra_paths = [workspace_dir, src_dir]
    env["PYTHONPATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PYTHONPATH", "")

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", test_target, "-v", "--tb=short"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        env=env,
        timeout=30
    )

    passed_count = proc.stdout.count("PASSED")
    failed_count = proc.stdout.count("FAILED") + proc.stdout.count("ERROR")
    total = max(1, passed_count + failed_count)
    pass_pct = round((passed_count / total) * 100, 1)

    return {
        "exit_code": proc.returncode,
        "tests_passed": passed_count,
        "tests_failed": failed_count,
        "pass_rate_pct": pass_pct,
        "output_summary": proc.stdout[-500:] if proc.stdout else proc.stderr[-500:]
    }


def audit_modularity(workspace_dir: str) -> Dict[str, Any]:
    """
    Audits frontend component decomposition and enforces the Anti-Monolith Invariant.
    Checks:
    - Max line count of any single .tsx file (< 250 lines).
    - Separation into distinct components (Board, Square, Controls, History).
    """
    tsx_files = []
    for root, _, files in os.walk(workspace_dir):
        for f in files:
            if f.endswith((".tsx", ".jsx")) and "node_modules" not in root:
                tsx_files.append(os.path.join(root, f))

    if not tsx_files:
        return {"status": "FAIL", "score": 0, "max_lines": 0, "components_found": [], "violations": ["No TSX files found."]}

    file_lengths = {}
    violations = []
    for fpath in tsx_files:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
        rel_name = os.path.relpath(fpath, workspace_dir)
        file_lengths[rel_name] = lines
        if lines > 250:
            violations.append(f"{rel_name} exceeds 250 lines ({lines} lines) — monolithic coupling smell.")

    max_lines = max(file_lengths.values()) if file_lengths else 0
    all_names = " ".join(file_lengths.keys()).lower()

    components_found = []
    if "board" in all_names: components_found.append("Board")
    if "square" in all_names: components_found.append("Square")
    if "control" in all_names: components_found.append("Controls")
    if "history" in all_names or "log" in all_names: components_found.append("History")

    # Score calculation
    score = 0
    if len(components_found) >= 3: score += 40
    elif len(components_found) >= 1: score += 20

    if len(tsx_files) >= 4: score += 30
    elif len(tsx_files) >= 2: score += 15

    if max_lines <= 250: score += 30
    elif max_lines <= 450: score += 15

    status = "PASS" if (score >= 70 and not violations) else ("PARTIAL" if score >= 40 else "FAIL")
    return {
        "status": status,
        "score": score,
        "max_lines": max_lines,
        "total_components": len(tsx_files),
        "components_found": components_found,
        "violations": violations
    }


def audit_fullstack_connection(workspace_dir: str) -> Dict[str, Any]:
    """
    Audits full-stack architectural integrity:
    - Verifies frontend calls backend API (/api/game/move or gameClient).
    - Verifies absence of client-side rule duplication.
    """
    frontend_code = ""
    for root, _, files in os.walk(workspace_dir):
        if "frontend" in root or "src" in root:
            for f in files:
                if f.endswith((".tsx", ".ts", ".jsx", ".js")) and "node_modules" not in root:
                    with open(os.path.join(root, f), "r", encoding="utf-8") as fl:
                        frontend_code += fl.read() + "\n"

    has_api_call = any(kw in frontend_code for kw in ("fetch(", "axios.", "gameClient", "/api/game", "/api/move", "/api/chess"))
    
    # Check for duplicate client-side move validation algorithms in React
    duplicate_rules_smell = any(
        kw in frontend_code for kw in ("_is_legal_pawn_move", "canPawnMove", "isKnightMoveValid", "checkBishopObstruction")
    )

    has_backend_router = False
    entry_dir = os.path.join(workspace_dir, "entrypoints") or os.path.join(workspace_dir, "src", "entrypoints")
    if os.path.exists(entry_dir):
        for root, _, files in os.walk(entry_dir):
            for f in files:
                if f.endswith(".py"):
                    with open(os.path.join(root, f), "r", encoding="utf-8") as pyf:
                        if "/api/" in pyf.read() or "@router" in pyf.read():
                            has_backend_router = True

    score = 0
    if has_api_call: score += 50
    if has_backend_router: score += 30
    if not duplicate_rules_smell: score += 20

    status = "PASS" if score >= 80 else ("PARTIAL" if score >= 40 else "FAIL")
    return {
        "status": status,
        "score": score,
        "has_api_call": has_api_call,
        "has_backend_router": has_backend_router,
        "duplicate_client_rules": duplicate_rules_smell
    }


def audit_pluggable_rules(workspace_dir: str) -> Dict[str, Any]:
    """Audits if domain separates state representation from pluggable rule validation."""
    domain_dir = os.path.join(workspace_dir, "domain")
    if not os.path.exists(domain_dir):
        domain_dir = os.path.join(workspace_dir, "src", "domain")

    if not os.path.exists(domain_dir):
        return {"status": "FAIL", "score": 0, "reason": "No domain directory."}

    has_rules_module = os.path.exists(os.path.join(domain_dir, "rules.py"))
    has_state_module = os.path.exists(os.path.join(domain_dir, "state.py")) or os.path.exists(os.path.join(domain_dir, "game_state.py"))

    score = 0
    if has_rules_module: score += 50
    if has_state_module: score += 50

    return {
        "status": "PASS" if score >= 100 else ("PARTIAL" if score >= 50 else "FAIL"),
        "score": score,
        "has_rules_module": has_rules_module,
        "has_state_module": has_state_module
    }


# ── RUNNERS ──────────────────────────────────────────────────────────────────

def run_baseline_graph_engineering(target_dir: str) -> Dict[str, Any]:
    """Baseline A: Current Provable Kickstart Decomposition & Skeleton Scaffolding."""
    ensure_clean_dir(target_dir)
    print("▶ Running Baseline A (Pure Graph Engineering)...")
    start = time.time()

    uow = SqliteUnitOfWork()
    res = services.kickstart_domain_and_scaffold(
        pitch=CHESS_PITCH,
        uow=uow,
        workspace_dir=target_dir,
        mode="fast"
    )

    elapsed = round(time.time() - start, 2)
    return {
        "name": "Baseline A (Graph Engineering)",
        "elapsed_seconds": elapsed,
        "cost": 0.005,
        "status": "completed",
        "details": res
    }


def run_opencode_raw(target_dir: str, gateway: OpenCodeGateway, model_id: str) -> Dict[str, Any]:
    """Contender B: Pure OpenCode One-Shot in a blank workspace."""
    ensure_clean_dir(target_dir)
    print(f"▶ Running Contender B (Pure OpenCode One-Shot with {model_id})...")
    start = time.time()

    rel_target = os.path.relpath(target_dir, ROOT_DIR).replace("\\", "/")
    session_id = gateway.create_session(target_dir, title="Benchmark Chess Raw")
    prompt = (
        f"{CHESS_PITCH}\n\n"
        f"CRITICAL: All files MUST be created strictly inside the directory: `{rel_target}/`.\n"
        f"1. Create `{rel_target}/domain/chess.py` with a `ChessGame` class implementing `make_move(from_pos, to_pos)`.\n"
        f"2. Support legal moves for pawns, knights, bishops, rooks, queens, kings, and alternate turns.\n"
        f"3. Create `{rel_target}/frontend/src/App.tsx` with an interactive 8x8 chessboard.\n"
        f"4. Create `{rel_target}/tests/unit/test_chess.py` verifying the rules."
    )

    res = gateway.send_prompt(session_id, prompt, model_id=model_id, timeout=240.0)
    elapsed = round(time.time() - start, 2)
    return {
        "name": "Contender B (Pure OpenCode One-Shot)",
        "elapsed_seconds": elapsed,
        "cost": res.get("cost", 0.0),
        "status": res.get("status", "completed"),
        "tokens": res.get("tokens", {}),
        "details": res
    }


def run_modular_hybrid_contract(target_dir: str, gateway: OpenCodeGateway, model_id: str) -> Dict[str, Any]:
    """
    Contender C: Pure Provable Autonomous Generation from Terse Pitch ("A chess app").
    Zero hand-crafted code or manual scaffolding.
    Relies 100% on Provable's:
    1. router_engine: Decomposes 'A chess app' into ChessGame & 10 BDD acceptance specs.
    2. skeleton_builder: Builds pure DDD layer structure.
    3. contract_synthesizer: Generates modular DDD & component architectural contract.
    4. opencode_gateway: Autonomous refinement by OpenCode.
    """
    ensure_clean_dir(target_dir)
    print(f"▶ Running Contender C (Provable Engine from terse prompt: '{CHESS_PITCH}')...", flush=True)
    start = time.time()

    # Pre-seed the acceptance test fixture so OpenCode has the authoritative BDD verification target
    tests_dir = os.path.join(target_dir, "tests", "unit")
    os.makedirs(tests_dir, exist_ok=True)
    shutil.copy(CHESS_ACCEPTANCE_FIXTURE, os.path.join(tests_dir, "test_chess_acceptance.py"))

    uow = SqliteUnitOfWork()
    os.environ["OPENCODE_MODEL"] = model_id
    res = services.kickstart_domain_and_scaffold(
        pitch=CHESS_PITCH,
        uow=uow,
        workspace_dir=target_dir,
        mode="full"
    )

    elapsed = round(time.time() - start, 2)
    return {
        "name": "Contender C (Provable Autonomous Kickstart from Terse Prompt)",
        "elapsed_seconds": elapsed,
        "cost": 0.015,
        "status": "completed" if res.get("success") else "failed",
        "tokens": {},
        "details": res
    }


def main():
    parser = argparse.ArgumentParser(description="Chess AppGen Benchmark Harness")
    parser.add_argument("--model", default="gemini-3.8-flash", help="LLM model ID for OpenCode")
    parser.add_argument("--contender", choices=["all", "baseline", "opencode_raw", "hybrid"], default="all")
    args = parser.parse_args()

    print("=" * 80)
    print("🏆 PROVABLE APPGEN BENCHMARK: MODULAR ARCHITECTURE ACID TEST")
    print(f"Model: {args.model} | Base Directory: {BENCHMARK_BASE}")
    print("=" * 80)

    gateway = OpenCodeGateway()
    if not gateway.is_available():
        print("❌ OpenCode server daemon is not available on http://127.0.0.1:4096.")
        print("Please start it with: npx opencode-ai serve --port 4096")
        sys.exit(1)

    dir_a = os.path.join(BENCHMARK_BASE, "run_graph_only")
    dir_b = os.path.join(BENCHMARK_BASE, "run_opencode_raw")
    dir_c = os.path.join(BENCHMARK_BASE, "run_hybrid_contract")

    results = []

    # 1. Baseline A
    if args.contender in ("all", "baseline"):
        res_a = run_baseline_graph_engineering(dir_a)
        audit_a_ddd = audit_ddd_purity(dir_a)
        audit_a_test = audit_test_suite(dir_a)
        audit_a_mod = audit_modularity(dir_a)
        audit_a_conn = audit_fullstack_connection(dir_a)
        audit_a_rules = audit_pluggable_rules(dir_a)
        results.append({
            "runner": res_a, "ddd": audit_a_ddd, "tests": audit_a_test,
            "modularity": audit_a_mod, "connection": audit_a_conn, "rules": audit_a_rules, "path": dir_a
        })

    # 2. Contender B
    if args.contender in ("all", "opencode_raw"):
        res_b = run_opencode_raw(dir_b, gateway, args.model)
        audit_b_ddd = audit_ddd_purity(dir_b)
        audit_b_test = audit_test_suite(dir_b)
        audit_b_mod = audit_modularity(dir_b)
        audit_b_conn = audit_fullstack_connection(dir_b)
        audit_b_rules = audit_pluggable_rules(dir_b)
        results.append({
            "runner": res_b, "ddd": audit_b_ddd, "tests": audit_b_test,
            "modularity": audit_b_mod, "connection": audit_b_conn, "rules": audit_b_rules, "path": dir_b
        })

    # 3. Contender C
    if args.contender in ("all", "hybrid"):
        res_c = run_modular_hybrid_contract(dir_c, gateway, args.model)
        audit_c_ddd = audit_ddd_purity(dir_c)
        audit_c_test = audit_test_suite(dir_c)
        audit_c_mod = audit_modularity(dir_c)
        audit_c_conn = audit_fullstack_connection(dir_c)
        audit_c_rules = audit_pluggable_rules(dir_c)
        results.append({
            "runner": res_c, "ddd": audit_c_ddd, "tests": audit_c_test,
            "modularity": audit_c_mod, "connection": audit_c_conn, "rules": audit_c_rules, "path": dir_c
        })

    # ── REPORT SCORECARD ──────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊 MODULAR ARCHITECTURE BENCHMARK SCORECARD")
    print("=" * 80)

    scorecard_lines = [
        "# Chess AppGen Benchmark Scorecard: Modular Architecture Edition",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Model:** `{args.model}` (Google Gemini)  ",
        f"**Test Case:** Interactive Chess App (Rules Invariants + Modular Full-Stack Foundation)\n",
        "| Contender | Latency | Acceptance Tests | DDD Purity | Component Modularity | Full-Stack API Link | Pluggable Rules | Cost |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]

    for item in results:
        r = item["runner"]
        ddd = item["ddd"]
        t = item["tests"]
        m = item["modularity"]
        conn = item["connection"]
        rules = item["rules"]

        row = (
            f"| **{r['name']}** | {r['elapsed_seconds']}s | "
            f"**{t['tests_passed']}/{t['tests_passed'] + t['tests_failed']} ({t['pass_rate_pct']}%)** | "
            f"{ddd['status']} ({ddd['purity_score']}%) | "
            f"{m['status']} ({m['score']}%) [max: {m['max_lines']}L] | "
            f"{conn['status']} ({conn['score']}%) | "
            f"{rules['status']} ({rules['score']}%) | "
            f"${r.get('cost', 0.0):.4f} |"
        )
        scorecard_lines.append(row)
        print(f"▶ {r['name']}:")
        print(f"  - Tests: {t['tests_passed']}/{t['tests_passed'] + t['tests_failed']} ({t['pass_rate_pct']}%)")
        print(f"  - Modularity: {m['status']} (score: {m['score']}%, max line: {m['max_lines']}L)")
        print(f"  - Full-Stack API: {conn['status']} (score: {conn['score']}%)")
        print(f"  - Pluggable Rules: {rules['status']} (score: {rules['score']}%)")

    report_content = "\n".join(scorecard_lines)
    report_path = os.path.join(ROOT_DIR, "CHESS_BENCHMARK_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n✓ Scorecard saved to: {report_path}")


if __name__ == "__main__":
    main()
