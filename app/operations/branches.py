# app/operations/branches.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.common.utils import github_request
from app.common.types import GitHubReference

class CreateBranchOptions(BaseModel):
    ref: str
    sha: str

class CreateBranchInput(BaseModel):
    owner: str
    repo: str
    branch: str
    from_branch: Optional[str] = None

def get_default_branch_sha(owner: str, repo: str) -> str:
    try:
        response = github_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/main"
        )
        data = GitHubReference.model_validate(response)
        return data.object.sha
    except Exception:
        master_response = github_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/master"
        )
        if not master_response:
            raise Exception("Could not find default branch (tried 'main' and 'master')")
        data = GitHubReference.model_validate(master_response)
        return data.object.sha

def create_branch(owner: str, repo: str, options: Dict[str, Any]) -> GitHubReference:
    opts = CreateBranchOptions(**options)
    full_ref = f"refs/heads/{opts.ref}"
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs",
        method="POST",
        body={
            "ref": full_ref,
            "sha": opts.sha,
        },
    )
    return GitHubReference.model_validate(response)

def get_branch_sha(owner: str, repo: str, branch: str) -> str:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    )
    data = GitHubReference.model_validate(response)
    return data.object.sha

def create_branch_from_ref(
    owner: str,
    repo: str,
    new_branch: str,
    from_branch: Optional[str] = None
) -> GitHubReference:
    if from_branch:
        sha = get_branch_sha(owner, repo, from_branch)
    else:
        sha = get_default_branch_sha(owner, repo)
    return create_branch(owner, repo, {"ref": new_branch, "sha": sha})

def update_branch(
    owner: str,
    repo: str,
    branch: str,
    sha: str
) -> GitHubReference:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}",
        method="PATCH",
        body={
            "sha": sha,
            "force": True,
        },
    )
    return GitHubReference.model_validate(response)
