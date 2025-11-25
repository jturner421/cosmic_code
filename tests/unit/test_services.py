import pytest

from domain.model import Batch
from repository import AbstractRepository
from service_layer.services import InvalidSku, add_batch, allocate


class FakeRepository(AbstractRepository):
    """Fake repository for entities."""

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, entity):
        self._batches.add(entity)

    def get_by_id(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return self._batches

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([Batch(ref, sku, qty, eta)])


class FakeSession:
    """Fake session for entities."""

    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("b1", "AREALSKU", 100, None, repo, session)
    with pytest.raises(InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)
    allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True
