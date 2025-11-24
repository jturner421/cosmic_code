import contextlib
import pathlib

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from db.session import Database
from domain.model import Batch
from repository import AbstractRepository

BASE_DIR = pathlib.Path(__file__).resolve().parent


@pytest.fixture()
class FakeRepository(AbstractRepository):
    """Fake repository for entities."""

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, entity: T):
        self._batches.add(entity)

    def get_by_id(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return self._batches

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([Batch(ref, sku, qty, eta)])


@pytest.fixture()
class FakeSession:
    """Fake session for entities."""

    committed = False

    def commit(self):
        self.committed = True


@pytest.fixture(scope="session")
def alembic_config():
    alembic_cfg = Config(str(BASE_DIR.parent / "alembic.ini"))
    return alembic_cfg


# --- Shared engine/connection from the Singleton -----------------------------
@pytest.fixture(scope="session")
def engine():
    return Database().engine


@pytest.fixture(scope="session")
def connection(engine):
    conn = engine.connect()
    conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def migrated_db(connection, alembic_config):
    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")
    connection.commit()
    db = Database()
    db._Session = sessionmaker(  # noqa: SLF001
        bind=connection,
        future=True,
        expire_on_commit=False,
        autocommit=False,
    )
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture(scope="session")
def sessionlocal():
    db = Database()
    return db.session


@pytest.fixture
def db_session(connection, migrated_db):
    """
    Transactional scope for DB tests; opt-in via the `db` marker or usefixtures.
    """
    from sqlalchemy.orm import Session

    outer = connection.begin()
    nested = connection.begin_nested()

    @event.listens_for(Session, "after_transaction_end")
    def _restart_savepoint(session, transaction):
        if transaction.nested and not session.get_bind().closed:
            session.begin_nested()

    try:
        yield
    finally:
        with contextlib.suppress(Exception):
            if outer.is_active:
                outer.rollback()
        event.remove(Session, "after_transaction_end", _restart_savepoint)


def pytest_collection_modifyitems(config, items):
    """
    Apply DB fixtures only to tests marked with @pytest.mark.db to avoid
    impacting pure domain tests.
    """
    db_marker = config.getoption("-m")
    for item in items:
        if "db" in item.keywords:
            item.fixturenames.append("db_session")
