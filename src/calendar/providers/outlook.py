"""
Microsoft Outlook Calendar provider implementation.

This module implements the CalendarProvider interface for Microsoft Outlook Calendar,
providing authentication, CRUD operations, and connection testing through Microsoft Graph API.
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
from ..models import CalendarEvent, Reminder
from ..exceptions import (
    AuthError, SyncError, ValidationError, ConnectionError, RateLimitError, ConflictError
)
from ..oauth import OAuthManager, OAuthConfig

# Configure logger
logger = logging.getLogger(__name__)

# Microsoft Graph API endpoints
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_USERINFO_ENDPOINT = "https://graph.microsoft.com/v1.0/me"


class OutlookCalendarProvider(CalendarProvider):
    """
    Microsoft Outlook Calendar provider implementation.
    
    This class implements the CalendarProvider interface for Microsoft Outlook Calendar,
    handling authentication, CRUD operations, and connection testing through Microsoft Graph API.
    """
    
    def __init__(self, oauth_manager: OAuthManager, user_id: Optional[str] = None):
        """
        Initialize Microsoft Outlook Calendar provider.
        
        Args:
            oauth_manager (OAuthManager): OAuth manager for authentication.
            user_id (Optional[str]): User ID or email for credential lookup.
        """
        super().__init__("Outlook")
        self.oauth_manager = oauth_manager
        self.user_id = user_id
        self._default_calendar_id = "primary"
        
        # Register Outlook OAuth configuration if not already registered
        if not oauth_manager.get_provider_config("outlook"):
            self._register_oauth_config()
    
    def _register_oauth_config(self):
        """Register Microsoft Outlook OAuth configuration with OAuth manager."""
        config = OAuthConfig(
            client_id="YOUR_MICROSOFT_CLIENT_ID",  # Replace with actual client ID
            client_secret="YOUR_MICROSOFT_CLIENT_SECRET",  # Replace with actual client secret
            auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            redirect_uri="http://localhost:8080/callback",  # Replace with actual redirect URI
            scopes=[
                "Calendars.ReadWrite",
                "User.Read",
                "offline_access"
            ],
            additional_params={
                "response_mode": "query"
            }
        )
        self.oauth_manager.register_provider("outlook", config)
    
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
        
        token = self.oauth_manager.get_valid_token("outlook", self.user_id)
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
            if isinstance(error_data.get("error"), str):
                error_message = error_data.get("error_description", "Unknown error")
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
    
    def _event_to_outlook_format(self, event: CalendarEvent) -> Dict[str, Any]:
        """
        Convert CalendarEvent to Microsoft Graph API event format.
        
        Args:
            event (CalendarEvent): Calendar event to convert.
            
        Returns:
            Dict[str, Any]: Microsoft Graph API event data.
        """
        # Format start and end times
        start_data = {}
        end_data = {}
        
        if event.all_day:
            # All-day event (date only)
            start_data = {
                "dateTime": event.start_datetime.strftime("%Y-%m-%d"),
                "timeZone": "UTC"
            }
            # Microsoft Graph API requires the end date to be the day after for all-day events
            end_date = event.end_datetime + timedelta(days=1)
            end_data = {
                "dateTime": end_date.strftime("%Y-%m-%d"),
                "timeZone": "UTC"
            }
        else:
            # Timed event (datetime with timezone)
            start_data = {
                "dateTime": event.start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "UTC"
            }
            end_data = {
                "dateTime": event.end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "UTC"
            }
        
        # Build event data
        event_data = {
            "subject": event.title,
            "body": {
                "contentType": "text",
                "content": event.description
            },
            "start": start_data,
            "end": end_data,
            "isAllDay": event.all_day,
            "extensions": [
                {
                    "@odata.type": "microsoft.graph.openTypeExtension",
                    "extensionName": "com.billstracker.eventdata",
                    "billId": str(event.bill_id),
                    "billsTrackerApp": "true"
                }
            ]
        }
        
        # Add location if present
        if event.location:
            event_data["location"] = {
                "displayName": event.location
            }
        
        # Add reminders if present
        if event.reminders:
            # Microsoft Graph API uses isReminderOn and reminderMinutesBeforeStart
            # We'll use the first reminder in our list
            event_data["isReminderOn"] = True
            event_data["reminderMinutesBeforeStart"] = event.reminders[0].minutes_before
        
        # Add color category if present
        if event.color:
            # Microsoft Graph API uses categories for colors
            # We'll need to map our hex colors to predefined categories
            # For now, use a default category
            event_data["categories"] = ["Bills"]
        
        return event_data
    
    def _outlook_to_event_format(self, outlook_event: Dict[str, Any]) -> CalendarEvent:
        """
        Convert Microsoft Graph API event to CalendarEvent.
        
        Args:
            outlook_event (Dict[str, Any]): Microsoft Graph API event data.
            
        Returns:
            CalendarEvent: Converted calendar event.
            
        Raises:
            ValidationError: If event data is invalid.
        """
        try:
            # Extract bill ID from extensions
            bill_id = 0
            extensions = outlook_event.get("extensions", [])
            for ext in extensions:
                if ext.get("extensionName") == "com.billstracker.eventdata":
                    bill_id_str = ext.get("billId", "0")
                    try:
                        bill_id = int(bill_id_str)
                    except ValueError:
                        bill_id = 0
            
            # Determine if all-day event
            all_day = outlook_event.get("isAllDay", False)
            
            # Parse start and end times
            start_obj = outlook_event.get("start", {})
            end_obj = outlook_event.get("end", {})
            
            start_str = start_obj.get("dateTime", "")
            end_str = end_obj.get("dateTime", "")
            time_zone = start_obj.get("timeZone", "UTC")
            
            if all_day:
                # All-day events have date strings
                start_dt = datetime.fromisoformat(f"{start_str}T00:00:00")
                # Microsoft adds an extra day for all-day events, so subtract it
                end_dt = datetime.fromisoformat(f"{end_str}T00:00:00") - timedelta(days=1)
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                # Timed events have datetime strings
                # Handle both formats: with and without 'Z' or timezone offset
                if 'T' not in start_str:
                    start_str = f"{start_str}T00:00:00"
                if 'T' not in end_str:
                    end_str = f"{end_str}T00:00:00"
                
                # Add Z if no timezone info
                if not (start_str.endswith('Z') or '+' in start_str or '-' in start_str.rsplit(':', 1)[0]):
                    start_str = f"{start_str}Z"
                if not (end_str.endswith('Z') or '+' in end_str or '-' in end_str.rsplit(':', 1)[0]):
                    end_str = f"{end_str}Z"
                
                start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            
            # Extract reminders
            reminders = []
            if outlook_event.get("isReminderOn", False):
                minutes_before = outlook_event.get("reminderMinutesBeforeStart", 15)
                reminders.append(Reminder(minutes_before=minutes_before, method="popup"))
            
            # Extract location
            location = None
            if "location" in outlook_event and "displayName" in outlook_event["location"]:
                location = outlook_event["location"]["displayName"]
            
            # Extract description
            description = ""
            if "body" in outlook_event and "content" in outlook_event["body"]:
                description = outlook_event["body"]["content"]
            
            # Create CalendarEvent
            return CalendarEvent(
                title=outlook_event.get("subject", "Untitled Event"),
                description=description,
                start_datetime=start_dt,
                end_datetime=end_dt,
                all_day=all_day,
                reminders=reminders,
                bill_id=bill_id,
                location=location,
                external_event_id=outlook_event.get("id"),
                provider="outlook",
                last_modified=datetime.now()
            )
        except Exception as e:
            raise ValidationError(f"Failed to convert Outlook event: {str(e)}")
    
    # Authentication Methods
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthResult:
        """
        Authenticate with Microsoft Outlook Calendar.
        
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
            result = self.oauth_manager.refresh_token("outlook", self.user_id)
            
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
            result = self.oauth_manager.revoke_access("outlook", self.user_id)
            
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
        Test connection to Microsoft Outlook Calendar.
        
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
                f"{GRAPH_API_BASE}/me/calendars",
                headers=self._get_headers()
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            if response.status_code == 200:
                # Extract provider info
                data = response.json()
                provider_info = {
                    "calendar_count": len(data.get("value", [])),
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
        Create a new calendar event in Microsoft Outlook Calendar.
        
        Args:
            event (CalendarEvent): Event to create.
            
        Returns:
            EventResult: Result of the event creation operation.
        """
        try:
            self._ensure_authenticated()
            
            # Convert event to Outlook format
            outlook_event = self._event_to_outlook_format(event)
            
            # Determine calendar ID
            calendar_id = self._default_calendar_id
            
            # Create event
            if calendar_id == "primary":
                # Use default calendar
                url = f"{GRAPH_API_BASE}/me/events"
            else:
                # Use specific calendar
                url = f"{GRAPH_API_BASE}/me/calendars/{calendar_id}/events"
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                data=json.dumps(outlook_event)
            )
            
            if response.status_code in (200, 201):
                # Event created successfully
                created_event = response.json()
                event_id = created_event.get("id")
                
                # Update event with external ID
                event.external_event_id = event_id
                event.provider = "outlook"
                
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
        Retrieve a calendar event by ID from Microsoft Outlook Calendar.
        
        Args:
            event_id (str): External event ID.
            
        Returns:
            EventResult: Result containing the event if found.
        """
        try:
            self._ensure_authenticated()
            
            # Get event
            response = requests.get(
                f"{GRAPH_API_BASE}/me/events/{event_id}",
                headers=self._get_headers(),
                params={
                    "$expand": "extensions($filter=id eq 'com.billstracker.eventdata')"
                }
            )
            
            if response.status_code == 200:
                # Event retrieved successfully
                outlook_event = response.json()
                
                # Convert to CalendarEvent
                event = self._outlook_to_event_format(outlook_event)
                
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
        Update an existing calendar event in Microsoft Outlook Calendar.
        
        Args:
            event_id (str): External event ID to update.
            event (CalendarEvent): Updated event data.
            
        Returns:
            EventResult: Result of the event update operation.
        """
        try:
            self._ensure_authenticated()
            
            # Convert event to Outlook format
            outlook_event = self._event_to_outlook_format(event)
            
            # Update event
            response = requests.patch(
                f"{GRAPH_API_BASE}/me/events/{event_id}",
                headers=self._get_headers(),
                data=json.dumps(outlook_event)
            )
            
            if response.status_code in (200, 201, 204):
                # Event updated successfully
                # If 204 No Content, we need to get the updated event
                if response.status_code == 204:
                    # Update event with external ID
                    event.external_event_id = event_id
                    event.provider = "outlook"
                    
                    return EventResult(
                        status=EventOperationStatus.SUCCESS,
                        event_id=event_id,
                        event=event
                    )
                else:
                    # We have the updated event data
                    updated_event = response.json()
                    
                    # Update event with any changes
                    event.external_event_id = updated_event.get("id")
                    event.provider = "outlook"
                    
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
        Delete a calendar event from Microsoft Outlook Calendar.
        
        Args:
            event_id (str): External event ID to delete.
            
        Returns:
            EventResult: Result of the event deletion operation.
        """
        try:
            self._ensure_authenticated()
            
            # Delete event
            response = requests.delete(
                f"{GRAPH_API_BASE}/me/events/{event_id}",
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
        Retrieve calendar events within a date range from Microsoft Outlook Calendar.
        
        Args:
            date_range (DateRange): Date range to search.
            calendar_id (Optional[str]): Specific calendar ID to search.
            
        Returns:
            List[CalendarEvent]: List of events found in the date range.
        """
        try:
            self._ensure_authenticated()
            
            # Format date range for Microsoft Graph API
            start_date_str = date_range.start_date.isoformat()
            end_date_str = date_range.end_date.isoformat()
            
            # Build filter query
            filter_query = f"start/dateTime ge '{start_date_str}' and end/dateTime le '{end_date_str}'"
            
            # Determine URL based on calendar ID
            if not calendar_id or calendar_id == "primary":
                url = f"{GRAPH_API_BASE}/me/events"
            else:
                url = f"{GRAPH_API_BASE}/me/calendars/{calendar_id}/events"
            
            # Get events
            response = requests.get(
                url,
                headers=self._get_headers(),
                params={
                    "$filter": filter_query,
                    "$top": 100,  # Limit results
                    "$expand": "extensions($filter=id eq 'com.billstracker.eventdata')"
                }
            )
            
            if response.status_code == 200:
                # Events retrieved successfully
                data = response.json()
                events = []
                
                for outlook_event in data.get("value", []):
                    try:
                        event = self._outlook_to_event_format(outlook_event)
                        events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to convert event: {e}")
                
                # Handle pagination if more events are available
                next_link = data.get("@odata.nextLink")
                while next_link:
                    response = requests.get(next_link, headers=self._get_headers())
                    if response.status_code == 200:
                        data = response.json()
                        for outlook_event in data.get("value", []):
                            try:
                                event = self._outlook_to_event_format(outlook_event)
                                events.append(event)
                            except Exception as e:
                                logger.warning(f"Failed to convert event: {e}")
                        next_link = data.get("@odata.nextLink")
                    else:
                        break
                
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
        Create multiple calendar events in batch in Microsoft Outlook Calendar.
        
        Args:
            events (List[CalendarEvent]): List of events to create.
            
        Returns:
            List[EventResult]: List of results for each event creation.
        """
        results = []
        
        # Microsoft Graph API supports batch requests, but for simplicity
        # and to match the Google implementation, we'll create events one by one
        for event in events:
            results.append(self.create_event(event))
        
        return results
    
    def batch_update_events(self, updates: List[tuple[str, CalendarEvent]]) -> List[EventResult]:
        """
        Update multiple calendar events in batch in Microsoft Outlook Calendar.
        
        Args:
            updates (List[tuple[str, CalendarEvent]]): List of (event_id, event) tuples.
            
        Returns:
            List[EventResult]: List of results for each event update.
        """
        results = []
        
        # Microsoft Graph API supports batch requests, but for simplicity
        # and to match the Google implementation, we'll update events one by one
        for event_id, event in updates:
            results.append(self.update_event(event_id, event))
        
        return results
    
    def batch_delete_events(self, event_ids: List[str]) -> List[EventResult]:
        """
        Delete multiple calendar events in batch from Microsoft Outlook Calendar.
        
        Args:
            event_ids (List[str]): List of external event IDs to delete.
            
        Returns:
            List[EventResult]: List of results for each event deletion.
        """
        results = []
        
        # Microsoft Graph API supports batch requests, but for simplicity
        # and to match the Google implementation, we'll delete events one by one
        for event_id in event_ids:
            results.append(self.delete_event(event_id))
        
        return results
    
    # Calendar Management
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """
        Get list of available calendars from Microsoft Outlook Calendar.
        
        Returns:
            List[Dict[str, Any]]: List of calendar information.
        """
        try:
            self._ensure_authenticated()
            
            # Get calendar list
            response = requests.get(
                f"{GRAPH_API_BASE}/me/calendars",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # Calendars retrieved successfully
                data = response.json()
                calendars = []
                
                for item in data.get("value", []):
                    calendars.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "color": item.get("color", "auto"),
                        "is_default": item.get("isDefaultCalendar", False),
                        "can_edit": item.get("canEdit", False),
                        "owner": item.get("owner", {}).get("name")
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
        Get the default calendar ID for Microsoft Outlook Calendar.
        
        Returns:
            Optional[str]: Default calendar ID if available.
        """
        try:
            self._ensure_authenticated()
            
            # Get calendar list
            response = requests.get(
                f"{GRAPH_API_BASE}/me/calendar",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                # Default calendar retrieved successfully
                data = response.json()
                return data.get("id")
            else:
                # Handle API error
                self._handle_api_error(response)
                
                # This line will only be reached if _handle_api_error doesn't raise an exception
                return None
        except Exception as e:
            logger.error(f"Default calendar retrieval error: {e}")
            return None
    
    # Provider-Specific Information
    
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get rate limit information for Microsoft Graph API.
        
        Returns:
            Dict[str, int]: Rate limit information (requests per time period).
        """
        return {
            "requests_per_minute": 600,  # Microsoft Graph API default limit
            "burst_requests": 100,
            "user_requests_per_day": 10000
        }
    
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features for Microsoft Outlook Calendar.
        
        Returns:
            List[str]: List of supported feature names.
        """
        return [
            "create_event",
            "update_event",
            "delete_event",
            "get_events",
            "reminders",
            "all_day_events",
            "recurring_events",
            "categories",
            "attachments",
            "attendees"
        ]