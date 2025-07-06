"""
Business logic services for Bills Tracker application.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from .db import (
    fetch_all_bills, insert_bill, update_bill, delete_bill,
    fetch_all_categories, insert_category, update_category, delete_category,
    fetch_all_payment_methods
)
from .validation import DataValidator
from ..utils.helpers import (
    parse_amount, format_amount, calculate_next_due_date,
    get_date_period_dates, get_urgency_color
)
from ..utils.constants import DATE_FORMAT


class BillService:
    """
    Service for bill-related business logic.

    Provides methods for retrieving, searching, creating, updating, deleting, and renewing bills.
    All methods are static and operate on the database via the data access layer.
    """
    
    @staticmethod
    def get_all_bills() -> List[Dict[str, Any]]:
        """
        Retrieve all bills from the database, adding computed fields for UI display.

        Returns:
            List[Dict[str, Any]]: List of bills with urgency color, formatted amount, and status flags.
        """
        bills = fetch_all_bills()
        
        # Add computed fields
        for bill in bills:
            bill['urgency_color'] = get_urgency_color(
                bill['due_date'], 
                bill.get('reminder_days', 7)
            )
            bill['formatted_amount'] = format_amount(bill.get('amount'))
            bill['is_overdue'] = BillService._is_bill_overdue(bill['due_date'])
            bill['is_urgent'] = BillService._is_bill_urgent(bill['due_date'], bill.get('reminder_days', 7))
        
        return bills
    
    @staticmethod
    def get_bills_by_period(period: str) -> List[Dict[str, Any]]:
        """
        Retrieve bills filtered by a time period (e.g., 'month', 'year').

        Args:
            period (str): The period to filter by (today, week, month, quarter, year).
        Returns:
            List[Dict[str, Any]]: Filtered list of bills.
        """
        start_date, end_date = get_date_period_dates(period)
        all_bills = BillService.get_all_bills()
        
        filtered_bills = []
        for bill in all_bills:
            try:
                due_date = datetime.strptime(bill['due_date'], DATE_FORMAT)
                start = datetime.strptime(start_date, DATE_FORMAT)
                end = datetime.strptime(end_date, DATE_FORMAT)
                
                if start <= due_date <= end:
                    filtered_bills.append(bill)
            except ValueError:
                continue
        
        return filtered_bills
    
    @staticmethod
    def get_bills_by_category(category_id: Optional[int]) -> List[Dict[str, Any]]:
        """
        Retrieve bills filtered by category.

        Args:
            category_id (Optional[int]): The category ID to filter by, or None for all.
        Returns:
            List[Dict[str, Any]]: Filtered list of bills.
        """
        all_bills = BillService.get_all_bills()
        
        if category_id is None:
            return all_bills
        
        return [bill for bill in all_bills if bill.get('category_id') == category_id]
    
    @staticmethod
    def search_bills(query: str, search_field: str = "name") -> List[Dict[str, Any]]:
        """
        Search bills by a query string and field.

        Args:
            query (str): The search query.
            search_field (str): The field to search in (default: 'name').
        Returns:
            List[Dict[str, Any]]: Filtered list of bills matching the query.
        """
        if not query.strip():
            return BillService.get_all_bills()
        
        all_bills = BillService.get_all_bills()
        query_lower = query.lower().strip()
        
        filtered_bills = []
        for bill in all_bills:
            field_value = str(bill.get(search_field, "")).lower()
            if query_lower in field_value:
                filtered_bills.append(bill)
        
        return filtered_bills
    
    @staticmethod
    def create_bill(bill_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Create a new bill after validating the input data.

        Args:
            bill_data (Dict[str, Any]): The bill data to create.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        # Validate bill data
        is_valid, error_msg, cleaned_data = DataValidator.validate_bill_data(bill_data)
        if not is_valid:
            return False, error_msg
        
        # Parse amount
        if cleaned_data.get('amount_str'):
            amount = parse_amount(cleaned_data['amount_str'])
            cleaned_data['amount'] = amount
            del cleaned_data['amount_str']
        
        try:
            insert_bill(cleaned_data)
            return True, None
        except Exception as e:
            return False, f"Failed to create bill: {str(e)}"
    
    @staticmethod
    def update_bill(bill_id: int, bill_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Update an existing bill after validating the input data.

        Args:
            bill_id (int): The ID of the bill to update.
            bill_data (Dict[str, Any]): The updated bill data.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        # Validate bill data
        is_valid, error_msg, cleaned_data = DataValidator.validate_bill_data(bill_data)
        if not is_valid:
            return False, error_msg
        
        # Parse amount
        if cleaned_data.get('amount_str'):
            amount = parse_amount(cleaned_data['amount_str'])
            cleaned_data['amount'] = amount
            del cleaned_data['amount_str']
        
        try:
            update_bill(bill_id, cleaned_data)
            return True, None
        except Exception as e:
            return False, f"Failed to update bill: {str(e)}"
    
    @staticmethod
    def delete_bill(bill_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a bill by its ID.

        Args:
            bill_id (int): The ID of the bill to delete.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        try:
            delete_bill(bill_id)
            return True, None
        except Exception as e:
            return False, f"Failed to delete bill: {str(e)}"
    
    @staticmethod
    def bulk_delete_bills(bill_ids: List[int]) -> Tuple[bool, Optional[str]]:
        """
        Delete multiple bills by their IDs.

        Args:
            bill_ids (List[int]): List of bill IDs to delete.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        success_count = 0
        failed_ids = []
        
        for bill_id in bill_ids:
            success, error = BillService.delete_bill(bill_id)
            if success:
                success_count += 1
            else:
                failed_ids.append(bill_id)
        
        if failed_ids:
            return False, f"Failed to delete bills: {failed_ids}"
        
        return True, f"Successfully deleted {success_count} bills"
    
    @staticmethod
    def toggle_paid_status(bill_id: int, current_paid: bool) -> Tuple[bool, Optional[str]]:
        """
        Toggle the paid status of a bill.

        Args:
            bill_id (int): The ID of the bill.
            current_paid (bool): The current paid status.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        try:
            update_bill(bill_id, {'paid': not current_paid})
            return True, None
        except Exception as e:
            return False, f"Failed to update paid status: {str(e)}"
    
    @staticmethod
    def renew_bill(bill_id: int) -> Tuple[bool, Optional[str]]:
        """
        Renew a bill by calculating and setting the next due date.

        Args:
            bill_id (int): The ID of the bill to renew.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        try:
            # Get current bill data
            all_bills = fetch_all_bills()
            bill = next((b for b in all_bills if b['id'] == bill_id), None)
            
            if not bill:
                return False, "Bill not found"
            
            if not bill.get('billing_cycle') or bill['billing_cycle'] == 'one-time':
                return False, "Cannot renew one-time bills"
            
            # Calculate next due date
            next_due_date = calculate_next_due_date(bill['due_date'], bill['billing_cycle'])
            
            # Update bill with new due date and reset paid status
            update_bill(bill_id, {
                'due_date': next_due_date,
                'paid': False
            })
            
            return True, None
        except Exception as e:
            return False, f"Failed to renew bill: {str(e)}"
    
    @staticmethod
    def _is_bill_overdue(due_date: str) -> bool:
        """
        Check if a bill is overdue based on its due date.

        Args:
            due_date (str): The due date string (YYYY-MM-DD).
        Returns:
            bool: True if overdue, False otherwise.
        """
        try:
            due = datetime.strptime(due_date, DATE_FORMAT)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return due < today
        except ValueError:
            return False
    
    @staticmethod
    def _is_bill_urgent(due_date: str, reminder_days: int) -> bool:
        """
        Check if a bill is urgent (due within reminder days).

        Args:
            due_date (str): The due date string (YYYY-MM-DD).
            reminder_days (int): Number of days before due to consider urgent.
        Returns:
            bool: True if urgent, False otherwise.
        """
        try:
            due = datetime.strptime(due_date, DATE_FORMAT)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            days_until_due = (due - today).days
            return 0 <= days_until_due <= reminder_days
        except ValueError:
            return False


