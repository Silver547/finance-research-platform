"""
DB engine + session factory + one-shot table creation.
Uses SQLite by default (see config/settings.py). Point DATABASE_URL at
Postgres/Supabase later and this file needs no changes.

Migration note (Phase 7): this project has no Alembic setup — schema changes
rely on Base.metadata.create_all(), which only creates tables that don't
exist yet and never alters existing tables. That's fine for brand-new
databases, but it means a new column added to an existing model (e.g.
Report.structured_digest in Phase 6) never appears on a database that
already had that table. _apply_column_migrations() below is a small,
dialect-aware patch for exactly that gap: it checks each table's actual
columns via SQLAlchemy's inspector and adds any missing ones with
ALTER TABLE. Safe to run repeatedly — it's a no-op once a column exists.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from backend.models.models import Base

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=280,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Columns added to existing models after their table may already have been
# created elsewhere. Each entry: (table_name, column_name, {dialect: ddl_type}).
# Add a new tuple here whenever a future phase adds a column to an existing
# table — no new migration file needed.
_COLUMN_MIGRATIONS = [
    (
        "reports",
        "structured_digest",
        {
            "sqlite": "TEXT",
            "postgresql": "JSON",
        },
    ),
]


def _apply_column_migrations():
    """Adds any columns listed in _COLUMN_MIGRATIONS that don't yet exist
    on their table. No-op for brand-new databases (create_all already
    included them) and no-op on repeat calls once applied."""
    inspector = inspect(engine)
    dialect_name = engine.dialect.name

    for table_name, column_name, ddl_by_dialect in _COLUMN_MIGRATIONS:
        if table_name not in inspector.get_table_names():
            # Table doesn't exist yet — create_all() will have built it
            # with this column already, so there's nothing to migrate.
            continue

        existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
        if column_name in existing_columns:
            continue

        ddl_type = ddl_by_dialect.get(dialect_name)
        if not ddl_type:
            print(
                f"[migration] No DDL type configured for dialect '{dialect_name}' — "
                f"skipping '{column_name}' on '{table_name}'. Add it to _COLUMN_MIGRATIONS."
            )
            continue

        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_type}"))
        print(f"[migration] Added missing column '{column_name}' to '{table_name}'.")


def init_db():
    """Create all tables if they don't exist yet, then apply any pending
    column migrations for tables that already existed. Safe to call
    repeatedly."""
    Base.metadata.create_all(bind=engine)
    _apply_column_migrations()


def get_session():
    return SessionLocal()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at: {settings.DATABASE_URL}")