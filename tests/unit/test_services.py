import pytest

from domain.model import Batch, OrderLine
from repository import AbstractRepository
from service_layer.services import InvalidSku, allocate


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
    line = OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        allocate(line, repo, FakeSession())


def test_commits():
    line = OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()
    allocate(line, repo, session)
    assert session.committed is True
