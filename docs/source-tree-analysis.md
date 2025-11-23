# Source Tree Analysis

## Project Structure Overview

This project follows a **Domain-Driven Design (DDD)** architecture with clear separation of concerns. The structure emphasizes domain logic independence from infrastructure concerns.

```
cosmicpython/
├── domain/                  # Domain Layer - Core business logic
│   ├── model.py            # Domain models: Batch, OrderLine, allocate()
│   ├── entities.py         # Base entity classes (Entity, AggregateRoot)
│   ├── value_objects.py    # Value objects (GenericUUID)
│   └── events.py           # Domain events
│
├── repository/              # Repository Pattern - Data access abstraction
│   └── repositories.py     # BatchRepository, OrderLineRepository
│
├── db/                      # Database Layer - Infrastructure/Persistence
│   ├── orm.py              # SQLAlchemy ORM mappings
│   └── session.py          # Database session management
│
├── cosmicpython/            # Alembic Migrations
│   ├── env.py              # Migration environment configuration
│   ├── script.py.mako      # Migration script template
│   └── versions/           # Migration version files
│
├── tests/                   # Test Suite
│   ├── test_allocate.py    # Domain logic tests (allocation algorithm)
│   ├── test_batches.py     # Batch entity tests
│   ├── test_repository.py  # Repository pattern tests (marked @pytest.mark.db)
│   ├── conftest.py         # Pytest fixtures and configuration
│   ├── DB_TESTS.md         # Database testing documentation
│   └── test_allocate_overview.md  # Test overview documentation
│
├── docs/                    # Project Documentation
│   ├── data-models.md      # Generated: Data models and database schema
│   ├── REPOSITORY_PATTERN_ANALYSIS.md  # Existing: Repository pattern analysis
│   ├── VALUE_OBJECTS_ORM_TRADEOFF.md  # Existing: ORM design decisions
│   └── batch_solid_assessment.md      # Existing: SOLID principles assessment
│
├── pyproject.toml           # Project configuration and dependencies
├── alembic.ini              # Alembic migration configuration
├── pytest.ini               # Pytest configuration (db markers)
├── mypy.ini                 # Type checking configuration
├── Makefile                 # Build and test commands
├── main.py                  # Application entry point (placeholder)
├── .env                     # Environment configuration (DATABASE_URL)
└── README.md                # Project readme and setup instructions
```

## Critical Directories

### `domain/` - Domain Layer
**Purpose:** Contains pure business logic independent of infrastructure

**Key Files:**
- `model.py` - Core domain models (Batch, OrderLine) and allocation logic
- `entities.py` - Base classes for domain entities with identity management
- `value_objects.py` - Immutable value objects
- `events.py` - Domain event definitions for event-driven patterns

**Design Principle:** No dependencies on database or external frameworks

### `repository/` - Repository Pattern
**Purpose:** Abstract data access layer following the Repository pattern

**Key Files:**
- `repositories.py` - Concrete repository implementations (BatchRepository, OrderLineRepository)

**Pattern:** Provides collection-like interface to domain objects, hiding persistence details

### `db/` - Database/Infrastructure Layer
**Purpose:** Handle all database and ORM concerns

**Key Files:**
- `orm.py` - SQLAlchemy mappings (imperative/classical mapping style)
- `session.py` - Database singleton and session management

**Design Decision:** Uses imperative mapping to keep domain models free of ORM concerns

### `cosmicpython/` - Database Migrations
**Purpose:** Alembic migration scripts for schema versioning

**Key Files:**
- `env.py` - Migration environment configuration
- `versions/` - Timestamped migration files

**Note:** Migration directory named after project (convention from book)

### `tests/` - Test Suite
**Purpose:** Comprehensive test coverage of domain logic and persistence

**Key Files:**
- `test_allocate.py` - Pure domain logic tests (no database)
- `test_batches.py` - Batch entity behavior tests
- `test_repository.py` - Repository integration tests (requires database)
- `conftest.py` - Shared test fixtures

**Test Organization:**
- Tests marked with `@pytest.mark.db` require database fixtures
- Domain logic tests are fast and database-independent
- Repository tests verify persistence behavior

## Architecture Pattern

**Primary Pattern:** Hexagonal Architecture / Ports and Adapters

**Layers:**
1. **Domain Core** (`domain/`) - Business logic
2. **Ports** (`repository/`) - Interfaces for external systems
3. **Adapters** (`db/`) - Concrete implementations for databases

**Dependencies Flow:** Infrastructure → Repository → Domain (dependencies point inward)

## Entry Points

**Main Entry Point:** `main.py`
- Currently a placeholder
- Future: Will contain FastAPI application or CLI commands

**Test Entry Point:** Via pytest
- Run all tests: `make test` or `pytest`
- Run database tests only: `pytest -m db`

## Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python project metadata, dependencies (FastAPI, SQLAlchemy, Alembic, pytest) |
| `alembic.ini` | Alembic configuration, migration location |
| `pytest.ini` | Pytest markers (db marker for database tests) |
| `mypy.ini` | Type checking configuration |
| `.env` | Environment variables (DATABASE_URL) |
| `Makefile` | Development commands (test, watch-tests, black) |

## Database Files

- `cosmicpython.db` - SQLite database file (gitignored in production)
- `identifier.sqlite` - Additional SQLite file (purpose unclear)
- `tests/cosmicpython.db` - Test database instance

## Documentation Structure

**Generated Documentation:** (AI-assisted development reference)
- `docs/data-models.md` - Comprehensive data model documentation

**Existing Documentation:** (Developer-written analysis)
- `docs/REPOSITORY_PATTERN_ANALYSIS.md` - Analysis of repository pattern implementation
- `docs/VALUE_OBJECTS_ORM_TRADEOFF.md` - Discussion of ORM mapping decisions
- `docs/batch_solid_assessment.md` - SOLID principles assessment
- `tests/DB_TESTS.md` - Database testing strategy
- `tests/test_allocate_overview.md` - Overview of allocation tests

## Special Files

- `model_uml.puml` - PlantUML diagram source
- `uv.lock` - UV package manager lock file
- `.python-version` - Python version specification (3.13)

## Development Workflow

1. **Install Dependencies:** `pip install -e .` (or use uv)
2. **Run Tests:** `make test`
3. **Apply Migrations:** `alembic upgrade head`
4. **Watch Tests:** `make watch-tests` (continuous testing)
5. **Format Code:** `make black`

## Key Integration Points

This is a **monolith** application - all components run in a single process.

**Database Integration:**
- Domain models → Mapped via `db/orm.py`
- Accessed through repositories in `repository/`
- Session managed by `db/session.py` (singleton pattern)

**Test Integration:**
- Domain tests require no database
- Repository tests use `@pytest.mark.db` and database fixtures from `conftest.py`