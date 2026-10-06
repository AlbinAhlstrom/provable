"""
LibCST Code Isolator — Surgical Aggregate Root AST/CST Slicing & Injection.
Uses Meta LibCST to extract target class definitions with full fidelity
(formatting, comments, docstrings) and safely splice updated classes back
without corrupting surrounding module code.
"""

import ast
import os
import re
from typing import Optional, Dict, List, Set
import libcst as cst


BUILTIN_EXCEPTIONS: Set[str] = {
    "BaseException", "Exception", "ArithmeticError", "BufferError", "LookupError",
    "AssertionError", "AttributeError", "EOFError", "FloatingPointError", "GeneratorExit",
    "ImportError", "IndexError", "KeyError", "KeyboardInterrupt", "MemoryError",
    "NameError", "NotImplementedError", "OSError", "OverflowError", "RecursionError",
    "ReferenceError", "RuntimeError", "StopAsyncIteration", "StopIteration", "SyntaxError",
    "IndentationError", "TabError", "SystemError", "SystemExit", "TypeError", "UnboundLocalError",
    "UnicodeError", "UnicodeEncodeError", "UnicodeDecodeError", "UnicodeTranslateError",
    "ValueError", "ZeroDivisionError", "BlockingIOError", "ChildProcessError",
    "ConnectionError", "BrokenPipeError", "ConnectionAbortedError", "ConnectionRefusedError",
    "ConnectionResetError", "FileExistsError", "FileNotFoundError", "InterruptedError",
    "IsADirectoryError", "NotADirectoryError", "PermissionError", "ProcessLookupError",
    "TimeoutError", "Warning", "UserWarning", "DeprecationWarning", "PendingDeprecationWarning",
    "SyntaxWarning", "RuntimeWarning", "FutureWarning", "ImportWarning", "UnicodeWarning",
    "BytesWarning", "EncodingWarning", "ResourceWarning"
}


def extract_domain_symbols_from_ast(source_code: str) -> Dict[str, List[str]]:
    """
    Extracts referenced custom exception and event names using AST.
    Returns {'exceptions': [...], 'events': [...]}
    """
    exceptions = set()
    events = set()
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                name = node.id
                if (name.endswith("Error") or name.endswith("Exception") or name.endswith("Violation")) and name not in BUILTIN_EXCEPTIONS:
                    exceptions.add(name)
                elif name.endswith("Event") and name != "DomainEvent":
                    events.add(name)
            elif isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    name = node.exc.func.id
                    if name not in BUILTIN_EXCEPTIONS:
                        exceptions.add(name)
                elif isinstance(node.exc, ast.Name):
                    name = node.exc.id
                    if name not in BUILTIN_EXCEPTIONS:
                        exceptions.add(name)
    except Exception:
        pass
    return {
        "exceptions": sorted(list(exceptions)),
        "events": sorted(list(events))
    }


def _add_import_symbol(source_code: str, module_from: str, symbol: str) -> str:
    """
    Safely adds a symbol to 'from <module_from> import ...' in source_code.
    Preserves exact line indentation (including in try/except blocks) and avoids duplicate/malformed syntax.
    """
    pattern = rf"^([ \t]*from\s+{re.escape(module_from)}\s+import\s+)([^\n]+)$"
    match = re.search(pattern, source_code, re.MULTILINE)
    if not match:
        return source_code

    indent_and_prefix = match.group(1)
    after_import = match.group(2).strip()

    existing_symbols = [s.strip() for s in after_import.replace("(", "").replace(")", "").split(",") if s.strip()]
    if symbol not in existing_symbols:
        new_line = f"{indent_and_prefix}{symbol}, {after_import}"
        source_code = source_code[:match.start()] + new_line + source_code[match.end():]

    return source_code


class _ClassExtractor(cst.CSTVisitor):
    def __init__(self, target_class_name: str):
        self.target_class_name = target_class_name
        self.found_node: Optional[cst.ClassDef] = None

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        if node.name.value == self.target_class_name:
            self.found_node = node
            return False
        return True


