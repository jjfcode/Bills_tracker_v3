import re
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class BillValidator:
    """Comprehensive validator for bill data"""
    
    # Validation patterns
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE_REGEX = r"^[\d\-\+\(\)\s\.]+$"
    URL_REGEX = r"^https?://[^\s/$.?#].[^\s]*$"
    ACCOUNT_NUMBER_REGEX = r"^[a-zA-Z0-9\-_\.\s]+$"
    REFERENCE_ID_REGEX = r"^[a-zA-Z0-9\-_\.\s]+$"
    CONFIRMATION_NUMBER_REGEX = r"^[a-zA-Z0-9\-_\.\s]+$"
    
    # Field constraints
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_WEB_PAGE_LENGTH = 200
    MAX_EMAIL_LENGTH = 100
    MAX_PHONE_LENGTH = 20
    MAX_ACCOUNT_NUMBER_LENGTH = 50
    MAX_REFERENCE_ID_LENGTH = 50
    MAX_CONFIRMATION_NUMBER_LENGTH = 50
    MAX_LOGIN_INFO_LENGTH = 100
    MAX_PASSWORD_LENGTH = 100
    
    # Valid billing cycles
    VALID_BILLING_CYCLES = [
        "weekly", "bi-weekly", "monthly", "quarterly", 
        "semi-annually", "annually", "one-time"
    ]
    
    # Valid reminder days
    VALID_REMINDER_DAYS = [1, 3, 5, 7, 10, 14, 30]
    
    @classmethod
    def validate_required_field(cls, value: str, field_name: str) -> str:
        """Validate that a required field is not empty"""
        if not value or not value.strip():
            raise ValidationError(field_name, f"{field_name} is required and cannot be empty")
        return value.strip()
    
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate bill name"""
        name = cls.validate_required_field(name, "Name")
        
        if len(name) > cls.MAX_NAME_LENGTH:
            raise ValidationError("Name", f"Name cannot exceed {cls.MAX_NAME_LENGTH} characters")
        
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', name):
            raise ValidationError("Name", "Name contains invalid characters")
        
        return name
    
    @classmethod
    def validate_date(cls, date_str: str, field_name: str = "Due Date") -> str:
        """Validate date format and ensure it's a valid date"""
        date_str = cls.validate_required_field(date_str, field_name)
        
        # Check format
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValidationError(field_name, "Date must be in YYYY-MM-DD format")
        
        # Check if it's a valid date
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if date is not too far in the past (more than 10 years)
            min_date = date.today().replace(year=date.today().year - 10)
            if parsed_date < min_date:
                raise ValidationError(field_name, "Date cannot be more than 10 years in the past")
            
            # Check if date is not too far in the future (more than 10 years)
            max_date = date.today().replace(year=date.today().year + 10)
            if parsed_date > max_date:
                raise ValidationError(field_name, "Date cannot be more than 10 years in the future")
                
        except ValueError:
            raise ValidationError(field_name, "Invalid date")
        
        return date_str
    
    @classmethod
    def validate_email(cls, email: str, required: bool = False) -> Optional[str]:
        """Validate email format"""
        if not email or not email.strip():
            if required:
                raise ValidationError("Email", "Email is required")
            return None
        
        email = email.strip()
        
        if len(email) > cls.MAX_EMAIL_LENGTH:
            raise ValidationError("Email", f"Email cannot exceed {cls.MAX_EMAIL_LENGTH} characters")
        
        if not re.match(cls.EMAIL_REGEX, email):
            raise ValidationError("Email", "Invalid email format")
        
        return email
    
    @classmethod
    def validate_phone(cls, phone: str, required: bool = False) -> Optional[str]:
        """Validate phone number format"""
        if not phone or not phone.strip():
            if required:
                raise ValidationError("Phone", "Phone number is required")
            return None
        
        phone = phone.strip()
        
        if len(phone) > cls.MAX_PHONE_LENGTH:
            raise ValidationError("Phone", f"Phone number cannot exceed {cls.MAX_PHONE_LENGTH} characters")
        
        if not re.match(cls.PHONE_REGEX, phone):
            raise ValidationError("Phone", "Phone number contains invalid characters")
        
        # Check if it has at least some digits
        if not re.search(r'\d', phone):
            raise ValidationError("Phone", "Phone number must contain at least one digit")
        
        return phone
    
    @classmethod
    def validate_url(cls, url: str, required: bool = False) -> Optional[str]:
        """Validate web page URL"""
        if not url or not url.strip():
            if required:
                raise ValidationError("Web Page", "Web page URL is required")
            return None
        
        url = url.strip()
        
        if len(url) > cls.MAX_WEB_PAGE_LENGTH:
            raise ValidationError("Web Page", f"URL cannot exceed {cls.MAX_WEB_PAGE_LENGTH} characters")
        
        if not re.match(cls.URL_REGEX, url):
            raise ValidationError("Web Page", "Invalid URL format. Must start with http:// or https://")
        
        return url
    
    @classmethod
    def validate_account_number(cls, account_number: str, required: bool = False) -> Optional[str]:
        """Validate account number format"""
        if not account_number or not account_number.strip():
            if required:
                raise ValidationError("Account Number", "Account number is required")
            return None
        
        account_number = account_number.strip()
        
        if len(account_number) > cls.MAX_ACCOUNT_NUMBER_LENGTH:
            raise ValidationError("Account Number", f"Account number cannot exceed {cls.MAX_ACCOUNT_NUMBER_LENGTH} characters")
        
        if not re.match(cls.ACCOUNT_NUMBER_REGEX, account_number):
            raise ValidationError("Account Number", "Account number contains invalid characters")
        
        return account_number
    
    @classmethod
    def validate_reference_id(cls, reference_id: str, required: bool = False) -> Optional[str]:
        """Validate reference ID format"""
        if not reference_id or not reference_id.strip():
            if required:
                raise ValidationError("Reference ID", "Reference ID is required")
            return None
        
        reference_id = reference_id.strip()
        
        if len(reference_id) > cls.MAX_REFERENCE_ID_LENGTH:
            raise ValidationError("Reference ID", f"Reference ID cannot exceed {cls.MAX_REFERENCE_ID_LENGTH} characters")
        
        if not re.match(cls.REFERENCE_ID_REGEX, reference_id):
            raise ValidationError("Reference ID", "Reference ID contains invalid characters")
        
        return reference_id
    
    @classmethod
    def validate_confirmation_number(cls, confirmation_number: str, required: bool = False) -> Optional[str]:
        """Validate confirmation number format"""
        if not confirmation_number or not confirmation_number.strip():
            if required:
                raise ValidationError("Confirmation Number", "Confirmation number is required")
            return None
        
        confirmation_number = confirmation_number.strip()
        
        if len(confirmation_number) > cls.MAX_CONFIRMATION_NUMBER_LENGTH:
            raise ValidationError("Confirmation Number", f"Confirmation number cannot exceed {cls.MAX_CONFIRMATION_NUMBER_LENGTH} characters")
        
        if not re.match(cls.CONFIRMATION_NUMBER_REGEX, confirmation_number):
            raise ValidationError("Confirmation Number", "Confirmation number contains invalid characters")
        
        return confirmation_number
    
    @classmethod
    def validate_billing_cycle(cls, billing_cycle: str, required: bool = False) -> Optional[str]:
        """Validate billing cycle"""
        if not billing_cycle or not billing_cycle.strip():
            if required:
                raise ValidationError("Billing Cycle", "Billing cycle is required")
            return None
        
        billing_cycle = billing_cycle.strip().lower()
        
        if billing_cycle not in cls.VALID_BILLING_CYCLES:
            raise ValidationError("Billing Cycle", f"Invalid billing cycle. Must be one of: {', '.join(cls.VALID_BILLING_CYCLES)}")
        
        return billing_cycle
    
    @classmethod
    def validate_reminder_days(cls, reminder_days: int, required: bool = False) -> Optional[int]:
        """Validate reminder days"""
        if reminder_days is None:
            if required:
                raise ValidationError("Reminder Days", "Reminder days is required")
            return None
        
        if not isinstance(reminder_days, int):
            try:
                reminder_days = int(reminder_days)
            except (ValueError, TypeError):
                raise ValidationError("Reminder Days", "Reminder days must be a number")
        
        if reminder_days not in cls.VALID_REMINDER_DAYS:
            raise ValidationError("Reminder Days", f"Invalid reminder days. Must be one of: {cls.VALID_REMINDER_DAYS}")
        
        return reminder_days
    
    @classmethod
    def validate_login_info(cls, login_info: str, required: bool = False) -> Optional[str]:
        """Validate login information"""
        if not login_info or not login_info.strip():
            if required:
                raise ValidationError("Login Info", "Login information is required")
            return None
        
        login_info = login_info.strip()
        
        if len(login_info) > cls.MAX_LOGIN_INFO_LENGTH:
            raise ValidationError("Login Info", f"Login information cannot exceed {cls.MAX_LOGIN_INFO_LENGTH} characters")
        
        return login_info
    
    @classmethod
    def validate_password(cls, password: str, required: bool = False) -> Optional[str]:
        """Validate password field"""
        if not password or not password.strip():
            if required:
                raise ValidationError("Password", "Password is required")
            return None
        
        password = password.strip()
        
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            raise ValidationError("Password", f"Password cannot exceed {cls.MAX_PASSWORD_LENGTH} characters")
        
        return password
    
    @classmethod
    def validate_customer_service_hours(cls, hours: str, required: bool = False) -> Optional[str]:
        """Validate customer service hours"""
        if not hours or not hours.strip():
            if required:
                raise ValidationError("Customer Service Hours", "Customer service hours are required")
            return None
        
        hours = hours.strip()
        
        if len(hours) > 100:  # Reasonable limit for hours text
            raise ValidationError("Customer Service Hours", "Customer service hours cannot exceed 100 characters")
        
        return hours
    
    @classmethod
    def validate_mobile_app(cls, mobile_app: str, required: bool = False) -> Optional[str]:
        """Validate mobile app field"""
        if not mobile_app or not mobile_app.strip():
            if required:
                raise ValidationError("Mobile App", "Mobile app information is required")
            return None
        
        mobile_app = mobile_app.strip()
        
        if len(mobile_app) > 100:  # Reasonable limit for app text
            raise ValidationError("Mobile App", "Mobile app information cannot exceed 100 characters")
        
        return mobile_app
    
    @classmethod
    def validate_bill_data(cls, bill_data: Dict) -> Dict[str, any]:
        """Validate complete bill data"""
        errors = []
        validated_data = {}
        
        try:
            # Required fields
            validated_data['name'] = cls.validate_name(bill_data.get('name', ''))
            validated_data['due_date'] = cls.validate_date(bill_data.get('due_date', ''))
            
            # Optional fields with validation
            validated_data['email'] = cls.validate_email(bill_data.get('email', ''))
            validated_data['support_phone'] = cls.validate_phone(bill_data.get('support_phone', ''))
            validated_data['billing_phone'] = cls.validate_phone(bill_data.get('billing_phone', ''))
            validated_data['web_page'] = cls.validate_url(bill_data.get('web_page', ''))
            validated_data['account_number'] = cls.validate_account_number(bill_data.get('account_number', ''))
            validated_data['reference_id'] = cls.validate_reference_id(bill_data.get('reference_id', ''))
            validated_data['confirmation_number'] = cls.validate_confirmation_number(bill_data.get('confirmation_number', ''))
            validated_data['billing_cycle'] = cls.validate_billing_cycle(bill_data.get('billing_cycle', ''))
            validated_data['reminder_days'] = cls.validate_reminder_days(bill_data.get('reminder_days', 7))
            validated_data['login_info'] = cls.validate_login_info(bill_data.get('login_info', ''))
            validated_data['password'] = cls.validate_password(bill_data.get('password', ''))
            validated_data['customer_service_hours'] = cls.validate_customer_service_hours(bill_data.get('customer_service_hours', ''))
            validated_data['mobile_app'] = cls.validate_mobile_app(bill_data.get('mobile_app', ''))
            
            # Boolean fields
            validated_data['paid'] = bool(bill_data.get('paid', False))
            
            # Category and payment method IDs (will be validated by database)
            validated_data['category_id'] = bill_data.get('category_id')
            validated_data['payment_method_id'] = bill_data.get('payment_method_id')
            
        except ValidationError as e:
            errors.append(str(e))
        
        if errors:
            raise ValidationError("Validation", "\n".join(errors))
        
        return validated_data

