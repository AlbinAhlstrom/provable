# ADR-001: Host vs Containerized Execution

## Context
Provable needs to run Vite web development/preview servers and execute pytest test suites for the code generated inside the `workspace/` directory. We must decide whether to run these processes directly on the developer's host machine (WSL environment) or isolate them inside Docker containers.

## Decision
For the initial prototype, we will run Vite servers and pytests **directly on the host machine (WSL)**. We defer full containerization of the target workspace for a later production design iteration.

## Alternatives Considered

### Option A: Host / WSL Execution (Selected)
Execute `npm run dev` and `pytest` using the host's runtime environment and the Python virtual environment located at `backend/venv`.
- **Pros**:
  - Extremely fast start times (Vite dev server launches in milliseconds).
  - Simpler networking (localhost is shared, avoiding port mapping issues).
  - Lower prototype complexity (no need to manage Docker containers programmatically).
- **Cons**:
  - No security sandbox: the LLM-generated code runs with the developer's user permissions (risk of executing malicious shell scripts).
  - Host pollution: requires Node, Python, Chrome, and ChromeDriver to be installed on the host WSL instance.

### Option B: Sandboxed Docker Containerization (Deferred)
Launch a Docker container for each ticket branch, mounting `workspace/` and executing tests inside the isolated container.
- **Pros**:
  - Secure sandboxing: agents cannot access host files or execute commands outside the container.
  - Consistent environments: dependencies are locked in the container image.
- **Cons**:
  - Virtualization startup overhead (seconds vs. milliseconds).
  - Complex network routing to bridge the PM Studio interface to nested containers.
  - File permission issues with bind mounts between WSL and Docker.

## Status
**Accepted (Prototype)** - Deferred full containerization to production design stage.
