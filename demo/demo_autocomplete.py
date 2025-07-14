#!/usr/bin/env python3
"""
Demo script to test the auto-complete functionality for the web page field.
This script demonstrates the website auto-complete feature with common bill websites.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.autocomplete_utils import WebsiteAutoComplete, AutoCompleteEntry
import tkinter as tk
from tkinter import ttk

def demo_autocomplete():
    """Demonstrate the auto-complete functionality"""
    
    print("=" * 60)
    print("Website Auto-Complete Demo")
    print("=" * 60)
    
    # Test the WebsiteAutoComplete class
    print("1. Testing WebsiteAutoComplete class:")
    print("-" * 60)
    
    # Get all websites
    all_websites = WebsiteAutoComplete.get_all_websites()
    print(f"Total websites available: {len(all_websites)}")
    
    # Show websites by category
    for category, websites in WebsiteAutoComplete.COMMON_WEBSITES.items():
        print(f"\n{category} ({len(websites)} websites):")
        for website in websites[:3]:  # Show first 3 for brevity
            print(f"  - {website}")
        if len(websites) > 3:
            print(f"  ... and {len(websites) - 3} more")
    
    # Test search functionality
    print("\n2. Testing search functionality:")
    print("-" * 60)
    
    test_queries = ["netflix", "bank", "insurance", "electric", "amazon"]
    
    for query in test_queries:
        results = WebsiteAutoComplete.search_websites(query, limit=5)
        print(f"\nSearch for '{query}' ({len(results)} results):")
        for result in results:
            print(f"  - {result}")
    
    # Test URL formatting
    print("\n3. Testing URL formatting:")
    print("-" * 60)
    
    test_urls = [
        "netflix.com",
        "https://www.amazon.com",
        "www.chase.com",
        "geico.com",
        ""
    ]
    
    for url in test_urls:
        formatted = WebsiteAutoComplete.format_url(url)
        domain = WebsiteAutoComplete.extract_domain(formatted)
        print(f"Original: '{url}'")
        print(f"Formatted: '{formatted}'")
        print(f"Domain: '{domain}'")
        print()
    
    # Test auto-complete entry widget
    print("4. Testing AutoCompleteEntry widget:")
    print("-" * 60)
    print("Creating a test window with auto-complete entry...")
    
    # Create test window
    root = tk.Tk()
    root.title("Auto-Complete Demo")
    root.geometry("600x400")
    
    # Add instructions
    instructions = tk.Label(
        root, 
        text="Type in the field below to see auto-complete suggestions.\n"
             "Use Up/Down arrows to navigate, Enter to select, Escape to close.",
        font=("Arial", 12),
        wraplength=550
    )
    instructions.pack(pady=20)
    
    # Create auto-complete entry
    entry = AutoCompleteEntry(root, width=50)
    entry.pack(pady=20)
    
    # Add a label to show selected value
    result_label = tk.Label(root, text="Selected: ", font=("Arial", 10))
    result_label.pack(pady=10)
    
    def update_result():
        """Update the result label with current entry value"""
        result_label.config(text=f"Selected: {entry.get()}")
        root.after(100, update_result)
    
    update_result()
    
    # Add category-specific buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    def set_category_websites(category):
        """Set auto-complete data for a specific category"""
        websites = WebsiteAutoComplete.get_websites_by_category(category)
        entry.set_auto_complete_data(websites)
        print(f"Set auto-complete data for {category}: {len(websites)} websites")
    
    categories = list(WebsiteAutoComplete.COMMON_WEBSITES.keys())
    for i, category in enumerate(categories):
        btn = tk.Button(
            button_frame, 
            text=category, 
            command=lambda cat=category: set_category_websites(cat)
        )
        btn.grid(row=i//3, column=i%3, padx=5, pady=5)
    
    # Add reset button
    reset_btn = tk.Button(
        button_frame, 
        text="All Websites", 
        command=lambda: entry.set_auto_complete_data(WebsiteAutoComplete.get_all_websites())
    )
    reset_btn.grid(row=len(categories)//3 + 1, column=0, columnspan=3, padx=5, pady=10)
    
    print("\nDemo window opened!")
    print("Features to test:")
    print("• Type 'netflix', 'amazon', 'chase', etc. to see suggestions")
    print("• Use Up/Down arrow keys to navigate suggestions")
    print("• Press Enter to select a suggestion")
    print("• Press Escape to close suggestions")
    print("• Click category buttons to filter suggestions")
    print("• Click 'All Websites' to show all suggestions")
    
    # Start the GUI
    root.mainloop()
    
    print("\n" + "=" * 60)
    print("Auto-Complete Demo completed!")
    print("=" * 60)

if __name__ == "__main__":
    demo_autocomplete() 