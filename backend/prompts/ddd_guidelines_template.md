# DDD Architecture & Code Structure Guidelines

When implementing code for this ticket, you MUST adhere to Domain-Driven Design (DDD) layer separation and clean architecture principles:

1. **Domain Model Layer (`domain/`)**:
   - Write pure domain logic (Entities, Value Objects, Domain Services).
   - Domain objects must NOT import ORMs (SQLAlchemy, Django), database connection pools, or web frameworks (FastAPI, Flask).
   - Enforce business invariants directly in domain entity methods.

2. **Repository Protocol & Adapters (`adapters/`)**:
   - Abstract data storage behind a Repository interface (`AbstractRepository`).
   - Standard operations: `.add(entity)`, `.get(id)`, `.list()`.
   - Keep ORM mappings or raw SQL isolated strictly within repository adapters (`SqlAlchemyRepository`).

3. **Application Service Layer & Unit of Work (`service_layer/`)**:
   - Orchestrate use cases in service functions.
   - Use the Unit of Work (UoW) pattern (`with uow:`) for atomic transaction management.
   - Service layer functions accept primitive parameters (e.g. `order_id: str`, `qty: int`), fetch entities via UoW repositories, execute domain operations, and commit transactions.

4. **Entrypoints & Presentation (`entrypoints/` or API routes)**:
   - Keep controllers, HTTP route handlers, and CLI commands thin.
   - Entrypoints must delegate requests to the Service Layer functions.
   - NEVER place raw SQL, ORM queries, or business rules inside API route handlers.

5. **Test-Driven Development (TDD)**:
   - Write **Low Gear** unit tests (`tests/unit/`) directly against `domain/` objects.
   - Write **High Gear** integration tests (`tests/integration/`) against `service_layer/` using `FakeUnitOfWork` and `FakeRepository`.
   - Write **End-to-End** API tests (`tests/e2e/`) against `entrypoints/` to verify HTTP contracts.
