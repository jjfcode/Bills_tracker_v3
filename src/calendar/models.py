"""
Calendar integration data models.

This module defines data classes for calendar events, sync operations,
and sync settings with proper validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import re

from .exceptions import ValidationError


class SyncOperationType(Enum):
    """Enumeration of sync operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ConflictResolutionStrategy(Enum):
    """Enumeration of conflict resolution strategies."""
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MERGE = "merge"
    ASK_USER = "ask_user"


class EventDuration(Enum):
    """Enumeration of event duration types."""
    ALL_DAY = "all_day"
    TIMED = "timed"


@dataclass
class Reminder:
    """
    Represents a calendar event reminder.
    
    Attributes:
        minutes_before (int): Minutes before event to trigger reminder.
        method (str): Reminder method (email, popup, sms).
    """
    minutes_before: int
    method: str = "popup"
    
    def __post_init__(self):
        """Validate reminder data after initialization."""
        if self.minutes_before < 0:
            raise ValidationError("Reminder minutes must be non-negative", "minutes_before")
        
        if self.minutes_before > 40320:  # 4 weeks in minutes
            raise ValidationError("Reminder cannot be more than 4 weeks before event", "minutes_before")
        
        valid_methods = ["popup", "email", "sms"]
        if self.method not in valid_methods:
            raise ValidationError(f"Invalid reminder method. Must be one of: {', '.join(valid_methods)}", "method")


