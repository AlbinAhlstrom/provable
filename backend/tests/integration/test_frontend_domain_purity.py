"""
Future E2E Purity Check: To mathematically prove the UI is a dumb projection, the test suite should feed the frontend a mock OpenAPI schema with complete gibberish (e.g., Aggregate: FlorgBorg, Attribute: Zorp). The test then asserts that the DOM renders 'FlorgBorg'. If the UI renders 'Pallet' when fed 'FlorgBorg', the test fails.
"""
import ast
import os
import pytest
from typing import Set

# Universal permanent banned list for legacy e-commerce / deprecated terms
PERMANENT_BANNED_WORDS = ["pizza", "cart", "checkout", "appcraft"]

# Universal generic programming, CSS, and generic DTO status identifiers to exclude
GENERIC_IGNORE_WORDS = {
    "id", "name", "type", "status", "title", "description", "created_at", "updated_at",
    "priority", "events", "tests", "item", "items", "value", "attributes", "fields",
    "data", "props", "class", "dict", "list", "str", "int", "float", "bool", "boolean",
    "optional", "none", "self", "to_dict", "root", "base", "model", "schema", "result",
    "error", "message", "key", "icon", "routes", "params", "string", "number", "spec",
    "specs", "payload", "entity", "aggregate", "domain", "project", "workspace", "success",
    "text", "docstring", "invariants", "methods", "command", "query", "event", "response",
    "request", "handler", "service", "repository", "uow", "unit_of_work", "view", "page",
    "dto", "object", "any", "all", "true", "false", "default", "table", "index", "code",
    "size", "in_progress", "pending", "done", "review", "backlog", "conflict", "ready",
    "received", "completed", "cancelled", "step", "attempt", "active", "path"
}

def extract_domain_terms_from_backend() -> Set[str]:
    """
    Dynamically extracts domain entities, aggregate root names, and domain-specific attributes
    from active backend services and generated domain models via static AST inspection.
    """
    domain_terms: Set[str] = set()

    from config_loader import get_workspace_base
    workspace_root = str(get_workspace_base())  # the isolated test workspace, never the live one

    # 1. Scan generated/active business domain files (<workspace>/src/domain and <workspace>/domain)
    domain_dirs = [
        os.path.join(workspace_root, "src", "domain"),
        os.path.join(workspace_root, "domain"),
    ]

    for d in domain_dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    stem = os.path.splitext(file)[0].lower()
                    if stem not in GENERIC_IGNORE_WORDS and len(stem) > 2:
                        domain_terms.add(stem)

                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            tree = ast.parse(f.read(), filename=file_path)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    cls_name = node.name.lower()
                                    if cls_name not in GENERIC_IGNORE_WORDS and len(cls_name) > 2:
                                        domain_terms.add(cls_name)
                                    for item in node.body:
                                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                            attr_name = item.target.id.lower()
                                            if attr_name not in GENERIC_IGNORE_WORDS and len(attr_name) > 2:
                                                domain_terms.add(attr_name)
                                        elif isinstance(item, ast.Assign):
                                            for target in item.targets:
                                                if isinstance(target, ast.Name):
                                                    attr_name = target.id.lower()
                                                    if attr_name not in GENERIC_IGNORE_WORDS and len(attr_name) > 2:
                                                        domain_terms.add(attr_name)
                    except Exception:
                        pass

    # 2. Inspect active domain aggregates and schemas from backend service layer / kickstart state
    try:
        from adapters.repository import SqliteUnitOfWork
        from service_layer import services
        agg_data = services.get_active_domain_aggregates(uow=SqliteUnitOfWork())
        if agg_data and "aggregates" in agg_data:
            for agg in agg_data["aggregates"]:
                name = agg.get("name", "").lower()
                key = agg.get("key", "").lower()
                if name and name not in GENERIC_IGNORE_WORDS and len(name) > 2:
                    domain_terms.add(name)
                if key and key not in GENERIC_IGNORE_WORDS and len(key) > 2:
                    domain_terms.add(key)
                for attr in agg.get("attributes", []) + agg.get("fields", []):
                    attr_name = attr.get("name", "").lower() if isinstance(attr, dict) else getattr(attr, "name", "").lower()
                    if attr_name and attr_name not in GENERIC_IGNORE_WORDS and len(attr_name) > 2:
                        domain_terms.add(attr_name)
    except Exception:
        pass

    # 3. If workspace is freshly reset, dynamically decompose standard domain pitch
    if not domain_terms:
        try:
            from onboarding.router_engine import decompose_pitch_into_structure_and_inbox
            decomp = decompose_pitch_into_structure_and_inbox("An industrial warehouse management system tracking Pallets, storage Zones, and forklift Operators.")
            for ent in decomp.structure.entities:
                if ent.name.lower() not in GENERIC_IGNORE_WORDS:
                    domain_terms.add(ent.name.lower())
                for attr in ent.attributes:
                    if attr.name.lower() not in GENERIC_IGNORE_WORDS and len(attr.name) > 2:
                        domain_terms.add(attr.name.lower())
        except Exception:
            pass

    return domain_terms


def test_dynamic_frontend_domain_purity():
    """
    Ensures that dynamically extracted domain terms from the backend and permanent banned legacy terms
    do not exist anywhere in frontend/src/ source code.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    frontend_src_dir = os.path.join(repo_root, "frontend", "src")
    assert os.path.isdir(frontend_src_dir), f"Frontend source directory not found at: {frontend_src_dir}"

    dynamic_terms = extract_domain_terms_from_backend()
    assert len(dynamic_terms) > 0, "Expected dynamic extraction to discover active backend domain terms."

    all_banned_terms = dynamic_terms.union(set(PERMANENT_BANNED_WORDS))
    active_banned_terms = {t for t in all_banned_terms if len(t) > 2}

    violations = []
    for root, _, files in os.walk(frontend_src_dir):
        for file in files:
            if file.endswith(".ts") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, frontend_src_dir)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    for term in active_banned_terms:
                        if term in content:
                            violations.append(f"File '{rel_path}' contains forbidden domain/legacy term: '{term}'")

    if violations:
        nl = "\n"
        raise AssertionError(
            f"DYNAMIC FRONTEND PURITY VIOLATION:\n"
            f"The frontend must remain a 100% domain-agnostic projection of backend schemas.\n"
            f"Active scanned domain terms: {sorted(list(active_banned_terms))}\n"
            f"Found {len(violations)} violation(s):\n"
            f"{nl.join(violations)}"
        )