class CategoryService:
    """
    Service for category-related business logic.

    Provides methods for retrieving, creating, updating, and deleting categories.
    """
    
    @staticmethod
    def get_all_categories() -> List[Dict[str, Any]]:
        """
        Retrieve all categories from the database.

        Returns:
            List[Dict[str, Any]]: List of categories.
        """
        return fetch_all_categories()
    
    @staticmethod
    def create_category(category_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Create a new category after validating the input data.

        Args:
            category_data (Dict[str, Any]): The category data to create.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        # Validate category data
        is_valid, error_msg, cleaned_data = DataValidator.validate_category_data(category_data)
        if not is_valid:
            return False, error_msg
        
        try:
            insert_category(cleaned_data)
            return True, None
        except Exception as e:
            return False, f"Failed to create category: {str(e)}"
    
    @staticmethod
    def update_category(category_id: int, category_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Update an existing category after validating the input data.

        Args:
            category_id (int): The ID of the category to update.
            category_data (Dict[str, Any]): The updated category data.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        # Validate category data
        is_valid, error_msg, cleaned_data = DataValidator.validate_category_data(category_data)
        if not is_valid:
            return False, error_msg
        
        try:
            update_category(category_id, cleaned_data)
            return True, None
        except Exception as e:
            return False, f"Failed to update category: {str(e)}"
    
    @staticmethod
    def delete_category(category_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a category by its ID.

        Args:
            category_id (int): The ID of the category to delete.
        Returns:
            Tuple[bool, Optional[str]]: (success, error message if any)
        """
        try:
            delete_category(category_id)
            return True, None
        except Exception as e:
            return False, f"Failed to delete category: {str(e)}"


class PaymentMethodService:
    """
    Service for payment method-related business logic.

    Provides methods for retrieving payment methods.
    """
    
    @staticmethod
    def get_all_payment_methods() -> List[Dict[str, Any]]:
        """
        Retrieve all payment methods from the database.

        Returns:
            List[Dict[str, Any]]: List of payment methods.
        """
        return fetch_all_payment_methods()


class AnalyticsService:
    """
    Service for analytics and reporting.

    Provides methods for generating bill statistics and monthly summaries.
    """
    
    @staticmethod
    def get_bill_statistics() -> Dict[str, Any]:
        """
        Get comprehensive statistics about bills, including totals, paid/unpaid counts, overdue/urgent counts, and category breakdowns.

        Returns:
            Dict[str, Any]: Dictionary of statistics.
        """
        bills = BillService.get_all_bills()
        
        total_bills = len(bills)
        paid_bills = len([b for b in bills if b.get('paid', False)])
        unpaid_bills = total_bills - paid_bills
        overdue_bills = len([b for b in bills if b.get('is_overdue', False)])
        urgent_bills = len([b for b in bills if b.get('is_urgent', False)])
        
        # Calculate total amounts
        total_amount = sum(b.get('amount', 0) or 0 for b in bills)
        paid_amount = sum(b.get('amount', 0) or 0 for b in bills if b.get('paid', False))
        unpaid_amount = total_amount - paid_amount
        
        # Category breakdown
        category_stats = {}
        for bill in bills:
            category_name = bill.get('category_name', 'Uncategorized')
            if category_name not in category_stats:
                category_stats[category_name] = {
                    'count': 0,
                    'total_amount': 0,
                    'paid_amount': 0
                }
            
            category_stats[category_name]['count'] += 1
            amount = bill.get('amount', 0) or 0
            category_stats[category_name]['total_amount'] += amount
            if bill.get('paid', False):
                category_stats[category_name]['paid_amount'] += amount
        
        return {
            'total_bills': total_bills,
            'paid_bills': paid_bills,
            'unpaid_bills': unpaid_bills,
            'overdue_bills': overdue_bills,
            'urgent_bills': urgent_bills,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'unpaid_amount': unpaid_amount,
            'category_stats': category_stats
        }
    
    @staticmethod
    def get_monthly_summary(year: int, month: int) -> Dict[str, Any]:
        """
        Get a summary of bills for a specific month and year.

        Args:
            year (int): The year of the summary.
            month (int): The month of the summary (1-12).
        Returns:
            Dict[str, Any]: Dictionary of monthly summary statistics.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        all_bills = BillService.get_all_bills()
        monthly_bills = []
        
        for bill in all_bills:
            try:
                due_date = datetime.strptime(bill['due_date'], DATE_FORMAT)
                if start_date <= due_date <= end_date:
                    monthly_bills.append(bill)
            except ValueError:
                continue
        
        total_amount = sum(b.get('amount', 0) or 0 for b in monthly_bills)
        paid_amount = sum(b.get('amount', 0) or 0 for b in monthly_bills if b.get('paid', False))
        
        return {
            'month': month,
            'year': year,
            'total_bills': len(monthly_bills),
            'paid_bills': len([b for b in monthly_bills if b.get('paid', False)]),
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'unpaid_amount': total_amount - paid_amount
        } 