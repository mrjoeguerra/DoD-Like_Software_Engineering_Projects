from __future__ import annotations
from .models import Client

def is_allowed(client: Client, report_type: str) -> bool:
    allowed = {t.strip() for t in (client.allowed_types or "").split(",") if t.strip()}
    return report_type in allowed
