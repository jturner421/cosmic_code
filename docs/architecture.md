# Architecture Documentation

## Executive Summary

**Project:** Cosmic Python Allocation System
**Type:** Python Backend (DDD/Hexagonal Architecture)
**Repository:** Monolith
**Primary Framework:** FastAPI + SQLAlchemy
**Python Version:** 3.13

This project implements a learning-focused allocation system demonstrating Domain-Driven Design (DDD) and Hexagonal Architecture patterns from the book "Architecture Patterns with Python". The system manages inventory batches and order allocations with clean separation between domain logic, data access, and infrastructure concerns.

## Architecture Overview

### Architectural Style

**Hexagonal Architecture** (Ports and Adapters Pattern)

The project follows a layered architecture with dependencies pointing inward toward the domain:

```
┌─────────────────────────────────────────┐
│         External Systems (Future)        │
│         (API Clients, UI, etc.)         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Adapters (db/)                  │
│   (ORM Mappings, Session Management)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Ports (repository/)              │
│      (Repository Interfaces)             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Domain Core (domain/)             │
│   (Entities, Value Objects, Logic)       │
└──────────────────────────────────────────┘
```

**Key Principle:** Domain layer has zero dependencies on infrastructure.

### Design Patterns

1. **Repository Pattern** - Abstracts data access
2. **Domain-Driven Design** - Business logic in domain layer
3. **Imperative ORM Mapping** - Decouples domain from ORM
4. **Singleton Pattern** - Database session management
5. **Test-Driven Development** - Comprehensive test coverage

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.13 | Core runtime |
| Web Framework | FastAPI | 0.120.4+ | API framework (future use) |
| ORM | SQLAlchemy | 2.0.44+ | Database abstraction |
| Migration Tool | Alembic | 1.17.1+ | Schema versioning |
| Validation | Pydantic | 2.12.3+ | Data validation |
| Testing | pytest | 8.4.2+ | Test framework |
| Type Checking | mypy | 1.18.2+ | Static analysis |
| Database | SQLite | Bundled | Development database |

### Development Tools

- **uv** - Fast Python package manager
- **Black** - Code formatter (86 char line length)
- **Make** - Build automation
- **Travis CI** - Continuous integration

## Component Architecture

### Domain Layer (`domain/`)

**Responsibility:** Pure business logic with no infrastructure dependencies

#### Core Entities

**Batch** (`domain/model.py:Batch`)
- Represents inventory batch with SKU and quantity
- Manages allocations to order lines
- Business rules:
  - Cannot allocate_batch mismatched SKUs
  - Cannot over-allocate_batch quantity
  - Allocation is idempotent

**OrderLine** (`domain/model.py:OrderLine`)
- Represents order line item
- Immutable value-like entity (frozen dataclass)
- Used as hashable allocation reference

#### Domain Logic

**allocate_batch() Function** (`domain/model.py:allocate_batch`)
- Core allocation algorithm
- Sorts batches by ETA (current stock first)
- Returns allocated batch reference
- Raises `OutOfStockError` on failure

#### Base Classes

- **Entity** (`domain/entities.py`) - Base entity with ID-based equality
- **AggregateRoot** (`domain/entities.py`) - Marks aggregate roots
- **GenericUUID** (`domain/value_objects.py`) - UUID value object
- **DomainEvent** (`domain/events.py`) - Event sourcing support

### Repository Layer (`repository/`)

**Responsibility:** Data access abstraction

#### Repositories

**SqlAlchemyRepository[T]** (Generic Base)
- `add(entity: T)` - Add to session
- `get(id) -> T` - Retrieve by ID

**BatchRepository**
- Specialized for Batch entities
- Eager loads allocations relationship

**OrderLineRepository**
- Specialized for OrderLine entities

**Pattern Benefits:**
- Hides persistence complexity from domain
- Enables test doubles for unit testing
- Provides collection-like interface

### Database Layer (`db/`)

**Responsibility:** Infrastructure and persistence

#### ORM Mapping (`db/orm.py`)

**Strategy:** Imperative/Classical Mapping

**Tables:**
- `batches` - Batch inventory records
- `order_lines` - Order line items
- `allocations` - Many-to-many batch↔order line

