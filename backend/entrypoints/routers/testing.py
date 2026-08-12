"""
Testing API Router — Handles test generation, test creation/fixing, test execution runs, and Allure metrics.
"""

from fastapi import APIRouter, BackgroundTasks
from service_layer import services
from service_layer.unit_of_work import SqliteUnitOfWork

router = APIRouter()


@router.post("/api/requirements/{req_id}/generate-test")
def generate_test_for_requirement(req_id: str):
    """Trigger automated LLM generator to synthesize BDD unit tests for a requirement."""
    uow = SqliteUnitOfWork()
    return services.generate_test_for_requirement(req_id, uow=uow)


@router.get("/api/coverage")
def get_coverage():
    """Returns matrix of test cases grouped by requirement, status, and BDD Given/When/Then descriptions."""
    uow = SqliteUnitOfWork()
    return services.get_coverage(uow=uow)


@router.post("/api/requirements/{req_id}/create-test-case")
def create_test_case(req_id: str):
    """Trigger generator to draft a new BDD test case file for a requirement."""
    uow = SqliteUnitOfWork()
    return services.create_test_case(req_id, uow=uow)


@router.post("/api/requirements/{req_id}/fix-test-case")
def fix_test_case(req_id: str, background_tasks: BackgroundTasks):
    """Trigger self-healing agent loop to fix failing test assertions for a requirement."""
    uow = SqliteUnitOfWork()
    return services.fix_test_case(req_id, uow=uow, background_tasks=background_tasks)


@router.post("/api/tests/run")
def run_all_tests(background_tasks: BackgroundTasks):
    """Executes full Pytest suite asynchronously in workspace container."""
    uow = SqliteUnitOfWork()
    return services.run_all_tests(uow=uow, background_tasks=background_tasks)


@router.post("/api/tests/{test_id}/run")
def run_single_test(test_id: str, background_tasks: BackgroundTasks):
    """Executes single test case by ID and updates DB result."""
    uow = SqliteUnitOfWork()
    return services.run_single_test(test_id, uow=uow, background_tasks=background_tasks)


@router.get("/api/allure/report")
def generate_allure_report():
    """Generates Allure report link and returns test coverage summary."""
    uow = SqliteUnitOfWork()
    return services.generate_allure_report(uow=uow)
