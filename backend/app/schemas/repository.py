from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RepositoryBase(BaseModel):
    owner: str = Field(..., max_length=100)
    name: str = Field(..., max_length=100)
    full_name: str = Field(..., max_length=205)
    default_branch: str = "main"
    is_private: bool = False
    html_url: str

class RepositoryConnectRequest(BaseModel):
    repo_input: str = Field(..., description="GitHub URL or 'owner/repo' string", json_schema_extra={"example": "facebook/react"})

class RepositoryResponse(RepositoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    open_prs_count: Optional[int] = 0
    total_reviews_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class RepositoryValidateResponse(BaseModel):
    valid: bool
    owner: Optional[str] = None
    name: Optional[str] = None
    full_name: Optional[str] = None
    is_private: Optional[bool] = None
    default_branch: Optional[str] = None
    description: Optional[str] = None
    message: Optional[str] = None
