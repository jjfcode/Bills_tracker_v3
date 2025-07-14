#!/usr/bin/env python3
"""
Demo script for URL auto-formatting feature.

This script demonstrates how the auto-complete entry widget
automatically formats URLs when users type domain names.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.utils.autocomplete_utils import create_website_autocomplete_entry

def test_url_autoformat():
    """Test the URL auto-formatting feature."""
    
    # Set up the application
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("URL Auto-Format Demo")
    root.geometry("700x500")
    
    # Create a frame
    frame = ctk.CTkFrame(root)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Add a title
    title = ctk.CTkLabel(frame, text="URL Auto-Formatting Demo", font=("Arial", 18, "bold"))
    title.pack(pady=(0, 20))
    
    # Add description
    description = ctk.CTkLabel(
        frame, 
        text="Type a domain name and then press Tab or click outside to see auto-formatting:",
        font=("Arial", 12)
    )
    description.pack(pady=(0, 10))
    
    # Create auto-complete entry
    entry = create_website_autocomplete_entry(
        frame, 
        placeholder_text="Type: netflix.com, amazon.com, etc.",
        width=400
    )
    entry.pack(pady=(0, 20))
    
    # Add examples section
    examples_frame = ctk.CTkFrame(frame)
    examples_frame.pack(fill="x", padx=20, pady=10)
    
    examples_title = ctk.CTkLabel(examples_frame, text="Examples:", font=("Arial", 14, "bold"))
    examples_title.pack(pady=(10, 5))
    
    examples = [
        "netflix.com → https://www.netflix.com",
        "amazon.com → https://www.amazon.com", 
        "chase.com → https://www.chase.com",
        "geico.com → https://www.geico.com",
        "www.netflix.com → https://www.netflix.com",
        "https://netflix.com → (no change, already formatted)"
    ]
    
    for example in examples:
        example_label = ctk.CTkLabel(examples_frame, text=f"• {example}", font=("Arial", 11))
        example_label.pack(anchor="w", padx=20, pady=2)
    
    # Add instructions
    instructions = ctk.CTkLabel(
        frame, 
        text="Instructions:\n"
             "• Type a domain name (e.g., 'netflix.com')\n"
             "• Press Tab or click outside the field\n"
             "• Watch it auto-format to 'https://www.netflix.com'\n"
             "• Also works with dropdown suggestions\n"
             "• Already formatted URLs won't change",
        font=("Arial", 12),
        justify="left"
    )
    instructions.pack(pady=20)
    
    # Add a test button
    def test_formatting():
        """Test the formatting with a sample domain."""
        entry.set("example.com")
        entry._auto_format_url()
    
    test_button = ctk.CTkButton(
        frame, 
        text="Test: example.com", 
        command=test_formatting,
        width=150
    )
    test_button.pack(pady=10)
    
    # Add a close button
    close_button = ctk.CTkButton(
        frame, 
        text="Close", 
        command=root.destroy,
        width=100
    )
    close_button.pack(pady=20)
    
    print("✅ URL Auto-Format Demo started!")
    print("   - Type 'netflix.com' and press Tab to see auto-formatting")
    print("   - The URL will become 'https://www.netflix.com'")
    print("   - Works with any domain name")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    test_url_autoformat() 