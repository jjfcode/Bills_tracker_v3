"""
Calendar module tests.

This module provides tests for the calendar integration functionality.
"""

# Add timegm function to avoid import conflicts with standard library calendar module
def timegm(tuple_time):
    """
    Convert a time tuple in UTC to seconds since the epoch.
    
    This is a reimplementation of calendar.timegm to avoid import conflicts.
    """
    import time
    return int(time.mktime(tuple_time) - time.timezone)