from typing import List

from app.schemas.finding import FindingBase
from app.schemas.pull_request import DiffSummary


def check_test_coverage(diff_summary: DiffSummary) -> List[FindingBase]:
    findings: List[FindingBase] = []

    # Check if any test files are included in the PR
    test_files = [
        f for f in diff_summary.files
        if any(t in f.path.lower() for t in ["test", "spec", "fixture", "__tests__"])
    ]

    has_test_modifications = len(test_files) > 0

    # Look for substantial business logic files modified without test coverage
    for file in diff_summary.files:
        is_code_file = file.path.endswith((".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".java"))
        is_test = any(t in file.path.lower() for t in ["test", "spec", "fixture", "__tests__", "migration"])
        is_config = file.path.endswith(("config.py", "settings.py", "vite.config.ts", "package.json"))

        if is_code_file and not is_test and not is_config and file.additions >= 25 and not has_test_modifications:
            findings.append(FindingBase(
                file_path=file.path,
                line_start=1,
                line_end=1,
                severity="medium",
                category="test_insufficiency",
                title="Significant Logic Changes Without Accompanying Tests",
                message=f"File '{file.path}' introduces {file.additions} added lines of logic, but this pull request contains zero test file updates.",
                evidence=f"{file.path}: +{file.additions} lines / -{file.deletions} lines",
                suggested_remediation=f"Add unit or integration tests verifying the new functionality in '{file.path}' to prevent regression.",
                detection_source="deterministic",
                confidence="deterministic",
                rule_id="TEST-001"
            ))

    return findings
