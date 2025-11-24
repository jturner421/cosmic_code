# Development Guide

## Overview

This guide provides setup instructions, development workflows, and testing strategies for the Cosmic Python allocation system. The project demonstrates Domain-Driven Design patterns from the "Architecture Patterns with Python" book.

## Prerequisites

### Required Software
- **Python 3.13** (specified in `.python-version`)
- **pip** or **uv** (package manager)
- **SQLite** (bundled with Python)

### Optional Software
- **Docker** with docker-compose (for chapters 3+ from the book)
- **make** (for using Makefile commands)

## Initial Setup

### 1. Clone and Navigate
```bash
git checkout feature/ch1-local  # Or your desired chapter branch
cd /path/to/cosmicpython
```

### 2. Create Virtual Environment
```bash
python3.13 -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -e .
# or using uv
uv sync
```

**Dependencies installed:**
- `fastapi[standard]>=0.120.4` - Web framework (future use)
- `sqlalchemy>=2.0.44` - ORM for database access
- `alembic>=1.17.1` - Database migration tool
- `pydantic>=2.12.3` - Data validation
- `python-dotenv>=1.2.1` - Environment variable management
- `mypy>=1.18.2` - Static type checker
- `pytest>=8.4.2` - Testing framework (dev dependency)

## Environment Configuration

### Database Configuration
Create/edit `.env` file in project root:

```bash
# Development/Production - file-based SQLite
DATABASE_URL=sqlite:///./cosmicpython.db

# Testing - in-memory SQLite (configure in tests)
# DATABASE_URL=sqlite:///:memory:
```

**Database Files:**
- `cosmicpython.db` - Main database file (auto-created)
- `tests/cosmicpython.db` - Test database (auto-created during tests)

## Database Migrations

### Running Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

### Creating New Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description of changes"
```

**Migration Files Location:** `cosmicpython/versions/`

**Configuration:** `alembic.ini`

## Development Workflow

### Running Tests

#### Using Makefile (Recommended)
```bash
# Run all tests with short traceback
make test

# Watch for file changes and re-run tests
make watch-tests
```

#### Using pytest Directly
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_allocate.py

# Run specific test function
pytest tests/test_allocate.py::test_prefers_earlier_batches

# Run only database tests
pytest -m db

# Run tests excluding database tests
pytest -m "not db"
```

### Test Organization

**Test Categories:**
1. **Domain Logic Tests** (`test_allocate.py`, `test_batches.py`)
   - No database required
   - Fast execution
   - Test pure business logic

2. **Repository Tests** (`test_repository.py`)
   - Marked with `@pytest.mark.db`
   - Require database fixtures
   - Test persistence layer

**Test Fixtures:** Defined in `tests/conftest.py`

### Code Formatting

```bash
# Format all Python files using Black
make black
```

**Configuration:** Black uses 86 character line length (specified in Makefile)

### Type Checking

```bash
# Run mypy type checker
mypy .
```

**Configuration:** `mypy.ini`

## Project Structure Explained

### Domain Layer (`domain/`)
- **Pure business logic** - no dependencies on infrastructure
- Contains: Entities, Value Objects, Domain Events
- Entry point: `domain/model.py` (Batch, OrderLine, allocate_batch function)

### Repository Layer (`repository/`)
- **Data access abstraction** - Repository pattern implementation
- Provides collection-like interface to domain objects
- Hides persistence details from domain layer

### Database Layer (`db/`)
- **Infrastructure concerns** - ORM mappings and session management
- `orm.py` - SQLAlchemy imperative mappings
- `session.py` - Database singleton and session lifecycle

### Test Layer (`tests/`)
- Comprehensive test coverage
- Uses pytest fixtures for database setup
- Separated by concern (domain vs. persistence)

## Common Development Tasks

### Adding a New Domain Model

1. Define model in `domain/model.py`:
```python
@dataclass
class MyEntity:
    id: EntityId
    name: str
    # ... other fields
```

2. Add ORM mapping in `db/orm.py`:
```python
my_entities = Table(
    'my_entities',
    metadata,
    Column('id', String, primary_key=True),
    Column('name', String),
)

# Add to perform_mapping():
mapper_registry.map_imperatively(MyEntity, my_entities)
```

