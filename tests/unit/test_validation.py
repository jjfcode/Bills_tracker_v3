"""
Unit tests for validation module.
"""

import pytest
from datetime import datetime, timedelta
from src.core.validation import DataValidator, BillValidator, CategoryValidator


class TestBillValidator:
    """Test BillValidator functionality."""
    
    def test_validate_required_fields_success(self):
        """Test successful validation of required fields."""
        bill_data = {
            'name': 'Test Bill',
            'due_date': '2024-12-31',
            'category_id': 1
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_required_fields_missing_name(self):
        """Test validation failure when name is missing."""
        bill_data = {
            'due_date': '2024-12-31',
            'category_id': 1
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is False
        assert "Bill name is required" in error
    
    def test_validate_required_fields_empty_name(self):
        """Test validation failure when name is empty."""
        bill_data = {
            'name': '',
            'due_date': '2024-12-31',
            'category_id': 1
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is False
        assert "Bill name is required" in error
    
    def test_validate_required_fields_whitespace_name(self):
        """Test validation failure when name is only whitespace."""
        bill_data = {
            'name': '   ',
            'due_date': '2024-12-31',
            'category_id': 1
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is False
        assert "Bill name is required" in error
    
    def test_validate_required_fields_missing_due_date(self):
        """Test validation failure when due_date is missing."""
        bill_data = {
            'name': 'Test Bill',
            'category_id': 1
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is False
        assert "Due date is required" in error
    
    def test_validate_required_fields_missing_category(self):
        """Test validation failure when category_id is missing."""
        bill_data = {
            'name': 'Test Bill',
            'due_date': '2024-12-31'
        }
        
        is_valid, error = BillValidator.validate_required_fields(bill_data)
        assert is_valid is False
        assert "Category is required" in error
    
    def test_validate_name_length_success(self):
        """Test successful name length validation."""
        bill_data = {'name': 'Valid Bill Name'}
        
        is_valid, error = BillValidator.validate_name_length(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_name_length_too_short(self):
        """Test name length validation failure when too short."""
        bill_data = {'name': ''}
        
        is_valid, error = BillValidator.validate_name_length(bill_data)
        assert is_valid is False
        assert "Bill name must be between 1 and 100 characters" in error
    
    def test_validate_name_length_too_long(self):
        """Test name length validation failure when too long."""
        bill_data = {'name': 'A' * 101}
        
        is_valid, error = BillValidator.validate_name_length(bill_data)
        assert is_valid is False
        assert "Bill name must be between 1 and 100 characters" in error
    
    def test_validate_name_characters_success(self):
        """Test successful name character validation."""
        bill_data = {'name': 'Valid Bill Name 123'}
        
        is_valid, error = BillValidator.validate_name_characters(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_name_characters_invalid(self):
        """Test name character validation failure with invalid characters."""
        bill_data = {'name': 'Invalid<>Bill'}
        
        is_valid, error = BillValidator.validate_name_characters(bill_data)
        assert is_valid is False
        assert "Bill name contains invalid characters" in error
    
    def test_validate_date_format_success(self):
        """Test successful date format validation."""
        bill_data = {'due_date': '2024-12-31'}
        
        is_valid, error = BillValidator.validate_date_format(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_date_format_invalid_format(self):
        """Test date format validation failure with invalid format."""
        bill_data = {'due_date': '12/31/2024'}
        
        is_valid, error = BillValidator.validate_date_format(bill_data)
        assert is_valid is False
        assert "Due date must be in YYYY-MM-DD format" in error
    
    def test_validate_date_format_invalid_date(self):
        """Test date format validation failure with invalid date."""
        bill_data = {'due_date': '2024-13-45'}
        
        is_valid, error = BillValidator.validate_date_format(bill_data)
        assert is_valid is False
        assert "Invalid date" in error
    
    def test_validate_date_range_success(self):
        """Test successful date range validation."""
        bill_data = {'due_date': '2024-12-31'}
        
        is_valid, error = BillValidator.validate_date_range(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_date_range_too_far_past(self):
        """Test date range validation failure with date too far in past."""
        past_date = (datetime.now() - timedelta(days=365*11)).strftime('%Y-%m-%d')
        bill_data = {'due_date': past_date}
        
        is_valid, error = BillValidator.validate_date_range(bill_data)
        assert is_valid is False
        assert "Due date cannot be more than 10 years in the past" in error
    
    def test_validate_date_range_too_far_future(self):
        """Test date range validation failure with date too far in future."""
        future_date = (datetime.now() + timedelta(days=365*11)).strftime('%Y-%m-%d')
        bill_data = {'due_date': future_date}
        
        is_valid, error = BillValidator.validate_date_range(bill_data)
        assert is_valid is False
        assert "Due date cannot be more than 10 years in the future" in error
    
    def test_validate_billing_cycle_success(self):
        """Test successful billing cycle validation."""
        valid_cycles = ['weekly', 'bi-weekly', 'monthly', 'quarterly', 'semi-annually', 'annually', 'one-time']
        
        for cycle in valid_cycles:
            bill_data = {'billing_cycle': cycle}
            is_valid, error = BillValidator.validate_billing_cycle(bill_data)
            assert is_valid is True, f"Billing cycle '{cycle}' should be valid"
            assert error is None
    
    def test_validate_billing_cycle_invalid(self):
        """Test billing cycle validation failure with invalid cycle."""
        bill_data = {'billing_cycle': 'invalid-cycle'}
        
        is_valid, error = BillValidator.validate_billing_cycle(bill_data)
        assert is_valid is False
        assert "Invalid billing cycle" in error
    
    def test_validate_reminder_days_success(self):
        """Test successful reminder days validation."""
        bill_data = {'reminder_days': 7}
        
        is_valid, error = BillValidator.validate_reminder_days(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_reminder_days_invalid(self):
        """Test reminder days validation failure with invalid value."""
        bill_data = {'reminder_days': 100}
        
        is_valid, error = BillValidator.validate_reminder_days(bill_data)
        assert is_valid is False
        assert "Reminder days must be between 0 and 90" in error
    
    def test_validate_reminder_days_negative(self):
        """Test reminder days validation failure with negative value."""
        bill_data = {'reminder_days': -1}
        
        is_valid, error = BillValidator.validate_reminder_days(bill_data)
        assert is_valid is False
        assert "Reminder days must be between 0 and 90" in error
    
    def test_validate_amount_success(self):
        """Test successful amount validation."""
        bill_data = {'amount_str': '150.00'}
        
        is_valid, error = BillValidator.validate_amount(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_amount_invalid_format(self):
        """Test amount validation failure with invalid format."""
        bill_data = {'amount_str': 'not-a-number'}
        
        is_valid, error = BillValidator.validate_amount(bill_data)
        assert is_valid is False
        assert "Invalid amount format" in error
    
    def test_validate_amount_negative(self):
        """Test amount validation failure with negative value."""
        bill_data = {'amount_str': '-150.00'}
        
        is_valid, error = BillValidator.validate_amount(bill_data)
        assert is_valid is False
        assert "Amount cannot be negative" in error
    
    def test_validate_web_page_success(self):
        """Test successful web page validation."""
        bill_data = {'web_page': 'https://example.com'}
        
        is_valid, error = BillValidator.validate_web_page(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_web_page_http(self):
        """Test web page validation with HTTP URL."""
        bill_data = {'web_page': 'http://example.com'}
        
        is_valid, error = BillValidator.validate_web_page(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_web_page_invalid_protocol(self):
        """Test web page validation failure with invalid protocol."""
        bill_data = {'web_page': 'ftp://example.com'}
        
        is_valid, error = BillValidator.validate_web_page(bill_data)
        assert is_valid is False
        assert "Web page must start with http:// or https://" in error
    
    def test_validate_web_page_no_protocol(self):
        """Test web page validation failure with no protocol."""
        bill_data = {'web_page': 'example.com'}
        
        is_valid, error = BillValidator.validate_web_page(bill_data)
        assert is_valid is False
        assert "Web page must start with http:// or https://" in error
    
    def test_validate_email_success(self):
        """Test successful email validation."""
        bill_data = {'company_email': 'test@example.com'}
        
        is_valid, error = BillValidator.validate_email(bill_data, 'company_email')
        assert is_valid is True
        assert error is None
    
    def test_validate_email_invalid_format(self):
        """Test email validation failure with invalid format."""
        bill_data = {'company_email': 'invalid-email'}
        
        is_valid, error = BillValidator.validate_email(bill_data, 'company_email')
        assert is_valid is False
        assert "Invalid email format" in error
    
    def test_validate_email_empty(self):
        """Test email validation with empty value (should be valid)."""
        bill_data = {'company_email': ''}
        
        is_valid, error = BillValidator.validate_email(bill_data, 'company_email')
        assert is_valid is True
        assert error is None
    
    def test_validate_phone_success(self):
        """Test successful phone validation."""
        bill_data = {'support_phone': '555-123-4567'}
        
        is_valid, error = BillValidator.validate_phone(bill_data, 'support_phone')
        assert is_valid is True
        assert error is None
    
    def test_validate_phone_invalid_format(self):
        """Test phone validation failure with invalid format."""
        bill_data = {'support_phone': 'invalid-phone'}
        
        is_valid, error = BillValidator.validate_phone(bill_data, 'support_phone')
        assert is_valid is False
        assert "Invalid phone format" in error
    
    def test_validate_phone_empty(self):
        """Test phone validation with empty value (should be valid)."""
        bill_data = {'support_phone': ''}
        
        is_valid, error = BillValidator.validate_phone(bill_data, 'support_phone')
        assert is_valid is True
        assert error is None
    
    def test_validate_account_number_success(self):
        """Test successful account number validation."""
        bill_data = {'account_number': '123456789'}
        
        is_valid, error = BillValidator.validate_account_number(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_account_number_invalid(self):
        """Test account number validation failure with invalid format."""
        bill_data = {'account_number': 'abc123'}
        
        is_valid, error = BillValidator.validate_account_number(bill_data)
        assert is_valid is False
        assert "Account number must contain only numbers and letters" in error
    
    def test_validate_account_number_empty(self):
        """Test account number validation with empty value (should be valid)."""
        bill_data = {'account_number': ''}
        
        is_valid, error = BillValidator.validate_account_number(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_confirmation_number_success(self):
        """Test successful confirmation number validation."""
        bill_data = {'confirmation_number': 'ABC123456'}
        
        is_valid, error = BillValidator.validate_confirmation_number(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_confirmation_number_invalid(self):
        """Test confirmation number validation failure with invalid format."""
        bill_data = {'confirmation_number': 'ABC<>123'}
        
        is_valid, error = BillValidator.validate_confirmation_number(bill_data)
        assert is_valid is False
        assert "Confirmation number contains invalid characters" in error
    
    def test_validate_confirmation_number_empty(self):
        """Test confirmation number validation with empty value (should be valid)."""
        bill_data = {'confirmation_number': ''}
        
        is_valid, error = BillValidator.validate_confirmation_number(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_bill_data_complete_success(self):
        """Test complete bill data validation with all valid fields."""
        bill_data = {
            'name': 'Test Bill',
            'due_date': '2024-12-31',
            'billing_cycle': 'monthly',
            'reminder_days': 7,
            'amount_str': '150.00',
            'web_page': 'https://example.com',
            'company_email': 'test@example.com',
            'support_phone': '555-123-4567',
            'account_number': '123456789',
            'confirmation_number': 'ABC123',
            'category_id': 1
        }
        
        is_valid, error, cleaned_data = BillValidator.validate_bill_data(bill_data)
        assert is_valid is True
        assert error is None
        assert cleaned_data['name'] == 'Test Bill'
        assert cleaned_data['amount'] == 150.00
        assert cleaned_data['due_date'] == '2024-12-31'
    
    def test_validate_bill_data_multiple_errors(self):
        """Test bill data validation with multiple errors."""
        bill_data = {
            'name': '',  # Empty name
            'due_date': 'invalid-date',  # Invalid date
            'billing_cycle': 'invalid-cycle',  # Invalid cycle
            'amount_str': 'not-a-number'  # Invalid amount
        }
        
        is_valid, error, cleaned_data = BillValidator.validate_bill_data(bill_data)
        assert is_valid is False
        assert "Bill name is required" in error
        assert "Due date must be in YYYY-MM-DD format" in error
        assert "Invalid billing cycle" in error
        assert "Invalid amount format" in error


class TestCategoryValidator:
    """Test CategoryValidator functionality."""
    
    def test_validate_required_fields_success(self):
        """Test successful validation of required fields."""
        category_data = {
            'name': 'Test Category',
            'color': '#ff0000'
        }
        
        is_valid, error = CategoryValidator.validate_required_fields(category_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_required_fields_missing_name(self):
        """Test validation failure when name is missing."""
        category_data = {
            'color': '#ff0000'
        }
        
        is_valid, error = CategoryValidator.validate_required_fields(category_data)
        assert is_valid is False
        assert "Category name is required" in error
    
    def test_validate_required_fields_missing_color(self):
        """Test validation failure when color is missing."""
        category_data = {
            'name': 'Test Category'
        }
        
        is_valid, error = CategoryValidator.validate_required_fields(category_data)
        assert is_valid is False
        assert "Category color is required" in error
    
    def test_validate_name_length_success(self):
        """Test successful name length validation."""
        category_data = {'name': 'Valid Category Name'}
        
        is_valid, error = CategoryValidator.validate_name_length(category_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_name_length_too_short(self):
        """Test name length validation failure when too short."""
        category_data = {'name': ''}
        
        is_valid, error = CategoryValidator.validate_name_length(category_data)
        assert is_valid is False
        assert "Category name must be between 1 and 50 characters" in error
    
    def test_validate_name_length_too_long(self):
        """Test name length validation failure when too long."""
        category_data = {'name': 'A' * 51}
        
        is_valid, error = CategoryValidator.validate_name_length(category_data)
        assert is_valid is False
        assert "Category name must be between 1 and 50 characters" in error
    
    def test_validate_name_characters_success(self):
        """Test successful name character validation."""
        category_data = {'name': 'Valid Category Name 123'}
        
        is_valid, error = CategoryValidator.validate_name_characters(category_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_name_characters_invalid(self):
        """Test name character validation failure with invalid characters."""
        category_data = {'name': 'Invalid<>Category'}
        
        is_valid, error = CategoryValidator.validate_name_characters(category_data)
        assert is_valid is False
        assert "Category name contains invalid characters" in error
    
    def test_validate_color_format_success(self):
        """Test successful color format validation."""
        valid_colors = ['#ff0000', '#00ff00', '#0000ff', '#ffffff', '#000000']
        
        for color in valid_colors:
            category_data = {'color': color}
            is_valid, error = CategoryValidator.validate_color_format(category_data)
            assert is_valid is True, f"Color '{color}' should be valid"
            assert error is None
    
    def test_validate_color_format_invalid(self):
        """Test color format validation failure with invalid format."""
        invalid_colors = ['red', '#ff00', '#ff000', '#ff00000', 'ff0000']
        
        for color in invalid_colors:
            category_data = {'color': color}
            is_valid, error = CategoryValidator.validate_color_format(category_data)
            assert is_valid is False, f"Color '{color}' should be invalid"
            assert "Category color must be in #RRGGBB format" in error
    
    def test_validate_category_data_complete_success(self):
        """Test complete category data validation with all valid fields."""
        category_data = {
            'name': 'Test Category',
            'color': '#ff0000',
            'description': 'Test category description'
        }
        
        is_valid, error, cleaned_data = CategoryValidator.validate_category_data(category_data)
        assert is_valid is True
        assert error is None
        assert cleaned_data['name'] == 'Test Category'
        assert cleaned_data['color'] == '#ff0000'
        assert cleaned_data['description'] == 'Test category description'
    
    def test_validate_category_data_multiple_errors(self):
        """Test category data validation with multiple errors."""
        category_data = {
            'name': '',  # Empty name
            'color': 'invalid-color'  # Invalid color
        }
        
        is_valid, error, cleaned_data = CategoryValidator.validate_category_data(category_data)
        assert is_valid is False
        assert "Category name is required" in error
        assert "Category color must be in #RRGGBB format" in error


class TestDataValidator:
    """Test DataValidator functionality."""
    
    def test_validate_bill_data_delegation(self):
        """Test that DataValidator.validate_bill_data delegates to BillValidator."""
        bill_data = {
            'name': 'Test Bill',
            'due_date': '2024-12-31',
            'category_id': 1
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_bill_data(bill_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_category_data_delegation(self):
        """Test that DataValidator.validate_category_data delegates to CategoryValidator."""
        category_data = {
            'name': 'Test Category',
            'color': '#ff0000'
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_category_data(category_data)
        assert is_valid is True
        assert error is None 