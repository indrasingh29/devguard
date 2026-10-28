from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import sanitize_repo_url
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.schemas.review import ReviewJobCreateRequest, ReviewJobResponse
from app.services.review_orchestrator import ReviewOrchestrator

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/start", response_model=ReviewJobResponse, status_code=status.HTTP_200_OK)
async def start_review(req: ReviewJobCreateRequest, db: Session = Depends(get_db)):
    """
    Trigger a full pull request analysis job. Runs deterministic static analysis
    (and optional model integration if requested). Returns full job findings.
    """
    try:
        clean_name = sanitize_repo_url(req.repo_full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        job = await ReviewOrchestrator.run_review(
            db=db,
            repo_full_name=clean_name,
            pull_number=req.pull_number,
            mode=req.mode
        )
        return ReviewOrchestrator.serialize_job_response(job)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute review: {str(e)}"
        )

@router.get("/{job_id}", response_model=ReviewJobResponse)
def get_review_job(job_id: int, db: Session = Depends(get_db)):
    """
    Get detailed results and findings for a specific review job.
    """
    job = db.scalar(select(ReviewJob).where(ReviewJob.id == job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review job not found")

    return ReviewOrchestrator.serialize_job_response(job)

@router.get("", response_model=List[ReviewJobResponse])
def list_review_history(
    repo_full_name: Optional[str] = Query(None, description="Filter by repository name"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by job status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List review history with pagination, status filtering, and repository search.
    """
    stmt = (
        select(ReviewJob)
        .join(PullRequest, ReviewJob.pull_request_id == PullRequest.id)
        .join(Repository, PullRequest.repository_id == Repository.id)
        .order_by(desc(ReviewJob.created_at))
    )

    if repo_full_name:
        stmt = stmt.where(Repository.full_name.ilike(f"%{repo_full_name}%"))

    if status_filter:
        stmt = stmt.where(ReviewJob.status == status_filter.upper())

    stmt = stmt.limit(limit).offset(offset)
    jobs = db.scalars(stmt).all()

    return [ReviewOrchestrator.serialize_job_response(j) for j in jobs]
