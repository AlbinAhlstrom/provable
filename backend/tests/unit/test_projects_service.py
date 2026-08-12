"""
Unit tests for Project service workflows using FakeUnitOfWork.
Tests project listing, project switching, project settings, project adding, and resetting all projects.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Project
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_list_projects_service():
    """
    Given a FakeUnitOfWork with initial projects
    When calling list_projects
    Then a list of project dicts with name, path, and active status is returned.
    """
    p1 = Project(name="Project A", path="/path/to/a", active=True)
    p2 = Project(name="Project B", path="/path/to/b", active=False)
    uow = FakeUnitOfWork(initial_projects=[p1, p2])

    result = services.list_projects(uow=uow)

    assert len(result) == 2
    assert result[0] == {"name": "Project A", "path": "/path/to/a", "active": True}
    assert result[1] == {"name": "Project B", "path": "/path/to/b", "active": False}


def test_get_active_project_settings_service():
    """
    Given a FakeUnitOfWork with an active project
    When calling get_active_project_settings
    Then settings dict is returned containing the workspace_path.
    """
    p = Project(name="Active Project", path="/path/to/active", active=True)
    uow = FakeUnitOfWork(initial_projects=[p])

    settings = services.get_active_project_settings(uow=uow)

    assert isinstance(settings, dict)
    assert settings.get("workspace_path") == "/path/to/active"


def test_switch_project_service(tmp_path):
    """
    Given a valid existing directory path and a FakeUnitOfWork
    When calling switch_project
    Then the project is marked as active in uow and success is returned.
    """
    proj_dir = str(tmp_path / "my_project")
    os.makedirs(proj_dir, exist_ok=True)
    p1 = Project(name="Project A", path="/path/to/a", active=True)
    p2 = Project(name="my_project", path=proj_dir, active=False)
    uow = FakeUnitOfWork(initial_projects=[p1, p2])

    result = services.switch_project(path=proj_dir, uow=uow)

    assert result["success"] is True
    assert result["project"]["path"] == os.path.abspath(proj_dir)
    active_projs = [p for p in uow.projects.list() if p.active]
    assert len(active_projs) == 1
    assert active_projs[0].path == os.path.abspath(proj_dir)
    assert uow.committed is True


def test_switch_project_invalid_path_service():
    """
    Given a non-existent directory path
    When calling switch_project
    Then success is False and an error message is returned.
    """
    uow = FakeUnitOfWork()
    result = services.switch_project(path="/nonexistent/path/xyz", uow=uow)

    assert result["success"] is False
    assert "Path does not exist" in result["error"]


def test_add_project_service(tmp_path):
    """
    Given a valid project directory path and a FakeUnitOfWork
    When calling add_project
    Then the new project is registered in uow.projects and success response is returned.
    """
    proj_dir = str(tmp_path / "new_project")
    os.makedirs(proj_dir, exist_ok=True)
    uow = FakeUnitOfWork()

    result = services.add_project(path=proj_dir, run_synthesis=False, uow=uow)

    assert result["success"] is True
    assert "Onboarding started" in result["message"]
    projs = uow.projects.list()
    assert any(p.path == os.path.abspath(proj_dir) for p in projs)
    assert uow.committed is True


def test_reset_all_projects_service(monkeypatch, tmp_path):
    """
    Given a FakeUnitOfWork and mocked reset operations
    When calling reset_all_projects
    Then UoW commits and success response is returned.
    """
    ws_dir = str(tmp_path / "workspace")
    os.makedirs(ws_dir, exist_ok=True)
    monkeypatch.setattr("config_loader.get_workspace_base", lambda: ws_dir)
    monkeypatch.setattr("db.store.reset_database", lambda: None)

    uow = FakeUnitOfWork()
    result = services.reset_all_projects(uow=uow)

    assert result["success"] is True
    assert "cleared" in result["message"]
    assert uow.committed is True


def test_workspace_switch_and_reset_database():
    """
    Test switch_database and reset_database methods on FakeWorkspaceAdapter.
    """
    from adapters.workspace import FakeWorkspaceAdapter
    ws = FakeWorkspaceAdapter()
    ws.switch_database("/path/to/test.db")
    assert "/path/to/test.db" in ws.switched_db_paths

    ws.reset_database()
    assert ws.database_reset is True


def test_switch_project_uses_workspace_adapter(tmp_path):
    """
    Given FakeWorkspaceAdapter and FakeUnitOfWork
    When switch_project is called
    Then workspace.switch_database is invoked with the project DB path.
    """
    from adapters.workspace import FakeWorkspaceAdapter
    proj_dir = str(tmp_path / "proj")
    os.makedirs(proj_dir, exist_ok=True)
    p = Project(name="proj", path=proj_dir, active=False)
    uow = FakeUnitOfWork(initial_projects=[p])
    ws = FakeWorkspaceAdapter()

    res = services.switch_project(path=proj_dir, uow=uow, workspace=ws)
    assert res["success"] is True
    expected_db_path = os.path.join(proj_dir, 'requirements', 'provable.db')
    assert expected_db_path in ws.switched_db_paths


def test_reset_all_projects_uses_workspace_adapter(monkeypatch, tmp_path):
    """
    Given FakeWorkspaceAdapter and FakeUnitOfWork
    When reset_all_projects is called
    Then workspace.reset_database is invoked.
    """
    from adapters.workspace import FakeWorkspaceAdapter
    ws_dir = str(tmp_path / "workspace")
    os.makedirs(ws_dir, exist_ok=True)
    monkeypatch.setattr("config_loader.get_workspace_base", lambda: ws_dir)

    uow = FakeUnitOfWork()
    ws = FakeWorkspaceAdapter()

    res = services.reset_all_projects(uow=uow, workspace=ws)
    assert res["success"] is True
    assert ws.database_reset is True

