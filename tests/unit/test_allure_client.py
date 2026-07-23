import pytest
from integrations.allure_client import load_allure_config, get_allure_project_id, get_allure_report_url, get_coverage_summary
from db import store


@pytest.mark.unit
def test_load_allure_config():
    """Test loading allure configuration dictionary."""
    config = load_allure_config()
    assert isinstance(config, dict)
    assert "enabled" in config
    assert "server_url" in config


@pytest.mark.unit
def test_get_allure_project_id_and_url():
    """Test project ID and report URL formatting."""
    project_id = get_allure_project_id()
    assert isinstance(project_id, str)
    assert len(project_id) > 0

    url = get_allure_report_url()
    assert f"/allure-docker-service/projects/{project_id}/reports/latest/index.html" in url


@pytest.mark.unit
def test_get_coverage_summary(isolated_db):
    """Test calculating coverage summary from database records."""
    summary = get_coverage_summary()
    assert summary["total_requirements"] == 0
    assert summary["passing"] == 0
    assert summary["failing"] == 0

    # Add a requirement and test case
    req = {
        "id": "REQ-COV-1",
        "title": "Cov Test",
        "type": "Requirement",
        "status": "in_progress"
    }
    store.create_requirement(req)
    store.replace_test_results_for_requirement("REQ-COV-1", [
        {"id": "TC-1", "name": "test_1", "status": "pass"}
    ])

    summary_after = get_coverage_summary()
    assert summary_after["total_requirements"] == 1
    assert summary_after["passing"] == 1
