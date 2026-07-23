# System Test Checklist

This checklist tracks system-level workflow tests for Provable's execution engine.

## Agent Orchestrator Pipeline (`agent_orchestrator.py`)
- [x] **State Machine Mechanics**:
    - [x] Verify prompt template loading (`backend/prompts/`).
    - [x] Verify agent execution status updates and ticket handling.

## Workspace Onboarding & Requirements Generation (`onboarding/`)
- [x] **Workspace Discovery**:
    - [x] Workspace file tree scanning and summary generation.
