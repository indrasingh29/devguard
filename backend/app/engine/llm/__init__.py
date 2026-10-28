from app.core.config import settings
from app.engine.llm.base import BaseLLMProvider
from app.engine.llm.fallback import FallbackLLMProvider
from app.engine.llm.gemini import GeminiProvider
from app.engine.llm.openai import OpenAICompatibleProvider


def get_llm_provider() -> BaseLLMProvider:
    provider = (settings.LLM_PROVIDER or "none").lower()

    if provider == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.LLM_MODEL or "gemini-1.5-flash"
        )
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return OpenAICompatibleProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL or "gpt-4o-mini"
        )
    elif provider == "ollama":
        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
            model=settings.LLM_MODEL or "codellama"
        )

    return FallbackLLMProvider()

__all__ = [
    "BaseLLMProvider",
    "FallbackLLMProvider",
    "GeminiProvider",
    "OpenAICompatibleProvider",
    "get_llm_provider",
]
