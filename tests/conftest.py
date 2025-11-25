import pathlib
import subprocess
import time

import httpx
import pytest

import config

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


def pytest_collection_modifyitems(config, items):
    """
    Apply DB fixtures only to tests marked with @pytest.mark.db to avoid
    impacting pure domain tests.
    """
    db_marker = config.getoption("-m")
    for item in items:
        if "db" in item.keywords:
            item.fixturenames.append("db_session")
