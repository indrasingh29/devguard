from typing import Optional

from pydantic import BaseModel


class WebhookResponse(BaseModel):
    status: str
    message: str
    delivery_id: Optional[str] = None
    job_id: Optional[int] = None
