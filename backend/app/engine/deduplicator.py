from typing import Dict, List, Set, Tuple

from app.core.logging import logger
from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary

SEVERITY_ORDER = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
}

class FindingDeduplicator:
    @classmethod
    def deduplicate(cls, findings: List[FindingBase]) -> List[FindingBase]:
        """
        Deduplicates findings on the same file, line, and category,
        retaining the highest severity finding.
        """
        dedup_map: Dict[Tuple[str, int, str], FindingBase] = {}

        for finding in findings:
            key = (finding.file_path, finding.line_start or 0, finding.category)
            existing = dedup_map.get(key)
            if not existing:
                dedup_map[key] = finding
            else:
                existing_score = SEVERITY_ORDER.get(existing.severity, 0)
                new_score = SEVERITY_ORDER.get(finding.severity, 0)
                if new_score > existing_score:
                    dedup_map[key] = finding

        return list(dedup_map.values())

    @classmethod
    def validate_and_filter(cls, findings: List[FindingBase], diff_summary: DiffSummary) -> List[FindingBase]:
        """
        Strict validation: Ensures all reported findings reference real files
        and valid lines present in the diff, preventing LLM hallucinations.
        """
        valid_files = {f.path for f in diff_summary.files}
        valid_line_map: Dict[str, Set[int]] = {}

        for f in diff_summary.files:
            valid_line_map[f.path] = set()
            for hunk in f.hunks:
                current_new = hunk.new_start
                for line in hunk.lines:
                    if not line.startswith("-"):
                        valid_line_map[f.path].add(current_new)
                        current_new += 1

        validated: List[FindingBase] = []
        for finding in findings:
            # 1. Check if file is in diff
            if finding.file_path not in valid_files:
                logger.warning(f"Dropping finding for non-existent file in PR: {finding.file_path}")
                continue

            # 2. Line check (if specified and > 1)
            if finding.line_start and finding.line_start > 1:
                file_lines = valid_line_map.get(finding.file_path, set())
                # If the line is within +/- 2 lines of changed lines or valid, accept it
                near_match = any(abs(finding.line_start - line_num) <= 2 for line_num in file_lines)
                if not near_match and file_lines:
                    logger.warning(
                        f"Adjusting or flagging hallucinated line {finding.line_start} for {finding.file_path}"
                    )
                    # If model picked an invalid line, fallback to first changed line of file
                    finding.line_start = min(file_lines)
                    finding.line_end = finding.line_start

            validated.append(finding)

        return cls.deduplicate(validated)
