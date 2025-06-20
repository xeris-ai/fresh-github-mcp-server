# app/common/errors.py

from typing import Any, Optional
from datetime import datetime, timedelta

class GitHubError(Exception):
    def __init__(self, message: str, status: int, response: Any):
        super().__init__(message)
        self.status = status
        self.response = response

class GitHubValidationError(GitHubError):
    def __init__(self, message: str, status: int, response: Any):
        super().__init__(message, status, response)

class GitHubResourceNotFoundError(GitHubError):
    def __init__(self, resource: str):
        super().__init__(
            f"Resource not found: {resource}",
            404,
            {"message": f"{resource} not found"}
        )

class GitHubAuthenticationError(GitHubError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401, {"message": message})

class GitHubPermissionError(GitHubError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403, {"message": message})

class GitHubRateLimitError(GitHubError):
    def __init__(self, message: str = "Rate limit exceeded", reset_at: Optional[datetime] = None):
        if reset_at is None:
            reset_at = datetime.now() + timedelta(minutes=1)
        super().__init__(message, 429, {"message": message, "reset_at": reset_at.isoformat()})
        self.reset_at = reset_at

class GitHubConflictError(GitHubError):
    def __init__(self, message: str):
        super().__init__(message, 409, {"message": message})

def is_github_error(error: Exception) -> bool:
    return isinstance(error, GitHubError)

def create_github_error(status: int, response: Optional[dict]) -> GitHubError:
    message = (response or {}).get("message", "")
    if status == 401:
        return GitHubAuthenticationError(message or "Authentication failed")
    elif status == 403:
        return GitHubPermissionError(message or "Insufficient permissions")
    elif status == 404:
        return GitHubResourceNotFoundError(message or "Resource")
    elif status == 409:
        return GitHubConflictError(message or "Conflict occurred")
    elif status == 422:
        return GitHubValidationError(message or "Validation failed", status, response)
    elif status == 429:
        reset_at_str = (response or {}).get("reset_at")
        reset_at = datetime.fromisoformat(reset_at_str) if reset_at_str else None
        return GitHubRateLimitError(message or "Rate limit exceeded", reset_at)
    else:
        return GitHubError(message or "GitHub API error", status, response)
