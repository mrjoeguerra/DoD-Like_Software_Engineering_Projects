import os
import base64
import hashlib
import hmac
import json
import time
import uuid
import pytest

from app import create_app
from app.extensions import db
from app.models import Client

def sign(secret: str, timestamp: str, nonce: str, raw_body: bytes) -> str:
    msg = (f"{timestamp}.{nonce}.").encode("utf-8") + raw_body
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

@pytest.fixture()
def app():
    os.environ["SECRET_KEY"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///instance/test.db"
    a = create_app()
    a.config.update(TESTING=True, MAX_CLOCK_SKEW_SECONDS=999, NONCE_TTL_SECONDS=999)

    with a.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(Client(
            client_id="alpha-sensor",
            api_key="alpha-key-123",
            shared_secret="alpha-secret-CHANGE-ME",
            allowed_types="position,status",
            is_active=True,
        ))
        db.session.commit()

    yield a

    with a.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def test_accepts_valid_signed_request(client):
    body = json.dumps({"type": "position", "payload": {"lat": 1, "lon": 2}}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex
    sig = sign("alpha-secret-CHANGE-ME", ts, nonce, body)

    rv = client.post("/api/ingest", data=body, headers={
        "Content-Type": "application/json",
        "X-Client-Id": "alpha-sensor",
        "X-Api-Key": "alpha-key-123",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig,
    })
    assert rv.status_code == 200
    assert rv.get_json()["accepted"] is True

def test_rejects_replayed_nonce(client):
    body = json.dumps({"type": "position", "payload": {"lat": 1, "lon": 2}}, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ts = str(int(time.time()))
    nonce = "fixednonce"
    sig = sign("alpha-secret-CHANGE-ME", ts, nonce, body)

    headers = {
        "Content-Type": "application/json",
        "X-Client-Id": "alpha-sensor",
        "X-Api-Key": "alpha-key-123",
        "X-Timestamp": ts,
        "X-Nonce": nonce,
        "X-Signature": sig,
    }

    rv1 = client.post("/api/ingest", data=body, headers=headers)
    assert rv1.status_code == 200

    rv2 = client.post("/api/ingest", data=body, headers=headers)
    assert rv2.status_code == 401
    assert rv2.get_json()["reason"] == "replayed_nonce"
