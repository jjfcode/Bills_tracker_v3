"""
Pytest configuration and fixtures for Bills Tracker tests.
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Test database and configuration
TEST_DB_FILE = 'test_bills_tracker.db'
TEST_CONFIG_FILE = 'test_config.json'


@pytest.fixture(scope="session")
def test_db_path():
    """Provide a temporary database path for testing."""
    return TEST_DB_FILE


@pytest.fixture(scope="session")
def test_config_path():
    """Provide a temporary config path for testing."""
    return TEST_CONFIG_FILE


@pytest.fixture(autouse=True)
def setup_test_environment(test_db_path, test_config_path):
    """Setup and teardown test environment."""
    # Setup: Remove any existing test files
    for file_path in [test_db_path, test_config_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    yield
    
    # Teardown: Clean up test files
    for file_path in [test_db_path, test_config_path]:
        if os.path.exists(file_path):
            os.remove(file_path)


@pytest.fixture
def sample_bill_data():
    """Provide sample bill data for testing."""
    return {
        'name': 'Test Electric Bill',
        'due_date': '2024-02-15',
        'billing_cycle': 'monthly',
        'reminder_days': 7,
        'amount': 150.00,
        'web_page': 'https://example.com',
        'login_info': 'testuser',
        'password': 'testpass',
        'paid': False,
        'confirmation_number': 'ABC123',
        'company_email': 'billing@example.com',
        'support_phone': '555-1234',
        'billing_phone': '555-5678',
        'customer_service_hours': '9AM-5PM',
        'account_number': '123456789',
        'reference_id': 'REF001',
        'support_chat_url': 'https://example.com/chat',
        'mobile_app': 'Example App',
        'category_id': 1,
        'payment_method_id': 1
    }


@pytest.fixture
def sample_category_data():
    """Provide sample category data for testing."""
    return {
        'name': 'Test Category',
        'color': '#ff0000',
        'description': 'Test category description'
    }


@pytest.fixture
def sample_payment_method_data():
    """Provide sample payment method data for testing."""
    return {
        'name': 'Test Payment Method',
        'description': 'Test payment method description',
        'is_automatic': False
    }


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing."""
    with patch('src.core.db.get_db_connection') as mock_conn:
        mock_cursor = Mock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_conn.return_value.commit = Mock()
        mock_conn.return_value.close = Mock()
        yield mock_conn


@pytest.fixture
def mock_auth_manager():
    """Mock authentication manager for testing."""
    with patch('src.core.auth.auth_manager') as mock_auth:
        mock_auth.is_authenticated.return_value = True
        mock_auth.get_current_user.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'user'
        }
        yield mock_auth


@pytest.fixture
def sample_bills_list():
    """Provide a list of sample bills for testing."""
    return [
        {
            'id': 1,
            'name': 'Electric Bill',
            'due_date': '2024-02-15',
            'amount': 150.00,
            'paid': False,
            'category_name': 'Utilities',
            'payment_method_name': 'Auto-Pay'
        },
        {
            'id': 2,
            'name': 'Internet Bill',
            'due_date': '2024-02-20',
            'amount': 80.00,
            'paid': True,
            'category_name': 'Utilities',
            'payment_method_name': 'Manual Bank Transfer'
        },
        {
            'id': 3,
            'name': 'Rent',
            'due_date': '2024-03-01',
            'amount': 1200.00,
            'paid': False,
            'category_name': 'Housing',
            'payment_method_name': 'Check'
        }
    ]


@pytest.fixture
def sample_categories_list():
    """Provide a list of sample categories for testing."""
    return [
        {
            'id': 1,
            'name': 'Utilities',
            'color': '#ff6b6b',
            'description': 'Electricity, water, gas, internet'
        },
        {
            'id': 2,
            'name': 'Housing',
            'color': '#4ecdc4',
            'description': 'Rent, mortgage, property taxes'
        },
        {
            'id': 3,
            'name': 'Transportation',
            'color': '#45b7d1',
            'description': 'Car payment, insurance, fuel'
        }
    ]


@pytest.fixture
def sample_payment_methods_list():
    """Provide a list of sample payment methods for testing."""
    return [
        {
            'id': 1,
            'name': 'Auto-Pay',
            'description': 'Automatic payment from bank account',
            'is_automatic': True
        },
        {
            'id': 2,
            'name': 'Manual Bank Transfer',
            'description': 'Manual bank transfer or online payment',
            'is_automatic': False
        },
        {
            'id': 3,
            'name': 'Credit Card',
            'description': 'Payment via credit card',
            'is_automatic': False
        }
    ]


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    with patch('src.utils.helpers.datetime') as mock_dt:
        # Set a fixed date for testing
        fixed_date = datetime(2024, 2, 1, 12, 0, 0)
        mock_dt.now.return_value = fixed_date
        mock_dt.strptime = datetime.strptime
        mock_dt.strftime = datetime.strftime
        yield mock_dt 