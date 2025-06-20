# app/operations/files.py

import base64
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

from app.common.utils import github_request, build_url
from app.common.types import (
    GitHubContent,
    GitHubAuthor,
    GitHubTree,
    GitHubCommit,
    GitHubReference,
    GitHubFileContent,
)

class FileOperation(BaseModel):
    path: str
    content: str

class CreateOrUpdateFileInput(BaseModel):
    owner: str
    repo: str
    path: str
    content: str
    message: str
    branch: str
    sha: Optional[str] = None

class GetFileContentsInput(BaseModel):
    owner: str
    repo: str
    path: str
    branch: Optional[str] = None

class PushFilesInput(BaseModel):
    owner: str
    repo: str
    branch: str
    files: List[FileOperation]
    message: str

def get_file_contents(owner: str, repo: str, path: str, branch: Optional[str] = None) -> GitHubContent:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    if branch:
        url = build_url(url, {"ref": branch})
    response = github_request(url)
    data = GitHubContent.__concrete__.model_validate(response) if hasattr(GitHubContent, "__concrete__") else response
    # If it's a file, decode the content
    if isinstance(data, GitHubFileContent) and data.content:
        try:
            data.content = base64.b64decode(data.content).decode("utf-8")
        except Exception:
            pass
    return data

def create_or_update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    sha: Optional[str] = None
) -> Dict[str, Any]:
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    current_sha = sha
    if not current_sha:
        try:
            existing = get_file_contents(owner, repo, path, branch)
            if isinstance(existing, GitHubFileContent):
                current_sha = existing.sha
        except Exception:
            pass  # File does not exist, will create new
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    body = {
        "message": message,
        "content": encoded_content,
        "branch": branch,
    }
    if current_sha:
        body["sha"] = current_sha
    response = github_request(url, method="PUT", body=body)
    return response

def _create_tree(owner: str, repo: str, files: List[FileOperation], base_tree: Optional[str] = None) -> GitHubTree:
    tree = [
        {
            "path": file.path,
            "mode": "100644",
            "type": "blob",
            "content": file.content,
        }
        for file in files
    ]
    body = {"tree": tree}
    if base_tree:
        body["base_tree"] = base_tree
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees",
        method="POST",
        body=body,
    )
    return GitHubTree.model_validate(response)

def _create_commit(owner: str, repo: str, message: str, tree_sha: str, parents: List[str]) -> GitHubCommit:
    body = {
        "message": message,
        "tree": tree_sha,
        "parents": parents,
    }
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/commits",
        method="POST",
        body=body,
    )
    return GitHubCommit.model_validate(response)

def _update_reference(owner: str, repo: str, ref: str, sha: str) -> GitHubReference:
    response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/{ref}",
        method="PATCH",
        body={"sha": sha, "force": True},
    )
    return GitHubReference.model_validate(response)

def push_files(
    owner: str,
    repo: str,
    branch: str,
    files: List[FileOperation],
    message: str
) -> GitHubReference:
    ref_response = github_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch}"
    )
    ref = GitHubReference.model_validate(ref_response)
    commit_sha = ref.object.sha
    tree = _create_tree(owner, repo, files, base_tree=commit_sha)
    commit = _create_commit(owner, repo, message, tree.sha, [commit_sha])
    return _update_reference(owner, repo, f"heads/{branch}", commit.sha)
