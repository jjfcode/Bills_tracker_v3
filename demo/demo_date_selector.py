#!/usr/bin/env python3
"""
Demo script for Advanced Date Selection features in Bills Tracker v3.

This script demonstrates:
1. Visual calendar picker functionality
2. Direct date input with validation
3. Fallback date picker when calendar unavailable
4. Date format validation and error handling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.db import initialize_database, insert_bill, fetch_all_bills
from datetime import datetime, timedelta

def demo_date_selector():
    """Demonstrate the advanced date selection features"""
    
    print("=" * 60)
    print("Bills Tracker v3 - Advanced Date Selection Demo")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Demonstrate different date scenarios
    print("\n2. Adding bills with various date scenarios...")
    
    today = datetime.now()
    
    sample_bills = [
        # Today
        {
            "name": "Urgent Payment",
            "due_date": today.strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "one-time",
            "reminder_days": 1,
            "category_id": 10,  # Other
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # Tomorrow
        {
            "name": "Tomorrow's Bill",
            "due_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "one-time",
            "reminder_days": 1,
            "category_id": 10,  # Other
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # This week
        {
            "name": "Weekly Subscription",
            "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "weekly",
            "reminder_days": 2,
            "category_id": 5,  # Entertainment
            "payment_method_id": 1  # Auto-Pay
        },
        # Next week
        {
            "name": "Next Week's Bill",
            "due_date": (today + timedelta(days=8)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "bi-weekly",
            "reminder_days": 5,
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # This month
        {
            "name": "Monthly Rent",
            "due_date": (today + timedelta(days=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "category_id": 2,  # Housing
            "payment_method_id": 1  # Auto-Pay
        },
        # Next month
        {
            "name": "Next Month's Insurance",
            "due_date": (today + timedelta(days=35)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 10,
            "category_id": 4,  # Insurance
            "payment_method_id": 3  # Credit Card
        },
        # This year (different month)
        {
            "name": "Annual Software License",
            "due_date": (today.replace(month=6, day=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "annually",
            "reminder_days": 30,
            "category_id": 9,  # Shopping
            "payment_method_id": 3  # Credit Card
        },
        # Next year
        {
            "name": "Next Year's Tax",
            "due_date": (today.replace(year=today.year + 1, month=4, day=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "billing_cycle": "annually",
            "reminder_days": 60,
            "category_id": 10,  # Other
            "payment_method_id": 2  # Manual Bank Transfer
        }
    ]
    
    for bill in sample_bills:
        insert_bill(bill)
        print(f"  ✓ Added: {bill['name']} - Due: {bill['due_date']}")
    
    # Fetch all bills
    all_bills = fetch_all_bills()
    print(f"\n3. Total bills in database: {len(all_bills)}")
    
    # Demonstrate date categorization
    print("\n4. Date Categorization:")
    print("-" * 60)
    
    # Today and tomorrow
    urgent_bills = [bill for bill in all_bills 
                   if bill["due_date"] in [today.strftime("%Y-%m-%d"), 
                                         (today + timedelta(days=1)).strftime("%Y-%m-%d")]]
    print(f"  Urgent (Today/Tomorrow) bills ({len(urgent_bills)}):")
    for bill in urgent_bills:
        print(f"    - {bill['name']} (Due: {bill['due_date']})")
    
    # This week
    this_week_end = today + timedelta(days=7)
    this_week_bills = [bill for bill in all_bills 
                      if bill["due_date"] <= this_week_end.strftime("%Y-%m-%d") 
                      and bill["due_date"] > (today + timedelta(days=1)).strftime("%Y-%m-%d")]
    print(f"  This Week bills ({len(this_week_bills)}):")
    for bill in this_week_bills:
        print(f"    - {bill['name']} (Due: {bill['due_date']})")
    
    # This month
    this_month_bills = [bill for bill in all_bills 
                       if bill["due_date"].startswith(today.strftime("%Y-%m")) 
                       and bill["due_date"] > this_week_end.strftime("%Y-%m-%d")]
    print(f"  This Month bills ({len(this_month_bills)}):")
    for bill in this_month_bills:
        print(f"    - {bill['name']} (Due: {bill['due_date']})")
    
    # Future months
    future_bills = [bill for bill in all_bills 
                   if bill["due_date"] > (today + timedelta(days=30)).strftime("%Y-%m-%d")]
    print(f"  Future bills ({len(future_bills)}):")
    for bill in future_bills:
        print(f"    - {bill['name']} (Due: {bill['due_date']})")
    
    # Demonstrate date validation scenarios
    print("\n5. Date Validation Scenarios:")
    print("-" * 60)
    
    test_dates = [
        "2024-12-31",  # Valid date
        "2024-02-29",  # Valid leap year date
        "2023-02-29",  # Invalid leap year date
        "2024-13-01",  # Invalid month
        "2024-12-32",  # Invalid day
        "2024-12-00",  # Invalid day (zero)
        "2024-00-15",  # Invalid month (zero)
        "invalid-date",  # Invalid format
        "2024/12/31",  # Wrong format
        "31-12-2024",  # Wrong format
    ]
    
    print("  Testing date validation:")
    for test_date in test_dates:
        try:
            datetime.strptime(test_date, "%Y-%m-%d")
            print(f"    ✓ '{test_date}' - Valid")
        except ValueError:
            print(f"    ✗ '{test_date}' - Invalid")
    
    # Demonstrate billing cycle calculations
    print("\n6. Billing Cycle Calculations:")
    print("-" * 60)
    
    sample_date = datetime(2024, 1, 15)
    cycles = ["weekly", "bi-weekly", "monthly", "quarterly", "semi-annually", "annually"]
    
    print(f"  Starting from: {sample_date.strftime('%Y-%m-%d')}")
    for cycle in cycles:
        if cycle == "weekly":
            next_date = sample_date + timedelta(weeks=1)
        elif cycle == "bi-weekly":
            next_date = sample_date + timedelta(weeks=2)
        elif cycle == "monthly":
            if sample_date.month == 12:
                next_date = sample_date.replace(year=sample_date.year + 1, month=1)
            else:
                next_date = sample_date.replace(month=sample_date.month + 1)
        elif cycle == "quarterly":
            new_month = sample_date.month + 3
            new_year = sample_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            next_date = sample_date.replace(year=new_year, month=new_month)
        elif cycle == "semi-annually":
            new_month = sample_date.month + 6
            new_year = sample_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            next_date = sample_date.replace(year=new_year, month=new_month)
        elif cycle == "annually":
            next_date = sample_date.replace(year=sample_date.year + 1)
        
        print(f"    {cycle.capitalize()}: {next_date.strftime('%Y-%m-%d')}")
    
    print("\n" + "=" * 60)
    print("Advanced Date Selection Demo completed successfully!")
    print("=" * 60)
    
    print("\nFeature Summary:")
    print("✓ Visual calendar picker for intuitive date selection")
    print("✓ Direct date input with YYYY-MM-DD format")
    print("✓ Fallback date picker when calendar widget unavailable")
    print("✓ Automatic date validation and error handling")
    print("✓ Support for all common billing cycles")
    print("✓ Smart next due date calculations")
    print("✓ Date format consistency across the application")
    
    print("\nTo test the GUI:")
    print("1. Run: python main_desktop.py")
    print("2. Click 'Add Bill' to open the bill creation dialog")
    print("3. Click the 📅 button next to the Due Date field")
    print("4. Use the visual calendar to select a date")
    print("5. Or type a date directly in YYYY-MM-DD format")
    print("6. Try invalid dates to see validation in action")

if __name__ == "__main__":
    demo_date_selector() 