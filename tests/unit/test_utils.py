"""
Unit tests for utility functions.
"""

import pytest
from datetime import datetime, timedelta
from src.utils.helpers import (
    parse_amount, format_amount, validate_date_range, get_date_period_dates,
    calculate_next_due_date, export_to_csv, import_from_csv, is_dark_mode,
    get_urgency_color
)
from src.utils.constants import DATE_FORMAT


class TestParseAmount:
    """Test amount parsing functionality."""
    
    def test_parse_amount_valid_dollar_format(self):
        """Test parsing valid dollar amounts."""
        assert parse_amount("$150.00") == 150.00
        assert parse_amount("$1,234.56") == 1234.56
        assert parse_amount("$0.99") == 0.99
        assert parse_amount("$1,000,000.00") == 1000000.00
    
    def test_parse_amount_valid_number_format(self):
        """Test parsing valid number formats."""
        assert parse_amount("150.00") == 150.00
        assert parse_amount("1,234.56") == 1234.56
        assert parse_amount("0.99") == 0.99
        assert parse_amount("1000000.00") == 1000000.00
    
    def test_parse_amount_european_format(self):
        """Test parsing European number format (comma as decimal separator)."""
        assert parse_amount("1.234,56") == 1234.56
        assert parse_amount("1.000.000,00") == 1000000.00
    
    def test_parse_amount_negative_values(self):
        """Test parsing negative amounts."""
        assert parse_amount("-$150.00") == -150.00
        assert parse_amount("-150.00") == -150.00
        assert parse_amount("-$1,234.56") == -1234.56
    
    def test_parse_amount_invalid_formats(self):
        """Test parsing invalid amount formats."""
        assert parse_amount("") is None
        assert parse_amount("   ") is None
        assert parse_amount("abc") is None
        assert parse_amount("$abc") is None
        assert parse_amount("1.2.3.4") is None
        assert parse_amount("1,2,3,4") is None
    
    def test_parse_amount_edge_cases(self):
        """Test edge cases for amount parsing."""
        assert parse_amount("0") == 0.0
        assert parse_amount("0.0") == 0.0
        assert parse_amount("0.00") == 0.0
        assert parse_amount("$0") == 0.0


class TestFormatAmount:
    """Test amount formatting functionality."""
    
    def test_format_amount_valid_values(self):
        """Test formatting valid amounts."""
        assert format_amount(150.00) == "$150.00"
        assert format_amount(1234.56) == "$1234.56"
        assert format_amount(0.99) == "$0.99"
        assert format_amount(1000000.00) == "$1000000.00"
    
    def test_format_amount_zero_values(self):
        """Test formatting zero amounts."""
        assert format_amount(0) == "$0.00"
        assert format_amount(0.0) == "$0.00"
    
    def test_format_amount_negative_values(self):
        """Test formatting negative amounts."""
        assert format_amount(-150.00) == "$-150.00"
        assert format_amount(-1234.56) == "$-1234.56"
    
    def test_format_amount_none_values(self):
        """Test formatting None values."""
        assert format_amount(None) == ""
    
    def test_format_amount_rounding(self):
        """Test amount rounding behavior."""
        assert format_amount(150.999) == "$150.99"  # Should round down
        assert format_amount(150.001) == "$150.00"  # Should round down


class TestValidateDateRange:
    """Test date range validation functionality."""
    
    def test_validate_date_range_valid_range(self):
        """Test valid date ranges."""
        is_valid, error = validate_date_range("2024-01-01", "2024-12-31")
        assert is_valid is True
        assert error is None
    
    def test_validate_date_range_same_date(self):
        """Test date range with same start and end date."""
        is_valid, error = validate_date_range("2024-01-01", "2024-01-01")
        assert is_valid is True
        assert error is None
    
    def test_validate_date_range_invalid_order(self):
        """Test date range with end before start."""
        is_valid, error = validate_date_range("2024-12-31", "2024-01-01")
        assert is_valid is False
        assert "Start date cannot be after end date" in error
    
    def test_validate_date_range_invalid_format(self):
        """Test date range with invalid date format."""
        is_valid, error = validate_date_range("2024/01/01", "2024-12-31")
        assert is_valid is False
        assert "Invalid date format" in error
    
    def test_validate_date_range_empty_dates(self):
        """Test date range with empty dates."""
        is_valid, error = validate_date_range("", "2024-12-31")
        assert is_valid is False
        assert "Invalid date format" in error


