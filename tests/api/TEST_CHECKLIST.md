# API Test Checklist

This checklist tracks FastAPI REST endpoint test coverage in Provable (`backend/main.py`).

## Project Management Endpoints
- [x] **`GET /api/projects`**: List all registered workspace projects.
- [x] **`GET /api/project/settings`**: Get current active project metadata.
- [x] **`POST /api/projects/switch`**: Switch active project workspace.
- [x] **`POST /api/projects/add`**: Register new project path.

## Requirements & Folder Endpoints
- [x] **`GET /api/requirements`**: Get full requirements hierarchy tree.
- [x] **`POST /api/create-requirement`**: Create requirement record.
- [x] **`POST /api/create-folder`**: Create section folder.
- [x] **`DELETE /api/requirements/{req_id}`**: Delete requirement or folder.
- [x] **`POST /api/requirements/{req_id}/move`**: Reparent requirement.

## Test Case & Coverage Endpoints
- [x] **`POST /api/requirements/{req_id}/create-test-case`**: Generate failing pytest spec for requirement.
- [x] **`GET /api/coverage`**: Calculate requirement coverage metrics.

## Agent Loop & Code Review Endpoints
- [x] **`GET /api/reviews`**: List tickets under code review.
- [x] **`GET /api/agent-status`**: Check background agent execution status.
- [x] **`GET /api/diff/{ticket_id}`**: Get raw git diff for review branch.
