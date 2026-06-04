"""
Migration tracker — records which migrations have been applied in a
schema_migrations table. Migrations run exactly once; subsequent startups
skip them with a single batch DB query.
"""
from sqlalchemy import text
from extensions import db
import logging

logger = logging.getLogger(__name__)

_applied: set[str] = set()   # in-memory cache, populated once at startup
_ready = False


def _ensure_table(connection):
    """Create schema_migrations table if it doesn't exist (MSSQL-compatible)."""
    connection.execute(text("""
        IF OBJECT_ID('schema_migrations', 'U') IS NULL
        CREATE TABLE schema_migrations (
            id          INT IDENTITY(1,1) PRIMARY KEY,
            name        NVARCHAR(255) NOT NULL UNIQUE,
            applied_at  DATETIME NOT NULL DEFAULT GETDATE()
        )
    """))
    connection.commit()


def load(connection):
    """Load all applied migration names into the in-memory set."""
    global _applied, _ready
    _ensure_table(connection)
    rows = connection.execute(text("SELECT name FROM schema_migrations")).fetchall()
    _applied = {row[0] for row in rows}
    _ready = True
    logger.info(f"Migration tracker: {len(_applied)} migrations already applied")


def is_applied(name: str) -> bool:
    return name in _applied


def mark_applied(connection, name: str):
    connection.execute(text("INSERT INTO schema_migrations (name) VALUES (:name)"), {"name": name})
    connection.commit()
    _applied.add(name)


def run(name: str, fn, *args, **kwargs) -> bool:
    """
    Run a migration function only if it hasn't been applied yet.
    Marks it applied on success. Returns True if it ran, False if skipped.
    """
    if is_applied(name):
        return False
    logger.info(f"Applying migration: {name}")
    try:
        fn(*args, **kwargs)
        with db.engine.connect() as conn:
            mark_applied(conn, name)
        logger.info(f"Migration applied: {name}")
        return True
    except Exception as e:
        logger.error(f"Migration failed [{name}]: {e}")
        raise
