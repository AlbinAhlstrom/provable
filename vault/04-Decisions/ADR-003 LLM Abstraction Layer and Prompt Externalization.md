# ADR-003: LLM Abstraction Layer and Prompt Externalization

## Context
In early Provable prototypes, LLM API calls were hardcoded to Gemini models, and system prompts were embedded directly in Python strings inside `backend/agent_orchestrator.py`. This made it difficult to swap LLM providers (e.g. to OpenAI, Anthropic, or local Ollama models) or modify developer agent prompts without modifying backend code.

## Decision
We abstract all LLM interactions and externalize prompt templates:

1. **LLM Abstraction Layer**: Built using the OpenAI Python SDK to allow a standardized, API-compatible interface. LLM routing is configured in `backend/config/models.yaml`, mapping custom identifiers (e.g., `gemini-2.5-flash`) to specific API models and parameters.
2. **Prompt Externalization**: Removed all system prompts and templates from Python files. They are stored as structured markdown files under `backend/prompts/` (e.g., `write_code.md`, `run_tests.md`) and loaded dynamically at runtime.
3. **Environment Setup**: The API key and LLM provider endpoint are configured via standard `.env` variables (`LLM_API_KEY`, etc.).

## Alternatives Considered
- **Direct Gemini SDK Integration**: Kept LLM calls restricted to Google Gemini. Dismissed because it limits the ability to test alternative models (e.g. GPT-4o, Claude) or local models (Ollama).
- **Embedded Python Prompt Strings**: Kept prompts inside code. Dismissed because prompt engineering is a primary workflow for refining agent developer behaviors, necessitating independent modification.

## Status
**Accepted**
