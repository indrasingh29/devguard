from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChangedHunk(BaseModel):
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    header: str
    lines: List[str]  # e.g. ["+added line", "-removed line", " context line"]

class ChangedFile(BaseModel):
    path: str
    old_path: Optional[str] = None
    change_type: str = "modified"  # added, modified, deleted, renamed
    additions: int = 0
    deletions: int = 0
    patch: Optional[str] = None
    hunks: List[ChangedHunk] = []
    is_binary: bool = False

class DiffSummary(BaseModel):
    total_files: int
    total_additions: int
    total_deletions: int
    files: List[ChangedFile]

class PullRequestBase(BaseModel):
    repository_id: int
    number: int
    title: str
    state: str = "open"
    author: str
    base_sha: str
    head_sha: str
    html_url: str
    diff_url: str

class PullRequestResponse(PullRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    repo_full_name: Optional[str] = None
    latest_review_job_id: Optional[int] = None
    latest_review_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FetchPRRequest(BaseModel):
    repo_full_name: str = Field(..., json_schema_extra={"example": "octocat/Hello-World"})
    pull_number: int = Field(..., json_schema_extra={"example": 42})
