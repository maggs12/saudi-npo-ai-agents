import os
from datetime import date
from urllib.parse import urlparse

import pytest
from sqlmodel import Session

# Set the test database before importing config so settings use it.
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/npo_ai_test")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_PROVIDER", "mock")

from app.database import SessionLocal, create_db_and_tables, engine  # noqa: E402
from app.seed import seed_data  # noqa: E402


def _ensure_test_database():
    """Create the test database if it does not exist."""
    url = os.environ["DATABASE_URL"]
    parsed = urlparse(url)
    db_name = parsed.path.lstrip("/")
    if not db_name:
        return
    try:
        import psycopg2

        admin_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}/postgres"
        conn = psycopg2.connect(admin_url)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()
    except Exception:
        # If we cannot connect to 'postgres', the DB may already exist.
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    _ensure_test_database()
    create_db_and_tables()
    seed_data()
    yield
    # Teardown: drop all tables after tests
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    with SessionLocal() as session:
        yield session
