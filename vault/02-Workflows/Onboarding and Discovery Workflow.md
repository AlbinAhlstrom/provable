# Onboarding & Workspace Discovery Workflow

When Provable is initialized against a new target repository (or when the active workspace is changed), the discovery subsystem inspects project structure, configuration files, and build manifests to auto-configure agent execution parameters.

```mermaid
flowchart TD
    Select[User selects target repository workspace] --> Scan[Discovery Agent scans workspace files]
    Scan --> DetectFramework{Detect App Framework}
    DetectFramework -->|package.json / vite| Vite[Configure Vite preview dev server port :5174]
    DetectFramework -->|pyproject.toml / pytest| Pytest[Configure Pytest runner & allure-results]
    Scan --> SyncSpecs[Scan workspace for existing requirements / sdoc specs]
    Vite --> Config[Synthesize project configuration]
    Pytest --> Config
    SyncSpecs --> Config
    Config --> Store[Save project settings to SQLite DataStore]
```

## Discovery Steps

### 1. Framework & Dev Server Auto-Detection
- Scans `package.json` for frontend framework markers (Vite, Next.js, React).
- Auto-configures preview server launch commands (e.g. `npm run dev -- --port 5174`).

### 2. Test Runner Discovery
- Checks for `pytest.ini`, `conftest.py`, or `pyproject.toml`.
- Configures default test command: `pytest -v --alluredir=allure-results`.

### 3. Specification Discovery
- Checks for `.sdoc` specification files or `requirements.json`.
- Automatically executes `sync_sdoc_to_db()` to import requirement hierarchies into SQLite.
