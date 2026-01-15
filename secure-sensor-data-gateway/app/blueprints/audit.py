from __future__ import annotations

import json
from flask import Blueprint, jsonify
from ..models import AuditEvent, AcceptedReport, QuarantinedReport

bp = Blueprint("audit", __name__)

@bp.get("/audit/recent")
def recent_audit():
    events = AuditEvent.query.order_by(AuditEvent.created_at.desc()).limit(200).all()
    return jsonify([{
        "id": e.id,
        "client_id": e.client_id,
        "event_type": e.event_type,
        "detail": json.loads(e.detail_json),
        "created_at": e.created_at.isoformat() + "Z",
    } for e in events])

@bp.get("/reports/accepted")
def accepted_reports():
    rows = AcceptedReport.query.order_by(AcceptedReport.received_at.desc()).limit(200).all()
    return jsonify([{
        "id": r.id,
        "client_id": r.client_id,
        "type": r.report_type,
        "payload": json.loads(r.payload_json),
        "received_at": r.received_at.isoformat() + "Z",
    } for r in rows])

@bp.get("/reports/quarantine")
def quarantine_reports():
    rows = QuarantinedReport.query.order_by(QuarantinedReport.received_at.desc()).limit(200).all()
    return jsonify([{
        "id": r.id,
        "client_id": r.client_id,
        "reason": r.reason,
        "payload_raw": r.payload_json,
        "received_at": r.received_at.isoformat() + "Z",
    } for r in rows])
