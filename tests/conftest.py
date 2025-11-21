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
    # alembic_cfg.set_main_option("script_location", str(BASE_DIR.parent / "alembic"))
    return alembic_cfg


# --- Shared engine/connection from the Singleton -----------------------------
@pytest.fixture(scope="session")
def engine():
    # Use the singleton’s engine; it’s configured with StaticPool and check_same_thread=False
    return Database().engine


@pytest.fixture(scope="session")
def connection(engine):
    conn = engine.connect()
    conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def migrated_db(connection, alembic_config):
    alembic_config.attributes["connection"] = connection
    command.upgrade(alembic_config, "head")
    connection.commit()  # Ensure clean state for db_session fixture
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


@pytest.fixture(autouse=True)
def db_session(connection):
    """
    Start an outer transaction and a nested SAVEPOINT for each test.

    Any ORM Session you create via Database().session or Database().get_session()
    will participate because the singleton's sessionmaker is bound to `connection`.

    Tests can freely call commit(); after each inner transaction ends, we reopen
    the SAVEPOINT so the test can continue to commit.
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
    except Exception:  # noqa: S110
        pass
    finally:
        with contextlib.suppress(Exception):
            nested.rollback()
        with contextlib.suppress(Exception):
            outer.rollback()
        event.remove(Session, "after_transaction_end", _restart_savepoint)
