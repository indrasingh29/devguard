from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SeverityLevel = Literal["critical", "high", "medium", "low", "info"]
FindingCategory = Literal["security", "bug_risk", "error_handling", "maintainability", "test_insufficiency", "secret_leak"]
DetectionSource = Literal["deterministic", "bandit", "ast_check", "regex_secret", "llm_suggestion", "quality_linter"]
ConfidenceLevel = Literal["deterministic", "high", "medium", "low"]

class FindingBase(BaseModel):
    file_path: str = Field(..., description="Relative file path within repository")
    line_start: Optional[int] = Field(None, description="Starting line number in changed diff")
    line_end: Optional[int] = Field(None, description="Ending line number")
    severity: SeverityLevel
    category: FindingCategory
    title: str = Field(..., max_length=300)
    message: str = Field(..., description="Detailed explanation of the issue")
    evidence: Optional[str] = Field(None, description="Supporting code snippet or problematic line")
    suggested_remediation: Optional[str] = Field(None, description="Actionable fix recommendation")
    detection_source: DetectionSource
    confidence: ConfidenceLevel = "high"
    rule_id: str = Field(..., max_length=100)

class FindingCreate(FindingBase):
    review_job_id: int

class FindingResponse(FindingBase):
    id: int
    review_job_id: int
    created_at: datetime
    feedback_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FindingFilter(BaseModel):
    severity: Optional[SeverityLevel] = None
    category: Optional[FindingCategory] = None
    file_path: Optional[str] = None
    detection_source: Optional[DetectionSource] = None
