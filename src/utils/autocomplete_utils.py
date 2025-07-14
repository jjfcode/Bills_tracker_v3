"""
Auto-complete utilities for Bills Tracker v3.

This module provides auto-complete functionality for various fields,
particularly the web page field with common bill website suggestions.
"""

import re
from typing import List, Optional, Dict, Any
from tkinter import ttk
import tkinter as tk
import customtkinter as ctk


class WebsiteAutoComplete:
    """
    Auto-complete functionality for website URLs.
    
    Provides suggestions for common bill websites and handles
    URL formatting and validation.
    """
    
    # Common bill websites organized by category
    COMMON_WEBSITES = {
        "Utilities": [
            "https://www.dominionenergy.com",
            "https://www.pge.com",
            "https://www.sce.com",
            "https://www.coned.com",
            "https://www.nationalgrid.com",
            "https://www.eversource.com",
            "https://www.duke-energy.com",
            "https://www.southerncompany.com",
            "https://www.exeloncorp.com",
            "https://www.ameren.com"
        ],
        "Internet & Phone": [
            "https://www.comcast.com",
            "https://www.verizon.com",
            "https://www.att.com",
            "https://www.spectrum.com",
            "https://www.cox.com",
            "https://www.optimum.com",
            "https://www.frontier.com",
            "https://www.centurylink.com",
            "https://www.xfinity.com",
            "https://www.mediacom.com"
        ],
        "Entertainment": [
            "https://www.netflix.com",
            "https://www.hulu.com",
            "https://www.disneyplus.com",
            "https://www.hbomax.com",
            "https://www.paramountplus.com",
            "https://www.peacocktv.com",
            "https://www.apple.com/apple-tv-plus",
            "https://www.amazon.com/prime",
            "https://www.youtube.com/premium",
            "https://www.spotify.com"
        ],
        "Insurance": [
            "https://www.statefarm.com",
            "https://www.allstate.com",
            "https://www.geico.com",
            "https://www.progressive.com",
            "https://www.farmers.com",
            "https://www.nationwide.com",
            "https://www.libertymutual.com",
            "https://www.americanfamily.com",
            "https://www.usaa.com",
            "https://www.travelers.com"
        ],
        "Banking & Credit": [
            "https://www.chase.com",
            "https://www.bankofamerica.com",
            "https://www.wellsfargo.com",
            "https://www.citibank.com",
            "https://www.capitalone.com",
            "https://www.discover.com",
            "https://www.americanexpress.com",
            "https://www.mastercard.com",
            "https://www.visa.com",
            "https://www.paypal.com"
        ],
        "Healthcare": [
            "https://www.bluecrossblueshield.com",
            "https://www.aetna.com",
            "https://www.cigna.com",
            "https://www.unitedhealthgroup.com",
            "https://www.humana.com",
            "https://www.kaiserpermanente.org",
            "https://www.anthem.com",
            "https://www.molinahealthcare.com",
            "https://www.centene.com",
            "https://www.healthnet.com"
        ],
        "Shopping": [
            "https://www.amazon.com",
            "https://www.walmart.com",
            "https://www.target.com",
            "https://www.bestbuy.com",
            "https://www.homedepot.com",
            "https://www.lowes.com",
            "https://www.costco.com",
            "https://www.samsclub.com",
            "https://www.ebay.com",
            "https://www.etsy.com"
        ],
        "Transportation": [
            "https://www.uber.com",
            "https://www.lyft.com",
            "https://www.hertz.com",
            "https://www.enterprise.com",
            "https://www.avis.com",
            "https://www.budget.com",
            "https://www.zipcar.com",
            "https://www.turo.com",
            "https://www.amtrak.com",
            "https://www.greyhound.com"
        ]
    }
    
    @classmethod
    def get_all_websites(cls) -> List[str]:
        """
        Get all common websites as a flat list.
        
        Returns:
            List[str]: All common website URLs.
        """
        all_websites = []
        for category_websites in cls.COMMON_WEBSITES.values():
            all_websites.extend(category_websites)
        return all_websites
    
    @classmethod
    def get_websites_by_category(cls, category: str) -> List[str]:
        """
        Get websites for a specific category.
        
        Args:
            category (str): The category name.
            
        Returns:
            List[str]: Websites for the specified category.
        """
        return cls.COMMON_WEBSITES.get(category, [])
    
    @classmethod
    def search_websites(cls, query: str, limit: int = 10) -> List[str]:
        """
        Search websites based on a query string.
        
        Args:
            query (str): The search query.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[str]: Matching website URLs.
        """
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for category, websites in cls.COMMON_WEBSITES.items():
            for website in websites:
                # Check if query matches domain or category
                if (query_lower in website.lower() or 
                    query_lower in category.lower()):
                    matches.append(website)
                    if len(matches) >= limit:
                        break
            if len(matches) >= limit:
                break
        
        return matches[:limit]
    
    @classmethod
    def format_url(cls, url: str) -> str:
        """
        Format a URL to ensure it has proper protocol.
        
        Args:
            url (str): The URL to format.
            
        Returns:
            str: Properly formatted URL.
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Add https:// if no protocol is specified
        if not re.match(r'^https?://', url):
            url = f"https://{url}"
        
        return url
    
    @classmethod
    def extract_domain(cls, url: str) -> str:
        """
        Extract domain name from a URL.
        
        Args:
            url (str): The URL to extract domain from.
            
        Returns:
            str: The domain name.
        """
        if not url:
            return ""
        
        # Remove protocol
        domain = re.sub(r'^https?://', '', url)
        
        # Remove path and query parameters
        domain = domain.split('/')[0]
        
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        
        return domain


class AutoCompleteEntry:
    """
    Custom entry widget with auto-complete functionality.
    
    Provides a dropdown with suggestions as the user types.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the auto-complete entry widget.
        
        Args:
            parent: The parent widget.
            **kwargs: Additional arguments for the entry widget.
        """
        self.parent = parent
        self.entry = ctk.CTkEntry(parent, **kwargs)
        self.suggestions = []
        self.current_suggestion = 0
        self.listbox = None
        self.is_listbox_visible = False
        
        # Bind events
        self.entry.bind('<KeyRelease>', self._on_key_release)
        self.entry.bind('<KeyPress>', self._on_key_press)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_return)
        self.entry.bind('<Escape>', self._on_escape)
        
        # Auto-complete data
        self.auto_complete_data = []
        self.set_auto_complete_data(WebsiteAutoComplete.get_all_websites())
    
    def set_auto_complete_data(self, data: List[str]):
        """
        Set the auto-complete data.
        
        Args:
            data (List[str]): List of strings to suggest.
        """
        self.auto_complete_data = data
    
    def _on_key_release(self, event):
        """Handle key release events."""
        if event.keysym in ['Up', 'Down', 'Return', 'Escape']:
            return
        
        self._show_suggestions()
        
        # Auto-format URL when user finishes typing (space, tab, or focus out)
        if event.keysym in ['space', 'Tab']:
            self._auto_format_url()
    
    def _on_key_press(self, event):
        """Handle key press events."""
        if event.keysym == 'Up':
            self._select_previous()
            return 'break'
        elif event.keysym == 'Down':
            self._select_next()
            return 'break'
    
    def _on_focus_out(self, event):
        """Handle focus out events."""
        self._hide_suggestions()
        self._auto_format_url()
    
    def _on_return(self, event):
        """Handle return key events."""
        if self.is_listbox_visible and self.suggestions:
            self._select_current()
        return 'break'
    
    def _auto_format_url(self):
        """Automatically format the URL when user finishes typing."""
        current_text = self.entry.get().strip()
        
        if not current_text:
            return
        
        # Don't format if it already has a protocol
        if re.match(r'^https?://', current_text):
            return
        
        # Don't format if it's already a complete URL
        if current_text.startswith('www.'):
            formatted_url = WebsiteAutoComplete.format_url(current_text)
        else:
            # Add www. prefix and format
            formatted_url = WebsiteAutoComplete.format_url(f"www.{current_text}")
        
        # Only update if the formatted URL is different
        if formatted_url != current_text:
            self.entry.delete(0, tk.END)
            self.entry.insert("0", formatted_url)
    
    def _on_escape(self, event):
        """Handle escape key events."""
        self._hide_suggestions()
        return 'break'
    
    def _show_suggestions(self):
        """Show suggestion dropdown."""
        current_text = self.entry.get()
        
        if len(current_text) < 2:
            self._hide_suggestions()
            return
        
        # Filter suggestions
        self.suggestions = [
            item for item in self.auto_complete_data
            if current_text.lower() in item.lower()
        ][:10]  # Limit to 10 suggestions
        
        if not self.suggestions:
            self._hide_suggestions()
            return
        
        # Create or update listbox
        if not self.listbox:
            self.listbox = tk.Listbox(
                self.parent,
                height=min(len(self.suggestions), 6),
                width=self.entry.winfo_width()
            )
            self.listbox.bind('<Button-1>', self._on_listbox_click)
            self.listbox.bind('<Return>', self._on_return)
        
        # Position listbox
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.listbox.place(x=x, y=y)
        
        # Populate listbox
        self.listbox.delete(0, tk.END)
        for suggestion in self.suggestions:
            self.listbox.insert(tk.END, suggestion)
        
        self.is_listbox_visible = True
        self.current_suggestion = 0
    
    def _hide_suggestions(self):
        """Hide suggestion dropdown."""
        if self.listbox:
            self.listbox.place_forget()
            self.is_listbox_visible = False
    
    def _select_next(self):
        """Select next suggestion."""
        if not self.is_listbox_visible or not self.suggestions:
            return
        
        self.current_suggestion = (self.current_suggestion + 1) % len(self.suggestions)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_suggestion)
        self.listbox.see(self.current_suggestion)
    
    def _select_previous(self):
        """Select previous suggestion."""
        if not self.is_listbox_visible or not self.suggestions:
            return
        
        self.current_suggestion = (self.current_suggestion - 1) % len(self.suggestions)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(self.current_suggestion)
        self.listbox.see(self.current_suggestion)
    
    def _select_current(self):
        """Select current suggestion."""
        if not self.is_listbox_visible or not self.suggestions:
            return
        
        selected = self.suggestions[self.current_suggestion]
        self.entry.delete(0, tk.END)
        self.entry.insert("0", selected)
        self._hide_suggestions()
    
    def _on_listbox_click(self, event):
        """Handle listbox click events."""
        if not self.listbox:
            return
        
        selection = self.listbox.curselection()
        if selection:
            self.current_suggestion = selection[0]
            self._select_current()
    
    def get(self) -> str:
        """Get the current value."""
        return self.entry.get()
    
    def set(self, value: str):
        """Set the current value."""
        self.entry.delete(0, tk.END)
        self.entry.insert("0", str(value or ""))
    
    def grid(self, **kwargs):
        """Grid the entry widget."""
        return self.entry.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the entry widget."""
        return self.entry.pack(**kwargs)
    
    def place(self, **kwargs):
        """Place the entry widget."""
        return self.entry.place(**kwargs)


def create_website_autocomplete_entry(parent, **kwargs) -> AutoCompleteEntry:
    """
    Create an auto-complete entry widget for websites.
    
    Args:
        parent: The parent widget.
        **kwargs: Additional arguments for the entry widget.
        
    Returns:
        AutoCompleteEntry: Configured auto-complete entry widget.
    """
    entry = AutoCompleteEntry(parent, **kwargs)
    entry.set_auto_complete_data(WebsiteAutoComplete.get_all_websites())
    return entry 