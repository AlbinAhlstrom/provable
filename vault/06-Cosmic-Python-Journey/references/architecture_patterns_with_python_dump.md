# Architecture Patterns with Python - Part 1

## Introduction: Why Do Our Designs Go Wrong?
Software systems tend toward chaos. Without deliberate effort, a well-ordered architecture collapses into a "Big Ball of Mud", characterized by a sameness of function where everything is coupled to everything else.

### Encapsulation and Abstractions
Encapsulation covers simplifying behavior and hiding data. We encapsulate behavior by identifying a task and giving it to a well-defined object or function, called an abstraction. Abstracting away details helps make code expressive, testable, and easier to maintain. 

### The Dependency Inversion Principle (DIP)
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

High-level modules deal with real-world business concepts, while low-level modules deal with technical infrastructure (network, filesystem, databases). We insert an abstraction layer between them so they can change independently. 

---

## Chapter 1: Domain Modeling
The domain model is the mental map business owners have of their business. It is the part of your code that is closest to the business, most likely to change, and where you deliver the most value.

### Entities vs Value Objects
- **Value Object**: Any domain object uniquely identified by the data it holds (e.g., an OrderLine or Money). Usually immutable. If you change an attribute, it becomes a different object.
- **Entity**: A domain object with long-lived identity (e.g., a Person or a Batch). Its attributes may change over time, but it remains the same entity. Usually implements equality (`__eq__`) based on a unique reference.

### Domain Service
Not everything has to be an object. If an operation doesn't naturally fit inside a stateful entity or value object, it can be a stateless function (e.g., `allocate(line, batches)`).

### Domain Exceptions
Exceptions can express domain concepts (e.g., `OutOfStock` when trying to allocate beyond available quantity).

---

## Chapter 2: Repository Pattern
The Repository pattern is an abstraction over persistent storage. It hides the details of data access by giving the illusion of a collection of in-memory objects.

