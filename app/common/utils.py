# app/common/utils.py

import os
import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

import requests

VERSION = "1.0.0"  # Update as needed

def create_github_error(status: int, response_body: Any) -> Exception:
    error = Exception(f"GitHub API error {status}: {response_body}")
    setattr(error, "status", status)
    return error

def build_url(base_url: str, params: Dict[str, Union[str, int, None]]) -> str:
    url_parts = list(urlparse(base_url))
    query = dict(parse_qsl(url_parts[4]))
    for key, value in params.items():
        if value is not None:
            query[key] = str(value)
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)

USER_AGENT = f"modelcontextprotocol/servers/github/v{VERSION} python-requests"

def github_request(
    url: str,
    method: str = "GET",
    body: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    req_headers = {
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    if headers:
        req_headers.update(headers)
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if token:
        req_headers["Authorization"] = f"Bearer {token}"
    response = requests.request(
        method=method,
        url=url,
        headers=req_headers,
        json=body if body is not None else None,
    )
    try:
        response_body = response.json()
    except Exception:
        response_body = response.text
    if not response.ok:
        raise create_github_error(response.status_code, response_body)
    return response_body

def validate_branch_name(branch: str) -> str:
    sanitized = branch.strip()
    if not sanitized:
        raise ValueError("Branch name cannot be empty")
    if ".." in sanitized:
        raise ValueError("Branch name cannot contain '..'")
    if re.search(r"[\s~^:?*\[\\\]]", sanitized):
        raise ValueError("Branch name contains invalid characters")
    if sanitized.startswith("/") or sanitized.endswith("/"):
        raise ValueError("Branch name cannot start or end with '/'")
    if sanitized.endswith(".lock"):
        raise ValueError("Branch name cannot end with '.lock'")
    return sanitized

def validate_repository_name(name: str) -> str:
    sanitized = name.strip().lower()
    if not sanitized:
        raise ValueError("Repository name cannot be empty")
    if not re.match(r"^[a-z0-9_.-]+$", sanitized):
        raise ValueError(
            "Repository name can only contain lowercase letters, numbers, hyphens, periods, and underscores"
        )
    if sanitized.startswith(".") or sanitized.endswith("."):
        raise ValueError("Repository name cannot start or end with a period")
    return sanitized

def validate_owner_name(owner: str) -> str:
    sanitized = owner.strip().lower()
    if not sanitized:
        raise ValueError("Owner name cannot be empty")
    if not re.match(r"^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){0,38}$", sanitized):
        raise ValueError(
            "Owner name must start with a letter or number and can contain up to 39 characters"
        )
    return sanitized

def check_branch_exists(owner: str, repo: str, branch: str) -> bool:
    try:
        github_request(
            f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
        )
        return True
    except Exception as error:
        if hasattr(error, "status") and getattr(error, "status") == 404:
            return False
        raise

def check_user_exists(username: str) -> bool:
    try:
        github_request(f"https://api.github.com/users/{username}")
        return True
    except Exception as error:
        if hasattr(error, "status") and getattr(error, "status") == 404:
            return False
        raise
