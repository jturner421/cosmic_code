# Database Test Guide

- Mark tests that need database fixtures with `@pytest.mark.db`.
- DB fixtures (`engine`, `connection`, `migrated_db`, `db_session`) only attach to tests marked `db`; pure domain tests stay isolated.
- Typical usage:
  ```python
  import pytest

  @pytest.mark.db
  def test_repository_can_save_a_batch(sessionlocal):
      ...
  ```
- Run only DB tests: `pytest -m db`
- Run everything: `pytest`
