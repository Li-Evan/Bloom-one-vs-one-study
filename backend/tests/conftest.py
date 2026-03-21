import os

# Must set env vars BEFORE importing app (which triggers config validation)
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as app_database
from app.main import app as fastapi_app
from app.database import Base, get_db

# Use in-memory SQLite with StaticPool so all connections share the same database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db

# Patch SessionLocal so that chat.py's generator uses the test DB
app_database.SessionLocal = TestSession


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(fastapi_app)


@pytest.fixture
def auth_client(client):
    """Returns a client with a registered and authenticated user."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
    })
    res = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    token = res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
