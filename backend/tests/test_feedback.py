from app.engine.llm.base import REVIEW_SYSTEM_PROMPT
from app.engine.static_analyzer import StaticAnalyzer
from app.models.finding import Finding
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.services.diff_parser import DiffParser


def test_feedback_submission(client, db_session):
    repo = Repository(
        owner="testowner",
        name="testrepo",
        full_name="testowner/testrepo",
        html_url="https://github.com/testowner/testrepo"
    )
    db_session.add(repo)
    db_session.flush()

    pr = PullRequest(
        repository_id=repo.id,
        number=1,
        title="Test PR",
        author="alice",
        base_sha="abc1",
        head_sha="def2",
        html_url="https://github.com/testowner/testrepo/pull/1",
        diff_url="https://github.com/testowner/testrepo/pull/1.diff"
    )
    db_session.add(pr)
    db_session.flush()

    job = ReviewJob(
        pull_request_id=pr.id,
        commit_sha="def2",
        idempotency_key="pr-1-commit-def2",
        status="COMPLETED"
    )
    db_session.add(job)
    db_session.flush()

    finding = Finding(
        review_job_id=job.id,
        file_path="app.py",
        line_start=10,
        severity="high",
        category="security",
        title="SQL Injection",
        message="SQL query with string format",
        detection_source="deterministic",
        rule_id="VULN-001"
    )
    db_session.add(finding)
    db_session.commit()

    # Submit feedback
    resp = client.post(
        f"/api/v1/findings/{finding.id}/feedback",
        json={"finding_id": finding.id, "feedback_type": "helpful", "comment": "Great catch!"}
    )
    assert resp.status_code == 201
    assert resp.json()["feedback_type"] == "helpful"
    assert resp.json()["comment"] == "Great catch!"

def test_prompt_injection_containment(prompt_injection_diff):
    diff_summary = DiffParser.parse_diff(prompt_injection_diff)
    findings = StaticAnalyzer.analyze(diff_summary)

    # Static analyzer processes markdown without executing malicious override
    assert isinstance(findings, list)

    # Verify that the system prompt explicitly quarantines untrusted code
    assert "UNTRUSTED INPUT" in REVIEW_SYSTEM_PROMPT
    assert "PROMPT INJECTION" in REVIEW_SYSTEM_PROMPT
