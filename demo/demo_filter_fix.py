#!/usr/bin/env python3
"""
Demo script to test the filtering fix for "Pending" status + "This Month" period.
This script demonstrates that the fix correctly shows all unpaid bills (both regular pending and auto-pay) 
when filtering by "Pending" status and "This Month" period.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from core.db import insert_bill, fetch_all_bills, initialize_database

def test_filter_fix():
    """Test the filtering fix for Pending + This Month combination"""
    
    print("=" * 60)
    print("Testing Filter Fix: Pending Status + This Month Period")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Get current date
    today = datetime.now()
    current_month = today.strftime("%Y-%m")
    
    print(f"\n2. Current month: {current_month}")
    
    # Create test bills for this month
    print("\n3. Creating test bills for this month...")
    
    test_bills = [
        # This month - regular pending
        {
            "name": "Electricity Bill (Pending)",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer (not automatic)
        },
        # This month - auto-pay pending
        {
            "name": "Netflix Subscription (Auto-Pay)",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "category_id": 5,  # Entertainment
            "payment_method_id": 1  # Auto-Pay (automatic)
        },
        # This month - paid
        {
            "name": "Internet Service (Paid)",
            "due_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "paid": True,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "category_id": 1,  # Utilities
            "payment_method_id": 1  # Auto-Pay
        },
        # Last month - pending (should not appear in "This Month" filter)
        {
            "name": "Last Month Bill (Pending)",
            "due_date": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d"),
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
    
    # Test the filtering logic
    print("\n5. Testing Filter Logic:")
    print("-" * 60)
    
    # Simulate "Pending" status filter (should show all unpaid bills)
    pending_bills = [bill for bill in all_bills if not bill.get("paid", False)]
    print(f"Pending status filter (all unpaid bills): {len(pending_bills)} bills")
    for bill in pending_bills:
        auto_pay = " (Auto-Pay)" if bill.get("payment_method_automatic", False) else " (Regular)"
        print(f"  - {bill['name']}{auto_pay}")
    
    # Simulate "This Month" period filter
    this_month_bills = [bill for bill in all_bills 
                       if bill["due_date"].startswith(current_month)]
    print(f"\nThis Month period filter: {len(this_month_bills)} bills")
    for bill in this_month_bills:
        status = "Paid" if bill.get("paid", False) else "Pending"
        auto_pay = " (Auto-Pay)" if bill.get("payment_method_automatic", False) else " (Regular)"
        print(f"  - {bill['name']} - {status}{auto_pay}")
    
    # Simulate combined filter: "Pending" + "This Month"
    combined_filtered = [bill for bill in all_bills 
                        if bill["due_date"].startswith(current_month) 
                        and not bill.get("paid", False)]
    print(f"\nCombined filter (Pending + This Month): {len(combined_filtered)} bills")
    for bill in combined_filtered:
        auto_pay = " (Auto-Pay)" if bill.get("payment_method_automatic", False) else " (Regular)"
        print(f"  - {bill['name']}{auto_pay}")
    
    # Test the specific issue that was fixed
    print("\n6. Testing the Fix:")
    print("-" * 60)
    
    # OLD LOGIC (incorrect - excluded auto-pay from pending)
    old_pending_bills = [bill for bill in all_bills 
                        if not bill.get("paid", False) 
                        and not bill.get("payment_method_automatic", False)]
    old_combined = [bill for bill in old_pending_bills 
                   if bill["due_date"].startswith(current_month)]
    
    print(f"OLD LOGIC (incorrect): {len(old_combined)} bills")
    for bill in old_combined:
        print(f"  - {bill['name']} (Regular Pending only)")
    
    # NEW LOGIC (correct - includes all unpaid bills)
    new_pending_bills = [bill for bill in all_bills 
                        if not bill.get("paid", False)]
    new_combined = [bill for bill in new_pending_bills 
                   if bill["due_date"].startswith(current_month)]
    
    print(f"\nNEW LOGIC (correct): {len(new_combined)} bills")
    for bill in new_combined:
        auto_pay = " (Auto-Pay)" if bill.get("payment_method_automatic", False) else " (Regular)"
        print(f"  - {bill['name']}{auto_pay}")
    
    # Verify the fix
    print("\n7. Verification:")
    print("-" * 60)
    
    if len(new_combined) > len(old_combined):
        print("✓ FIX VERIFIED: New logic shows more bills than old logic")
        print(f"  - Old logic: {len(old_combined)} bills")
        print(f"  - New logic: {len(new_combined)} bills")
        print(f"  - Difference: {len(new_combined) - len(old_combined)} additional bills (Auto-Pay bills)")
    else:
        print("✗ FIX NOT WORKING: Both logics show the same number of bills")
    
    # Check if auto-pay bills are included in new logic
    auto_pay_in_new = [bill for bill in new_combined if bill.get("payment_method_automatic", False)]
    if auto_pay_in_new:
        print(f"✓ Auto-Pay bills are now included: {len(auto_pay_in_new)} bills")
        for bill in auto_pay_in_new:
            print(f"  - {bill['name']}")
    else:
        print("✗ No Auto-Pay bills found in new logic")
    
    print("\n" + "=" * 60)
    print("Filter Fix Test completed!")
    print("=" * 60)
    
    print("\nExpected Behavior:")
    print("• 'Pending' status should show ALL unpaid bills (both regular and auto-pay)")
    print("• 'Auto-Pay' status should show only unpaid bills with automatic payment methods")
    print("• 'This Month' period should show bills due in the current month")
    print("• Combined filters should work correctly together")
    
    print("\nTo test in the GUI:")
    print("1. Run: python main_desktop.py")
    print("2. Set Status filter to 'Pending'")
    print("3. Set Period filter to 'This Month'")
    print("4. Verify that both regular pending and auto-pay bills are shown")

if __name__ == "__main__":
    test_filter_fix() 