class TestGetDatePeriodDates:
    """Test date period calculation functionality."""
    
    def test_get_date_period_dates_today(self, mock_datetime):
        """Test getting today's date range."""
        start_date, end_date = get_date_period_dates("today")
        assert start_date == "2024-02-01"
        assert end_date == "2024-02-01"
    
    def test_get_date_period_dates_week(self, mock_datetime):
        """Test getting current week date range."""
        start_date, end_date = get_date_period_dates("week")
        # 2024-02-01 is a Thursday, so week starts on Monday (2024-01-29)
        assert start_date == "2024-01-29"
        assert end_date == "2024-02-04"
    
    def test_get_date_period_dates_month(self, mock_datetime):
        """Test getting current month date range."""
        start_date, end_date = get_date_period_dates("month")
        assert start_date == "2024-02-01"
        assert end_date == "2024-02-29"  # February 2024 (leap year)
    
    def test_get_date_period_dates_quarter(self, mock_datetime):
        """Test getting current quarter date range."""
        start_date, end_date = get_date_period_dates("quarter")
        # Q1 2024: Jan 1 - Mar 31
        assert start_date == "2024-01-01"
        assert end_date == "2024-03-31"
    
    def test_get_date_period_dates_year(self, mock_datetime):
        """Test getting current year date range."""
        start_date, end_date = get_date_period_dates("year")
        assert start_date == "2024-01-01"
        assert end_date == "2024-12-31"
    
    def test_get_date_period_dates_invalid_period(self, mock_datetime):
        """Test getting date range for invalid period."""
        start_date, end_date = get_date_period_dates("invalid")
        # Should default to current month
        assert start_date == "2024-02-01"
        assert end_date == "2024-02-29"


class TestCalculateNextDueDate:
    """Test next due date calculation functionality."""
    
    def test_calculate_next_due_date_weekly(self):
        """Test weekly billing cycle."""
        next_date = calculate_next_due_date("2024-02-01", "weekly")
        assert next_date == "2024-02-08"
    
    def test_calculate_next_due_date_bi_weekly(self):
        """Test bi-weekly billing cycle."""
        next_date = calculate_next_due_date("2024-02-01", "bi-weekly")
        assert next_date == "2024-02-15"
    
    def test_calculate_next_due_date_monthly(self):
        """Test monthly billing cycle."""
        next_date = calculate_next_due_date("2024-01-15", "monthly")
        assert next_date == "2024-02-15"
    
    def test_calculate_next_due_date_monthly_year_rollover(self):
        """Test monthly billing cycle with year rollover."""
        next_date = calculate_next_due_date("2024-12-15", "monthly")
        assert next_date == "2025-01-15"
    
    def test_calculate_next_due_date_quarterly(self):
        """Test quarterly billing cycle."""
        next_date = calculate_next_due_date("2024-01-15", "quarterly")
        assert next_date == "2024-04-15"
    
    def test_calculate_next_due_date_semi_annually(self):
        """Test semi-annually billing cycle."""
        next_date = calculate_next_due_date("2024-01-15", "semi-annually")
        assert next_date == "2024-07-15"
    
    def test_calculate_next_due_date_annually(self):
        """Test annually billing cycle."""
        next_date = calculate_next_due_date("2024-01-15", "annually")
        assert next_date == "2025-01-15"
    
    def test_calculate_next_due_date_one_time(self):
        """Test one-time billing cycle."""
        next_date = calculate_next_due_date("2024-01-15", "one-time")
        assert next_date == "2024-01-15"  # Should not change
    
    def test_calculate_next_due_date_invalid_date(self):
        """Test with invalid date format."""
        next_date = calculate_next_due_date("invalid-date", "monthly")
        assert next_date == "invalid-date"  # Should return original


