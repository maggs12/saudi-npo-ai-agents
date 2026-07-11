from app.database import SessionLocal, get_session


def get_db():
    with SessionLocal() as session:
        yield session
