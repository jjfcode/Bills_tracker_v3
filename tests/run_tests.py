#!/usr/bin/env python3
"""
Test runner for Bills Tracker application.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_tests(test_type=None, verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory
    test_dir = Path(__file__).parent
    
    if test_type:
        if test_type == 'unit':
            cmd.append(str(test_dir / 'unit'))
        elif test_type == 'integration':
            cmd.append(str(test_dir / 'integration'))
        elif test_type == 'all':
            cmd.append(str(test_dir))
        else:
            print(f"Unknown test type: {test_type}")
            return False
    else:
        # Default to all tests
        cmd.append(str(test_dir))
    
    # Add verbosity
    if verbose:
        cmd.append('-v')
    
    # Add coverage
    if coverage:
        cmd.extend([
            '--cov=src',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=80'
        ])
    
    # Add other useful options
    cmd.extend([
        '--tb=short',  # Shorter traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings'  # Disable warnings for cleaner output
    ])
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 60)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("-" * 60)
        print(f"❌ Tests failed with exit code: {e.returncode}")
        return False


def run_specific_test(test_file, verbose=False):
    """Run a specific test file."""
    cmd = ['python', '-m', 'pytest', test_file]
    
    if verbose:
        cmd.append('-v')
    
    cmd.extend([
        '--tb=short',
        '--strict-markers',
        '--disable-warnings'
    ])
    
    print(f"Running specific test: {test_file}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("-" * 60)
        print("✅ Test passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("-" * 60)
        print(f"❌ Test failed with exit code: {e.returncode}")
        return False


def list_tests():
    """List all available test files."""
    test_dir = Path(__file__).parent
    
    print("Available test files:")
    print("-" * 40)
    
    # Unit tests
    unit_dir = test_dir / 'unit'
    if unit_dir.exists():
        print("\nUnit Tests:")
        for test_file in unit_dir.glob('test_*.py'):
            print(f"  {test_file.relative_to(test_dir)}")
    
    # Integration tests
    integration_dir = test_dir / 'integration'
    if integration_dir.exists():
        print("\nIntegration Tests:")
        for test_file in integration_dir.glob('test_*.py'):
            print(f"  {test_file.relative_to(test_dir)}")
    
    # Other tests
    other_tests = []
    for test_file in test_dir.glob('test_*.py'):
        if test_file.parent == test_dir:
            other_tests.append(test_file)
    
    if other_tests:
        print("\nOther Tests:")
        for test_file in other_tests:
            print(f"  {test_file.name}")


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='Run Bills Tracker tests')
    parser.add_argument(
        '--type', '-t',
        choices=['unit', 'integration', 'all'],
        help='Type of tests to run'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run with coverage report'
    )
    parser.add_argument(
        '--file', '-f',
        help='Run specific test file'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available test files'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    if args.file:
        success = run_specific_test(args.file, args.verbose)
    else:
        success = run_tests(args.type, args.verbose, args.coverage)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 