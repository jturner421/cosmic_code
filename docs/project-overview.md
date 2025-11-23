# Project Overview

## Project Summary

**Name:** Cosmic Python Allocation System
**Type:** Learning/Modernization Project (Backend)
**Repository Type:** Monolith
**Primary Language:** Python 3.13
**Architecture:** Domain-Driven Design (DDD) / Hexagonal Architecture

## Purpose

This project serves as a practical implementation of architecture patterns from the book "Architecture Patterns with Python" (https://www.cosmicpython.com). It demonstrates best practices for building maintainable, testable backend systems using Domain-Driven Design principles.

The system models a warehouse allocation system where inventory batches are allocated to customer order lines, showcasing:
- Clean architecture with separated concerns
- Repository pattern for data access
- Test-driven development practices
- Database migrations with Alembic

## Quick Reference

### Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.13 |
| **Web Framework** | FastAPI 0.120.4+ (future use) |
| **ORM** | SQLAlchemy 2.0.44+ |
| **Database** | SQLite (dev), PostgreSQL (future prod) |
| **Migrations** | Alembic 1.17.1+ |
| **Testing** | pytest 8.4.2+ |
| **Validation** | Pydantic 2.12.3+ |
| **Type Checking** | mypy 1.18.2+ |

### Architecture Pattern

**Hexagonal Architecture** (Ports and Adapters)

```
Domain Layer (domain/)
    ↑
Repository Layer (repository/)
    ↑
Database Layer (db/)
```

**Key Principle:** Business logic is independent of infrastructure.

### Project Statistics

- **Domain Models:** 2 (Batch, OrderLine)
- **Database Tables:** 3 (batches, order_lines, allocations)
- **Repositories:** 2 (BatchRepository, OrderLineRepository)
- **Test Files:** 3 test suites
- **Documentation:** 5 generated docs + 4 existing docs

## Repository Structure

### Directory Layout

```
cosmicpython/
├── domain/              # Pure business logic
├── repository/          # Data access abstraction
├── db/                  # ORM and session management
├── cosmicpython/        # Alembic migrations
├── tests/               # Comprehensive test suite
└── docs/                # Project documentation
```

### Key Components

**Domain Layer:**
- Batch entity with allocation logic
- OrderLine value-like entity
- Pure Python with zero infrastructure dependencies

**Repository Layer:**
- Repository pattern implementation
- Abstracts database access from domain

**Database Layer:**
- SQLAlchemy imperative mappings
- Singleton session management
- Alembic migration versioning

## Getting Started

### Quick Setup

```bash
# 1. Create virtual environment
python3.13 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Run migrations
alembic upgrade head

# 4. Run tests
make test
```

### Entry Points

- **Application:** `main.py` (currently placeholder)
- **Tests:** `pytest` or `make test`
- **Migrations:** `alembic` commands

## Core Functionality

### Domain Model

**Allocation System:**
1. Create batches of inventory (reference, SKU, quantity, ETA)
2. Create order lines (order ID, SKU, quantity)
3. Allocate order lines to batches
4. Track available quantity

**Business Rules:**
- Allocate to current stock before shipments
- Prefer earlier shipment dates
- Cannot over-allocate quantities
- Cannot allocate mismatched SKUs

### Database Schema

```
batches ──┐
          ├── allocations ──┤
order_lines ──┘
```

- **batches:** Inventory records with SKU and quantity
- **order_lines:** Customer order line items
- **allocations:** Many-to-many linking table

## Documentation Structure

### Generated Documentation

Comprehensive AI-generated documentation for development:

1. **[Architecture](./architecture.md)** - Complete architecture reference
2. **[Data Models](./data-models.md)** - Domain models and database schema
3. **[Source Tree Analysis](./source-tree-analysis.md)** - Directory structure explained
4. **[Development Guide](./development-guide.md)** - Setup and workflows
5. **[Project Overview](./project-overview.md)** - This document

### Existing Documentation

Developer-written analysis and notes:

1. **[Repository Pattern Analysis](./REPOSITORY_PATTERN_ANALYSIS.md)** - Pattern implementation analysis
2. **[Value Objects ORM Tradeoff](./VALUE_OBJECTS_ORM_TRADEOFF.md)** - ORM mapping decisions
3. **[Batch SOLID Assessment](./batch_solid_assessment.md)** - SOLID principles review
4. **[Test Overview](../tests/test_allocate_overview.md)** - Allocation test documentation
5. **[DB Tests](../tests/DB_TESTS.md)** - Database testing strategy

## Development Workflow

### Test-Driven Development

1. **Write Test** - Define expected behavior
2. **Implement** - Write minimal code to pass
3. **Refactor** - Improve design
4. **Repeat** - Next feature

**Test Commands:**
```bash
make test           # Run all tests
make watch-tests    # Continuous testing
pytest -m db        # Database tests only
pytest -m "not db"  # Domain tests only
```

### Code Quality

```bash
make black    # Format code
mypy .        # Type check
```

### Database Migrations

```bash
alembic upgrade head                    # Apply migrations
alembic revision -m "description"       # Create migration
alembic revision --autogenerate -m "x"  # Auto-generate from models
```

## Design Principles

### Clean Architecture

- **Dependencies point inward** toward domain
- **Domain has zero infrastructure dependencies**
- **Repository pattern** abstracts data access
- **Imperative ORM mapping** keeps models pure

### Test Pyramid

```
         E2E (Future)
       ┌──────────┐
       │ Integration│
       ├──────────┤
       │   Unit     │  ← Focus here
       └──────────┘
```

Most tests are fast domain logic tests. Integration tests cover repository layer.

### Domain-Driven Design

- **Entities:** Objects with identity (Batch)
- **Value Objects:** Immutable data (OrderLine)
- **Aggregates:** Consistency boundaries
- **Repositories:** Collection-like data access
- **Domain Events:** Future event sourcing support

## Future Roadmap

Based on book chapters:

1. **API Layer** - FastAPI REST endpoints (Ch 3+)
2. **Event Sourcing** - Domain events and handlers (Ch 8+)
3. **CQRS** - Separate read/write models (Ch 12+)
4. **Microservices** - Service decomposition (Ch 13+)

## Learning Resources

- **Book:** "Architecture Patterns with Python" - https://www.cosmicpython.com
- **Code Repository:** https://github.com/python-leap/code
- **Chapter Branches:** Each chapter has complete working code
- **Exercises:** Practice branches for hands-on learning

## Key Takeaways

### What This Project Demonstrates

✓ **Hexagonal Architecture** - Clean separation of concerns
✓ **Repository Pattern** - Data access abstraction
✓ **Test-Driven Development** - Comprehensive test coverage
✓ **Domain-Driven Design** - Business logic in domain layer
✓ **Database Migrations** - Version-controlled schema evolution
✓ **Type Safety** - Static typing with mypy

### Production-Ready Practices

- Environment-based configuration (`.env`)
- Migration management (Alembic)
- Comprehensive testing (pytest)
- Code formatting (Black)
- Type checking (mypy)
- CI/CD ready (`.travis.yml`)

## Contributing

This is a learning project following the book's progression. Each chapter is developed on its own branch:

- `chapter_01` - Domain model
- `chapter_02` - Repository pattern
- `chapter_03` - API layer (Flask/FastAPI)
- etc.

## Contact & Support

- **Issues:** GitHub repository issues
- **Book:** Official Cosmic Python book and forums
- **Documentation:** See `docs/` folder for detailed guides

---

**Last Updated:** 2025-11-21
**Documentation Generated by:** BMad Document Project Workflow