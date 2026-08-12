"""
Unit tests for Testing service layer workflows using FakeUnitOfWork.
Tests test case execution, coverage calculation, manual test case creation, and allure report generation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement, TestSpec
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services, exceptions


def test_create_test_case_service():
    """
    Given a FakeUnitOfWork containing a requirement REQ-101
    When calling create_test_case for REQ-101
    Then a new TestSpec is created, attached to REQ-101 in UoW, and UoW is committed.
    """
    req = Requirement(id="REQ-101", title="User Login", description="User must be able to log in")
    uow = FakeUnitOfWork(initial_requirements=[req])

    result = services.create_test_case(
        req_id="REQ-101",
        uow=uow,
        name="test_user_login_valid",
        given="Given user on login page",
        when="When entering valid credentials",
        then="Then user is authenticated"
    )

    assert result["success"] is True
    assert result["test_case_id"] == "TC-REQ-101"
    
    saved_req = uow.requirements.get("REQ-101")
    assert saved_req is not None
    assert len(saved_req.tests) == 1
    assert saved_req.tests[0]["id"] == "TC-REQ-101"
    assert saved_req.tests[0]["name"] == "test_user_login_valid"
    assert uow.committed is True


def test_get_coverage_service():
    """
    Given a FakeUnitOfWork with requirements having passing, failing, and missing tests
    When calling get_coverage service handler
    Then accurate coverage metrics summary and grouped matrix are returned.
    """
    tc_pass = {
        "id": "TC-REQ-201",
        "name": "test_pass",
        "given": "Given X",
        "when": "When Y",
        "then": "Then Z",
        "status": "Passing",
        "last_result": "pass",
        "requirement_id": "REQ-201"
    }
    tc_fail = {
        "id": "TC-REQ-202",
        "name": "test_fail",
        "given": "Given A",
        "when": "When B",
        "then": "Then C",
        "status": "Failing",
        "last_result": "fail",
        "requirement_id": "REQ-202"
    }

    req1 = Requirement(id="REQ-201", title="Req 1", description="Desc 1", tests=[tc_pass])
    req2 = Requirement(id="REQ-202", title="Req 2", description="Desc 2", tests=[tc_fail])
    req3 = Requirement(id="REQ-203", title="Req 3", description="Desc 3", tests=[])
    
    uow = FakeUnitOfWork(initial_requirements=[req1, req2, req3])

    coverage = services.get_coverage(uow=uow)

    summary = coverage["summary"]
    assert summary["total_requirements"] == 3
    assert summary["total_test_cases"] == 2
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["uncovered"] == 1
    assert summary["coverage_percent"] == 50.0
    assert len(coverage["matrix"]) == 2


def test_run_test_execution_services():
    """
    Given a FakeUnitOfWork
    When calling run_all_tests and run_single_test service handlers
    Then execution start responses are returned cleanly.
    """
    uow = FakeUnitOfWork()

    all_res = services.run_all_tests(uow=uow)
    assert all_res["success"] is True
    assert "started" in all_res["message"].lower()

    single_res = services.run_single_test(test_id="TC-REQ-101", uow=uow)
    assert single_res["success"] is True
    assert "TC-REQ-101" in single_res["message"]


def test_generate_allure_report_service():
    """
    Given a FakeUnitOfWork containing requirements with tests
    When calling generate_allure_report service handler
    Then report URL and summary metrics are returned cleanly.
    """
    tc = {
        "id": "TC-REQ-301",
        "name": "test_report",
        "status": "Passing",
        "last_result": "pass",
        "requirement_id": "REQ-301"
    }
    req = Requirement(id="REQ-301", title="Req Report", description="Report Desc", tests=[tc])
    uow = FakeUnitOfWork(initial_requirements=[req])

    report = services.generate_allure_report(uow=uow)
    assert report["success"] is True
    assert "report_url" in report
    assert report["summary"]["total_requirements"] == 1
    assert report["summary"]["passing"] == 1
