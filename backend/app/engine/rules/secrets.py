import re
from typing import List

from app.schemas.finding import FindingBase
from app.schemas.pull_request import ChangedFile
from app.services.diff_parser import DiffParser

SECRET_PATTERNS = [
    {
        "id": "SEC-001",
        "title": "Hardcoded AWS Access Key ID",
        "regex": re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        "severity": "critical",
        "remediation": "Revoke this key immediately and store credentials in environment variables or an AWS secrets manager."
    },
    {
        "id": "SEC-002",
        "title": "Hardcoded GitHub Personal Access Token",
        "regex": re.compile(r"(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{50,})"),
        "severity": "critical",
        "remediation": "Revoke this GitHub token immediately in GitHub settings and load via GITHUB_TOKEN environment variable."
    },
    {
        "id": "SEC-003",
        "title": "Hardcoded Private Key",
        "regex": re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----"),
        "severity": "critical",
        "remediation": "Never commit private cryptographic keys to version control. Use a secret manager or vault."
    },
    {
        "id": "SEC-004",
        "title": "Hardcoded API Key or Secret",
        "regex": re.compile(r"""(?i)(?:api_key|apikey|secret_key|app_secret|auth_token|client_secret)\s*[:=]\s*["']([A-Za-z0-9_\-\.]{16,})["']"""),
        "severity": "high",
        "remediation": "Move hardcoded secrets into secure environment variables (.env) and add .env to .gitignore."
    },
    {
        "id": "SEC-005",
        "title": "OpenAI / Anthropic API Key Leak",
        "regex": re.compile(r"(?:sk-[a-zA-Z0-9]{32,}|sk-ant-[a-zA-Z0-9_\-]{32,})"),
        "severity": "critical",
        "remediation": "Rotate this LLM provider key immediately. Store provider keys in server environment variables."
    }
]

def check_secrets(file: ChangedFile) -> List[FindingBase]:
    findings: List[FindingBase] = []

    # Skip binary files or lock files
    if file.is_binary or file.path.endswith(("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock")):
        return findings

    for hunk in file.hunks:
        added_lines = DiffParser.get_added_line_numbers(hunk)
        for line_num, line_content in added_lines:
            # Skip commented explanatory lines in markdown or docs unless explicitly looking like code
            if file.path.endswith((".md", ".txt")) and ("example" in line_content.lower() or "placeholder" in line_content.lower()):
                continue

            for pattern in SECRET_PATTERNS:
                if pattern["regex"].search(line_content):
                    findings.append(FindingBase(
                        file_path=file.path,
                        line_start=line_num,
                        line_end=line_num,
                        severity=pattern["severity"],
                        category="secret_leak",
                        title=pattern["title"],
                        message=f"Possible secret credential detected on line {line_num}. Committing secrets to repositories leads to credential compromise.",
                        evidence=line_content.strip()[:120],
                        suggested_remediation=pattern["remediation"],
                        detection_source="regex_secret",
                        confidence="deterministic",
                        rule_id=pattern["id"]
                    ))
                    break  # One secret match per line is enough

    return findings
