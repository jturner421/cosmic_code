"""FastAPI dependency injection providers."""

from typing import Generator

from sqlalchemy.orm import Session

from db.session import Database
from repository.repositories import BatchRepository


def get_db() -> Database:
    """Get the Database singleton."""
    return Database()


def get_session() -> Generator[Session, None, None]:
    """Yield a session that auto-commits on success, rolls back on error."""
    db = get_db()
    with db.get_session() as session:
        yield session


def get_batch_repository(session: Session) -> BatchRepository:
    """Create a BatchRepository with the provided session."""
    db = get_db()
    return BatchRepository(db, session)
