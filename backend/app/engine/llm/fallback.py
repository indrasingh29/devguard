from typing import List

from app.core.logging import logger
from app.engine.llm.base import BaseLLMProvider
from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary


class FallbackLLMProvider(BaseLLMProvider):
    """
    Fallback provider when no external LLM API is configured.
    Guarantees that DevGuard remains fully operational via deterministic static analysis.
    """

    async def analyze_diff(
        self, diff_summary: DiffSummary, repo_name: str, pr_title: str
    ) -> List[FindingBase]:
        logger.info("Using Fallback LLM provider (no LLM configured). Relying solely on deterministic static analysis.")
        return []
