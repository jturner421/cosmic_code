import pytest

from domain.model import Batch, OrderLine
from service_layer.services import allocate, InvalidSku


def test_returns_allocation(FakeRepository, FakeSession):
    line = OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku(FakeRepository, FakeSession):
    line = OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        allocate(line, repo, FakeSession())


def test_commits(FakeRepository, FakeSession):
    line = OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    allocate(line, repo, session)
    assert session.committed is True
