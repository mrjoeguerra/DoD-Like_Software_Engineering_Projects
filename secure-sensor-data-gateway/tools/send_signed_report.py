from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import time
import uuid
import urllib.request

def sign(secret: str, timestamp: str, nonce: str, raw_body: bytes) -> str:
    msg = (f"{timestamp}.{nonce}.").encode("utf-8") + raw_body
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--client-id", required=True)
    p.add_argument("--api-key", required=True)
    p.add_argument("--secret", required=True)
    p.add_argument("--type", required=True, choices=["position", "status", "telemetry"])
    p.add_argument("--payload", required=True, help='JSON string, e.g. {"lat":1,"lon":2}')
    args = p.parse_args()

    payload_obj = json.loads(args.payload)
    body = json.dumps({"type": args.type, "payload": payload_obj}, separators=(",", ":"), sort_keys=True).encode("utf-8")

    timestamp = str(int(time.time()))
    nonce = uuid.uuid4().hex
    signature = sign(args.secret, timestamp, nonce, body)

    req = urllib.request.Request(args.url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Client-Id", args.client_id)
    req.add_header("X-Api-Key", args.api_key)
    req.add_header("X-Timestamp", timestamp)
    req.add_header("X-Nonce", nonce)
    req.add_header("X-Signature", signature)

    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode("utf-8"))

if __name__ == "__main__":
    main()
