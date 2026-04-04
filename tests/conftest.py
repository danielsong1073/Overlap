import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db


DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides = {get_db: override_get_db}
Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def auth_client(db_setup):
    c = TestClient(app)
    c.post("/users/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })
    response = c.post("/users/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = response.json()["access_token"]
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


@pytest.fixture
def auth_client2(db_setup):
    c = TestClient(app)
    c.post("/users/register", json={
        "username": "testuser2",
        "email": "test2@test.com",
        "password": "password123"
    })
    response = c.post("/users/login", data={
        "username": "testuser2",
        "password": "password123"
    })
    token = response.json()["access_token"]
    c.headers.update({"Authorization": f"Bearer {token}"})
    return c


@pytest.fixture
def client(db_setup):
    return TestClient(app)