class _ClassReplacer(cst.CSTTransformer):
    def __init__(self, target_class_name: str, replacement_node: cst.ClassDef):
        self.target_class_name = target_class_name
        self.replacement_node = replacement_node

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.CSTNode:
        if original_node.name.value == self.target_class_name:
            return self.replacement_node
        return updated_node


def extract_class_cst(source_code: str, class_name: str) -> str:
    """
    Extracts the exact CST representation of a target class from source code,
    preserving all docstrings, comments, type annotations, and inner methods.
    """
    try:
        module = cst.parse_module(source_code)
        extractor = _ClassExtractor(class_name)
        module.visit(extractor)
        if extractor.found_node:
            return module.code_for_node(extractor.found_node)
        return ""
    except Exception as e:
        print(f"LibCST extraction notice ({class_name}): {e}")
        return ""


def splice_class_cst(original_source: str, class_name: str, new_class_code: str, domain_dir: Optional[str] = None) -> str:
    """
    Replaces the target class definition in original_source with new_class_code
    using LibCST, preserving all surrounding module comments, imports, functions,
    and formatting.
    """

    try:
        orig_module = cst.parse_module(original_source)
        new_module = cst.parse_module(new_class_code.strip())

        # Extract the replacement class node from new_module
        extractor = _ClassExtractor(class_name)
        new_module.visit(extractor)
        
        replacement_node = extractor.found_node
        if not replacement_node:
            # Check top-level statements
            for stmt in new_module.body:
                if isinstance(stmt, cst.ClassDef) and stmt.name.value == class_name:
                    replacement_node = stmt
                    break

        if not replacement_node:
            return original_source

        replacer = _ClassReplacer(class_name, replacement_node)
        modified_module = orig_module.visit(replacer)
        result_code = modified_module.code

        # Ensure required imports are present if newly introduced in spliced class
        if "field(" in result_code or "default_factory=" in result_code:
            result_code = _add_import_symbol(result_code, "dataclasses", "field")

        typing_symbols = ["Optional", "List", "Dict", "Any", "Union", "Set", "Tuple", "Callable"]
        for typ in typing_symbols:
            if typ in result_code:
                result_code = _add_import_symbol(result_code, "typing", typ)

        if any(dt_sym in result_code for dt_sym in ["datetime", "date", "timezone", "timedelta"]):
            if "from datetime import" not in result_code and "import datetime" not in result_code:
                result_code = "from datetime import datetime, date, timezone, timedelta\n" + result_code
            else:
                for dt_sym in ["datetime", "date", "timezone", "timedelta"]:
                    if dt_sym in result_code:
                        result_code = _add_import_symbol(result_code, "datetime", dt_sym)

        # Standard library auto-imports
        if "math." in result_code and "import math" not in result_code and "from math import" not in result_code:
            result_code = "import math\n" + result_code

        if ("uuid." in result_code or "uuid4(" in result_code or "UUID" in result_code) and "import uuid" not in result_code and "from uuid import" not in result_code:
            result_code = "import uuid\n" + result_code

        if ("Decimal(" in result_code or "Decimal" in result_code) and "from decimal import" not in result_code and "import decimal" not in result_code:
            result_code = "from decimal import Decimal\n" + result_code

        if ("Enum" in result_code or "auto()" in result_code) and "from enum import" not in result_code and "import enum" not in result_code:
            result_code = "from enum import Enum, auto\n" + result_code

        if "copy." in result_code and "import copy" not in result_code and "from copy import" not in result_code:
            result_code = "import copy\n" + result_code

        # Discover all domain exceptions and events referenced in code
        discovered_symbols = extract_domain_symbols_from_ast(result_code)
        domain_exceptions = set(discovered_symbols["exceptions"]) | {
            "MaintenanceRequiredError", "MaintenanceLockoutError", "ReservationConflictError",
            "BusinessRuleViolation", "StaleDataError", "InvariantViolation", "DomainError"
        }
        for exc in sorted(domain_exceptions):
            if exc in result_code and exc not in result_code.split("class ")[0]:
                result_code = _add_import_symbol(result_code, "src.domain.exceptions", exc)
                result_code = _add_import_symbol(result_code, "domain.exceptions", exc)

        domain_events = set(discovered_symbols["events"]) | {
            "MaintenanceRequiredEvent", "MaintenanceLockedEvent", "DomainEvent"
        }
        for evt in sorted(domain_events):
            if evt in result_code and evt not in result_code.split("class ")[0]:
                result_code = _add_import_symbol(result_code, "src.domain.events", evt)
                result_code = _add_import_symbol(result_code, "domain.events", evt)

        # Auto-import companion domain models only if they actually exist in the domain directory
        if domain_dir and os.path.exists(domain_dir):
            for fname in os.listdir(domain_dir):
                if fname.endswith(".py") and not fname.startswith("__") and fname not in ["exceptions.py", "events.py"]:
                    ent_slug = fname[:-3]
                    fpath = os.path.join(domain_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            ent_content = f.read()
                        class_matches = re.findall(r"^class\s+([A-Z][a-zA-Z0-9]+)\b", ent_content, re.MULTILINE)
                        for ent_class in class_matches:
                            if ent_class != class_name and re.search(rf"\b{ent_class}\b", result_code):
                                if f"class {ent_class}" not in result_code and f"import {ent_class}" not in result_code:
                                    import_stmt = f"try:\n    from src.domain.{ent_slug} import {ent_class}\nexcept ImportError:\n    pass\n"
                                    result_code = import_stmt + result_code
                    except Exception:
                        pass

        # Add from __future__ import annotations at the top to eliminate annotation NameErrors
        if "from __future__ import annotations" not in result_code:
            result_code = "from __future__ import annotations\n" + result_code

        return sanitize_dataclass_field_ordering(result_code)

    except Exception as e:
        print(f"LibCST splicing notice ({class_name}): {e}")
        return original_source



def sanitize_dataclass_field_ordering(source_code: str) -> str:
    """
    Ensures all dataclass fields without default values precede all fields with default values.
    Preserves all methods, properties, docstrings, and comments in their original relative positions.
    """
    try:
        module = cst.parse_module(source_code)

        class DataclassReorderer(cst.CSTTransformer):
            def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
                is_dataclass = False
                for dec in updated_node.decorators:
                    if isinstance(dec.decorator, cst.Name) and dec.decorator.value == "dataclass":
                        is_dataclass = True
                        break
                    elif isinstance(dec.decorator, cst.Call) and isinstance(dec.decorator.func, cst.Name) and dec.decorator.func.value == "dataclass":
                        is_dataclass = True
                        break

                if not is_dataclass:
                    return updated_node

                non_default_fields = []
                default_fields = []
                other_body = []

                for stmt in updated_node.body.body:
                    if isinstance(stmt, cst.SimpleStatementLine) and len(stmt.body) == 1 and isinstance(stmt.body[0], cst.AnnAssign):
                        ann = stmt.body[0]
                        if ann.value is None:
                            non_default_fields.append(stmt)
                        else:
                            default_fields.append(stmt)
                    else:
                        other_body.append(stmt)

                new_body_stmts = []
                if other_body and isinstance(other_body[0], cst.SimpleStatementLine) and len(other_body[0].body) == 1 and isinstance(other_body[0].body[0], cst.Expr) and isinstance(other_body[0].body[0].value, (cst.SimpleString, cst.FormattedString)):
                    new_body_stmts.append(other_body[0])
                    other_body = other_body[1:]

                new_body_stmts.extend(non_default_fields)
                new_body_stmts.extend(default_fields)
                new_body_stmts.extend(other_body)

                return updated_node.with_changes(body=updated_node.body.with_changes(body=new_body_stmts))

        reordered = module.visit(DataclassReorderer())
        return reordered.code
    except Exception as e:
        print(f"Dataclass reordering notice: {e}")
        return source_code

