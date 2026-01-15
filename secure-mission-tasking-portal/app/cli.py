from __future__ import annotations
import click
from .extensions import db
from .models import User
from .security import hash_password


@click.command("init-db")
def init_db_cmd():
    db.create_all()
    click.echo("Database initialized.")


@click.command("seed-users")
def seed_users_cmd():
    defaults = [
        ("admin", "Admin!234", "admin"),
        ("operator", "Operator!234", "operator"),
        ("auditor", "Auditor!234", "auditor"),
    ]
    for username, password, role in defaults:
        if User.query.filter_by(username=username).first():
            continue
        db.session.add(User(username=username, password_hash=hash_password(password), role=role, is_active=True))
    db.session.commit()
    click.echo("Seeded users (if missing).")
