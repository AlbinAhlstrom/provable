# Testing Strategy & Quality Assurance Architecture

Provable enforces a 3-tier Domain-Driven Design (DDD) test architecture combined with deterministic Test-Driven Development (TDD). Every business rule is backed by automated BDD test specs before implementation code is written.

---

## 3-Tier DDD Test Architecture (`backend/tests/`)

```
backend/tests/
├── unit/         # Fast (<0.5s) in-memory unit tests using FakeUnitOfWork and pure domain logic
├── integration/  # Multi-component integration tests (router engine, startup, purity)
└── e2e/          # Dynamic UI projection verification via The Gibberish Strategy
```

### Tier 1: Unit Tests (`backend/tests/unit/`)
- Fast in-memory unit tests exercising pure domain models (`domain/model.py`), Unit of Work (`FakeUnitOfWork`), service handlers, and LibCST class isolators.
- **Execution Speed**: 100+ tests execute in `< 1.5s`.

### Tier 2: Integration Tests (`backend/tests/integration/`)
- Verifies multi-stage domain synthesis pipelines (`test_dual_track_benchmarks.py`), tri-service startup connectivity, and strict frontend domain vocabulary purity (`test_frontend_domain_purity.py`).

### Tier 3: E2E Tests (`backend/tests/e2e/`)
- **The Gibberish Strategy (`test_ui_dynamic_projection.py`)**: Feeds synthetic nonsense schemas (`TestFlorg` / `Zorp`) to mathematically prove the UI is a 100% domain-agnostic projection with zero hardcoded legacy components.

---

## BDD Test Docstring & Allure Metadata Tagging

All generated pytest specs (`workspace/tests/unit/test_*.py`) must include BDD Given-When-Then docstrings:

```python
import pytest

def test_pallet_capacity_limit():
    """
    BDD Specification: Enforce Maximum Weight Limit
    Given a storage Zone with 1000kg maximum capacity
    When a Pallet weighing 1200kg is allocated to the Zone
    Then raise CapacityExceededError
    """
    ...
```

---

## 5-Line Hash Lock Anti-Cheat Verification

```python
initial_hash = compute_test_file_hash(test_file_path)
# Execute GREEN Phase Code Generation
verify_test_file_integrity(test_file_path, initial_hash)
```

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original testing strategy envisioned full browser-driven Selenium E2E tests validating visual renders on every ticket run. While browser automation is valuable, consolidating visual QA to lightweight API contracts and The Gibberish Strategy reduced test execution time from 80s+ to 2s.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[Automated-Verification-And-Self-Healing-Pipeline]]
- [[Bug-Reproduction-and-Testing-Policy]]

