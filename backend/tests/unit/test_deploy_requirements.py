"""The engine runs pytest itself (the TDD loop, service_layer/tdd_machine.py), so the deployed engine must install
pytest and every plugin whose options run_isolated_pytest passes. A missing one makes each run a usage error."""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _requirement_names(path: str) -> set:
    with open(path, encoding="utf-8") as f:
        lines = [ln.split("#", 1)[0].strip() for ln in f]
    return {re.split(r"[<>=\[ ;]", ln, 1)[0].lower() for ln in lines if ln and not ln.startswith("-")}


def test_engine_runtime_requirements_include_the_pytest_plugins_the_tdd_loop_uses():
    names = _requirement_names(os.path.join(ROOT, "backend", "requirements.txt"))
    assert {"pytest", "pytest-timeout", "pytest-json-report"} <= names


def test_docker_image_installs_the_engine_runtime_requirements():
    with open(os.path.join(ROOT, "Dockerfile"), encoding="utf-8") as f:
        assert "-r backend/requirements.txt" in f.read()
