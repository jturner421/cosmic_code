import pathlib
import subprocess
import time
from datetime import date

import httpx
import pytest
from sqlalchemy import text

import config
from db.session import Database

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
def add_stock():
    """Fixture to add batches directly to database for test setup."""
    url = config.get_postgres_uri()
    db = Database(url=url)
    session = db.session
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            eta_date = date.fromisoformat(eta) if eta else None
            stmt = text(
                "INSERT INTO batches (reference, sku,_purchased_qty, eta)"
                " VALUES (:ref, :sku, :qty, :eta)",
            )
            session.execute(stmt, {"ref": ref, "sku": sku, "qty": qty, "eta": eta})
            stmt2 = text(
                "SELECT id FROM batches WHERE reference=:ref AND sku=:sku",
            )
            [[batch_id]] = session.execute(stmt2, {"ref": ref, "sku": sku}).fetchall()
            batches_added.add(batch_id)
            skus_added.add(sku)
        session.commit()

    yield _add_stock

    for batch_id in batches_added:
        stmt = text("DELETE FROM allocations WHERE batch_id=:batch_id")
        session.execute(stmt, {"batch_id": batch_id})

    for sku in skus_added:
        stmt = text(
            "DELETE FROM order_lines WHERE sku=:sku",
        )
        session.execute(stmt, {"sku": sku})
    session.commit()


def pytest_collection_modifyitems(config, items):
    """
    Apply DB fixtures only to tests marked with @pytest.mark.db to avoid
    impacting pure domain tests.
    """
    db_marker = config.getoption("-m")
    for item in items:
        if "db" in item.keywords:
            item.fixturenames.append("db_session")
