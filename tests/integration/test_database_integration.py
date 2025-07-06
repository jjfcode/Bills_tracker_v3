"""
Integration tests for database operations and service layer.
"""

import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch
from src.core.db import (
    initialize_database, get_db_connection, fetch_all_bills, insert_bill,
    update_bill, delete_bill, fetch_all_categories, insert_category,
    update_category, delete_category, fetch_all_payment_methods
)
from src.core.services import BillService, CategoryService, PaymentMethodService
from src.core.validation import DataValidator


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize the database
        with patch('src.core.db.DB_FILE', db_path):
            initialize_database()
            yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_database_initialization(self, temp_db):
        """Test database initialization creates all required tables."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['categories', 'payment_methods', 'bills', 'templates']
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    def test_default_categories_created(self, temp_db):
        """Test that default categories are created during initialization."""
        categories = fetch_all_categories()
        
        # Check that default categories exist
        category_names = [cat['name'] for cat in categories]
        expected_categories = [
            'Utilities', 'Housing', 'Transportation', 'Insurance',
            'Entertainment', 'Food & Dining', 'Healthcare', 'Education',
            'Shopping', 'Other'
        ]
        
        for expected in expected_categories:
            assert expected in category_names
    
    def test_default_payment_methods_created(self, temp_db):
        """Test that default payment methods are created during initialization."""
        payment_methods = fetch_all_payment_methods()
        
        # Check that default payment methods exist
        method_names = [pm['name'] for pm in payment_methods]
        expected_methods = [
            'Auto-Pay', 'Manual Bank Transfer', 'Credit Card', 'Check',
            'Cash', 'Digital Wallet', 'Direct Debit', 'Other'
        ]
        
        for expected in expected_methods:
            assert expected in method_names
    
    def test_bill_crud_operations(self, temp_db):
        """Test complete CRUD operations for bills."""
        # Create a test bill
        bill_data = {
            'name': 'Test Electric Bill',
            'due_date': '2024-02-15',
            'billing_cycle': 'monthly',
            'reminder_days': 7,
            'amount': 150.00,
            'web_page': 'https://example.com',
            'paid': False,
            'category_id': 1,
            'payment_method_id': 1
        }
        
        # Insert bill
        insert_bill(bill_data)
        
        # Fetch all bills and verify
        bills = fetch_all_bills()
        assert len(bills) == 1
        assert bills[0]['name'] == 'Test Electric Bill'
        assert bills[0]['amount'] == 150.00
        assert bills[0]['paid'] == 0  # SQLite stores as integer
        
        # Update bill
        update_data = {'name': 'Updated Electric Bill', 'amount': 175.00}
        update_bill(bills[0]['id'], update_data)
        
        # Fetch and verify update
        updated_bills = fetch_all_bills()
        assert updated_bills[0]['name'] == 'Updated Electric Bill'
        assert updated_bills[0]['amount'] == 175.00
        
        # Delete bill
        delete_bill(updated_bills[0]['id'])
        
        # Verify deletion
        remaining_bills = fetch_all_bills()
        assert len(remaining_bills) == 0
    
    def test_category_crud_operations(self, temp_db):
        """Test complete CRUD operations for categories."""
        # Create a test category
        category_data = {
            'name': 'Test Category',
            'color': '#ff0000',
            'description': 'Test category description'
        }
        
        # Insert category
        insert_category(category_data)
        
        # Fetch all categories and verify
        categories = fetch_all_categories()
        test_category = next((cat for cat in categories if cat['name'] == 'Test Category'), None)
        assert test_category is not None
        assert test_category['color'] == '#ff0000'
        
        # Update category
        update_data = {'name': 'Updated Test Category', 'color': '#00ff00'}
        update_category(test_category['id'], update_data)
        
        # Fetch and verify update
        updated_categories = fetch_all_categories()
        updated_category = next((cat for cat in updated_categories if cat['id'] == test_category['id']), None)
        assert updated_category['name'] == 'Updated Test Category'
        assert updated_category['color'] == '#00ff00'
        
        # Delete category
        delete_category(updated_category['id'])
        
        # Verify deletion
        remaining_categories = fetch_all_categories()
        deleted_category = next((cat for cat in remaining_categories if cat['id'] == test_category['id']), None)
        assert deleted_category is None
    
    def test_bill_with_category_and_payment_method(self, temp_db):
        """Test creating a bill with category and payment method relationships."""
        # Create a custom category
        category_data = {
            'name': 'Custom Category',
            'color': '#ff0000',
            'description': 'Custom category'
        }
        insert_category(category_data)
        categories = fetch_all_categories()
        custom_category = next((cat for cat in categories if cat['name'] == 'Custom Category'), None)
        
        # Create a custom payment method
        payment_method_data = {
            'name': 'Custom Payment',
            'description': 'Custom payment method',
            'is_automatic': False
        }
        insert_category(payment_method_data)  # Note: This should be insert_payment_method
        payment_methods = fetch_all_payment_methods()
        custom_payment = next((pm for pm in payment_methods if pm['name'] == 'Custom Payment'), None)
        
        # Create bill with relationships
        bill_data = {
            'name': 'Test Bill with Relationships',
            'due_date': '2024-02-15',
            'billing_cycle': 'monthly',
            'reminder_days': 7,
            'amount': 200.00,
            'paid': False,
            'category_id': custom_category['id'],
            'payment_method_id': custom_payment['id'] if custom_payment else 1
        }
        
        insert_bill(bill_data)
        
        # Fetch and verify relationships
        bills = fetch_all_bills()
        test_bill = next((bill for bill in bills if bill['name'] == 'Test Bill with Relationships'), None)
        assert test_bill is not None
        assert test_bill['category_id'] == custom_category['id']
        assert test_bill['payment_method_id'] == (custom_payment['id'] if custom_payment else 1)


class TestServiceLayerIntegration:
    """Integration tests for service layer with database."""
    
    @pytest.fixture
    def temp_db_with_data(self):
        """Create a temporary database with test data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize the database
        with patch('src.core.db.DB_FILE', db_path):
            initialize_database()
            
            # Add some test data
            test_bill_data = {
                'name': 'Test Bill 1',
                'due_date': '2024-02-15',
                'billing_cycle': 'monthly',
                'reminder_days': 7,
                'amount': 150.00,
                'paid': False,
                'category_id': 1,
                'payment_method_id': 1
            }
            insert_bill(test_bill_data)
            
            test_bill_data2 = {
                'name': 'Test Bill 2',
                'due_date': '2024-03-01',
                'billing_cycle': 'monthly',
                'reminder_days': 7,
                'amount': 200.00,
                'paid': True,
                'category_id': 2,
                'payment_method_id': 2
            }
            insert_bill(test_bill_data2)
            
            yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
    
    def test_bill_service_integration(self, temp_db_with_data):
        """Test BillService integration with database."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Test getting all bills
            bills = BillService.get_all_bills()
            assert len(bills) == 2
            
            # Verify enhanced data is added
            for bill in bills:
                assert 'urgency_color' in bill
                assert 'formatted_amount' in bill
                assert 'is_overdue' in bill
                assert 'is_urgent' in bill
            
            # Test filtering by period
            monthly_bills = BillService.get_bills_by_period("month")
            assert len(monthly_bills) == 1  # Only one bill due in February
            
            # Test filtering by category
            category_1_bills = BillService.get_bills_by_category(1)
            assert len(category_1_bills) == 1
            
            # Test searching
            search_results = BillService.search_bills("Test Bill 1", "name")
            assert len(search_results) == 1
            assert search_results[0]['name'] == 'Test Bill 1'
    
    def test_category_service_integration(self, temp_db_with_data):
        """Test CategoryService integration with database."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Test getting all categories
            categories = CategoryService.get_all_categories()
            assert len(categories) >= 10  # Default categories
            
            # Test creating a new category
            new_category_data = {
                'name': 'Integration Test Category',
                'color': '#ff0000',
                'description': 'Category created during integration test'
            }
            
            success, error = CategoryService.create_category(new_category_data)
            assert success is True
            assert error is None
            
            # Verify category was created
            updated_categories = CategoryService.get_all_categories()
            category_names = [cat['name'] for cat in updated_categories]
            assert 'Integration Test Category' in category_names
    
    def test_payment_method_service_integration(self, temp_db_with_data):
        """Test PaymentMethodService integration with database."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Test getting all payment methods
            payment_methods = PaymentMethodService.get_all_payment_methods()
            assert len(payment_methods) >= 8  # Default payment methods
            
            # Verify payment method data structure
            for pm in payment_methods:
                assert 'id' in pm
                assert 'name' in pm
                assert 'description' in pm
                assert 'is_automatic' in pm
    
    def test_bill_creation_with_validation(self, temp_db_with_data):
        """Test bill creation with validation through service layer."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Valid bill data
            valid_bill_data = {
                'name': 'Valid Test Bill',
                'due_date': '2024-04-15',
                'billing_cycle': 'monthly',
                'reminder_days': 7,
                'amount_str': '250.00',
                'category_id': 1,
                'payment_method_id': 1
            }
            
            success, error = BillService.create_bill(valid_bill_data)
            assert success is True
            assert error is None
            
            # Verify bill was created
            bills = BillService.get_all_bills()
            bill_names = [bill['name'] for bill in bills]
            assert 'Valid Test Bill' in bill_names
            
            # Invalid bill data
            invalid_bill_data = {
                'name': '',  # Empty name should fail validation
                'due_date': '2024-04-15',
                'billing_cycle': 'monthly'
            }
            
            success, error = BillService.create_bill(invalid_bill_data)
            assert success is False
            assert "Bill name is required" in error
    
    def test_bill_update_and_delete_integration(self, temp_db_with_data):
        """Test bill update and delete operations through service layer."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Get existing bills
            bills = BillService.get_all_bills()
            test_bill = bills[0]
            
            # Update bill
            update_data = {
                'name': 'Updated Bill Name',
                'amount_str': '300.00'
            }
            
            success, error = BillService.update_bill(test_bill['id'], update_data)
            assert success is True
            assert error is None
            
            # Verify update
            updated_bills = BillService.get_all_bills()
            updated_bill = next((bill for bill in updated_bills if bill['id'] == test_bill['id']), None)
            assert updated_bill['name'] == 'Updated Bill Name'
            assert updated_bill['formatted_amount'] == '$300.00'
            
            # Delete bill
            success, error = BillService.delete_bill(test_bill['id'])
            assert success is True
            assert error is None
            
            # Verify deletion
            remaining_bills = BillService.get_all_bills()
            deleted_bill = next((bill for bill in remaining_bills if bill['id'] == test_bill['id']), None)
            assert deleted_bill is None
    
    def test_analytics_integration(self, temp_db_with_data):
        """Test analytics service integration with database."""
        with patch('src.core.db.DB_FILE', temp_db_with_data):
            # Get bill statistics
            stats = BillService.get_all_bills()
            assert len(stats) == 2
            
            # Test analytics calculations
            total_amount = sum(bill.get('amount', 0) or 0 for bill in stats)
            paid_amount = sum(bill.get('amount', 0) or 0 for bill in stats if bill.get('paid', False))
            
            assert total_amount == 350.00  # 150 + 200
            assert paid_amount == 200.00   # Only second bill is paid


class TestDataValidationIntegration:
    """Integration tests for data validation with services."""
    
    def test_bill_validation_integration(self):
        """Test bill validation integration with service layer."""
        # Test valid bill data
        valid_bill_data = {
            'name': 'Valid Bill',
            'due_date': '2024-12-31',
            'billing_cycle': 'monthly',
            'reminder_days': 7,
            'amount_str': '100.00',
            'web_page': 'https://example.com',
            'company_email': 'test@example.com',
            'support_phone': '555-1234'
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_bill_data(valid_bill_data)
        assert is_valid is True
        assert error is None
        assert cleaned_data['name'] == 'Valid Bill'
        assert cleaned_data['amount'] == 100.00  # Should be parsed from amount_str
        
        # Test invalid bill data
        invalid_bill_data = {
            'name': '',  # Empty name
            'due_date': 'invalid-date',
            'billing_cycle': 'invalid-cycle',
            'amount_str': 'not-a-number'
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_bill_data(invalid_bill_data)
        assert is_valid is False
        assert "Bill name is required" in error
    
    def test_category_validation_integration(self):
        """Test category validation integration with service layer."""
        # Test valid category data
        valid_category_data = {
            'name': 'Valid Category',
            'color': '#ff0000',
            'description': 'Valid category description'
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_category_data(valid_category_data)
        assert is_valid is True
        assert error is None
        assert cleaned_data['name'] == 'Valid Category'
        
        # Test invalid category data
        invalid_category_data = {
            'name': '',  # Empty name
            'color': 'invalid-color'
        }
        
        is_valid, error, cleaned_data = DataValidator.validate_category_data(invalid_category_data)
        assert is_valid is False
        assert "Category name is required" in error 