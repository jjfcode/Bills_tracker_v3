"""
Unit tests for calendar integration interfaces and result classes.
"""

import pytest
from datetime import datetime, date, timedelta
from src.calendar.interfaces import (
    CalendarProvider, AuthResult, ConnectionResult, EventResult, DateRange,
    AuthStatus, ConnectionStatus, EventOperationStatus
)
from src.calendar.models import CalendarEvent, Reminder
from src.calendar.exceptions import CalendarError


class TestAuthResult:
    """Test cases for AuthResult class."""
    
    def test_auth_result_success(self):
        """Test successful auth result."""
        expires_at = datetime.now() + timedelta(hours=1)
        result = AuthResult(
            status=AuthStatus.SUCCESS,
            access_token="token123",
            refresh_token="refresh123",
            expires_at=expires_at
        )
        
        assert result.is_success is True
        assert result.is_expired is False
        assert result.access_token == "token123"
        assert result.refresh_token == "refresh123"
    
    def test_auth_result_failed(self):
        """Test failed auth result."""
        result = AuthResult(
            status=AuthStatus.FAILED,
            error_message="Invalid credentials"
        )
        
        assert result.is_success is False
        assert result.error_message == "Invalid credentials"
    
    def test_auth_result_expired_check(self):
        """Test expired token check."""
        # Expired token
        expired_result = AuthResult(
            status=AuthStatus.SUCCESS,
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert expired_result.is_expired is True
        
        # Valid token
        valid_result = AuthResult(
            status=AuthStatus.SUCCESS,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        assert valid_result.is_expired is False
        
        # No expiration time
        no_expiry_result = AuthResult(status=AuthStatus.SUCCESS)
        assert no_expiry_result.is_expired is False


class TestConnectionResult:
    """Test cases for ConnectionResult class."""
    
    def test_connection_result_success(self):
        """Test successful connection result."""
        result = ConnectionResult(
            status=ConnectionStatus.CONNECTED,
            response_time_ms=150
        )
        
        assert result.is_connected is True
        assert result.response_time_ms == 150
    
    def test_connection_result_failed(self):
        """Test failed connection result."""
        result = ConnectionResult(
            status=ConnectionStatus.ERROR,
            error_message="Network timeout"
        )
        
        assert result.is_connected is False
        assert result.error_message == "Network timeout"
    
    def test_connection_result_with_provider_info(self):
        """Test connection result with provider info."""
        provider_info = {"version": "v3", "features": ["events", "calendars"]}
        result = ConnectionResult(
            status=ConnectionStatus.CONNECTED,
            provider_info=provider_info
        )
        
        assert result.provider_info == provider_info


class TestEventResult:
    """Test cases for EventResult class."""
    
    def test_event_result_success(self):
        """Test successful event result."""
        result = EventResult(
            status=EventOperationStatus.SUCCESS,
            event_id="event123"
        )
        
        assert result.is_success is True
        assert result.should_retry is False
        assert result.event_id == "event123"
    
    def test_event_result_failed(self):
        """Test failed event result."""
        result = EventResult(
            status=EventOperationStatus.FAILED,
            error_message="Event creation failed"
        )
        
        assert result.is_success is False
        assert result.should_retry is True
        assert result.error_message == "Event creation failed"
    
    def test_event_result_rate_limited(self):
        """Test rate limited event result."""
        result = EventResult(
            status=EventOperationStatus.RATE_LIMITED,
            retry_after=60
        )
        
        assert result.is_success is False
        assert result.should_retry is True
        assert result.retry_after == 60
    
    def test_event_result_not_found(self):
        """Test not found event result."""
        result = EventResult(
            status=EventOperationStatus.NOT_FOUND,
            error_message="Event not found"
        )
        
        assert result.is_success is False
        assert result.should_retry is False


class TestDateRange:
    """Test cases for DateRange class."""
    
    def test_date_range_valid(self):
        """Test valid date range creation."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        date_range = DateRange(start_date=start_date, end_date=end_date)
        assert date_range.start_date == start_date
        assert date_range.end_date == end_date
        assert date_range.days == 31
    
    def test_date_range_same_day(self):
        """Test date range with same start and end date."""
        test_date = date(2024, 1, 15)
        date_range = DateRange(start_date=test_date, end_date=test_date)
        assert date_range.days == 1
    
    def test_date_range_invalid_order(self):
        """Test date range with invalid date order."""
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)
        
        with pytest.raises(ValueError) as exc_info:
            DateRange(start_date=start_date, end_date=end_date)
        assert "Start date must be before or equal to end date" in str(exc_info.value)


class MockCalendarProvider(CalendarProvider):
    """Mock implementation of CalendarProvider for testing."""
    
    def __init__(self, provider_name: str = "mock"):
        super().__init__(provider_name)
        self.mock_authenticated = False
        self.mock_events = {}
        self.mock_calendars = [{"id": "primary", "name": "Primary Calendar"}]
    
    def authenticate(self, credentials):
        self.mock_authenticated = True
        self._authenticated = True
        return AuthResult(status=AuthStatus.SUCCESS, access_token="mock_token")
    
    def refresh_authentication(self):
        if self.mock_authenticated:
            return AuthResult(status=AuthStatus.SUCCESS, access_token="refreshed_token")
        return AuthResult(status=AuthStatus.FAILED, error_message="Not authenticated")
    
    def revoke_authentication(self):
        self.mock_authenticated = False
        self._authenticated = False
        return True
    
    def test_connection(self):
        if self.mock_authenticated:
            return ConnectionResult(status=ConnectionStatus.CONNECTED, response_time_ms=100)
        return ConnectionResult(status=ConnectionStatus.DISCONNECTED)
    
    def create_event(self, event):
        if not self.mock_authenticated:
            return EventResult(status=EventOperationStatus.FAILED, error_message="Not authenticated")
        
        event_id = f"mock_event_{len(self.mock_events) + 1}"
        self.mock_events[event_id] = event
        return EventResult(status=EventOperationStatus.SUCCESS, event_id=event_id)
    
    def get_event(self, event_id):
        if event_id in self.mock_events:
            return EventResult(status=EventOperationStatus.SUCCESS, event=self.mock_events[event_id])
        return EventResult(status=EventOperationStatus.NOT_FOUND)
    
    def update_event(self, event_id, event):
        if event_id in self.mock_events:
            self.mock_events[event_id] = event
            return EventResult(status=EventOperationStatus.SUCCESS, event_id=event_id)
        return EventResult(status=EventOperationStatus.NOT_FOUND)
    
    def delete_event(self, event_id):
        if event_id in self.mock_events:
            del self.mock_events[event_id]
            return EventResult(status=EventOperationStatus.SUCCESS)
        return EventResult(status=EventOperationStatus.NOT_FOUND)
    
    def get_events(self, date_range, calendar_id=None):
        return list(self.mock_events.values())
    
    def batch_create_events(self, events):
        results = []
        for event in events:
            results.append(self.create_event(event))
        return results
    
    def batch_update_events(self, updates):
        results = []
        for event_id, event in updates:
            results.append(self.update_event(event_id, event))
        return results
    
    def batch_delete_events(self, event_ids):
        results = []
        for event_id in event_ids:
            results.append(self.delete_event(event_id))
        return results
    
    def get_calendars(self):
        return self.mock_calendars
    
    def get_default_calendar_id(self):
        return "primary"
    
    def get_rate_limits(self):
        return {"requests_per_minute": 100, "requests_per_day": 10000}
    
    def get_supported_features(self):
        return ["events", "reminders", "colors", "batch_operations"]


class TestCalendarProvider:
    """Test cases for CalendarProvider abstract class."""
    
    def test_provider_initialization(self):
        """Test calendar provider initialization."""
        provider = MockCalendarProvider("test_provider")
        assert provider.provider_name == "test_provider"
        assert provider.provider_type == "test_provider"
        assert provider.is_authenticated is False
    
    def test_provider_authentication_flow(self):
        """Test provider authentication flow."""
        provider = MockCalendarProvider()
        
        # Initially not authenticated
        assert provider.is_authenticated is False
        
        # Authenticate
        result = provider.authenticate({"token": "test"})
        assert result.is_success is True
        assert provider.is_authenticated is True
        
        # Test connection after authentication
        conn_result = provider.test_connection()
        assert conn_result.is_connected is True
        
        # Revoke authentication
        assert provider.revoke_authentication() is True
        assert provider.is_authenticated is False
    
    def test_provider_ensure_authenticated(self):
        """Test ensure authenticated utility method."""
        provider = MockCalendarProvider()
        
        # Should raise error when not authenticated
        with pytest.raises(CalendarError) as exc_info:
            provider._ensure_authenticated()
        assert "not authenticated" in str(exc_info.value)
        
        # Should not raise error when authenticated
        provider.authenticate({"token": "test"})
        provider._ensure_authenticated()  # Should not raise
    
    def test_provider_event_operations(self):
        """Test provider event CRUD operations."""
        provider = MockCalendarProvider()
        provider.authenticate({"token": "test"})
        
        # Create test event
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        event = CalendarEvent(
            title="Test Event",
            description="Test Description",
            start_datetime=start_time,
            end_datetime=end_time,
            all_day=False,
            reminders=[Reminder(minutes_before=60)],
            bill_id=1
        )
        
        # Create event
        create_result = provider.create_event(event)
        assert create_result.is_success is True
        assert create_result.event_id is not None
        
        event_id = create_result.event_id
        
        # Get event
        get_result = provider.get_event(event_id)
        assert get_result.is_success is True
        assert get_result.event.title == "Test Event"
        
        # Update event
        event.title = "Updated Event"
        update_result = provider.update_event(event_id, event)
        assert update_result.is_success is True
        
        # Verify update
        get_result = provider.get_event(event_id)
        assert get_result.event.title == "Updated Event"
        
        # Delete event
        delete_result = provider.delete_event(event_id)
        assert delete_result.is_success is True
        
        # Verify deletion
        get_result = provider.get_event(event_id)
        assert get_result.status == EventOperationStatus.NOT_FOUND
    
    def test_provider_batch_operations(self):
        """Test provider batch operations."""
        provider = MockCalendarProvider()
        provider.authenticate({"token": "test"})
        
        # Create multiple events
        events = []
        for i in range(3):
            start_time = datetime.now() + timedelta(days=i+1)
            end_time = start_time + timedelta(hours=1)
            
            event = CalendarEvent(
                title=f"Event {i+1}",
                description=f"Description {i+1}",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=i+1
            )
            events.append(event)
        
        # Batch create
        create_results = provider.batch_create_events(events)
        assert len(create_results) == 3
        assert all(result.is_success for result in create_results)
        
        # Get event IDs
        event_ids = [result.event_id for result in create_results]
        
        # Batch update
        updates = []
        for i, event_id in enumerate(event_ids):
            events[i].title = f"Updated Event {i+1}"
            updates.append((event_id, events[i]))
        
        update_results = provider.batch_update_events(updates)
        assert len(update_results) == 3
        assert all(result.is_success for result in update_results)
        
        # Batch delete
        delete_results = provider.batch_delete_events(event_ids)
        assert len(delete_results) == 3
        assert all(result.is_success for result in delete_results)
    
    def test_provider_calendar_management(self):
        """Test provider calendar management methods."""
        provider = MockCalendarProvider()
        
        # Get calendars
        calendars = provider.get_calendars()
        assert len(calendars) == 1
        assert calendars[0]["id"] == "primary"
        
        # Get default calendar
        default_id = provider.get_default_calendar_id()
        assert default_id == "primary"
    
    def test_provider_metadata_methods(self):
        """Test provider metadata methods."""
        provider = MockCalendarProvider()
        
        # Get rate limits
        rate_limits = provider.get_rate_limits()
        assert "requests_per_minute" in rate_limits
        assert isinstance(rate_limits["requests_per_minute"], int)
        
        # Get supported features
        features = provider.get_supported_features()
        assert isinstance(features, list)
        assert "events" in features
    
    def test_provider_utility_methods(self):
        """Test provider utility methods."""
        provider = MockCalendarProvider()
        
        # Test rate limit handling
        rate_limit_result = provider._handle_rate_limit(60)
        assert rate_limit_result.status == EventOperationStatus.RATE_LIMITED
        assert rate_limit_result.retry_after == 60
        
        # Test error result creation
        error_result = provider._create_error_result("Test error")
        assert error_result.status == EventOperationStatus.FAILED
        assert error_result.error_message == "Test error"