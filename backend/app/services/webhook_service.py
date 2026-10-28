import hashlib
import json
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidWebhookSignatureException
from app.core.logging import logger
from app.core.security import verify_github_signature
from app.models.webhook_delivery import WebhookDelivery
from app.services.background_worker import BackgroundWorker


class WebhookService:
    @classmethod
    def handle_github_webhook(
        cls,
        db: Session,
        raw_body: bytes,
        signature_header: str,
        event_type: str,
        delivery_id: str
    ) -> Tuple[str, str]:
        # 1. Verify HMAC-SHA256 signature
        if not verify_github_signature(raw_body, signature_header):
            logger.warning(f"Rejected webhook delivery {delivery_id}: Invalid signature")
            raise InvalidWebhookSignatureException()

        # 2. Check for duplicate delivery
        existing_delivery = db.scalar(
            select(WebhookDelivery).where(WebhookDelivery.delivery_id == delivery_id)
        )
        if existing_delivery:
            logger.info(f"Duplicate webhook delivery ignored: {delivery_id}")
            return "ignored", f"Delivery {delivery_id} was already processed"

        # 3. Hash payload
        payload_hash = hashlib.sha256(raw_body).hexdigest()

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to decode webhook payload JSON: {e}")
            delivery_record = WebhookDelivery(
                delivery_id=delivery_id,
                event_type=event_type,
                action="invalid_json",
                payload_hash=payload_hash,
                status="failed"
            )
            db.add(delivery_record)
            db.commit()
            return "failed", "Invalid JSON payload"

        action = payload.get("action")
        status = "ignored"
        message = f"Event '{event_type}' with action '{action}' acknowledged"

        # 4. Handle PR events
        if event_type == "pull_request" and action in ("opened", "synchronize", "reopened"):
            repo_full_name = payload.get("repository", {}).get("full_name")
            pr_number = payload.get("pull_request", {}).get("number")

            if repo_full_name and pr_number:
                logger.info(f"Triggering background review for {repo_full_name}#{pr_number} from webhook")
                BackgroundWorker.schedule_review(repo_full_name, pr_number, mode="deterministic")
                status = "processed"
                message = f"Scheduled review for {repo_full_name}#{pr_number}"

        # 5. Persist delivery record
        delivery_record = WebhookDelivery(
            delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            payload_hash=payload_hash,
            status=status
        )
        db.add(delivery_record)
        db.commit()

        return status, message
