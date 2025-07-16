"""
Unit tests for calendar integration data models.
"""

import pytest
from datetime import datetime, timedelta, date
from src.calendar.models import (
    CalendarEvent, SyncOperation, SyncSettings, EventTemplate, Reminder,
    SyncOperationType, ConflictResolutionStrategy, EventDuration
)
from src.calendar.exceptions import ValidationError


class TestReminder:
    """Test cases for Reminder model."""
    
    def test_valid_reminder_creation(self):
        """Test creating a valid reminder."""
        reminder = Reminder(minutes_before=60, method="popup")
        assert reminder.minutes_before == 60
        assert reminder.method == "popup"
    
    def test_reminder_default_method(self):
        """Test reminder with default method."""
        reminder = Reminder(minutes_before=30)
        assert reminder.method == "popup"
    
    def test_reminder_invalid_minutes_negative(self):
        """Test reminder with negative minutes."""
        with pytest.raises(ValidationError) as exc_info:
            Reminder(minutes_before=-10)
        assert "non-negative" in str(exc_info.value)
    
    def test_reminder_invalid_minutes_too_large(self):
        """Test reminder with too many minutes."""
        with pytest.raises(ValidationError) as exc_info:
            Reminder(minutes_before=50000)  # More than 4 weeks
        assert "4 weeks" in str(exc_info.value)
    
    def test_reminder_invalid_method(self):
        """Test reminder with invalid method."""
        with pytest.raises(ValidationError) as exc_info:
            Reminder(minutes_before=60, method="invalid")
        assert "Invalid reminder method" in str(exc_info.value)


