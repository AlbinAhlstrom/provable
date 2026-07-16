# ADR-002: SQLite and StrictDoc Bidirectional Sync

## Context
Provable requires a robust, structured way to model software requirements, parent-child relations, and test linking. We need to bridge the gap between human-readable requirements specification formats (like StrictDoc's `.sdoc` specifications) and the high-performance database queries needed by the React-based PM Studio frontend.

## Decision
We implement a hybrid, bidirectional synchronization system between an SQLite database (`backend/provable.db`) and StrictDoc text specification files (`workspace/requirements/requirements.sdoc`).

1. **SQLite DataStore**: Serves as the primary runtime storage for API endpoints. It stores requirements, test cases, and agent runs, allowing fast reads, parent-child tree queries, and transactional updates.
2. **StrictDoc `.sdoc` File**: Serves as the persistent local requirements file inside the codebase. It represents the "specs" in the "specs-to-code" loop.
3. **Synchronization Logic (`strictdoc_client.py`)**:
   - **Import (`sync_sdoc_to_db`)**: Parses the `.sdoc` spec file on backend startup and imports/syncs its sections and requirement UIDs into the SQLite database.
   - **Export (`export_sdoc`)**: Rewrites the `.sdoc` file dynamically whenever a requirement or task is modified, added, or deleted via the frontend PM Studio interface.

## Alternatives Considered
- **StrictDoc Only**: Direct parsing of `.sdoc` files for every API request. Dismissed due to file-IO performance bottleneck and complex relational queries.
- **SQLite Only**: Storing requirements only in database tables. Dismissed because it lacks a localized, text-based specification format that simulated developer agents can easily read and write inside the repository.

## Status
**Accepted**
