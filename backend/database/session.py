"""
Database session management for SQLAlchemy with PostgreSQL
"""

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from typing import Generator
from .postgres_connection import create_spirit_engine, get_postgres_database_url

# Create PostgreSQL engine
engine = create_spirit_engine()

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Yields a session and closes it after use
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_session_sync() -> Session:
    """
    Get a synchronous database session (for non-async contexts)
    Remember to close it manually: session.close()
    """
    return SessionLocal()
