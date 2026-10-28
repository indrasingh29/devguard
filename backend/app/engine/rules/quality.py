import re
from typing import List

from app.schemas.finding import FindingBase
from app.schemas.pull_request import ChangedFile
from app.services.diff_parser import DiffParser

QUALITY_PATTERNS = [
    {
        "id": "QUAL-001",
        "title": "Leftover Debugger or Breakpoint",
        "regex": re.compile(r"""\b(?:pdb\.set_trace|breakpoint\(\)|debugger;)\b"""),
        "severity": "high",
        "category": "maintainability",
        "message": "Interactive debug statements left in production code will halt execution or expose internals in production environments.",
        "remediation": "Remove debugger calls or replace with structured logging before merging."
    },
    {
        "id": "QUAL-002",
        "title": "Leftover Print / Console Log Statement",
        "regex": re.compile(r"""^\s*(?:console\.log|print)\s*\("""),
        "severity": "low",
        "category": "maintainability",
        "message": "Raw print or console.log statements clutter output streams and bypass log levels.",
        "remediation": "Use the application's structured logger (e.g. logger.info or logger.debug) instead of stdout prints."
    },
    {
        "id": "QUAL-003",
        "title": "Security Check or Linter Suppression",
        "regex": re.compile(r"""(?:#\s*nosec|#\s*noqa|//\s*eslint-disable-next-line|//\s*ts-ignore)"""),
        "severity": "medium",
        "category": "maintainability",
        "message": "Direct suppression of security or linter checks hides potential risks without documenting justification.",
        "remediation": "Resolve the root issue or provide a documented justification comment explaining why the suppression is safe."
    },
    {
        "id": "QUAL-004",
        "title": "Unresolved TODO or FIXME Marker",
        "regex": re.compile(r"""(?i)(?:#|//|\*)\s*(?:TODO|FIXME|XXX)\b(?!\s*\(#[0-9]+\))"""),
        "severity": "info",
        "category": "maintainability",
        "message": "Unassigned TODO / FIXME comment found without a reference issue ticket.",
        "remediation": "Link the TODO comment to a tracked GitHub issue (e.g., 'TODO(#123): ...') or resolve it before merge."
    }
]

def check_quality(file: ChangedFile) -> List[FindingBase]:
    findings: List[FindingBase] = []
    if file.is_binary:
        return findings

    # Skip test files for print or debug checks
    is_test_file = any(t in file.path.lower() for t in ["test", "spec", "fixture"])

    for hunk in file.hunks:
        added_lines = DiffParser.get_added_line_numbers(hunk)
        for line_num, line_content in added_lines:
            # Check deep nesting (indentation > 16 spaces)
            leading_spaces = len(line_content) - len(line_content.lstrip(' '))
            if leading_spaces >= 16 and not line_content.strip().startswith(("#", "//", "/*", "*")):
                findings.append(FindingBase(
                    file_path=file.path,
                    line_start=line_num,
                    line_end=line_num,
                    severity="low",
                    category="maintainability",
                    title="Deeply Nested Control Flow",
                    message="Control flow is nested 4 or more levels deep, significantly increasing cyclomatic complexity and reducing readability.",
                    evidence=line_content.strip()[:100],
                    suggested_remediation="Refactor nested blocks into early return guards or helper functions.",
                    detection_source="deterministic",
                    confidence="deterministic",
                    rule_id="QUAL-005"
                ))

            for pattern in QUALITY_PATTERNS:
                if is_test_file and pattern["id"] == "QUAL-002":
                    continue  # print in tests is acceptable
                if pattern["regex"].search(line_content):
                    findings.append(FindingBase(
                        file_path=file.path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=pattern["severity"],
                        category=pattern["category"],
                        title=pattern["title"],
                        message=f"{pattern['message']} (Line {line_num})",
                        evidence=line_content.strip()[:140],
                        suggested_remediation=pattern["remediation"],
                        detection_source="deterministic",
                        confidence="deterministic",
                        rule_id=pattern["id"]
                    ))

    return findings
