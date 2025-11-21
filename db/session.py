"""
Provide a single Database object (Singleton) that exposes a SQLAlchemy engine and convenient ways to get sessions.

    Notes for developers:
    - SingletonMeta ensures only one Database instance exists per Python process
      (thread-safe via a Lock).
    - Database holds the SQLAlchemy Engine and a sessionmaker factory.
    - Use Database().session for a quick one-off Session (not context-managed).
    - Use Database().get_session() as a context manager to get a transactional
      session that automatically commits on success and rolls back on error.
    - On first instantiation, Alembic migrations are auto-applied to "head".
"""

import os
import pathlib
from contextlib import contextmanager
from threading import Lock
from typing import ClassVar

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.orm import perform_mapping

# Load environment variables from .env file
load_dotenv()

# Default to in-memory SQLite if DATABASE_URL not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")


def run_migrations(connection=None):
    """
    Run Alembic migrations programmatically to 'head'.

    Args:
        connection: Optional SQLAlchemy connection. If provided, migrations
                    run against this connection (required for in-memory SQLite
                    to ensure migrations use the same connection as the app).

    """
    from alembic import command
    from alembic.config import Config

    alembic_ini_path = pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    if connection is not None:
        # Pass connection to env.py via config.attributes
        alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


class SingletonMeta(type):
    """
    A thread-safe implementation of Singleton as a metaclass.

    Behavior:
    - _instances holds a single instance per class that uses this metaclass.
    - _lock ensures only one thread can create the instance at a time.
    - __call__ checks _instances and creates/stores the instance on first use.
    """

    _instances: ClassVar[dict[type, "Database"]] = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        # Critical section guarded by a lock to avoid race conditions when
        # multiple threads try to create the singleton simultaneously.
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    """
    Singleton wrapping SQLAlchemy Engine and Session factory.

    Args:
        url: database URL (defaults to module-level DATABASE_URL).

    """

    def __init__(self, url: str = DATABASE_URL):
        # Perform ORM mapping before engine/session creation
        perform_mapping()

        # Use the provided url (previous code used the module constant unconditionally).
        # For SQLite in-memory tests, we disable thread check and use StaticPool
        # so the same connection is reused across sessions/threads (useful for tests).
        self._engine = create_engine(
            url,
            connect_args={"check_same_thread": False}
            if url.startswith("sqlite")
            else {},
            future=True,
            echo=True,
            poolclass=StaticPool,
        )
        # sessionmaker configured for explicit transaction handling:
        # - autocommit=False: manual commit via session.commit()
        # - expire_on_commit=False: avoid expiring objects on commit (convenient in tests)
        # - autoflush=False: avoid automatic flushes unless explicitly requested
        self._Session = sessionmaker(
            bind=self._engine,
            autocommit=False,
            expire_on_commit=False,
            future=True,
            autoflush=False,
        )

        # Auto-run Alembic migrations to "head" on first instantiation.
        # For in-memory SQLite, we must use the same connection so migrations
        # persist in the same database instance.
        with self._engine.connect() as connection:
            run_migrations(connection)
            connection.commit()

    @property
    def engine(self):
        """Return the underlying SQLAlchemy Engine."""
        return self._engine

    @property
    def session(self):
        """
        Return a new Session instance.

        Shortcut for quick one-off sessions. Prefer get_session() for transactional
        context management (commits/rollbacks handled automatically).
        """
        return self._Session()

    @contextmanager
    def get_session(self):
        """
        Context manager that yields a Session and manages commit/rollback.

        Usage:
            with Database().get_session() as session:
                # use session
        On successful exit it commits; on exception it rolls back and re-raises.
        """
        session = self._Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
