import contextlib
import pathlib
import subprocess
import time
from datetime import date

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

import config
from db.session import Database
from repository.repositories import BatchRepository
from service_layer.services import add_batch

BASE_DIR = pathlib.Path(__file__).resolve().parent


def wait_for_webapp_to_come_up():
    """Poll the API until it responds or timeout after 10 seconds."""
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                return response
        except httpx.ConnectError:
            time.sleep(0.5)
    pytest.fail("API never came up")


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


@pytest.fixture
def api_server():
    """Start uvicorn server for e2e testing."""
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "localhost", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    wait_for_webapp_to_come_up()
    yield
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture
def add_stock(db_session):
    """Fixture to add batches directly to database for test setup."""

    def _add_stock(batches):
        session = Database().session
        repo = BatchRepository(session)
        for ref, sku, qty, eta in batches:
            eta_date = date.fromisoformat(eta) if eta else None
            add_batch(ref, sku, qty, eta_date, repo, session)

    return _add_stock


def pytest_collection_modifyitems(config, items):
    """
    Apply DB fixtures only to tests marked with @pytest.mark.db to avoid
    impacting pure domain tests.
    """
    db_marker = config.getoption("-m")
    for item in items:
        if "db" in item.keywords:
            item.fixturenames.append("db_session")
