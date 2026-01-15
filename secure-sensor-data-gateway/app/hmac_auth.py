from __future__ import annotations

import base64
import hmac
import hashlib
import time
from dataclasses import dataclass
from flask import current_app
from .extensions import db
from .models import Client, Nonce

@dataclass
class AuthResult:
    ok: bool
    client: Client | None
    reason: str

def _canonical_string(timestamp: str, nonce: str, raw_body: bytes) -> bytes:
    return (f"{timestamp}.{nonce}.").encode("utf-8") + raw_body

def verify_hmac_request(client_id, api_key, timestamp, nonce, signature_b64, raw_body: bytes) -> AuthResult:
    if not all([client_id, api_key, timestamp, nonce, signature_b64]):
        return AuthResult(False, None, "missing_headers")

    client = Client.query.filter_by(client_id=client_id).first()
    if not client or not client.is_active:
        return AuthResult(False, None, "unknown_or_inactive_client")

    if api_key != client.api_key:
        return AuthResult(False, client, "invalid_api_key")

    try:
        ts = int(timestamp)
    except ValueError:
        return AuthResult(False, client, "invalid_timestamp")

    now = int(time.time())
    if abs(now - ts) > current_app.config["MAX_CLOCK_SKEW_SECONDS"]:
        return AuthResult(False, client, "timestamp_out_of_range")

    if Nonce.query.filter_by(client_id=client.client_id, nonce=nonce).first():
        return AuthResult(False, client, "replayed_nonce")

    msg = _canonical_string(timestamp, nonce, raw_body)
    expected = hmac.new(client.shared_secret.encode("utf-8"), msg, hashlib.sha256).digest()
    expected_b64 = base64.b64encode(expected).decode("utf-8")

    if not hmac.compare_digest(expected_b64, signature_b64):
        return AuthResult(False, client, "bad_signature")

    db.session.add(Nonce(client_id=client.client_id, nonce=nonce))
    db.session.commit()
    return AuthResult(True, client, "ok")

def cleanup_old_nonces():
    import datetime
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=current_app.config["NONCE_TTL_SECONDS"])
    Nonce.query.filter(Nonce.seen_at < cutoff).delete()
    db.session.commit()
