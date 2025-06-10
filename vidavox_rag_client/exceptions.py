"""
Custom exceptions for RAG API Client
"""


class RAGAPIError(Exception):
    """Base exception for all RAG API related errors."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"RAG API Error {self.status_code}: {self.message}"
        return f"RAG API Error: {self.message}"


class DuplicateFolderError(RAGAPIError):
    """Raised when trying to create a folder with the same name."""

    def __init__(self, message: str = "Folder already exists"):
        super().__init__(message, 409)


class AuthenticationError(RAGAPIError):
    """Raised when authentication fails (401 Unauthorized)."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class NotFoundError(RAGAPIError):
    """Raised when a resource is not found (404 Not Found)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ValidationError(RAGAPIError):
    """Raised when request validation fails (400 Bad Request)."""

    def __init__(self, message: str = "Request validation failed"):
        super().__init__(message, 400)


class ServerError(RAGAPIError):
    """Raised when server encounters an error (5xx Server Error)."""

    def __init__(self, message: str = "Server error occurred"):
        super().__init__(message, 500)


class ConflictError(RAGAPIError):
    """Raised when a conflict occurs (409 Conflict)."""

    def __init__(self, message: str = "Conflict occurred"):
        super().__init__(message, 409)


class RateLimitError(RAGAPIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


class TimeoutError(RAGAPIError):
    """Raised when a request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message)


class ConnectionError(RAGAPIError):
    """Raised when connection to API fails."""

    def __init__(self, message: str = "Connection failed"):
        super().__init__(message)


class InvalidResponseError(RAGAPIError):
    """Raised when API returns an invalid response."""

    def __init__(self, message: str = "Invalid response received"):
        super().__init__(message)
