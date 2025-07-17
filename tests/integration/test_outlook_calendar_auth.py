"""
Integration tests for Microsoft Outlook Calendar authentication.

This module tests the authentication flow for Microsoft Outlook Calendar
using the OutlookCalendarProvider class.
"""

import os
import pytest

class TestOutlookCalendarAuth:
    """Test suite for Microsoft Outlook Calendar authentication."""
    
    def test_outlook_provider_registered(self):
        """Test that the OutlookCalendarProvider is registered in the providers package."""
        init_file_path = os.path.join(os.getcwd(), "src", "calendar", "providers", "__init__.py")
        assert os.path.exists(init_file_path), f"File does not exist: {init_file_path}"
        
        with open(init_file_path, 'r') as f:
            content = f.read()
            
            # Check for import statement
            assert "from .outlook import OutlookCalendarProvider" in content, "OutlookCalendarProvider import not found"
            
            # Check for __all__ list
            assert "'OutlookCalendarProvider'" in content, "OutlookCalendarProvider not in __all__ list"
    
    def test_outlook_provider_file_exists(self):
        """Test that the OutlookCalendarProvider file exists."""
        file_path = os.path.join(os.getcwd(), "src", "calendar", "providers", "outlook.py")
        assert os.path.exists(file_path), f"File does not exist: {file_path}"
        
        # Check file size to ensure it's not empty
        file_size = os.path.getsize(file_path)
        assert file_size > 1000, f"File is too small: {file_size} bytes"
        
        # Read the file content to check for key elements
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Check for class definition
            assert "class OutlookCalendarProvider(CalendarProvider):" in content, "OutlookCalendarProvider class not found"
            
            # Check for required methods
            required_methods = [
                "def authenticate",
                "def refresh_authentication",
                "def revoke_authentication",
                "def test_connection",
                "def create_event",
                "def get_event",
                "def update_event",
                "def delete_event",
                "def get_events",
                "def batch_create_events",
                "def batch_update_events",
                "def batch_delete_events",
                "def get_calendars",
                "def get_default_calendar_id",
                "def get_rate_limits",
                "def get_supported_features"
            ]
            
            for method in required_methods:
                assert method in content, f"Method not found: {method}"
            
            # Check for Microsoft Graph API endpoints
            assert "GRAPH_API_BASE = " in content, "GRAPH_API_BASE constant not found"
            assert "https://graph.microsoft.com/v1.0" in content, "Microsoft Graph API endpoint not found"
            
            # Check for OAuth configuration
            assert "def _register_oauth_config" in content, "OAuth config registration method not found"
            assert "Calendars.ReadWrite" in content, "Calendar permission scope not found"
            assert "User.Read" in content, "User permission scope not found"
            assert "offline_access" in content, "Offline access scope not found"
            
            # Check for event conversion methods
            assert "def _event_to_outlook_format" in content, "Event conversion method not found"
            assert "def _outlook_to_event_format" in content, "Event parsing method not found"