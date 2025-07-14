#!/usr/bin/env python3
"""
Test script to verify the auto-complete entry widget fix.

This script tests that the AutoCompleteEntry widget properly handles
the placeholder_text parameter and other CustomTkinter features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.utils.autocomplete_utils import create_website_autocomplete_entry

def test_autocomplete_entry():
    """Test the auto-complete entry widget."""
    
    # Set up the application
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Auto-Complete Entry Test")
    root.geometry("600x400")
    
    # Create a frame
    frame = ctk.CTkFrame(root)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Add a label
    label = ctk.CTkLabel(frame, text="Test Auto-Complete Entry Widget", font=("Arial", 16, "bold"))
    label.pack(pady=(0, 20))
    
    # Test 1: Basic auto-complete entry with placeholder
    test_label1 = ctk.CTkLabel(frame, text="Test 1: Basic entry with placeholder_text:")
    test_label1.pack(anchor="w", padx=20, pady=(10, 5))
    
    entry1 = create_website_autocomplete_entry(
        frame, 
        placeholder_text="Enter website URL...",
        width=400
    )
    entry1.pack(pady=(0, 20))
    
    # Test 2: Auto-complete entry with different placeholder
    test_label2 = ctk.CTkLabel(frame, text="Test 2: Entry with custom placeholder:")
    test_label2.pack(anchor="w", padx=20, pady=(10, 5))
    
    entry2 = create_website_autocomplete_entry(
        frame, 
        placeholder_text="Type to see suggestions...",
        width=400
    )
    entry2.pack(pady=(0, 20))
    
    # Test 3: Auto-complete entry without placeholder
    test_label3 = ctk.CTkLabel(frame, text="Test 3: Entry without placeholder:")
    test_label3.pack(anchor="w", padx=20, pady=(10, 5))
    
    entry3 = create_website_autocomplete_entry(
        frame, 
        width=400
    )
    entry3.pack(pady=(0, 20))
    
    # Add instructions
    instructions = ctk.CTkLabel(
        frame, 
        text="Instructions:\n"
             "• Type in any entry field to see website suggestions\n"
             "• Use Up/Down arrows to navigate suggestions\n"
             "• Press Enter to select a suggestion\n"
             "• Press Escape to close suggestions",
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
    
    print("✅ Auto-complete entry widget test started successfully!")
    print("   - All entries should display with proper placeholder text")
    print("   - Type to see website suggestions")
    print("   - No errors should occur")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    test_autocomplete_entry() 