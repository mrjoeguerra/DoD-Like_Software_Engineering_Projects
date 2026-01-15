from __future__ import annotations
from datetime import datetime
from .extensions import db

class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), unique=True, nullable=False, index=True)
    api_key = db.Column(db.String(128), nullable=False)
    shared_secret = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    allowed_types = db.Column(db.String(500), default="position,status", nullable=False)

class Nonce(db.Model):
    __tablename__ = "nonces"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), nullable=False, index=True)
    nonce = db.Column(db.String(128), nullable=False, index=True)
    seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class AcceptedReport(db.Model):
    __tablename__ = "accepted_reports"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), nullable=False, index=True)
    report_type = db.Column(db.String(40), nullable=False, index=True)
    payload_json = db.Column(db.Text, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class QuarantinedReport(db.Model):
    __tablename__ = "quarantined_reports"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), nullable=True, index=True)
    reason = db.Column(db.String(120), nullable=False, index=True)
    payload_json = db.Column(db.Text, nullable=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class AuditEvent(db.Model):
    __tablename__ = "audit_events"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), nullable=True, index=True)
    event_type = db.Column(db.String(60), nullable=False, index=True)
    detail_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
