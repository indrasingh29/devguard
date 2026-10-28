from typing import List

from app.core.logging import logger
from app.engine.deduplicator import FindingDeduplicator
from app.engine.rules.bugs import check_bugs
from app.engine.rules.quality import check_quality
from app.engine.rules.secrets import check_secrets
from app.engine.rules.security import check_security
from app.engine.rules.tests import check_test_coverage
from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary


class StaticAnalyzer:
    """
    High-performance deterministic static analysis suite.
    Runs without external dependencies or LLM APIs.
    """

    @classmethod
    def analyze(cls, diff_summary: DiffSummary) -> List[FindingBase]:
        raw_findings: List[FindingBase] = []

        for file in diff_summary.files:
            # Check secret leaks
            raw_findings.extend(check_secrets(file))
            # Check security vulnerabilities
            raw_findings.extend(check_security(file))
            # Check bug risks & error handling
            raw_findings.extend(check_bugs(file))
            # Check code quality & maintainability
            raw_findings.extend(check_quality(file))

        # Check PR-wide test sufficiency
        raw_findings.extend(check_test_coverage(diff_summary))

        # Deduplicate and validate
        deduped = FindingDeduplicator.validate_and_filter(raw_findings, diff_summary)
        logger.info(f"Deterministic static analyzer produced {len(deduped)} findings across {len(diff_summary.files)} files")
        return deduped
