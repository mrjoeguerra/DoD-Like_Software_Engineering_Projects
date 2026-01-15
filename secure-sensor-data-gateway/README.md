# Secure Sensor Data Gateway (Portfolio Replica)

> **Portfolio note (DoD-style, sanitized):** This project emulates common patterns used in classified “edge-to-core” ingestion services (message authentication, replay protection, quarantine lanes, validation, policy gating). It is **not** based on any classified system and does **not** include classified logic/data. It’s a safe public analog to demonstrate engineering ability.

## What this app is
A Flask API that ingests “sensor reports” from clients in a controlled way:
- **Client identity** via API key
- **Message authenticity** via HMAC signature
- **Replay protection** via timestamp + nonce tracking
- **Schema validation** (Marshmallow)
- **Quarantine lane** for invalid/failed-auth payloads
- **Policy gating** (simple allow/deny rules for clients + data types)
- **Audit logging** for ingest decisions

## Tech stack
- Python 3.11+
- Flask + SQLAlchemy + SQLite
- Marshmallow for validation
- HMAC-SHA256 signing
- Pytest tests
- Minimal CI scaffolding

## Quick start
```bash
cd secure-sensor-data-gateway
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

cp .env.example .env
flask --app wsgi.py init-db
flask --app wsgi.py seed-clients

flask --app wsgi.py run
```

## Default client (seeded)
- client_id: `alpha-sensor`
- api_key: `alpha-key-123`
- shared_secret (HMAC): `alpha-secret-CHANGE-ME`

## How signing works
Clients send headers:
- `X-Client-Id`
- `X-Api-Key`
- `X-Timestamp` (unix seconds)
- `X-Nonce` (random unique per request)
- `X-Signature` (base64 HMAC-SHA256)

Signature is computed over a canonical string:
```
{timestamp}.{nonce}.{raw_json_body}
```
(Where `raw_json_body` is the raw request body bytes.)

## Try it (send an ingest request)
Run the helper to generate a signed request:
```bash
python tools/send_signed_report.py --url http://127.0.0.1:5000/api/ingest \
  --client-id alpha-sensor --api-key alpha-key-123 --secret "alpha-secret-CHANGE-ME" \
  --type position --payload '{"lat":29.42,"lon":-98.49,"alt_m":210.2}'
```

## Lanes
- **Accepted**: passes auth, replay protection, validation, policy
- **Quarantine**: anything else, with reason captured

## Suggested portfolio write-up (resume bullet seeds)
- Implemented HMAC-based message authentication + anti-replay controls (nonce + timestamp) for high-integrity ingestion
- Designed “accepted vs quarantine” lanes with structured reasons for incident triage
- Built policy gate engine for client- and data-type based authorization
- Delivered test coverage and CI workflow suitable for regulated environments
