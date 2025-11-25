"""FastAPI dependency injection providers."""

from db.session import Database
from repository.repositories import BatchRepository


def get_batch_repository() -> BatchRepository:
    """Create a BatchRepository with a session from the Database."""
    db = Database()
    return BatchRepository(db.session)
