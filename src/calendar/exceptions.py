"""
Calendar integration exception classes.

This module defines custom exception classes for calendar integration errors,
providing specific error types for different failure scenarios.
"""

from typing import Optional, Dict, Any


class CalendarError(Exception):
    """
    Base exception class for all calendar integration errors.
    
    Attributes:
        message (str): The error message.
        details (Dict[str, Any]): Additional error details.
        provider (str): The calendar provider that caused the error.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        self.message = message
        self.details = details or {}
        self.provider = provider
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.provider:
            return f"[{self.provider}] {self.message}"
        return self.message


class AuthError(CalendarError):
    """
    Exception raised for authentication-related errors.
    
    This includes OAuth failures, token expiration, invalid credentials,
    and authorization scope issues.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        super().__init__(f"Authentication Error: {message}", details, provider)


class SyncError(CalendarError):
    """
    Exception raised for synchronization-related errors.
    
    This includes network failures, API rate limits, calendar not found,
    and event creation/update/deletion failures.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        super().__init__(f"Sync Error: {message}", details, provider)


class ValidationError(CalendarError):
    """
    Exception raised for data validation errors.
    
    This includes invalid event data, template parsing errors,
    date/time format issues, and missing required fields.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        self.field = field
        error_msg = f"Validation Error: {message}"
        if field:
            error_msg = f"Validation Error [{field}]: {message}"
        super().__init__(error_msg, details, provider)


class ConnectionError(CalendarError):
    """
    Exception raised for connection-related errors.
    
    This includes network connectivity issues, timeout errors,
    and calendar service unavailability.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        super().__init__(f"Connection Error: {message}", details, provider)


class RateLimitError(CalendarError):
    """
    Exception raised when API rate limits are exceeded.
    
    This includes provider-specific rate limiting and quota exceeded errors.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        self.retry_after = retry_after
        error_msg = f"Rate Limit Error: {message}"
        if retry_after:
            error_msg += f" (retry after {retry_after} seconds)"
        super().__init__(error_msg, details, provider)


class ConflictError(CalendarError):
    """
    Exception raised when calendar event conflicts are detected.
    
    This includes events modified externally and sync conflicts.
    """
    
    def __init__(self, message: str, local_event: Optional[Dict[str, Any]] = None, remote_event: Optional[Dict[str, Any]] = None, provider: Optional[str] = None):
        self.local_event = local_event
        self.remote_event = remote_event
        details = {}
        if local_event:
            details['local_event'] = local_event
        if remote_event:
            details['remote_event'] = remote_event
        super().__init__(f"Conflict Error: {message}", details, provider)