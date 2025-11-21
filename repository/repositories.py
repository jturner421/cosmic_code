from typing import Generic, TypeVar

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
        return self.session.query(self.entity_class).filter_by(**kwargs).one_or_none()

    def list(self) -> list[T]:
        return self.session.query(self.entity_class).all()


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
        return self.session.query(OrderLine).filter_by(orderid=orderid).all()
