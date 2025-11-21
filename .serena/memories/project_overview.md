# Cosmic Python Project Overview
- Purpose: reference implementation derived from the *Architecture Patterns with Python* ("Cosmic Python") book; demonstrates DDD-style domain, persistence, and FastAPI service layers.
- Core tech: Python 3.13, FastAPI, SQLAlchemy 2.x, Alembic for migrations, Pydantic for typed domain/value objects, pytest for testing, mypy for optional static checks.
- High-level structure:
  - `domain/`: domain model entities, value objects, domain events, repository abstractions, and use-case orchestration.
  - `db/`: SQLAlchemy ORM registry and session helpers.
  - `cosmicpython/`: Alembic migration environment plus generated revisions.
  - `tests/`: unit/integration/e2e suites matching the book's chapter layout.
  - `main.py`, `model.py`: application entry points / adapters for running chapters or experiments.
- Typical workflow: iterate on domain & persistence modules, add/adjust Alembic migrations, run pytest suites, and exercise HTTP layer through FastAPI when present.