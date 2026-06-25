"""Exceptions raised by the Zaycev.net client."""

from __future__ import annotations

from typing import Optional

__all__ = ["ZaycevError", "AuthenticationError", "ApiError"]


class ZaycevError(Exception):
    """Base class for every error raised by this library."""


class AuthenticationError(ZaycevError):
    """Raised when required credentials or tokens are missing."""


class ApiError(ZaycevError):
    """Raised when the API responds with an error or a non-200 status.

    Attributes:
        status_code: HTTP status code, when the failure is transport-level.
        code: Application-level error code returned in the JSON body.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
