#!/usr/bin/env python3
"""
Test script to verify notification button functionality.

This script creates a simple notification dialog to test
if the buttons are clickable and working properly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.gui.notification_dialog import BillNotificationDialog

def test_notification_buttons():
    """Test notification button functionality."""
    
    # Set up the application
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Notification Button Test")
    root.geometry("400x300")
    
    # Create a frame
    frame = ctk.CTkFrame(root)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Add a title
    title = ctk.CTkLabel(frame, text="Notification Button Test", font=("Arial", 16, "bold"))
    title.pack(pady=(0, 20))
    
    def create_test_notification():
        """Create a test notification."""
        test_data = {
            'title': 'Test Bill Reminder',
            'message': 'This is a test notification',
            'bill_name': 'Test Bill',
            'details': 'Due: 2024-12-31\nAmount: $100.00',
            'urgency': 'REMINDER',
            'bill_id': 123,
            'web_page': 'https://www.example.com',
            'company_email': 'test@example.com'
        }
        
        def on_mark_paid(bill_id):
            print(f"[TEST] Mark Paid callback called for bill_id: {bill_id}")
        
        def on_snooze(bill_id, seconds):
            print(f"[TEST] Snooze callback called for bill_id: {bill_id}, seconds: {seconds}")
        
        notification = BillNotificationDialog(
            test_data, 
            on_mark_paid=on_mark_paid, 
            on_snooze=on_snooze
        )
        print("[TEST] Test notification created")
    
    # Add a button to create test notification
    test_btn = ctk.CTkButton(
        frame, 
        text="Create Test Notification", 
        command=create_test_notification,
        width=200
    )
    test_btn.pack(pady=20)
    
    # Add instructions
    instructions = ctk.CTkLabel(
        frame, 
        text="Instructions:\n"
             "• Click 'Create Test Notification' to open a test popup\n"
             "• Try clicking the buttons in the popup\n"
             "• Check terminal for debug messages\n"
             "• Close the popup with the X button",
        font=("Arial", 12),
        justify="left"
    )
    instructions.pack(pady=20)
    
    # Add a close button
    close_button = ctk.CTkButton(
        frame, 
        text="Close", 
        command=root.destroy,
        width=100
    )
    close_button.pack(pady=20)
    
    print("✅ Notification Button Test started!")
    print("   - Click 'Create Test Notification' to test")
    print("   - Watch for debug messages in terminal")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    test_notification_buttons() 