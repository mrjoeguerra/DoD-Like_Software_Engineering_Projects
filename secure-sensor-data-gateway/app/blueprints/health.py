from flask import Blueprint, jsonify
from ..extensions import db

bp = Blueprint("health", __name__)

@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})

@bp.get("/readyz")
def readyz():
    try:
        db.session.execute("SELECT 1")
        return jsonify({"status": "ready"})
    except Exception as exc:
        return jsonify({"status": "not_ready", "error": str(exc)}), 503
