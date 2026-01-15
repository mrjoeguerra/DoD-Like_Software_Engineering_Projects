from __future__ import annotations

import json
from flask import Blueprint, jsonify

from ..extensions import limiter
from ..models import AuditLog
from ..security import require_roles

bp = Blueprint("audit_api", __name__)


@bp.get("/audit")
@require_roles(["admin", "auditor"])
@limiter.limit("10 per minute")
def list_audit():
    events = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify([{
        "id": e.id,
        "event_type": e.event_type,
        "actor": e.actor,
        "actor_role": e.actor_role,
        "request_id": e.request_id,
        "ip": e.ip,
        "path": e.path,
        "method": e.method,
        "detail": json.loads(e.detail or "{}"),
        "created_at": e.created_at.isoformat() + "Z",
    } for e in events])
