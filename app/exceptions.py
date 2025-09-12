from typing import Any, Dict, Optional


class NalewkaException(Exception):
    """Base exception class for the Nalewka application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationException(NalewkaException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 401, details)


class AuthorizationException(NalewkaException):
    """Exception raised for authorization errors."""

    def __init__(
        self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, 403, details)


class ValidationException(NalewkaException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 400, details)


class NotFoundException(NalewkaException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 404, details)


class ConflictException(NalewkaException):
    """Exception raised for resource conflicts."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 409, details)


class InternalServerErrorException(NalewkaException):
    """Exception raised for internal server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, 500, details)
