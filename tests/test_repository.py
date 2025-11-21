import pytest
import pytest
from sqlalchemy import text

from db.session import Database
from model import Batch
from repository.repositories import BatchRepository

pytestmark = pytest.mark.db


@pytest.mark.db
def test_repository_can_save_a_batch():
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    session = Database().session
    repo = BatchRepository(session)
    repo.add(batch)
    session.commit()
    stmt = text("SELECT reference, sku, _purchased_qty, eta FROM batches")
    rows = session.execute(stmt).fetchall()
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


@pytest.mark.db
def test_repository_can_retrieve_a_batch():
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    session = Database().session
    repo = BatchRepository(session)
    repo.add(batch)
    session.commit()

    retrieved = repo.get_by_reference("batch1")
    assert retrieved is not None
    assert retrieved.reference == "batch1"
    assert retrieved.sku == "RUSTY-SOAPDISH"
    assert retrieved._purchased_quantity == 100
