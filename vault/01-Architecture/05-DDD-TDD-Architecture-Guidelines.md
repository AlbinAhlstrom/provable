# DDD & TDD Architecture Guidelines

This document defines the standardized Domain-Driven Design (DDD) and Test-Driven Development (TDD) architectural guidelines for applications built and maintained within Provable, based on patterns from *Architecture Patterns with Python* (Cosmic Python).

```mermaid
graph TD
    subgraph Entrypoints [Layer 4: Presentation & Entrypoints]
        API[FastAPI / Web Routes] --> ServiceLayer
        CLI[CLI Commands / Events] --> ServiceLayer
    end

    subgraph ServiceLayer [Layer 3: Application Service Layer & Unit of Work]
        UoW[Unit of Work (UoW)] --> Repo[Repository Protocol]
        UoW --> DomainModel[Domain Model]
        Handlers[Service Functions / Command Handlers] --> UoW
    end

    subgraph Adapters [Layer 2: Infrastructure & Adapters]
        Repo --> SQLAlchemy[ORM / SQLite Datastore]
        Repo --> ExternalAPIs[External API Clients]
    end

    subgraph Domain [Layer 1: Core Domain Model]
        DomainModel --> Entities[Entities & Value Objects]
        DomainModel --> DomainEvents[Domain Events]
    end
```

---

## 🏛️ Architectural Principles

Applications created or modified by Provable autonomous developer agents must adhere to the 4 concentric architectural layers:

### 1. Pure Domain Model (`domain/`)
- **Isolation**: Must not import ORMs, database frameworks (SQLAlchemy, Django), HTTP clients, or IO libraries.
- **Components**:
  - **Entities**: Objects with persistent identity (e.g. `Order`, `Batch`).
  - **Value Objects**: Immutable data structures defined purely by attributes (e.g. `Money`, `Sku`, `Quantity`).
  - **Domain Services**: Pure business logic operations involving multiple domain entities.
- **Testing**: Tested exclusively via **Low Gear TDD** (fast, pure-Python unit tests with zero IO).

### 2. Repository Abstraction (`adapters/`)
- **Purpose**: Decouple domain models from persistence mechanisms.
- **Protocol**: Expose explicit abstract base classes or protocols (`AbstractRepository`) with standard methods like `.add(entity)` and `.get(id)`.
- **Implementations**:
  - `SqlAlchemyRepository` for production SQL storage.
  - `FakeRepository` in-memory implementation for high-gear testing without database dependencies.

### 3. Application Service Layer & Unit of Work (`service_layer/`)
- **Use Case Orchestration**: Accepts primitive types (strings, ints, dicts), fetches entities via Repository, invokes domain methods, and commits changes.
- **Unit of Work (UoW)**:
  - Manages atomic transactions and context boundaries (`with uow:`).
  - Owns instances of repositories for the duration of a transaction.
- **Testing**: Tested via **High Gear TDD** (end-to-end use case tests using `FakeUnitOfWork`).

### 4. Entrypoints & Presentation (`entrypoints/`)
- **Role**: Thin wrappers mapping HTTP requests, CLI commands, or message events into call signatures for the Service Layer.
- **Strict Boundary**: API route handlers must **NEVER** contain SQL queries, ORM session manipulation, or direct business rules.

---

## 🧪 Shift-Left TDD Execution Pipeline

Provable enforces a requirement-driven TDD pipeline across all feature branches:

1. **Requirement Mapping**: Every StrictDoc requirement (`workspace/requirements/requirements.sdoc`) maps directly to a BDD Pytest scenario in `workspace/tests/`.
2. **Low Gear vs High Gear Strategy**:
   - **Low Gear**: Pure unit tests verifying business invariants on `domain/` objects.
   - **High Gear**: Integration tests verifying use case workflows in `service_layer/` with `FakeUnitOfWork`.
   - **End-to-End**: API contract tests verifying `entrypoints/` using Pytest WebTest / TestClient.
3. **Allure Matrix Mapping**: All tests must include `@allure.epic`, `@allure.feature`, and `@allure.story` annotations matching requirement IDs.

---

## 📚 Chapter Pattern Reference (Cosmic Python)

| Chapter / Pattern | Architectural Responsibility | Provable Implementation Guidance |
| :--- | :--- | :--- |
| **Ch 1: Domain Model** | Enforce business rules in pure Python objects | Store in `workspace/src/domain/` without ORM annotations |
| **Ch 2: Repository Pattern** | Abstract storage behind clean interface | Define `AbstractRepository` in `workspace/src/adapters/repository.py` |
| **Ch 3 & 5: High vs Low Gear TDD** | Balance test speed with coverage | Write domain unit tests first (Low Gear), service tests second (High Gear) |
| **Ch 4: Service Layer** | Orchestrate use cases & primitive parameters | Define use case functions in `workspace/src/service_layer/services.py` |
| **Ch 6: Unit of Work** | Provide atomic transaction boundaries | Implement `AbstractUnitOfWork` in `workspace/src/service_layer/unit_of_work.py` |
| **Ch 7: Aggregates** | Define consistency boundaries for data mutations | Wrap related domain entities under a single Aggregate root |
| **Ch 8-11: Events & Message Bus** | Decouple side-effects and microservice integrations | Use in-memory `MessageBus` for domain events and command handlers |
| **Ch 12: CQRS** | Separate read queries from write commands | Provide dedicated optimized read queries bypassing full domain models |

---

## 🔗 Related Documentation
- [[System Architecture]]
- [[Shift-Left TDD Workflow]]
- [[Testing Strategy]]
- [[Agent Execution Loop]]