@dataclass
class CalendarEvent:
    """
    Represents a calendar event for bill synchronization.
    
    Attributes:
        title (str): Event title.
        description (str): Event description.
        start_datetime (datetime): Event start date and time.
        end_datetime (datetime): Event end date and time.
        all_day (bool): Whether the event is all-day.
        reminders (List[Reminder]): List of event reminders.
        color (Optional[str]): Event color (hex format).
        location (Optional[str]): Event location.
        bill_id (int): Associated bill ID.
        external_event_id (Optional[str]): External calendar event ID.
        provider (Optional[str]): Calendar provider name.
        last_modified (Optional[datetime]): Last modification timestamp.
    """
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool
    reminders: List[Reminder]
    bill_id: int
    color: Optional[str] = None
    location: Optional[str] = None
    external_event_id: Optional[str] = None
    provider: Optional[str] = None
    last_modified: Optional[datetime] = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate calendar event data after initialization."""
        # Validate title
        if not self.title or not self.title.strip():
            raise ValidationError("Event title is required", "title")
        
        if len(self.title.strip()) > 255:
            raise ValidationError("Event title cannot exceed 255 characters", "title")
        
        # Validate description
        if len(self.description) > 8192:  # 8KB limit
            raise ValidationError("Event description cannot exceed 8192 characters", "description")
        
        # Validate dates
        if self.start_datetime >= self.end_datetime:
            raise ValidationError("Event start time must be before end time", "start_datetime")
        
        # Validate bill_id
        if self.bill_id <= 0:
            raise ValidationError("Bill ID must be a positive integer", "bill_id")
        
        # Validate color format
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError("Color must be in hex format (#RRGGBB)", "color")
        
        # Validate location
        if self.location and len(self.location) > 255:
            raise ValidationError("Location cannot exceed 255 characters", "location")
        
        # Validate provider
        if self.provider:
            valid_providers = ["google", "outlook", "apple"]
            if self.provider.lower() not in valid_providers:
                raise ValidationError(f"Invalid provider. Must be one of: {', '.join(valid_providers)}", "provider")
        
        # Clean up title and description
        self.title = self.title.strip()
        self.description = self.description.strip()
        if self.location:
            self.location = self.location.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calendar event to dictionary."""
        return {
            'title': self.title,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'all_day': self.all_day,
            'reminders': [{'minutes_before': r.minutes_before, 'method': r.method} for r in self.reminders],
            'color': self.color,
            'location': self.location,
            'bill_id': self.bill_id,
            'external_event_id': self.external_event_id,
            'provider': self.provider,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        """Create calendar event from dictionary."""
        reminders = [
            Reminder(minutes_before=r['minutes_before'], method=r.get('method', 'popup'))
            for r in data.get('reminders', [])
        ]
        
        return cls(
            title=data['title'],
            description=data['description'],
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            all_day=data['all_day'],
            reminders=reminders,
            bill_id=data['bill_id'],
            color=data.get('color'),
            location=data.get('location'),
            external_event_id=data.get('external_event_id'),
            provider=data.get('provider'),
            last_modified=datetime.fromisoformat(data['last_modified']) if data.get('last_modified') else None
        )


@dataclass
class SyncOperation:
    """
    Represents a calendar synchronization operation.
    
    Attributes:
        operation_type (SyncOperationType): Type of sync operation.
        bill_id (int): Associated bill ID.
        calendar_provider (str): Target calendar provider.
        priority (int): Operation priority (lower numbers = higher priority).
        created_at (datetime): Operation creation timestamp.
        retry_count (int): Number of retry attempts.
        max_retries (int): Maximum number of retries allowed.
        last_error (Optional[str]): Last error message if operation failed.
        event_data (Optional[Dict[str, Any]]): Event data for create/update operations.
    """
    operation_type: SyncOperationType
    bill_id: int
    calendar_provider: str
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate sync operation data after initialization."""
        # Validate bill_id
        if self.bill_id <= 0:
            raise ValidationError("Bill ID must be a positive integer", "bill_id")
        
        # Validate calendar_provider
        if not self.calendar_provider or not self.calendar_provider.strip():
            raise ValidationError("Calendar provider is required", "calendar_provider")
        
        valid_providers = ["google", "outlook", "apple"]
        if self.calendar_provider.lower() not in valid_providers:
            raise ValidationError(f"Invalid calendar provider. Must be one of: {', '.join(valid_providers)}", "calendar_provider")
        
        # Validate priority
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 10:
            raise ValidationError("Priority must be an integer between 1 and 10", "priority")
        
        # Validate retry counts
        if self.retry_count < 0:
            raise ValidationError("Retry count cannot be negative", "retry_count")
        
        if self.max_retries < 0:
            raise ValidationError("Max retries cannot be negative", "max_retries")
        
        # Clean up provider name
        self.calendar_provider = self.calendar_provider.lower().strip()
    
    def can_retry(self) -> bool:
        """Check if operation can be retried."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self, error_message: str):
        """Increment retry count and set error message."""
        self.retry_count += 1
        self.last_error = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sync operation to dictionary."""
        return {
            'operation_type': self.operation_type.value,
            'bill_id': self.bill_id,
            'calendar_provider': self.calendar_provider,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'last_error': self.last_error,
            'event_data': self.event_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncOperation':
        """Create sync operation from dictionary."""
        return cls(
            operation_type=SyncOperationType(data['operation_type']),
            bill_id=data['bill_id'],
            calendar_provider=data['calendar_provider'],
            priority=data.get('priority', 5),
            created_at=datetime.fromisoformat(data['created_at']),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            last_error=data.get('last_error'),
            event_data=data.get('event_data')
        )


@dataclass
class EventTemplate:
    """
    Represents a template for generating calendar events from bill data.
    
    Attributes:
        title_template (str): Template for event title with placeholders.
        description_template (str): Template for event description with placeholders.
        duration_type (EventDuration): Whether events should be all-day or timed.
        duration_minutes (int): Duration in minutes for timed events.
        default_color (Optional[str]): Default color for events.
        category_colors (Dict[str, str]): Color mapping by bill category.
    """
    title_template: str = "[Bill] {name} - ${amount}"
    description_template: str = "Bill: {name}\nAmount: ${amount}\nCategory: {category}\nDue Date: {due_date}"
    duration_type: EventDuration = EventDuration.ALL_DAY
    duration_minutes: int = 60
    default_color: Optional[str] = "#1f538d"
    category_colors: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate event template data after initialization."""
        # Validate title template
        if not self.title_template or not self.title_template.strip():
            raise ValidationError("Title template is required", "title_template")
        
        if len(self.title_template) > 255:
            raise ValidationError("Title template cannot exceed 255 characters", "title_template")
        
        # Validate description template
        if len(self.description_template) > 2048:
            raise ValidationError("Description template cannot exceed 2048 characters", "description_template")
        
        # Validate duration
        if self.duration_minutes <= 0:
            raise ValidationError("Duration must be positive", "duration_minutes")
        
        if self.duration_minutes > 1440:  # 24 hours
            raise ValidationError("Duration cannot exceed 24 hours", "duration_minutes")
        
        # Validate colors
        if self.default_color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.default_color):
            raise ValidationError("Default color must be in hex format (#RRGGBB)", "default_color")
        
        for category, color in self.category_colors.items():
            if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                raise ValidationError(f"Category color for '{category}' must be in hex format (#RRGGBB)", "category_colors")


