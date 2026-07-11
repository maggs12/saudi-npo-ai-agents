import json
from typing import Any

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Text, TypeDecorator
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.core.security import decrypt, encrypt


class EncryptedString(TypeDecorator):
    """SQLAlchemy type that transparently encrypts/decrypts strings at rest."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any | None, dialect: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        return encrypt(value)

    def process_result_value(self, value: Any | None, dialect: Any) -> Any:
        if value is None:
            return None
        return decrypt(value)


class JSONDict(TypeDecorator):
    """Store a Python dict as JSON text."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any | None, dialect: Any) -> Any:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False, default=str)

    def process_result_value(self, value: Any | None, dialect: Any) -> Any:
        if value is None:
            return None
        return json.loads(value)


# Use the sync URL for SQLModel operations
engine: Engine = create_engine(
    settings.sync_database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_session() -> Session:
    with SessionLocal() as session:
        yield session


def create_db_and_tables() -> None:
    """Create the pgvector extension and all tables."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    SQLModel.metadata.create_all(engine)
