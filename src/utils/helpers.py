"""
Helper functions for Bills Tracker application.
"""

import re
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from .constants import DATE_FORMAT, EMAIL_REGEX, PHONE_REGEX


def parse_amount(amount_str: str) -> Optional[float]:
    """
    Parse amount string to float, handling various formats.
    
    Args:
        amount_str: Amount string to parse
        
    Returns:
        Parsed float value or None if invalid
    """
    if not amount_str or not amount_str.strip():
        return None
    
    # Remove currency symbols and extra whitespace
    cleaned = re.sub(r'[^\d.,-]', '', amount_str.strip())
    
    if not cleaned:
        return None
    
    try:
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Format like "1,234.56" or "1.234,56"
            if cleaned.rfind('.') > cleaned.rfind(','):
                # "1,234.56" format
                cleaned = cleaned.replace(',', '')
            else:
                # "1.234,56" format
                cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Check if comma is decimal separator
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                cleaned = cleaned.replace(',', '.')
            else:
                # Likely thousands separator
                cleaned = cleaned.replace(',', '')
        
        return float(cleaned)
    except ValueError:
        return None


def format_amount(amount: Optional[float]) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return ""
    return f"${amount:.2f}"


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date range.
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start = datetime.strptime(start_date, DATE_FORMAT)
        end = datetime.strptime(end_date, DATE_FORMAT)
        
        if start > end:
            return False, "Start date cannot be after end date"
        
        return True, None
    except ValueError:
        return False, f"Invalid date format. Please use {DATE_FORMAT}"


def get_date_period_dates(period: str) -> Tuple[str, str]:
    """
    Get start and end dates for a given period.
    
    Args:
        period: Period string (today, week, month, quarter, year)
        
    Returns:
        Tuple of (start_date, end_date) strings
    """
    today = datetime.now()
    
    if period == "today":
        start_date = today
        end_date = today
    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == "month":
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    elif period == "quarter":
        quarter_start_month = ((today.month - 1) // 3) * 3 + 1
        start_date = today.replace(month=quarter_start_month, day=1)
        if quarter_start_month == 10:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=quarter_start_month + 3, day=1) - timedelta(days=1)
    elif period == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    else:
        # Default to current month
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    return start_date.strftime(DATE_FORMAT), end_date.strftime(DATE_FORMAT)


def calculate_next_due_date(current_due_date: str, billing_cycle: str) -> str:
    """
    Calculate next due date based on billing cycle.
    
    Args:
        current_due_date: Current due date string
        billing_cycle: Billing cycle string
        
    Returns:
        Next due date string
    """
    try:
        current_date = datetime.strptime(current_due_date, DATE_FORMAT)
    except ValueError:
        return current_due_date
    
    if billing_cycle == "weekly":
        next_date = current_date + timedelta(days=7)
    elif billing_cycle == "bi-weekly":
        next_date = current_date + timedelta(days=14)
    elif billing_cycle == "monthly":
        # Add one month, handling year rollover
        if current_date.month == 12:
            next_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_date = current_date.replace(month=current_date.month + 1)
    elif billing_cycle == "quarterly":
        # Add three months
        new_month = current_date.month + 3
        new_year = current_date.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        next_date = current_date.replace(year=new_year, month=new_month)
    elif billing_cycle == "semi-annually":
        # Add six months
        new_month = current_date.month + 6
        new_year = current_date.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        next_date = current_date.replace(year=new_year, month=new_month)
    elif billing_cycle == "annually":
        next_date = current_date.replace(year=current_date.year + 1)
    else:  # one-time
        return current_due_date
    
    return next_date.strftime(DATE_FORMAT)


def export_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str] = None) -> bool:
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        filename: Output filename
        fieldnames: List of field names to include
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not data:
            return False
        
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return True
    except Exception:
        return False


def import_from_csv(filename: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Import data from CSV file.
    
    Args:
        filename: Input filename
        
    Returns:
        Tuple of (data_list, error_messages)
    """
    data = []
    errors = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                try:
                    # Convert empty strings to None for optional fields
                    cleaned_row = {}
                    for key, value in row.items():
                        cleaned_row[key] = value.strip() if value and value.strip() else None
                    
                    data.append(cleaned_row)
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
    
    except Exception as e:
        errors.append(f"File error: {str(e)}")
    
    return data, errors


def is_dark_mode() -> bool:
    """
    Check if system is in dark mode.
    
    Returns:
        True if dark mode is detected
    """
    try:
        import customtkinter as ctk
        return ctk.get_appearance_mode() == "dark"
    except:
        return False


def get_urgency_color(due_date: str, reminder_days: int = 7) -> str:
    """
    Get color based on bill urgency.
    
    Args:
        due_date: Due date string
        reminder_days: Number of days before due to show as urgent
        
    Returns:
        Color string for urgency level
    """
    try:
        from .constants import URGENT_COLOR, WARNING_COLOR, SUCCESS_COLOR
        
        due = datetime.strptime(due_date, DATE_FORMAT)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        due = due.replace(hour=0, minute=0, second=0, microsecond=0)
        
        days_until_due = (due - today).days
        
        if days_until_due < 0:
            return URGENT_COLOR  # Overdue
        elif days_until_due <= reminder_days:
            return WARNING_COLOR  # Urgent
        else:
            return SUCCESS_COLOR  # Not urgent
    except:
        return SUCCESS_COLOR 