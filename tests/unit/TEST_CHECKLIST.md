# Unit Test Checklist

This checklist tracks unit test coverage for the Provable backend components (`db/store.py`, `config_loader.py`, `integrations/`, `onboarding/`).

## SQLite DataStore (`db/store.py`)
- [x] **Database Initialization (`init_db`)**:
    - [x] Verify table schemas (`requirements`, `test_cases`, `agent_runs`, `settings`).
    - [x] Verify column additions and migration handling.
- [x] **Requirement CRUD**:
    - [x] Create requirement (`create_requirement`).
    - [x] Fetch requirements hierarchy (`get_all_requirements`).
    - [x] Fetch single requirement (`get_requirement_by_id`).
    - [x] Update requirement status / content (`update_requirement`).
    - [x] Move requirement (`move_requirement`).
    - [x] Delete requirement (`delete_requirement`).
- [x] **Test Cases CRUD**:
    - [x] Create test case (`create_test_case`).
    - [x] Fetch test cases for requirement (`get_test_cases_for_req`).
    - [x] Update test case execution result & failure message (`update_test_case_status`).
- [x] **Agent Runs & Settings**:
    - [x] Log agent run (`log_agent_run`).
    - [x] Retrieve agent runs (`get_agent_runs`).
    - [x] Fetch & update global settings (`get_settings`, `update_settings`).

## Configuration Loader (`config_loader.py`)
- [x] **YAML Configurations**:
    - [x] Load models config (`get_models_config`).
    - [x] Load integrations config (`get_integrations_config`).
    - [x] Dynamic workspace path resolution (`get_workspace_base`).

## StrictDoc Integration (`integrations/strictdoc_client.py`)
- [x] **Export & Import**:
    - [x] Export DataStore requirements to `.sdoc` string.
    - [x] Parse `.sdoc` document strings.

## Allure Dashboard Integration (`integrations/allure_client.py`)
- [x] **Allure Client**:
    - [x] Allure endpoint status check (`check_allure_status`).
    - [x] Project setup payload generation.

## Server Supervision (`onboarding/server_manager.py`)
- [x] **Server Manager**:
    - [x] Port checking functionality (`is_port_in_use`).
