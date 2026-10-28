from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import sanitize_repo_url
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.schemas.repository import (
    RepositoryConnectRequest,
    RepositoryResponse,
)
from app.services.github_service import GitHubService

router = APIRouter(prefix="/repositories", tags=["Repositories"])

@router.post("/connect", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def connect_repository(req: RepositoryConnectRequest, db: Session = Depends(get_db)):
    """
    Connect a GitHub repository by URL or owner/name. Validates repository access with GitHub.
    """
    try:
        clean_name = sanitize_repo_url(req.repo_input)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Check if already exists in DB
    existing = db.scalar(select(Repository).where(Repository.full_name == clean_name))
    if existing:
        return existing

    owner, repo_name = clean_name.split("/")
    gh = GitHubService()
    try:
        repo_data = await gh.get_repository(owner, repo_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{clean_name}' not found or inaccessible on GitHub: {e}"
        )

    new_repo = Repository(
        owner=owner,
        name=repo_name,
        full_name=clean_name,
        default_branch=repo_data.get("default_branch", "main"),
        is_private=repo_data.get("private", False),
        html_url=repo_data.get("html_url", f"https://github.com/{clean_name}"),
    )
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)
    return new_repo

@router.get("", response_model=List[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    """
    List all connected repositories along with their PR and review counts.
    """
    repos = db.scalars(select(Repository).order_by(Repository.created_at.desc())).all()
    results = []
    for r in repos:
        pr_count = db.scalar(select(func.count(PullRequest.id)).where(PullRequest.repository_id == r.id)) or 0
        review_count = db.scalar(
            select(func.count(ReviewJob.id))
            .join(PullRequest, ReviewJob.pull_request_id == PullRequest.id)
            .where(PullRequest.repository_id == r.id)
        ) or 0

        resp = RepositoryResponse.model_validate(r)
        resp.open_prs_count = pr_count
        resp.total_reviews_count = review_count
        results.append(resp)

    return results

@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.scalar(select(Repository).where(Repository.id == repo_id))
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    pr_count = db.scalar(select(func.count(PullRequest.id)).where(PullRequest.repository_id == repo.id)) or 0
    review_count = db.scalar(
        select(func.count(ReviewJob.id))
        .join(PullRequest, ReviewJob.pull_request_id == PullRequest.id)
        .where(PullRequest.repository_id == repo.id)
    ) or 0

    resp = RepositoryResponse.model_validate(repo)
    resp.open_prs_count = pr_count
    resp.total_reviews_count = review_count
    return resp
