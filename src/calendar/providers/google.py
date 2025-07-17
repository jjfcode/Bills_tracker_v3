"""
Google Calendar provider implementation.

This module implements the CalendarProvider interface for Google Calendar,
providing authentication, CRUD operations, and connection testing.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

import requests

from ..interfaces import (
    CalendarProvider, AuthResult, ConnectionResult, EventResult, DateRange,
    AuthStatus, ConnectionStatus, EventOperationStatus
)
from ..models import CalendarEvent
from ..exceptions import (
    AuthError, SyncError, ValidationError, ConnectionError, RateLimitError, ConflictError
)
from ..oauth import OAuthManager, OAuthConfig

# Configure logger
logger = logging.getLogger(__name__)

# Google Calendar API endpoints
GOOGLE_API_BASE = "https://www.googleapis.com/calendar/v3"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleCalendarProvider(CalendarProvider):
    """
    Google Calendar provider implementation.
    
    This class implements the CalendarProvider interface for Google Calendar,
    handling authentication, CRUD operations, and connection testing.
    """
    
    def __init__(self, oauth_manager: OAuthManager, user_id: Optional[str] = None):
        """
        Initialize Google Calendar provider.
        
        Args:
            oauth_manager (OAuthManager): OAuth manager for authentication.
            user_id (Optional[str]): User ID or email for credential lookup.
        """
        super().__init__("Google")
        self.oauth_manager = oauth_manager
        self.user_id = user_id
        self._default_calendar_id = "primary"
        
        # Register Google OAuth configuration if not already registered
        if not oauth_manager.get_provider_config("google"):
            self._register_oauth_config()
    
    def _register_oauth_config(self):
        """Register Google OAuth configuration with OAuth manager."""
        config = OAuthConfig(
            client_id="YOUR_GOOGLE_CLIENT_ID",  # Replace with actual client ID
            client_secret="YOUR_GOOGLE_CLIENT_SECRET",  # Replace with actual client secret
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            redirect_uri="http://localhost:8080/callback",  # Replace with actual redirect URI
            scopes=[
                "https://www.googleapis.com/auth/calendar",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ],
            additional_params={
                "access_type": "offline",
                "prompt": "consent"
            }
        )
        self.oauth_manager.register_provider("google", config)
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with authorization token.
        
        Returns:
            Dict[str, str]: Headers dictionary with authorization token.
            
        Raises:
            AuthError: If not authenticated or token retrieval fails.
        """
        if not self.user_id:
            raise AuthError("User ID not set")
        
        token = self.oauth_manager.get_valid_token("google", self.user_id)
        if not token:
            raise AuthError("Failed to get valid token")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """
        Handle API error responses.
        
        Args:
            response (requests.Response): API response.
            
        Raises:
            RateLimitError: If rate limit exceeded.
            ConflictError: If resource conflict.
            AuthError: If authentication error.
            SyncError: For other API errors.
        """
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
        except Exception:
            error_message = f"API error: {response.status_code}"
        
        if response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(error_message, retry_after=retry_after, provider=self.provider_name)
        elif response.status_code == 409:
            # Resource conflict
            raise ConflictError(error_message, provider=self.provider_name)
        elif response.status_code in (401, 403):
            # Authentication error
            raise AuthError(error_message, provider=self.provider_name)
        else:
            # Other API error
            raise SyncError(error_message, provider=self.provider_name)
    
    def _event_to_google_format(self, event: CalendarEvent) -> Dict[str, Any]:
        """
        Convert CalendarEvent to Google Calendar event format.
        
        Args:
            event (CalendarEvent): Calendar event to convert.
            
        Returns:
            Dict[str, Any]: Google Calendar event data.
        """
        # Format start and end times
        start_data = {}
        end_data = {}
        
        if event.all_day:
            # All-day event (date only)
            start_data["date"] = event.start_datetime.date().isoformat()
            end_data["date"] = event.end_datetime.date().isoformat()
        else:
            # Timed event (datetime with timezone)
            start_data["dateTime"] = event.start_datetime.isoformat()
            end_data["dateTime"] = event.end_datetime.isoformat()
        
        # Format reminders
        reminders = {
            "useDefault": False,
            "overrides": [
                {
                    "method": reminder.method,
                    "minutes": reminder.minutes_before
                }
                for reminder in event.reminders
            ]
        }
        
        # If no reminders specified, use default
        if not event.reminders:
            reminders["useDefault"] = True
            reminders["overrides"] = []
        
        # Build event data
        event_data = {
            "summary": event.title,
            "description": event.description,
            "start": start_data,
            "end": end_data,
            "reminders": reminders,
            "extendedProperties": {
                "private": {
                    "billId": str(event.bill_id),
                    "billsTrackerApp": "true"
                }
            }
        }
        
        # Add optional fields if present
        if event.color:
            # Google uses colorId (1-11) instead of hex colors
            # We'll need to map our hex colors to Google's color IDs
            # For now, use a default color ID
            event_data["colorId"] = "1"
        
        if event.location:
            event_data["location"] = event.location
        
        return event_data
    
    def _google_to_event_format(self, google_event: Dict[str, Any]) -> CalendarEvent:
        """
        Convert Google Calendar event to CalendarEvent.
        
        Args:
            google_event (Dict[str, Any]): Google Calendar event data.
            
        Returns:
            CalendarEvent: Converted calendar event.
            
        Raises:
            ValidationError: If event data is invalid.
        """
        try:
            # Extract bill ID from extended properties
            bill_id = 0
            if "extendedProperties" in google_event and "private" in google_event["extendedProperties"]:
                bill_id_str = google_event["extendedProperties"]["private"].get("billId", "0")
                try:
                    bill_id = int(bill_id_str)
                except ValueError:
                    bill_id = 0
            
            # Determine if all-day event
            all_day = "date" in google_event.get("start", {})
            
            # Parse start and end times
            if all_day:
                start_str = google_event["start"]["date"]
                end_str = google_event["end"]["date"]
                start_dt = datetime.fromisoformat(f"{start_str}T00:00:00")
                end_dt = datetime.fromisoformat(f"{end_str}T00:00:00") - timedelta(days=1)  # Google adds an extra day
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                start_str = google_event["start"]["dateTime"]
                end_str = google_event["end"]["dateTime"]
                start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            
            # Extract reminders
            reminders = []
            if "reminders" in google_event and not google_event["reminders"].get("useDefault", True):
                for override in google_event["reminders"].get("overrides", []):
                    from ..models import Reminder
                    reminders.append(Reminder(
                        minutes_before=override.get("minutes", 30),
                        method=override.get("method", "popup")
                    ))
            
            # Create CalendarEvent
            return CalendarEvent(
                title=google_event.get("summary", "Untitled Event"),
                description=google_event.get("description", ""),
                start_datetime=start_dt,
                end_datetime=end_dt,
                all_day=all_day,
                reminders=reminders,
                bill_id=bill_id,
                location=google_event.get("location"),
                external_event_id=google_event.get("id"),
                provider="google",
                last_modified=datetime.now()
            )
        except Exception as e:
            raise ValidationError(f"Failed to convert Google event: {str(e)}")
    
    # Authentication Methods
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate with Google Calendar.
        
        Args:
            credentials (Dict[str, Any]): Authentication credentials.
                Should contain 'code' and 'state' from OAuth callback.
                
        Returns:
            AuthResult: Result of the authentication operation.
        """
        try:
            # Extract code and state from credentials
            code = credentials.get("code")
            state = credentials.get("state")
            
            if not code or not state:
                return AuthResult(
                    status=AuthStatus.FAILED,
                    error_message="Missing code or state parameter"
                )
            
            # Handle OAuth callback
            result = self.oauth_manager.handle_auth_callback(code, state)
            
            # Set user ID if authentication successful
            if result.is_success and result.user_info and "email" in result.user_info:
                self.user_id = result.user_info["email"]
                self._authenticated = True
            
            return result
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message=str(e)
            )
    
    def refresh_authentication(self) -> AuthResult:
        """
        Refresh authentication tokens.
        
        Returns:
            AuthResult: Result of the token refresh operation.
        """
        if not self.user_id:
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message="User ID not set"
            )
        
        try:
            result = self.oauth_manager.refresh_token("google", self.user_id)
            
            # Update authenticated status
            self._authenticated = result.is_success
            
            return result
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message=str(e)
            )
    
    def revoke_authentication(self) -> bool:
        """
        Revoke authentication and clear stored credentials.
        
        Returns:
            bool: True if revocation was successful.
        """
        if not self.user_id:
            return False
        
        try:
            result = self.oauth_manager.revoke_access("google", self.user_id)
            
            if result:
                self._authenticated = False
                self.user_id = None
            
            return result
        except Exception as e:
            logger.error(f"Revocation error: {e}")
            return False
    
    # Connection Testing
    
    def test_connection(self) -> ConnectionResult:
        """
        Test connection to Google Calendar.
        
        Returns:
            ConnectionResult: Result of the connection test.
        """
        if not self._authenticated:
            return ConnectionResult(
                status=ConnectionStatus.DISCONNECTED,
                error_message="Not authenticated"
            )
        
        try:
            start_time = time.time()
            
            # Make a lightweight API call to test connection
            response = requests.get(
                f"{GOOGLE_API_BASE}/users/me/calendarList",
                headers=self._get_headers()
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            if response.status_code == 200:
                # Extract provider info
                data = response.json()
                provider_info = {
                    "calendar_count": len(data.get("items", [])),
                    "user_id": self.user_id
                }
                
                return ConnectionResult(
                    status=ConnectionStatus.CONNECTED,
                    response_time_ms=response_time_ms,
                    provider_info=provider_info
                )
            else:
                error_message = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", error_message)
                except Exception:
                    pass
                
                return ConnectionResult(
                    status=ConnectionStatus.ERROR,
                    response_time_ms=response_time_ms,
                    error_message=error_message
                )
        except requests.Timeout:
            return ConnectionResult(
                status=ConnectionStatus.TIMEOUT,
                error_message="Connection timed out"
            )
        except Exception as e:
            return ConnectionResult(
                status=ConnectionStatus.ERROR,
                error_message=str(e)
            )
    
    # Calendar Event CRUD Operations
    
    def create_event(self, event: CalendarEvent) -> EventResult:
        """
        Create a new calendar event in Google Calendar.
        
        Args:
            event (CalendarEvent): Event to create.
            
        Returns:
            EventResult: Result of the event creation operation.
        """
        try:
            self._ensure_authenticated()
            
            # Convert event to Google format
            google_event = self._event_to_google_format(event)
            
            # Determine calendar ID
            calendar_id = self._default_calendar_id
            
            # Create event
            response = requests.post(
                f"{GOOGLE_API_BASE}/calendars/{calendar_id}/events",
                headers=self._get_headers(),
                data=json.dumps(google_event)
            )
            
            if response.status_code == 200:
                # Event created successfully
                created_event = response.json()
                event_id = created_event.get("id")
                
                # Update event with external ID
                event.external_event_id = event_id
                event.provider = "google"
                
                return EventResult(
                    status=EventOperationStatus.SUCCESS,
                    event_id=event_id,
                    event=event
                )
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return self._create_error_result(f"API error: {response.status_code}")
        except RateLimitError as e:
            return self._handle_rate_limit(e.retry_after)
        except Exception as e:
            logger.error(f"Event creation error: {e}")
            return self._create_error_result(str(e))
    
    def get_event(self, event_id: str) -> EventResult:
        """
        Retrieve a calendar event by ID from Google Calendar.
        
        Args:
            event_id (str): External event ID.
            
        Returns:
            EventResult: Result containing the event if found.
        """
        try:
            self._ensure_authenticated()
            
            # Determine calendar ID
            calendar_id = self._default_calendar_id
            
            # Get event
            response = requests.get(
                f"{GOOGLE_API_BASE}/calendars/{calendar_id}/events/{event_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # Event retrieved successfully
                google_event = response.json()
                
                # Convert to CalendarEvent
                event = self._google_to_event_format(google_event)
                
                return EventResult(
                    status=EventOperationStatus.SUCCESS,
                    event_id=event_id,
                    event=event
                )
            elif response.status_code == 404:
                # Event not found
                return EventResult(
                    status=EventOperationStatus.NOT_FOUND,
                    error_message=f"Event {event_id} not found"
                )
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return self._create_error_result(f"API error: {response.status_code}")
        except RateLimitError as e:
            return self._handle_rate_limit(e.retry_after)
        except Exception as e:
            logger.error(f"Event retrieval error: {e}")
            return self._create_error_result(str(e))
    
    def update_event(self, event_id: str, event: CalendarEvent) -> EventResult:
        """
        Update an existing calendar event in Google Calendar.
        
        Args:
            event_id (str): External event ID to update.
            event (CalendarEvent): Updated event data.
            
        Returns:
            EventResult: Result of the event update operation.
        """
        try:
            self._ensure_authenticated()
            
            # Convert event to Google format
            google_event = self._event_to_google_format(event)
            
            # Determine calendar ID
            calendar_id = self._default_calendar_id
            
            # Update event
            response = requests.put(
                f"{GOOGLE_API_BASE}/calendars/{calendar_id}/events/{event_id}",
                headers=self._get_headers(),
                data=json.dumps(google_event)
            )
            
            if response.status_code == 200:
                # Event updated successfully
                updated_event = response.json()
                
                # Update event with any changes
                event.external_event_id = updated_event.get("id")
                event.provider = "google"
                
                return EventResult(
                    status=EventOperationStatus.SUCCESS,
                    event_id=event_id,
                    event=event
                )
            elif response.status_code == 404:
                # Event not found
                return EventResult(
                    status=EventOperationStatus.NOT_FOUND,
                    error_message=f"Event {event_id} not found"
                )
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return self._create_error_result(f"API error: {response.status_code}")
        except RateLimitError as e:
            return self._handle_rate_limit(e.retry_after)
        except Exception as e:
            logger.error(f"Event update error: {e}")
            return self._create_error_result(str(e))
    
    def delete_event(self, event_id: str) -> EventResult:
        """
        Delete a calendar event from Google Calendar.
        
        Args:
            event_id (str): External event ID to delete.
            
        Returns:
            EventResult: Result of the event deletion operation.
        """
        try:
            self._ensure_authenticated()
            
            # Determine calendar ID
            calendar_id = self._default_calendar_id
            
            # Delete event
            response = requests.delete(
                f"{GOOGLE_API_BASE}/calendars/{calendar_id}/events/{event_id}",
                headers=self._get_headers()
            )
            
            if response.status_code in (200, 204):
                # Event deleted successfully
                return EventResult(
                    status=EventOperationStatus.SUCCESS,
                    event_id=event_id
                )
            elif response.status_code == 404:
                # Event not found
                return EventResult(
                    status=EventOperationStatus.NOT_FOUND,
                    error_message=f"Event {event_id} not found"
                )
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return self._create_error_result(f"API error: {response.status_code}")
        except RateLimitError as e:
            return self._handle_rate_limit(e.retry_after)
        except Exception as e:
            logger.error(f"Event deletion error: {e}")
            return self._create_error_result(str(e))
    
    # Batch Operations
    
    def get_events(self, date_range: DateRange, calendar_id: Optional[str] = None) -> List[CalendarEvent]:
        """
        Retrieve calendar events within a date range from Google Calendar.
        
        Args:
            date_range (DateRange): Date range to search.
            calendar_id (Optional[str]): Specific calendar ID to search.
            
        Returns:
            List[CalendarEvent]: List of events found in the date range.
        """
        try:
            self._ensure_authenticated()
            
            # Determine calendar ID
            if not calendar_id:
                calendar_id = self._default_calendar_id
            
            # Format date range for Google Calendar API
            time_min = datetime.combine(date_range.start_date, datetime.min.time()).isoformat() + "Z"
            time_max = datetime.combine(date_range.end_date, datetime.max.time()).isoformat() + "Z"
            
            # Get events
            response = requests.get(
                f"{GOOGLE_API_BASE}/calendars/{calendar_id}/events",
                headers=self._get_headers(),
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": 2500  # Maximum allowed by Google
                }
            )
            
            if response.status_code == 200:
                # Events retrieved successfully
                data = response.json()
                events = []
                
                for google_event in data.get("items", []):
                    try:
                        event = self._google_to_event_format(google_event)
                        events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to convert event: {e}")
                
                return events
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return []
        except Exception as e:
            logger.error(f"Events retrieval error: {e}")
            return []
    
    def batch_create_events(self, events: List[CalendarEvent]) -> List[EventResult]:
        """
        Create multiple calendar events in batch in Google Calendar.
        
        Args:
            events (List[CalendarEvent]): List of events to create.
            
        Returns:
            List[EventResult]: List of results for each event creation.
        """
        results = []
        
        # Google Calendar API doesn't support true batch operations for free accounts
        # So we'll just create events one by one
        for event in events:
            results.append(self.create_event(event))
        
        return results
    
    def batch_update_events(self, updates: List[tuple[str, CalendarEvent]]) -> List[EventResult]:
        """
        Update multiple calendar events in batch in Google Calendar.
        
        Args:
            updates (List[tuple[str, CalendarEvent]]): List of (event_id, event) tuples.
            
        Returns:
            List[EventResult]: List of results for each event update.
        """
        results = []
        
        # Google Calendar API doesn't support true batch operations for free accounts
        # So we'll just update events one by one
        for event_id, event in updates:
            results.append(self.update_event(event_id, event))
        
        return results
    
    def batch_delete_events(self, event_ids: List[str]) -> List[EventResult]:
        """
        Delete multiple calendar events in batch from Google Calendar.
        
        Args:
            event_ids (List[str]): List of external event IDs to delete.
            
        Returns:
            List[EventResult]: List of results for each event deletion.
        """
        results = []
        
        # Google Calendar API doesn't support true batch operations for free accounts
        # So we'll just delete events one by one
        for event_id in event_ids:
            results.append(self.delete_event(event_id))
        
        return results
    
    # Calendar Management
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get list of available calendars from Google Calendar.
        
        Returns:
            List[Dict[str, Any]]: List of calendar information.
        """
        try:
            self._ensure_authenticated()
            
            # Get calendar list
            response = requests.get(
                f"{GOOGLE_API_BASE}/users/me/calendarList",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # Calendars retrieved successfully
                data = response.json()
                calendars = []
                
                for item in data.get("items", []):
                    calendars.append({
                        "id": item.get("id"),
                        "summary": item.get("summary"),
                        "description": item.get("description"),
                        "primary": item.get("primary", False),
                        "access_role": item.get("accessRole")
                    })
                
                return calendars
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return []
        except Exception as e:
            logger.error(f"Calendars retrieval error: {e}")
            return []
    
    def get_default_calendar_id(self) -> Optional[str]:
        """
        Get the default calendar ID for Google Calendar.
        
        Returns:
            Optional[str]: Default calendar ID if available.
        """
        try:
            calendars = self.get_calendars()
            
            # Look for primary calendar
            for calendar in calendars:
                if calendar.get("primary", False):
                    return calendar.get("id")
            
            # If no primary calendar found, return first calendar
            if calendars:
                return calendars[0].get("id")
            
            # Default to "primary" if no calendars found
            return "primary"
        except Exception as e:
            logger.error(f"Default calendar retrieval error: {e}")
            return "primary"
    
    # Provider-Specific Information
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get rate limit information for Google Calendar API.
        
        Returns:
            Dict[str, int]: Rate limit information (requests per time period).
        """
        # Google Calendar API has a quota of 1,000,000 requests per day
        # and a limit of 500 requests per 100 seconds per user
        return {
            "daily_quota": 1000000,
            "user_rate_limit": 500,
            "user_rate_period_seconds": 100
        }
    
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features for Google Calendar.
        
        Returns:
            List[str]: List of supported feature names.
        """
        return [
            "create_event",
            "update_event",
            "delete_event",
            "get_event",
            "get_events",
            "reminders",
            "all_day_events",
            "recurring_events",
            "color_coding",
            "multiple_calendars"
        ]
    
    # Utility Methods
    
    def initiate_auth_flow(self) -> Tuple[str, str]:
        """
        Initiate OAuth authentication flow for Google Calendar.
        
        Returns:
            Tuple[str, str]: (auth_url, state) where auth_url is the URL to redirect the user to
                and state is a unique state identifier for this flow.
        """
        return self.oauth_manager.initiate_auth_flow("google")