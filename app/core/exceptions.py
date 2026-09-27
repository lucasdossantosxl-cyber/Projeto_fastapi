"""Custom exceptions for the application."""

from __future__ import annotations


class AdviceServiceError(Exception):
    """Base exception for advice service failures."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ExternalAPIError(AdviceServiceError):
    """Raised when the external advice API fails or returns unexpected data."""

    pass


class HistoryIOError(AdviceServiceError):
    """Raised when reading/writing the history file fails."""

    pass
