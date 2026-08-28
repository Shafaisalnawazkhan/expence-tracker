from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db():
    with TestingSession() as session: yield session


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_registration_requires_separate_login():
    email = f"user-{uuid4()}@example.com"; password = "SecurePass123"
    assert client.post("/api/auth/login", json={"email": email, "password": password}).status_code == 401
    registered = client.post("/api/auth/register", json={"name": "Test User", "email": email, "password": password})
    assert registered.status_code == 201
    assert "access_token" not in registered.json()
    logged_in = client.post("/api/auth/login", json={"email": email, "password": password})
    assert logged_in.status_code == 200
    assert logged_in.json()["access_token"]


def test_protected_routes_reject_anonymous_users():
    assert client.get("/api/dashboard").status_code in (401, 403)


def test_app_lock_pin_is_verified_server_side():
    email = f"lock-{uuid4()}@example.com"; password = "SecurePass123"
    client.post("/api/auth/register", json={"name": "Lock User", "email": email, "password": password})
    tokens = client.post("/api/auth/login", json={"email": email, "password": password}).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.post("/api/auth/app-lock/setup", json={"pin": "2468"}, headers=headers).status_code == 200
    assert client.post("/api/auth/app-lock/verify", json={"pin": "0000"}, headers=headers).status_code == 401
    assert client.post("/api/auth/app-lock/verify", json={"pin": "2468"}, headers=headers).json()["verified"] is True
