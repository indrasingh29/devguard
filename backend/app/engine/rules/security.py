import re
from typing import List

from app.schemas.finding import FindingBase
from app.schemas.pull_request import ChangedFile
from app.services.diff_parser import DiffParser

SECURITY_PATTERNS = [
    {
        "id": "VULN-001",
        "title": "Potential SQL Injection",
        "regex": re.compile(r"""(?i)(?:f["'].*(?:SELECT|INSERT|UPDATE|DELETE|FROM)\s+.*\{|(?:cursor\.execute|session\.execute|raw_sql)\s*\(\s*(?:f["']|.*%s|.*\.format\())"""),
        "severity": "critical",
        "category": "security",
        "message": "Dynamic string interpolation inside a SQL query detected. This allows arbitrary SQL injection attacks.",
        "remediation": "Use parameterized queries or ORM query builders (e.g., execute('SELECT * FROM users WHERE id = :id', {'id': user_id}))."
    },
    {
        "id": "VULN-002",
        "title": "Command Injection via shell=True or os.system",
        "regex": re.compile(r"""(?i)(?:subprocess\.(?:Popen|run|call|check_output)\s*\(.*shell\s*=\s*True|os\.system\s*\(|os\.popen\s*\()"""),
        "severity": "critical",
        "category": "security",
        "message": "Execution of system commands with shell=True or os.system can allow arbitrary command execution if input is tainted.",
        "remediation": "Avoid shell=True. Pass commands as a list of arguments (e.g. ['git', 'status']) and validate all user inputs."
    },
    {
        "id": "VULN-003",
        "title": "Arbitrary Code Execution via eval/exec",
        "regex": re.compile(r"""(?i)\b(?:eval|exec)\s*\((?!.*(?:ast\.literal_eval))"""),
        "severity": "critical",
        "category": "security",
        "message": "Use of eval() or exec() executes arbitrary code strings at runtime, creating severe Remote Code Execution (RCE) vectors.",
        "remediation": "Use safe alternatives such as ast.literal_eval for parsing primitives or structured JSON/YAML parsers."
    },
    {
        "id": "VULN-004",
        "title": "Insecure Deserialization via pickle or unsafe YAML loader",
        "regex": re.compile(r"""(?i)(?:pickle\.(?:loads|load)\s*\(|yaml\.load\s*\([^,)]*\)(?!.*Loader=yaml\.SafeLoader)|yaml\.load\s*\(.*Loader\s*=\s*yaml\.Loader)"""),
        "severity": "high",
        "category": "security",
        "message": "Deserializing untrusted data with pickle or unsafe YAML loader can lead to arbitrary code execution.",
        "remediation": "Use json.loads() or yaml.safe_load() which do not instantiate arbitrary objects during parsing."
    },
    {
        "id": "VULN-005",
        "title": "Weak Cryptographic Hash (MD5 / SHA1)",
        "regex": re.compile(r"""(?i)hashlib\.(?:md5|sha1)\s*\("""),
        "severity": "medium",
        "category": "security",
        "message": "MD5 and SHA-1 have known collision vulnerabilities and should not be used for security purposes or password hashing.",
        "remediation": "Use SHA-256 (hashlib.sha256) for general hashing, or Argon2 / bcrypt for password storage."
    },
    {
        "id": "VULN-006",
        "title": "Potential Path Traversal in File Access",
        "regex": re.compile(r"""(?i)open\s*\(\s*(?:f["'].*\{|path\s*\+\s*["']|\w+\s*\+\s*["']/|\w+\.get\(["']path["']\))"""),
        "severity": "high",
        "category": "security",
        "message": "Direct path concatenation in open() may allow directory traversal (e.g. '../../etc/passwd') if input is untrusted.",
        "remediation": "Resolve absolute paths with os.path.abspath and verify with os.path.commonpath([base_dir, target_path]) == base_dir."
    }
]

def check_security(file: ChangedFile) -> List[FindingBase]:
    findings: List[FindingBase] = []
    if file.is_binary:
        return findings

    for hunk in file.hunks:
        added_lines = DiffParser.get_added_line_numbers(hunk)
        for line_num, line_content in added_lines:
            for pattern in SECURITY_PATTERNS:
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
