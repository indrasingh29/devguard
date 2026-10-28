import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "DevGuard AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/devguard"
    )
    
    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = Field(default=None)
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None)

    # Analysis & Limits
    MAX_DIFF_FILES: int = 50
    MAX_DIFF_BYTES: int = 1_000_000  # 1MB limit for diffs
    MAX_REVIEW_TIMEOUT_SECONDS: int = 120

    # LLM Settings
    LLM_PROVIDER: str = Field(default="none")  # none, gemini, openai, ollama, fallback
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: Optional[str] = None

    # Security & CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    API_KEY: Optional[str] = None  # Optional API key protection for endpoints

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v):
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            val = self.CORS_ORIGINS.strip()
            if val == "*":
                return ["*"]
            if val.startswith("[") and val.endswith("]"):
                try:
                    import json
                    return json.loads(val)
                except Exception:
                    pass
            return [i.strip() for i in val.split(",") if i.strip()]
        return ["*"]

settings = Settings()
