"""
Unit tests for service layer classes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.core.services import BillService, CategoryService, PaymentMethodService, AnalyticsService
from src.core.validation import DataValidator


class TestBillService:
    """Test BillService functionality."""
    
    def test_get_all_bills_success(self, sample_bills_list):
        """Test successful retrieval of all bills."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            bills = BillService.get_all_bills()
            
            assert len(bills) == 3
            assert bills[0]['name'] == 'Electric Bill'
            assert bills[0]['urgency_color'] is not None
            assert bills[0]['formatted_amount'] == '$150.00'
            assert 'is_overdue' in bills[0]
            assert 'is_urgent' in bills[0]
    
    def test_get_bills_by_period(self, sample_bills_list):
        """Test filtering bills by time period."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            bills = BillService.get_bills_by_period("month")
            
            # Should return bills due in February 2024
            assert len(bills) == 2  # Electric Bill and Internet Bill
            assert all('2024-02' in bill['due_date'] for bill in bills)
    
    def test_get_bills_by_category(self, sample_bills_list):
        """Test filtering bills by category."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            # Mock category_id for Utilities
            sample_bills_list[0]['category_id'] = 1
            sample_bills_list[1]['category_id'] = 1
            sample_bills_list[2]['category_id'] = 2
            
            bills = BillService.get_bills_by_category(1)
            assert len(bills) == 2
            assert all(bill['category_id'] == 1 for bill in bills)
    
    def test_get_bills_by_category_none(self, sample_bills_list):
        """Test filtering bills with no category filter."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            bills = BillService.get_bills_by_category(None)
            assert len(bills) == 3  # Should return all bills
    
    def test_search_bills_by_name(self, sample_bills_list):
        """Test searching bills by name."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            bills = BillService.search_bills("Electric", "name")
            assert len(bills) == 1
            assert bills[0]['name'] == 'Electric Bill'
    
    def test_search_bills_empty_query(self, sample_bills_list):
        """Test searching bills with empty query."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            bills = BillService.search_bills("", "name")
            assert len(bills) == 3  # Should return all bills
    
    def test_create_bill_success(self, sample_bill_data):
        """Test successful bill creation."""
        with patch('src.core.services.insert_bill') as mock_insert:
            success, error = BillService.create_bill(sample_bill_data)
            
            assert success is True
            assert error is None
            mock_insert.assert_called_once()
    
    def test_create_bill_validation_error(self, sample_bill_data):
        """Test bill creation with validation error."""
        # Modify data to cause validation error
        sample_bill_data['name'] = ""  # Empty name should fail validation
        
        with patch('src.core.services.insert_bill'):
            success, error = BillService.create_bill(sample_bill_data)
            
            assert success is False
            assert "Bill name is required" in error
    
    def test_create_bill_database_error(self, sample_bill_data):
        """Test bill creation with database error."""
        with patch('src.core.services.insert_bill', side_effect=Exception("Database error")):
            success, error = BillService.create_bill(sample_bill_data)
            
            assert success is False
            assert "Failed to create bill" in error
    
    def test_update_bill_success(self, sample_bill_data):
        """Test successful bill update."""
        with patch('src.core.services.update_bill') as mock_update:
            success, error = BillService.update_bill(1, sample_bill_data)
            
            assert success is True
            assert error is None
            mock_update.assert_called_once_with(1, sample_bill_data)
    
    def test_update_bill_validation_error(self, sample_bill_data):
        """Test bill update with validation error."""
        sample_bill_data['name'] = ""  # Empty name should fail validation
        
        with patch('src.core.services.update_bill'):
            success, error = BillService.update_bill(1, sample_bill_data)
            
            assert success is False
            assert "Bill name is required" in error
    
    def test_delete_bill_success(self):
        """Test successful bill deletion."""
        with patch('src.core.services.delete_bill') as mock_delete:
            success, error = BillService.delete_bill(1)
            
            assert success is True
            assert error is None
            mock_delete.assert_called_once_with(1)
    
    def test_delete_bill_database_error(self):
        """Test bill deletion with database error."""
        with patch('src.core.services.delete_bill', side_effect=Exception("Database error")):
            success, error = BillService.delete_bill(1)
            
            assert success is False
            assert "Failed to delete bill" in error
    
    def test_bulk_delete_bills_success(self):
        """Test successful bulk bill deletion."""
        with patch('src.core.services.delete_bill') as mock_delete:
            mock_delete.return_value = None  # No exception
            
            success, error = BillService.bulk_delete_bills([1, 2, 3])
            
            assert success is True
            assert "Successfully deleted 3 bills" in error
            assert mock_delete.call_count == 3
    
    def test_bulk_delete_bills_partial_failure(self):
        """Test bulk bill deletion with partial failures."""
        with patch('src.core.services.delete_bill') as mock_delete:
            # First call succeeds, second fails
            mock_delete.side_effect = [None, Exception("Error"), None]
            
            success, error = BillService.bulk_delete_bills([1, 2, 3])
            
            assert success is False
            assert "Failed to delete bills" in error
            assert "[2]" in error  # Should mention the failed bill ID
    
    def test_toggle_paid_status_success(self):
        """Test successful paid status toggle."""
        with patch('src.core.services.update_bill') as mock_update:
            success, error = BillService.toggle_paid_status(1, False)
            
            assert success is True
            assert error is None
            mock_update.assert_called_once_with(1, {'paid': True})
    
    def test_toggle_paid_status_database_error(self):
        """Test paid status toggle with database error."""
        with patch('src.core.services.update_bill', side_effect=Exception("Database error")):
            success, error = BillService.toggle_paid_status(1, False)
            
            assert success is False
            assert "Failed to update paid status" in error
    
    def test_renew_bill_success(self, sample_bills_list):
        """Test successful bill renewal."""
        bill_data = sample_bills_list[0].copy()
        bill_data['billing_cycle'] = 'monthly'
        bill_data['due_date'] = '2024-01-15'
        
        with patch('src.core.services.fetch_all_bills', return_value=[bill_data]):
            with patch('src.core.services.update_bill') as mock_update:
                success, error = BillService.renew_bill(1)
                
                assert success is True
                assert error is None
                mock_update.assert_called_once()
                # Check that the update includes new due date and paid=False
                call_args = mock_update.call_args[0]
                assert call_args[0] == 1  # bill_id
                assert call_args[1]['paid'] is False
                assert call_args[1]['due_date'] == '2024-02-15'
    
    def test_renew_bill_not_found(self, sample_bills_list):
        """Test bill renewal with non-existent bill."""
        with patch('src.core.services.fetch_all_bills', return_value=sample_bills_list):
            success, error = BillService.renew_bill(999)
            
            assert success is False
            assert "Bill not found" in error
    
    def test_renew_bill_one_time(self, sample_bills_list):
        """Test bill renewal for one-time bills."""
        bill_data = sample_bills_list[0].copy()
        bill_data['billing_cycle'] = 'one-time'
        
        with patch('src.core.services.fetch_all_bills', return_value=[bill_data]):
            success, error = BillService.renew_bill(1)
            
            assert success is False
            assert "Cannot renew one-time bills" in error
    
    def test_is_bill_overdue(self):
        """Test overdue bill detection."""
        # Test overdue bill
        assert BillService._is_bill_overdue("2024-01-01") is True
        
        # Test future bill
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        assert BillService._is_bill_overdue(future_date) is False
        
        # Test invalid date
        assert BillService._is_bill_overdue("invalid-date") is False
    
    def test_is_bill_urgent(self):
        """Test urgent bill detection."""
        # Test urgent bill (due within reminder days)
        urgent_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        assert BillService._is_bill_urgent(urgent_date, 7) is True
        
        # Test non-urgent bill
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        assert BillService._is_bill_urgent(future_date, 7) is False
        
        # Test overdue bill (should not be urgent)
        past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        assert BillService._is_bill_urgent(past_date, 7) is False
        
        # Test invalid date
        assert BillService._is_bill_urgent("invalid-date", 7) is False


class TestCategoryService:
    """Test CategoryService functionality."""
    
    def test_get_all_categories_success(self, sample_categories_list):
        """Test successful retrieval of all categories."""
        with patch('src.core.services.fetch_all_categories', return_value=sample_categories_list):
            categories = CategoryService.get_all_categories()
            
            assert len(categories) == 3
            assert categories[0]['name'] == 'Utilities'
            assert categories[1]['name'] == 'Housing'
    
    def test_create_category_success(self, sample_category_data):
        """Test successful category creation."""
        with patch('src.core.services.insert_category') as mock_insert:
            success, error = CategoryService.create_category(sample_category_data)
            
            assert success is True
            assert error is None
            mock_insert.assert_called_once()
    
    def test_create_category_validation_error(self, sample_category_data):
        """Test category creation with validation error."""
        sample_category_data['name'] = ""  # Empty name should fail validation
        
        with patch('src.core.services.insert_category'):
            success, error = CategoryService.create_category(sample_category_data)
            
            assert success is False
            assert "Category name is required" in error
    
    def test_update_category_success(self, sample_category_data):
        """Test successful category update."""
        with patch('src.core.services.update_category') as mock_update:
            success, error = CategoryService.update_category(1, sample_category_data)
            
            assert success is True
            assert error is None
            mock_update.assert_called_once_with(1, sample_category_data)
    
    def test_delete_category_success(self):
        """Test successful category deletion."""
        with patch('src.core.services.delete_category') as mock_delete:
            success, error = CategoryService.delete_category(1)
            
            assert success is True
            assert error is None
            mock_delete.assert_called_once_with(1)
    
    def test_delete_category_database_error(self):
        """Test category deletion with database error."""
        with patch('src.core.services.delete_category', side_effect=Exception("Database error")):
            success, error = CategoryService.delete_category(1)
            
            assert success is False
            assert "Failed to delete category" in error


class TestPaymentMethodService:
    """Test PaymentMethodService functionality."""
    
    def test_get_all_payment_methods_success(self, sample_payment_methods_list):
        """Test successful retrieval of all payment methods."""
        with patch('src.core.services.fetch_all_payment_methods', return_value=sample_payment_methods_list):
            payment_methods = PaymentMethodService.get_all_payment_methods()
            
            assert len(payment_methods) == 3
            assert payment_methods[0]['name'] == 'Auto-Pay'
            assert payment_methods[0]['is_automatic'] is True
            assert payment_methods[1]['name'] == 'Manual Bank Transfer'
            assert payment_methods[1]['is_automatic'] is False


class TestAnalyticsService:
    """Test AnalyticsService functionality."""
    
    def test_get_bill_statistics_success(self, sample_bills_list):
        """Test successful bill statistics calculation."""
        with patch('src.core.services.BillService.get_all_bills', return_value=sample_bills_list):
            stats = AnalyticsService.get_bill_statistics()
            
            assert stats['total_bills'] == 3
            assert stats['paid_bills'] == 1
            assert stats['unpaid_bills'] == 2
            assert stats['overdue_bills'] == 0  # Assuming no overdue bills in sample
            assert stats['urgent_bills'] == 0   # Assuming no urgent bills in sample
            assert stats['total_amount'] == 1430.00
            assert stats['paid_amount'] == 80.00
            assert stats['unpaid_amount'] == 1350.00
            
            # Check category stats
            assert 'Utilities' in stats['category_stats']
            assert 'Housing' in stats['category_stats']
            assert stats['category_stats']['Utilities']['count'] == 2
            assert stats['category_stats']['Housing']['count'] == 1
    
    def test_get_monthly_summary_success(self, sample_bills_list):
        """Test successful monthly summary calculation."""
        with patch('src.core.services.BillService.get_all_bills', return_value=sample_bills_list):
            summary = AnalyticsService.get_monthly_summary(2024, 2)
            
            assert summary['month'] == 2
            assert summary['year'] == 2024
            assert summary['total_bills'] == 2  # Only bills due in February
            assert summary['paid_bills'] == 1
            assert summary['total_amount'] == 230.00  # 150 + 80
            assert summary['paid_amount'] == 80.00
            assert summary['unpaid_amount'] == 150.00
    
    def test_get_monthly_summary_no_bills(self, sample_bills_list):
        """Test monthly summary with no bills in the month."""
        with patch('src.core.services.BillService.get_all_bills', return_value=sample_bills_list):
            summary = AnalyticsService.get_monthly_summary(2024, 12)
            
            assert summary['month'] == 12
            assert summary['year'] == 2024
            assert summary['total_bills'] == 0
            assert summary['paid_bills'] == 0
            assert summary['total_amount'] == 0
            assert summary['paid_amount'] == 0
            assert summary['unpaid_amount'] == 0 