from typing import List, Optional

from pydantic import BaseModel


class SystemSettingsStatus(BaseModel):
    project_name: str
    version: str
    environment: str
    database_connected: bool
    database_dialect: str
    github_token_configured: bool
    github_rate_limit_remaining: Optional[int] = None
    github_webhook_configured: bool
    llm_provider: str
    llm_configured: bool
    available_providers: List[str]
    max_diff_files: int
    max_diff_bytes: int
