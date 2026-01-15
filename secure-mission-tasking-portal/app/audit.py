from __future__ import annotations

import json
import uuid
from flask import Flask, g, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from .extensions import db
from .models import AuditLog


def _get_request_id() -> str:
    rid = request.headers.get("X-Request-Id")
    if rid and len(rid) <= 64:
        return rid
    return uuid.uuid4().hex


def register_audit_hooks(app: Flask) -> None:
    @app.before_request
    def _before_request():
        g.request_id = _get_request_id()

    @app.after_request
    def _after_request(response):
        response.headers["X-Request-Id"] = g.get("request_id", "unknown")
        return response


def write_audit(event_type: str, detail: dict | None = None, actor_override: str | None = None) -> None:
    actor = None
    actor_role = None
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        actor = claims.get("sub")
        actor_role = claims.get("role")
    except Exception:
        pass

    if actor_override is not None:
        actor = actor_override

    entry = AuditLog(
        event_type=event_type,
        actor=actor,
        actor_role=actor_role,
        request_id=getattr(g, "request_id", uuid.uuid4().hex),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        path=request.path,
        method=request.method,
        detail=json.dumps(detail or {}, ensure_ascii=False),
    )
    db.session.add(entry)
    db.session.commit()
