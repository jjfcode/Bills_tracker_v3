#!/usr/bin/env python3
"""
Demo script for testing the "Next Month" filter functionality in Bills Tracker v3.

This script demonstrates how the new "Next Month" period filter works.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from core.db import insert_bill, fetch_all_bills
import sqlite3

def create_test_bills():
    """Create test bills with various due dates including next month"""
    
    # Connect to database
    conn = sqlite3.connect('bills.db')
    cursor = conn.cursor()
    
    # Get current date
    today = datetime.now()
    
    # Calculate next month
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    # Create test bills with different due dates
    test_bills = [
        {
            "name": "Next Month Rent",
            "amount": 1200.00,
            "due_date": next_month.strftime('%Y-%m-%d'),
            "category_id": 1,
            "payment_method_id": 1,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "paid": False
        },
        {
            "name": "Next Month Internet",
            "amount": 89.99,
            "due_date": (next_month + timedelta(days=5)).strftime('%Y-%m-%d'),
            "category_id": 1,
            "payment_method_id": 2,
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "paid": False
        },
        {
            "name": "This Month Electricity",
            "amount": 150.00,
            "due_date": today.strftime('%Y-%m-%d'),
            "category_id": 1,
            "payment_method_id": 1,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "paid": False
        },
        {
            "name": "Last Month Water",
            "amount": 75.50,
            "due_date": (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'),
            "category_id": 1,
            "payment_method_id": 1,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "paid": True
        }
    ]
    
    print("Creating test bills...")
    
    for bill in test_bills:
        try:
            insert_bill(
                name=bill["name"],
                amount=bill["amount"],
                due_date=bill["due_date"],
                category_id=bill["category_id"],
                payment_method_id=bill["payment_method_id"],
                billing_cycle=bill["billing_cycle"],
                reminder_days=bill["reminder_days"],
                paid=bill["paid"]
            )
            print(f"✓ Created: {bill['name']} - Due: {bill['due_date']}")
        except Exception as e:
            print(f"✗ Failed to create {bill['name']}: {e}")
    
    conn.close()

def test_next_month_filter():
    """Test the next month filtering logic"""
    
    print("\n" + "="*50)
    print("TESTING NEXT MONTH FILTER")
    print("="*50)
    
    # Get all bills
    all_bills = fetch_all_bills()
    
    # Current date
    today = datetime.now()
    
    # Calculate next month
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    
    print(f"Current date: {today.strftime('%Y-%m-%d')}")
    print(f"Next month: {next_month.strftime('%Y-%m')}")
    print()
    
    # Filter bills for next month
    next_month_bills = []
    for bill in all_bills:
        try:
            due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
            if due_date.year == next_month.year and due_date.month == next_month.month:
                next_month_bills.append(bill)
        except ValueError:
            continue
    
    print(f"Bills due next month ({next_month.strftime('%Y-%m')}):")
    if next_month_bills:
        for bill in next_month_bills:
            status = "Paid" if bill.get("paid", False) else "Pending"
            print(f"  • {bill['name']} - ${bill['amount']:.2f} - Due: {bill['due_date']} - {status}")
    else:
        print("  No bills found for next month")
    
    print(f"\nTotal bills in database: {len(all_bills)}")
    print(f"Bills due next month: {len(next_month_bills)}")

def show_all_bills():
    """Show all bills with their due dates"""
    
    print("\n" + "="*50)
    print("ALL BILLS IN DATABASE")
    print("="*50)
    
    all_bills = fetch_all_bills()
    
    if all_bills:
        for bill in all_bills:
            status = "Paid" if bill.get("paid", False) else "Pending"
            print(f"• {bill['name']} - ${bill['amount']:.2f} - Due: {bill['due_date']} - {status}")
    else:
        print("No bills found in database")

def main():
    """Main demo function"""
    
    print("Bills Tracker v3 - Next Month Filter Demo")
    print("="*50)
    
    # Check if database exists
    if not os.path.exists('bills.db'):
        print("Database not found. Please run the main application first to create the database.")
        return
    
    # Create test bills
    create_test_bills()
    
    # Test the filter
    test_next_month_filter()
    
    # Show all bills
    show_all_bills()
    
    print("\n" + "="*50)
    print("DEMO COMPLETE")
    print("="*50)
    print("To test the UI filter:")
    print("1. Run the main application: python run.py")
    print("2. Go to Bills view")
    print("3. Select 'Next Month' from the Period dropdown")
    print("4. Verify that only bills due next month are shown")

if __name__ == "__main__":
    main() 