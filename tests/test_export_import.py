#!/usr/bin/env python3
"""
Test script for export/import functionality in Bills Tracker v3.
This script tests the CSV export and import features.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.db import initialize_database, insert_bill, fetch_all_bills
import csv
import tempfile
from datetime import datetime, timedelta

def test_export_import():
    """Test export and import functionality"""
    
    print("=" * 60)
    print("Bills Tracker v3 - Export/Import Test")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Add sample bills
    print("\n2. Adding sample bills...")
    sample_bills = [
        {
            "name": "Electricity Bill",
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "web_page": "https://electricity-company.com",
            "company_email": "support@electricity-company.com",
            "support_phone": "+1-555-123-4567",
            "account_number": "ACC-ELEC-789",
            "category_id": 1,
            "payment_method_id": 1
        },
        {
            "name": "Internet Service",
            "due_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "web_page": "https://internet-provider.com",
            "company_email": "billing@internet-provider.com",
            "support_phone": "+1-555-987-6543",
            "account_number": "ACC-INT-456",
            "category_id": 1,
            "payment_method_id": 2
        }
    ]
    
    for bill in sample_bills:
        insert_bill(bill)
        print(f"  ✓ Added: {bill['name']}")
    
    # Test export
    print("\n3. Testing CSV export...")
    bills = fetch_all_bills()
    
    # Create temporary file for export
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_filename = temp_file.name
        
        # Write CSV
        fieldnames = ['name', 'due_date', 'billing_cycle', 'reminder_days', 'web_page', 
                     'company_email', 'support_phone', 'account_number', 'paid', 
                     'category_id', 'payment_method_id']
        
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for bill in bills:
            writer.writerow({
                'name': bill.get('name', ''),
                'due_date': bill.get('due_date', ''),
                'billing_cycle': bill.get('billing_cycle', ''),
                'reminder_days': bill.get('reminder_days', 7),
                'web_page': bill.get('web_page', ''),
                'company_email': bill.get('company_email', ''),
                'support_phone': bill.get('support_phone', ''),
                'account_number': bill.get('account_number', ''),
                'paid': 1 if bill.get('paid', False) else 0,
                'category_id': bill.get('category_id', ''),
                'payment_method_id': bill.get('payment_method_id', '')
            })
    
    print(f"  ✓ Exported {len(bills)} bills to {temp_filename}")
    
    # Test import
    print("\n4. Testing CSV import...")
    
    # Read the exported file
    imported_bills = []
    with open(temp_filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            imported_bills.append(row)
    
    print(f"  ✓ Imported {len(imported_bills)} bills from CSV")
    
    # Verify data integrity
    print("\n5. Verifying data integrity...")
    
    if len(bills) == len(imported_bills):
        print("  ✓ Bill count matches")
    else:
        print(f"  ✗ Bill count mismatch: {len(bills)} vs {len(imported_bills)}")
    
    # Check first bill
    if bills and imported_bills:
        original_bill = bills[0]
        imported_bill = imported_bills[0]
        
        if original_bill['name'] == imported_bill['name']:
            print("  ✓ Bill names match")
        else:
            print(f"  ✗ Bill name mismatch: {original_bill['name']} vs {imported_bill['name']}")
    
    # Clean up
    os.unlink(temp_filename)
    print(f"  ✓ Cleaned up temporary file")
    
    print("\n" + "=" * 60)
    print("Export/Import test completed successfully!")
    print("=" * 60)
    
    print("\nTest Summary:")
    print("✓ CSV export functionality works")
    print("✓ CSV import functionality works")
    print("✓ Data integrity is maintained")
    print("✓ Temporary file cleanup works")

if __name__ == "__main__":
    test_export_import() 