**Mapping Configuration:**
```python
mapper_registry.map_imperatively(Batch, batches)
mapper_registry.map_imperatively(OrderLine, order_lines)
```

**Design Decision:** Imperative mapping keeps domain models clean of ORM annotations.

#### Session Management (`db/session.py`)

**Database Singleton:**
- One instance per process
- Configuration via `DATABASE_URL` environment variable
- Context manager for session lifecycle

**Session Lifecycle:**
```python
with Database().get_session() as session:
    repo = BatchRepository(session)
    # ... operations
    session.commit()
```

## Data Architecture

### Database Schema

```sql
CREATE TABLE batches (
    id INTEGER PRIMARY KEY,
    reference VARCHAR NOT NULL UNIQUE,
    sku VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    eta DATE
);

CREATE TABLE order_lines (
    id INTEGER PRIMARY KEY,
    orderid VARCHAR NOT NULL,
    sku VARCHAR NOT NULL,
    qty INTEGER NOT NULL
);

CREATE TABLE allocations (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER REFERENCES batches(id),
    orderline_id INTEGER REFERENCES order_lines(id)
);
```

### Entity Relationships

```
Batch 1───────* Allocation *───────1 OrderLine
   │                                      │
   │ reference (PK)                  orderid │
   │ sku                             sku     │
   │ quantity                        qty     │
   └ eta (nullable)                         ┘
```

### Data Flow

1. **Create Batch** → Insert into `batches` table
2. **Create OrderLine** → Insert into `order_lines` table
3. **Allocate** → Create record in `allocations` table
4. **Query Available** → Calculate: `batch.quantity - SUM(allocations)`

## API Design

**Current State:** No API layer implemented yet

**Future Design:** FastAPI REST endpoints

**Planned Endpoints:**
```
POST   /allocate_batch           # Allocate order line to batch
GET    /batches            # List all batches
GET    /batches/{ref}      # Get batch by reference
POST   /batches            # Create new batch
GET    /allocations        # List all allocations
```

## Development Workflow

### Local Development

1. **Setup:** Create venv, install dependencies
2. **Migrations:** `alembic upgrade head`
3. **Development:** TDD cycle (write test, implement, refactor)
4. **Testing:** `make test` or `pytest`
5. **Formatting:** `make black`
6. **Type Checking:** `mypy .`

### Testing Strategy

**Test Pyramid:**
```
         ┌──────────┐
         │   E2E    │  (Future)
         │  Tests   │
         ├──────────┤
         │Integration│  (@pytest.mark.db)
         │  Tests    │  Repository layer
         ├──────────┤
         │   Unit    │  Domain logic
         │  Tests    │  Fast, isolated
         └──────────┘
```

**Test Organization:**
- `test_allocate.py` - Domain logic (no database)
- `test_batches.py` - Batch entity behavior
- `test_repository.py` - Repository integration tests

**Fixture Management:**
- Database fixtures in `conftest.py`
- Use `@pytest.mark.db` for database-dependent tests
- In-memory SQLite for fast test execution

### Migration Workflow

1. Modify domain models
2. Create migration: `alembic revision --autogenerate -m "msg"`
3. Review generated migration
4. Apply: `alembic upgrade head`
5. Test with real data

## Deployment Architecture

**Current State:** Development-only (SQLite)

**Future Production:** (From book chapters 3+)
- Docker containers
- PostgreSQL database
- Docker Compose orchestration
- CI/CD via Travis CI

**Deployment Files:**
- `.travis.yml` - CI configuration
- `Makefile` - Build commands
- `alembic.ini` - Migration config

## Testing Architecture

### Test Isolation

**Domain Tests:**
- Pure Python objects
- No database required
- Fast execution (<100ms)

**Repository Tests:**
- Use test database
- Marked with `@pytest.mark.db`
- Isolated transactions

### Test Configuration

**pytest.ini:**
```ini
markers =
    db: tests that require database fixtures/session
```

**Test Execution:**
```bash
pytest              # All tests
pytest -m db        # Database tests only
pytest -m "not db"  # Exclude database tests
```

## Security Considerations

