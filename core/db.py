from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import get_settings


class Base(DeclarativeBase):
    pass


def get_engine():
    return create_engine(get_settings().database_url)


def init_db(engine=None) -> None:
    """Legt die pgvector-Extension und alle Tabellen an (idempotent)."""
    import core.models  # noqa: F401  registriert alle Modelle auf Base

    engine = engine or get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


def get_sessionmaker(engine=None):
    return sessionmaker(bind=engine or get_engine())
