import os

from sqlalchemy import text

from db.session import Database
from domain.model import Batch
from repository.repositories import BatchRepository

# pytestmark = pytest.mark.db

os.environ["TESTING"] = "1"


def test_repository_can_save_a_batch():
    Database.reset_instance()
    repo = BatchRepository(Database(url="sqlite:///:memory:"))
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    repo.add(batch)
    stmt = text("SELECT reference, sku, _purchased_qty, eta FROM batches")
    rows = repo.get(reference=batch.reference)
    # rows = session.execute(stmt).fetchall()
    assert list(rows) == ["batch1", "RUSTY-SOAPDISH", 100, None]


def test_repository_can_retrieve_a_batch():
    Database.reset_instance()
    repo = BatchRepository(Database(url="sqlite:///:memory:"))
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    repo.add(batch)

    retrieved = repo.get_by_reference("batch1")
    assert retrieved is not None
    assert retrieved.reference == "batch1"
    assert retrieved.sku == "RUSTY-SOAPDISH"
    assert retrieved._purchased_quantity == 100


def insert_order_line(session):
    session = Database(url="sqlite:///:memory:").session
    stmt = text(
        "INSERT INTO order_lines (sku, qty, orderid) "
        "VALUES ('GENERIC-SOFA', 12,'order1')",
    )
    session.execute(stmt)
    stmt = text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku")
    result = session.execute(
        stmt,
        {"orderid": "order1", "sku": "GENERIC-SOFA"},
    ).fetchall()
    [[orderline_id]] = result
    return orderline_id


# def insert_batch(session, batch_id, sku="GENERIC-SOFA", eta=None, qty=100):
#     stmt = text(
#         "INSERT INTO batches (reference, sku, _purchased_qty, eta) "
#         "VALUES (:reference, :sku, :qty, :eta)",
#     )
#     session.execute(
#         stmt,
#         {
#             "reference": batch_id,
#             "sku": sku,
#             "qty": qty,
#             "eta": eta,
#         },
#     )
#
#     stmt = text("SELECT id FROM batches WHERE reference=:reference")
#     result = session.execute(
#         stmt,
#         {"reference": batch_id},
#     ).fetchall()
#     [[batch_id]] = result
#     return batch_id
#
#
# def insert_allocation(session, orderline_id, batch_id):
#     stmt = text(
#         "INSERT INTO allocations (orderline_id, batch_id) "
#         "VALUES (:orderline_id, :batch_id)",
#     )
#     session.execute(stmt, {"orderline_id": orderline_id, "batch_id": batch_id})
#
#
# @pytest.mark.db
# def test_repository_can_retrieve_a_batch_with_allocations():
#     session = Database().session
#     orderline_id = insert_order_line(session)
#     batch1_id = insert_batch(session, "batch1")
#     insert_batch(session, "batch2")
#     insert_allocation(session, orderline_id, batch1_id)  # (2)
#
#     repo = BatchRepository(session)
#     retrieved = repo.get_by_reference("batch1")
#
#     expected = Batch("batch1", "GENERIC-SOFA", 100, None)
#     assert retrieved == expected  # Batch.__eq__ only compares reference  #(3)
#     assert retrieved.sku == expected.sku  # (4)
#     assert retrieved._purchased_quantity == expected._purchased_quantity
#     assert retrieved._allocations == {
#         OrderLine("order1", "GENERIC-SOFA", 12),
#     }
