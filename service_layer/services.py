from datetime import date

from domain.model import Batch, OrderLine, allocate_batch
from repository import AbstractRepository
from repository.repositories import SqlAlchemyRepository


class InvalidSku(Exception):  # noqa: N818
    pass


def is_valid_sku(sku: str, batches) -> bool:
    return sku in {b.sku for b in batches}


def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: date | None,
    repo: AbstractRepository | SqlAlchemyRepository,
    session,
) -> None:
    repo.add(Batch(ref, sku, qty, eta))
    session.commit()


def allocate(
    orderid: str,
    sku: str,
    qty: int,
    repo: AbstractRepository | SqlAlchemyRepository,
    session,
) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        error = f"Invalid sku {sku}"
        raise InvalidSku(error)
    batchref = allocate_batch(line, batches)
    session.commit()
    return batchref
