#!/usr/bin/env python3
"""
Demo script for testing the reminder and notification system.
This script creates sample bills with various due dates to test the notification system.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.db import initialize_database, insert_bill, fetch_all_bills
from core.reminder_service import ReminderService
from gui.notification_dialog import NotificationManager
import customtkinter as ctk

def demo_reminders_notifications():
    """Demo the reminder and notification system."""
    print("🚀 Starting Reminders & Notifications Demo")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    initialize_database()
    
    # Create sample bills with various due dates
    print("📝 Creating sample bills...")
    today = datetime.now().date()
    
    sample_bills = [
        # Overdue bill
        {
            "name": "Overdue Electricity Bill",
            "due_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "amount": 125.50,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "web_page": "https://electricity-company.com",
            "company_email": "support@electricity-company.com",
            "support_phone": "+1-555-123-4567",
            "account_number": "ACC-ELEC-789",
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        },
        # Due today
        {
            "name": "Today's Internet Bill",
            "due_date": today.strftime("%Y-%m-%d"),
            "amount": 89.99,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 3,
            "web_page": "https://internet-provider.com",
            "company_email": "billing@internet-provider.com",
            "support_phone": "+1-555-987-6543",
            "account_number": "ACC-INT-456",
            "category_id": 1,  # Utilities
            "payment_method_id": 1  # Auto-Pay
        },
        # Due tomorrow
        {
            "name": "Tomorrow's Rent Payment",
            "due_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "amount": 1200.00,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "web_page": "https://rental-portal.com",
            "company_email": "rental@property.com",
            "support_phone": "+1-555-456-7890",
            "account_number": "ACC-RENT-123",
            "category_id": 2,  # Housing
            "payment_method_id": 1  # Auto-Pay
        },
        # Due in 3 days
        {
            "name": "Car Insurance Premium",
            "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "amount": 245.75,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 7,
            "web_page": "https://car-insurance.com",
            "company_email": "claims@car-insurance.com",
            "support_phone": "+1-555-321-6547",
            "account_number": "ACC-INS-987",
            "category_id": 4,  # Insurance
            "payment_method_id": 3  # Credit Card
        },
        # Due in 7 days
        {
            "name": "Netflix Subscription",
            "due_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            "amount": 15.99,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 1,
            "web_page": "https://netflix.com",
            "company_email": "support@netflix.com",
            "support_phone": "+1-555-888-9999",
            "account_number": "ACC-NETFLIX-001",
            "category_id": 5,  # Entertainment
            "payment_method_id": 3  # Credit Card
        },
        # Due in 10 days
        {
            "name": "Phone Bill",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "amount": 75.00,
            "paid": False,
            "billing_cycle": "monthly",
            "reminder_days": 5,
            "web_page": "https://phone-provider.com",
            "company_email": "billing@phone-provider.com",
            "support_phone": "+1-555-777-8888",
            "account_number": "ACC-PHONE-555",
            "category_id": 1,  # Utilities
            "payment_method_id": 2  # Manual Bank Transfer
        }
    ]
    
    # Insert sample bills
    for bill in sample_bills:
        try:
            insert_bill(bill)
            print(f"✅ Added: {bill['name']} - Due: {bill['due_date']} - Amount: ${bill['amount']}")
        except Exception as e:
            print(f"❌ Failed to add {bill['name']}: {e}")
    
    print("\n📋 Current bills in database:")
    bills = fetch_all_bills()
    for bill in bills:
        if not bill['paid']:
            print(f"  - {bill['name']}: Due {bill['due_date']}, Amount: ${bill.get('amount', 'N/A')}")
    
    print("\n🔔 Testing Reminder Service...")
    
    # Create a simple test window
    root = ctk.CTk()
    root.title("Reminder Demo")
    root.geometry("400x300")
    
    # Initialize notification manager
    notification_manager = NotificationManager()
    
    # Initialize reminder service with shorter check interval for demo
    reminder_service = ReminderService(check_interval=10)  # Check every 10 seconds for demo
    
    def on_notification(notification_data):
        """Handle notifications from reminder service."""
        print(f"🔔 Notification triggered: {notification_data['message']}")
        notification_manager.show_notification(
            notification_data,
            on_mark_paid=lambda bill_id: print(f"✅ Marked bill {bill_id} as paid"),
            on_snooze=lambda bill_id, seconds: print(f"⏰ Snoozed bill {bill_id} for {seconds//3600} hours")
        )
    
    # Start reminder service
    reminder_service.start(notification_callback=on_notification)
    
    # Add some UI elements for demo control
    info_label = ctk.CTkLabel(
        root, 
        text="Reminder service is running!\n\nCheck interval: 10 seconds\n\nClose this window to stop the demo.",
        font=("Arial", 12)
    )
    info_label.pack(pady=20)
    
    def show_upcoming_reminders():
        """Show upcoming reminders."""
        reminders = reminder_service.get_upcoming_reminders(days_ahead=14)
        if reminders:
            reminder_text = "📅 Upcoming Reminders (next 14 days):\n\n"
            for reminder in reminders:
                reminder_text += f"• {reminder['name']}: Due {reminder['due_date']} (in {reminder['days_until_due']} days)\n"
        else:
            reminder_text = "No upcoming reminders in the next 14 days."
        
        # Show in a popup
        popup = ctk.CTkToplevel(root)
        popup.title("Upcoming Reminders")
        popup.geometry("500x400")
        
        text_widget = ctk.CTkTextbox(popup, width=480, height=350)
        text_widget.pack(pady=10, padx=10)
        text_widget.insert("1.0", reminder_text)
        text_widget.configure(state="disabled")
    
    def show_service_status():
        """Show reminder service status."""
        status = reminder_service.get_service_status()
        status_text = f"🔧 Reminder Service Status:\n\n"
        status_text += f"Running: {status['running']}\n"
        status_text += f"Check Interval: {status['check_interval']} seconds\n"
        status_text += f"Last Check: {status['last_check_time'] or 'Never'}\n"
        status_text += f"Sent Reminders: {status['sent_reminders_count']}\n"
        status_text += f"Thread Alive: {status['thread_alive']}"
        
        # Show in a popup
        popup = ctk.CTkToplevel(root)
        popup.title("Service Status")
        popup.geometry("400x300")
        
        text_widget = ctk.CTkTextbox(popup, width=380, height=250)
        text_widget.pack(pady=10, padx=10)
        text_widget.insert("1.0", status_text)
        text_widget.configure(state="disabled")
    
    # Add control buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=20)
    
    ctk.CTkButton(
        button_frame, 
        text="Show Upcoming Reminders", 
        command=show_upcoming_reminders
    ).pack(side="left", padx=10)
    
    ctk.CTkButton(
        button_frame, 
        text="Show Service Status", 
        command=show_service_status
    ).pack(side="left", padx=10)
    
    def on_close():
        """Handle window close."""
        print("🛑 Stopping reminder service...")
        reminder_service.stop()
        notification_manager.close_all_notifications()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    print("🎯 Demo window opened. The reminder service will check for due bills every 10 seconds.")
    print("💡 You should see notifications for overdue bills and bills due today/tomorrow.")
    print("💡 Use the buttons to check upcoming reminders and service status.")
    
    # Start the GUI
    root.mainloop()
    
    print("✅ Demo completed!")

if __name__ == "__main__":
    demo_reminders_notifications() 