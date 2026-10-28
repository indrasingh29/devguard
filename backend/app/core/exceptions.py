from typing import Any, Dict, Optional


class DevGuardException(Exception):
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class GitHubAPIException(DevGuardException):
    def __init__(self, message: str, status_code: int = 502, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=status_code, details=details)

class DiffLimitExceededException(DevGuardException):
    def __init__(self, message: str = "Diff exceeds size or file count limits", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=413, details=details)

class DuplicateJobException(DevGuardException):
    def __init__(self, message: str = "A review job for this PR commit is already queued or processing", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=409, details=details)

class InvalidWebhookSignatureException(DevGuardException):
    def __init__(self, message: str = "Invalid HMAC signature for GitHub webhook"):
        super().__init__(message=message, status_code=401)

class ResourceNotFoundException(DevGuardException):
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message=message, status_code=404)
