from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

FeedbackType = Literal["helpful", "false_positive", "ignored"]

class FeedbackCreateRequest(BaseModel):
    finding_id: int
    feedback_type: FeedbackType
    comment: Optional[str] = Field(None, max_length=1000)

class FeedbackResponse(BaseModel):
    id: int
    finding_id: int
    feedback_type: str
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
