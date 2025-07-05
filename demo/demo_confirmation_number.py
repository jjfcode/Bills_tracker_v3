#!/usr/bin/env python3
"""
Demo script for Payment Confirmation Number feature in Bills Tracker v3.

This script demonstrates:
1. Adding bills with confirmation numbers
2. Marking bills as paid with confirmation numbers
3. Viewing confirmation numbers in the table
4. Searching by confirmation number
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.db import initialize_database, insert_bill, fetch_all_bills, update_bill
from datetime import datetime, timedelta

def demo_confirmation_number_feature():
    """Demonstrate the payment confirmation number feature"""
    
    print("=" * 60)
    print("Bills Tracker v3 - Payment Confirmation Number Demo")
    print("=" * 60)
    
    # Initialize database
    print("1. Initializing database...")
    initialize_database()
    print("✓ Database initialized")
    
    # Add sample bills with confirmation numbers
    print("\n2. Adding sample bills with confirmation numbers...")
    
    sample_bills = [
        {
            "name": "Electricity Bill",
            "due_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "paid": True,
            "confirmation_number": "ELEC-2024-001234",
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "web_page": "https://electricity-company.com",
            "company_email": "support@electricity-company.com",
            "support_phone": "+1-555-123-4567",
            "account_number": "ACC-ELEC-789",
            "category_id": 1,  # Utilities
            "payment_method_id": 1  # Auto-Pay
        },
        {
            "name": "Internet Service",
            "due_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "paid": False,
            "confirmation_number": "",
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "web_page": "https://internet-provider.com",
            "company_email": "billing@internet-provider.com",
            "support_phone": "+1-555-987-6543",
            "account_number": "ACC-INT-456",
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        {
            "name": "Car Insurance",
            "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "paid": True,
            "confirmation_number": "INS-2024-567890",
            "billing_cycle": "monthly",
            "reminder_days": 10,
            "web_page": "https://car-insurance.com",
            "company_email": "claims@car-insurance.com",
            "support_phone": "+1-555-456-7890",
            "account_number": "ACC-INS-123",
            "category_id": 4,  # Insurance
            "payment_method_id": 3  # Credit Card
        },
        {
            "name": "Netflix Subscription",
            "due_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "paid": False,
            "confirmation_number": "",
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "web_page": "https://netflix.com",
            "company_email": "help@netflix.com",
            "support_phone": "+1-555-321-0987",
            "account_number": "ACC-NET-321",
            "category_id": 5,  # Entertainment
            "payment_method_id": 1  # Auto-Pay
        }
    ]
    
    for bill in sample_bills:
        insert_bill(bill)
        status = "Paid" if bill["paid"] else "Pending"
        confirmation = bill["confirmation_number"] if bill["confirmation_number"] else "None"
        print(f"  ✓ Added: {bill['name']} - {status} - Confirmation: {confirmation}")
    
    # Fetch and display all bills
    print("\n3. Current bills in database:")
    print("-" * 80)
    print(f"{'Name':<20} {'Due Date':<12} {'Status':<8} {'Confirmation Number':<25}")
    print("-" * 80)
    
    bills = fetch_all_bills()
    for bill in bills:
        status = "Paid" if bill["paid"] else "Pending"
        confirmation = bill["confirmation_number"] if bill["confirmation_number"] else "None"
        print(f"{bill['name']:<20} {bill['due_date']:<12} {status:<8} {confirmation:<25}")
    
    # Demonstrate updating a bill with confirmation number
    print("\n4. Demonstrating payment with confirmation number...")
    
    # Find the Netflix bill (unpaid)
    netflix_bill = None
    for bill in bills:
        if bill["name"] == "Netflix Subscription" and not bill["paid"]:
            netflix_bill = bill
            break
    
    if netflix_bill:
        # Update the bill to mark it as paid with confirmation number
        netflix_bill["paid"] = True
        netflix_bill["confirmation_number"] = "NET-2024-654321"
        update_bill(netflix_bill["id"], netflix_bill)
        print(f"  ✓ Marked '{netflix_bill['name']}' as paid with confirmation: {netflix_bill['confirmation_number']}")
    
    # Show updated bills
    print("\n5. Updated bills after payment:")
    print("-" * 80)
    print(f"{'Name':<20} {'Due Date':<12} {'Status':<8} {'Confirmation Number':<25}")
    print("-" * 80)
    
    updated_bills = fetch_all_bills()
    for bill in updated_bills:
        status = "Paid" if bill["paid"] else "Pending"
        confirmation = bill["confirmation_number"] if bill["confirmation_number"] else "None"
        print(f"{bill['name']:<20} {bill['due_date']:<12} {status:<8} {confirmation:<25}")
    
    # Demonstrate searching by confirmation number
    print("\n6. Searching by confirmation number...")
    
    # Search for bills with confirmation numbers
    paid_bills_with_confirmation = [bill for bill in updated_bills if bill["confirmation_number"]]
    print(f"  Found {len(paid_bills_with_confirmation)} bills with confirmation numbers:")
    
    for bill in paid_bills_with_confirmation:
        print(f"    - {bill['name']}: {bill['confirmation_number']}")
    
    # Search for specific confirmation number
    search_term = "ELEC"
    matching_bills = [bill for bill in updated_bills if search_term in bill.get("confirmation_number", "")]
    print(f"\n  Bills with confirmation numbers containing '{search_term}':")
    
    for bill in matching_bills:
        print(f"    - {bill['name']}: {bill['confirmation_number']}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print("\nFeature Summary:")
    print("✓ Payment confirmation numbers can be added when marking bills as paid")
    print("✓ Confirmation numbers are displayed in a new 'Confirmation' column")
    print("✓ Confirmation numbers can be searched and filtered")
    print("✓ Confirmation numbers are stored in the database")
    print("✓ Confirmation numbers can be edited in the bill edit dialog")
    print("✓ When marking a bill as unpaid, confirmation number is cleared")
    
    print("\nTo test the GUI:")
    print("1. Run: python main_desktop.py")
    print("2. Click on the checkbox in the 'Paid' column to mark a bill as paid")
    print("3. Enter a confirmation number in the dialog that appears")
    print("4. View the confirmation number in the 'Confirmation' column")
    print("5. Use the search feature to find bills by confirmation number")

if __name__ == "__main__":
    demo_confirmation_number_feature() 