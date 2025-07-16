"""
Unit tests for calendar integration exception classes.
"""

import pytest
from src.calendar.exceptions import (
    CalendarError, AuthError, SyncError, ValidationError,
    ConnectionError, RateLimitError, ConflictError
)


class TestCalendarError:
    """Test cases for CalendarError base exception."""
    
    def test_calendar_error_basic(self):
        """Test basic calendar error creation."""
        error = CalendarError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.details == {}
        assert error.provider is None
    
    def test_calendar_error_with_details(self):
        """Test calendar error with details."""
        details = {"code": 500, "reason": "Internal error"}
        error = CalendarError("Test error", details=details)
        assert error.details == details
    
    def test_calendar_error_with_provider(self):
        """Test calendar error with provider."""
        error = CalendarError("Test error", provider="google")
        assert str(error) == "[google] Test error"
        assert error.provider == "google"
    
    def test_calendar_error_with_all_params(self):
        """Test calendar error with all parameters."""
        details = {"code": 404}
        error = CalendarError("Not found", details=details, provider="outlook")
        assert str(error) == "[outlook] Not found"
        assert error.details == details
        assert error.provider == "outlook"


class TestAuthError:
    """Test cases for AuthError exception."""
    
    def test_auth_error_basic(self):
        """Test basic auth error creation."""
        error = AuthError("Invalid credentials")
        assert "Authentication Error: Invalid credentials" in str(error)
        assert error.provider is None
    
    def test_auth_error_with_provider(self):
        """Test auth error with provider."""
        error = AuthError("Token expired", provider="google")
        assert str(error) == "[google] Authentication Error: Token expired"
        assert error.provider == "google"
    
    def test_auth_error_with_details(self):
        """Test auth error with details."""
        details = {"error_code": "invalid_grant"}
        error = AuthError("OAuth failed", details=details)
        assert error.details == details


class TestSyncError:
    """Test cases for SyncError exception."""
    
    def test_sync_error_basic(self):
        """Test basic sync error creation."""
        error = SyncError("Failed to sync event")
        assert "Sync Error: Failed to sync event" in str(error)
    
    def test_sync_error_with_provider(self):
        """Test sync error with provider."""
        error = SyncError("Rate limit exceeded", provider="outlook")
        assert str(error) == "[outlook] Sync Error: Rate limit exceeded"
    
    def test_sync_error_with_details(self):
        """Test sync error with details."""
        details = {"retry_after": 60, "quota_exceeded": True}
        error = SyncError("Quota exceeded", details=details)
        assert error.details == details


class TestValidationError:
    """Test cases for ValidationError exception."""
    
    def test_validation_error_basic(self):
        """Test basic validation error creation."""
        error = ValidationError("Invalid field value")
        assert "Validation Error: Invalid field value" in str(error)
        assert error.field is None
    
    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        error = ValidationError("Value too long", field="title")
        assert "Validation Error [title]: Value too long" in str(error)
        assert error.field == "title"
    
    def test_validation_error_with_provider_and_field(self):
        """Test validation error with provider and field."""
        error = ValidationError("Invalid format", field="color", provider="google")
        assert str(error) == "[google] Validation Error [color]: Invalid format"
        assert error.field == "color"
        assert error.provider == "google"


class TestConnectionError:
    """Test cases for ConnectionError exception."""
    
    def test_connection_error_basic(self):
        """Test basic connection error creation."""
        error = ConnectionError("Network timeout")
        assert "Connection Error: Network timeout" in str(error)
    
    def test_connection_error_with_provider(self):
        """Test connection error with provider."""
        error = ConnectionError("Service unavailable", provider="apple")
        assert str(error) == "[apple] Connection Error: Service unavailable"
    
    def test_connection_error_with_details(self):
        """Test connection error with details."""
        details = {"timeout": 30, "attempts": 3}
        error = ConnectionError("Connection failed", details=details)
        assert error.details == details


class TestRateLimitError:
    """Test cases for RateLimitError exception."""
    
    def test_rate_limit_error_basic(self):
        """Test basic rate limit error creation."""
        error = RateLimitError("Too many requests")
        assert "Rate Limit Error: Too many requests" in str(error)
        assert error.retry_after is None
    
    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry after."""
        error = RateLimitError("Quota exceeded", retry_after=120)
        assert "retry after 120 seconds" in str(error)
        assert error.retry_after == 120
    
    def test_rate_limit_error_with_provider(self):
        """Test rate limit error with provider."""
        error = RateLimitError("API limit reached", retry_after=60, provider="google")
        expected = "[google] Rate Limit Error: API limit reached (retry after 60 seconds)"
        assert str(error) == expected


class TestConflictError:
    """Test cases for ConflictError exception."""
    
    def test_conflict_error_basic(self):
        """Test basic conflict error creation."""
        error = ConflictError("Event modified externally")
        assert "Conflict Error: Event modified externally" in str(error)
        assert error.local_event is None
        assert error.remote_event is None
    
    def test_conflict_error_with_events(self):
        """Test conflict error with event data."""
        local_event = {"id": "123", "title": "Local Title"}
        remote_event = {"id": "123", "title": "Remote Title"}
        
        error = ConflictError("Title conflict", local_event=local_event, remote_event=remote_event)
        assert error.local_event == local_event
        assert error.remote_event == remote_event
        assert error.details["local_event"] == local_event
        assert error.details["remote_event"] == remote_event
    
    def test_conflict_error_with_provider(self):
        """Test conflict error with provider."""
        error = ConflictError("Sync conflict detected", provider="outlook")
        assert str(error) == "[outlook] Conflict Error: Sync conflict detected"


class TestExceptionInheritance:
    """Test cases for exception inheritance."""
    
    def test_all_exceptions_inherit_from_calendar_error(self):
        """Test that all custom exceptions inherit from CalendarError."""
        exceptions = [
            AuthError("test"),
            SyncError("test"),
            ValidationError("test"),
            ConnectionError("test"),
            RateLimitError("test"),
            ConflictError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, CalendarError)
            assert isinstance(exc, Exception)
    
    def test_exception_attributes_preserved(self):
        """Test that exception attributes are preserved through inheritance."""
        error = AuthError("Test message", details={"code": 401}, provider="test")
        
        # Should have CalendarError attributes
        assert hasattr(error, 'message')
        assert hasattr(error, 'details')
        assert hasattr(error, 'provider')
        
        # Should maintain values
        assert error.details == {"code": 401}
        assert error.provider == "test"