#!/usr/bin/env python3
"""
Demo script to test the new Apply button functionality.
This script demonstrates how the Apply button works with different Status and Period filter combinations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from core.db import insert_bill, fetch_all_bills, initialize_database

def test_apply_button():
    """Test the Apply button with different filter combinations"""
    
    print("=" * 60)
    print("Testing Apply Button Functionality")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Get current date
    today = datetime.now()
    current_month = today.strftime("%Y-%m")
    
    print(f"\n2. Current month: {current_month}")
    
    # Create test bills for different scenarios
    print("\n3. Creating test bills...")
    
    test_bills = [
        # This month - regular pending
        {
            "name": "Electricity Bill (This Month - Pending)",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # This month - auto-pay pending
        {
            "name": "Netflix (This Month - Auto-Pay)",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "category_id": 5,  # Entertainment
            "payment_method_id": 1  # Auto-Pay
        },
        # This month - paid
        {
            "name": "Internet (This Month - Paid)",
            "due_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "paid": True,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "category_id": 1,  # Utilities
            "payment_method_id": 1  # Auto-Pay
        },
        # Last month - pending
        {
            "name": "Last Month Bill (Pending)",
            "due_date": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # Next month - pending
        {
            "name": "Next Month Bill (Pending)",
            "due_date": (today.replace(month=today.month + 1, day=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        }
    ]
    
    for bill in test_bills:
        insert_bill(bill)
        status = "Paid" if bill["paid"] else "Pending"
        print(f"  ✓ Added: {bill['name']} - {status} - Due: {bill['due_date']}")
    
    # Fetch all bills
    all_bills = fetch_all_bills()
    print(f"\n4. Total bills in database: {len(all_bills)}")
    
    # Test different filter combinations
    print("\n5. Testing Apply Button with Different Filter Combinations:")
    print("-" * 60)
    
    # Test 1: Pending + This Month
    print("\nTest 1: Status='Pending' + Period='This Month'")
    print("Expected: All unpaid bills due this month")
    
    filtered_bills = all_bills.copy()
    # Apply status filter (all unpaid bills)
    filtered_bills = [bill for bill in filtered_bills if not bill.get("paid", False)]
    # Apply period filter (this month)
    this_month_bills = []
    for bill in filtered_bills:
        try:
            due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
            if due_date.year == today.year and due_date.month == today.month:
                this_month_bills.append(bill)
        except ValueError:
            continue
    
    print(f"Result: {len(this_month_bills)} bills")
    for bill in this_month_bills:
        auto_pay = " (Auto-Pay)" if bill.get("payment_method_automatic", False) else " (Regular)"
        print(f"  - {bill['name']}{auto_pay}")
    
    # Test 2: Auto-Pay + This Month
    print("\nTest 2: Status='Auto-Pay' + Period='This Month'")
    print("Expected: Only unpaid auto-pay bills due this month")
    
    filtered_bills = all_bills.copy()
    # Apply status filter (only auto-pay unpaid bills)
    filtered_bills = [bill for bill in filtered_bills if not bill.get("paid", False) and bill.get("payment_method_automatic", False)]
    # Apply period filter (this month)
    auto_pay_this_month = []
    for bill in filtered_bills:
        try:
            due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
            if due_date.year == today.year and due_date.month == today.month:
                auto_pay_this_month.append(bill)
        except ValueError:
            continue
    
    print(f"Result: {len(auto_pay_this_month)} bills")
    for bill in auto_pay_this_month:
        print(f"  - {bill['name']}")
    
    # Test 3: Paid + This Month
    print("\nTest 3: Status='Paid' + Period='This Month'")
    print("Expected: Only paid bills due this month")
    
    filtered_bills = all_bills.copy()
    # Apply status filter (only paid bills)
    filtered_bills = [bill for bill in filtered_bills if bill.get("paid", False)]
    # Apply period filter (this month)
    paid_this_month = []
    for bill in filtered_bills:
        try:
            due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
            if due_date.year == today.year and due_date.month == today.month:
                paid_this_month.append(bill)
        except ValueError:
            continue
    
    print(f"Result: {len(paid_this_month)} bills")
    for bill in paid_this_month:
        print(f"  - {bill['name']}")
    
    # Test 4: Pending + Last Month
    print("\nTest 4: Status='Pending' + Period='Last Month'")
    print("Expected: All unpaid bills due last month")
    
    filtered_bills = all_bills.copy()
    # Apply status filter (all unpaid bills)
    filtered_bills = [bill for bill in filtered_bills if not bill.get("paid", False)]
    # Apply period filter (last month)
    last_month = today.replace(day=1) - timedelta(days=1)
    pending_last_month = []
    for bill in filtered_bills:
        try:
            due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
            if due_date.year == last_month.year and due_date.month == last_month.month:
                pending_last_month.append(bill)
        except ValueError:
            continue
    
    print(f"Result: {len(pending_last_month)} bills")
    for bill in pending_last_month:
        print(f"  - {bill['name']}")
    
    print("\n" + "=" * 60)
    print("Apply Button Test completed!")
    print("=" * 60)
    
    print("\nExpected Behavior:")
    print("• Apply button should apply whatever Status and Period are selected")
    print("• Users can change filters without them being applied automatically")
    print("• Apply button gives users control over when filters are applied")
    print("• Clear button resets to default view (Pending + All)")
    
    print("\nTo test in the GUI:")
    print("1. Run: python main_desktop.py")
    print("2. Select different Status and Period combinations")
    print("3. Click 'Apply' to see the results")
    print("4. Click 'Clear' to reset to default view")
    print("5. Verify that filters are not applied automatically when selecting from dropdowns")

if __name__ == "__main__":
    test_apply_button() 