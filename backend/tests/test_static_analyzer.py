from app.engine.static_analyzer import StaticAnalyzer
from app.services.diff_parser import DiffParser


def test_clean_code_has_no_security_findings(clean_code_diff):
    diff_summary = DiffParser.parse_diff(clean_code_diff)
    findings = StaticAnalyzer.analyze(diff_summary)

    # Should have no security or secret findings
    security_findings = [f for f in findings if f.category in ("security", "secret_leak")]
    assert len(security_findings) == 0

def test_detect_secret_leaks(secret_leak_diff):
    diff_summary = DiffParser.parse_diff(secret_leak_diff)
    findings = StaticAnalyzer.analyze(diff_summary)

    rule_ids = {f.rule_id for f in findings}
    assert "SEC-001" in rule_ids  # AWS Key
    assert "SEC-002" in rule_ids  # GitHub Token
    assert "SEC-005" in rule_ids  # OpenAI Key

    for f in findings:
        assert f.category == "secret_leak"
        assert f.severity in ("critical", "high")
        assert f.detection_source == "regex_secret"

def test_detect_security_vulnerabilities(security_vulnerable_diff):
    diff_summary = DiffParser.parse_diff(security_vulnerable_diff)
    findings = StaticAnalyzer.analyze(diff_summary)

    rule_ids = {f.rule_id for f in findings}
    assert "VULN-001" in rule_ids  # SQL Injection
    assert "VULN-002" in rule_ids  # Command Injection

    sqli = next(f for f in findings if f.rule_id == "VULN-001")
    assert "SQL" in sqli.title
    assert sqli.severity == "critical"

def test_detect_bugs_and_error_handling(bug_risk_diff):
    diff_summary = DiffParser.parse_diff(bug_risk_diff)
    findings = StaticAnalyzer.analyze(diff_summary)

    rule_ids = {f.rule_id for f in findings}
    assert "BUG-001" in rule_ids  # Bare except
    assert "BUG-002" in rule_ids  # Mutable default
    assert "BUG-004" in rule_ids  # Tuple assert
