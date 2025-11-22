# Task Completion Checklist
- Re-run impacted pytest targets (`make test` or narrower selections) after making changes.
- Apply formatting with `make black` when touching Python files, and run `mypy` when editing typed modules or interfaces.
- Regenerate and apply Alembic migrations (`alembic revision --autogenerate`, `alembic upgrade head`) whenever schema definitions change.
- For Docker-backed chapters, ensure services are up via `make up` before running integration/e2e tests.
- Review domain boundaries (entities, events, repositories) for consistency before finalizing changes.
- When done, summarize modifications, note any skipped validations, and suggest follow-up steps if necessary.