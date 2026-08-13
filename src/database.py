"""
Database configuration and session management

Provides database connection, session factory, and initialization utilities
for persistent data storage.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent

# Database URL - using SQLite for development
# Can be easily switched to PostgreSQL: postgresql://user:password@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/activities.db")

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency injection for database sessions.
    Use this in FastAPI endpoint definitions to get a database session.
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    
    This should be called once at application startup.
    """
    Base.metadata.create_all(bind=engine)


def reset_db():
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This deletes all data. Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    init_db()
