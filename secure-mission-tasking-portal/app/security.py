from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)


def require_roles(roles: Iterable[str]) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in set(roles):
                return jsonify({"error": "forbidden", "message": "Insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
