from typing import ClassVar, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db.session import Database
from domain.model import Batch, OrderLine

T = TypeVar("T")


class SqlAlchemyRepository(Generic[T]):
    """Generic SQLAlchemy repository for any entity type."""

    _eager_load_relationships: ClassVar[list] = []

    def __init__(
        self, db: Database, entity_class: type[T], session: Session | None = None
    ):
        self._db = db
        self.entity_class = entity_class
        self._session = session

    def _get_session(self) -> Session:
        """Return the injected session or create a new one."""
        if self._session is not None:
            return self._session
        return self._db.session

    def add(self, entity: T):
        session = self._get_session()
        session.add(entity)

    def get(self, **kwargs) -> T | None:
        stmt = select(self.entity_class).filter_by(**kwargs)
        for rel_name in self._eager_load_relationships:
            stmt = stmt.options(joinedload(getattr(self.entity_class, rel_name)))
        session = self._get_session()
        return session.execute(stmt).unique().scalar_one_or_none()

    def list(self) -> list[T]:
        stmt = select(self.entity_class)
        for rel_name in self._eager_load_relationships:
            stmt = stmt.options(joinedload(getattr(self.entity_class, rel_name)))
        session = self._get_session()
        return session.execute(stmt).unique().scalars().all()


class BatchRepository(SqlAlchemyRepository[Batch]):
    """Repository for Batch entities."""

    _eager_load_relationships = ["_allocations"]

    def __init__(self, db: Database, session: Session | None = None):
        super().__init__(db, Batch, session)

    def get_by_reference(self, reference: str) -> Batch | None:
        return self.get(reference=reference)


class OrderLineRepository(SqlAlchemyRepository[OrderLine]):
    """Repository for OrderLine entities."""

    def __init__(self, db: Database, session: Session | None = None):
        super().__init__(db, OrderLine, session)

    def get_by_orderid(self, orderid: str) -> list[OrderLine]:
        stmt = select(OrderLine).filter_by(orderid=orderid)
        session = self._get_session()
        return session.execute(stmt).scalars().all()
