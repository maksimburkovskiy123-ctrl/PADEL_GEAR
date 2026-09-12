import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database
from app.main import app
from app.seed import seed_database


@pytest.fixture
def test_database(monkeypatch):
    # A separate in-memory database for every test, even if DATABASE_URL is set.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", sessionmaker(bind=engine, expire_on_commit=False))
    database.Base.metadata.create_all(engine)
    with database.get_session() as session:
        seed_database(session)
    yield engine
    engine.dispose()


@pytest.fixture
def client(test_database):
    with TestClient(app) as client:
        yield client
