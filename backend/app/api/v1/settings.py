from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, get_db
from app.schemas.settings import SystemSettingsStatus
from app.services.github_service import GitHubService

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/status", response_model=SystemSettingsStatus)
async def get_system_settings_status(db: Session = Depends(get_db)):
    """
    Returns public system status, configured providers, and database health.
    Safely hides all API keys, secrets, and sensitive tokens.
    """
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    gh = GitHubService()
    rate_info = await gh.get_rate_limit()
    rate_remaining = rate_info.get("rate", {}).get("remaining")

    available_providers = ["none", "gemini", "openai", "ollama"]
    llm_configured = False
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        llm_configured = True
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        llm_configured = True
    elif settings.LLM_PROVIDER == "ollama":
        llm_configured = True

    return SystemSettingsStatus(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
        database_dialect=engine.dialect.name,
        github_token_configured=bool(settings.GITHUB_TOKEN),
        github_rate_limit_remaining=rate_remaining,
        github_webhook_configured=bool(settings.GITHUB_WEBHOOK_SECRET),
        llm_provider=settings.LLM_PROVIDER,
        llm_configured=llm_configured,
        available_providers=available_providers,
        max_diff_files=settings.MAX_DIFF_FILES,
        max_diff_bytes=settings.MAX_DIFF_BYTES,
    )
