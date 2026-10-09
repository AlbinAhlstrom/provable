"""
Page contract: what the page was written against, compared with what the classes hold once their actions exist.

The page reads the records the API serves, which are the fields of the domain classes. Everything else it needs of an
action (its name and parameters, the values a field takes, what a new object holds) is fixed by the action protocol
before any method is written. So the page is written while the methods are (`synthesis_stages.py`), from the classes
as the skeleton left them.

Writing the methods can still change what a class holds: a field the decomposition did not foresee. The fields are
therefore read before and after, and only a class that gained or lost one sends the page back to be written again,
once, for the classes as they are.

Pure inspection: nothing here writes or calls a model.
"""

import ast
import os
from dataclasses import dataclass, field
from typing import Dict, List

SHARED_MODULES = ("__init__.py", "events.py", "exceptions.py")  # written by the skeleton for every app; no records


@dataclass
class FieldChange:
    """One class whose fields differ from the ones the page was written for."""
    class_name: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    def describe(self) -> str:
        parts = ([f"now also holds {', '.join(self.added)}"] if self.added else []) + \
                ([f"no longer holds {', '.join(self.removed)}"] if self.removed else [])
        return f"{self.class_name} {' and '.join(parts)}"


def domain_fields(workspace_dir: str) -> Dict[str, List[str]]:
    """The public fields of every class in `src/domain`, by class name, in the order they are declared. A module
    that cannot be read as Python lists nothing: its classes then show up as changed."""
    folder = os.path.join(workspace_dir, "src", "domain")
    found: Dict[str, List[str]] = {}
    if not os.path.isdir(folder):
        return found
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".py") or name in SHARED_MODULES:
            continue
        with open(os.path.join(folder, name), "r", encoding="utf-8") as f:
            source = f.read()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            names = [item.target.id for item in node.body
                     if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
                     and not item.target.id.startswith("_")]
            if names:
                found[node.name] = names
    return found


def field_changes(before: Dict[str, List[str]], after: Dict[str, List[str]]) -> List[FieldChange]:
    """The classes that hold something else in `after` than in `before`; the order of a class's fields is not a
    change."""
    changes = []
    for class_name in list(after) + [name for name in before if name not in after]:
        was, now = before.get(class_name, []), after.get(class_name, [])
        added, removed = [n for n in now if n not in was], [n for n in was if n not in now]
        if added or removed:
            changes.append(FieldChange(class_name=class_name, added=added, removed=removed))
    return changes
