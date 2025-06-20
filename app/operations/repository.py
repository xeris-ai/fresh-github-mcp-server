# app/operations/repository.py

from typing import Optional

from app.common.utils import github_request, build_url
from app.common.types import (
    GitHubRepository,
    GitHubSearchResponse,
)

def create_repository(
    name: str,
    description: Optional[str] = None,
    private: Optional[bool] = None,
    auto_init: Optional[bool] = None,
) -> GitHubRepository:
    body = {
        "name": name,
    }
    if description is not None:
        body["description"] = description
    if private is not None:
        body["private"] = str(private)
    if auto_init is not None:
        body["auto_init"] = str(auto_init)

    response = github_request(
        "https://api.github.com/user/repos",
        method="POST",
        body=body,
    )
    return GitHubRepository.model_validate(response)

def search_repositories(
    query: str,
    page: int = 1,
    per_page: int = 30,
) -> GitHubSearchResponse:
    url = build_url(
        "https://api.github.com/search/repositories",
        {
            "q": query,
            "page": page,
            "per_page": per_page,
        },
    )
    response = github_request(url)
    return GitHubSearchResponse.model_validate(response)

def fork_repository(
    owner: str,
    repo: str,
    organization: Optional[str] = None,
) -> GitHubRepository:
    base_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    url = build_url(base_url, {"organization": organization} if organization else {})
    response = github_request(url, method="POST")
    # parent/source fields are not in the base model, so parse as dict and attach if needed
    repo_obj = GitHubRepository.model_validate(response)
    # Optionally, you can handle parent/source fields here if needed
    return repo_obj
