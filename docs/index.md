# Cosmic Python - Project Documentation Index

**📚 Primary AI Reference for Development**

## Project Overview

- **Type:** Monolith
- **Primary Language:** Python 3.13
- **Architecture:** Domain-Driven Design (DDD) / Hexagonal Architecture
- **Framework:** FastAPI + SQLAlchemy

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Entry Point** | `main.py` (placeholder for future FastAPI app) |
| **Domain Models** | Batch, OrderLine in `domain/model.py` |
| **Database** | SQLite (3 tables: batches, order_lines, allocations) |
| **Testing** | pytest with `@pytest.mark.db` for database tests |
| **Migrations** | Alembic in `cosmicpython/versions/` |

## Generated Documentation

### Core Reference Documents

- **[Project Overview](./project-overview.md)** - Executive summary and quick start
- **[Architecture](./architecture.md)** - Complete architecture reference with diagrams and ADRs
- **[Data Models](./data-models.md)** - Domain models, database schema, ORM mappings, repositories
- **[Source Tree Analysis](./source-tree-analysis.md)** - Annotated directory structure and file purposes
- **[Development Guide](./development-guide.md)** - Setup, testing, migrations, and workflows

## Existing Documentation

### Developer-Written Analysis

- **[Repository Pattern Analysis](./REPOSITORY_PATTERN_ANALYSIS.md)** - Deep dive into repository implementation
- **[Value Objects ORM Tradeoff](./VALUE_OBJECTS_ORM_TRADEOFF.md)** - Design decisions for ORM mapping
- **[Batch SOLID Assessment](./batch_solid_assessment.md)** - SOLID principles assessment

### Test Documentation

- **[Test Allocate Overview](../tests/test_allocate_overview.md)** - Allocation algorithm test overview
- **[DB Tests Guide](../tests/DB_TESTS.md)** - Database testing strategy and patterns

## Getting Started

### First-Time Setup

```bash
# 1. Create virtual environment
python3.13 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Apply database migrations
alembic upgrade head

# 4. Run tests to verify setup
make test
```

### Common Commands

```bash
# Testing
make test           # Run all tests
make watch-tests    # Continuous testing
pytest -m db        # Database tests only
pytest -m "not db"  # Domain tests only

# Database
alembic upgrade head              # Apply migrations
alembic revision -m "message"     # Create migration
sqlite3 cosmicpython.db           # Inspect database

# Code Quality
make black          # Format code
mypy .             # Type check
```

## Architecture at a Glance

### Layer Structure

```
┌─────────────────────────────────┐
│    Domain Layer (domain/)        │  ← Pure business logic
│    - Batch, OrderLine entities   │    No framework dependencies
│    - allocate() function         │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│  Repository Layer (repository/)  │  ← Data access abstraction
│  - BatchRepository               │
│  - OrderLineRepository           │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│    Database Layer (db/)          │  ← Infrastructure
│    - ORM mappings (orm.py)       │
│    - Session management          │
└─────────────────────────────────┘
```

### Key Design Patterns

1. **Hexagonal Architecture** - Domain independence from infrastructure
2. **Repository Pattern** - Collection-like data access
3. **Imperative ORM Mapping** - Keeps domain models pure
4. **Singleton Database** - One connection per process

## Domain Model Summary

### Core Entities

**Batch** (`domain/model.py:Batch`)
- Inventory batch with reference, SKU, quantity, and optional ETA
- Manages allocations to order lines
- Business rule: Cannot over-allocate or mismatch SKUs

**OrderLine** (`domain/model.py:OrderLine`)
- Order line item with order ID, SKU, and quantity
- Frozen dataclass with `unsafe_hash=True` for set membership

### Allocation Logic

**allocate()** function (`domain/model.py:allocate`)
- Sorts batches by ETA (current stock first, then earliest shipments)
- Allocates order line to first suitable batch
- Returns batch reference or raises `OutOfStockError`

## Database Schema

### Tables

```sql
batches (reference, sku, quantity, eta)
    ↓
allocations (batch_id, orderline_id)  ← Many-to-many junction
    ↓
order_lines (orderid, sku, qty)
```

### Repositories

- **BatchRepository** - Eager loads allocations relationship
- **OrderLineRepository** - Standard CRUD operations

## Testing Strategy

### Test Categories

1. **Domain Tests** (`test_allocate.py`, `test_batches.py`)
   - Pure Python, no database required
   - Fast execution
   - Test business logic in isolation

2. **Repository Tests** (`test_repository.py`)
   - Marked with `@pytest.mark.db`
   - Test persistence behavior
   - Use database fixtures from `conftest.py`

### Running Tests

