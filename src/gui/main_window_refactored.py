"""
Refactored Main Window for Bills Tracker application.
This version uses the new modular architecture with services and components.
"""

import customtkinter as ctk
from tkinter import ttk
import sys
import os
from typing import List, Dict, Any, Optional

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

from ..core.db import initialize_database
from ..core.services import BillService, CategoryService, PaymentMethodService, AnalyticsService
from ..core.config_manager import config_manager
from ..core.auth import auth_manager, AuthenticationError
from ..core.reminder_service import ReminderService
from ..utils.constants import *
from ..utils.ui_helpers import show_popup, show_confirmation_dialog, center_window
from ..utils.helpers import export_to_csv, import_from_csv
from .login_dialog import LoginDialog, ChangePasswordDialog
from .notification_dialog import NotificationManager
from .components.bills_table import BillsTable


class MainWindow(ctk.CTk):
    """Refactored main window with modular architecture."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize services
        self.bill_service = BillService()
        self.category_service = CategoryService()
        self.payment_service = PaymentMethodService()
        self.analytics_service = AnalyticsService()
        
        # State variables
        self.current_user = None
        self.current_view = "bills"
        self.bills_data = []
        self.categories_data = []
        self.payment_methods_data = []
        
        # UI components
        self.bills_table = None
        self.notification_manager = None
        self.reminder_service = None
        
        # Setup window
        self._setup_window()
        self._setup_ui()
        self._setup_services()
        
        # Load initial data
        self._load_data()
    
    def _setup_window(self):
        """Setup the main window."""
        self.title("Bills Tracker v3")
        
        # Get saved window size
        window_size = config_manager.get_window_size()
        self.geometry(f"{window_size['width']}x{window_size['height']}")
        
        # Set minimum size
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Check authentication
        if not self._check_authentication():
            return
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area
        self._create_main_content()
        
        # Create status bar
        self._create_status_bar()
    
    def _setup_services(self):
        """Setup background services."""
        # Setup notification manager
        self.notification_manager = NotificationManager(self)
        
        # Setup reminder service
        self.reminder_service = ReminderService(
            check_interval=config_manager.get_check_interval(),
            notification_callback=self._handle_reminder_notification
        )
        
        if config_manager.get_notifications_enabled():
            self.reminder_service.start()
    
    def _check_authentication(self) -> bool:
        """Check if user is authenticated."""
        try:
            if auth_manager.is_authenticated():
                self.current_user = auth_manager.get_current_user()
                return True
            else:
                self._show_login_dialog()
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def _show_login_dialog(self):
        """Show login dialog."""
        login_dialog = LoginDialog(self)
        login_dialog.grab_set()
        self.wait_window(login_dialog)
        
        if auth_manager.is_authenticated():
            self.current_user = auth_manager.get_current_user()
            self._setup_ui()
        else:
            self.quit()
    
    def _create_sidebar(self):
        """Create the sidebar navigation."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Bills Tracker", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.bills_btn = ctk.CTkButton(
            self.sidebar, 
            text="Bills", 
            command=self._show_bills_view,
            fg_color=PRIMARY_COLOR
        )
        self.bills_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.categories_btn = ctk.CTkButton(
            self.sidebar, 
            text="Categories", 
            command=self._show_categories_view
        )
        self.categories_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.settings_btn = ctk.CTkButton(
            self.sidebar, 
            text="Settings", 
            command=self._show_settings_view
        )
        self.settings_btn.grid(row=3, column=0, padx=20, pady=10)
        
        # User section
        user_frame = ctk.CTkFrame(self.sidebar)
        user_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        if self.current_user:
            user_label = ctk.CTkLabel(
                user_frame, 
                text=f"User: {self.current_user.get('username', 'Unknown')}",
                font=ctk.CTkFont(size=12)
            )
            user_label.pack(pady=5)
        
        logout_btn = ctk.CTkButton(
            user_frame, 
            text="Logout", 
            command=self._logout,
            fg_color=ERROR_COLOR
        )
        logout_btn.pack(pady=5)
    
    def _create_main_content(self):
        """Create the main content area."""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Show bills view by default
        self._show_bills_view()
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text="Ready",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Statistics
        self.stats_label = ctk.CTkLabel(
            self.status_bar, 
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.stats_label.pack(side="right", padx=10, pady=5)
    
    def _load_data(self):
        """Load initial data."""
        try:
            self.bills_data = self.bill_service.get_all_bills()
            self.categories_data = self.category_service.get_all_categories()
            self.payment_methods_data = self.payment_service.get_all_payment_methods()
            
            self._update_status()
        except Exception as e:
            show_popup(self, "Error", f"Failed to load data: {str(e)}", ERROR_COLOR)
    
    def _show_bills_view(self):
        """Show the bills view."""
        self.current_view = "bills"
        self._clear_main_content()
        
        # Create bills table component
        self.bills_table = BillsTable(self.main_frame)
        self.bills_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Set callbacks
        self.bills_table.set_callbacks(
            on_bill_edited=self._edit_bill,
            on_bill_deleted=self._delete_bill,
            on_bulk_delete=self._bulk_delete_bills,
            on_paid_toggled=self._toggle_paid_status
        )
        
        # Load bills data
        self.bills_table.load_bills(self.bills_data)
        
        # Update navigation
        self._update_navigation()
    
    def _show_categories_view(self):
        """Show the categories view."""
        self.current_view = "categories"
        self._clear_main_content()
        
        # Create categories table (simplified for now)
        categories_frame = ctk.CTkFrame(self.main_frame)
        categories_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Categories table implementation would go here
        # For now, just show a placeholder
        placeholder = ctk.CTkLabel(
            categories_frame, 
            text="Categories View\n(To be implemented)",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(expand=True)
        
        self._update_navigation()
    
    def _show_settings_view(self):
        """Show the settings view."""
        self.current_view = "settings"
        self._clear_main_content()
        
        # Create settings view (simplified for now)
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Settings implementation would go here
        # For now, just show a placeholder
        placeholder = ctk.CTkLabel(
            settings_frame, 
            text="Settings View\n(To be implemented)",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(expand=True)
        
        self._update_navigation()
    
    def _clear_main_content(self):
        """Clear the main content area."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def _update_navigation(self):
        """Update navigation button states."""
        # Reset all buttons
        for btn in [self.bills_btn, self.categories_btn, self.settings_btn]:
            btn.configure(fg_color=("gray75", "gray25"))
        
        # Highlight current view
        if self.current_view == "bills":
            self.bills_btn.configure(fg_color=PRIMARY_COLOR)
        elif self.current_view == "categories":
            self.categories_btn.configure(fg_color=PRIMARY_COLOR)
        elif self.current_view == "settings":
            self.settings_btn.configure(fg_color=PRIMARY_COLOR)
    
    def _update_status(self):
        """Update status bar with current statistics."""
        try:
            stats = self.analytics_service.get_bill_statistics()
            
            status_text = f"Total Bills: {stats['total_bills']} | "
            status_text += f"Paid: {stats['paid_bills']} | "
            status_text += f"Unpaid: {stats['unpaid_bills']} | "
            status_text += f"Overdue: {stats['overdue_bills']}"
            
            self.status_label.configure(text=status_text)
            
            # Update stats label
            total_amount = stats.get('total_amount', 0)
            stats_text = f"Total Amount: ${total_amount:.2f}"
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            self.status_label.configure(text=f"Error updating status: {str(e)}")
    
    def _edit_bill(self, bill_id: int):
        """Edit a bill."""
        # Find the bill data
        bill = next((b for b in self.bills_data if b['id'] == bill_id), None)
        if not bill:
            show_popup(self, "Error", "Bill not found", ERROR_COLOR)
            return
        
        # Create edit dialog (simplified for now)
        show_popup(self, "Edit Bill", f"Edit bill: {bill['name']}\n(To be implemented)")
    
    def _delete_bill(self, bill_id: int):
        """Delete a bill."""
        # Find the bill data
        bill = next((b for b in self.bills_data if b['id'] == bill_id), None)
        if not bill:
            show_popup(self, "Error", "Bill not found", ERROR_COLOR)
            return
        
        def confirm_delete():
            success, error = self.bill_service.delete_bill(bill_id)
            if success:
                self._load_data()
                if self.bills_table:
                    self.bills_table.load_bills(self.bills_data)
                show_popup(self, "Success", "Bill deleted successfully", SUCCESS_COLOR)
            else:
                show_popup(self, "Error", f"Failed to delete bill: {error}", ERROR_COLOR)
        
        show_confirmation_dialog(
            self, 
            "Delete Bill", 
            f"Are you sure you want to delete '{bill['name']}'?",
            confirm_delete
        )
    
    def _bulk_delete_bills(self, bill_ids: List[int]):
        """Delete multiple bills."""
        def confirm_bulk_delete():
            success, error = self.bill_service.bulk_delete_bills(bill_ids)
            if success:
                self._load_data()
                if self.bills_table:
                    self.bills_table.load_bills(self.bills_data)
                show_popup(self, "Success", error, SUCCESS_COLOR)
            else:
                show_popup(self, "Error", f"Failed to delete bills: {error}", ERROR_COLOR)
        
        show_confirmation_dialog(
            self,
            "Bulk Delete",
            f"Are you sure you want to delete {len(bill_ids)} bills?",
            confirm_bulk_delete
        )
    
    def _toggle_paid_status(self, bill_id: int):
        """Toggle paid status of a bill."""
        # Find the bill data
        bill = next((b for b in self.bills_data if b['id'] == bill_id), None)
        if not bill:
            return
        
        success, error = self.bill_service.toggle_paid_status(bill_id, bill.get('paid', False))
        if success:
            self._load_data()
            if self.bills_table:
                self.bills_table.load_bills(self.bills_data)
        else:
            show_popup(self, "Error", f"Failed to update paid status: {error}", ERROR_COLOR)
    
    def _handle_reminder_notification(self, notification_data: Dict[str, Any]):
        """Handle reminder notifications."""
        if self.notification_manager:
            self.notification_manager.show_notification(notification_data)
    
    def _logout(self):
        """Logout current user."""
        try:
            auth_manager.logout()
            self.current_user = None
            show_popup(self, "Success", "Logged out successfully", SUCCESS_COLOR)
            self._show_login_dialog()
        except Exception as e:
            show_popup(self, "Error", f"Logout failed: {str(e)}", ERROR_COLOR)
    
    def _on_close(self):
        """Handle window close event."""
        try:
            # Save window size
            width = self.winfo_width()
            height = self.winfo_height()
            config_manager.set_window_size(width, height)
            
            # Stop services
            if self.reminder_service:
                self.reminder_service.stop()
            
            # Destroy window
            self.destroy()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.destroy()


def main():
    """Main entry point for the application."""
    # Initialize database
    initialize_database()
    
    # Create and run application
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main() 