**Current State:** Learning project, minimal security

**Production Considerations:**
- Input validation via Pydantic models
- SQL injection protection via ORM
- Environment variable configuration (`.env`)

## Performance Considerations

### Database Performance

**Current:**
- SQLite (development)
- Eager loading for allocations
- Indexed on `reference` column

**Future Optimizations:**
- PostgreSQL for production
- Connection pooling
- Query optimization for batch allocation

### Application Performance

**Design Decisions:**
- Pure Python domain logic (fast)
- Minimal ORM overhead (imperative mapping)
- Batch operations where possible

## Scalability

**Current Design:** Single-process monolith

**Future Scaling Paths:**
1. **Vertical Scaling** - Increase server resources
2. **Read Replicas** - Separate read/write databases
3. **Event Sourcing** - Domain events for audit trail
4. **CQRS** - Separate read/write models
5. **Microservices** - Split by bounded context

## Known Limitations

1. **No API Layer** - FastAPI installed but not implemented
2. **SQLite Only** - Development database only
3. **Single Process** - No concurrency/parallelism
4. **No Authentication** - Learning project focus
5. **Limited Validation** - Basic Pydantic only

## Architecture Decision Records

### ADR-001: Imperative ORM Mapping

**Decision:** Use SQLAlchemy imperative mapping instead of declarative

**Rationale:**
- Keeps domain models pure Python
- No ORM framework dependencies in domain layer
- Enables true hexagonal architecture
- Easier to test domain logic in isolation

**Trade-offs:**
- More verbose mapping code
- Less IDE autocomplete for relationships
- Requires manual mapping configuration

### ADR-002: Repository Pattern

**Decision:** Implement repository pattern for data access

**Rationale:**
- Abstracts persistence details
- Enables unit testing with test doubles
- Follows DDD best practices
- Collection-like interface for domain objects

**Trade-offs:**
- Additional abstraction layer
- More code than direct ORM usage
- Learning curve for team

### ADR-003: Value Object Hashing

**Decision:** Use `unsafe_hash=True` on OrderLine frozen dataclass

**Rationale:**
- Enables use in sets (for allocations)
- OrderLine is logically immutable
- Required for allocation tracking

**Trade-offs:**
- "Unsafe" flag raises eyebrows
- Documented in `VALUE_OBJECTS_ORM_TRADEOFF.md`
- Requires developer awareness

## Diagram: System Context

```
┌─────────────────────────────────────────────────┐
│                                                 │
│        Cosmic Python Allocation System          │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Domain  │  │Repository│  │    DB    │      │
│  │  Logic   │◄─┤  Pattern │◄─┤   ORM    │      │
│  │          │  │          │  │          │      │
│  └──────────┘  └──────────┘  └─────┬────┘      │
│                                    │           │
│                                    ▼           │
│                              ┌──────────┐      │
│                              │ SQLite   │      │
│                              │   DB     │      │
│                              └──────────┘      │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Further Reading

- **Documentation:**
  - [Data Models](./data-models.md) - Detailed model documentation
  - [Source Tree Analysis](./source-tree-analysis.md) - Directory structure
  - [Development Guide](./development-guide.md) - Setup and workflows
  - [Repository Pattern Analysis](./REPOSITORY_PATTERN_ANALYSIS.md) - Existing analysis
  - [Value Objects ORM Tradeoff](./VALUE_OBJECTS_ORM_TRADEOFF.md) - Design decisions

- **Book:** "Architecture Patterns with Python" - https://www.cosmicpython.com
- **Repository:** https://github.com/python-leap/code

## Appendix: Key Files Reference

| File | Purpose | Layer |
|------|---------|-------|
| `domain/model.py` | Core domain models | Domain |
| `domain/entities.py` | Base entity classes | Domain |
| `repository/repositories.py` | Data access | Repository |
| `db/orm.py` | ORM mappings | Infrastructure |
| `db/session.py` | Session management | Infrastructure |
| `cosmicpython/versions/*.py` | Migrations | Infrastructure |
| `tests/test_*.py` | Test suite | Testing |
| `pyproject.toml` | Dependencies | Config |
| `alembic.ini` | Migration config | Config |