3. Create migration:
```bash
alembic revision --autogenerate -m "add my_entity table"
alembic upgrade head
```

4. Add repository in `repository/repositories.py`:
```python
class MyEntityRepository(SqlAlchemyRepository[MyEntity]):
    pass
```

5. Write tests in `tests/test_my_entity.py`

### Running the Application

**Current State:** No API endpoints yet (placeholder in `main.py`)

**Future:** Will contain FastAPI application

```python
# main.py will eventually contain:
from fastapi import FastAPI
app = FastAPI()

@app.post("/allocate_batch")
def allocate_endpoint(...):
    # Implementation
    pass
```

## Testing Strategy

### Test Pyramid

1. **Unit Tests (Domain Logic)** - Majority of tests
   - Fast, isolated, no I/O
   - Test business rules and domain logic
   - Example: `test_allocate.py`

2. **Integration Tests (Repository Layer)** - Moderate coverage
   - Test database interactions
   - Use `@pytest.mark.db` marker
   - Example: `test_repository.py`

3. **End-to-End Tests** - (Future)
   - Will test complete API workflows
   - Not yet implemented

### Writing Tests

```python
# Domain test (no database)
def test_allocation_logic():
    batch = Batch("batch-001", "SMALL-TABLE", 20)
    line = OrderLine("order-123", "SMALL-TABLE", 5)

    batch.allocate_batch(line)

    assert batch.available_quantity == 15


# Repository test (requires database)
@pytest.mark.db
def test_repository_persistence(session):
    repo = BatchRepository(session)
    batch = Batch("batch-001", "SMALL-TABLE", 20)

    repo.add(batch)
    session.commit()

    retrieved = repo.get("batch-001")
    assert retrieved.reference == "batch-001"
```

## Debugging

### Database Inspection

```bash
# Open SQLite database
sqlite3 cosmicpython.db

# View tables
.tables

# Query data
SELECT * FROM batches;
SELECT * FROM order_lines;
SELECT * FROM allocations;

# Exit
.quit
```

### Common Issues

**Issue:** `ModuleNotFoundError` when running tests
**Solution:** Ensure you're in the virtual environment and ran `pip install -e .`

**Issue:** Database locked errors
**Solution:** Close any open SQLite connections/browsers

**Issue:** Migration conflicts
**Solution:** Check `alembic current` and resolve version conflicts

## Development Best Practices

1. **Test-Driven Development (TDD)**
   - Write tests before implementation
   - Follow red-green-refactor cycle
   - Keep tests fast and isolated

2. **Domain-Driven Design**
   - Keep domain models pure (no framework dependencies)
   - Use repositories for data access
   - Implement business rules in domain layer

3. **Database Migrations**
   - Always create migrations for schema changes
   - Test migrations on sample data
   - Never edit applied migrations

4. **Code Quality**
   - Run `make black` before committing
   - Run `mypy .` to check types
   - Ensure all tests pass: `make test`

## Continuous Integration

**Configuration:** `.travis.yml` (Travis CI)

**CI Pipeline:**
1. Install dependencies
2. Run migrations
3. Run test suite
4. Check code formatting
5. Run type checker

## Additional Resources

- **Book:** "Architecture Patterns with Python" (https://www.cosmicpython.com)
- **Repository:** https://github.com/python-leap/code
- **Chapter Branches:** Each chapter has its own branch with complete code
- **Exercises:** Branches follow `{chapter_name}_exercise` convention

## Getting Help

- Check existing documentation in `docs/` folder
- Review test files for usage examples
- Consult the book chapters for detailed explanations
- Check the project's GitHub issues

## Quick Reference Commands

```bash
# Setup
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e .

# Development
make test          # Run all tests
make watch-tests   # Continuous testing
make black         # Format code
mypy .            # Type check

# Database
alembic upgrade head         # Apply migrations
alembic revision -m "msg"    # Create migration
sqlite3 cosmicpython.db      # Inspect database

# Testing
pytest                  # All tests
pytest -v              # Verbose
pytest -m db           # Database tests only
pytest -m "not db"     # Non-database tests only
```