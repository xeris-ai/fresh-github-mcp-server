# app/common/types.py

from typing import List, Optional, Union
from pydantic import BaseModel, Field

class GitHubAuthor(BaseModel):
    name: str
    email: str
    date: str

class GitHubOwner(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    url: str
    html_url: str
    type: str

class GitHubRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: GitHubOwner
    html_url: str
    description: Optional[str]
    fork: bool
    url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    default_branch: str

class GithubFileContentLinks(BaseModel):
    self_: str = Field(..., alias="self")
    git: Optional[str]
    html: Optional[str]

class GitHubFileContent(BaseModel):
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str
    type: str
    content: Optional[str] = None
    encoding: Optional[str] = None
    _links: GithubFileContentLinks

class GitHubDirectoryContent(BaseModel):
    type: str
    size: int
    name: str
    path: str
    sha: str
    url: str
    git_url: str
    html_url: str
    download_url: Optional[str]

GitHubContent = Union[GitHubFileContent, List[GitHubDirectoryContent]]

class GitHubTreeEntry(BaseModel):
    path: str
    mode: str
    type: str
    size: Optional[int] = None
    sha: str
    url: str

class GitHubTree(BaseModel):
    sha: str
    url: str
    tree: List[GitHubTreeEntry]
    truncated: bool

class GitHubCommitTree(BaseModel):
    sha: str
    url: str

class GitHubCommitParent(BaseModel):
    sha: str
    url: str

class GitHubCommit(BaseModel):
    sha: str
    node_id: str
    url: str
    author: GitHubAuthor
    committer: GitHubAuthor
    message: str
    tree: GitHubCommitTree
    parents: List[GitHubCommitParent]

class GitHubListCommitTree(BaseModel):
    sha: str
    url: str

class GitHubListCommit(BaseModel):
    sha: str
    node_id: str
    commit: dict
    url: str
    html_url: str
    comments_url: str

GitHubListCommits = List[GitHubListCommit]

class GitHubReferenceObject(BaseModel):
    sha: str
    type: str
    url: str

class GitHubReference(BaseModel):
    ref: str
    node_id: str
    url: str
    object: GitHubReferenceObject

class GitHubIssueAssignee(BaseModel):
    login: str
    id: int
    avatar_url: str
    url: str
    html_url: str

class GitHubLabel(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: Optional[str] = None

class GitHubMilestone(BaseModel):
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    title: str
    description: str
    state: str

class GitHubIssue(BaseModel):
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: GitHubIssueAssignee
    labels: List[GitHubLabel]
    state: str
    locked: bool
    assignee: Optional[GitHubIssueAssignee]
    assignees: List[GitHubIssueAssignee]
    milestone: Optional[GitHubMilestone]
    comments: int
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    body: Optional[str]

class GitHubSearchResponse(BaseModel):
    total_count: int
    incomplete_results: bool
    items: List[GitHubRepository]

class GitHubPullRequestRef(BaseModel):
    label: str
    ref: str
    sha: str
    user: GitHubIssueAssignee
    repo: GitHubRepository

class GitHubPullRequest(BaseModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubIssueAssignee
    body: Optional[str]
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    merged_at: Optional[str]
    merge_commit_sha: Optional[str]
    assignee: Optional[GitHubIssueAssignee]
    assignees: List[GitHubIssueAssignee]
    requested_reviewers: List[GitHubIssueAssignee]
    labels: List[GitHubLabel]
    head: GitHubPullRequestRef
    base: GitHubPullRequestRef
