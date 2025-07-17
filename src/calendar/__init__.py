"""
Calendar integration module for Bills Tracker.

This module provides calendar synchronization functionality with external calendar providers
such as Google Calendar, Microsoft Outlook, and Apple Calendar.
"""

from .models import CalendarEvent, SyncOperation, SyncSettings, Reminder, EventTemplate
from .interfaces import CalendarProvider, AuthResult, ConnectionResult, EventResult, DateRange
from .exceptions import CalendarError, AuthError, SyncError, ValidationError, ConnectionError, RateLimitError, ConflictError
from .oauth import OAuthManager, OAuthConfig, CredentialStorage
from .providers import GoogleCalendarProvider

__all__ = [
    'CalendarEvent',
    'SyncOperation', 
    'SyncSettings',
    'Reminder',
    'EventTemplate',
    'CalendarProvider',
    'AuthResult',
    'ConnectionResult',
    'EventResult',
    'DateRange',
    'CalendarError',
    'AuthError',
    'SyncError',
    'ValidationError',
    'ConnectionError',
    'RateLimitError',
    'ConflictError',
    'OAuthManager',
    'OAuthConfig',
    'CredentialStorage',
    'GoogleCalendarProvider'
]