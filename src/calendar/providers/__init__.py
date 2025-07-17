"""
Calendar provider implementations.

This package contains implementations of the CalendarProvider interface
for different calendar services.
"""

from .google import GoogleCalendarProvider

__all__ = [
    'GoogleCalendarProvider'
]