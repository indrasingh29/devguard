from fastapi import APIRouter, HTTPException, status

from app.core.security import sanitize_repo_url
from app.schemas.pull_request import DiffSummary, FetchPRRequest
from app.services.diff_parser import DiffParser
from app.services.github_service import GitHubService

router = APIRouter(prefix="/pull-requests", tags=["Pull Requests"])

@router.post("/fetch-diff", response_model=DiffSummary)
async def fetch_pr_diff(req: FetchPRRequest):
    """
    Fetches and parses a pull request diff from GitHub, returning changed files,
    hunks, additions, and deletions for UI inspection.
    """
    try:
        clean_name = sanitize_repo_url(req.repo_full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    owner, repo = clean_name.split("/")
    gh = GitHubService()

    try:
        raw_diff = await gh.get_pull_request_diff(owner, repo, req.pull_number)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch PR diff from GitHub: {e}"
        )

    try:
        diff_summary = DiffParser.parse_diff(raw_diff)
        return diff_summary
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
