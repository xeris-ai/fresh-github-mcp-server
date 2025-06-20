# issues/operations/issues.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.common.utils import github_request, build_url
from app.common.types import GitHubIssue

class GetIssueInput(BaseModel):
    owner: str
    repo: str
    issue_number: int

class IssueCommentInput(BaseModel):
    owner: str
    repo: str
    issue_number: int
    body: str

class CreateIssueInput(BaseModel):
    owner: str
    repo: str
    title: str
    body: Optional[str] = None
    assignees: Optional[List[str]] = None
    milestone: Optional[int] = None
    labels: Optional[List[str]] = None

class ListIssuesInput(BaseModel):
    owner: str
    repo: str
    direction: Optional[str] = None
    labels: Optional[List[str]] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    since: Optional[str] = None
    sort: Optional[str] = None
    state: Optional[str] = None

class UpdateIssueInput(BaseModel):
    owner: str
    repo: str
    issue_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    assignees: Optional[List[str]] = None
    milestone: Optional[int] = None
    labels: Optional[List[str]] = None
    state: Optional[str] = None

def get_issue(owner: str, repo: str, issue_number: int) -> GitHubIssue:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    )
    return GitHubIssue.model_validate(response)

def add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments",
        method="POST",
        body={"body": body},
    )
    return response

def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
) -> GitHubIssue:
    payload = {
        "title": title,
        "body": body,
        "assignees": assignees,
        "milestone": milestone,
        "labels": labels,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        method="POST",
        body=payload,
    )
    return GitHubIssue.model_validate(response)

def list_issues(
    owner: str,
    repo: str,
    direction: Optional[str] = None,
    labels: Optional[List[str]] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    since: Optional[str] = None,
    sort: Optional[str] = None,
    state: Optional[str] = None,
) -> List[GitHubIssue]:
    params = {
        "direction": direction,
        "labels": ",".join(labels) if labels else None,
        "page": page,
        "per_page": per_page,
        "since": since,
        "sort": sort,
        "state": state,
    }
    params = {k: v for k, v in params.items() if v is not None}
    url = build_url(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        params
    )
    response = github_request(url)
    return [GitHubIssue.model_validate(item) for item in response]

def update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
    state: Optional[str] = None,
) -> GitHubIssue:
    payload = {
        "title": title,
        "body": body,
        "assignees": assignees,
        "milestone": milestone,
        "labels": labels,
        "state": state,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}",
        method="PATCH",
        body=payload,
    )
    return GitHubIssue.model_validate(response)
