"""
DB engine + session factory + one-shot table creation.
Uses SQLite by default (see config/settings.py). Point DATABASE_URL at
Postgres/Supabase later and this file needs no changes.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from backend.models.models import Base

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    """Create all tables if they don't exist yet. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at: {settings.DATABASE_URL}")
