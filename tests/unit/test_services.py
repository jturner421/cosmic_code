from service_layer.services import allocate


def test_returns_allocation(FakeRepository, FakeSession):  # noqa: N803
    repo = FakeRepository.for_batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    result = allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"
