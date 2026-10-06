# ADR-003: LLM Abstraction Layer and Prompt Externalization

## Context
In early Provable prototypes, LLM API calls were hardcoded to Gemini models, and system prompts were embedded directly in Python strings inside `backend/agent_orchestrator.py`. This made it difficult to swap LLM providers (e.g. to OpenAI, Anthropic, or local Ollama models) or modify developer agent prompts without modifying backend code.

## Decision
We abstract all LLM interactions and externalize prompt templates:

1. **LLM Abstraction Layer**: Built using the OpenAI Python SDK to allow a standardized, API-compatible interface. Provider, endpoint and model are chosen via environment variables.
2. **Prompt Externalization**: Intended to move system prompts and templates out of Python files. They are stored as structured markdown files under `backend/prompts/` and loaded at runtime with `load_prompt`.
3. **Environment Setup**: The API key and LLM provider endpoint are configured via standard `.env` variables (`LLM_API_KEY`, etc.).

## Alternatives Considered
- **Direct Gemini SDK Integration**: Kept LLM calls restricted to Google Gemini. Dismissed because it limits the ability to test alternative models (e.g. GPT-4o, Claude) or local models (Ollama).
- **Embedded Python Prompt Strings**: Kept prompts inside code. Dismissed because prompt engineering is a primary workflow for refining agent developer behaviors, necessitating independent modification.

## Status
**Accepted**

## Amendment
Only part of the prompt externalization was completed: 4 prompts are file-based and the rest remain inline in `backend/onboarding/`. The `models.yaml` router was never read by code and was removed. See [[LLM Abstraction and Prompts]] for the current state.