```bash
pytest tests/test_allocate.py       # Allocation algorithm tests
pytest tests/test_batches.py        # Batch entity tests
pytest tests/test_repository.py     # Repository integration tests
pytest -v                           # Verbose output
```

## Development Workflow

### TDD Cycle

1. **Red** - Write failing test
2. **Green** - Implement minimal code to pass
3. **Refactor** - Improve design
4. **Repeat** - Next feature

### Making Changes

1. **Domain Changes:**
   - Modify models in `domain/model.py`
   - Update tests first (TDD)
   - Run `pytest` to verify

2. **Database Changes:**
   - Modify domain models or ORM mappings
   - Create migration: `alembic revision --autogenerate -m "description"`
   - Review generated migration file
   - Apply: `alembic upgrade head`

3. **Repository Changes:**
   - Add methods to repository classes
   - Write integration tests with `@pytest.mark.db`
   - Test with real database

## Technology Stack Details

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.13 | Language runtime |
| FastAPI | 0.120.4+ | Web framework (future API layer) |
| SQLAlchemy | 2.0.44+ | ORM and database toolkit |
| Alembic | 1.17.1+ | Database migration tool |
| Pydantic | 2.12.3+ | Data validation |
| pytest | 8.4.2+ | Testing framework |
| mypy | 1.18.2+ | Static type checker |

### Configuration Files

- `pyproject.toml` - Project metadata and dependencies
- `alembic.ini` - Migration configuration
- `pytest.ini` - Test markers (db marker)
- `mypy.ini` - Type checking rules
- `.env` - Environment variables (DATABASE_URL)
- `Makefile` - Build and test commands

## File Locations Quick Reference

### Domain Layer
- Domain models: `domain/model.py`
- Base entities: `domain/entities.py`
- Value objects: `domain/value_objects.py`
- Domain events: `domain/events.py`

### Data Layer
- Repositories: `repository/repositories.py`
- ORM mappings: `db/orm.py`
- Session management: `db/session.py`

### Infrastructure
- Migrations: `cosmicpython/versions/`
- Migration config: `alembic.ini`
- Environment: `.env`

### Testing
- Domain tests: `tests/test_allocate.py`, `tests/test_batches.py`
- Repository tests: `tests/test_repository.py`
- Test fixtures: `tests/conftest.py`

## Key Design Decisions

### Why Imperative ORM Mapping?

Keeps domain models as pure Python classes without SQLAlchemy decorators or base classes. This enables:
- True hexagonal architecture
- Easier unit testing
- Framework independence

See: `docs/VALUE_OBJECTS_ORM_TRADEOFF.md`

### Why Repository Pattern?

Abstracts database access behind a collection-like interface. Benefits:
- Domain code doesn't know about database
- Easy to swap implementations (in-memory for tests)
- Follows DDD best practices

See: `docs/REPOSITORY_PATTERN_ANALYSIS.md`

### Why unsafe_hash on OrderLine?

Enables OrderLine (a frozen dataclass) to be used in sets for tracking allocations. While the flag name is "unsafe", the usage is safe because OrderLine is immutable.

See: `docs/VALUE_OBJECTS_ORM_TRADEOFF.md`

## Learning Path

This project follows the "Architecture Patterns with Python" book:

1. **Chapter 1-2:** Domain model and repository pattern (current state)
2. **Chapter 3+:** API layer with FastAPI
3. **Chapter 8+:** Domain events and message bus
4. **Chapter 12+:** CQRS pattern
5. **Chapter 13+:** Microservices architecture

Each chapter builds incrementally on previous patterns.

## Additional Resources

- **Book:** https://www.cosmicpython.com
- **Code Repository:** https://github.com/python-leap/code
- **Chapter Branches:** https://github.com/python-leap/code/branches/all
- **Exercises:** Branches follow `{chapter}_exercise` convention

## Documentation Generation

This documentation was generated by the **BMad Document Project** workflow on 2025-11-21 using deep scan mode.

**Scan Details:**
- Mode: Deep Scan (reads critical files)
- Project Type: Backend (Python, DDD/Hexagonal)
- Files Generated: 6 comprehensive documentation files

**Regeneration:**
To update this documentation after code changes, run:
```bash
/bmad:bmm:workflows:document-project
```

## Notes

- **API Layer:** FastAPI is installed but not yet implemented (placeholder in `main.py`)
- **Database:** Currently using SQLite; PostgreSQL planned for production
- **Learning Focus:** This is an educational project demonstrating architecture patterns

---

**Master Index Version:** 1.0
**Last Updated:** 2025-11-21
**Next Steps:** Review documentation and start building features with TDD