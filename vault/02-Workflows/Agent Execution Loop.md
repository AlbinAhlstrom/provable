# Deterministic TDD Agent Execution Pipeline

Provable utilizes a **Deterministic TDD State Machine** ([`backend/service_layer/tdd_machine.py`](../../backend/service_layer/tdd_machine.py)) enforcing programmatic Red-Gate evaluation, Meta LibCST code isolation, and SHA-256 test integrity hash locking.

```mermaid
sequenceDiagram
    participant Inbox as Behavior Inbox (Specs)
    participant TDD as TDD State Machine (tdd_machine.py)
    participant LibCST as LibCST Isolator (cst_isolator.py)
    participant Pytest as Pytest Runner (5s Timeout)
    participant Git as Git Version Control

    Inbox->>TDD: 1. Pop Next Business Spec (SPEC-XXX)
    activate TDD
    TDD->>TDD: 2. RED_GEN: Generate BDD unit test (test_spec.py)
    TDD->>Pytest: 3. Execute Pytest on test_spec.py
    Pytest-->>TDD: Evaluate Exit Code 1 & AssertionError (Approved RED)
    
    TDD->>TDD: 4. 5-Line Hash Lock: Compute SHA-256 hash of test_spec.py
    TDD->>LibCST: 5. Extract Aggregate Root CST from domain model
    LibCST-->>TDD: Target Class Definition CST
    TDD->>LibCST: 6. Splice implemented class back into module
    
    TDD->>TDD: 7. Re-verify test_spec.py SHA-256 hash (Anti-Cheat)
    TDD->>Pytest: 8. Execute Pytest on test_spec.py (5s Timeout)
    
    alt Green Phase Passed (Exit Code 0)
        Pytest-->>TDD: 0 Errors / All Assertions Pass
        TDD->>Git: Auto-commit spec feature branch / main
        TDD->>Inbox: Update Spec Status to "FULFILLED" 🟢
    else Green Phase Failed (Attempts < 3)
        Pytest-->>TDD: AssertionError in Green
        TDD->>TDD: Retry LibCST repair loop
    else Green Phase Dead-End (Attempts == 3)
        TDD->>Git: git reset --hard to pre-RED state
        TDD->>Inbox: Update Spec Status to "REQUIRES_HUMAN_INTERVENTION" 🔴
    end
    deactivate TDD
```

---

## Detailed Execution Steps

### 1. Spec Intake & RED Gate
- Ingests atomic `BusinessSpec` from Behavior Inbox.
- Generates BDD pytest test file (`workspace/tests/unit/test_<spec_id>.py`).
- Executes Pytest with `--timeout=5` and `--json-report`.
- **Programmatic Red-Gate Evaluation (`evaluate_red_gate_result`)**:
  - Exit Code 0 (Pass without code) $\rightarrow$ **REJECTED_TAUTOLOGY**.
  - Before that verdict, the test is run once more against the class with every method emptied out (`service_layer/hollow_check.py`, on a temporary copy of the sources). If it fails there, it does test behaviour and the class already has it (the action stage writes the methods before the rule deck runs): the spec is `FULFILLED` with `already_satisfied`, no code is generated, and the test stays in `tests/unit` as the rule's regression guard. If it passes there too, it asserts nothing and is a tautology.
  - Exit Code 2 / SyntaxError / Timeout $\rightarrow$ **REJECTED_SYNTAX_OR_EXEC**.
  - Exit Code 1 with `AssertionError` $\rightarrow$ **APPROVED_RED**.

### 2. 5-Line SHA-256 Hash Lock Anti-Cheat
- Computes SHA-256 hash snapshot of `test_<spec_id>.py`.
- Enforces that no test assertion or file content is tampered with during code generation.

### 3. LibCST Surgical Class Splicing (`cst_isolator.py`)
- Extracts the exact class CST node from the domain module.
- Generates or updates domain methods and invariants.
- Splices updated class back into the module preserving 100% of formatting, comments, and docstrings.

### 4. GREEN Gate & Commit / Rollback
- Re-verifies test file SHA-256 hash (`verify_test_file_integrity`).
- Executes Pytest. If Exit Code 0: marks spec `FULFILLED` and commits.
- If failed after 3 attempts: executes `git reset --hard` to pre-RED state and flags `REQUIRES_HUMAN_INTERVENTION`.

---

## 🏛️ Discrepancies & Evolution Tags

> [!NOTE]
> [DISCREPANCY: Doc approach better - The original execution loop specification was designed for autonomous LLM code generation iterating over full repo branches. While tdd_machine.py successfully isolates the RED-GREEN-COMMIT loop, the GREEN implementation currently relies on stub mutations rather than live LLM-driven LibCST prompts. Connecting the LLM to the LibCST micro-context is architecturally superior.]

---

## 🔗 Related Documentation
- [[Enterprise-AppGen-TDD-Engine-Architecture]]
- [[System Architecture]]
- [[DDD_TDD_Developer_Workflow]]

