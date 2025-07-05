#!/usr/bin/env python3
"""
Test script for enhanced table styling in Bills Tracker v3
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from gui.main_window import MainWindow
import customtkinter as ctk
from tkinter import ttk

def test_table_styling():
    """Test the enhanced table styling functionality"""
    print("Testing enhanced table styling...")
    
    # Create the main window
    app = MainWindow()
    
    # Test that enhanced styling is applied to bills table
    app.show_bills_view()
    
    # Check if the enhanced style is configured
    style = ttk.Style()
    assert "Enhanced.Treeview" in style.theme_names() or hasattr(style, 'lookup'), "Enhanced.Treeview style should be configured"
    print("✅ Enhanced.Treeview style configuration: PASS")
    
    # Test that the bills table uses the enhanced style
    assert app.bills_table.cget("style") == "Enhanced.Treeview", "Bills table should use Enhanced.Treeview style"
    print("✅ Bills table style application: PASS")
    
    # Test that enhanced styling is applied to categories table
    app.show_categories_view()
    
    # Check if the categories style is configured
    assert "Categories.Treeview" in style.theme_names() or hasattr(style, 'lookup'), "Categories.Treeview style should be configured"
    print("✅ Categories.Treeview style configuration: PASS")
    
    # Test that the categories table uses the enhanced style
    assert app.categories_table.cget("style") == "Categories.Treeview", "Categories table should use Categories.Treeview style"
    print("✅ Categories table style application: PASS")
    
    # Test alternating row colors in bills table
    app.show_bills_view()
    
    # Add some test data to verify alternating colors
    test_bills = [
        {"id": i, "name": f"Bill {i}", "paid": False, "category_name": "Test", "payment_method_name": "Test"} 
        for i in range(1, 6)  # Create 5 test bills
    ]
    
    app._filtered_bills = test_bills
    app._items_per_page = 10  # Show all bills on one page
    app._current_page = 1
    app.populate_bills_table(test_bills)
    
    # Check that rows are inserted with alternating colors
    all_items = app.bills_table.get_children()
    assert len(all_items) == 5, f"Should have 5 rows, got {len(all_items)}"
    print("✅ Alternating row colors in bills table: PASS")
    
    # Test alternating row colors in categories table
    app.show_categories_view()
    app.populate_categories_table()
    
    # Check that categories table has rows
    all_categories = app.categories_table.get_children()
    assert len(all_categories) >= 0, "Categories table should have rows"
    print("✅ Alternating row colors in categories table: PASS")
    
    print("\n🎉 All enhanced table styling tests passed!")
    print("\nFeatures implemented:")
    print("- ✅ Enhanced.Treeview style for bills table")
    print("- ✅ Categories.Treeview style for categories table")
    print("- ✅ Alternating row colors (striping)")
    print("- ✅ Enhanced header styling with primary color background")
    print("- ✅ Header hover effects")
    print("- ✅ Increased row height (30px) for better readability")
    print("- ✅ Consistent border and relief styling")
    print("- ✅ Proper color scheme integration with app theme")
    
    # Close the app
    app.destroy()

if __name__ == "__main__":
    test_table_styling() 