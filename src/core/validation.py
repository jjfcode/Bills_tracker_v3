#!/usr/bin/env python3
"""
Comprehensive validation module for Bills Tracker application.
Provides enhanced validation for all data types with detailed error messages.
"""

import re
import urllib.parse
from datetime import datetime, timedelta
from typing import Tuple, Optional, Union, Dict, Any

# Constants
DATE_FORMAT = '%Y-%m-%d'
MAX_BILL_NAME_LENGTH = 100
MAX_LOGIN_INFO_LENGTH = 200
MAX_PASSWORD_LENGTH = 100
MAX_PHONE_LENGTH = 20
MAX_ACCOUNT_NUMBER_LENGTH = 50
MAX_REFERENCE_ID_LENGTH = 50
MAX_SERVICE_HOURS_LENGTH = 100
MAX_MOBILE_APP_LENGTH = 200

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class DataValidator:
    """Comprehensive data validator for Bills Tracker."""
    
    @staticmethod
    def validate_bill_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate bill name.
        
        Args:
            name: Bill name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Bill name is required"
        
        name = name.strip()
        
        if len(name) > MAX_BILL_NAME_LENGTH:
            return False, f"Bill name must be {MAX_BILL_NAME_LENGTH} characters or less"
        
        # Check for invalid characters
        invalid_chars = re.findall(r'[<>:"/\\|?*]', name)
        if invalid_chars:
            return False, f"Bill name contains invalid characters: {', '.join(set(invalid_chars))}"
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', name):
            return False, "Bill name contains excessive whitespace"
        
        return True, None
    
    @staticmethod
    def validate_due_date(date_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate due date format and range.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str or not date_str.strip():
            return False, "Due date is required"
        
        try:
            date_obj = datetime.strptime(date_str.strip(), DATE_FORMAT)
        except ValueError:
            return False, f"Invalid date format. Please use {DATE_FORMAT} (YYYY-MM-DD)"
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date_obj = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if date is too far in the past (more than 1 year)
        one_year_ago = today - timedelta(days=365)
        if date_obj < one_year_ago:
            return False, "Due date cannot be more than 1 year in the past"
        
        # Check if date is too far in the future (more than 10 years)
        ten_years_future = today + timedelta(days=10*365)
        if date_obj > ten_years_future:
            return False, "Due date cannot be more than 10 years in the future"
        
        return True, None
    
    @staticmethod
    def validate_billing_cycle(cycle: str) -> Tuple[bool, Optional[str]]:
        """
        Validate billing cycle.
        
        Args:
            cycle: Billing cycle to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_cycles = [
            "weekly", "bi-weekly", "monthly", "quarterly", 
            "semi-annually", "annually", "one-time"
        ]
        
        if not cycle or not cycle.strip():
            return False, "Billing cycle is required"
        
        cycle = cycle.strip()
        
        if cycle.lower() not in valid_cycles:
            return False, f"Invalid billing cycle. Must be one of: {', '.join(valid_cycles)}"
        
        return True, None
    
    @staticmethod
    def validate_reminder_days(days: Union[str, int]) -> Tuple[bool, Optional[str]]:
        """
        Validate reminder days.
        
        Args:
            days: Reminder days to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if isinstance(days, str):
                days = int(days.strip())
        except (ValueError, AttributeError):
            return False, "Reminder days must be a number"
        
        if not isinstance(days, int):
            return False, "Reminder days must be a whole number"
        
        if days <= 0:
            return False, "Reminder days must be greater than 0"
        
        if days > 365:
            return False, "Reminder days cannot exceed 365 days"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate URL format and return cleaned URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_url)
        """
        if not url or not url.strip():
            return True, None, ""  # Empty URLs are allowed
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check if domain is valid
            if not parsed.netloc:
                return False, "Invalid URL: missing domain", None
            
            # Basic domain validation
            domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            if not re.match(domain_pattern, parsed.netloc.split(':')[0]):
                return False, "Invalid URL: invalid domain format", None
            
            # Check for common TLDs
            tld_pattern = r'\.[a-zA-Z]{2,}$'
            if not re.search(tld_pattern, parsed.netloc):
                return False, "Invalid URL: missing or invalid top-level domain", None
            
            return True, None, url
            
        except Exception:
            return False, "Invalid URL format", None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not email.strip():
            return True, None  # Empty emails are allowed
        
        email = email.strip().lower()
        
        # Comprehensive email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format. Please use format: user@domain.com"
        
        # Additional checks
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email address is too long (maximum 254 characters)"
        
        if email.count('@') != 1:
            return False, "Email address must contain exactly one @ symbol"
        
        local_part, domain = email.split('@')
        
        if len(local_part) > 64:  # RFC 5321 limit
            return False, "Email local part is too long (maximum 64 characters)"
        
        if len(domain) > 253:  # RFC 5321 limit
            return False, "Email domain is too long (maximum 253 characters)"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone or not phone.strip():
            return True, None  # Empty phone numbers are allowed
        
        phone = phone.strip()
        
        if len(phone) > MAX_PHONE_LENGTH:
            return False, f"Phone number is too long (maximum {MAX_PHONE_LENGTH} characters)"
        
        # Remove common formatting characters
        cleaned_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it contains only digits and optional + at start
        if not re.match(r'^\+?[\d]+$', cleaned_phone):
            return False, "Phone number contains invalid characters"
        
        # Check minimum length (at least 7 digits for international numbers)
        if len(cleaned_phone) < 7:
            return False, "Phone number is too short (minimum 7 digits)"
        
        # Check maximum length (15 digits for international numbers)
        if len(cleaned_phone) > 15:
            return False, "Phone number is too long (maximum 15 digits)"
        
        return True, None
    
    @staticmethod
    def validate_login_info(login_info: str) -> Tuple[bool, Optional[str]]:
        """
        Validate login information.
        
        Args:
            login_info: Login information to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not login_info or not login_info.strip():
            return True, None  # Empty login info is allowed
        
        login_info = login_info.strip()
        
        if len(login_info) > MAX_LOGIN_INFO_LENGTH:
            return False, f"Login information is too long (maximum {MAX_LOGIN_INFO_LENGTH} characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = re.findall(r'[<>"\']', login_info)
        if dangerous_chars:
            return False, f"Login information contains invalid characters: {', '.join(set(dangerous_chars))}"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password (for display purposes, not security).
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password or not password.strip():
            return True, None  # Empty passwords are allowed
        
        password = password.strip()
        
        if len(password) > MAX_PASSWORD_LENGTH:
            return False, f"Password is too long (maximum {MAX_PASSWORD_LENGTH} characters)"
        
        return True, None
    
    @staticmethod
    def validate_account_number(account_number: str) -> Tuple[bool, Optional[str]]:
        """
        Validate account number.
        
        Args:
            account_number: Account number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not account_number or not account_number.strip():
            return True, None  # Empty account numbers are allowed
        
        account_number = account_number.strip()
        
        if len(account_number) > MAX_ACCOUNT_NUMBER_LENGTH:
            return False, f"Account number is too long (maximum {MAX_ACCOUNT_NUMBER_LENGTH} characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = re.findall(r'[<>"\']', account_number)
        if dangerous_chars:
            return False, f"Account number contains invalid characters: {', '.join(set(dangerous_chars))}"
        
        return True, None
    
    @staticmethod
    def validate_reference_id(reference_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate reference ID.
        
        Args:
            reference_id: Reference ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not reference_id or not reference_id.strip():
            return True, None  # Empty reference IDs are allowed
        
        reference_id = reference_id.strip()
        
        if len(reference_id) > MAX_REFERENCE_ID_LENGTH:
            return False, f"Reference ID is too long (maximum {MAX_REFERENCE_ID_LENGTH} characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = re.findall(r'[<>"\']', reference_id)
        if dangerous_chars:
            return False, f"Reference ID contains invalid characters: {', '.join(set(dangerous_chars))}"
        
        return True, None
    
    @staticmethod
    def validate_service_hours(service_hours: str) -> Tuple[bool, Optional[str]]:
        """
        Validate service hours.
        
        Args:
            service_hours: Service hours to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not service_hours or not service_hours.strip():
            return True, None  # Empty service hours are allowed
        
        service_hours = service_hours.strip()
        
        if len(service_hours) > MAX_SERVICE_HOURS_LENGTH:
            return False, f"Service hours are too long (maximum {MAX_SERVICE_HOURS_LENGTH} characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = re.findall(r'[<>"\']', service_hours)
        if dangerous_chars:
            return False, f"Service hours contain invalid characters: {', '.join(set(dangerous_chars))}"
        
        return True, None
    
    @staticmethod
    def validate_mobile_app(mobile_app: str) -> Tuple[bool, Optional[str]]:
        """
        Validate mobile app information.
        
        Args:
            mobile_app: Mobile app information to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not mobile_app or not mobile_app.strip():
            return True, None  # Empty mobile app info is allowed
        
        mobile_app = mobile_app.strip()
        
        if len(mobile_app) > MAX_MOBILE_APP_LENGTH:
            return False, f"Mobile app information is too long (maximum {MAX_MOBILE_APP_LENGTH} characters)"
        
        # Check for potentially dangerous characters
        dangerous_chars = re.findall(r'[<>"\']', mobile_app)
        if dangerous_chars:
            return False, f"Mobile app information contains invalid characters: {', '.join(set(dangerous_chars))}"
        
        return True, None
    
    @staticmethod
    def validate_bill_data(bill_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate complete bill data.
        
        Args:
            bill_data: Bill data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        cleaned_data = {}
        errors = []
        
        # Validate required fields
        name_valid, name_error = DataValidator.validate_bill_name(bill_data.get('name', ''))
        if not name_valid:
            errors.append(f"Name: {name_error}")
        else:
            cleaned_data['name'] = bill_data.get('name', '').strip()
        
        due_date_valid, due_date_error = DataValidator.validate_due_date(bill_data.get('due_date', ''))
        if not due_date_valid:
            errors.append(f"Due Date: {due_date_error}")
        else:
            cleaned_data['due_date'] = bill_data.get('due_date', '').strip()
        
        # Validate optional fields
        billing_cycle = bill_data.get('billing_cycle', 'monthly')
        cycle_valid, cycle_error = DataValidator.validate_billing_cycle(billing_cycle)
        if not cycle_valid:
            errors.append(f"Billing Cycle: {cycle_error}")
        else:
            cleaned_data['billing_cycle'] = billing_cycle
        
        reminder_days = bill_data.get('reminder_days', 7)
        reminder_valid, reminder_error = DataValidator.validate_reminder_days(reminder_days)
        if not reminder_valid:
            errors.append(f"Reminder Days: {reminder_error}")
        else:
            cleaned_data['reminder_days'] = int(reminder_days)
        
        # Validate URL
        url_valid, url_error, cleaned_url = DataValidator.validate_url(bill_data.get('web_page', ''))
        if not url_valid:
            errors.append(f"Website: {url_error}")
        else:
            cleaned_data['web_page'] = cleaned_url
        
        # Validate other fields
        for field, validator in [
            ('login_info', DataValidator.validate_login_info),
            ('password', DataValidator.validate_password),
            ('company_email', DataValidator.validate_email),
            ('support_phone', DataValidator.validate_phone),
            ('billing_phone', DataValidator.validate_phone),
            ('customer_service_hours', DataValidator.validate_service_hours),
            ('account_number', DataValidator.validate_account_number),
            ('reference_id', DataValidator.validate_reference_id),
            ('mobile_app', DataValidator.validate_mobile_app)
        ]:
            value = bill_data.get(field, '')
            is_valid, error_msg = validator(value)
            if not is_valid:
                errors.append(f"{field.replace('_', ' ').title()}: {error_msg}")
            else:
                cleaned_data[field] = value.strip() if isinstance(value, str) else value
        
        # Validate support chat URL
        chat_url_valid, chat_url_error, cleaned_chat_url = DataValidator.validate_url(bill_data.get('support_chat_url', ''))
        if not chat_url_valid:
            errors.append(f"Support Chat URL: {chat_url_error}")
        else:
            cleaned_data['support_chat_url'] = cleaned_chat_url
        
        # Add paid status
        cleaned_data['paid'] = bool(bill_data.get('paid', False))
        
        if errors:
            return False, "; ".join(errors), cleaned_data
        
        return True, None, cleaned_data
    
    @staticmethod
    def validate_template_data(template_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate complete template data.
        
        Args:
            template_data: Template data dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        cleaned_data = {}
        errors = []
        
        # Validate required fields (templates don't need due_date)
        name_valid, name_error = DataValidator.validate_bill_name(template_data.get('name', ''))
        if not name_valid:
            errors.append(f"Name: {name_error}")
        else:
            cleaned_data['name'] = template_data.get('name', '').strip()
        
        # Validate optional fields
        billing_cycle = template_data.get('billing_cycle', 'monthly')
        cycle_valid, cycle_error = DataValidator.validate_billing_cycle(billing_cycle)
        if not cycle_valid:
            errors.append(f"Billing Cycle: {cycle_error}")
        else:
            cleaned_data['billing_cycle'] = billing_cycle
        
        reminder_days = template_data.get('reminder_days', 7)
        reminder_valid, reminder_error = DataValidator.validate_reminder_days(reminder_days)
        if not reminder_valid:
            errors.append(f"Reminder Days: {reminder_error}")
        else:
            cleaned_data['reminder_days'] = int(reminder_days)
        
        # Validate URL
        url_valid, url_error, cleaned_url = DataValidator.validate_url(template_data.get('web_page', ''))
        if not url_valid:
            errors.append(f"Website: {url_error}")
        else:
            cleaned_data['web_page'] = cleaned_url
        
        # Validate other fields
        for field, validator in [
            ('login_info', DataValidator.validate_login_info),
            ('password', DataValidator.validate_password),
            ('company_email', DataValidator.validate_email),
            ('support_phone', DataValidator.validate_phone),
            ('billing_phone', DataValidator.validate_phone),
            ('customer_service_hours', DataValidator.validate_service_hours),
            ('account_number', DataValidator.validate_account_number),
            ('reference_id', DataValidator.validate_reference_id),
            ('mobile_app', DataValidator.validate_mobile_app)
        ]:
            value = template_data.get(field, '')
            is_valid, error_msg = validator(value)
            if not is_valid:
                errors.append(f"{field.replace('_', ' ').title()}: {error_msg}")
            else:
                cleaned_data[field] = value.strip() if isinstance(value, str) else value
        
        # Validate support chat URL
        chat_url_valid, chat_url_error, cleaned_chat_url = DataValidator.validate_url(template_data.get('support_chat_url', ''))
        if not chat_url_valid:
            errors.append(f"Support Chat URL: {chat_url_error}")
        else:
            cleaned_data['support_chat_url'] = cleaned_chat_url
        
        if errors:
            return False, "; ".join(errors), cleaned_data
        
        return True, None, cleaned_data

# Convenience functions for backward compatibility
def validate_url(url: str) -> Optional[str]:
    """Legacy URL validation function."""
    is_valid, error_msg, cleaned_url = DataValidator.validate_url(url)
    return cleaned_url if is_valid else None

def validate_email(email: str) -> Optional[str]:
    """Legacy email validation function."""
    is_valid, error_msg = DataValidator.validate_email(email)
    return email.strip().lower() if is_valid else None

def validate_future_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """Legacy future date validation function."""
    return DataValidator.validate_due_date(date_str)

def validate_reminder_days(days_str: str) -> bool:
    """Legacy reminder days validation function."""
    is_valid, error_msg = DataValidator.validate_reminder_days(days_str)
    return is_valid 