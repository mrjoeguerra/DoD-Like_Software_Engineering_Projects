from __future__ import annotations

import os
from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .extensions import db
from .blueprints.ingest import bp as ingest_bp
from .blueprints.audit import bp as audit_bp
from .blueprints.health import bp as health_bp


def create_app(config_object: type[Config] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)

    cfg = config_object or Config
    app.config.from_object(cfg)

    db.init_app(app)

    app.register_blueprint(ingest_bp, url_prefix="/api")
    app.register_blueprint(audit_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")

    from .cli import init_db_cmd, seed_clients_cmd  # noqa: WPS433
    app.cli.add_command(init_db_cmd)
    app.cli.add_command(seed_clients_cmd)

    return app
