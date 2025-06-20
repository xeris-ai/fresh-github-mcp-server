# app/operations/search.py

from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

from app.common.utils import github_request, build_url
from app.common.types import GitHubSearchResponse

class SearchOptions(BaseModel):
    q: str
    order: Optional[Literal["asc", "desc"]] = None
    page: Optional[int] = Field(1, ge=1)
    per_page: Optional[int] = Field(30, ge=1, le=100)

class SearchUsersOptions(SearchOptions):
    sort: Optional[Literal["followers", "repositories", "joined"]] = None

class SearchIssuesOptions(SearchOptions):
    sort: Optional[
        Literal[
            "comments",
            "reactions",
            "reactions-+1",
            "reactions--1",
            "reactions-smile",
            "reactions-thinking_face",
            "reactions-heart",
            "reactions-tada",
            "interactions",
            "created",
            "updated",
        ]
    ] = None

def search_code(params: Dict[str, Any]) -> Dict[str, Any]:
    opts = SearchOptions(**params)
    url = build_url("https://api.github.com/search/code", opts.model_dump(exclude_none=True))
    return github_request(url)

def search_issues(params: Dict[str, Any]) -> GitHubSearchResponse:
    opts = SearchIssuesOptions(**params)
    url = build_url("https://api.github.com/search/issues", opts.model_dump(exclude_none=True))
    response = github_request(url)
    return GitHubSearchResponse.model_validate(response)

def search_users(params: Dict[str, Any]) -> Dict[str, Any]:
    opts = SearchUsersOptions(**params)
    url = build_url("https://api.github.com/search/users", opts.model_dump(exclude_none=True))
    return github_request(url)
