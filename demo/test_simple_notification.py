#!/usr/bin/env python3
"""
Simple notification test to isolate button click issues.
"""

import tkinter as tk
from tkinter import ttk

def create_simple_notification():
    """Create a very simple notification with basic tkinter widgets."""
    
    # Create main window
    root = tk.Tk()
    root.title("Simple Notification Test")
    root.geometry("400x300")
    
    def show_notification():
        """Show a simple notification popup."""
        
        # Create popup
        popup = tk.Toplevel(root)
        popup.title("Test Notification")
        popup.geometry("300x200")
        popup.resizable(False, False)
        
        # Make it modal
        popup.transient(root)
        popup.grab_set()
        
        # Add content
        tk.Label(popup, text="Test Notification", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(popup, text="This is a test notification").pack(pady=5)
        
        # Add buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=20)
        
        def test_click():
            print("[TEST] Button clicked!")
            popup.destroy()
        
        def test_click2():
            print("[TEST] Button 2 clicked!")
            popup.destroy()
        
        # Simple tkinter buttons
        btn1 = tk.Button(button_frame, text="Test Button 1", command=test_click, bg="green", fg="white")
        btn1.pack(side=tk.LEFT, padx=5)
        
        btn2 = tk.Button(button_frame, text="Test Button 2", command=test_click2, bg="blue", fg="white")
        btn2.pack(side=tk.LEFT, padx=5)
        
        # Add click bindings
        btn1.bind("<Button-1>", lambda e: print("[TEST] Button 1 binding clicked"))
        btn2.bind("<Button-1>", lambda e: print("[TEST] Button 2 binding clicked"))
        
        # Close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=10)
        
        # Focus the popup
        popup.focus_force()
        popup.lift()
        
        print("[TEST] Simple notification created")
    
    # Add button to create notification
    test_btn = tk.Button(root, text="Show Simple Notification", command=show_notification, bg="orange", fg="white")
    test_btn.pack(pady=20)
    
    # Add instructions
    instructions = tk.Label(root, text="Click 'Show Simple Notification' to test basic button functionality", font=("Arial", 10))
    instructions.pack(pady=10)
    
    # Close button
    close_btn = tk.Button(root, text="Close", command=root.destroy)
    close_btn.pack(pady=20)
    
    print("✅ Simple notification test started!")
    print("   - Click 'Show Simple Notification' to test")
    print("   - Watch for debug messages in terminal")
    
    root.mainloop()

if __name__ == "__main__":
    create_simple_notification() 