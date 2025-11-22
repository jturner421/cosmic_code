# Repository Pattern Analysis: Abstract vs Concrete Implementations

**Date:** November 21, 2025
**Context:** Comparing `AbstractRepository` (ABC-based) vs `SqlAlchemyRepository` (concrete generic) approaches
**Future Application:** Event-sourced aggregates with UUID-based entities

---

## Executive Summary

This analysis examines two repository patterns coexisting in this codebase:

1. **`AbstractRepository`** - Formal ABC interface for UUID-based domain entities
2. **`SqlAlchemyRepository`** - Pragmatic concrete generic for simple models

**Key Finding:** These patterns are **complementary, not competing**. SqlAlchemyRepository did NOT replace AbstractRepository - they serve different purposes and were designed to coexist.

---

## File Structure

```
repository/
├── __init__.py          # AbstractRepository (ABC for UUID-based entities)
└── repositories.py      # SqlAlchemyRepository + domain-specific repos
```

---

## Pattern 1: AbstractRepository (ABC Approach)

**Location:** `/repository/__init__.py`

### Implementation

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from domain.entities import Entity
from domain.value_objects import GenericUUID

Entity = TypeVar("Entity", bound="DomainEntity")
EntityId = TypeVar("EntityId", bound=GenericUUID)

class AbstractRepository(ABC, Generic[Entity, EntityId]):
    """Abstract base class for repositories managing domain entities.

    This abstract class is designed for UUID-based entities that inherit
    from domain.entities.Entity. For simpler domain models like Batch/OrderLine,
    see SqlAlchemyRepository in repositories.py.
    """

    @abstractmethod
    def add(self, entity: Entity) -> None:
        """Add an entity to the repository."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: EntityId) -> Entity | None:
        """Retrieve an entity by its ID."""
        raise NotImplementedError

    def __getitem__(self, entity_id: EntityId) -> Entity | None:
        """Dict-like access to get_by_id."""
        return self.get_by_id(entity_id)
```

### Characteristics

- **Type:** Abstract Base Class (ABC)
- **Generics:** Two type variables with strict bounds
  - `Entity` → must inherit from `domain.entities.Entity`
  - `EntityId` → must inherit from `GenericUUID`
- **Purpose:** Formal contract for complex domain entities
- **Contract:** Compile-time interface verification via ABC
- **Identity:** UUID-based only

### When to Use

✅ **Use AbstractRepository when:**
- Building event-sourced aggregates
- Entities have UUID-based identity
- Need multiple implementations (SQL, EventStore, in-memory)
- Require formal interface guarantees
- Building large DDD systems with substitutable repositories
- Type safety at boundaries is critical

❌ **Don't use when:**
- Models use non-UUID identifiers (string refs, integers)
- Doing simple CRUD on DTOs or value objects
- Only one implementation exists
- Models are plain classes/dataclasses without rich behavior

---

## Pattern 2: SqlAlchemyRepository (Concrete Generic)

**Location:** `/repository/repositories.py`

### Implementation

```python
from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")

class SqlAlchemyRepository(Generic[T]):
    """Generic SQLAlchemy repository implementation."""

    def __init__(self, entity_class: Type[T], session: Session):
        self.entity_class = entity_class
        self.session = session

    def add(self, entity: T) -> None:
        """Add an entity to the session."""
        self.session.add(entity)

    def get(self, **kwargs) -> T | None:
        """Get a single entity by filter criteria."""
        stmt = select(self.entity_class).filter_by(**kwargs)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[T]:
        """List all entities."""
        stmt = select(self.entity_class)
        return list(self.session.scalars(stmt))


class BatchRepository(SqlAlchemyRepository[Batch]):
    """Repository for Batch aggregate."""

    def get_by_reference(self, reference: str) -> Batch | None:
        """Get a batch by its reference."""
        return self.get(reference=reference)


class OrderLineRepository(SqlAlchemyRepository[OrderLine]):
    """Repository for OrderLine entities."""

    def get_by_orderid(self, orderid: str) -> OrderLine | None:
        """Get an order line by order ID."""
        return self.get(orderid=orderid)
```

### Characteristics

- **Type:** Concrete generic class (no ABC)
- **Generics:** One unbounded type variable (`T`)
- **Purpose:** Pragmatic CRUD for simple models
- **Contract:** Duck typing, no formal interface
- **Identity:** Any type (strings, integers, UUIDs)
- **Extensibility:** Composition via subclassing

### When to Use

✅ **Use SqlAlchemyRepository when:**
- Models are simple (plain classes, dataclasses, Pydantic models)
- Identifiers are non-UUID (strings, integers, composite keys)
- Doing straightforward CRUD operations
- Only need SQLAlchemy implementation
- Want to add domain-specific query methods via subclassing
- Pragmatism over formalism

❌ **Don't use when:**
- Need multiple storage backends (SQL + EventStore + cache)
- Require formal interface contracts
- Building complex DDD system with many aggregate types
- Need compile-time verification of repository interface

---

## Historical Evidence: Git Analysis

### Timeline of Changes

**1. Initial Creation (Nov 2, 2025) - Commit b82a126**
```
Created domain/repositories.py with GenericRepository (ABC with UUID)
```

**2. Refactoring (Nov 21, 2025) - Commit 3a26443**
```
refactor: implement repository pattern with SqlAlchemy

- Moved domain/repositories.py → repository/__init__.py
- Renamed GenericRepository → AbstractRepository
- Created SqlAlchemyRepository as SEPARATE implementation (NOT inheriting from ABC)
```

**3. Domain Repositories (Nov 21, 2025) - Commit 6547a55**
```
feat: add BatchRepository and OrderLineRepository implementations

- Added domain-specific repos extending SqlAlchemyRepository
- Updated AbstractRepository docstring to recommend SqlAlchemyRepository for simple models
- Message: "Replace generic AbstractRepository usage with concrete implementations"
```

**4. SQLAlchemy 2.0 Migration (Nov 21, 2025) - Commit 2926166**
```
Migrated from legacy Query API to modern select() statements
```

### Key Insights from History

1. **Both created simultaneously** - Not a replacement scenario
2. **Intentional separation** - Different purposes documented from the start
3. **"Replace usage"** ≠ "Replace class" - Usage pattern changed, not architecture
4. **AbstractRepository preserved** - Still exists for future complex entities

---

## Comparison Matrix

| Aspect | AbstractRepository | SqlAlchemyRepository |
|--------|-------------------|---------------------|
| **Type** | Abstract Base Class (ABC) | Concrete Generic Class |
| **Interface Contract** | ✅ Formal (ABC enforced) | ❌ Informal (duck typing) |
| **Type Safety** | ✅ High (bounded generics) | ⚠️ Medium (unbounded T) |
| **Identity Type** | 🔒 UUID only | ✅ Any type |
| **Entity Requirements** | 🔒 Must inherit Entity | ✅ Any class |
| **Multiple Implementations** | ✅ Designed for it | ❌ Single implementation |
| **Boilerplate** | ⚠️ High (inherit + implement) | ✅ Low (just instantiate) |
| **Extensibility** | ⚠️ Via inheritance | ✅ Via subclassing |
| **YAGNI Friendly** | ❌ Premature abstraction risk | ✅ Start simple |
| **DDD Alignment** | ✅ Perfect for aggregates | ⚠️ Good for simple models |
| **Testing** | ✅ Easy to mock interface | ⚠️ Mock concrete class |

---

## Domain Models in This Codebase

### Simple Models (Current)

**OrderLine:**
```python
from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class OrderLine:
    orderid: str  # NOT UUID
    sku: str
    qty: int
```

**Batch:**
```python
class Batch:
    def __init__(self, reference: str, sku: str, qty: int, eta: date | None = None):
        self.reference = reference  # NOT UUID
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations: set[OrderLine] = set()
```

**Why SqlAlchemyRepository fits:**
- Neither inherits from `domain.entities.Entity`
- Neither uses UUID identifiers
- Simple state, minimal behavior
- Basic CRUD sufficient

### Rich Domain Entities (Future)

**domain.entities.Entity:**
```python
from domain.value_objects import GenericUUID

EntityId = TypeVar("EntityId", bound=GenericUUID)

class Entity(ABC, Generic[EntityId]):
    """Base class for domain entities with identity."""

    def __init__(self, id: EntityId):
        self.id = id

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id


class AggregateRoot(Entity[EntityId]):
    """Base class for aggregate roots that produce domain events."""

    def __init__(self, id: EntityId):
        super().__init__(id)
        self.events: list[DomainEvent] = []
```

**Why AbstractRepository fits:**
- UUID-based identity
- Rich domain behavior
- Domain events (event sourcing ready)
- Multiple implementations needed (EventStore + read models)

---

## Trade-offs Analysis

### AbstractRepository (ABC) Approach

#### Advantages
✅ **Formal Contract:** ABC enforces interface implementation at class definition time
✅ **Polymorphism:** Easy substitution of implementations (SQL, NoSQL, in-memory, EventStore)
✅ **Type Safety:** Bounded generics prevent using wrong entity types
✅ **Documentation:** Abstract methods self-document required operations
✅ **Testing:** Mock/stub the interface, not concrete implementations
✅ **Consistency:** Forces all repos to implement same methods

#### Disadvantages
❌ **Rigidity:** Requires specific base classes (Entity, GenericUUID)
❌ **Boilerplate:** Must inherit ABC and implement all abstract methods
❌ **Over-engineering:** Overkill for simple CRUD on DTOs
❌ **Premature Abstraction:** YAGNI violation if multiple implementations never needed
❌ **Type Constraints:** Can't use with plain classes or non-UUID identifiers

### SqlAlchemyRepository (Concrete Generic) Approach

#### Advantages
✅ **Flexibility:** Works with any type (plain classes, dataclasses, ORM models)
✅ **Simplicity:** No inheritance required, just instantiate
✅ **Pragmatic:** Right amount of abstraction for simple models
✅ **Composable:** Easy to extend via subclassing (BatchRepository, OrderLineRepository)
✅ **Modern Python:** Generic without ABC overhead
✅ **Fast to Build:** Less ceremony, quicker to implement

#### Disadvantages
❌ **No Interface Contract:** No compile-time guarantee of method signatures
❌ **Single Implementation:** Tied to SQLAlchemy
❌ **Less Type Safety:** Unbounded `T` allows any type
❌ **Harder to Mock:** Must mock concrete class, not interface
❌ **No Consistency Enforcement:** Nothing forces similar repos to implement same methods

---

## Architectural Decision Guide

### Decision Tree

```
Is your entity a rich domain model with UUID identity?
│
├─ YES → Use AbstractRepository
│   │
│   ├─ Do you need multiple storage backends?
│   │   ├─ YES → Definitely AbstractRepository
│   │   └─ NO → Still consider AbstractRepository for consistency
│   │
│   └─ Does it produce domain events (event sourcing)?
│       └─ YES → AbstractRepository is perfect
│
└─ NO → Use SqlAlchemyRepository
    │
    ├─ Is it a simple DTO/value object?
    │   └─ YES → SqlAlchemyRepository
    │
    ├─ Uses string/integer identifiers?
    │   └─ YES → SqlAlchemyRepository
    │
    └─ Just doing basic CRUD?
        └─ YES → SqlAlchemyRepository
```

### Pattern Selection Matrix

| Your Situation | Recommended Pattern | Rationale |
|---------------|-------------------|-----------|
| Event-sourced aggregates with UUIDs | AbstractRepository | Needs multiple implementations (EventStore + projections) |
| Simple models with string IDs | SqlAlchemyRepository | Pragmatic for straightforward CRUD |
| Value objects (immutable) | SqlAlchemyRepository | No identity, just data access |
| Complex aggregates with behavior | AbstractRepository | Rich domain model benefits from formal contract |
| Read models / projections | SqlAlchemyRepository | Simple queries, no domain logic |
| Single database, simple app | SqlAlchemyRepository | Don't over-engineer |
| Microservices with event sourcing | AbstractRepository | Multiple storage types, formal boundaries |

---

## Event Sourcing Considerations

### Why AbstractRepository Shines in Event-Sourced Systems

**Event-sourced aggregates typically need:**

1. **Event Store Access**
```python
class EventSourcedRepository(AbstractRepository[Aggregate, AggregateId]):
    def get_by_id(self, aggregate_id: AggregateId) -> Aggregate | None:
        events = self.event_store.load_events(aggregate_id)
        return Aggregate.reconstruct_from_events(events)

    def add(self, aggregate: Aggregate) -> None:
        new_events = aggregate.collect_events()
        self.event_store.append_events(aggregate.id, new_events)
```

2. **Snapshot Repository (performance optimization)**
```python
class SnapshotRepository(AbstractRepository[Aggregate, AggregateId]):
    def get_by_id(self, aggregate_id: AggregateId) -> Aggregate | None:
        snapshot = self.snapshot_store.load_snapshot(aggregate_id)
        if snapshot:
            events = self.event_store.load_events_after(aggregate_id, snapshot.version)
            return snapshot.aggregate.apply_events(events)
        return self._load_from_full_history(aggregate_id)
```

3. **Read Model Repository (CQRS)**
```python
class ReadModelRepository(SqlAlchemyRepository[ReadModel]):
    """Projections don't need AbstractRepository - they're just queries."""
    pass
```

### Pattern Recommendation for Event Sourcing

```python
# Aggregates (write side) → AbstractRepository
class OrderAggregate(AggregateRoot[OrderId]):
    pass

class OrderRepository(AbstractRepository[OrderAggregate, OrderId]):
    """Event-sourced aggregate repository."""
    pass

# Read models (query side) → SqlAlchemyRepository
class OrderSummaryRepository(SqlAlchemyRepository[OrderSummary]):
    """Projection repository for queries."""
    pass
```

**Key Principle:**
- **Write side (aggregates):** AbstractRepository with EventStore
- **Read side (projections):** SqlAlchemyRepository with SQL

---

## Lessons Learned for Event-Sourced Systems

### 1. Identity Matters

Event-sourced aggregates MUST have:
- Stable UUID identity
- Identity assigned at creation, never changes
- Used across all events for that aggregate

→ AbstractRepository's UUID constraint is a **feature**, not a limitation

### 2. Multiple Implementations Are Real

In event sourcing, you WILL have multiple repository implementations:
- EventStore for write model
- SQL for read models
- Cache for hot aggregates
- In-memory for testing

→ AbstractRepository's formal interface becomes essential

### 3. The CQRS Split

Command side (write):
```python
class WriteRepository(AbstractRepository[Aggregate, AggregateId]):
    """Command side: saves events to event store."""
    pass
```

Query side (read):
```python
class QueryRepository(SqlAlchemyRepository[ReadModel]):
    """Query side: efficient SQL queries on projections."""
    pass
```

→ Use BOTH patterns in the same system

### 4. Testing Event-Sourced Aggregates

With AbstractRepository:
```python
class InMemoryRepository(AbstractRepository[Aggregate, AggregateId]):
    """Test double that stores aggregates in memory."""
    def __init__(self):
        self.aggregates: dict[AggregateId, Aggregate] = {}

    def add(self, aggregate: Aggregate) -> None:
        self.aggregates[aggregate.id] = aggregate

    def get_by_id(self, aggregate_id: AggregateId) -> Aggregate | None:
        return self.aggregates.get(aggregate_id)
```

Easy to test because the interface is formal and clear.

### 5. Versioning and Schema Evolution

Event-sourced systems evolve:
- Event schemas change
- Aggregates get refactored
- Multiple versions coexist

AbstractRepository provides stable contract:
```python
# V1
class OrderRepositoryV1(AbstractRepository[OrderV1, OrderId]):
    pass

# V2 (different implementation, same interface)
class OrderRepositoryV2(AbstractRepository[OrderV2, OrderId]):
    pass
```

### 6. Domain Event Collection

AbstractRepository pattern works well with event collection:

```python
class EventSourcedRepository(AbstractRepository[T, TId]):
    def add(self, aggregate: T) -> None:
        events = aggregate.collect_events()  # Get uncommitted events
        self.event_store.save_events(aggregate.id, events)
        aggregate.clear_events()  # Mark events as committed
```

---

## Anti-Patterns to Avoid

### ❌ Don't Mix Patterns Inappropriately

**Bad:**
```python
class BatchRepository(AbstractRepository[Batch, str]):  # Batch uses str, not UUID
    pass
```

**Why:** Forces UUID constraint on non-UUID entity

**Good:**
```python
class BatchRepository(SqlAlchemyRepository[Batch]):  # Matches actual ID type
    pass
```

### ❌ Don't Create AbstractRepository Without Need

**Bad:**
```python
# Only one implementation, no plans for more
class UserRepository(AbstractRepository[User, UserId]):
    pass

class SqlUserRepository(UserRepository):
    # Only implementation, boilerplate for no benefit
    pass
```

**Why:** Premature abstraction (YAGNI violation)

**Good:**
```python
# Just use concrete repository until you need abstraction
class UserRepository(SqlAlchemyRepository[User]):
    pass
```

### ❌ Don't Over-Genericize Simple Models

**Bad:**
```python
class ConfigRepository(AbstractRepository[Config, ConfigId]):
    """Config is just key-value pairs, not a rich aggregate"""
    pass
```

**Why:** Config doesn't need DDD aggregate pattern

**Good:**
```python
class ConfigRepository(SqlAlchemyRepository[Config]):
    """Simple CRUD for configuration"""
    pass
```

---

## Migration Strategy: Simple → Rich Domain

### Phase 1: Start Simple
```python
# Simple models, simple repository
class OrderRepository(SqlAlchemyRepository[Order]):
    pass
```

### Phase 2: Add Domain Logic
```python
# Order gains behavior but still uses simple repo
class Order:
    def add_line(self, line: OrderLine) -> None:
        self.lines.append(line)

    def calculate_total(self) -> Money:
        return sum(line.total for line in self.lines)
```

### Phase 3: Introduce Events
```python
# Order becomes event-sourced aggregate
class Order(AggregateRoot[OrderId]):
    def add_line(self, line: OrderLine) -> None:
        self.lines.append(line)
        self.record_event(OrderLineAdded(self.id, line))
```

### Phase 4: Switch to AbstractRepository
```python
# Now need event store and read models
class OrderWriteRepository(AbstractRepository[Order, OrderId]):
    """Event store implementation"""
    pass

class OrderReadRepository(SqlAlchemyRepository[OrderReadModel]):
    """SQL projection for queries"""
    pass
```

**Key Insight:** You can keep SqlAlchemyRepository for read models even after adopting AbstractRepository for aggregates.

---

## Conclusion

### Core Takeaways

1. **SqlAlchemyRepository did NOT replace AbstractRepository** - they coexist by design for different purposes

2. **Neither is universally "better"** - choose based on your domain model complexity:
   - Simple models → SqlAlchemyRepository
   - Rich aggregates → AbstractRepository

3. **Event sourcing strongly favors AbstractRepository** because:
   - Multiple implementations are inevitable (EventStore + projections)
   - UUID identity is standard
   - Formal contracts prevent errors at system boundaries

4. **Use BOTH patterns in the same system** - AbstractRepository for write models, SqlAlchemyRepository for read models (CQRS)

5. **Start simple, evolve complexity** - Don't prematurely use AbstractRepository if SqlAlchemyRepository suffices

### For Your Event-Sourced Project

**Recommended Approach:**

```python
# Write side (commands / aggregates)
from repository import AbstractRepository

class OrderRepository(AbstractRepository[Order, OrderId]):
    """Event-sourced aggregate repository."""
    pass

# Read side (queries / projections)
from repository.repositories import SqlAlchemyRepository

class OrderSummaryRepository(SqlAlchemyRepository[OrderSummary]):
    """SQL projection for efficient queries."""
    pass
```

**Why This Works:**
- AbstractRepository's UUID constraint aligns with event sourcing
- Formal interface enables multiple event store implementations
- SqlAlchemyRepository keeps read models simple and fast
- Clear separation between command and query responsibilities

---

## References

- **Cosmic Python Book:** Architecture Patterns with Python by Harry Percival and Bob Gregory
- **Domain-Driven Design:** Eric Evans
- **Implementing Domain-Driven Design:** Vaughn Vernon
- **Event Sourcing Pattern:** Martin Fowler

---

**Last Updated:** November 21, 2025
**Maintainer:** Project Team
**Next Review:** When introducing first event-sourced aggregate
