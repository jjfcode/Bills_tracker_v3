#!/usr/bin/env python3
"""
Demo script for Advanced Filtering features in Bills Tracker v3.

This script demonstrates:
1. Default pending view (shows only unpaid bills)
2. Status filtering (Pending, Paid, Auto-Pay, All)
3. Period filtering (This Month, Last Month, etc.)
4. Combined filtering (status + period + search)
5. Bill counter and clear filter options
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.db import initialize_database, insert_bill, fetch_all_bills
from datetime import datetime, timedelta

def demo_advanced_filtering():
    """Demonstrate the advanced filtering features"""
    
    print("=" * 60)
    print("Bills Tracker v3 - Advanced Filtering Demo")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Add sample bills for different scenarios
    print("\n2. Adding sample bills for filtering demonstration...")
    
    today = datetime.now()
    
    sample_bills = [
        # This month - pending
        {
            "name": "Electricity Bill",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # This month - paid
        {
            "name": "Internet Service",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "paid": True,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "category_id": 1,  # Utilities
            "payment_method_id": 1  # Auto-Pay
        },
        # This month - auto-pay
        {
            "name": "Netflix Subscription",
            "due_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "category_id": 5,  # Entertainment
            "payment_method_id": 1  # Auto-Pay
        },
        # Last month - paid
        {
            "name": "Car Insurance",
            "due_date": (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d"),
            "paid": True,
            "billing_cycle": "monthly",
            "reminder_days": 10,
            "category_id": 4,  # Insurance
            "payment_method_id": 3  # Credit Card
        },
        # Last month - pending
        {
            "name": "Phone Bill",
            "due_date": (today.replace(day=1) - timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # This year - different month
        {
            "name": "Annual Software License",
            "due_date": (today.replace(month=6, day=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "annually",
            "reminder_days": 30,
            "category_id": 9,  # Shopping
            "payment_method_id": 3  # Credit Card
        }
    ]
    
    for bill in sample_bills:
        insert_bill(bill)
        status = "Paid" if bill["paid"] else "Pending"
        print(f"  ✓ Added: {bill['name']} - {status} - Due: {bill['due_date']}")
    
    # Fetch all bills
    all_bills = fetch_all_bills()
    print(f"\n3. Total bills in database: {len(all_bills)}")
    
    # Demonstrate default pending view
    print("\n4. Default Pending View (shows only unpaid bills):")
    print("-" * 60)
    pending_bills = [bill for bill in all_bills if not bill["paid"]]
    for bill in pending_bills:
        print(f"  - {bill['name']} (Due: {bill['due_date']})")
    print(f"  Total pending bills: {len(pending_bills)}")
    
    # Demonstrate status filtering
    print("\n5. Status Filtering:")
    print("-" * 60)
    
    # Paid bills
    paid_bills = [bill for bill in all_bills if bill["paid"]]
    print(f"  Paid bills ({len(paid_bills)}):")
    for bill in paid_bills:
        print(f"    - {bill['name']}")
    
    # Auto-Pay bills (unpaid but with automatic payment method)
    auto_pay_bills = [bill for bill in all_bills if not bill["paid"] and bill.get("payment_method_automatic", False)]
    print(f"  Auto-Pay bills ({len(auto_pay_bills)}):")
    for bill in auto_pay_bills:
        print(f"    - {bill['name']}")
    
    # Regular pending bills
    regular_pending = [bill for bill in all_bills if not bill["paid"] and not bill.get("payment_method_automatic", False)]
    print(f"  Regular pending bills ({len(regular_pending)}):")
    for bill in regular_pending:
        print(f"    - {bill['name']}")
    
    # Demonstrate period filtering
    print("\n6. Period Filtering:")
    print("-" * 60)
    
    # This month
    this_month_bills = [bill for bill in all_bills 
                       if bill["due_date"].startswith(today.strftime("%Y-%m"))]
    print(f"  This Month bills ({len(this_month_bills)}):")
    for bill in this_month_bills:
        status = "Paid" if bill["paid"] else "Pending"
        print(f"    - {bill['name']} ({status})")
    
    # Last month
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_bills = [bill for bill in all_bills 
                       if bill["due_date"].startswith(last_month.strftime("%Y-%m"))]
    print(f"  Last Month bills ({len(last_month_bills)}):")
    for bill in last_month_bills:
        status = "Paid" if bill["paid"] else "Pending"
        print(f"    - {bill['name']} ({status})")
    
    # This year
    this_year_bills = [bill for bill in all_bills 
                      if bill["due_date"].startswith(str(today.year))]
    print(f"  This Year bills ({len(this_year_bills)}):")
    for bill in this_year_bills:
        status = "Paid" if bill["paid"] else "Pending"
        print(f"    - {bill['name']} ({status})")
    
    # Demonstrate combined filtering
    print("\n7. Combined Filtering (This Month + Pending):")
    print("-" * 60)
    combined_filtered = [bill for bill in all_bills 
                        if bill["due_date"].startswith(today.strftime("%Y-%m")) 
                        and not bill["paid"]]
    for bill in combined_filtered:
        print(f"  - {bill['name']} (Due: {bill['due_date']})")
    print(f"  Total: {len(combined_filtered)} bills")
    
    # Demonstrate search functionality
    print("\n8. Search Functionality:")
    print("-" * 60)
    
    # Search by name
    search_term = "bill"
    name_search = [bill for bill in all_bills if search_term.lower() in bill["name"].lower()]
    print(f"  Bills with '{search_term}' in name ({len(name_search)}):")
    for bill in name_search:
        print(f"    - {bill['name']}")
    
    # Search by category
    utilities_bills = [bill for bill in all_bills if bill.get("category_name") == "Utilities"]
    print(f"  Utilities category bills ({len(utilities_bills)}):")
    for bill in utilities_bills:
        print(f"    - {bill['name']}")
    
    print("\n" + "=" * 60)
    print("Advanced Filtering Demo completed successfully!")
    print("=" * 60)
    
    print("\nFeature Summary:")
    print("✓ Default view shows only pending bills (most useful for daily use)")
    print("✓ Status filtering: Pending, Paid, Auto-Pay, All")
    print("✓ Period filtering: This Month, Last Month, Previous Month, This Year, Last Year")
    print("✓ Combined filtering: Use multiple filters together")
    print("✓ Real-time search with multiple field options")
    print("✓ Bill counter shows exactly how many bills are displayed")
    print("✓ Clear filter options to reset to default view")
    
    print("\nTo test the GUI:")
    print("1. Run: python main_desktop.py")
    print("2. Use the Status dropdown to filter by Pending/Paid/Auto-Pay/All")
    print("3. Use the Period dropdown to filter by time periods")
    print("4. Use the search bar to find specific bills")
    print("5. Combine filters for precise results")
    print("6. Use 'Clear All' to reset to default pending view")

if __name__ == "__main__":
    demo_advanced_filtering() 