@dataclass
class SyncSettings:
    """
    Represents calendar synchronization settings.
    
    Attributes:
        enabled_providers (List[str]): List of enabled calendar providers.
        sync_categories (List[int]): List of category IDs to sync.
        sync_individual_bills (Dict[int, bool]): Individual bill sync preferences.
        event_template (EventTemplate): Template for generating events.
        sync_frequency_minutes (int): Sync frequency in minutes.
        auto_sync_enabled (bool): Whether automatic sync is enabled.
        sync_on_bill_change (bool): Whether to sync immediately on bill changes.
        conflict_resolution (ConflictResolutionStrategy): Default conflict resolution strategy.
        max_sync_age_days (int): Maximum age of bills to sync (in days).
    """
    enabled_providers: List[str] = field(default_factory=list)
    sync_categories: List[int] = field(default_factory=list)
    sync_individual_bills: Dict[int, bool] = field(default_factory=dict)
    event_template: EventTemplate = field(default_factory=EventTemplate)
    sync_frequency_minutes: int = 60
    auto_sync_enabled: bool = True
    sync_on_bill_change: bool = True
    conflict_resolution: ConflictResolutionStrategy = ConflictResolutionStrategy.ASK_USER
    max_sync_age_days: int = 365
    
    def __post_init__(self):
        """Validate sync settings data after initialization."""
        # Validate providers
        valid_providers = ["google", "outlook", "apple"]
        for provider in self.enabled_providers:
            if provider.lower() not in valid_providers:
                raise ValidationError(f"Invalid provider '{provider}'. Must be one of: {', '.join(valid_providers)}", "enabled_providers")
        
        # Clean up provider names
        self.enabled_providers = [p.lower() for p in self.enabled_providers]
        
        # Validate sync frequency
        if self.sync_frequency_minutes <= 0:
            raise ValidationError("Sync frequency must be positive", "sync_frequency_minutes")
        
        if self.sync_frequency_minutes > 10080:  # 1 week
            raise ValidationError("Sync frequency cannot exceed 1 week", "sync_frequency_minutes")
        
        # Validate max sync age
        if self.max_sync_age_days <= 0:
            raise ValidationError("Max sync age must be positive", "max_sync_age_days")
        
        if self.max_sync_age_days > 3650:  # 10 years
            raise ValidationError("Max sync age cannot exceed 10 years", "max_sync_age_days")
        
        # Validate category IDs
        for category_id in self.sync_categories:
            if not isinstance(category_id, int) or category_id <= 0:
                raise ValidationError("Category IDs must be positive integers", "sync_categories")
        
        # Validate individual bill settings
        for bill_id, enabled in self.sync_individual_bills.items():
            if not isinstance(bill_id, int) or bill_id <= 0:
                raise ValidationError("Bill IDs must be positive integers", "sync_individual_bills")
            if not isinstance(enabled, bool):
                raise ValidationError("Individual bill sync settings must be boolean", "sync_individual_bills")
    
    def is_bill_sync_enabled(self, bill_id: int, category_id: Optional[int] = None) -> bool:
        """
        Check if sync is enabled for a specific bill.
        
        Args:
            bill_id (int): Bill ID to check.
            category_id (Optional[int]): Bill category ID.
            
        Returns:
            bool: True if sync is enabled for the bill.
        """
        # Check individual bill setting first
        if bill_id in self.sync_individual_bills:
            return self.sync_individual_bills[bill_id]
        
        # Check category setting if categories are specified
        if self.sync_categories:
            if category_id:
                return category_id in self.sync_categories
            else:
                # If categories are specified but bill has no category, don't sync
                return False
        
        # Default to enabled if no specific settings
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sync settings to dictionary."""
        return {
            'enabled_providers': self.enabled_providers,
            'sync_categories': self.sync_categories,
            'sync_individual_bills': self.sync_individual_bills,
            'event_template': {
                'title_template': self.event_template.title_template,
                'description_template': self.event_template.description_template,
                'duration_type': self.event_template.duration_type.value,
                'duration_minutes': self.event_template.duration_minutes,
                'default_color': self.event_template.default_color,
                'category_colors': self.event_template.category_colors
            },
            'sync_frequency_minutes': self.sync_frequency_minutes,
            'auto_sync_enabled': self.auto_sync_enabled,
            'sync_on_bill_change': self.sync_on_bill_change,
            'conflict_resolution': self.conflict_resolution.value,
            'max_sync_age_days': self.max_sync_age_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncSettings':
        """Create sync settings from dictionary."""
        template_data = data.get('event_template', {})
        event_template = EventTemplate(
            title_template=template_data.get('title_template', "[Bill] {name} - ${amount}"),
            description_template=template_data.get('description_template', "Bill: {name}\nAmount: ${amount}\nCategory: {category}\nDue Date: {due_date}"),
            duration_type=EventDuration(template_data.get('duration_type', 'all_day')),
            duration_minutes=template_data.get('duration_minutes', 60),
            default_color=template_data.get('default_color', "#1f538d"),
            category_colors=template_data.get('category_colors', {})
        )
        
        return cls(
            enabled_providers=data.get('enabled_providers', []),
            sync_categories=data.get('sync_categories', []),
            sync_individual_bills=data.get('sync_individual_bills', {}),
            event_template=event_template,
            sync_frequency_minutes=data.get('sync_frequency_minutes', 60),
            auto_sync_enabled=data.get('auto_sync_enabled', True),
            sync_on_bill_change=data.get('sync_on_bill_change', True),
            conflict_resolution=ConflictResolutionStrategy(data.get('conflict_resolution', 'ask_user')),
            max_sync_age_days=data.get('sync_age_days', 365)
        )