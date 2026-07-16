# ADR-004: Allure Reporting Server Docker Integration

## Context
Provable requires a test reporting dashboard showing detailed metrics, history, and requirement coverage. Generating static HTML reports for every run is resource-intensive and does not support dynamic visual updates.

## Decision
We integrate the Allure Docker Service to host and serve visual test reports.

1. **Docker Container**: A containerized Allure service (`frankescobar/allure-docker-service`) is executed on port `5050` (mapped via `docker-compose.allure.yaml` or run command).
2. **Startup Initialization Hook**: On backend startup, the FastAPI app performs an HTTP POST request to register the project ID (`provable`):
   ```python
   requests.post("http://localhost:5050/projects", json={"id": "provable"})
   ```
   This ensures that the project is registered inside the Allure container memory, resolving any `project_id not found` issues when the Allure iframe is embedded in the frontend.
3. **Report Generation**: The pytest runner in the workspace outputs results to `workspace/allure-results/` using `--alluredir=allure-results`. The Allure service monitors this folder and auto-generates reports.

## Alternatives Considered
- **Static Allure HTML Generation**: Generating reports locally and rendering them. Dismissed because static HTML generation is slow, and linking coverage metrics back to requirement IDs is highly complex without a database dashboard.

## Status
**Accepted**
