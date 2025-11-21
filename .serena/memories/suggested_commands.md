# Suggested Commands
- `uv pip sync` or `pip install -r requirements.txt` (if not using the provided `.venv`) to install dependencies; project targets Python 3.13.
- `make build` / `make up` (from README) to build and start docker services for integration/e2e scenarios.
- `make test` (or `pytest --tb=short`) for the full automated test suite; use `make unit`, `make integration`, or `make e2e` to run subsets when defined.
- `make watch-tests` to rerun pytest automatically on file changes.
- `black -l 86 $(find * -name '*.py')` (via `make black`) to format code consistently.
- `alembic revision --autogenerate -m "description"` and `alembic upgrade head` for schema migrations (configured via `alembic.ini`).
- `mypy` (configured by `mypy.ini`) to run static type checking where desired.