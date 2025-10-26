"""
Database connection and session management
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from .models import Base
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with connection pooling"""

    def __init__(self, database_url: str = None, echo: bool = False):
        """
        Initialize database manager

        Args:
            database_url: PostgreSQL connection URL
            echo: Enable SQL query logging
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/biomedical_platform'
        )

        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Set up connection event listeners
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Set up database event listeners for logging and monitoring"""

        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.info("Database connection established")

        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.info("Database connection closed")

    def create_all_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_all_tables(self):
        """Drop all database tables (USE WITH CAUTION!)"""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("All database tables dropped")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic commit/rollback

        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    def get_session_dependency(self) -> Generator[Session, None, None]:
        """
        FastAPI dependency for database sessions

        Usage:
            @app.get("/users")
            def get_users(db: Session = Depends(db_manager.get_session_dependency)):
                return db.query(User).all()
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check database connection health"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database manager instance
db_manager = None


def init_database(database_url: str = None, echo: bool = False) -> DatabaseManager:
    """
    Initialize global database manager

    Args:
        database_url: PostgreSQL connection URL
        echo: Enable SQL query logging

    Returns:
        DatabaseManager instance
    """
    global db_manager
    db_manager = DatabaseManager(database_url=database_url, echo=echo)
    return db_manager


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for FastAPI dependency injection

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()