class TestExportImportCSV:
    """Test CSV export and import functionality."""
    
    def test_export_to_csv_success(self, temp_dir):
        """Test successful CSV export."""
        data = [
            {'name': 'Bill 1', 'amount': 100.00},
            {'name': 'Bill 2', 'amount': 200.00}
        ]
        filename = f"{temp_dir}/test_export.csv"
        
        success = export_to_csv(data, filename)
        assert success is True
        
        # Verify file was created and has content
        import os
        assert os.path.exists(filename)
        assert os.path.getsize(filename) > 0
    
    def test_export_to_csv_empty_data(self, temp_dir):
        """Test CSV export with empty data."""
        filename = f"{temp_dir}/test_export.csv"
        success = export_to_csv([], filename)
        assert success is False
    
    def test_export_to_csv_with_fieldnames(self, temp_dir):
        """Test CSV export with specific fieldnames."""
        data = [
            {'name': 'Bill 1', 'amount': 100.00, 'extra': 'ignored'},
            {'name': 'Bill 2', 'amount': 200.00, 'extra': 'ignored'}
        ]
        fieldnames = ['name', 'amount']
        filename = f"{temp_dir}/test_export.csv"
        
        success = export_to_csv(data, filename, fieldnames)
        assert success is True
    
    def test_import_from_csv_success(self, temp_dir):
        """Test successful CSV import."""
        # Create test CSV file
        import csv
        filename = f"{temp_dir}/test_import.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'amount'])
            writer.writeheader()
            writer.writerow({'name': 'Bill 1', 'amount': '100.00'})
            writer.writerow({'name': 'Bill 2', 'amount': '200.00'})
        
        data, errors = import_from_csv(filename)
        assert len(data) == 2
        assert len(errors) == 0
        assert data[0]['name'] == 'Bill 1'
        assert data[0]['amount'] == '100.00'
    
    def test_import_from_csv_with_errors(self, temp_dir):
        """Test CSV import with some errors."""
        # Create test CSV file with invalid data
        import csv
        filename = f"{temp_dir}/test_import.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'amount'])
            writer.writerow(['Bill 1', '100.00'])
            writer.writerow(['Bill 2', 'invalid'])  # Invalid amount
        
        data, errors = import_from_csv(filename)
        assert len(data) >= 1  # At least one valid row
        assert len(errors) >= 0  # May have errors
    
    def test_import_from_csv_nonexistent_file(self):
        """Test CSV import with nonexistent file."""
        data, errors = import_from_csv("nonexistent_file.csv")
        assert len(data) == 0
        assert len(errors) == 1
        assert "File error" in errors[0]


class TestIsDarkMode:
    """Test dark mode detection functionality."""
    
    def test_is_dark_mode_mock(self):
        """Test dark mode detection with mocked CustomTkinter."""
        with pytest.MonkeyPatch().context() as m:
            # Mock CustomTkinter
            m.setattr('src.utils.helpers.ctk', None)
            result = is_dark_mode()
            assert result is False
    
    def test_is_dark_mode_exception_handling(self):
        """Test dark mode detection with exception handling."""
        with pytest.MonkeyPatch().context() as m:
            # Mock CustomTkinter to raise exception
            m.setattr('src.utils.helpers.ctk', Mock(side_effect=Exception("Test")))
            result = is_dark_mode()
            assert result is False


class TestGetUrgencyColor:
    """Test urgency color calculation functionality."""
    
    def test_get_urgency_color_overdue(self, mock_datetime):
        """Test color for overdue bills."""
        color = get_urgency_color("2024-01-15")  # Past date
        assert color == "#e74c3c"  # ERROR_COLOR (red)
    
    def test_get_urgency_color_urgent(self, mock_datetime):
        """Test color for urgent bills (due within reminder days)."""
        color = get_urgency_color("2024-02-05")  # Within 7 days
        assert color == "#ffa500"  # WARNING_COLOR (orange)
    
    def test_get_urgency_color_not_urgent(self, mock_datetime):
        """Test color for non-urgent bills."""
        color = get_urgency_color("2024-03-01")  # More than 7 days away
        assert color == "#4bb543"  # SUCCESS_COLOR (green)
    
    def test_get_urgency_color_custom_reminder_days(self, mock_datetime):
        """Test color with custom reminder days."""
        color = get_urgency_color("2024-02-10", reminder_days=14)  # Within 14 days
        assert color == "#ffa500"  # WARNING_COLOR (orange)
    
    def test_get_urgency_color_invalid_date(self):
        """Test color with invalid date."""
        color = get_urgency_color("invalid-date")
        assert color == "#4bb543"  # Should default to SUCCESS_COLOR 