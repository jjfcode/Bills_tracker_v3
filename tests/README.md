# Bills Tracker Testing Suite

This directory contains comprehensive unit and integration tests for the Bills Tracker application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── run_tests.py               # Test runner script
├── README.md                  # This file
├── unit/                      # Unit tests
│   ├── test_utils.py          # Utility function tests
│   ├── test_services.py       # Service layer tests
│   └── test_config_manager.py # Configuration manager tests
├── integration/               # Integration tests
│   └── test_database_integration.py # Database and service integration tests
├── validation/                # Validation tests
├── table_features/            # Table feature tests
├── ui_improvements/           # UI improvement tests
└── test_export_import.py      # Export/import functionality tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **test_utils.py**: Tests for utility functions (amount parsing, date handling, CSV operations)
- **test_services.py**: Tests for service layer classes (BillService, CategoryService, etc.)
- **test_config_manager.py**: Tests for configuration management
- **test_validation.py**: Tests for data validation logic

### Integration Tests (`tests/integration/`)
- **test_database_integration.py**: Tests database operations and service layer integration

### Feature Tests
- **test_export_import.py**: Export/import functionality tests
- **table_features/**: Table-related feature tests
- **validation/**: Validation-specific tests
- **ui_improvements/**: UI improvement tests

## Running Tests

### Quick Start
```bash
# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py --verbose

# Run with coverage report
python tests/run_tests.py --coverage
```

### Specific Test Types
```bash
# Run only unit tests
python tests/run_tests.py --type unit

# Run only integration tests
python tests/run_tests.py --type integration

# Run all tests (explicit)
python tests/run_tests.py --type all
```

### Specific Test Files
```bash
# Run a specific test file
python tests/run_tests.py --file tests/unit/test_utils.py

# Run with verbose output
python tests/run_tests.py --file tests/unit/test_services.py --verbose
```

### List Available Tests
```bash
# List all test files
python tests/run_tests.py --list
```

### Direct Pytest Usage
```bash
# Run all tests with pytest directly
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_utils.py -v

# Run tests matching pattern
python -m pytest tests/ -k "test_parse_amount"
```

## Test Coverage

The test suite provides comprehensive coverage of:

### Core Functionality
- ✅ **Utility Functions**: Amount parsing, date handling, CSV operations
- ✅ **Service Layer**: Business logic for bills, categories, payment methods
- ✅ **Configuration Management**: Settings persistence and management
- ✅ **Data Validation**: Input validation for all data types
- ✅ **Database Operations**: CRUD operations and relationships

### Integration Testing
- ✅ **Database Integration**: Real database operations with temporary files
- ✅ **Service Integration**: Service layer with actual database
- ✅ **Validation Integration**: Validation with service layer

### Test Quality
- ✅ **Mocking**: Proper isolation of external dependencies
- ✅ **Fixtures**: Reusable test data and setup
- ✅ **Error Handling**: Testing of error conditions and edge cases
- ✅ **Data Validation**: Comprehensive validation testing

## Test Fixtures

### Database Fixtures
- `temp_db`: Creates temporary database for testing
- `temp_db_with_data`: Creates database with sample data
- `test_db_path`: Provides test database path
- `test_config_path`: Provides test config path

### Data Fixtures
- `sample_bill_data`: Sample bill data for testing
- `sample_category_data`: Sample category data
- `sample_payment_method_data`: Sample payment method data
- `sample_bills_list`: List of sample bills
- `sample_categories_list`: List of sample categories
- `sample_payment_methods_list`: List of sample payment methods

### Mock Fixtures
- `mock_db_connection`: Mocked database connection
- `mock_auth_manager`: Mocked authentication manager
- `mock_datetime`: Mocked datetime for consistent testing

## Test Patterns

### Unit Test Pattern
```python
def test_function_name_success(self):
    """Test successful operation."""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_value
```

### Integration Test Pattern
```python
def test_feature_integration(self, temp_db_with_data):
    """Test feature integration with database."""
    with patch('src.core.db.DB_FILE', temp_db_with_data):
        # Test integration between components
        result = service.method()
        assert result is not None
```

### Mock Test Pattern
```python
def test_with_mocked_dependency(self, mock_db_connection):
    """Test with mocked external dependency."""
    with patch('src.core.services.fetch_all_bills', return_value=[]):
        result = service.get_all_bills()
        assert len(result) == 0
```

## Coverage Requirements

The test suite aims for:
- **Minimum Coverage**: 80% code coverage
- **Critical Paths**: 100% coverage of core business logic
- **Error Handling**: 100% coverage of error conditions
- **Edge Cases**: Comprehensive testing of boundary conditions

## Continuous Integration

Tests are designed to run in CI/CD environments:
- No external dependencies (uses temporary files)
- Proper cleanup of test artifacts
- Consistent results across environments
- Fast execution (< 30 seconds for full suite)

## Debugging Tests

### Verbose Output
```bash
python tests/run_tests.py --verbose
```

### Specific Test Debugging
```bash
# Run single test with maximum verbosity
python -m pytest tests/unit/test_utils.py::TestParseAmount::test_parse_amount_valid_dollar_format -vvv -s
```

### Coverage Analysis
```bash
# Generate HTML coverage report
python tests/run_tests.py --coverage

# View coverage report
open htmlcov/index.html
```

## Adding New Tests

### Unit Test Guidelines
1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Follow naming convention: `test_<module_name>.py`
3. Use descriptive test method names: `test_<function>_<scenario>`
4. Include docstrings explaining test purpose
5. Use appropriate fixtures for test data
6. Mock external dependencies

### Integration Test Guidelines
1. Use temporary database fixtures
2. Test real database operations
3. Verify data persistence
4. Test service layer integration
5. Clean up test data

### Test Data Guidelines
1. Use realistic but minimal test data
2. Create fixtures for reusable data
3. Test edge cases and error conditions
4. Include both valid and invalid data

## Test Maintenance

### Regular Tasks
- Run full test suite before commits
- Update tests when adding new features
- Maintain test coverage above 80%
- Review and refactor tests regularly

### Best Practices
- Keep tests fast and focused
- Use descriptive assertions
- Avoid test interdependencies
- Clean up resources properly
- Document complex test scenarios

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `src/` is in Python path
2. **Database Errors**: Check temporary file permissions
3. **Mock Issues**: Verify mock setup and teardown
4. **Coverage Issues**: Check for missing test cases

### Environment Setup
```bash
# Install test dependencies
pip install -r requirements.txt

# Verify pytest installation
python -m pytest --version

# Run basic test
python tests/run_tests.py --list
```

## Performance

### Test Execution Times
- **Unit Tests**: ~5 seconds
- **Integration Tests**: ~10 seconds
- **Full Suite**: ~15 seconds
- **With Coverage**: ~20 seconds

### Optimization Tips
- Use appropriate test scope (unit vs integration)
- Mock expensive operations
- Use efficient test data
- Parallel test execution (when possible)

---

For more information about testing patterns and best practices, see the main project documentation. 