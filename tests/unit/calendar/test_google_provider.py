"""
Unit tests for Google Calendar provider.

This module tests the Google Calendar provider implementation,
including authentication, CRUD operations, and connection testing.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
import requests

from src.calendar.providers.google import GoogleCalendarProvider
from src.calendar.oauth import OAuthManager
from src.calendar.models import CalendarEvent, Reminder
from src.calendar.interfaces import AuthStatus, ConnectionStatus, EventOperationStatus
from src.calendar.exceptions import AuthError, SyncError


class TestGoogleCalendarProvider(unittest.TestCase):
    """Test Google Calendar provider implementation."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock OAuth manager
        self.oauth_manager = MagicMock(spec=OAuthManager)
        
        # Configure mock OAuth manager
        self.oauth_manager.get_provider_config.return_value = None
        self.oauth_manager.register_provider.return_value = True
        
        # Create Google Calendar provider
        self.provider = GoogleCalendarProvider(self.oauth_manager, "test@example.com")
        self.provider._authenticated = True  # Set authenticated for testing
        
        # Sample calendar event
        self.sample_event = CalendarEvent(
            title="Test Bill",
            description="Test bill payment",
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=1),
            all_day=False,
            reminders=[Reminder(minutes_before=30)],
            bill_id=123,
            color="#1f538d",
            location="Home"
        )
    
    def test_initialization(self):
        """Test provider initialization."""
        # Verify OAuth config registration
        self.oauth_manager.register_provider.assert_called_once()
        
        # Verify provider properties
        self.assertEqual(self.provider.provider_name, "Google")
        self.assertEqual(self.provider.user_id, "test@example.com")
        self.assertEqual(self.provider._default_calendar_id, "primary")
    
    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection test."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": "primary", "summary": "Primary Calendar"}]
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Test connection
        result = self.provider.test_connection()
        
        # Verify result
        self.assertEqual(result.status, ConnectionStatus.CONNECTED)
        self.assertIsNotNone(result.response_time_ms)
        self.assertEqual(result.provider_info["calendar_count"], 1)
        self.assertEqual(result.provider_info["user_id"], "test@example.com")
        
        # Verify API call
        mock_get.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/users/me/calendarList", 
                     mock_get.call_args[0][0])
    
    @patch('requests.get')
    def test_test_connection_error(self, mock_get):
        """Test connection test with error."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"message": "Invalid credentials"}
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Test connection
        result = self.provider.test_connection()
        
        # Verify result
        self.assertEqual(result.status, ConnectionStatus.ERROR)
        self.assertIsNotNone(result.response_time_ms)
        self.assertEqual(result.error_message, "Invalid credentials")
    
    @patch('requests.get')
    def test_test_connection_timeout(self, mock_get):
        """Test connection test with timeout."""
        # Configure mock to raise timeout
        mock_get.side_effect = requests.Timeout()
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Test connection
        result = self.provider.test_connection()
        
        # Verify result
        self.assertEqual(result.status, ConnectionStatus.TIMEOUT)
        self.assertEqual(result.error_message, "Connection timed out")
    
    def test_event_to_google_format(self):
        """Test converting CalendarEvent to Google format."""
        # Convert event to Google format
        google_event = self.provider._event_to_google_format(self.sample_event)
        
        # Verify conversion
        self.assertEqual(google_event["summary"], "Test Bill")
        self.assertEqual(google_event["description"], "Test bill payment")
        self.assertIn("dateTime", google_event["start"])
        self.assertIn("dateTime", google_event["end"])
        self.assertEqual(google_event["reminders"]["useDefault"], False)
        self.assertEqual(len(google_event["reminders"]["overrides"]), 1)
        self.assertEqual(google_event["reminders"]["overrides"][0]["minutes"], 30)
        self.assertEqual(google_event["location"], "Home")
        self.assertEqual(google_event["extendedProperties"]["private"]["billId"], "123")
    
    def test_event_to_google_format_all_day(self):
        """Test converting all-day CalendarEvent to Google format."""
        # Create all-day event
        all_day_event = CalendarEvent(
            title="All Day Test",
            description="All day test event",
            start_datetime=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            end_datetime=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0),
            all_day=True,
            reminders=[],
            bill_id=456
        )
        
        # Convert event to Google format
        google_event = self.provider._event_to_google_format(all_day_event)
        
        # Verify conversion
        self.assertEqual(google_event["summary"], "All Day Test")
        self.assertIn("date", google_event["start"])
        self.assertIn("date", google_event["end"])
        self.assertEqual(google_event["reminders"]["useDefault"], True)
    
    @patch('requests.post')
    def test_create_event_success(self, mock_post):
        """Test successful event creation."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "event123",
            "summary": "Test Bill",
            "description": "Test bill payment"
        }
        mock_post.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Create event
        result = self.provider.create_event(self.sample_event)
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.SUCCESS)
        self.assertEqual(result.event_id, "event123")
        self.assertEqual(result.event.external_event_id, "event123")
        self.assertEqual(result.event.provider, "google")
        
        # Verify API call
        mock_post.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/calendars/primary/events", 
                     mock_post.call_args[0][0])
    
    @patch('requests.post')
    def test_create_event_error(self, mock_post):
        """Test event creation with error."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid event data"}
        }
        mock_post.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Create event (should return error result)
        result = self.provider.create_event(self.sample_event)
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.FAILED)
        self.assertIn("Invalid event data", result.error_message)
    
    @patch('requests.get')
    def test_get_event_success(self, mock_get):
        """Test successful event retrieval."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "event123",
            "summary": "Test Bill",
            "description": "Test bill payment",
            "start": {"dateTime": datetime.now().isoformat()},
            "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 30}]
            },
            "extendedProperties": {
                "private": {"billId": "123"}
            }
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Get event
        result = self.provider.get_event("event123")
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.SUCCESS)
        self.assertEqual(result.event_id, "event123")
        self.assertEqual(result.event.title, "Test Bill")
        self.assertEqual(result.event.bill_id, 123)
        
        # Verify API call
        mock_get.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/calendars/primary/events/event123", 
                     mock_get.call_args[0][0])
    
    @patch('requests.get')
    def test_get_event_not_found(self, mock_get):
        """Test event retrieval for non-existent event."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": {"message": "Not found"}
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Get event
        result = self.provider.get_event("nonexistent")
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.NOT_FOUND)
        self.assertIn("not found", result.error_message.lower())
    
    @patch('requests.put')
    def test_update_event_success(self, mock_put):
        """Test successful event update."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "event123",
            "summary": "Updated Test Bill",
            "description": "Updated test bill payment"
        }
        mock_put.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Update event
        self.sample_event.title = "Updated Test Bill"
        self.sample_event.description = "Updated test bill payment"
        result = self.provider.update_event("event123", self.sample_event)
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.SUCCESS)
        self.assertEqual(result.event_id, "event123")
        self.assertEqual(result.event.title, "Updated Test Bill")
        
        # Verify API call
        mock_put.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/calendars/primary/events/event123", 
                     mock_put.call_args[0][0])
    
    @patch('requests.delete')
    def test_delete_event_success(self, mock_delete):
        """Test successful event deletion."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Delete event
        result = self.provider.delete_event("event123")
        
        # Verify result
        self.assertEqual(result.status, EventOperationStatus.SUCCESS)
        self.assertEqual(result.event_id, "event123")
        
        # Verify API call
        mock_delete.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/calendars/primary/events/event123", 
                     mock_delete.call_args[0][0])
    
    @patch('requests.get')
    def test_get_events_success(self, mock_get):
        """Test successful events retrieval."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Test Bill 1",
                    "description": "Test bill payment 1",
                    "start": {"dateTime": datetime.now().isoformat()},
                    "end": {"dateTime": (datetime.now() + timedelta(hours=1)).isoformat()},
                    "extendedProperties": {
                        "private": {"billId": "123"}
                    }
                },
                {
                    "id": "event2",
                    "summary": "Test Bill 2",
                    "description": "Test bill payment 2",
                    "start": {"dateTime": (datetime.now() + timedelta(days=1)).isoformat()},
                    "end": {"dateTime": (datetime.now() + timedelta(days=1, hours=1)).isoformat()},
                    "extendedProperties": {
                        "private": {"billId": "456"}
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Create date range
        from src.calendar.interfaces import DateRange
        date_range = DateRange(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7)
        )
        
        # Get events
        events = self.provider.get_events(date_range)
        
        # Verify result
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].title, "Test Bill 1")
        self.assertEqual(events[0].bill_id, 123)
        self.assertEqual(events[1].title, "Test Bill 2")
        self.assertEqual(events[1].bill_id, 456)
        
        # Verify API call
        mock_get.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/calendars/primary/events", 
                     mock_get.call_args[0][0])
    
    @patch('requests.get')
    def test_get_calendars_success(self, mock_get):
        """Test successful calendars retrieval."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "primary",
                    "summary": "Primary Calendar",
                    "primary": True,
                    "accessRole": "owner"
                },
                {
                    "id": "calendar2",
                    "summary": "Secondary Calendar",
                    "accessRole": "owner"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Configure OAuth manager
        self.oauth_manager.get_valid_token.return_value = "test_token"
        
        # Get calendars
        calendars = self.provider.get_calendars()
        
        # Verify result
        self.assertEqual(len(calendars), 2)
        self.assertEqual(calendars[0]["id"], "primary")
        self.assertEqual(calendars[0]["summary"], "Primary Calendar")
        self.assertTrue(calendars[0]["primary"])
        self.assertEqual(calendars[1]["id"], "calendar2")
        self.assertEqual(calendars[1]["summary"], "Secondary Calendar")
        
        # Verify API call
        mock_get.assert_called_once()
        self.assertIn("https://www.googleapis.com/calendar/v3/users/me/calendarList", 
                     mock_get.call_args[0][0])
    
    def test_get_rate_limits(self):
        """Test getting rate limits."""
        rate_limits = self.provider.get_rate_limits()
        
        self.assertIn("daily_quota", rate_limits)
        self.assertIn("user_rate_limit", rate_limits)
        self.assertIn("user_rate_period_seconds", rate_limits)
    
    def test_get_supported_features(self):
        """Test getting supported features."""
        features = self.provider.get_supported_features()
        
        self.assertIn("create_event", features)
        self.assertIn("update_event", features)
        self.assertIn("delete_event", features)
        self.assertIn("get_event", features)
        self.assertIn("get_events", features)
    
    def test_initiate_auth_flow(self):
        """Test initiating authentication flow."""
        # Configure OAuth manager
        self.oauth_manager.initiate_auth_flow.return_value = ("https://example.com/auth", "state123")
        
        # Initiate auth flow
        auth_url, state = self.provider.initiate_auth_flow()
        
        # Verify result
        self.assertEqual(auth_url, "https://example.com/auth")
        self.assertEqual(state, "state123")
        
        # Verify OAuth manager call
        self.oauth_manager.initiate_auth_flow.assert_called_once_with("google")


if __name__ == '__main__':
    unittest.main()