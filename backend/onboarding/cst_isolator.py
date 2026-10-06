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
