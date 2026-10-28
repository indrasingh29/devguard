import re
from typing import List

from app.schemas.finding import FindingBase
from app.schemas.pull_request import ChangedFile
from app.services.diff_parser import DiffParser

BUG_PATTERNS = [
    {
        "id": "BUG-001",
        "title": "Bare or Generic Exception Handler",
        "regex": re.compile(r"""^\s*except\s*:\s*$|^\s*except\s+BaseException\s*:"""),
        "severity": "medium",
        "category": "error_handling",
        "message": "Catching bare 'except:' or 'BaseException' catches system-exiting exceptions like KeyboardInterrupt and hides unexpected syntax or type errors.",
        "remediation": "Catch specific exception types (e.g. 'except (ValueError, KeyError):') or at minimum catch 'Exception:'."
    },
    {
        "id": "BUG-002",
        "title": "Mutable Default Argument in Function Definition",
        "regex": re.compile(r"""def\s+[a-zA-Z0-9_]+\s*\([^)]*=\s*(?:\[\]|\{\}|set\(\))"""),
        "severity": "high",
        "category": "bug_risk",
        "message": "Default parameter values are evaluated once when the function is defined. A mutable default is shared across all function calls.",
        "remediation": "Use None as the default value and initialize the collection inside the function body: if arg is None: arg = []."
    },
    {
        "id": "BUG-003",
        "title": "Comparison to None Using Equality Operator",
        "regex": re.compile(r"""\b(?:==|!=)\s*None\b|\bNone\s*(?:==|!=)"""),
        "severity": "low",
        "category": "bug_risk",
        "message": "Comparisons to None should use identity comparison ('is None' or 'is not None') rather than equality ('== None').",
        "remediation": "Replace '== None' with 'is None' and '!= None' with 'is not None'."
    },
    {
        "id": "BUG-004",
        "title": "Tuple Passed to Assert Statement",
        "regex": re.compile(r"""^\s*assert\s*\([^,]+,\s*[^)]+\)"""),
        "severity": "high",
        "category": "bug_risk",
        "message": "Assert with a parenthesized tuple (e.g. assert (x, 'msg')) always evaluates to True in Python because non-empty tuples are truthy.",
        "remediation": "Remove the outer parentheses: 'assert condition, message'."
    },
    {
        "id": "BUG-005",
        "title": "Unclosed File Resource Without Context Manager",
        "regex": re.compile(r"""^\s*[a-zA-Z0-9_]+\s*=\s*open\s*\([^)]+\)\s*$"""),
        "severity": "medium",
        "category": "bug_risk",
        "message": "Opening files without a 'with' context manager can lead to file descriptor leaks if an exception occurs before .close().",
        "remediation": "Use 'with open(...) as f:' to guarantee proper cleanup."
    }
]

def check_bugs(file: ChangedFile) -> List[FindingBase]:
    findings: List[FindingBase] = []
    if file.is_binary:
        return findings

    for hunk in file.hunks:
        added_lines = DiffParser.get_added_line_numbers(hunk)
        for line_num, line_content in added_lines:
            for pattern in BUG_PATTERNS:
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
