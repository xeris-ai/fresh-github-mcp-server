# app/operations/pulls.py

from typing import Optional, List, Literal, Dict, Any, Union
from pydantic import BaseModel, Field

from app.common.utils import github_request, build_url
from app.common.types import GitHubPullRequest, GitHubIssueAssignee, GitHubRepository

# --- Schemas ---

class PullRequestFile(BaseModel):
    sha: str
    filename: str
    status: Literal['added', 'removed', 'modified', 'renamed', 'copied', 'changed', 'unchanged']
    additions: int
    deletions: int
    changes: int
    blob_url: str
    raw_url: str
    contents_url: str
    patch: Optional[str] = None

class StatusCheck(BaseModel):
    url: str
    state: Literal['error', 'failure', 'pending', 'success']
    description: Optional[str]
    target_url: Optional[str]
    context: str
    created_at: str
    updated_at: str

class CombinedStatus(BaseModel):
    state: Literal['error', 'failure', 'pending', 'success']
    statuses: List[StatusCheck]
    sha: str
    total_count: int

class PullRequestCommentLinks(BaseModel):
    self_: Dict[str, str] = Field(..., alias="self")
    html: Dict[str, str]
    pull_request: Dict[str, str]

class PullRequestComment(BaseModel):
    url: str
    id: int
    node_id: str
    pull_request_review_id: Optional[int]
    diff_hunk: str
    path: Optional[str]
    position: Optional[int]
    original_position: Optional[int]
    commit_id: str
    original_commit_id: str
    user: GitHubIssueAssignee
    body: str
    created_at: str
    updated_at: str
    html_url: str
    pull_request_url: str
    author_association: str
    _links: PullRequestCommentLinks

class PullRequestReview(BaseModel):
    id: int
    node_id: str
    user: GitHubIssueAssignee
    body: Optional[str]
    state: Literal['APPROVED', 'CHANGES_REQUESTED', 'COMMENTED', 'DISMISSED', 'PENDING']
    html_url: str
    pull_request_url: str
    commit_id: str
    submitted_at: Optional[str]
    author_association: str

# --- Input Schemas ---

class CreatePullRequestInput(BaseModel):
    owner: str
    repo: str
    title: str
    body: Optional[str] = None
    head: str
    base: str
    draft: Optional[bool] = None
    maintainer_can_modify: Optional[bool] = None

class ListPullRequestsInput(BaseModel):
    owner: str
    repo: str
    state: Optional[Literal['open', 'closed', 'all']] = None
    head: Optional[str] = None
    base: Optional[str] = None
    sort: Optional[Literal['created', 'updated', 'popularity', 'long-running']] = None
    direction: Optional[Literal['asc', 'desc']] = None
    per_page: Optional[int] = None
    page: Optional[int] = None

class CreatePullRequestReviewInput(BaseModel):
    owner: str
    repo: str
    pull_number: int
    commit_id: Optional[str] = None
    body: str
    event: Literal['APPROVE', 'REQUEST_CHANGES', 'COMMENT']
    comments: Optional[List[Dict[str, Any]]] = None

class MergePullRequestInput(BaseModel):
    owner: str
    repo: str
    pull_number: int
    commit_title: Optional[str] = None
    commit_message: Optional[str] = None
    merge_method: Optional[Literal['merge', 'squash', 'rebase']] = None

class UpdatePullRequestBranchInput(BaseModel):
    owner: str
    repo: str
    pull_number: int
    expected_head_sha: Optional[str] = None

# --- Functions ---

def create_pull_request(params: Dict[str, Any]) -> GitHubPullRequest:
    data = CreatePullRequestInput(**params)
    owner, repo = data.owner, data.repo
    body = data.model_dump(exclude={'owner', 'repo'}, exclude_none=True)
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        method="POST",
        body=body,
    )
    return GitHubPullRequest.model_validate(response)

def get_pull_request(owner: str, repo: str, pull_number: int) -> GitHubPullRequest:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    )
    return GitHubPullRequest.model_validate(response)

def list_pull_requests(owner: str, repo: str, options: Dict[str, Any]) -> List[GitHubPullRequest]:
    params = ListPullRequestsInput(owner=owner, repo=repo, **options)
    url = build_url(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        params.model_dump(exclude={'owner', 'repo'}, exclude_none=True)
    )
    response = github_request(url)
    return [GitHubPullRequest.model_validate(pr) for pr in response]

def create_pull_request_review(owner: str, repo: str, pull_number: int, options: Dict[str, Any]) -> PullRequestReview:
    data = CreatePullRequestReviewInput(owner=owner, repo=repo, pull_number=pull_number, **options)
    body = data.model_dump(exclude={'owner', 'repo', 'pull_number'}, exclude_none=True)
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
        method="POST",
        body=body,
    )
    return PullRequestReview.model_validate(response)

def merge_pull_request(owner: str, repo: str, pull_number: int, options: Dict[str, Any]) -> Dict[str, Any]:
    data = MergePullRequestInput(owner=owner, repo=repo, pull_number=pull_number, **options)
    body = data.model_dump(exclude={'owner', 'repo', 'pull_number'}, exclude_none=True)
    return github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/merge",
        method="PUT",
        body=body,
    )

def get_pull_request_files(owner: str, repo: str, pull_number: int) -> List[PullRequestFile]:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    )
    return [PullRequestFile.model_validate(f) for f in response]

def update_pull_request_branch(owner: str, repo: str, pull_number: int, expected_head_sha: Optional[str] = None) -> None:
    body = {"expected_head_sha": expected_head_sha} if expected_head_sha else None
    github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/update-branch",
        method="PUT",
        body=body,
    )

def get_pull_request_comments(owner: str, repo: str, pull_number: int) -> List[PullRequestComment]:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments"
    )
    return [PullRequestComment.model_validate(c) for c in response]

def get_pull_request_reviews(owner: str, repo: str, pull_number: int) -> List[PullRequestReview]:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    )
    return [PullRequestReview.model_validate(r) for r in response]

def get_pull_request_status(owner: str, repo: str, pull_number: int) -> CombinedStatus:
    pr = get_pull_request(owner, repo, pull_number)
    sha = pr.head.sha
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/status"
    )
    return CombinedStatus.model_validate(response)
