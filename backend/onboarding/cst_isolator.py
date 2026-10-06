"""
LibCST Code Isolator — Surgical Aggregate Root AST/CST Slicing & Injection.
Uses Meta LibCST to extract target class definitions with full fidelity
(formatting, comments, docstrings) and safely splice updated classes back
without corrupting surrounding module code.
"""

from pipeline_trace import traced
from typing import Optional
import libcst as cst


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
def splice_class_cst(original_source: str, class_name: str, new_class_code: str) -> str:
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
        return modified_module.code
    except Exception as e:
        print(f"LibCST splicing notice ({class_name}): {e}")
        return original_source


class FragmentError(ValueError):
    """The LLM's module fragment cannot be merged (invalid Python, missing target class, forbidden module-level code)."""


def _is_import_line(stmt: cst.CSTNode) -> bool:
    return isinstance(stmt, cst.SimpleStatementLine) and all(
        isinstance(item, (cst.Import, cst.ImportFrom)) for item in stmt.body
    )


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

    The fragment may contain import statements, helper classes (e.g. domain exceptions) and the target
    class. Missing imports are added after the existing ones, helper classes are inserted before the
    target (or replaced when they already exist), and the target class is merged member by member (members
    the fragment does not mention are kept). Anything else at
    module level is refused, as is unparseable output: this raises FragmentError instead of silently
    returning the original source.
    """
    try:
        frag = cst.parse_module(fragment.strip() + "\n")
    except Exception as e:
        raise FragmentError(f"Your answer is not valid Python: {str(e).splitlines()[0] if str(e) else type(e).__name__}") from e

    imports, classes = [], []
    for stmt in frag.body:
        if _is_import_line(stmt):
            imports.append(stmt)
        elif isinstance(stmt, cst.ClassDef):
            classes.append(stmt)
        elif _is_docstring_line(stmt):
            continue
        else:
            kind = type(stmt).__name__
            raise FragmentError(
                f"Only import statements and class definitions are allowed at module level (found {kind}). "
                "Move helper logic into a class."
            )
    if target_class not in {c.name.value for c in classes}:
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
        return next((i for i, s in enumerate(body) if isinstance(s, cst.ClassDef) and s.name.value == name), None)

    for cls in classes:
        name = cls.name.value
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
