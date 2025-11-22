# Value Objects and ORM Compatibility Tradeoff

## The Problem

In Domain-Driven Design, value objects should be immutable. Python's `@dataclass(frozen=True)` provides this immutability. However, SQLAlchemy's ORM cannot work with frozen dataclasses when using imperative mapping with relationships.

## Technical Explanation

### Why SQLAlchemy Requires Mutability

When SQLAlchemy maps a class to a database table, it instruments each instance by adding a special attribute:

```python
instance._sa_instance_state = InstanceState(...)
```

This `_sa_instance_state` attribute tracks:
- Object lifecycle (pending, persistent, detached)
- Modified fields for dirty checking
- Relationship state and lazy loading
- Session association

### Why Frozen Dataclasses Block This

With `@dataclass(frozen=True)`, Python prevents ALL attribute assignment after `__init__` completes:

```python
@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

# Later, when SQLAlchemy tries to instrument:
instance._sa_instance_state = InstanceState(...)  # ❌ FrozenInstanceError
```

The frozen constraint is enforced at the Python level and cannot be bypassed by SQLAlchemy.

## The Tradeoff: `unsafe_hash=True`

### What We Changed

```python
# From:
@dataclass(frozen=True)
class OrderLine:
    ...

# To:
@dataclass(unsafe_hash=True)
class OrderLine:
    ...
```

### What This Means

- **Allows SQLAlchemy instrumentation**: Instances can have `_sa_instance_state` attached
- **Provides hashability**: Required for storing in `set[OrderLine]` (used in `Batch._allocations`)
- **Sacrifices enforcement**: No language-level immutability guarantee

The `unsafe_hash=True` parameter is called "unsafe" because it makes objects both:
1. **Mutable** - attributes can be changed
2. **Hashable** - can be stored in sets/dicts

This violates the general rule that mutable objects shouldn't be hashable (since their hash could change, breaking set/dict invariants).

## Alternatives Considered

### 1. Don't Persist Value Objects Directly (Orthodox DDD)

Store `OrderLine` data as JSON within the `Batch` aggregate:

```python
batches = Table(
    "batches",
    metadata,
    Column("allocations", JSON),  # Store OrderLines as serialized data
)
```

**Rejected because**:
- Loses relational querying capabilities
- Makes it harder to track order lines independently
- `OrderLineRepository` suggests we treat these as entities in practice

### 2. Separate Domain and Persistence Models

Create separate classes for domain logic and database mapping:

```python
# Domain model (pure, immutable)
@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

# Persistence model (ORM-friendly)
@dataclass(unsafe_hash=True)
class OrderLineDTO:
    orderid: str
    sku: str
    qty: int

    def to_domain(self) -> OrderLine:
        return OrderLine(self.orderid, self.sku, self.qty)
```

**Rejected because**:
- Significant boilerplate for translation between layers
- Extra complexity with minimal practical benefit in Python
- Python lacks compile-time type enforcement anyway

### 3. Use Different ORM Patterns

Options like SQLAlchemy's declarative mapping or alternative ORMs.

**Rejected because**:
- Still requires mutability for instrumentation
- Would require restructuring the entire persistence layer
- Imperative mapping keeps domain models cleaner

## The Pragmatic Decision

We accept **conceptual immutability** enforced by convention rather than **technical immutability** enforced by the language.

### Contract

- **Domain logic**: Treat `OrderLine` instances as immutable after creation
- **Never**: Assign to attributes after construction
- **Never**: Pass instances to code that might mutate them
- **Trust**: Team discipline over language enforcement

### Why This Works for Python

Python already lacks many compile-time guarantees:
- No true private attributes (just `_name` convention)
- No interface enforcement without ABC
- Dynamic typing allows any attribute assignment

Adding `unsafe_hash=True` aligns with Python's philosophy: "We're all consenting adults here."

## Guidelines for Maintaining Immutability

### DO:
```python
# Create new instances instead of modifying
line = OrderLine("order1", "LAMP", 10)
# If you need different values, create a new instance
new_line = OrderLine("order1", "LAMP", 15)
```

### DON'T:
```python
# Don't mutate existing instances
line = OrderLine("order1", "LAMP", 10)
line.qty = 15  # ❌ Violates the conceptual contract
```

### Code Review Checklist:
- [ ] No direct attribute assignment to `OrderLine` instances after creation
- [ ] Use factory functions or replace() if different values needed
- [ ] `OrderLine` instances only flow through read-only operations in domain logic

## Conclusion

The `unsafe_hash=True` tradeoff is a pragmatic engineering decision that:
1. Enables SQLAlchemy ORM integration without significant architecture changes
2. Maintains domain model clarity (no separate DTOs cluttering the codebase)
3. Relies on team discipline rather than language enforcement
4. Aligns with Python's dynamic nature and trust-based conventions

The risk of accidental mutation is mitigated by:
- Clear documentation of the immutability contract
- Code review practices
- Simple, focused value objects with minimal surface area
- The fact that SQLAlchemy only adds `_sa_instance_state`, not domain attributes
