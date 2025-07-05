# Tests

This folder contains test scripts and utilities for Bills Tracker v3.

## Purpose

Test scripts help verify that the application features work correctly and help identify issues before they reach production.

## Files

- `test_export_import.py` - Tests CSV export and import functionality

## Usage

To run a test script:

```bash
cd tests
python test_export_import.py
```

## Test Categories

### Functional Tests
- Test specific features like export/import
- Verify data integrity
- Check error handling

### Integration Tests
- Test database operations
- Verify GUI functionality
- Check data flow between components

### Performance Tests
- Test with large datasets
- Verify response times
- Check memory usage

## Writing New Tests

When adding new features, create corresponding test scripts:

1. Create a test file with descriptive name (e.g., `test_feature_name.py`)
2. Include setup and teardown functions
3. Test both success and failure scenarios
4. Use clear assertions and error messages
5. Update this README with new test details

## Best Practices

- Test one feature per test file
- Use descriptive test names
- Include proper error handling
- Clean up test data after tests
- Document test requirements and dependencies 