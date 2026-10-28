from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import InvalidWebhookSignatureException
from app.schemas.webhook import WebhookResponse
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/github", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: str = Header("ping", alias="X-GitHub-Event"),
    x_github_delivery: str = Header(None, alias="X-GitHub-Delivery"),
    db: Session = Depends(get_db)
):
    """
    Receives and processes GitHub webhook events with HMAC-SHA256 signature verification.
    """
    raw_body = await request.body()
    delivery_id = x_github_delivery or "unknown-delivery"

    try:
        delivery_status, message = WebhookService.handle_github_webhook(
            db=db,
            raw_body=raw_body,
            signature_header=x_hub_signature_256,
            event_type=x_github_event,
            delivery_id=delivery_id
        )
        return WebhookResponse(
            status=delivery_status,
            message=message,
            delivery_id=delivery_id
        )
    except InvalidWebhookSignatureException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid HMAC webhook signature"
        )
