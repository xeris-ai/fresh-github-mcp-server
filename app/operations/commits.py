# app/operations/commits.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.common.utils import github_request, build_url
from app.common.types import GitHubListCommit

class ListCommitsInput(BaseModel):
    owner: str
    repo: str
    sha: Optional[str] = None
    page: Optional[int] = None
    per_page: Optional[int]

def list_commits(
    owner: str,
    repo: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    sha: Optional[str] = None
) -> List[GitHubListCommit]:
    params = ListCommitsInput(
        owner=owner,
        repo=repo,
        sha=sha,
        page=page,
        per_page=per_page
    )
    url = build_url(
        f"https://api.github.com/repos/{owner}/{repo}/commits",
        params.model_dump(
            exclude={"owner", "repo"},
            by_alias=True,
            exclude_none=True
        )
    )

    response = github_request(url)
    return [GitHubListCommit.model_validate(commit) for commit in response]
