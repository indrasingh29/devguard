import hashlib
import hmac
import json

from app.core.config import settings


def test_webhook_signature_verification(client):
    secret = "test-webhook-secret-12345"
    settings.GITHUB_WEBHOOK_SECRET = secret

    payload = {
        "action": "opened",
        "pull_request": {"number": 42},
        "repository": {"full_name": "octocat/Hello-World"}
    }
    raw_body = json.dumps(payload).encode("utf-8")
    mac = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    valid_signature = f"sha256={mac}"

    # 1. Successful delivery with valid signature
    response = client.post(
        "/api/v1/webhooks/github",
        content=raw_body,
        headers={
            "X-Hub-Signature-256": valid_signature,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-unique-001",
            "Content-Type": "application/json"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"

    # 2. Duplicate delivery should be ignored (idempotent)
    response_dup = client.post(
        "/api/v1/webhooks/github",
        content=raw_body,
        headers={
            "X-Hub-Signature-256": valid_signature,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-unique-001",
            "Content-Type": "application/json"
        }
    )
    assert response_dup.status_code == 200
    assert response_dup.json()["status"] == "ignored"

    # 3. Invalid signature should be rejected with 401
    response_bad_sig = client.post(
        "/api/v1/webhooks/github",
        content=raw_body,
        headers={
            "X-Hub-Signature-256": "sha256=invalidhashvalue000000000000000000000000000000000000000000000000",
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-unique-002",
            "Content-Type": "application/json"
        }
    )
    assert response_bad_sig.status_code == 401
