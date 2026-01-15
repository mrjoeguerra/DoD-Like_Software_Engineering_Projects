import os
import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.security import hash_password


@pytest.fixture()
def app():
    os.environ["SECRET_KEY"] = "test"
    os.environ["JWT_SECRET_KEY"] = "test-jwt"
    os.environ["DATABASE_URL"] = "sqlite:///instance/test.db"

    a = create_app()
    a.config.update(TESTING=True)

    with a.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(username="admin", password_hash=hash_password("Admin!234"), role="admin", is_active=True))
        db.session.add(User(username="operator", password_hash=hash_password("Operator!234"), role="operator", is_active=True))
        db.session.add(User(username="auditor", password_hash=hash_password("Auditor!234"), role="auditor", is_active=True))
        db.session.commit()

    yield a

    with a.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password):
    rv = client.post("/api/auth/login", json={"username": username, "password": password})
    return rv.status_code, rv.get_json()


def test_admin_can_create_task(client):
    code, data = login(client, "admin", "Admin!234")
    assert code == 200
    token = data["access_token"]
    rv = client.post("/api/tasks", json={"title": "t1", "priority": "low"}, headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 201


def test_operator_cannot_create_task(client):
    code, data = login(client, "operator", "Operator!234")
    assert code == 200
    token = data["access_token"]
    rv = client.post("/api/tasks", json={"title": "t1"}, headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 403


def test_auditor_can_read_audit(client):
    code, data = login(client, "admin", "Admin!234")
    token_admin = data["access_token"]
    client.post("/api/tasks", json={"title": "t1"}, headers={"Authorization": f"Bearer {token_admin}"})
    code, data = login(client, "auditor", "Auditor!234")
    token_auditor = data["access_token"]
    rv = client.get("/api/audit", headers={"Authorization": f"Bearer {token_auditor}"})
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)
