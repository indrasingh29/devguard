import hashlib
import hmac
import re
from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_github_signature(payload_body: bytes, signature_header: Optional[str]) -> bool:
    """
    Verifies GitHub webhook HMAC-SHA256 signature against the raw payload bytes.
    """
    if not settings.GITHUB_WEBHOOK_SECRET:
        # If no secret configured in development, webhook signature is not enforced
        return True

    if not signature_header:
        return False

    parts = signature_header.split("=")
    if len(parts) != 2 or parts[0] != "sha256":
        return False

    expected_mac = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(parts[1], expected_mac)

def sanitize_repo_url(url: str) -> str:
    """
    Validates and standardizes GitHub repository URLs to prevent SSRF and injection.
    Only allows https://github.com/owner/repo or github.com/owner/repo or owner/repo.
    """
    url = url.strip()
    match = re.match(r"^(?:https?://github\.com/)?([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)/*$", url)
    if not match:
        raise ValueError("Invalid GitHub repository format. Expected 'owner/repo' or 'https://github.com/owner/repo'")
    owner, repo = match.groups()
    # Strip .git if present
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"

def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Optional API Key check for enterprise endpoints.
    """
    if not settings.API_KEY:
        return True
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True
