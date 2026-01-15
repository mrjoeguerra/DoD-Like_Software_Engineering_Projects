"""Application factory for the Secure Mission Tasking Portal."""

from __future__ import annotations

import os
from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .extensions import db, jwt, limiter, talisman
from .audit import register_audit_hooks
from .blueprints.auth import bp as auth_bp
from .blueprints.tasks import bp as tasks_bp
from .blueprints.audit_api import bp as audit_bp
from .blueprints.health import bp as health_bp


def create_app(config_object: type[Config] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    cfg = config_object or Config
    app.config.from_object(cfg)

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    if app.config.get("SECURE_HEADERS"):
        talisman.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api")
    app.register_blueprint(audit_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")

    register_audit_hooks(app)

    from .cli import init_db_cmd, seed_users_cmd  # noqa: WPS433
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(seed_users_cmd)

    return app
