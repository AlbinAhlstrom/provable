import pytest
from db import store
from integrations import allure_client


@pytest.mark.integration
def test_allure_coverage_integration(isolated_db):
    """Integration test verifying database test updates update Allure coverage calculations."""
    initial = allure_client.get_coverage_summary()
    assert initial["passing"] == 0

    req = {
        "id": "REQ-ALLURE-01",
        "title": "Allure Integration Req",
        "type": "Requirement",
        "status": "in_progress"
    }
    store.create_requirement(req)

    store.replace_test_results_for_requirement("REQ-ALLURE-01", [
        {"id": "TC-ALLURE-1", "name": "test_feature", "status": "pass"}
    ])

    updated = allure_client.get_coverage_summary()
    assert updated["total_requirements"] == 1
    assert updated["passing"] == 1
    assert updated["failing"] == 0
