# Style and Conventions
- Follow Python DDD patterns from *Cosmic Python*: keep rich domain models in `domain/`, isolate persistence/session logic under `db/`, and treat migrations via Alembic.
- Use Pydantic dataclasses and typed value objects for domain entities; prefer explicit type hints throughout (reinforced by `mypy.ini`).
- Formatting: project uses `black` with line length 86 (see Makefile) and defaults to ASCII unless a dependency requires otherwise.
- Event-driven aggregate roots collect domain events via `register_event`/`collect_events`; prefer small helper methods rather than manipulating lists directly.
- Tests organized by layer (unit/integration/e2e); mirror naming patterns when adding new tests.
- Keep Alembic environment code compatible with SQLAlchemy 2 engine patterns (context manager scopes, `NullPool`, etc.).