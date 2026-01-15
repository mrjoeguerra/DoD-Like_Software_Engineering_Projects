import click
from .extensions import db
from .models import Client

@click.command("init-db")
def init_db_cmd():
    db.create_all()
    click.echo("Database initialized.")

@click.command("seed-clients")
def seed_clients_cmd():
    existing = Client.query.filter_by(client_id="alpha-sensor").first()
    if not existing:
        db.session.add(Client(
            client_id="alpha-sensor",
            api_key="alpha-key-123",
            shared_secret="alpha-secret-CHANGE-ME",
            allowed_types="position,status",
            is_active=True,
        ))
        db.session.commit()
        click.echo("Seeded default client alpha-sensor.")
    else:
        click.echo("Client already exists; skipping.")
