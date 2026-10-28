import asyncio
import re
from typing import Any, Dict, Optional, Tuple

import httpx

from app.core.config import settings
from app.core.exceptions import GitHubAPIException
from app.core.logging import logger


class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = settings.GITHUB_API_BASE.rstrip("/")
        self.timeout = httpx.Timeout(15.0, connect=5.0)

    def _get_headers(self, accept: str = "application/vnd.github.v3+json") -> Dict[str, str]:
        headers = {
            "Accept": accept,
            "User-Agent": "DevGuard-AI/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request_with_retry(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, max_retries: int = 3
    ) -> httpx.Response:
        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, headers=headers)

                    # Handle rate limiting
                    if response.status_code == 403 and "rate limit" in response.text.lower():
                        reset_time = response.headers.get("x-ratelimit-reset", "unknown")
                        logger.warning(f"GitHub API rate limit hit on attempt {attempt+1}. Reset at: {reset_time}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise GitHubAPIException("GitHub API rate limit exceeded. Provide a GITHUB_TOKEN to increase limit.", status_code=429)

                    if response.status_code in (500, 502, 503, 504) and attempt < max_retries - 1:
                        logger.warning(f"GitHub API server error {response.status_code}. Retrying in {2 ** attempt}s...")
                        await asyncio.sleep(2 ** attempt)
                        continue

                    if response.status_code == 404:
                        raise GitHubAPIException(f"Resource not found on GitHub: {url}", status_code=404)

                    if response.status_code >= 400:
                        raise GitHubAPIException(
                            f"GitHub API error {response.status_code}: {response.text[:200]}",
                            status_code=response.status_code
                        )

                    return response
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Network error contacting GitHub ({url}): {e}. Attempt {attempt+1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise GitHubAPIException(f"Failed to communicate with GitHub API after {max_retries} attempts: {last_error}")

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = await self._request_with_retry("GET", url, headers=self._get_headers())
        return response.json()

    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        response = await self._request_with_retry("GET", url, headers=self._get_headers())
        return response.json()

    async def get_pull_request_diff(self, owner: str, repo: str, pull_number: int) -> str:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        headers = self._get_headers(accept="application/vnd.github.v3.diff")
        response = await self._request_with_retry("GET", url, headers=headers)
        return response.text

    async def get_rate_limit(self) -> Dict[str, Any]:
        url = f"{self.base_url}/rate_limit"
        try:
            response = await self._request_with_retry("GET", url, headers=self._get_headers())
            return response.json()
        except Exception as e:
            logger.warning(f"Could not retrieve rate limit: {e}")
            return {"rate": {"remaining": 60, "limit": 60}}

    @staticmethod
    def parse_repo_and_pr_url(url: str) -> Tuple[str, str, Optional[int]]:
        """
        Parses URLs like:
        - https://github.com/facebook/react/pull/1234
        - https://github.com/facebook/react
        - facebook/react
        Returns (owner, repo, pr_number)
        """
        url = url.strip()
        pr_match = re.match(r"^(?:https?://github\.com/)?([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)/pull/(\d+)", url)
        if pr_match:
            return pr_match.group(1), pr_match.group(2), int(pr_match.group(3))

        repo_match = re.match(r"^(?:https?://github\.com/)?([a-zA-Z0-9_\-\.]+)/([a-zA-Z0-9_\-\.]+)", url)
        if repo_match:
            repo_name = repo_match.group(2)
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]
            return repo_match.group(1), repo_name, None

        raise ValueError("Invalid GitHub URL or repository format")
