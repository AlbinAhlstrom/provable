"""
LibCST Code Isolator — Surgical Aggregate Root AST/CST Slicing & Injection.
Uses Meta LibCST to extract target class definitions with full fidelity
(formatting, comments, docstrings) and safely splice updated classes back
without corrupting surrounding module code.
"""

from pipeline_trace import traced
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


@traced("tdd.cst_extract")
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


@traced("tdd.cst_splice")
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


class FragmentError(ValueError):
    """The LLM's module fragment cannot be merged (invalid Python, missing target class, forbidden module-level code)."""


def _is_import_line(stmt: cst.CSTNode) -> bool:
    return isinstance(stmt, cst.SimpleStatementLine) and all(
        isinstance(item, (cst.Import, cst.ImportFrom)) for item in stmt.body
    )


def _module_name_of(stmt: cst.CSTNode) -> Optional[str]:
    """The one name a module-level statement defines: a class, a function, or a constant assigned to a single name.
    None for anything else."""
    if isinstance(stmt, (cst.ClassDef, cst.FunctionDef)):
        return stmt.name.value
    if isinstance(stmt, cst.SimpleStatementLine) and len(stmt.body) == 1:
        inner = stmt.body[0]
        if isinstance(inner, cst.AnnAssign) and isinstance(inner.target, cst.Name):
            return inner.target.value
        if isinstance(inner, cst.Assign) and len(inner.targets) == 1 and isinstance(inner.targets[0].target, cst.Name):
            return inner.targets[0].target.value
    return None


def _is_docstring_line(stmt: cst.CSTNode) -> bool:
    return (
        isinstance(stmt, cst.SimpleStatementLine)
        and len(stmt.body) == 1
        and isinstance(stmt.body[0], cst.Expr)
        and isinstance(stmt.body[0].value, (cst.SimpleString, cst.ConcatenatedString))
    )


def module_import_lines(source_code: str) -> str:
    """The module's top-level import statements, as text (what the generator may already rely on)."""
    try:
        module = cst.parse_module(source_code)
    except Exception:
        return ""
    return "\n".join(module.code_for_node(s).strip() for s in module.body if _is_import_line(s))


def module_helpers_source(source: str, target_class: str) -> str:
    """The module's helpers beside the target class (classes, functions, constants), as source: what a code writer
    shown only the class would otherwise not know exists, and write a second time under another name."""
    module = cst.parse_module(source)
    return "\n\n".join(module.code_for_node(s).strip() for s in module.body
                       if _module_name_of(s) not in (None, target_class))


def _member_key(stmt: cst.CSTNode) -> Optional[tuple]:
    """Identity of a class-body member: ("fn", name), ("field", name) or ("assign", name); None for docstrings/pass/etc."""
    if isinstance(stmt, cst.FunctionDef):
        return ("fn", stmt.name.value)
    if isinstance(stmt, cst.SimpleStatementLine) and len(stmt.body) == 1:
        inner = stmt.body[0]
        if isinstance(inner, cst.AnnAssign) and isinstance(inner.target, cst.Name):
            return ("field", inner.target.value)
        if isinstance(inner, cst.Assign) and len(inner.targets) == 1 and isinstance(inner.targets[0].target, cst.Name):
            return ("assign", inner.targets[0].target.value)
    return None


def _merge_class_members(original: cst.ClassDef, fragment: cst.ClassDef) -> cst.ClassDef:
    """Member-wise merge: fragment members replace same-named members or are added; everything else is kept.

    Fields without a default are kept before fields with defaults so the dataclass stays valid. The original
    class keeps its decorators, bases and docstring; docstring/pass statements in the fragment are ignored.
    """
    body = list(original.body.body)
    doc = [body.pop(0)] if body and _is_docstring_line(body[0]) else []
    fields = {}
    rest = []
    for stmt in body:
        key = _member_key(stmt)
        if key and key[0] == "field":
            fields[key[1]] = stmt
        elif isinstance(stmt, cst.SimpleStatementLine) and all(isinstance(i, cst.Pass) for i in stmt.body):
            continue
        else:
            rest.append(stmt)

    for stmt in fragment.body.body:
        key = _member_key(stmt)
        if key is None:
            continue
        if key[0] == "field":
            fields[key[1]] = stmt
            continue
        idx = next((i for i, existing in enumerate(rest) if _member_key(existing) == key), None)
        if idx is not None:
            rest[idx] = stmt
        else:
            rest.append(stmt)

    def has_default(field_stmt: cst.SimpleStatementLine) -> bool:
        return field_stmt.body[0].value is not None

    ordered = [f for f in fields.values() if not has_default(f)] + [f for f in fields.values() if has_default(f)]
    new_body = doc + ordered + rest
    if not new_body:
        new_body = [cst.SimpleStatementLine(body=[cst.Pass()])]
    return original.with_changes(body=original.body.with_changes(body=new_body))


@traced("tdd.cst_merge")
def merge_module_fragment(original_source: str, target_class: str, fragment: str) -> str:
    """Merges an LLM-produced module fragment into a module.

    The fragment may contain import statements, helpers (classes such as domain exceptions, functions, and
    constants assigned to one name) and the target class. Missing imports are added after the existing ones,
    helpers are inserted before the target (or replaced when one of that name already exists), and the target
    class is merged member by member (members the fragment does not mention are kept). Anything else at
    module level (code that runs at import, an assignment to several names) is refused, as is unparseable
    output: this raises FragmentError instead of silently returning the original source.
    """
    try:
        frag = cst.parse_module(fragment.strip() + "\n")
    except Exception as e:
        raise FragmentError(f"Your answer is not valid Python: {str(e).splitlines()[0] if str(e) else type(e).__name__}") from e

    imports, classes = [], []
    for stmt in frag.body:
        if _is_import_line(stmt):
            imports.append(stmt)
        elif _module_name_of(stmt) is not None:
            classes.append(stmt)  # the target class and every named helper beside it
        elif _is_docstring_line(stmt):
            continue
        else:
            kind = type(stmt.body[0] if isinstance(stmt, cst.SimpleStatementLine) else stmt).__name__
            raise FragmentError(
                f"Only imports, classes, functions and constants assigned to one name are allowed at module level "
                f"(found {kind}). Move that logic into a function or a class."
            )
    if target_class not in {_module_name_of(c) for c in classes if isinstance(c, cst.ClassDef)}:
        raise FragmentError(f"Your answer does not define class {target_class}.")

    orig = cst.parse_module(original_source)
    body = list(orig.body)

    present = {orig.code_for_node(s).strip() for s in body if _is_import_line(s)}
    new_imports = [s for s in imports if frag.code_for_node(s).strip() not in present]
    import_positions = [i for i, s in enumerate(body) if _is_import_line(s)]
    if import_positions:
        pos = import_positions[-1] + 1
    else:
        pos = 1 if body and _is_docstring_line(body[0]) else 0
    body[pos:pos] = new_imports

    def index_of(name: str) -> Optional[int]:
        return next((i for i, s in enumerate(body) if _module_name_of(s) == name), None)

    for cls in classes:
        name = _module_name_of(cls)
        idx = index_of(name)
        if idx is not None and name == target_class:
            body[idx] = _merge_class_members(body[idx], cls)
        elif idx is not None:
            body[idx] = cls
        elif name == target_class:
            body.append(cls)
        else:
            target_idx = index_of(target_class)
            body.insert(target_idx if target_idx is not None else len(body), cls)
    return orig.with_changes(body=body).code

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