class TestCalendarEvent:
    """Test cases for CalendarEvent model."""
    
    def create_valid_event(self) -> CalendarEvent:
        """Create a valid calendar event for testing."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        return CalendarEvent(
            title="Test Bill Payment",
            description="Payment for electricity bill",
            start_datetime=start_time,
            end_datetime=end_time,
            all_day=False,
            reminders=[Reminder(minutes_before=60)],
            bill_id=1,
            color="#ff0000"
        )
    
    def test_valid_event_creation(self):
        """Test creating a valid calendar event."""
        event = self.create_valid_event()
        assert event.title == "Test Bill Payment"
        assert event.bill_id == 1
        assert len(event.reminders) == 1
        assert event.color == "#ff0000"
    
    def test_event_title_validation_empty(self):
        """Test event with empty title."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="",
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1
            )
        assert "title is required" in str(exc_info.value)
    
    def test_event_title_validation_too_long(self):
        """Test event with title too long."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="x" * 300,  # Too long
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1
            )
        assert "cannot exceed 255 characters" in str(exc_info.value)
    
    def test_event_description_validation_too_long(self):
        """Test event with description too long."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="Test",
                description="x" * 10000,  # Too long
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1
            )
        assert "cannot exceed 8192 characters" in str(exc_info.value)
    
    def test_event_date_validation_invalid_order(self):
        """Test event with start time after end time."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time - timedelta(hours=1)  # Before start time
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="Test",
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1
            )
        assert "start time must be before end time" in str(exc_info.value)
    
    def test_event_bill_id_validation_invalid(self):
        """Test event with invalid bill ID."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="Test",
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=0  # Invalid
            )
        assert "positive integer" in str(exc_info.value)
    
    def test_event_color_validation_invalid_format(self):
        """Test event with invalid color format."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="Test",
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1,
                color="invalid"  # Invalid format
            )
        assert "hex format" in str(exc_info.value)
    
    def test_event_provider_validation_invalid(self):
        """Test event with invalid provider."""
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValidationError) as exc_info:
            CalendarEvent(
                title="Test",
                description="Test",
                start_datetime=start_time,
                end_datetime=end_time,
                all_day=False,
                reminders=[],
                bill_id=1,
                provider="invalid"
            )
        assert "Invalid provider" in str(exc_info.value)
    
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = self.create_valid_event()
        event_dict = event.to_dict()
        
        assert event_dict['title'] == event.title
        assert event_dict['bill_id'] == event.bill_id
        assert len(event_dict['reminders']) == 1
        assert event_dict['color'] == event.color
    
    def test_event_from_dict(self):
        """Test creating event from dictionary."""
        event_dict = {
            'title': 'Test Bill',
            'description': 'Test description',
            'start_datetime': '2024-01-01T10:00:00',
            'end_datetime': '2024-01-01T11:00:00',
            'all_day': False,
            'reminders': [{'minutes_before': 60, 'method': 'popup'}],
            'bill_id': 1,
            'color': '#ff0000'
        }
        
        event = CalendarEvent.from_dict(event_dict)
        assert event.title == 'Test Bill'
        assert event.bill_id == 1
        assert len(event.reminders) == 1
        assert event.color == '#ff0000'


class TestSyncOperation:
    """Test cases for SyncOperation model."""
    
    def test_valid_sync_operation_creation(self):
        """Test creating a valid sync operation."""
        operation = SyncOperation(
            operation_type=SyncOperationType.CREATE,
            bill_id=1,
            calendar_provider="google"
        )
        
        assert operation.operation_type == SyncOperationType.CREATE
        assert operation.bill_id == 1
        assert operation.calendar_provider == "google"
        assert operation.priority == 5  # Default
        assert operation.retry_count == 0
    
    def test_sync_operation_bill_id_validation(self):
        """Test sync operation with invalid bill ID."""
        with pytest.raises(ValidationError) as exc_info:
            SyncOperation(
                operation_type=SyncOperationType.CREATE,
                bill_id=0,  # Invalid
                calendar_provider="google"
            )
        assert "positive integer" in str(exc_info.value)
    
    def test_sync_operation_provider_validation_empty(self):
        """Test sync operation with empty provider."""
        with pytest.raises(ValidationError) as exc_info:
            SyncOperation(
                operation_type=SyncOperationType.CREATE,
                bill_id=1,
                calendar_provider=""  # Empty
            )
        assert "provider is required" in str(exc_info.value)
    
    def test_sync_operation_provider_validation_invalid(self):
        """Test sync operation with invalid provider."""
        with pytest.raises(ValidationError) as exc_info:
            SyncOperation(
                operation_type=SyncOperationType.CREATE,
                bill_id=1,
                calendar_provider="invalid"
            )
        assert "Invalid calendar provider" in str(exc_info.value)
    
    def test_sync_operation_priority_validation(self):
        """Test sync operation with invalid priority."""
        with pytest.raises(ValidationError) as exc_info:
            SyncOperation(
                operation_type=SyncOperationType.CREATE,
                bill_id=1,
                calendar_provider="google",
                priority=15  # Too high
            )
        assert "between 1 and 10" in str(exc_info.value)
    
    def test_sync_operation_can_retry(self):
        """Test sync operation retry logic."""
        operation = SyncOperation(
            operation_type=SyncOperationType.CREATE,
            bill_id=1,
            calendar_provider="google",
            max_retries=3
        )
        
        assert operation.can_retry() is True
        
        operation.increment_retry("Test error")
        assert operation.retry_count == 1
        assert operation.last_error == "Test error"
        assert operation.can_retry() is True
        
        # Exhaust retries
        operation.increment_retry("Error 2")
        operation.increment_retry("Error 3")
        assert operation.can_retry() is False
    
    def test_sync_operation_to_dict(self):
        """Test converting sync operation to dictionary."""
        operation = SyncOperation(
            operation_type=SyncOperationType.UPDATE,
            bill_id=2,
            calendar_provider="outlook"
        )
        
        op_dict = operation.to_dict()
        assert op_dict['operation_type'] == 'update'
        assert op_dict['bill_id'] == 2
        assert op_dict['calendar_provider'] == 'outlook'
    
    def test_sync_operation_from_dict(self):
        """Test creating sync operation from dictionary."""
        op_dict = {
            'operation_type': 'delete',
            'bill_id': 3,
            'calendar_provider': 'apple',
            'priority': 1,
            'created_at': '2024-01-01T10:00:00',
            'retry_count': 2,
            'max_retries': 5
        }
        
        operation = SyncOperation.from_dict(op_dict)
        assert operation.operation_type == SyncOperationType.DELETE
        assert operation.bill_id == 3
        assert operation.calendar_provider == 'apple'
        assert operation.priority == 1
        assert operation.retry_count == 2


class TestEventTemplate:
    """Test cases for EventTemplate model."""
    
    def test_valid_event_template_creation(self):
        """Test creating a valid event template."""
        template = EventTemplate(
            title_template="Bill: {name}",
            description_template="Amount: ${amount}",
            duration_type=EventDuration.TIMED,
            duration_minutes=30
        )
        
        assert template.title_template == "Bill: {name}"
        assert template.duration_type == EventDuration.TIMED
        assert template.duration_minutes == 30
    
    def test_event_template_defaults(self):
        """Test event template with default values."""
        template = EventTemplate()
        assert "[Bill]" in template.title_template
        assert template.duration_type == EventDuration.ALL_DAY
        assert template.duration_minutes == 60
    
    def test_event_template_title_validation_empty(self):
        """Test event template with empty title."""
        with pytest.raises(ValidationError) as exc_info:
            EventTemplate(title_template="")
        assert "Title template is required" in str(exc_info.value)
    
    def test_event_template_duration_validation_negative(self):
        """Test event template with negative duration."""
        with pytest.raises(ValidationError) as exc_info:
            EventTemplate(duration_minutes=-10)
        assert "Duration must be positive" in str(exc_info.value)
    
    def test_event_template_duration_validation_too_large(self):
        """Test event template with duration too large."""
        with pytest.raises(ValidationError) as exc_info:
            EventTemplate(duration_minutes=2000)  # More than 24 hours
        assert "cannot exceed 24 hours" in str(exc_info.value)
    
    def test_event_template_color_validation(self):
        """Test event template with invalid color."""
        with pytest.raises(ValidationError) as exc_info:
            EventTemplate(default_color="invalid")
        assert "hex format" in str(exc_info.value)
    
    def test_event_template_category_colors_validation(self):
        """Test event template with invalid category colors."""
        with pytest.raises(ValidationError) as exc_info:
            EventTemplate(category_colors={"utilities": "invalid"})
        assert "hex format" in str(exc_info.value)


class TestSyncSettings:
    """Test cases for SyncSettings model."""
    
    def test_valid_sync_settings_creation(self):
        """Test creating valid sync settings."""
        settings = SyncSettings(
            enabled_providers=["google", "outlook"],
            sync_categories=[1, 2, 3],
            sync_frequency_minutes=30
        )
        
        assert "google" in settings.enabled_providers
        assert "outlook" in settings.enabled_providers
        assert settings.sync_categories == [1, 2, 3]
        assert settings.sync_frequency_minutes == 30
    
    def test_sync_settings_defaults(self):
        """Test sync settings with default values."""
        settings = SyncSettings()
        assert settings.enabled_providers == []
        assert settings.auto_sync_enabled is True
        assert settings.sync_on_bill_change is True
        assert settings.conflict_resolution == ConflictResolutionStrategy.ASK_USER
    
    def test_sync_settings_provider_validation(self):
        """Test sync settings with invalid provider."""
        with pytest.raises(ValidationError) as exc_info:
            SyncSettings(enabled_providers=["invalid"])
        assert "Invalid provider" in str(exc_info.value)
    
    def test_sync_settings_frequency_validation_negative(self):
        """Test sync settings with negative frequency."""
        with pytest.raises(ValidationError) as exc_info:
            SyncSettings(sync_frequency_minutes=-10)
        assert "Sync frequency must be positive" in str(exc_info.value)
    
    def test_sync_settings_frequency_validation_too_large(self):
        """Test sync settings with frequency too large."""
        with pytest.raises(ValidationError) as exc_info:
            SyncSettings(sync_frequency_minutes=20000)  # More than 1 week
        assert "cannot exceed 1 week" in str(exc_info.value)
    
    def test_sync_settings_category_validation(self):
        """Test sync settings with invalid category IDs."""
        with pytest.raises(ValidationError) as exc_info:
            SyncSettings(sync_categories=[0, -1])  # Invalid IDs
        assert "positive integers" in str(exc_info.value)
    
    def test_sync_settings_is_bill_sync_enabled(self):
        """Test bill sync enabled logic."""
        settings = SyncSettings(
            sync_categories=[1, 2],
            sync_individual_bills={10: False, 11: True}
        )
        
        # Individual bill setting takes precedence
        assert settings.is_bill_sync_enabled(10) is False
        assert settings.is_bill_sync_enabled(11) is True
        
        # Category-based setting
        assert settings.is_bill_sync_enabled(20, category_id=1) is True
        assert settings.is_bill_sync_enabled(21, category_id=3) is False  # Not in sync categories
        
        # No category provided when categories are specified - should not sync
        assert settings.is_bill_sync_enabled(30) is False
        
        # Test with no category restrictions
        settings_no_categories = SyncSettings()
        assert settings_no_categories.is_bill_sync_enabled(30) is True  # Default enabled
    
    def test_sync_settings_to_dict(self):
        """Test converting sync settings to dictionary."""
        settings = SyncSettings(
            enabled_providers=["google"],
            sync_categories=[1, 2]
        )
        
        settings_dict = settings.to_dict()
        assert settings_dict['enabled_providers'] == ["google"]
        assert settings_dict['sync_categories'] == [1, 2]
        assert 'event_template' in settings_dict
    
    def test_sync_settings_from_dict(self):
        """Test creating sync settings from dictionary."""
        settings_dict = {
            'enabled_providers': ['outlook'],
            'sync_categories': [3, 4],
            'sync_frequency_minutes': 120,
            'auto_sync_enabled': False
        }
        
        settings = SyncSettings.from_dict(settings_dict)
        assert settings.enabled_providers == ['outlook']
        assert settings.sync_categories == [3, 4]
        assert settings.sync_frequency_minutes == 120
        assert settings.auto_sync_enabled is False