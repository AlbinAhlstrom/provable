# Integration Test Checklist

This checklist tracks integration test coverage across Provable subsystems.

## SQLite DataStore & StrictDoc Sync
- [x] **Bidirectional Synchronization**:
    - [x] Verify requirement addition in DataStore exports to `.sdoc`.
    - [x] Verify SDoc import populates SQLite database without data corruption.

## SQLite DataStore & Allure Coverage
- [x] **Coverage Metric Calculation**:
    - [x] Verify updating test case status updates `get_coverage_summary` calculation.

## Requirement Test Case Generation Flow (`create-test-case`)
- [x] **Automated TDD Spec Generation Flow**:
    - [x] Verify `POST /api/requirements/{req_id}/create-test-case` generates failing TDD test spec file and attaches record to requirement (`REQ-TST-002`).
