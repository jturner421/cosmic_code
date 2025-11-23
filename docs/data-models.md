# Data Models Documentation

## Overview

This project implements a Domain-Driven Design (DDD) architecture for an allocation system. The domain models follow the Repository pattern with clean separation between domain logic and persistence.

## Domain Model

### Core Entities

#### Batch
**Location:** `domain/model.py:Batch`

Represents a batch of inventory with a specific SKU and quantity.

**Attributes:**
- `reference` (str): Unique batch identifier
- `sku` (str): Stock Keeping Unit identifier
- `quantity` (int): Total quantity in batch
- `eta` (date, optional): Estimated time of arrival for shipment batches
- `_allocations` (Set[OrderLine]): Internal set of allocated order lines

**Key Methods:**
- `allocate(line: OrderLine)`: Allocate an order line to this batch
- `deallocate(line: OrderLine)`: Remove an allocation
- `available_quantity`: Property calculating remaining available quantity

**Business Rules:**
- Cannot allocate if SKUs don't match
- Cannot allocate if insufficient quantity available
- Allocation is idempotent (same line can be allocated multiple times safely)

#### OrderLine
**Location:** `domain/model.py:OrderLine`

Represents a line item from an order.

**Attributes:**
- `orderid` (str): Order identifier
- `sku` (str): Stock Keeping Unit identifier
- `qty` (int): Quantity ordered

**Note:** Implemented as a frozen dataclass with `unsafe_hash=True` to allow usage in sets despite mutability concerns.

### Domain Functions

#### allocate()
**Location:** `domain/model.py:allocate`

**Signature:** `allocate(line: OrderLine, batches: List[Batch]) -> str`

Core allocation algorithm that:
1. Sorts batches by ETA (current stock first, then earliest shipments)
2. Attempts to allocate the order line to the first suitable batch
3. Returns the reference of the allocated batch
4. Raises `OutOfStockError` if no batch can fulfill the order

### Base Classes

#### Entity
**Location:** `domain/entities.py`

Abstract base class for domain entities providing:
- Identity management via `EntityId` type
- Equality based on ID rather than attributes

#### AggregateRoot
**Location:** `domain/entities.py`

Extends `Entity` to mark aggregate roots in DDD terminology.

#### GenericUUID
**Location:** `domain/value_objects.py`

UUID-based value object implementation.

### Domain Events

**Location:** `domain/events.py`

- `DomainEvent`: Base class for domain events
- `CompositeDomainEvent`: Supports composite event patterns

## Database Schema

### Tables

#### batches
**Columns:**
- `id`: Primary key
- `reference`: Unique batch reference (str)
- `sku`: Stock Keeping Unit (str)
- `quantity`: Total quantity (int)
- `eta`: Estimated time of arrival (date, nullable)

#### order_lines
**Columns:**
- `id`: Primary key
- `orderid`: Order identifier (str)
- `sku`: Stock Keeping Unit (str)
- `qty`: Quantity ordered (int)

#### allocations
**Columns:**
- `id`: Primary key
- `batch_id`: Foreign key → batches.id
- `orderline_id`: Foreign key → order_lines.id

**Represents:** Many-to-many relationship between batches and order lines.

## ORM Mapping

**Location:** `db/orm.py`

Uses SQLAlchemy's Imperative Mapping (Classical Mapping) approach:

- `mapper_registry`: Central registry for all mappings
- `metadata`: SQLAlchemy metadata object
- `perform_mapping()`: Configures mappings between domain objects and database tables

**Key Design Decision:** Mappings are configured lazily on first access to avoid circular import issues.

## Repository Pattern

### SqlAlchemyRepository[T]
**Location:** `repository/repositories.py`

Generic base repository providing:
- `add(entity: T)`: Add entity to session
- `get(id: EntityId) -> T`: Retrieve entity by ID

### BatchRepository
**Location:** `repository/repositories.py`

Specialized repository for Batch entities with:
- Custom `get()` implementation that eagerly loads allocations
- Handles ORM session management

### OrderLineRepository
**Location:** `repository/repositories.py`

Repository for OrderLine entities following the same pattern.

## Database Session Management

**Location:** `db/session.py`

### Database (Singleton)

Manages database connections and sessions with:
- Singleton pattern ensures one database instance per process
- `get_session()`: Context manager for session lifecycle
- `run_migrations()`: Alembic integration for schema migrations
- Environment-based configuration via `DATABASE_URL`

**Configuration:**
- Development/Production: `sqlite:///./cosmicpython.db`
- Testing: `sqlite:///:memory:` (configured in tests)

## Testing Database Markers

Tests requiring database access are marked with `@pytest.mark.db` decorator for selective test execution.

**Location:** `pytest.ini`
```ini
markers =
    db: tests that require database fixtures/session
```

## Migration Management

**Tool:** Alembic
**Location:** `cosmicpython/` directory
**Configuration:** `alembic.ini`

Migrations track schema changes for the batches, order_lines, and allocations tables.