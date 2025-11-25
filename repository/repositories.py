from typing import ClassVar, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.session import Database
from domain.model import Batch, OrderLine

T = TypeVar("T")


class SqlAlchemyRepository(Generic[T]):
    """Generic SQLAlchemy repository for any entity type."""

    _eager_load_relationships: ClassVar[list] = []

    def __init__(self, db: Database, entity_class: type[T]):
        self._db = db
        self.entity_class = entity_class

    def add(self, entity: T):
        with self._db.get_session() as session:
            session.add(entity)

    def get(self, **kwargs) -> T | None:
        stmt = select(self.entity_class).filter_by(**kwargs)
        for rel_name in self._eager_load_relationships:
            stmt = stmt.options(joinedload(getattr(self.entity_class, rel_name)))
        with self._db.get_session() as session:
            return session.execute(stmt).unique().scalar_one_or_none()

    def list(self) -> list[T]:
        with self._db.get_session() as session:
            return session.execute(select(self.entity_class)).scalars().all()


class BatchRepository(SqlAlchemyRepository[Batch]):
    """Repository for Batch entities."""

    _eager_load_relationships = ["_allocations"]

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
        with self._db.get_session() as session:
            return session.execute(stmt).scalars().all()
