"""Application-specific exceptions and HTTP error mapping."""


class AppError(Exception):
    """Raised when a user-facing error should be returned as an HTTP response."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)
