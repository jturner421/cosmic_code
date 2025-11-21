from db.session import Database
from model import Batch
from repository.repositories import SqlAlchemyRepository


def test_repository_can_save_a_batch():
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    with Database().get_session() as session:
        repo = SqlAlchemyRepository(session)
        repo.add(batch)
