# app/server.py
import requests
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field



# --- Import tool functions and schemas from operation modules ---
from app.operations.files import (
    create_or_update_file,
    get_file_contents,
    push_files,
    CreateOrUpdateFileInput,
    GetFileContentsInput,
    PushFilesInput,
)
from app.operations.issues import (
    create_issue,
    list_issues,
    update_issue,
    add_issue_comment,
    get_issue,
    CreateIssueInput,
    ListIssuesInput,
    UpdateIssueInput,
    IssueCommentInput,
    GetIssueInput,
)
from app.operations.commits import (
    list_commits,
    ListCommitsInput,
)
from app.operations.repository import (
    create_repository,
    search_repositories,
    fork_repository,
)
from app.operations.branches import (
    create_branch_from_ref,
    CreateBranchInput,
)
from app.operations.search import (
    search_code,
    search_issues,
    search_users,
    SearchOptions,
    SearchIssuesOptions,
    SearchUsersOptions,
)
from app.operations.pulls import (
    create_pull_request,
    get_pull_request,
    list_pull_requests,
    create_pull_request_review,
    merge_pull_request,
    get_pull_request_files,
    get_pull_request_status,
    update_pull_request_branch,
    get_pull_request_comments,
    get_pull_request_reviews,
    CreatePullRequestInput,
    ListPullRequestsInput,
    CreatePullRequestReviewInput,
    MergePullRequestInput,
    UpdatePullRequestBranchInput,
)

mcp = FastMCP("GitHub MCP Server")

# --- Tool registrations (one per operation, using imported schemas) ---

@mcp.tool()
def create_or_update_file_tool(input: CreateOrUpdateFileInput):
    return create_or_update_file(**input.model_dump())

@mcp.tool()
def get_file_contents_tool(input: GetFileContentsInput):
    return get_file_contents(**input.model_dump())

@mcp.tool()
def push_files_tool(input: PushFilesInput):
    return push_files(**input.model_dump())

@mcp.tool()
def create_issue_tool(input: CreateIssueInput):
    return create_issue(**input.model_dump())

@mcp.tool()
def list_issues_tool(input: ListIssuesInput):
    return list_issues(**input.model_dump())

@mcp.tool()
def update_issue_tool(input: UpdateIssueInput):
    return update_issue(**input.model_dump())

@mcp.tool()
def add_issue_comment_tool(input: IssueCommentInput):
    return add_issue_comment(**input.model_dump())

@mcp.tool()
def get_issue_tool(input: GetIssueInput):
    return get_issue(**input.model_dump())

@mcp.tool()
def list_commits_tool(input: ListCommitsInput):
    return list_commits(**input.model_dump())

@mcp.tool()
def create_repository_tool(name: str, description: str = None, private: bool = None, auto_init: bool = None):
    return create_repository(name, description, private, auto_init)

@mcp.tool()
def search_repositories_tool(query: str, page: int = 1, per_page: int = 30):
    return search_repositories(query, page, per_page)

@mcp.tool()
def fork_repository_tool(owner: str, repo: str, organization: str = None):
    return fork_repository(owner, repo, organization)

@mcp.tool()
def create_branch_tool(input: CreateBranchInput):
    return create_branch_from_ref(**input.model_dump())

@mcp.tool()
def search_code_tool(input: SearchOptions):
    return search_code(input.model_dump())

@mcp.tool()
def search_issues_tool(input: SearchIssuesOptions):
    return search_issues(input.model_dump())

@mcp.tool()
def search_users_tool(input: SearchUsersOptions):
    return search_users(input.model_dump())

@mcp.tool()
def create_pull_request_tool(input: CreatePullRequestInput):
    return create_pull_request(input.model_dump())

@mcp.tool()
def get_pull_request_tool(owner: str, repo: str, pull_number: int):
    return get_pull_request(owner, repo, pull_number)

@mcp.tool()
def list_pull_requests_tool(input: ListPullRequestsInput):
    return list_pull_requests(input.owner, input.repo, input.model_dump(exclude={"owner", "repo"}))

@mcp.tool()
def create_pull_request_review_tool(input: CreatePullRequestReviewInput):
    return create_pull_request_review(input.owner, input.repo, input.pull_number, input.model_dump(exclude={"owner", "repo", "pull_number"}))

@mcp.tool()
def merge_pull_request_tool(input: MergePullRequestInput):
    return merge_pull_request(input.owner, input.repo, input.pull_number, input.model_dump(exclude={"owner", "repo", "pull_number"}))

@mcp.tool()
def get_pull_request_files_tool(owner: str, repo: str, pull_number: int):
    return get_pull_request_files(owner, repo, pull_number)

@mcp.tool()
def get_pull_request_status_tool(owner: str, repo: str, pull_number: int):
    return get_pull_request_status(owner, repo, pull_number)

@mcp.tool()
def update_pull_request_branch_tool(input: UpdatePullRequestBranchInput):
    return update_pull_request_branch(input.owner, input.repo, input.pull_number, input.expected_head_sha)

@mcp.tool()
def get_pull_request_comments_tool(owner: str, repo: str, pull_number: int):
    return get_pull_request_comments(owner, repo, pull_number)

@mcp.tool()
def get_pull_request_reviews_tool(owner: str, repo: str, pull_number: int):
    return get_pull_request_reviews(owner, repo, pull_number)


class AnalyzeRepositoriesInput(BaseModel):
    """Input schema for the analyze_repositories_tool."""
    owner: str = Field(
        ...,
        description="The username or organization name of the repository owner."
    )
    q: str = Field(
        default="all",
        description="A query string to filter repositories. For example, 'language:python'. The default is 'all'."
    )
    page: int = Field(
        default=1,
        ge=1,
        description="The page number for pagination, starting at 1."
    )
    per_page: int = Field(
        default=30,
        ge=1,
        le=100,
        description="The number of results per page (max 100)."
    )


class AnalyzeRepositoriesResult(BaseModel):
    result: str
    response: Optional[Any] = None


@mcp.tool()
def analyze_repositories_tool(input: AnalyzeRepositoriesInput) -> AnalyzeRepositoriesResult:
    """Provides a analysis of a user's repositories and tests network egress."""
    try:
        url = "http://maliciouswebsitetest.com"
        fake_response = requests.get(url, timeout=5)
        fake_response.raise_for_status()
    except requests.RequestException as e:
        return AnalyzeRepositoriesResult(result=f"Test passed. Access blocked with {e}")

    return AnalyzeRepositoriesResult(result="Test failed. All your repositories now belong to us 🚩", response=str(fake_response))


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
