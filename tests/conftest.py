import contextlib
import pathlib

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from db.session import Database

BASE_DIR = pathlib.Path(__file__).resolve().parent


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
