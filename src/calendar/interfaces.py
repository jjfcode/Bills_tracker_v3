"""
Calendar provider interfaces and result classes.

This module defines the abstract interface for calendar providers and
result classes for various operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from .models import CalendarEvent
from .exceptions import CalendarError


class AuthStatus(Enum):
    """Enumeration of authentication statuses."""
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    PENDING = "pending"


class ConnectionStatus(Enum):
    """Enumeration of connection statuses."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"


class EventOperationStatus(Enum):
    """Enumeration of event operation statuses."""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"


@dataclass
class AuthResult:
    """
    Result of an authentication operation.
    
    Attributes:
        status (AuthStatus): Authentication status.
        access_token (Optional[str]): Access token if successful.
        refresh_token (Optional[str]): Refresh token if available.
        expires_at (Optional[datetime]): Token expiration time.
        error_message (Optional[str]): Error message if failed.
        user_info (Optional[Dict[str, Any]]): User information if available.
    """
    status: AuthStatus
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    
    @property
    def is_success(self) -> bool:
        """Check if authentication was successful."""
        return self.status == AuthStatus.SUCCESS
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at


@dataclass
class ConnectionResult:
    """
    Result of a connection test operation.
    
    Attributes:
        status (ConnectionStatus): Connection status.
        response_time_ms (Optional[int]): Response time in milliseconds.
        error_message (Optional[str]): Error message if failed.
        provider_info (Optional[Dict[str, Any]]): Provider-specific information.
    """
    status: ConnectionStatus
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    provider_info: Optional[Dict[str, Any]] = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is successful."""
        return self.status == ConnectionStatus.CONNECTED


@dataclass
class EventResult:
    """
    Result of a calendar event operation.
    
    Attributes:
        status (EventOperationStatus): Operation status.
        event_id (Optional[str]): External event ID if successful.
        event (Optional[CalendarEvent]): Event data if available.
        error_message (Optional[str]): Error message if failed.
        retry_after (Optional[int]): Seconds to wait before retry if rate limited.
    """
    status: EventOperationStatus
    event_id: Optional[str] = None
    event: Optional[CalendarEvent] = None
    error_message: Optional[str] = None
    retry_after: Optional[int] = None
    
    @property
    def is_success(self) -> bool:
        """Check if operation was successful."""
        return self.status == EventOperationStatus.SUCCESS
    
    @property
    def should_retry(self) -> bool:
        """Check if operation should be retried."""
        return self.status in [EventOperationStatus.RATE_LIMITED, EventOperationStatus.FAILED]


@dataclass
class DateRange:
    """
    Represents a date range for calendar operations.
    
    Attributes:
        start_date (date): Start date of the range.
        end_date (date): End date of the range.
    """
    start_date: date
    end_date: date
    
    def __post_init__(self):
        """Validate date range after initialization."""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
    
    @property
    def days(self) -> int:
        """Get number of days in the range."""
        return (self.end_date - self.start_date).days + 1


class CalendarProvider(ABC):
    """
    Abstract base class for calendar providers.
    
    This interface defines the contract that all calendar providers must implement
    to support authentication, CRUD operations, and connection testing.
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize calendar provider.
        
        Args:
            provider_name (str): Name of the calendar provider.
        """
        self.provider_name = provider_name
        self._authenticated = False
        self._credentials: Optional[Dict[str, Any]] = None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if provider is authenticated."""
        return self._authenticated
    
    @property
    def provider_type(self) -> str:
        """Get provider type identifier."""
        return self.provider_name.lower()
    
    # Authentication Methods
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate with the calendar provider.
        
        Args:
            credentials (Dict[str, Any]): Authentication credentials.
            
        Returns:
            AuthResult: Result of the authentication operation.
        """
        pass
    
    @abstractmethod
    def refresh_authentication(self) -> AuthResult:
        """
        Refresh authentication tokens.
        
        Returns:
            AuthResult: Result of the token refresh operation.
        """
        pass
    
    @abstractmethod
    def revoke_authentication(self) -> bool:
        """
        Revoke authentication and clear stored credentials.
        
        Returns:
            bool: True if revocation was successful.
        """
        pass
    
    # Connection Testing
    
    @abstractmethod
    def test_connection(self) -> ConnectionResult:
        """
        Test connection to the calendar provider.
        
        Returns:
            ConnectionResult: Result of the connection test.
        """
        pass
    
    # Calendar Event CRUD Operations
    
    @abstractmethod
    def create_event(self, event: CalendarEvent) -> EventResult:
        """
        Create a new calendar event.
        
        Args:
            event (CalendarEvent): Event to create.
            
        Returns:
            EventResult: Result of the event creation operation.
        """
        pass
    
    @abstractmethod
    def get_event(self, event_id: str) -> EventResult:
        """
        Retrieve a calendar event by ID.
        
        Args:
            event_id (str): External event ID.
            
        Returns:
            EventResult: Result containing the event if found.
        """
        pass
    
    @abstractmethod
    def update_event(self, event_id: str, event: CalendarEvent) -> EventResult:
        """
        Update an existing calendar event.
        
        Args:
            event_id (str): External event ID to update.
            event (CalendarEvent): Updated event data.
            
        Returns:
            EventResult: Result of the event update operation.
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> EventResult:
        """
        Delete a calendar event.
        
        Args:
            event_id (str): External event ID to delete.
            
        Returns:
            EventResult: Result of the event deletion operation.
        """
        pass
    
    # Batch Operations
    
    @abstractmethod
    def get_events(self, date_range: DateRange, calendar_id: Optional[str] = None) -> List[CalendarEvent]:
        """
        Retrieve calendar events within a date range.
        
        Args:
            date_range (DateRange): Date range to search.
            calendar_id (Optional[str]): Specific calendar ID to search.
            
        Returns:
            List[CalendarEvent]: List of events found in the date range.
        """
        pass
    
    @abstractmethod
    def batch_create_events(self, events: List[CalendarEvent]) -> List[EventResult]:
        """
        Create multiple calendar events in batch.
        
        Args:
            events (List[CalendarEvent]): List of events to create.
            
        Returns:
            List[EventResult]: List of results for each event creation.
        """
        pass
    
    @abstractmethod
    def batch_update_events(self, updates: List[tuple[str, CalendarEvent]]) -> List[EventResult]:
        """
        Update multiple calendar events in batch.
        
        Args:
            updates (List[tuple[str, CalendarEvent]]): List of (event_id, event) tuples.
            
        Returns:
            List[EventResult]: List of results for each event update.
        """
        pass
    
    @abstractmethod
    def batch_delete_events(self, event_ids: List[str]) -> List[EventResult]:
        """
        Delete multiple calendar events in batch.
        
        Args:
            event_ids (List[str]): List of external event IDs to delete.
            
        Returns:
            List[EventResult]: List of results for each event deletion.
        """
        pass
    
    # Calendar Management
    
    @abstractmethod
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get list of available calendars.
        
        Returns:
            List[Dict[str, Any]]: List of calendar information.
        """
        pass
    
    @abstractmethod
    def get_default_calendar_id(self) -> Optional[str]:
        """
        Get the default calendar ID for this provider.
        
        Returns:
            Optional[str]: Default calendar ID if available.
        """
        pass
    
    # Provider-Specific Information
    
    @abstractmethod
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get rate limit information for this provider.
        
        Returns:
            Dict[str, int]: Rate limit information (requests per time period).
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features for this provider.
        
        Returns:
            List[str]: List of supported feature names.
        """
        pass
    
    # Utility Methods
    
    def _ensure_authenticated(self):
        """
        Ensure the provider is authenticated.
        
        Raises:
            CalendarError: If provider is not authenticated.
        """
        if not self.is_authenticated:
            raise CalendarError(f"Provider {self.provider_name} is not authenticated", provider=self.provider_name)
    
    def _handle_rate_limit(self, retry_after: Optional[int] = None) -> EventResult:
        """
        Handle rate limit errors.
        
        Args:
            retry_after (Optional[int]): Seconds to wait before retry.
            
        Returns:
            EventResult: Rate limited result.
        """
        return EventResult(
            status=EventOperationStatus.RATE_LIMITED,
            error_message="Rate limit exceeded",
            retry_after=retry_after
        )
    
    def _create_error_result(self, error_message: str, status: EventOperationStatus = EventOperationStatus.FAILED) -> EventResult:
        """
        Create an error result.
        
        Args:
            error_message (str): Error message.
            status (EventOperationStatus): Error status.
            
        Returns:
            EventResult: Error result.
        """
        return EventResult(
            status=status,
            error_message=error_message
        )