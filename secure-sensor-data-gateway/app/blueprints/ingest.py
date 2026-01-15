from __future__ import annotations

import json
from flask import Blueprint, jsonify, request
from ..extensions import db
from ..schemas import IngestSchema
from ..hmac_auth import verify_hmac_request, cleanup_old_nonces
from ..policy import is_allowed
from ..models import AcceptedReport, QuarantinedReport, AuditEvent

bp = Blueprint("ingest", __name__)
schema = IngestSchema()

def audit(client_id, event_type: str, detail: dict) -> None:
    db.session.add(AuditEvent(client_id=client_id, event_type=event_type, detail_json=json.dumps(detail)))
    db.session.commit()

@bp.post("/ingest")
def ingest():
    raw_body = request.get_data(cache=False)
    headers = request.headers

    try:
        cleanup_old_nonces()
    except Exception:
        pass

    auth = verify_hmac_request(
        client_id=headers.get("X-Client-Id"),
        api_key=headers.get("X-Api-Key"),
        timestamp=headers.get("X-Timestamp"),
        nonce=headers.get("X-Nonce"),
        signature_b64=headers.get("X-Signature"),
        raw_body=raw_body,
    )

    if not auth.ok:
        db.session.add(QuarantinedReport(
            client_id=headers.get("X-Client-Id"),
            reason=auth.reason,
            payload_json=raw_body.decode("utf-8", errors="replace"),
        ))
        db.session.commit()
        audit(headers.get("X-Client-Id"), "ingest.rejected", {"reason": auth.reason})
        return jsonify({"accepted": False, "reason": auth.reason}), 401

    try:
        data = request.get_json(force=True)
    except Exception:
        db.session.add(QuarantinedReport(client_id=auth.client.client_id, reason="invalid_json",
                                         payload_json=raw_body.decode("utf-8", errors="replace")))
        db.session.commit()
        audit(auth.client.client_id, "ingest.rejected", {"reason": "invalid_json"})
        return jsonify({"accepted": False, "reason": "invalid_json"}), 400

    try:
        validated = schema.load(data)
    except Exception as exc:
        db.session.add(QuarantinedReport(client_id=auth.client.client_id, reason="schema_validation_failed",
                                         payload_json=json.dumps(data)))
        db.session.commit()
        audit(auth.client.client_id, "ingest.rejected", {"reason": "schema_validation_failed", "error": str(exc)})
        return jsonify({"accepted": False, "reason": "schema_validation_failed"}), 400

    report_type = validated["type"]
    if not is_allowed(auth.client, report_type):
        db.session.add(QuarantinedReport(client_id=auth.client.client_id, reason="policy_denied",
                                         payload_json=json.dumps(validated)))
        db.session.commit()
        audit(auth.client.client_id, "ingest.rejected", {"reason": "policy_denied", "type": report_type})
        return jsonify({"accepted": False, "reason": "policy_denied"}), 403

    db.session.add(AcceptedReport(client_id=auth.client.client_id, report_type=report_type,
                                 payload_json=json.dumps(validated["payload"])))
    db.session.commit()
    audit(auth.client.client_id, "ingest.accepted", {"type": report_type})
    return jsonify({"accepted": True})
