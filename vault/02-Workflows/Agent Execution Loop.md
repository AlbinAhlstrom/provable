# Agent Execution Loop

Provable orchestrates autonomous coding agents using a StateGraph state machine implemented via **LangGraph**. The orchestrator manages branch checkout, code generation, preview serving, pytest execution, Allure reporting uploads, selenium screenshot captures, visual layout validations, and clean git rollback controls.

```mermaid
graph TD
    START([START]) --> prepare_branch[Node: prepare_branch]
    prepare_branch --> code_generation[Node: code_generation]
    code_generation --> test_runner[Node: test_runner]
    
    test_runner -->|Failed & attempt < max| code_generation
    test_runner -->|Failed & attempt >= max| finalize[Node: finalize]
    test_runner -->|Passed| visual_qa[Node: visual_qa]
    
    visual_qa -->|Failed & attempt < max| code_generation
    visual_qa -->|Failed & attempt >= max| finalize
    visual_qa -->|Passed| finalize
    
    finalize --> END([END])
```

## LangGraph Nodes & Logic

### 1. `prepare_branch`
*   Sets up the clean developer sandbox environment.
*   Determines if a target git branch (prefixed with `ticket/`) already exists.
*   Resets and checks out the branch, ensuring a clean slate.

### 2. `code_generation`
*   Loads external prompt templates (from `backend/prompts/code_generation.md`).
*   Injects the requirement context (title, description), failing test code, and any prior loop execution errors/hints (from test or visual QA failures).
*   Calls the LLM (Gemini 2.5 Flash) via the OpenAI abstraction layer to generate source file edits.
*   Writes the generated code files directly into the `workspace/` project.

### 3. `test_runner`
*   Launches the Vite preview dev server on port `5174` (via `ensure_preview_server`).
*   Executes the test suite inside the workspace sandbox using `pytest -v --alluredir=allure-results`.
*   Uploads generated results to the Allure container (`allure_client.py`).
*   Evaluates outcome:
    *   If the target test case fails and the current attempt is below the maximum limit, loops back to `code_generation` with stderr log feedback.
    *   If it fails and the maximum limit (default: 3) is reached, routes directly to `finalize` as a failure.
    *   If tests pass, routes to `visual_qa`.

### 4. `visual_qa`
*   Initializes a headless Selenium Webdriver inside WSL.
*   Takes application screenshots at mobile (`375x812`) and desktop (`1280x800`) resolutions.
*   Calls Gemini Vision with the screenshots and proposed code to perform a layout check (checking for overflows, text overlaps, or broken styles).
*   Evaluates outcome:
    *   If visual discrepancies are found and attempts remain, loops back to `code_generation` with visual layout corrective suggestions.
    *   If it fails and attempts are exhausted, routes to `finalize` as a failure.
    *   If it passes, routes to `finalize` as a success.

### 5. `finalize`
*   Wraps up the execution run.
*   **On Success**: Stages and commits code changes to the ticket branch using git, and sets the SQLite requirement status to `Review`.
*   **On Failure**: Discards all uncommitted changes (`git checkout -- .` and `git clean -fd`), reverts the workspace state, updates the ticket feedback column in SQLite with run failure reasons, and resets status to `Backlog`.