class CategoryValidator:
    """Validator for category data"""
    
    MAX_NAME_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 200
    
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate category name"""
        name = BillValidator.validate_required_field(name, "Name")
        
        if len(name) > cls.MAX_NAME_LENGTH:
            raise ValidationError("Name", f"Category name cannot exceed {cls.MAX_NAME_LENGTH} characters")
        
        # Check for invalid characters
        if re.search(r'[<>:"/\\|?*]', name):
            raise ValidationError("Name", "Category name contains invalid characters")
        
        return name
    
    @classmethod
    def validate_color(cls, color: str) -> str:
        """Validate hex color format"""
        color = BillValidator.validate_required_field(color, "Color")
        
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValidationError("Color", "Color must be in #RRGGBB format (e.g., #ff0000)")
        
        return color.upper()
    
    @classmethod
    def validate_description(cls, description: str, required: bool = False) -> Optional[str]:
        """Validate category description"""
        if not description or not description.strip():
            if required:
                raise ValidationError("Description", "Description is required")
            return None
        
        description = description.strip()
        
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValidationError("Description", f"Description cannot exceed {cls.MAX_DESCRIPTION_LENGTH} characters")
        
        return description
    
    @classmethod
    def validate_category_data(cls, category_data: Dict) -> Dict[str, any]:
        """Validate complete category data"""
        errors = []
        validated_data = {}
        
        try:
            validated_data['name'] = cls.validate_name(category_data.get('name', ''))
            validated_data['color'] = cls.validate_color(category_data.get('color', ''))
            validated_data['description'] = cls.validate_description(category_data.get('description', ''))
            
        except ValidationError as e:
            errors.append(str(e))
        
        if errors:
            raise ValidationError("Validation", "\n".join(errors))
        
        return validated_data

def validate_field_in_real_time(value: str, field_type: str, required: bool = False) -> Tuple[bool, str]:
    """
    Validate a field in real-time and return (is_valid, error_message)
    
    Args:
        value: The field value to validate
        field_type: Type of field ('name', 'email', 'phone', 'url', 'account_number', etc.)
        required: Whether the field is required
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if field_type == 'name':
            BillValidator.validate_name(value)
        elif field_type == 'email':
            BillValidator.validate_email(value, required)
        elif field_type == 'phone':
            BillValidator.validate_phone(value, required)
        elif field_type == 'url':
            BillValidator.validate_url(value, required)
        elif field_type == 'account_number':
            BillValidator.validate_account_number(value, required)
        elif field_type == 'reference_id':
            BillValidator.validate_reference_id(value, required)
        elif field_type == 'confirmation_number':
            BillValidator.validate_confirmation_number(value, required)
        elif field_type == 'date':
            BillValidator.validate_date(value)
        elif field_type == 'billing_cycle':
            BillValidator.validate_billing_cycle(value, required)
        elif field_type == 'reminder_days':
            try:
                BillValidator.validate_reminder_days(int(value), required)
            except ValueError:
                if required:
                    return False, "Reminder days must be a number"
        elif field_type == 'category_name':
            CategoryValidator.validate_name(value)
        elif field_type == 'color':
            CategoryValidator.validate_color(value)
        else:
            # For unknown field types, just check if required
            if required and (not value or not value.strip()):
                return False, f"{field_type.title()} is required"
        
        return True, ""
        
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}" 