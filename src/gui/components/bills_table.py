"""
Bills Table Component for Bills Tracker application.
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional
from ...utils.constants import *
from ...utils.ui_helpers import apply_table_styling, create_styled_button, create_styled_label
from ...core.services import BillService


class BillsTable(ctk.CTkFrame):
    """Enhanced bills table with multi-select, pagination, and sorting."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # State variables
        self.bills_data = []
        self.filtered_bills = []
        self.selected_bills = set()
        self.current_page = 1
        self.items_per_page = DEFAULT_ITEMS_PER_PAGE
        self.sort_column = "due_date"
        self.sort_reverse = False
        
        # Callbacks
        self.on_bill_selected = None
        self.on_bill_edited = None
        self.on_bill_deleted = None
        self.on_bulk_delete = None
        self.on_paid_toggled = None
        
        self._setup_ui()
        self._setup_table()
    
    def _setup_ui(self):
        """Setup the UI components."""
        # Table frame
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=SPACING_SM, pady=SPACING_SM)
        
        # Action buttons frame
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(fill="x", padx=SPACING_SM, pady=(0, SPACING_SM))
        
        # Add button
        self.add_btn = create_styled_button(
            self.action_frame, "Add Bill", self._on_add_bill,
            fg_color=SUCCESS_COLOR
        )
        self.add_btn.pack(side="left", padx=SPACING_SM)
        
        # Edit button
        self.edit_btn = create_styled_button(
            self.action_frame, "Edit", self._on_edit_bill,
            fg_color=PRIMARY_COLOR
        )
        self.edit_btn.pack(side="left", padx=SPACING_SM)
        
        # Delete button
        self.delete_btn = create_styled_button(
            self.action_frame, "Delete", self._on_delete_bill,
            fg_color=ERROR_COLOR
        )
        self.delete_btn.pack(side="left", padx=SPACING_SM)
        
        # Bulk delete button
        self.bulk_delete_btn = create_styled_button(
            self.action_frame, "Delete Selected (0)", self._on_bulk_delete_bills,
            fg_color=ERROR_COLOR
        )
        self.bulk_delete_btn.pack(side="left", padx=SPACING_SM)
        
        # Refresh button
        self.refresh_btn = create_styled_button(
            self.action_frame, "Refresh", self._on_refresh
        )
        self.refresh_btn.pack(side="right", padx=SPACING_SM)
        
        # Export button
        self.export_btn = create_styled_button(
            self.action_frame, "Export", self._on_export
        )
        self.export_btn.pack(side="right", padx=SPACING_SM)
        
        # Import button
        self.import_btn = create_styled_button(
            self.action_frame, "Import", self._on_import
        )
        self.import_btn.pack(side="right", padx=SPACING_SM)
    
    def _setup_table(self):
        """Setup the treeview table."""
        # Create treeview with scrollbars
        tree_frame = ctk.CTkFrame(self.table_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Treeview
        columns = (
            "select", "name", "due_date", "amount", "category", "payment_method", 
            "billing_cycle", "paid", "web_page", "company_email", "support_phone"
        )
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("select", text="☐")
        self.tree.column("select", width=30, anchor="center")
        
        self.tree.heading("name", text="Bill Name")
        self.tree.column("name", width=150, anchor="w")
        
        self.tree.heading("due_date", text="Due Date")
        self.tree.column("due_date", width=100, anchor="center")
        
        self.tree.heading("amount", text="Amount")
        self.tree.column("amount", width=80, anchor="e")
        
        self.tree.heading("category", text="Category")
        self.tree.column("category", width=100, anchor="w")
        
        self.tree.heading("payment_method", text="Payment Method")
        self.tree.column("payment_method", width=120, anchor="w")
        
        self.tree.heading("billing_cycle", text="Billing Cycle")
        self.tree.column("billing_cycle", width=100, anchor="w")
        
        self.tree.heading("paid", text="Paid")
        self.tree.column("paid", width=60, anchor="center")
        
        self.tree.heading("web_page", text="Website")
        self.tree.column("web_page", width=100, anchor="w")
        
        self.tree.heading("company_email", text="Email")
        self.tree.column("company_email", width=120, anchor="w")
        
        self.tree.heading("support_phone", text="Phone")
        self.tree.column("support_phone", width=100, anchor="w")
        
        # Apply styling
        apply_table_styling(self.tree)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Button-1>", self._on_table_click)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_enter_key)
    
    def set_callbacks(self, on_bill_selected=None, on_bill_edited=None, 
                     on_bill_deleted=None, on_bulk_delete=None, on_paid_toggled=None):
        """Set callback functions."""
        self.on_bill_selected = on_bill_selected
        self.on_bill_edited = on_bill_edited
        self.on_bill_deleted = on_bill_deleted
        self.on_bulk_delete = on_bulk_delete
        self.on_paid_toggled = on_paid_toggled
    
    def load_bills(self, bills: List[Dict[str, Any]]):
        """Load bills data into the table."""
        self.bills_data = bills
        self.filtered_bills = bills.copy()
        self._populate_table()
    
    def _populate_table(self):
        """Populate the table with current data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate pagination
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_bills = self.filtered_bills[start_idx:end_idx]
        
        # Add items to table
        for i, bill in enumerate(page_bills):
            item_id = f"item_{i}"
            
            # Determine selection status
            is_selected = bill['id'] in self.selected_bills
            select_text = "☑" if is_selected else "☐"
            
            # Determine paid status
            paid_text = "✓" if bill.get('paid', False) else "✗"
            paid_color = SUCCESS_COLOR if bill.get('paid', False) else ERROR_COLOR
            
            # Insert item
            self.tree.insert("", "end", item_id, values=(
                select_text,
                bill.get('name', ''),
                bill.get('due_date', ''),
                bill.get('formatted_amount', ''),
                bill.get('category_name', 'Uncategorized'),
                bill.get('payment_method_name', 'Not Set'),
                bill.get('billing_cycle', ''),
                paid_text,
                bill.get('web_page', ''),
                bill.get('company_email', ''),
                bill.get('support_phone', '')
            ))
            
            # Apply row styling
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.item(item_id, tags=(tag,))
            
            # Store bill ID in item
            self.tree.set(item_id, "bill_id", bill['id'])
        
        # Update bulk delete button
        self._update_bulk_actions()
    
    def _on_table_click(self, event):
        """Handle table click events."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            self._sort_by_column(column)
        elif region == "cell":
            item = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            
            if column == "#1":  # Select column
                self._toggle_bill_selection(item)
            elif column == "#8":  # Paid column
                self._toggle_paid_status(item)
    
    def _on_double_click(self, event):
        """Handle double-click events."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item and self.on_bill_edited:
            bill_id = self.tree.set(item, "bill_id")
            self.on_bill_edited(bill_id)
    
    def _on_enter_key(self, event):
        """Handle Enter key events."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item and self.on_bill_edited:
            bill_id = self.tree.set(item, "bill_id")
            self.on_bill_edited(bill_id)
    
    def _sort_by_column(self, column):
        """Sort table by column."""
        column_map = {
            "#1": "select",
            "#2": "name", 
            "#3": "due_date",
            "#4": "amount",
            "#5": "category",
            "#6": "payment_method",
            "#7": "billing_cycle",
            "#8": "paid"
        }
        
        sort_field = column_map.get(column, "due_date")
        
        if self.sort_column == sort_field:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = sort_field
            self.sort_reverse = False
        
        # Sort the data
        self.filtered_bills.sort(
            key=lambda x: x.get(sort_field, ""),
            reverse=self.sort_reverse
        )
        
        # Reset to first page and repopulate
        self.current_page = 1
        self._populate_table()
    
    def _toggle_bill_selection(self, item):
        """Toggle selection of a bill."""
        bill_id = self.tree.set(item, "bill_id")
        
        if bill_id in self.selected_bills:
            self.selected_bills.remove(bill_id)
            self.tree.set(item, "select", "☐")
        else:
            self.selected_bills.add(bill_id)
            self.tree.set(item, "select", "☑")
        
        self._update_bulk_actions()
    
    def _toggle_paid_status(self, item):
        """Toggle paid status of a bill."""
        bill_id = self.tree.set(item, "bill_id")
        if self.on_paid_toggled:
            self.on_paid_toggled(bill_id)
    
    def _update_bulk_actions(self):
        """Update bulk action buttons."""
        count = len(self.selected_bills)
        self.bulk_delete_btn.configure(text=f"Delete Selected ({count})")
        self.bulk_delete_btn.configure(state="normal" if count > 0 else "disabled")
    
    def _on_add_bill(self):
        """Handle add bill button click."""
        # This will be handled by the parent component
        pass
    
    def _on_edit_bill(self):
        """Handle edit bill button click."""
        selection = self.tree.selection()
        if selection and self.on_bill_edited:
            item = selection[0]
            bill_id = self.tree.set(item, "bill_id")
            self.on_bill_edited(bill_id)
    
    def _on_delete_bill(self):
        """Handle delete bill button click."""
        selection = self.tree.selection()
        if selection and self.on_bill_deleted:
            item = selection[0]
            bill_id = self.tree.set(item, "bill_id")
            self.on_bill_deleted(bill_id)
    
    def _on_bulk_delete_bills(self):
        """Handle bulk delete button click."""
        if self.selected_bills and self.on_bulk_delete:
            self.on_bulk_delete(list(self.selected_bills))
    
    def _on_refresh(self):
        """Handle refresh button click."""
        self.load_bills(BillService.get_all_bills())
    
    def _on_export(self):
        """Handle export button click."""
        # This will be handled by the parent component
        pass
    
    def _on_import(self):
        """Handle import button click."""
        # This will be handled by the parent component
        pass
    
    def set_page(self, page: int):
        """Set current page."""
        self.current_page = page
        self._populate_table()
    
    def set_items_per_page(self, items: int):
        """Set items per page."""
        self.items_per_page = items
        self.current_page = 1
        self._populate_table()
    
    def clear_selection(self):
        """Clear all selections."""
        self.selected_bills.clear()
        self._populate_table()
    
    def get_selected_bills(self) -> List[int]:
        """Get list of selected bill IDs."""
        return list(self.selected_bills)
    
    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return max(1, (len(self.filtered_bills) + self.items_per_page - 1) // self.items_per_page)
    
    def get_current_page(self) -> int:
        """Get current page number."""
        return self.current_page 