import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.engine.deduplicator import FindingDeduplicator
from app.engine.llm import get_llm_provider
from app.engine.static_analyzer import StaticAnalyzer
from app.models.finding import Finding
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.schemas.finding import FindingResponse
from app.schemas.review import ReviewJobResponse, SeverityCount
from app.services.diff_parser import DiffParser
from app.services.github_service import GitHubService


class ReviewOrchestrator:
    @classmethod
    async def run_review(
        cls,
        db: Session,
        repo_full_name: str,
        pull_number: int,
        mode: str = "deterministic"
    ) -> ReviewJob:
        start_time = time.time()
        logger.info(f"Starting review pipeline for {repo_full_name}#{pull_number} (mode: {mode})")

        # 1. Fetch metadata from GitHub
        owner, repo_name = repo_full_name.split("/")
        gh = GitHubService()
        pr_data = await gh.get_pull_request(owner, repo_name, pull_number)
        repo_data = await gh.get_repository(owner, repo_name)

        head_sha = pr_data["head"]["sha"]
        base_sha = pr_data["base"]["sha"]
        pr_title = pr_data.get("title", f"PR #{pull_number}")

        # 2. Persist or update Repository
        db_repo = db.scalar(select(Repository).where(Repository.full_name == repo_full_name))
        if not db_repo:
            db_repo = Repository(
                owner=owner,
                name=repo_name,
                full_name=repo_full_name,
                default_branch=repo_data.get("default_branch", "main"),
                is_private=repo_data.get("private", False),
                html_url=repo_data.get("html_url", f"https://github.com/{repo_full_name}"),
            )
            db.add(db_repo)
            db.flush()

        # 3. Persist or update PullRequest
        db_pr = db.scalar(
            select(PullRequest).where(
                PullRequest.repository_id == db_repo.id,
                PullRequest.number == pull_number
            )
        )
        if not db_pr:
            db_pr = PullRequest(
                repository_id=db_repo.id,
                number=pull_number,
                title=pr_title,
                state=pr_data.get("state", "open"),
                author=pr_data.get("user", {}).get("login", "unknown"),
                base_sha=base_sha,
                head_sha=head_sha,
                html_url=pr_data.get("html_url", f"https://github.com/{repo_full_name}/pull/{pull_number}"),
                diff_url=pr_data.get("diff_url", f"https://github.com/{repo_full_name}/pull/{pull_number}.diff"),
            )
            db.add(db_pr)
            db.flush()
        else:
            db_pr.title = pr_title
            db_pr.state = pr_data.get("state", "open")
            db_pr.head_sha = head_sha
            db_pr.base_sha = base_sha
            db.flush()

        # 4. Check Idempotency
        idempotency_key = f"pr-{db_pr.id}-sha-{head_sha[:12]}-{mode}"
        existing_job = db.scalar(select(ReviewJob).where(ReviewJob.idempotency_key == idempotency_key))
        if existing_job:
            if existing_job.status in ("QUEUED", "PROCESSING"):
                logger.info(f"Review job {existing_job.id} already active for {idempotency_key}")
                return existing_job
            elif existing_job.status == "COMPLETED":
                logger.info(f"Returning completed cached review job {existing_job.id}")
                return existing_job

        # 5. Create new ReviewJob
        job = ReviewJob(
            pull_request_id=db_pr.id,
            commit_sha=head_sha,
            idempotency_key=idempotency_key,
            status="PROCESSING",
            mode=mode,
            started_at=datetime.now(timezone.utc),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            # 6. Fetch raw diff & parse
            raw_diff = await gh.get_pull_request_diff(owner, repo_name, pull_number)
            diff_summary = DiffParser.parse_diff(raw_diff)

            # 7. Run Deterministic Analysis
            findings = StaticAnalyzer.analyze(diff_summary)

            # 8. Optional Model Integration
            if mode == "hybrid_llm" and settings.LLM_PROVIDER != "none":
                llm = get_llm_provider()
                llm_findings = await llm.analyze_diff(diff_summary, repo_full_name, pr_title)
                if llm_findings:
                    findings.extend(llm_findings)
                    findings = FindingDeduplicator.validate_and_filter(findings, diff_summary)

            # 9. Store findings in DB
            db_findings = []
            for f in findings:
                db_f = Finding(
                    review_job_id=job.id,
                    file_path=f.file_path,
                    line_start=f.line_start,
                    line_end=f.line_end,
                    severity=f.severity,
                    category=f.category,
                    title=f.title,
                    message=f.message,
                    evidence=f.evidence,
                    suggested_remediation=f.suggested_remediation,
                    detection_source=f.detection_source,
                    confidence=f.confidence,
                    rule_id=f.rule_id
                )
                db.add(db_f)
                db_findings.append(db_f)

            # 10. Update job statistics and completion status
            elapsed_ms = int((time.time() - start_time) * 1000)
            job.status = "COMPLETED"
            job.total_files_analyzed = diff_summary.total_files
            job.total_findings = len(findings)
            job.execution_time_ms = elapsed_ms
            job.completed_at = datetime.now(timezone.utc)
            job.summary = (
                f"Analyzed {diff_summary.total_files} changed files (+{diff_summary.total_additions}/-{diff_summary.total_deletions} lines). "
                f"Identified {len(findings)} findings ({sum(1 for f in findings if f.severity in ('critical', 'high'))} high/critical) "
                f"in {elapsed_ms}ms using {mode} engine."
            )
            db.commit()
            db.refresh(job)
            logger.info(f"Review job {job.id} completed successfully in {elapsed_ms}ms with {len(findings)} findings")
            return job

        except Exception as e:
            db.rollback()
            logger.error(f"Review pipeline error for job {job.id}: {e}")
            job.status = "FAILED"
            job.error_message = str(e)[:1000]
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise

    @classmethod
    def serialize_job_response(cls, job: ReviewJob) -> ReviewJobResponse:
        counts = SeverityCount()
        finding_responses = []

        for f in job.findings:
            if f.severity == "critical":
                counts.critical += 1
            elif f.severity == "high":
                counts.high += 1
            elif f.severity == "medium":
                counts.medium += 1
            elif f.severity == "low":
                counts.low += 1
            else:
                counts.info += 1

            feedback_type = f.feedback[0].feedback_type if f.feedback else None
            finding_responses.append(
                FindingResponse(
                    id=f.id,
                    review_job_id=f.review_job_id,
                    file_path=f.file_path,
                    line_start=f.line_start,
                    line_end=f.line_end,
                    severity=f.severity,
                    category=f.category,
                    title=f.title,
                    message=f.message,
                    evidence=f.evidence,
                    suggested_remediation=f.suggested_remediation,
                    detection_source=f.detection_source,
                    confidence=f.confidence,
                    rule_id=f.rule_id,
                    created_at=f.created_at,
                    feedback_type=feedback_type
                )
            )

        pr = job.pull_request
        repo = pr.repository if pr else None

        return ReviewJobResponse(
            id=job.id,
            pull_request_id=job.pull_request_id,
            commit_sha=job.commit_sha,
            idempotency_key=job.idempotency_key,
            status=job.status,
            mode=job.mode,
            total_files_analyzed=job.total_files_analyzed,
            total_findings=job.total_findings,
            summary=job.summary,
            error_message=job.error_message,
            execution_time_ms=job.execution_time_ms,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            updated_at=job.updated_at,
            severity_counts=counts,
            findings=finding_responses,
            repo_full_name=repo.full_name if repo else None,
            pr_number=pr.number if pr else None,
            pr_title=pr.title if pr else None
        )
