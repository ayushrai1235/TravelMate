"""RailRadar exception hierarchy."""
from __future__ import annotations


class RailRadarServiceException(Exception):
    """Base exception for RailRadar operations."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RailRadarConnectionError(RailRadarServiceException):
    def __init__(self, message: str = "Failed to connect to RailRadar API"):
        super().__init__(message, status_code=502)


class RailRadarTimeoutError(RailRadarServiceException):
    def __init__(self, message: str = "RailRadar API request timed out"):
        super().__init__(message, status_code=504)


class RailRadarAuthError(RailRadarServiceException):
    def __init__(self, message: str = "Invalid RailRadar API key"):
        super().__init__(message, status_code=401)


class RailRadarForbiddenError(RailRadarServiceException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


class RailRadarNotFoundError(RailRadarServiceException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RailRadarRateLimitError(RailRadarServiceException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class RailRadarValidationError(RailRadarServiceException):
    def __init__(self, message: str = "Invalid input provided"):
        super().__init__(message, status_code=400)


class RailRadarServerError(RailRadarServiceException):
    def __init__(self, message: str = "Internal RailRadar server error"):
        super().__init__(message, status_code=500)
