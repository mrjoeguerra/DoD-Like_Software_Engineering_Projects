from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

from ..models import User
from ..schemas import LoginSchema
from ..security import verify_password
from ..audit import write_audit
from ..extensions import limiter

bp = Blueprint("auth", __name__)
login_schema = LoginSchema()


@bp.post("/login")
@limiter.limit("10 per minute")
def login():
    payload = request.get_json(silent=True) or {}
    data = login_schema.load(payload)

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.is_active or not verify_password(data["password"], user.password_hash):
        write_audit("auth.login_failed", {"username": data.get("username")}, actor_override=data.get("username"))
        return jsonify({"error": "invalid_credentials"}), 401

    additional_claims = {"role": user.role}
    access = create_access_token(identity=user.username, additional_claims=additional_claims)
    refresh = create_refresh_token(identity=user.username, additional_claims=additional_claims)

    write_audit("auth.login_success", {"username": user.username, "role": user.role})
    return jsonify({"access_token": access, "refresh_token": refresh, "role": user.role})


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user or not user.is_active:
        return jsonify({"error": "inactive_user"}), 401

    access = create_access_token(identity=user.username, additional_claims={"role": user.role})
    write_audit("auth.token_refreshed", {"username": user.username})
    return jsonify({"access_token": access})
