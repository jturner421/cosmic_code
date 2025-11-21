from typing import Generic, TypeVar

from sqlalchemy import select
from model import Batch, OrderLine

T = TypeVar("T")


class SqlAlchemyRepository(Generic[T]):
    """Generic SQLAlchemy repository for any entity type."""

    def __init__(self, session, entity_class: type[T]):
        self.session = session
        self.entity_class = entity_class

    def add(self, entity: T):
        self.session.add(entity)

    def get(self, **kwargs) -> T | None:
        stmt = select(self.entity_class).filter_by(**kwargs)
        return self.session.execute(stmt).scalar_one_or_none()

    def list(self) -> list[T]:
        return self.session.execute(select(self.entity_class)).scalars().all()


class BatchRepository(SqlAlchemyRepository[Batch]):
    """Repository for Batch entities."""

    def __init__(self, session):
        super().__init__(session, Batch)

    def get_by_reference(self, reference: str) -> Batch | None:
        return self.get(reference=reference)


class OrderLineRepository(SqlAlchemyRepository[OrderLine]):
    """Repository for OrderLine entities."""

    def __init__(self, session):
        super().__init__(session, OrderLine)

    def get_by_orderid(self, orderid: str) -> list[OrderLine]:
        stmt = select(OrderLine).filter_by(orderid=orderid)
        return self.session.execute(stmt).scalars().all()
