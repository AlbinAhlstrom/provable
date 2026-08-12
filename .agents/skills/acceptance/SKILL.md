---
name: acceptance
description: Rigorous 6-step TDD, self-critique, acceptance criteria formulation, and verification workflow for code changes.
---

# Acceptance Protocol Skill

This skill defines the standard 6-step Quality & Acceptance Protocol for Antigravity agents executing complex code modifications, refactorings, or new features.

---

## 📋 The 6-Step Acceptance Workflow

### Step 1: Self-Critique & Plan Refinement
Before modifying source code, perform a critical review of the proposed plan:
- **Edge Cases & Failure Modes**: What boundary conditions or unexpected inputs could break this logic?
- **Performance & Latency**: Does this approach introduce synchronous network bottlenecks or heavy loops?
- **Architectural Integrity**: Does this introduce hardcoded string hacks or special-casing? If so, replace with contract-driven abstractions.
- **Accessibility & UX**: Does this violate WCAG contrast ratios, typography rules, or visual layout boundaries?

### Step 2: Define Acceptance Criteria
Formulate clear, unambiguous criteria divided into two categories:

#### 🧪 Testable Acceptance Criteria (Automated)
- Quantitative invariants (e.g., zero hardcoded keyword cascades, zero pizza string leakage, WCAG contrast ratio $\ge 4.5:1$).
- Specific API response schemas and database state contracts.
- 100% pass rate across automated test suites.

#### 🖐️ Manual Verification Criteria (User Verification)
- Visual styling, color harmony, and layout proportions.
- Interactive UX responsiveness and canvas controls.
- End-to-end user flows in the live browser preview (`http://localhost:5174`).

### Step 3: Test-Driven Development (TDD) First
- Author automated tests **BEFORE** modifying implementation code (`backend/tests/test_<feature>.py`).
- Include edge case assertions and contract invariants.
- Execute the test suite to verify initial expected failure (Red state).

### Step 4: Implement Solution
- Implement source code changes adhering to Domain-Driven Design (DDD) layer boundaries.
- Ensure all business logic relies on contracts/schemas rather than hardcoded string checks.

### Step 5: Automated Verification Loop
- Run automated tests (`pytest backend/tests`).
- If any assertion fails, inspect the error traceback silently, fix the underlying root cause, and re-run.
- Repeat until 100% of testable criteria pass (Green state).

### Step 6: Handover & Manual Verification Report
- Summarize work accomplished and automated test results.
- Explicitly list the manual verification steps for the user to perform in the live preview.
- Update documentation sitemap and handover records (`vault/HANDOVER.md`).

---

## 🛠️ Usage Example

When instructed to apply the `acceptance` workflow:

```bash
# 1. Run TDD tests (expecting failure)
pytest backend/tests/test_feature.py

# 2. Implement changes in backend/

# 3. Verify clean pass
pytest backend/tests

# 4. Re-sync application shell if needed
python -c "import sys; sys.path.insert(0, 'backend'); from main import sync_workspace_app_shell; sync_workspace_app_shell()"
```
