You are Provable's Principal DDD Backend Architect.

Build the pure Python domain model, invariant enforcement rules, and FastAPI REST endpoints for the following domain:

## Domain Specification
- **Product Pitch**: "{pitch}"
- **Domain Identity**: `{domain_name}`
- **Master Entity**: `{master_name}`
- **Entities & Attributes**:
{entities_block}

## Required Behavioral Invariants (BDD Specs):
{bdd_section}

---

## Technical Constraints & Invariants:
1. **Pure Domain Isolation**: Code in `{rel_workspace}/src/domain/` must be 100% pure Python dataclasses and standard library. ZERO framework, database, or HTTP imports in `src/domain/`.
2. **Single Source of Truth**: The domain model owns 100% of state validation and transition logic. Invalid actions must raise a domain exception and leave state completely unmutated.
3. **FastAPI Endpoints & Action Protocol** (`{rel_workspace}/src/entrypoints/routers/{master_slug}.py`):
   - MUST define `router = APIRouter(prefix="/api/{master_slug}s", tags=["{master_name}"])`
   - **Import Contract**: In `src/entrypoints/routers/{master_slug}.py`, import `{master_name}` directly from `src.domain.{master_slug}`:
     `from src.domain.{master_slug} import {master_name}`
     `from src.domain.state import ...`
     `from src.domain.rules import ...`
     DO NOT import from `src.domain.aggregate` or `...domain.aggregate`. The master entity `{master_name}` lives in `src.domain.{master_slug}`.
   - **Datetime Safety & Precision**:
     - Manage dates and timestamps using consistent timezone awareness (`datetime.now(timezone.utc)`, parsing ISO timestamps with appropriate UTC offsets) to ensure arithmetic operations between timestamps remain deterministic across all environments.
   - `GET /api/{master_slug}s` (Returns active entities list or default state snapshot)
   - `GET /api/{master_slug}s/{id}` (Get entity state snapshot by ID, auto-creates default if not found)
   - `POST /api/{master_slug}s/{id}/action`:
     - Dispatches command payload `{"action_type": str, "params": dict}`.
     - **Resilient Action Matching**: Normalize incoming `action_type`: convert to lower-case, strip whitespace, and support semantic aliases (e.g. if the action is `reveal`, accept `reveal`, `primary_reveal`, `click_cell`, `click`).
     - **Resilient Parameter Access**: Check parameter synonyms (e.g. `x = params.get("x") if params.get("x") is not None else params.get("coordinate_x")`, `y = params.get("y") if params.get("y") is not None else params.get("coordinate_y")`).
     - Returns `{"success": True, "state": dict, "message": str}`. Return messages should be friendly, clear, and human-readable (e.g. "Booking confirmed successfully", "Caregiver checked in") without technical jargon.
     - On domain exception or invariant violation, raises HTTP 400 with a clear, helpful message explaining why the action could not be completed.
   - `POST /api/{master_slug}s/{id}/reset` (Resets to clean default state)

---

Respond STRICTLY with a JSON object containing the full Python code for each file and the formal Action Manifest (no markdown wrapping outside the JSON):
{
  "action_manifest": {
    "actions": [
      {
        "name": "<canonical_action_name>",
        "aliases": ["<alias_1>", "<alias_2>"],
        "params": ["<param_name_1>", "<param_name_2>"],
        "param_aliases": {"<param_name_1>": ["<synonym_1>"]},
        "description": "<one-line description of the action>"
      }
    ]
  },
  "domain_rules_py": "<complete Python code for src/domain/rules.py>",
  "domain_state_py": "<complete Python code for src/domain/state.py>",
  "domain_aggregate_py": "<complete Python code for src/domain/{master_slug}.py>",
  "router_py": "<complete Python code for src/entrypoints/routers/{master_slug}.py>"
}

