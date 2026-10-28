from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.finding import FindingResponse


class SeverityCount(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

class ReviewJobCreateRequest(BaseModel):
    repo_full_name: str = Field(..., json_schema_extra={"example": "octocat/Hello-World"})
    pull_number: int = Field(..., json_schema_extra={"example": 42})
    mode: str = Field(default="deterministic", description="deterministic, hybrid_llm")

class ReviewJobResponse(BaseModel):
    id: int
    pull_request_id: int
    commit_sha: str
    idempotency_key: str
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED
    mode: str
    total_files_analyzed: int
    total_findings: int
    summary: str
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    severity_counts: Optional[SeverityCount] = None
    findings: Optional[List[FindingResponse]] = None
    repo_full_name: Optional[str] = None
    pr_number: Optional[int] = None
    pr_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReviewHistoryFilter(BaseModel):
    repo_full_name: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0
