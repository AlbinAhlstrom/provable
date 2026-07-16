# Provable Project Wiki

Welcome to the Provable Project Obsidian Vault! This is the centralized knowledge base for Provable, an agentic software engineering simulation platform where PMs orchestrate autonomous developer agents using a strict, Requirements-Driven TDD workflow.

## 🗺️ Vault Map

### 1. 🏗️ [[System Architecture]]
- [[System Architecture]]: Overview of the frontend, backend, database, and LangGraph orchestrator.
- [[Database Schema]]: Database design of SQLite tables and triggers.
- [[Integrations]]: Sync clients for Jira, StrictDoc, and Allure reporting.

### 2. 🔄 Agent Workflows
- [[Shift-Left TDD Workflow]]: Unified pre-review testing execution, requirement-driven test generation, and test coverage mapping.
- [[Agent Execution Loop]]: LangGraph-driven execution, screenshot capture mechanics, and error state rollbacks.

### 3. ⚖️ Architectural Decisions (ADRs)
- [[ADR-001 Host vs Containerized Execution]]: Decision record on executing Vite dev servers and Pytest on the host/WSL machine vs sandboxed Docker container.
- [[ADR-002 SQLite and StrictDoc Bidirectional Sync]]: Decision record on bridging specifications with a performant relational SQLite database.
- [[ADR-003 LLM Abstraction Layer and Prompt Externalization]]: Decision record on prompt externalization and model-agnostic routing.
- [[ADR-004 Allure Reporting Server Docker Integration]]: Decision record on utilizing a containerized Allure service for automated visual test reports.

### 4. 📜 Agent Rules & Customizations
- [[Agent Customizations]]: Workspace restriction rules (`workspace/` off-limits) and Chrome/Selenium headless args.

---
*Updated by Antigravity on 2026-07-16.*
