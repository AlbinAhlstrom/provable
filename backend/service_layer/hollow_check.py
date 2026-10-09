"""
Hollow check: does a test that passes at once test behaviour the class already has, or nothing at all?

The RED gate rejects a test that passes before any code is written. That is right for a test that asserts nothing
(it reads a default value), and wrong for a rule an earlier step already implemented: the action stage writes an
aggregate's methods before the rule deck runs, so a rule those methods enforce passes at once.

The two are told apart by running the test once more against the class with its behaviour emptied out (every method
except `to_dict` does nothing, and a starting state the class works out, a `default_factory` that is not a bare
builtin, is an empty container of the field's kind):

- it fails there for a behavioural reason: the test does test behaviour, and that behaviour is in the class. The rule
  is already satisfied and the test is kept as its regression guard.
- it passes there too: it holds without any behaviour. A tautology, as before.

The hollow class never touches the workspace: the Python sources are copied to a temporary folder and the test runs
there, so the running app and the stages writing alongside see nothing of it.
"""

import ast
import os
import shutil
import tempfile
from typing import Any, Callable, Dict

from pipeline_trace import traced

KEPT_METHODS = {"to_dict"}  # serialisation, not behaviour
EMPTY_FACTORIES = {"list", "dict", "set", "tuple", "str", "int", "float", "bool"}  # a start that is already empty
CONTAINERS = {"list": "list", "dict": "dict", "set": "set", "tuple": "tuple"}


def _hollow_starting_state(member: ast.AnnAssign) -> None:
    """A field whose starting value the class computes (`field(default_factory=<its own function>)`) starts empty:
    how a new object starts is behaviour when code produces it, and a literal default when it is written down."""
    call = member.value
    if not (isinstance(call, ast.Call) and getattr(call.func, "id", getattr(call.func, "attr", "")) == "field"):
        return
    for keyword in call.keywords:
        factory = keyword.value
        if keyword.arg == "default_factory" and not (isinstance(factory, ast.Name) and factory.id in EMPTY_FACTORIES):
            kind = ast.unparse(member.annotation).split("[", 1)[0].rsplit(".", 1)[-1].lower()
            nothing = ast.Lambda(args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                                 body=ast.Constant(value=None))
            keyword.value = ast.Name(id=CONTAINERS[kind], ctx=ast.Load()) if kind in CONTAINERS else nothing


def hollow_class_source(source: str, class_name: str) -> str:
    """The module with every method of `class_name` (except `to_dict`) reduced to its docstring and `pass`, and
    every starting state it computes emptied."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name not in KEPT_METHODS:
                    docstring = member.body[:1] if ast.get_docstring(member) is not None else []
                    member.body = docstring + [ast.Pass()]
                elif isinstance(member, ast.AnnAssign):
                    _hollow_starting_state(member)
    return ast.unparse(ast.fix_missing_locations(tree)) + "\n"


def _python_only(folder: str, names: list) -> list:
    return [n for n in names if not (os.path.isdir(os.path.join(folder, n)) or n.endswith(".py")) or n == "__pycache__"]


@traced("tdd.hollow_check")
def fails_without_behaviour(
    test_file_path: str,
    workspace_dir: str,
    domain_file: str,
    class_name: str,
    run: Callable[..., Dict[str, Any]],
    judge: Callable[..., Dict[str, Any]],
) -> bool:
    """True when the test, run against the hollow class, fails the way a valid RED test fails. `run` executes pytest
    (`run_isolated_pytest`) and `judge` is the RED gate (`evaluate_red_gate_result`)."""
    with tempfile.TemporaryDirectory(prefix="hollow_") as copy:
        shutil.copytree(os.path.join(workspace_dir, "src"), os.path.join(copy, "src"), ignore=_python_only)
        conftest = os.path.join(workspace_dir, "tests", "conftest.py")
        os.makedirs(os.path.join(copy, "tests", "unit"))
        if os.path.exists(conftest):
            shutil.copy(conftest, os.path.join(copy, "tests", "conftest.py"))
        copied_test = os.path.join(copy, "tests", "unit", os.path.basename(test_file_path))
        shutil.copy(test_file_path, copied_test)

        copied_domain = os.path.join(copy, os.path.relpath(domain_file, workspace_dir))
        with open(copied_domain, encoding="utf-8") as f:
            source = f.read()
        with open(copied_domain, "w", encoding="utf-8") as f:
            f.write(hollow_class_source(source, class_name))

        result = run(copied_test, cwd=copy)
        return bool(judge(result["exit_code"], result.get("report"), result.get("stderr"))["approved"])