### Inverting the Dependency
Instead of the model depending on the ORM (e.g., inheriting from SQLAlchemy's `Base`), the ORM should depend on the model. Using SQLAlchemy's classical mapper (`mapper(model.OrderLine, order_lines)`) keeps the domain pure and unaware of the database.

### Abstract Repository
```python
class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError
```

### Trade-offs: Repository Pattern
| Pros | Cons |
| --- | --- |
| Simple interface between storage and domain model. | Maintaining ORM mappings by hand requires extra work. |
| Easy to make a `FakeRepository` for unit testing. | Extra layer of indirection increases maintenance costs. |
| Keeps focus on business logic rather than DB schemas. | Can be confusing for programmers unfamiliar with the pattern. |

---

## Chapter 3: Coupling and Abstractions
When we are unable to change component A for fear of breaking component B, we say they are coupled. We can reduce coupling by introducing a simpler abstraction between them.

### Functional Core, Imperative Shell (FCIS)
Isolate the stateful, I/O-heavy parts of the application from the business logic. Let the business logic (Functional Core) take simple data structures and return simple data structures representing actions to be taken, which the Imperative Shell then executes.

### Testing Philosophy: Fakes over Mocks
- **Mocks** (London-school TDD): Verify *how* something gets used (e.g., `assert_called_once_with`). Lead to tests tightly coupled to implementation.
- **Fakes** (Classic-style TDD): Working implementations of dependencies designed for tests (e.g., an in-memory FakeRepository). Allow assertions about the end state of a system.
- TDD is a design practice first. Over-mocked tests get overwhelmed with setup code and hinder refactoring.

---

## Chapter 4: Service Layer
The Service Layer (or Orchestration Layer) orchestrates workflows and defines the use cases of the system. 

### Responsibilities of a Service Layer
1. Fetch objects from the repository.
2. Validate input against current state.
3. Call a domain service.
4. Persist any changes.

By keeping orchestration logic in the service layer, the domain logic stays pure, and the web entrypoints (e.g., Flask APIs) remain thin.

### Service Layer Implementation
```python
def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
```

### Trade-offs: Service Layer
| Pros | Cons |
| --- | --- |
| Single place capturing all application use cases. | Can seem like boilerplate for purely CRUD web apps. |
| Defines a clear API, allowing independent refactoring. | Requires passing around stateful components. |
| Enables fast "high gear" unit testing with fakes. | |
# Architecture Patterns with Python - Part 2 Extract

## Chapter 6: Unit of Work Pattern

### Pattern Definition and Explanation
The Unit of Work (UoW) pattern is an abstraction over the idea of atomic operations. It allows decoupling the service layer from the data layer. The UoW acts as a single entrypoint to persistent storage and keeps track of what objects were loaded and of the latest state. This provides:
1. A stable snapshot of the database to work with.
2. A way to persist all changes at once, so if something goes wrong, the system doesn't end up in an inconsistent state.
3. A simple API to persistence concerns and a handy place to get a repository.

### Code Example
```python
class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
```

### Wrap-Up / Recap
- **The Unit of Work pattern is an abstraction around data integrity**: It helps enforce consistency of the domain model and improves performance by letting us perform a single flush operation at the end of an operation.
- **It works closely with the Repository and Service Layer patterns**: The UoW completes abstractions over data access by representing atomic updates.
- **This is a lovely case for a context manager**: Context managers are an idiomatic way of defining scope in Python.
- **SQLAlchemy already implements this pattern**: We introduce an even simpler abstraction over the SQLAlchemy Session object in order to "narrow" the interface between the ORM and our code.

### Trade-offs
| Pros | Cons |
|------|------|
| We have a nice abstraction over atomic operations, and the context manager makes it easy to see what blocks of code are grouped atomically. | Your ORM probably already has some perfectly good abstractions around atomicity (like SQLAlchemy context managers). |
| Explicit control over when a transaction starts and finishes; application fails in a way that is safe by default. | You have to think quite carefully about things like rollbacks, multithreading, and nested transactions. |
| It's a nice place to put all your repositories so client code can access them. | |
| Atomicity isn't only about transactions; it can help us work with events and the message bus. | |

## Chapter 7: Aggregates and Consistency Boundaries

### Pattern Definition and Explanation
An **Aggregate** is a cluster of associated objects that we treat as a unit for the purpose of data changes. It helps to resolve the tension between protecting invariants and allowing for concurrency. The aggregate acts as a boundary where every operation ends in a consistent state.

### Code Example
```python
class Product:
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events = [] # type: List[events.Event]

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(
                b for b in sorted(self.batches) if b.can_allocate(line)
            )
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None
```

### Wrap-Up / Recap
- **Aggregates are your entrypoints into the domain model**: By restricting the number of ways that things can be changed, we make the system easier to reason about.
- **Aggregates are in charge of a consistency boundary**: An aggregate's job is to manage business rules about invariants as they apply to a group of related objects.
- **Aggregates and concurrency issues go together**: Choosing the right aggregate is about performance as well as conceptual organization.

### Trade-offs
| Pros | Cons |
|------|------|
| Choosing aggregates lets you decide which domain classes are public and which aren't. | Yet another new concept for developers to take on. |
| Modeling operations around explicit consistency boundaries helps avoid ORM performance problems. | Sticking rigidly to the rule of modifying only one aggregate at a time is a big mental shift. |
| Putting the aggregate in sole charge of state changes makes the system easier to reason about. | Dealing with eventual consistency between aggregates can be complex. |

## Part II: Event-Driven Architecture (Intro)

### Philosophical Statement
> "I'm sorry that I long ago coined the term 'objects' for this topic because it gets many people to focus on the lesser idea. The big idea is 'messaging.'...The key in making great and growable systems is much more to design how its modules communicate rather than what their internal properties and behaviors should be." â€” Alan Kay

## Chapter 8: Events and the Message Bus

### Pattern Definition and Explanation
- **Domain Events**: Trigger workflows that cross consistency boundaries. Events are facts about things that have happened.
- **Message Bus**: Provides a unified way of invoking use cases from any endpoint. It acts as a publish-subscribe system mapping events to their handlers.

### Code Example
```python
@dataclass
class OutOfStock(Event):
    sku: str

def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

HANDLERS = {
    events.OutOfStock: [send_out_of_stock_notification],
}
```

### Wrap-Up / Recap
- **Events can help with the single responsibility principle**: Events help keep things tidy by separating primary use cases from secondary ones.
- **A message bus routes messages to handlers**: It's a piece of dumb infrastructure for getting messages around the system.
- **Options for publishing events**:
  1. Service layer raises events and passes them to message bus.
  2. Domain model raises events, service layer passes them to message bus.
  3. UoW collects events from aggregates and passes them to message bus (recommended).

### Trade-offs
| Pros | Cons |
|------|------|
| A message bus separates responsibilities when taking multiple actions per request. | An additional concept to learn; UoW magically raising events might obscure flow. |
| Event handlers are decoupled from core application logic. | Hidden event-handling code executes synchronously by default. |
| Domain events model the real world and align with business language. | Event-driven workflows can make it harder to trace the lifecycle of a request. |

## Chapter 9: Going to Town on the Message Bus

### Pattern Definition and Explanation
Transforming the application fundamentally into a message processor. External API calls and internal side effects all map to events (e.g., `AllocationRequired`, `BatchQuantityChanged`) which are routed through the message bus to handlers. This eliminates the distinction between internal and external event handlers.

### Code Example
```python
def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
        queue.extend(uow.collect_new_events())
    return results
```
# Architecture Patterns with Python - Part 3 Extract (Chapters 10-13, Epilogue)

## Chapter 10: Commands and Command Handler

### Pattern Definitions: Commands vs Events
*   **Commands:** Capture intent. They express our wish for the system to do something. They are sent by one actor to another specific actor with the expectation that a particular thing will happen. They are named with imperative mood verb phrases like "allocate stock". When they fail, the sender needs to receive error information.
*   **Events:** Capture facts about things that happened in the past. They are broadcast by an actor to all interested listeners. Senders should not care whether the receivers succeeded or failed. They are named with past-tense verb phrases like "order allocated".

### Trade-off Table: Events vs Commands

| Feature | Event | Command |
| :--- | :--- | :--- |
| Named | Past tense | Imperative mood |
| Error handling | Fail independently | Fail noisily |
| Sent to | All listeners | One recipient |

### Error Handling Philosophy
By separating messages into commands and events, we make it possible for things to fail in isolation, improving overall reliability. A command should modify a single aggregate and succeed or fail in totality. Any other bookkeeping, cleanup, and notification happen via events. Event handlers don't need to succeed for the command to be successful. We invite failure but handle it by making failures smaller and more isolated.

### Code Example: Dispatching Events vs Commands differently

```python
Message = Union[commands.Command, events.Event]

def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} was not an Event or Command')
    return results

def handle_event(event: events.Event, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception('Exception handling event %s', event)
            continue

def handle_command(command: commands.Command, queue: List[Message], uow: unit_of_work.AbstractUnitOfWork):
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception('Exception handling command %s', command)
        raise
```

### Wrap-Up / Trade-offs Table

| Pros | Cons |
| :--- | :--- |
| Treating commands and events differently helps us understand which things have to succeed and which things we can tidy up later. | The semantic differences between commands and events can be subtle. Expect bikeshedding arguments. |
| Explicit names like `CreateBatch` convey user intent clearly. | We're expressly inviting failure, choosing to make failures smaller and isolated. This can make the system harder to reason about and requires better monitoring. |


## Chapter 11: Event-Driven Architecture (Microservices Integration)

### Temporal Decoupling and Microservices
A naive approach to microservices splits systems by nouns (e.g., Batches, Orders), linking them with synchronous HTTP calls. This creates a "Distributed Ball of Mud" with temporal coupling: every part of the system has to work at the same time for any part of it to work. 

Instead, think in verbs (e.g., ordering, allocating). Like aggregates, microservices should be consistency boundaries. Between two services, accept eventual consistency using asynchronous messaging (events). This reduces the strength of coupling (Connascence of Name instead of Connascence of Execution/Timing) and allows services to fail independently.

### Trade-off Table: Event-Based Integration

| Pros | Cons |
| :--- | :--- |
| Avoids the distributed big ball of mud. | The overall flows of information are harder to see. |
| Services are decoupled: it's easier to change individual services and add new ones. | Eventual consistency is a new concept to deal with. |
| | Message reliability and delivery guarantees need thinking through. |


## Chapter 12: Command-Query Responsibility Segregation (CQRS)

### Pattern Definition: CQRS
Reads (queries) and writes (commands) are different and should be treated differently. Domain models apply complex business rules and consistency boundaries (aggregates) during writes. Reads often require different data shapes, can tolerate stale (eventually consistent) data, and need high cacheability and performance. Command-Query Separation (CQS) states that functions should either modify state or answer questions, but never both.

### Trade-off Table: Read vs Write

| | Read side | Write side |
| :--- | :--- | :--- |
| Behavior | Simple read | Complex business logic |
| Cacheability | Highly cacheable | Uncacheable |
| Consistency | Can be stale | Must be transactionally consistent |

### Code Example: Updating a Read Model Table via Event Handler

```python
def add_allocation_to_read_model(
    event: events.Allocated, uow: unit_of_work.SqlAlchemyUnitOfWork,
):
    with uow:
        uow.session.execute(
            'INSERT INTO allocations_view (orderid, sku, batchref)'
            ' VALUES (:orderid, :sku, :batchref)',
            dict(orderid=event.orderid, sku=event.sku, batchref=event.batchref)
        )
        uow.commit()
```

### Trade-off Table: View Model Options

| Option | Pros | Cons |
| :--- | :--- | :--- |
| Just use repositories | Simple, consistent approach. | Expect performance issues with complex query patterns. |
| Use custom queries with ORM | Allows reuse of DB config and models. | Adds another query language with quirks. |
| Use hand-rolled SQL | Fine control over performance, standard syntax. | DB schema changes affect hand-rolled queries and ORM. |
| Separate read stores with events | Read-only copies scale easily; views can be customized for queries. | Complex technique; suspicious motives. |


## Chapter 13: Dependency Injection and Bootstrapping

### Pattern Definition: Composition Root (Bootstrap)
We use explicit dependencies (Dependency Inversion Principle) to avoid heavy monkeypatching and coupling to implementations. The Composition Root (bootstrap script) is a single place where dependencies are configured, instantiated, and injected into handlers, initializing the message bus at runtime.

### Code Example: Manual DI with Closures/Partials

```python
def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
```

### Wrap-Up
Setting up Dependency Injection (DI) is part of the one-time initialization done at app startup in a bootstrap script. The script provides sensible defaults for adapters and is a single place to override those adapters with fakes for testing. For complex dependency chains, a DI framework might be useful, but manual DI via functions/classes is often sufficient.


## Epilogue: Getting There from Here

### Extracting Use Cases from a Ball of Mud
To break apart a legacy system, start by separating responsibilities into a Service Layer. Identify use cases with imperative names (e.g., "Apply Billing Charges"). Each use case orchestrates work: starts a transaction, fetches data, updates the domain model, and persists changes. Move data-access and orchestration out of the domain model and into the use cases.

### Identifying Aggregates
Highly connected object graphs (where `user.account.workspaces[0].documents` is possible) kill performance. Break direct links and bidirectional relationships by replacing object references with identifiers. An aggregate is a consistency boundary; each use case should update a single aggregate at a time to remain eventually consistent.

### The Strangler Fig Pattern
To move to microservices, use "event interception":
1. Raise events for changes in the old system.
2. Build a new system that consumes those events for its domain model.
3. Replace the older system with the new one.
# Architecture Patterns with Python - Part 4

## Footguns

Before attempting to implement these patterns in a production system, consider the following caveats:

### Reliable messaging is hard
Redis pub/sub is not reliable and shouldn't be used as a general-purpose messaging tool. Consider using tools like Event Store, RabbitMQ, or Amazon EventBridge. Understanding trade-offs in distributed messaging is essential (e.g., exactly-once delivery is a myth).

### We explicitly choose small, focused transactions that can fail independently
In our models, updating an aggregate and related aggregates often happen in separate units of work. You will need monitoring to know when these transactions fail, and tooling to replay events. Using a transaction log as your message broker (e.g., Kafka or EventStore) or the Outbox pattern can help.

### We don't discuss idempotency
Handlers should ideally be idempotent so that calling them repeatedly with the same message will not make repeated changes to state. This enables safely retrying events when they fail.

### Your events will need to change their schema over time
You'll need a way of documenting your events and sharing schemas with consumers (e.g., JSON schema). Versioning event-sourced systems is a complex topic.

## Appendix A: Summary Diagram and Table

### Components of our architecture

| Layer | Component | Description |
|-------|-----------|-------------|
| **Domain** | Entity | A domain object whose attributes may change but that has a recognizable identity over time. |
| | Value object | An immutable domain object whose attributes entirely define it. Fungible with identical objects. |
| | Aggregate | Cluster of associated objects treated as a unit for data changes. Defines a consistency boundary. |
| | Event | Represents something that happened. |
| | Command | Represents a job the system should perform. |
| **Service Layer** | Handler | Receives a command or event and performs what needs to happen. |
| | Unit of work | Abstraction around data integrity. Represents an atomic update. Tracks new events on retrieved aggregates. |
| | Message bus (internal) | Routes commands and events to the appropriate handler. |
| **Adapters** | Repository | Abstraction around persistent storage. Each aggregate has its own repository. |
| | Event publisher | Pushes events onto the external message bus. |
| **Entrypoints** | Web | Receives web requests and translates them into commands for the internal message bus. |
| | Event consumer | Reads events from the external message bus and translates them into commands for the internal message bus. |
| **External** | External message bus | Infrastructure that different services use to intercommunicate via events. |

## Appendix B: A Template Project Structure

The basic folder structure for a well-organized project:

```
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ Makefile
â”œâ”€â”€ README.md
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ mypy.ini
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ src
â”‚   â”œâ”€â”€ allocation
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ adapters
â”‚   â”‚   â”‚   â”œâ”€â”€ orm.py
â”‚   â”‚   â”‚   â””â”€â”€ repository.py
â”‚   â”‚   â”œâ”€â”€ config.py
â”‚   â”‚   â”œâ”€â”€ domain
â”‚   â”‚   â”‚   â””â”€â”€ model.py
â”‚   â”‚   â”œâ”€â”€ entrypoints
â”‚   â”‚   â”‚   â””â”€â”€ flask_app.py
â”‚   â”‚   â””â”€â”€ service_layer
â”‚   â”‚       â””â”€â”€ services.py
â”‚   â””â”€â”€ setup.py
â””â”€â”€ tests
    â”œâ”€â”€ conftest.py
    â”œâ”€â”€ e2e
    â”œâ”€â”€ integration
    â”œâ”€â”€ pytest.ini
    â””â”€â”€ unit
```

- **`config.py`**: Centralized configuration management using environment variables.
- **`docker-compose.yml`**: Defines the different services (containers) needed. 
- **`setup.py`**: Makes the `src` folder pip-installable for easy imports.

## Appendix C: Swapping Out the Infrastructure

The benefits of the Repository, Unit of Work, and Service Layer patterns become clear when swapping out infrastructure, such as moving from a database to CSV files. Because infrastructure concerns are decoupled from the domain model and service layer, switching to CSVs only requires writing new Repository and UnitOfWork classes, allowing full reuse of domain logic.

## Appendix D: Repository and Unit of Work Patterns with Django

To use Django instead of SQLAlchemy:
- **Repository Pattern**: You can create a DjangoRepository that implements `add`, `get`, and `list`. Since Django's ORM couples models to the database, you'll need custom methods on your Django models to translate to and from your pure domain model (e.g., `update_from_domain` and `to_domain`).
- **Unit of Work Pattern**: Implement a DjangoUnitOfWork that sets `transaction.set_autocommit(False)` on entry and uses `transaction.commit()` or `transaction.rollback()`.
- **Views**: Django views act as adapters, functioning similarly to Flask endpoints, passing requests to the service layer.

**Caveat**: If your app is heavily read-oriented or a simple CRUD app, these patterns may add unnecessary boilerplate and fight against Django's strengths. 

## Appendix E: Validation

Validation is about testing inputs to ensure they match criteria before processing (preconditions). It's useful to categorize it into three subtypes:

### 1. Syntactic Validation
Validating the structure of incoming data (e.g., "Quantity must be a positive integer").
- **Where**: Validate syntax at the edge of the system (e.g., on the message class or API endpoint). Handlers should only receive well-formed messages.
- **Tolerant Reader Pattern**: Be strict in what you send, lenient in what you receive. Read only the fields you need, and don't overspecify their structure (e.g., treat a SKU as an opaque string rather than strictly validating its format, unless you own the format).

### 2. Semantic Validation
Validating the meaning of the data (e.g., "The product SKU exists").
- **Where**: Often handled at the service layer or message handler layer using preconditions (e.g., checking if an entity exists before processing).

### 3. Pragmatic Validation
Validating business rules in context (e.g., "Is there enough stock available to fulfill this order?").
- **Where**: Pragmatics belong in the domain model. This is the core business logic.
