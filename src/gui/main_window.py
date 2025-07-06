import customtkinter as ctk  # noqa
from tkinter import ttk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from ..core.db import fetch_all_bills, insert_bill, update_bill, delete_bill, fetch_all_categories, fetch_all_payment_methods
from datetime import datetime, timedelta
from tkinter import StringVar
from tkinter import IntVar
import re
import csv
from tkinter import filedialog
from tkcalendar import DateEntry  # noqa
from tkinter import messagebox
from .icon_utils import icon_manager, ICON_ADD, ICON_EDIT, ICON_DELETE, ICON_SAVE, ICON_CANCEL, ICON_SEARCH, ICON_CALENDAR, ICON_EXPORT, ICON_IMPORT, ICON_REFRESH, ICON_SETTINGS, ICON_CATEGORIES, ICON_BILLS, ICON_APPLY, ICON_CLEAR
from .validation import BillValidator, CategoryValidator, ValidationError, validate_field_in_real_time
from .notification_dialog import NotificationManager
from ..core.reminder_service import ReminderService
from ..core.auth import auth_manager, AuthenticationError
from .login_dialog import LoginDialog, ChangePasswordDialog
from customtkinter import CTkComboBox

BILLING_CYCLES = [
    "weekly", "bi-weekly", "monthly", "quarterly", "semi-annually", "annually", "one-time"
]
REMINDER_DAYS = [1, 3, 5, 7, 10, 14, 30]

# === UI THEME CONSTANTS ===
PRIMARY_COLOR = "#1f538d"
SECONDARY_COLOR = "#4ecdc4"
ACCENT_COLOR = "#ff6b6b"
BACKGROUND_COLOR = "#f7f9fa"
TEXT_COLOR = "#222831"
SUCCESS_COLOR = "#4bb543"
ERROR_COLOR = "#e74c3c"
WARNING_COLOR = "#ffa500"
URGENT_COLOR = "#ff0000"
DISABLED_COLOR = "#b0b0b0"

SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24

def show_popup(master, title, message, color="green"):
    """
    Display a popup dialog with a message.

    Args:
        master: The parent window for the popup.
        title (str): The title of the popup window.
        message (str): The message to display in the popup.
        color (str): The color of the message text (default: "green").
    """
    try:
        popup = ctk.CTkToplevel(master)
        popup.title(title)
        popup.geometry("350x120")
        
        def close_popup():
            try:
                if popup.winfo_exists():
                    popup.destroy()
            except:
                pass
        
        label = ctk.CTkLabel(popup, text=message, text_color=color, font=("Arial", 14))
        label.pack(pady=20)
        ctk.CTkButton(popup, text="OK", command=close_popup).pack(pady=10)
        
        # Use after() to delay the focus operations
        def set_focus():
            try:
                if popup.winfo_exists():
                    popup.lift()
                    popup.focus_force()
                    popup.grab_set()
            except:
                pass
        
        popup.after(100, set_focus)
        
    except Exception as e:
        # If popup creation fails, just print the message to console
        print(f"Popup Error: {title} - {message}")

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_REGEX = r"^[\d\-\+\(\)\s]+$"

class DateSelectorFrame(ctk.CTkFrame):
    """
    Custom frame for date selection with calendar and quick options.

    Provides a date entry field with a calendar button for easy date selection.
    Supports both calendar dialog and fallback simple date picker.
    """
    
    def __init__(self, master, **kwargs):
        """
        Initialize the DateSelectorFrame.

        Args:
            master: The parent widget.
            **kwargs: Additional keyword arguments for CTkFrame.
        """
        super().__init__(master, **kwargs)
        self.selected_date = StringVar()
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Setup the date selector UI with entry field and calendar button.
        """
        # Main date entry with calendar button
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)
        
        # Date entry
        self.date_entry = ctk.CTkEntry(date_frame, textvariable=self.selected_date, placeholder_text="YYYY-MM-DD", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING_SM))
        
        # Calendar button
        self.calendar_btn = ctk.CTkButton(date_frame, text="📅", width=40, command=self._show_calendar, fg_color=PRIMARY_COLOR, text_color="white")
        self.calendar_btn.pack(side="right")
    
    def _show_calendar(self):
        """
        Show calendar dialog for date selection using tkcalendar.
        Falls back to simple date picker if tkcalendar is not available.
        """
        try:
            # Create calendar dialog
            calendar_dialog = ctk.CTkToplevel(self)
            calendar_dialog.title("Select Date")
            calendar_dialog.geometry("300x250")
            calendar_dialog.transient(self.winfo_toplevel())
            calendar_dialog.grab_set()
            
            # Center the dialog
            calendar_dialog.update_idletasks()
            x = (calendar_dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (calendar_dialog.winfo_screenheight() // 2) - (250 // 2)
            calendar_dialog.geometry(f"300x250+{x}+{y}")
            
            # Create calendar widget
            calendar = DateEntry(calendar_dialog, width=20, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            calendar.pack(pady=SPACING_MD)
            
            # Buttons
            button_frame = ctk.CTkFrame(calendar_dialog)
            button_frame.pack(pady=SPACING_MD)
            
            def on_select():
                self.selected_date.set(calendar.get_date().strftime('%Y-%m-%d'))
                calendar_dialog.destroy()
            
            def on_cancel():
                calendar_dialog.destroy()
            
            ctk.CTkButton(button_frame, text="Select", command=on_select).pack(side="left", padx=SPACING_SM)
            ctk.CTkButton(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=SPACING_SM)
            
        except Exception as e:
            # Fallback to simple date picker if tkcalendar is not available
            self._show_simple_date_picker()
    
    def _show_simple_date_picker(self):
        """
        Fallback simple date picker with year, month, and day dropdowns.
        """
        try:
            # Create simple date picker dialog
            picker_dialog = ctk.CTkToplevel(self)
            picker_dialog.title("Select Date")
            picker_dialog.geometry("250x200")
            picker_dialog.transient(self.winfo_toplevel())
            picker_dialog.grab_set()
            
            # Year selection
            year_frame = ctk.CTkFrame(picker_dialog)
            year_frame.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkLabel(year_frame, text="Year:").pack(side="left")
            current_year = datetime.now().year
            year_var = StringVar(value=str(current_year))
            year_combo = ttk.Combobox(year_frame, textvariable=year_var, 
                                    values=[str(y) for y in range(current_year, current_year + 5)])
            year_combo.pack(side="right", padx=SPACING_SM)
            
            # Month selection
            month_frame = ctk.CTkFrame(picker_dialog)
            month_frame.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkLabel(month_frame, text="Month:").pack(side="left")
            month_var = StringVar(value=str(datetime.now().month))
            month_combo = ttk.Combobox(month_frame, textvariable=month_var,
                                     values=[str(m) for m in range(1, 13)])
            month_combo.pack(side="right", padx=SPACING_SM)
            
            # Day selection
            day_frame = ctk.CTkFrame(picker_dialog)
            day_frame.pack(fill="x", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkLabel(day_frame, text="Day:").pack(side="left")
            day_var = StringVar(value=str(datetime.now().day))
            day_combo = ttk.Combobox(day_frame, textvariable=day_var,
                                   values=[str(d) for d in range(1, 32)])
            day_combo.pack(side="right", padx=SPACING_SM)
            
            def on_select():
                try:
                    year = int(year_var.get())
                    month = int(month_var.get())
                    day = int(day_var.get())
                    date = datetime(year, month, day)
                    self.selected_date.set(date.strftime('%Y-%m-%d'))
                    picker_dialog.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Invalid date")
            
            def on_cancel():
                picker_dialog.destroy()
            
            # Buttons
            button_frame = ctk.CTkFrame(picker_dialog)
            button_frame.pack(pady=SPACING_MD)
            
            ctk.CTkButton(button_frame, text="Select", command=on_select).pack(side="left", padx=SPACING_SM)
            ctk.CTkButton(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=SPACING_SM)
            
        except Exception as e:
            print(f"Error creating date picker: {e}")
    

    
    def get_date(self):
        """
        Get the selected date as string.

        Returns:
            str: The selected date in YYYY-MM-DD format.
        """
        return self.selected_date.get()
    
    def set_date(self, date_str):
        """
        Set the date from string.

        Args:
            date_str (str): Date string in YYYY-MM-DD format.
        """
        self.selected_date.set(date_str)

class AddBillDialog(ctk.CTkToplevel):
    """
    Dialog for adding a new bill to the system.

    Provides a comprehensive form for entering all bill details including name,
    due date, amount, category, payment method, and contact information.
    """
    
    def __init__(self, master, on_success):
        """
        Initialize the AddBillDialog.

        Args:
            master: The parent window.
            on_success (callable): Callback to invoke when bill is successfully added.
        """
        super().__init__(master)
        self.title("Add Bill")
        self.geometry("550x700")
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
        """
        Setup the add bill dialog UI with all form fields.
        """
        self.grid_columnconfigure(1, weight=1)
        row = 0
        # Name
        ctk.CTkLabel(self, text="Name:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Due Date with improved selector
        ctk.CTkLabel(self, text="Due Date:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ne")
        self.date_selector = DateSelectorFrame(self)
        self.date_selector.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Paid
        ctk.CTkLabel(self, text="Paid:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.paid_var = ctk.BooleanVar()
        self.paid_checkbox = ctk.CTkCheckBox(self, variable=self.paid_var, text="Yes")
        self.paid_checkbox.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="w")
        row += 1
        
        # Confirmation Number
        ctk.CTkLabel(self, text="Confirmation Number:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.confirmation_entry = ctk.CTkEntry(self, placeholder_text="Enter confirmation number...", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.confirmation_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Billing Cycle (dropdown)
        ctk.CTkLabel(self, text="Billing Cycle:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.billing_cycle_var = StringVar(value=BILLING_CYCLES[2])
        self.billing_cycle_combo = ttk.Combobox(self, textvariable=self.billing_cycle_var, values=BILLING_CYCLES, state="readonly")
        self.billing_cycle_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Reminder Days (dropdown)
        ctk.CTkLabel(self, text="Reminder Days:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.reminder_days_var = IntVar(value=7)
        self.reminder_days_combo = ttk.Combobox(self, textvariable=self.reminder_days_var, values=REMINDER_DAYS, state="readonly")
        self.reminder_days_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Amount
        ctk.CTkLabel(self, text="Amount ($):").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Enter amount...")
        self.amount_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Payment Method (dropdown)
        ctk.CTkLabel(self, text="Payment Method:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.payment_method_var = StringVar(value="Not Set")
        self.payment_method_combo = ttk.Combobox(self, textvariable=self.payment_method_var, state="readonly")
        self.payment_method_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self._load_payment_methods()
        row += 1
        # Web Page
        ctk.CTkLabel(self, text="Web Page:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.web_page_entry = ctk.CTkEntry(self)
        self.web_page_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Company Email
        ctk.CTkLabel(self, text="Company Email:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.company_email_entry = ctk.CTkEntry(self)
        self.company_email_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Support Phone
        ctk.CTkLabel(self, text="Support Phone:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.support_phone_entry = ctk.CTkEntry(self)
        self.support_phone_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Account Number
        ctk.CTkLabel(self, text="Account Number:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.account_number_entry = ctk.CTkEntry(self)
        self.account_number_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Category (dropdown)
        ctk.CTkLabel(self, text="Category:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.category_var = StringVar(value="Uncategorized")
        self.category_combo = ttk.Combobox(self, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self._load_categories()
        row += 1
        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row, column=0, columnspan=2)
        row += 1
        # Add button with icon
        self.add_button = icon_manager.get_button_with_icon(
            self, text=" Add Bill", icon_name=ICON_ADD, 
            command=self._on_add, fg_color=ACCENT_COLOR, text_color="white"
        )
        self.add_button.grid(row=row, column=0, columnspan=2, pady=SPACING_MD)

    def _load_categories(self):
        """
        Load categories into the dropdown from the database.
        """
        try:
            self.categories = fetch_all_categories()
            category_names = ["Uncategorized"] + [cat['name'] for cat in self.categories]
            self.category_combo['values'] = category_names
        except Exception as e:
            print(f"Error loading categories: {e}")
            self.categories = []
            self.category_combo['values'] = ["Uncategorized"]

    def _load_payment_methods(self):
        try:
            self.payment_methods = fetch_all_payment_methods()
            method_names = ["Not Set"] + [pm['name'] for pm in self.payment_methods]
            self.payment_method_combo['values'] = method_names
        except Exception as e:
            print(f"Error loading payment methods: {e}")
            self.payment_methods = []
            self.payment_method_combo['values'] = ["Not Set"]

    def _on_add(self):
        """
        Handle bill addition with comprehensive validation.
        Validates all fields and inserts the bill into the database.
        """
        try:
            # Collect all field values
            bill_data = {
                "name": self.name_entry.get().strip(),
                "due_date": self.date_selector.get_date().strip(),
                "paid": self.paid_var.get(),
                "confirmation_number": self.confirmation_entry.get().strip(),
                "billing_cycle": self.billing_cycle_var.get(),
                "reminder_days": self.reminder_days_var.get(),
                "amount": self._parse_amount(self.amount_entry.get().strip()),
                "web_page": self.web_page_entry.get().strip(),
                "company_email": self.company_email_entry.get().strip(),
                "support_phone": self.support_phone_entry.get().strip(),
                "account_number": self.account_number_entry.get().strip(),
                "reference_id": "",  # Not in current UI but validated
                "login_info": "",    # Not in current UI but validated
                "password": "",      # Not in current UI but validated
                "customer_service_hours": "",  # Not in current UI but validated
                "mobile_app": "",    # Not in current UI but validated
                "support_chat_url": ""  # Not in current UI but validated
            }
            
            # Validate all fields using the comprehensive validator
            validated_data = BillValidator.validate_bill_data(bill_data)
            
            # Get category ID
            category_id = None
            if self.category_var.get() != "Uncategorized":
                for category in self.categories:
                    if category['name'] == self.category_var.get():
                        category_id = category['id']
                        break
            
            # Get payment method ID
            payment_method_id = None
            if self.payment_method_var.get() != "Not Set":
                for pm in self.payment_methods:
                    if pm['name'] == self.payment_method_var.get():
                        payment_method_id = pm['id']
                        break
            
            # Add IDs to validated data
            validated_data['category_id'] = category_id
            validated_data['payment_method_id'] = payment_method_id
            
            # Clear any previous error messages
            self.error_label.configure(text="")
            
            # Insert the bill
            insert_bill(validated_data)
                            # Success popup removed for faster workflow
            self.on_success()
            self.destroy()
            
        except ValidationError as e:
            # Show validation error
            error_message = str(e)
            self.error_label.configure(text=error_message)
            show_popup(self, "Validation Error", error_message, color="red")
        except Exception as e:
            # Show general error
            error_message = f"Failed to add bill: {str(e)}"
            self.error_label.configure(text=error_message)
            show_popup(self, "Error", error_message, color="red")
            
    def _parse_amount(self, amount_str):
        """
        Parse amount string to float, return None if empty or invalid.

        Args:
            amount_str (str): The amount string to parse.

        Returns:
            float or None: The parsed amount or None if invalid.
        """
        if not amount_str:
            return None
        try:
            # Remove currency symbols and commas
            cleaned = amount_str.replace('$', '').replace(',', '').strip()
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

class EditBillDialog(ctk.CTkToplevel):
    """
    Dialog for editing an existing bill.

    Provides a form pre-filled with current bill data for editing.
    Similar to AddBillDialog but for updating existing bills.
    """
    
    def __init__(self, master, bill_data, on_success):
        """
        Initialize the EditBillDialog.

        Args:
            master: The parent window.
            bill_data (dict): The current bill data to edit.
            on_success (callable): Callback to invoke when bill is successfully updated.
        """
        super().__init__(master)
        self.title("Edit Bill")
        self.geometry("550x700")
        self.bill_data = bill_data
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
        """
        Setup the edit bill dialog UI with pre-filled form fields.
        """
        self.grid_columnconfigure(1, weight=1)
        row = 0
        # Name
        ctk.CTkLabel(self, text="Name:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.insert(0, self.bill_data.get("name", ""))
        self.name_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Due Date with improved selector
        ctk.CTkLabel(self, text="Due Date:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ne")
        self.date_selector = DateSelectorFrame(self)
        self.date_selector.set_date(self.bill_data.get("due_date", ""))
        self.date_selector.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Paid
        ctk.CTkLabel(self, text="Paid:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.paid_var = ctk.BooleanVar(value=self.bill_data.get("paid", False))
        self.paid_checkbox = ctk.CTkCheckBox(self, variable=self.paid_var, text="Yes")
        self.paid_checkbox.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="w")
        row += 1
        
        # Confirmation Number
        ctk.CTkLabel(self, text="Confirmation Number:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.confirmation_entry = ctk.CTkEntry(self, placeholder_text="Enter confirmation number...", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.confirmation_entry.insert(0, self.bill_data.get("confirmation_number", ""))
        self.confirmation_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Billing Cycle (dropdown)
        ctk.CTkLabel(self, text="Billing Cycle:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.billing_cycle_var = StringVar(value=self.bill_data.get("billing_cycle", BILLING_CYCLES[2]))
        self.billing_cycle_combo = ttk.Combobox(self, textvariable=self.billing_cycle_var, values=BILLING_CYCLES, state="readonly")
        self.billing_cycle_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Reminder Days (dropdown)
        ctk.CTkLabel(self, text="Reminder Days:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.reminder_days_var = IntVar(value=self.bill_data.get("reminder_days", 7))
        self.reminder_days_combo = ttk.Combobox(self, textvariable=self.reminder_days_var, values=REMINDER_DAYS, state="readonly")
        self.reminder_days_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Amount
        ctk.CTkLabel(self, text="Amount ($):").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Enter amount...")
        amount_value = self.bill_data.get("amount")
        if amount_value:
            self.amount_entry.insert(0, f"${amount_value:.2f}")
        self.amount_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Payment Method (dropdown)
        ctk.CTkLabel(self, text="Payment Method:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.payment_method_var = StringVar(value="Not Set")
        self.payment_method_combo = ttk.Combobox(self, textvariable=self.payment_method_var, state="readonly")
        self.payment_method_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self._load_payment_methods()
        row += 1
        # Web Page
        ctk.CTkLabel(self, text="Web Page:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.web_page_entry = ctk.CTkEntry(self)
        self.web_page_entry.insert(0, self.bill_data.get("web_page", ""))
        self.web_page_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Company Email
        ctk.CTkLabel(self, text="Company Email:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.company_email_entry = ctk.CTkEntry(self)
        self.company_email_entry.insert(0, self.bill_data.get("company_email", ""))
        self.company_email_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Support Phone
        ctk.CTkLabel(self, text="Support Phone:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.support_phone_entry = ctk.CTkEntry(self)
        self.support_phone_entry.insert(0, self.bill_data.get("support_phone", ""))
        self.support_phone_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Account Number
        ctk.CTkLabel(self, text="Account Number:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.account_number_entry = ctk.CTkEntry(self)
        self.account_number_entry.insert(0, self.bill_data.get("account_number", ""))
        self.account_number_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        # Category (dropdown)
        ctk.CTkLabel(self, text="Category:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.category_var = StringVar(value="Uncategorized")
        self.category_combo = ttk.Combobox(self, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self._load_categories()
        row += 1
        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row, column=0, columnspan=2)
        row += 1
        # Save button with icon
        self.save_button = icon_manager.get_button_with_icon(
            self, text=" Save Changes", icon_name=ICON_SAVE, 
            command=self._on_save, fg_color=ACCENT_COLOR, text_color="white"
        )
        self.save_button.grid(row=row, column=0, columnspan=2, pady=SPACING_MD)

    def _load_categories(self):
        """
        Load categories into the dropdown and set current category.
        """
        try:
            self.categories = fetch_all_categories()
            category_names = ["Uncategorized"] + [cat['name'] for cat in self.categories]
            self.category_combo['values'] = category_names
            # Set current category
            current_category = self.bill_data.get("category_name", "Uncategorized")
            self.category_var.set(current_category)
        except Exception as e:
            print(f"Error loading categories: {e}")
            self.categories = []
            self.category_combo['values'] = ["Uncategorized"]

    def _load_payment_methods(self):
        try:
            self.payment_methods = fetch_all_payment_methods()
            method_names = ["Not Set"] + [pm['name'] for pm in self.payment_methods]
            self.payment_method_combo['values'] = method_names
            # Set current payment method
            current_method = self.bill_data.get("payment_method_name", "Not Set")
            self.payment_method_var.set(current_method)
        except Exception as e:
            print(f"Error loading payment methods: {e}")
            self.payment_methods = []
            self.payment_method_combo['values'] = ["Not Set"]

    def _on_save(self):
        """
        Handle bill update with comprehensive validation.
        Validates all fields and updates the bill in the database.
        """
        try:
            # Collect all field values
            bill_data = {
                "name": self.name_entry.get().strip(),
                "due_date": self.date_selector.get_date().strip(),
                "paid": self.paid_var.get(),
                "confirmation_number": self.confirmation_entry.get().strip(),
                "billing_cycle": self.billing_cycle_var.get(),
                "reminder_days": self.reminder_days_var.get(),
                "amount": self._parse_amount(self.amount_entry.get().strip()),
                "web_page": self.web_page_entry.get().strip(),
                "company_email": self.company_email_entry.get().strip(),
                "support_phone": self.support_phone_entry.get().strip(),
                "account_number": self.account_number_entry.get().strip(),
                "reference_id": self.bill_data.get("reference_id", ""),
                "login_info": self.bill_data.get("login_info", ""),
                "password": self.bill_data.get("password", ""),
                "customer_service_hours": self.bill_data.get("customer_service_hours", ""),
                "mobile_app": self.bill_data.get("mobile_app", ""),
                "support_chat_url": self.bill_data.get("support_chat_url", "")
            }
            
            # Validate all fields using the comprehensive validator
            validated_data = BillValidator.validate_bill_data(bill_data)
            
            # Get category ID
            category_id = None
            if self.category_var.get() != "Uncategorized":
                for category in self.categories:
                    if category['name'] == self.category_var.get():
                        category_id = category['id']
                        break
            
            # Get payment method ID
            payment_method_id = None
            if self.payment_method_var.get() != "Not Set":
                for pm in self.payment_methods:
                    if pm['name'] == self.payment_method_var.get():
                        payment_method_id = pm['id']
                        break
            
            # Update the bill data with validated values and IDs
            bill_data = self.bill_data.copy()
            bill_data.update(validated_data)
            bill_data["category_id"] = category_id
            bill_data["payment_method_id"] = payment_method_id
            
            # Clear any previous error messages
            self.error_label.configure(text="")
            
            # Update the bill
            update_bill(bill_data["id"], bill_data)
                            # Success popup removed for faster workflow
            self.on_success()
            self.destroy()
            
        except ValidationError as e:
            # Show validation error
            error_message = str(e)
            self.error_label.configure(text=error_message)
            show_popup(self, "Validation Error", error_message, color="red")
        except Exception as e:
            # Show general error
            error_message = f"Failed to update bill: {str(e)}"
            self.error_label.configure(text=error_message)
            show_popup(self, "Error", error_message, color="red")
            
    def _parse_amount(self, amount_str):
        """
        Parse amount string to float, return None if empty or invalid.

        Args:
            amount_str (str): The amount string to parse.

        Returns:
            float or None: The parsed amount or None if invalid.
        """
        if not amount_str:
            return None
        try:
            # Remove currency symbols and commas
            cleaned = amount_str.replace('$', '').replace(',', '').strip()
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

class AddCategoryDialog(ctk.CTkToplevel):
    """
    Dialog for adding a new category.

    Provides a form for entering category name, color, and description.
    """
    
    def __init__(self, master, on_success):
        """
        Initialize the AddCategoryDialog.

        Args:
            master: The parent window.
            on_success (callable): Callback to invoke when category is successfully added.
        """
        super().__init__(master)
        self.title("Add Category")
        self.geometry("400x300")
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
        """
        Setup the add category dialog UI with form fields.
        """
        self.grid_columnconfigure(1, weight=1)
        row = 0
        
        # Name
        ctk.CTkLabel(self, text="Name:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Color
        ctk.CTkLabel(self, text="Color:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.color_var = ctk.StringVar(value="#1f538d")
        self.color_entry = ctk.CTkEntry(self, textvariable=self.color_var)
        self.color_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Description
        ctk.CTkLabel(self, text="Description:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.description_text = ctk.CTkTextbox(self, height=100)
        self.description_text.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row, column=0, columnspan=2)
        row += 1
        
        # Add button with icon
        self.add_button = icon_manager.get_button_with_icon(
            self, text=" Add Category", icon_name=ICON_ADD, 
            command=self._on_add, fg_color=ACCENT_COLOR, text_color="white"
        )
        self.add_button.grid(row=row, column=0, columnspan=2, pady=SPACING_MD)

    def _on_add(self):
        """
        Handle category addition with comprehensive validation.
        Validates all fields and inserts the category into the database.
        """
        try:
            # Collect field values
            category_data = {
                "name": self.name_entry.get().strip(),
                "color": self.color_var.get().strip(),
                "description": self.description_text.get("1.0", "end-1c").strip()
            }
            
            # Validate all fields using the comprehensive validator
            validated_data = CategoryValidator.validate_category_data(category_data)
            
            # Clear any previous error messages
            self.error_label.configure(text="")
            
            # Insert the category
            from db import insert_category
            insert_category(validated_data)
                            # Success popup removed for faster workflow
            self.on_success()
            self.destroy()
            
        except ValidationError as e:
            # Show validation error
            error_message = str(e)
            self.error_label.configure(text=error_message)
            show_popup(self, "Validation Error", error_message, color="red")
        except Exception as e:
            # Show general error
            error_message = f"Failed to add category: {str(e)}"
            self.error_label.configure(text=error_message)
            show_popup(self, "Error", error_message, color="red")

class EditCategoryDialog(ctk.CTkToplevel):
    """
    Dialog for editing an existing category.

    Provides a form pre-filled with current category data for editing.
    """
    
    def __init__(self, master, category_data, on_success):
        """
        Initialize the EditCategoryDialog.

        Args:
            master: The parent window.
            category_data (dict): The current category data to edit.
            on_success (callable): Callback to invoke when category is successfully updated.
        """
        super().__init__(master)
        self.title("Edit Category")
        self.geometry("400x300")
        self.category_data = category_data
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
        """
        Setup the edit category dialog UI with pre-filled form fields.
        """
        self.grid_columnconfigure(1, weight=1)
        row = 0
        
        # Name
        ctk.CTkLabel(self, text="Name:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.insert(0, self.category_data.get("name", ""))
        self.name_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Color
        ctk.CTkLabel(self, text="Color:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.color_var = ctk.StringVar(value=self.category_data.get("color", "#1f538d"))
        self.color_entry = ctk.CTkEntry(self, textvariable=self.color_var)
        self.color_entry.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Description
        ctk.CTkLabel(self, text="Description:").grid(row=row, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="e")
        self.description_text = ctk.CTkTextbox(self, height=100)
        self.description_text.insert("1.0", self.category_data.get("description", ""))
        self.description_text.grid(row=row, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        row += 1
        
        # Error label
        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=row, column=0, columnspan=2)  # noqa
        row += 1
        
        # Save button with icon
        self.save_button = icon_manager.get_button_with_icon(
            self, text=" Save Changes", icon_name=ICON_SAVE, 
            command=self._on_save, fg_color=ACCENT_COLOR, text_color="white"
        )
        self.save_button.grid(row=row, column=0, columnspan=2, pady=SPACING_MD)

    def _on_save(self):
        """
        Handle category update with comprehensive validation.
        Validates all fields and updates the category in the database.
        """
        try:
            # Collect field values
            category_data = {
                "name": self.name_entry.get().strip(),
                "color": self.color_var.get().strip(),
                "description": self.description_text.get("1.0", "end-1c").strip()
            }
            
            # Validate all fields using the comprehensive validator
            validated_data = CategoryValidator.validate_category_data(category_data)
            
            # Clear any previous error messages
            self.error_label.configure(text="")
            
            # Update the category
            from db import update_category
            update_category(self.category_data["id"], validated_data)
                            # Success popup removed for faster workflow
            self.on_success()
            self.destroy()
            
        except ValidationError as e:
            # Show validation error
            error_message = str(e)
            self.error_label.configure(text=error_message)
            show_popup(self, "Validation Error", error_message, color="red")
        except Exception as e:
            # Show general error
            error_message = f"Failed to update category: {str(e)}"
            self.error_label.configure(text=error_message)
            show_popup(self, "Error", error_message, color="red")

class MainWindow(ctk.CTk):
    """
    Main application window for the Bills Tracker application.

    Provides the primary interface for managing bills, categories, and settings.
    Includes authentication, reminder notifications, and data management features.
    """
    
    def __init__(self):
        """
        Initialize the MainWindow with authentication, configuration, and UI setup.
        """
        super().__init__()
        self.title("Bills Tracker v3")
        self.geometry("1200x800")
        self.minsize(800, 600)  # Set minimum window size for responsive design

        # Configure the main window
        self.configure(bg_color=BACKGROUND_COLOR)
        
        # Authentication
        self.current_user = None
        self.session_token = None
        
        # Cerrar toda la app si se cierra la ventana principal
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Inicializar pending_changes para evitar errores
        self.pending_changes = {}
        self._selected_bills = set()  # Track selected bill IDs for bulk operations
        
        # Pagination variables
        self._current_page = 1
        self._items_per_page = 20  # Default items per page
        self._total_pages = 1
        
        # Load configuration
        try:
            from core.config import config_manager
            self.config_manager = config_manager
            
            # Apply saved theme
            saved_theme = config_manager.get_theme()
            if saved_theme != "System":
                ctk.set_appearance_mode(saved_theme.lower())
            
            # Apply saved window size
            width, height = config_manager.get_window_size()
            self.geometry(f"{width}x{height}")
            
            # Apply saved items per page
            self._items_per_page = config_manager.get_items_per_page()
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config_manager = None
        
        # Initialize reminder service with saved interval
        check_interval = 300
        if hasattr(self, 'config_manager') and self.config_manager:
            check_interval = self.config_manager.get_reminder_check_interval()
        
        self.reminder_service = ReminderService(check_interval=check_interval)
        
        # Initialize notification manager with saved settings
        max_notifications = 3
        if hasattr(self, 'config_manager') and self.config_manager:
            max_notifications = self.config_manager.get_max_notifications()
        
        self.notification_manager = NotificationManager()
        self.notification_manager.max_notifications = max_notifications
        
        # Setup UI
        self._setup_ui()
        
        # Check authentication
        self._check_authentication()
        
        # Start reminder service
        try:
            self.reminder_service.start(notification_callback=self._handle_reminder_notification)
        except Exception as e:
            print(f"Error starting reminder service: {e}")
    
    def _setup_ui(self):
        """
        Setup the main window UI with sidebar navigation and content area.
        """
        # Configure grid for responsive layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar with improved styling
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=PRIMARY_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(SPACING_SM, 0), pady=SPACING_SM)
        self.sidebar.grid_rowconfigure(6, weight=1)  # Increased for auth buttons
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Sidebar header with icon
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=SPACING_SM, pady=(SPACING_MD, SPACING_LG))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="💰", font=("Arial", 24)).grid(row=0, column=0, pady=(0, SPACING_XS))
        ctk.CTkLabel(header_frame, text="Bills Tracker", font=("Arial", 18, "bold"), text_color="white").grid(row=1, column=0)

        # Sidebar navigation buttons with icons
        nav_buttons = [
            ("📋 Bills", self.show_bills_view),
            ("🏷️ Categories", self.show_categories_view),
            ("⚙️ Settings", self.show_settings_view)
        ]
        
        for i, (text, command) in enumerate(nav_buttons, 1):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                command=command,
                fg_color="transparent",
                text_color="white",
                hover_color=SECONDARY_COLOR,
                anchor="w",
                height=40
            )
            btn.grid(row=i, column=0, sticky="ew", padx=SPACING_SM, pady=SPACING_XS)
        
        # Authentication buttons (bottom of sidebar)
        auth_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        auth_frame.grid(row=7, column=0, sticky="ew", padx=SPACING_SM, pady=SPACING_MD)
        auth_frame.grid_columnconfigure(0, weight=1)
        
        # User info label
        self.user_info_label = ctk.CTkLabel(
            auth_frame,
            text="Not logged in",
            text_color="white",
            font=("Arial", 10)
        )
        self.user_info_label.grid(row=0, column=0, pady=(0, SPACING_SM))
        
        # Change password button
        self.change_password_btn = ctk.CTkButton(
            auth_frame,
            text="Change Password",
            command=self._show_change_password_dialog,
            fg_color="transparent",
            text_color="white",
            hover_color=SECONDARY_COLOR,
            anchor="w",
            height=30
        )
        self.change_password_btn.grid(row=1, column=0, sticky="ew", pady=SPACING_XS)
        
        # Logout button
        self.logout_btn = ctk.CTkButton(
            auth_frame,
            text="Logout",
            command=self._logout,
            fg_color="transparent",
            text_color="white",
            hover_color=ERROR_COLOR,
            anchor="w",
            height=30
        )
        self.logout_btn.grid(row=2, column=0, sticky="ew", pady=SPACING_XS)
        
        # Main content area with improved responsive design
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nswe", padx=SPACING_SM, pady=SPACING_SM)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_bills_view(self):
        self.clear_content()
        
        # Detect dark mode
        dark_mode = is_dark_mode()
        
        # Set colors based on mode
        if dark_mode:
            table_bg = "#23272e"
            table_fg = "#f7f9fa"
            table_alt_bg = "#2c313a"
            table_header_bg = "#1f538d"
            table_header_fg = "#ffffff"
            button_bg = "#222831"
            button_fg = "#f7f9fa"
            entry_bg = "#23272e"
            entry_fg = "#f7f9fa"
            border_color = "#444"
        else:
            table_bg = BACKGROUND_COLOR
            table_fg = TEXT_COLOR
            table_alt_bg = "#f0f0f0"
            table_header_bg = PRIMARY_COLOR
            table_header_fg = "white"
            button_bg = BACKGROUND_COLOR
            button_fg = TEXT_COLOR
            entry_bg = BACKGROUND_COLOR
            entry_fg = TEXT_COLOR
            border_color = "#ccc"

        # Button frame for Add, Export, Import with icons
        btn_frame = ctk.CTkFrame(self.content, fg_color=button_bg, border_color=border_color, border_width=1)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        btn_frame.grid_columnconfigure(3, weight=1)
        
        add_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Add Bill", icon_name=ICON_ADD, 
            command=self.open_add_bill_dialog, fg_color=ACCENT_COLOR if not dark_mode else "#3a6ea5", text_color="white", height=36
        )
        add_btn.grid(row=0, column=0, padx=(SPACING_SM, SPACING_SM), pady=SPACING_SM)
        
        export_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Export CSV", icon_name=ICON_EXPORT, 
            command=self.export_bills, fg_color=SECONDARY_COLOR if not dark_mode else "#2cba9f", text_color="white", height=36
        )
        export_btn.grid(row=0, column=1, padx=(0, SPACING_SM), pady=SPACING_SM)
        
        import_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Import CSV", icon_name=ICON_IMPORT, 
            command=self.import_bills, fg_color=SECONDARY_COLOR if not dark_mode else "#2cba9f", text_color="white", height=36
        )
        import_btn.grid(row=0, column=2, padx=(0, SPACING_SM), pady=SPACING_SM)

        # Filter options frame
        filter_frame = ctk.CTkFrame(self.content, fg_color=button_bg, border_color=border_color, border_width=1)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        filter_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(filter_frame, text="Status:", text_color=button_fg).grid(row=0, column=0, padx=(SPACING_SM, SPACING_SM), pady=SPACING_SM)
        self.status_filter_var = ctk.StringVar(value="Pending")
        status_combo = CTkComboBox(filter_frame, variable=self.status_filter_var,
                                   values=["Pending", "Auto-Pay", "Paid", "All"], width=120, fg_color=entry_bg, text_color=entry_fg, dropdown_fg_color=entry_bg, dropdown_text_color=entry_fg)
        status_combo.grid(row=0, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="w")
        status_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        ctk.CTkLabel(filter_frame, text="Period:", text_color=button_fg).grid(row=0, column=2, padx=(SPACING_MD, SPACING_SM), pady=SPACING_SM)
        self.period_filter_var = ctk.StringVar(value="All")
        period_combo = CTkComboBox(filter_frame, variable=self.period_filter_var,
                                   values=["All", "This Month", "Last Month", "Previous Month", "Next Month", "This Year", "Last Year"], width=150, fg_color=entry_bg, text_color=entry_fg, dropdown_fg_color=entry_bg, dropdown_text_color=entry_fg)
        period_combo.grid(row=0, column=3, padx=SPACING_SM, pady=SPACING_SM)
        period_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        clear_btn = ctk.CTkButton(filter_frame, text="Clear All", command=self.clear_all_filters, width=80, fg_color=button_bg, text_color=button_fg, hover_color=SECONDARY_COLOR)
        clear_btn.grid(row=0, column=4, padx=SPACING_SM, pady=SPACING_SM)

        # Search bar
        search_frame = ctk.CTkFrame(self.content, fg_color=button_bg, border_color=border_color, border_width=1)
        search_frame.grid(row=2, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search:", text_color=button_fg).grid(row=0, column=0, padx=(SPACING_SM, SPACING_SM), pady=SPACING_SM)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, fg_color=entry_bg, text_color=entry_fg, border_color=border_color)
        self.search_entry.grid(row=0, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self.search_var.trace("w", self.apply_filters)
        
        self.search_field_var = ctk.StringVar(value="Name")
        search_field_combo = CTkComboBox(search_frame, variable=self.search_field_var,
                                         values=["Name", "Due Date", "Category", "Status", "Paid", "Confirmation"], width=150, fg_color=entry_bg, text_color=entry_fg, dropdown_fg_color=entry_bg, dropdown_text_color=entry_fg)
        search_field_combo.grid(row=0, column=2, padx=SPACING_SM, pady=SPACING_SM)
        search_field_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        clear_search_btn = ctk.CTkButton(search_frame, text="Clear Search", command=self.clear_search, width=100, fg_color=button_bg, text_color=button_fg, hover_color=SECONDARY_COLOR)
        clear_search_btn.grid(row=0, column=3, padx=SPACING_SM, pady=SPACING_SM)

        self.bills_table_frame = ctk.CTkFrame(self.content)
        self.bills_table_frame.grid(row=2, column=0, sticky="nswe", padx=SPACING_SM)
        self.bills_table_frame.grid_rowconfigure(0, weight=1)
        self.bills_table_frame.grid_columnconfigure(0, weight=1)

        # Enhanced table styling
        style = ttk.Style()
        
        # Configure Treeview style for better visual separation
        style.theme_use("default")
        style.configure("Enhanced.Treeview",
                       background=BACKGROUND_COLOR,
                       foreground=TEXT_COLOR,
                       rowheight=30,
                       fieldbackground=BACKGROUND_COLOR,
                       borderwidth=1,
                       relief="solid")
        
        # Configure alternating row colors using tags
        style.configure("Enhanced.Treeview",
                       background=BACKGROUND_COLOR,
                       foreground=TEXT_COLOR,
                       rowheight=30,
                       fieldbackground=BACKGROUND_COLOR,
                       borderwidth=1,
                       relief="solid")
        
        # Configure alternate row style
        style.configure("Alternate.Treeview",
                       background="#f0f0f0",
                       foreground=TEXT_COLOR,
                       rowheight=30,
                       fieldbackground="#f0f0f0",
                       borderwidth=1,
                       relief="solid")
        
        # Configure header style
        style.configure("Enhanced.Treeview.Heading",
                       background=PRIMARY_COLOR,
                       foreground="white",
                       relief="flat",
                       borderwidth=1,
                       font=("Arial", 10, "bold"))
        
        # Configure header hover effect
        style.map("Enhanced.Treeview.Heading",
                 background=[("active", SECONDARY_COLOR)])

        columns = ("Select", "Paid", "Name", "Due Date", "Amount", "Category", "Status", "Payment Method", "Confirmation")
        self.bills_table = ttk.Treeview(self.bills_table_frame, columns=columns, show="headings", height=15, style="Enhanced.Treeview")
        
        # Configure tag colors for alternating rows
        self.bills_table.tag_configure("alternate", background="#f0f0f0")
        self._sort_column = None
        self._sort_reverse = False
        self._selected_bills = set()  # Track selected bill IDs
        
        # Configure columns
        self.bills_table.heading("Select", text="☐", command=self.toggle_select_all)
        self.bills_table.column("Select", width=50, anchor="center")
        
        self.bills_table.heading("Paid", text="Paid", command=lambda c="Paid": self.sort_by_column(c))
        self.bills_table.column("Paid", width=60, anchor="center")
        
        for col in ["Name", "Due Date", "Amount", "Category", "Status", "Payment Method", "Confirmation"]:
            self.bills_table.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.bills_table.column(col, width=120, anchor="center")
        
        # Bind checkbox click event
        self.bills_table.bind("<Button-1>", self.on_table_click)

        self.bills_by_id = {}  # id -> bill dict
        self._bills_data = fetch_all_bills()
        # Apply default filter (Pending bills only)
        self._filtered_bills = [bill for bill in self._bills_data if not bill.get("paid", False)]

        scrollbar = ttk.Scrollbar(self.bills_table_frame, orient="vertical", command=self.bills_table.yview)
        self.bills_table.configure(yscrollcommand=scrollbar.set)
        self.bills_table.grid(row=0, column=0, sticky="nswe")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bills counter
        self.bills_counter_label = ctk.CTkLabel(self.content, text="", font=("Arial", 12))
        self.bills_counter_label.grid(row=3, column=0, sticky="w", padx=SPACING_SM, pady=(SPACING_SM, 0))
        
        # Now populate the table after the counter label is created
        self.populate_bills_table(self._filtered_bills)
        
        # --- Action Buttons (Edit, Delete, Bulk Delete, Apply, Refresh) ---
        action_btn_frame = ctk.CTkFrame(self.content, fg_color=button_bg, border_color=border_color, border_width=1)
        action_btn_frame.grid(row=4, column=0, sticky="ew", pady=(SPACING_SM, SPACING_SM))
        
        edit_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Edit", icon_name=ICON_EDIT, 
            command=self.edit_selected_bill, fg_color=PRIMARY_COLOR, text_color="white", height=36
        )
        edit_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        delete_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Delete", icon_name=ICON_DELETE, 
            command=self.delete_selected_bill, fg_color=ERROR_COLOR, text_color="white", height=36
        )
        delete_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        self.bulk_delete_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text="Delete Selected", icon_name=ICON_DELETE, 
            command=self.bulk_delete_selected_bills, fg_color=ERROR_COLOR, text_color="white", state="disabled", height=36
        )
        self.bulk_delete_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        refresh_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Refresh", icon_name=ICON_REFRESH, 
            command=self.refresh_bills_data, fg_color=SECONDARY_COLOR, text_color="white", height=36
        )
        refresh_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        self.apply_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Apply Changes", icon_name=ICON_APPLY, 
            command=self.apply_pending_changes, fg_color=SUCCESS_COLOR, text_color="white", height=36
        )
        self.apply_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        # --- Pagination Controls ---
        pagination_frame = ctk.CTkFrame(self.content, fg_color=button_bg, border_color=border_color, border_width=1)
        pagination_frame.grid(row=5, column=0, sticky="ew", pady=(SPACING_SM, SPACING_SM))
        ctk.CTkLabel(pagination_frame, text="Items per page:", text_color=button_fg).pack(side="left", padx=SPACING_SM)
        self.items_per_page_var = ctk.StringVar(value=str(self._items_per_page))
        items_combo = CTkComboBox(pagination_frame, variable=self.items_per_page_var,
                                  values=["10", "20", "50", "100"], width=80, fg_color=entry_bg, text_color=entry_fg, dropdown_fg_color=entry_bg, dropdown_text_color=entry_fg)
        items_combo.pack(side="left", padx=SPACING_SM)
        items_combo.bind("<<ComboboxSelected>>", self.on_items_per_page_change)
        
        # Pagination info
        self.pagination_info_label = ctk.CTkLabel(pagination_frame, text="", font=("Arial", 12))
        self.pagination_info_label.pack(side="left", padx=SPACING_MD)
        
        # Navigation buttons
        self.first_page_btn = ctk.CTkButton(pagination_frame, text="⏮️ First", width=80, 
                                           command=self.go_to_first_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.first_page_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        self.prev_page_btn = ctk.CTkButton(pagination_frame, text="◀️ Prev", width=80, 
                                          command=self.go_to_prev_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.prev_page_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        self.next_page_btn = ctk.CTkButton(pagination_frame, text="Next ▶️", width=80, 
                                          command=self.go_to_next_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.next_page_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        self.last_page_btn = ctk.CTkButton(pagination_frame, text="Last ⏭️", width=80, 
                                          command=self.go_to_last_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.last_page_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)

    def apply_filters(self, *args):
        """
        Apply filters to the bills table based on search and filter criteria.
        """
        # Start with all bills
        filtered_bills = self._bills_data.copy()
        
        # Apply status filter
        status_filter = self.status_filter_var.get()
        if status_filter == "Pending":
            filtered_bills = [bill for bill in filtered_bills if not bill.get("paid", False) and not bill.get("payment_method_automatic", False)]
        elif status_filter == "Auto-Pay":
            filtered_bills = [bill for bill in filtered_bills if not bill.get("paid", False) and bill.get("payment_method_automatic", False)]
        elif status_filter == "Paid":
            filtered_bills = [bill for bill in filtered_bills if bill.get("paid", False)]
        # "All" means no status filtering
        
        # Apply period filter
        period_filter = self.period_filter_var.get()
        if period_filter != "All":
            filtered_bills = self._filter_by_period(filtered_bills, period_filter)
        
        # Apply search filter
        search_term = self.search_var.get().lower()
        search_field = self.search_field_var.get()
        
        if search_term:
            search_filtered = []
            for bill in filtered_bills:
                if search_field == "Name":
                    if search_term in bill.get("name", "").lower():
                        search_filtered.append(bill)
                elif search_field == "Due Date":
                    if search_term in bill.get("due_date", "").lower():
                        search_filtered.append(bill)
                elif search_field == "Category":
                    category_name = bill.get("category_name", "Uncategorized")
                    if search_term in category_name.lower():
                        search_filtered.append(bill)
                elif search_field == "Status":
                    if bill.get("paid", False):
                        status = "Paid"
                    elif bill.get("payment_method_automatic", False):
                        status = "Auto-Pay"
                    else:
                        status = "Pending"
                    if search_term in status.lower():
                        search_filtered.append(bill)
                elif search_field == "Paid":
                    paid_status = "paid" if bill.get("paid", False) else "unpaid"
                    if search_term in paid_status.lower():
                        search_filtered.append(bill)
                elif search_field == "Confirmation":
                    confirmation = bill.get("confirmation_number", "")
                    if search_term in confirmation.lower():
                        search_filtered.append(bill)
            filtered_bills = search_filtered
        
        self._filtered_bills = filtered_bills
        
        # Clear selection and reset pagination when filters change
        self._selected_bills.clear()
        self._current_page = 1  # Reset to first page
        
        # Maintain current sort order
        if self._sort_column:
            self.sort_by_column(self._sort_column)
        else:
            self.populate_bills_table(self._filtered_bills)
    
    def _filter_by_period(self, bills, period):
        """
        Filter bills by time period.

        Args:
            bills (list): List of bills to filter.
            period (str): The time period to filter by.

        Returns:
            list: Filtered list of bills.
        """
        from datetime import datetime, timedelta
        
        today = datetime.now()
        filtered_bills = []
        
        for bill in bills:
            try:
                due_date = datetime.strptime(bill.get("due_date", ""), "%Y-%m-%d")
                
                if period == "This Month":
                    if due_date.year == today.year and due_date.month == today.month:
                        filtered_bills.append(bill)
                        
                elif period == "Last Month":
                    last_month = today.replace(day=1) - timedelta(days=1)
                    if due_date.year == last_month.year and due_date.month == last_month.month:
                        filtered_bills.append(bill)
                        
                elif period == "Previous Month":
                    # Two months ago
                    prev_month = today.replace(day=1) - timedelta(days=1)
                    prev_month = prev_month.replace(day=1) - timedelta(days=1)
                    if due_date.year == prev_month.year and due_date.month == prev_month.month:
                        filtered_bills.append(bill)
                        
                elif period == "Next Month":
                    # Next month
                    if today.month == 12:
                        next_month = today.replace(year=today.year + 1, month=1, day=1)
                    else:
                        next_month = today.replace(month=today.month + 1, day=1)
                    if due_date.year == next_month.year and due_date.month == next_month.month:
                        filtered_bills.append(bill)
                        
                elif period == "This Year":
                    if due_date.year == today.year:
                        filtered_bills.append(bill)
                        
                elif period == "Last Year":
                    if due_date.year == today.year - 1:
                        filtered_bills.append(bill)
                        
            except ValueError:
                # Skip bills with invalid dates
                continue
        
        return filtered_bills
    
    def clear_all_filters(self):
        """
        Clear all active filters and search criteria.
        """
        self.search_var.set("")
        self.status_filter_var.set("Pending")
        self.period_filter_var.set("All")
        self._filtered_bills = [bill for bill in self._bills_data if not bill.get("paid", False) and not bill.get("payment_method_automatic", False)]
        
        # Clear selection and reset pagination when filters change
        self._selected_bills.clear()
        self._current_page = 1  # Reset to first page
        
        if self._sort_column:
            self.sort_by_column(self._sort_column)
        else:
            self.populate_bills_table(self._filtered_bills)
    
    def clear_search(self):
        """
        Clear the search field and reset search results.
        """
        self.search_var.set("")
        self.apply_filters()

    def populate_bills_table(self, bills):
        # Calculate pagination
        self._total_pages = max(1, (len(bills) + self._items_per_page - 1) // self._items_per_page)
        self._current_page = min(self._current_page, self._total_pages)
        
        # Get current page data
        start_index = (self._current_page - 1) * self._items_per_page
        end_index = start_index + self._items_per_page
        current_page_bills = bills[start_index:end_index]
        
        # Clear table
        for row in self.bills_table.get_children():
            self.bills_table.delete(row)
        self.bills_by_id = {}
        
        # Populate current page
        for i, bill in enumerate(current_page_bills):
            paid_status = "✓" if bill.get("paid", False) else "☐"
            category_name = bill.get("category_name", "Uncategorized")
            payment_method_name = bill.get("payment_method_name", "Not Set")
            
            # Determine status: Paid, Auto-Pay, or Pending
            if bill.get("paid", False):
                status = "Paid"
            elif bill.get("payment_method_automatic", False):
                status = "Auto-Pay"
            else:
                status = "Pending"
            
            # Check if this bill is selected
            select_status = "☑" if bill["id"] in self._selected_bills else "☐"
            
            row = (
                select_status,
                paid_status,
                bill.get("name", ""),
                bill.get("due_date", ""),
                bill.get("amount", ""),
                category_name,
                status,
                payment_method_name,
                bill.get("confirmation_number", "")
            )
            item_id = self.bills_table.insert("", "end", values=row)
            
            # Apply alternating row colors using tags
            if i % 2 == 1:  # Odd rows (0-indexed, so i=1,3,5...)
                self.bills_table.item(item_id, tags=("alternate",))
            
            self.bills_by_id[item_id] = bill
        
        # Update bills counter
        total_bills = len(self._bills_data)
        filtered_bills = len(bills)
        status_filter = self.status_filter_var.get()
        period_filter = self.period_filter_var.get()
        
        counter_text = f"Showing {filtered_bills} of {total_bills} bills"
        if status_filter != "All":
            counter_text += f" | Status: {status_filter}"
        if period_filter != "All":
            counter_text += f" | Period: {period_filter}"
        
        self.bills_counter_label.configure(text=counter_text)
        
        # Update pagination info and controls
        self.update_pagination_controls()

    def sort_by_column(self, col):
        """
        Sort the bills table by the specified column.

        Args:
            col (str): The column name to sort by.
        """
        col_map = {
            "Paid": "paid",
            "Name": "name",
            "Due Date": "due_date",
            "Amount": "amount",
            "Category": "category_name",
            "Status": "paid",
            "Confirmation": "confirmation_number"
        }
        key = col_map.get(col, col)
        reverse = False
        if self._sort_column == col:
            reverse = not self._sort_reverse
        self._sort_column = col
        self._sort_reverse = reverse
        # For status, sort by paid boolean
        if key == "paid":
            sorted_bills = sorted(self._filtered_bills, key=lambda b: b.get("paid", False), reverse=reverse)
        else:
            sorted_bills = sorted(self._filtered_bills, key=lambda b: (b.get(key) or ""), reverse=reverse)
        
        # Update filtered bills and maintain current page
        self._filtered_bills = sorted_bills
        self.populate_bills_table(self._filtered_bills)
        # Update header text to show sort order
        for c in ("Select", "Paid", "Name", "Due Date", "Amount", "Category", "Status", "Payment Method", "Confirmation"):
            arrow = ""
            if c == col:
                arrow = " ↓" if reverse else " ↑"
            if c == "Select":
                self.bills_table.heading(c, text="☐", command=self.toggle_select_all)
            else:
                self.bills_table.heading(c, text=c + arrow, command=lambda c=c: self.sort_by_column(c))

    def open_add_bill_dialog(self):
        AddBillDialog(self, self.show_bills_view)

    def show_categories_view(self):
        self.clear_content()
        
        # Configure grid for responsive layout
        self.content.grid_rowconfigure(2, weight=1)  # Table row gets the weight
        self.content.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(self.content, text="Categories Management", font=("Arial", 24, "bold"), text_color=TEXT_COLOR)
        title_label.grid(row=0, column=0, pady=(SPACING_MD, SPACING_SM))
        
        # Button frame with icons
        btn_frame = ctk.CTkFrame(self.content, fg_color=BACKGROUND_COLOR)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        
        add_category_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Add Category", icon_name=ICON_ADD, 
            command=self.open_add_category_dialog, fg_color=ACCENT_COLOR, text_color="white"
        )
        add_category_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        # Categories table frame
        table_frame = ctk.CTkFrame(self.content)
        table_frame.grid(row=2, column=0, sticky="nswe", padx=SPACING_SM, pady=(0, SPACING_SM))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Enhanced table styling for categories
        style = ttk.Style()
        
        # Configure Treeview style for categories table
        style.configure("Categories.Treeview",
                       background=BACKGROUND_COLOR,
                       foreground=TEXT_COLOR,
                       rowheight=30,
                       fieldbackground=BACKGROUND_COLOR,
                       borderwidth=1,
                       relief="solid")
        
        # Configure alternating row colors for categories using tags
        style.configure("Categories.Treeview",
                       background=BACKGROUND_COLOR,
                       foreground=TEXT_COLOR,
                       rowheight=30,
                       fieldbackground=BACKGROUND_COLOR,
                       borderwidth=1,
                       relief="solid")
        
        # Configure header style for categories
        style.configure("Categories.Treeview.Heading",
                       background=PRIMARY_COLOR,
                       foreground="white",
                       relief="flat",
                       borderwidth=1,
                       font=("Arial", 10, "bold"))
        
        # Configure header hover effect for categories
        style.map("Categories.Treeview.Heading",
                 background=[("active", SECONDARY_COLOR)])
        
        # Categories table
        columns = ("Name", "Color", "Description", "Bills Count")
        self.categories_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Categories.Treeview")
        
        # Configure tag colors for alternating rows
        self.categories_table.tag_configure("alternate", background="#f0f0f0")
        
        # Configure columns
        for col in columns:
            self.categories_table.heading(col, text=col)
            self.categories_table.column(col, width=150, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.categories_table.yview)
        self.categories_table.configure(yscrollcommand=scrollbar.set)
        self.categories_table.grid(row=0, column=0, sticky="nswe")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Action buttons with icons
        action_frame = ctk.CTkFrame(self.content, fg_color=BACKGROUND_COLOR)
        action_frame.grid(row=3, column=0, sticky="ew", pady=(0, SPACING_SM))
        
        edit_category_btn = icon_manager.get_button_with_icon(
            action_frame, text=" Edit", icon_name=ICON_EDIT, 
            command=self.edit_selected_category, fg_color=PRIMARY_COLOR, text_color="white"
        )
        edit_category_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        delete_category_btn = icon_manager.get_button_with_icon(
            action_frame, text=" Delete", icon_name=ICON_DELETE, 
            command=self.delete_selected_category, fg_color=ERROR_COLOR, text_color="white"
        )
        delete_category_btn.pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
        
        refresh_btn = icon_manager.get_button_with_icon(
            action_frame, text=" Refresh", icon_name=ICON_REFRESH, 
            command=self.refresh_categories, fg_color=SECONDARY_COLOR, text_color="white"
        )
        refresh_btn.pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
        
        # Populate categories
        self.populate_categories_table()

    def show_settings_view(self):
        """
        Display the settings view with theme, backup, notification, and database options.
        """
        self.clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content, 
            text="Settings", 
            font=("Arial", 24, "bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.pack(pady=(SPACING_LG, SPACING_MD))
        
        # Create scrollable settings frame
        settings_frame = ctk.CTkScrollableFrame(
            self.content,
            width=600,
            height=500
        )
        settings_frame.pack(pady=SPACING_MD, padx=SPACING_MD, fill="both", expand=True)
        
        # Theme Settings Section
        self._create_theme_section(settings_frame)
        
        # Backup Settings Section
        self._create_backup_section(settings_frame)
        
        # Notification Settings Section
        self._create_notification_section(settings_frame)
        
        # Database Settings Section
        self._create_database_section(settings_frame)
        
        # About Section
        self._create_about_section(settings_frame)
        
        # User Management Section (admin only)
        if auth_manager.is_admin(self.current_user):
            self._create_user_management_section(settings_frame)
    
    def _create_theme_section(self, parent):
        """
        Create theme settings section
        """
        # Theme section header
        theme_header = ctk.CTkLabel(
            parent,
            text="🎨 Theme Settings",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        theme_header.pack(pady=(SPACING_MD, SPACING_SM), anchor="w")
        
        # Theme selection frame
        theme_frame = ctk.CTkFrame(parent)
        theme_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Current theme label
        current_theme = ctk.get_appearance_mode()
        theme_label = ctk.CTkLabel(
            theme_frame,
            text=f"Current Theme: {current_theme.title()}",
            font=("Arial", 12)
        )
        theme_label.pack(pady=SPACING_SM)
        
        # Theme buttons frame
        theme_buttons_frame = ctk.CTkFrame(theme_frame)
        theme_buttons_frame.pack(pady=SPACING_SM)
        
        # Light theme button
        light_btn = ctk.CTkButton(
            theme_buttons_frame,
            text="Light Theme",
            command=lambda: self._change_theme("Light"),
            fg_color=PRIMARY_COLOR if current_theme == "Light" else "gray",
            width=120
        )
        light_btn.pack(side="left", padx=SPACING_SM)
        
        # Dark theme button
        dark_btn = ctk.CTkButton(
            theme_buttons_frame,
            text="Dark Theme",
            command=lambda: self._change_theme("Dark"),
            fg_color=PRIMARY_COLOR if current_theme == "Dark" else "gray",
            width=120
        )
        dark_btn.pack(side="left", padx=SPACING_SM)
        
        # System theme button
        system_btn = ctk.CTkButton(
            theme_buttons_frame,
            text="System Theme",
            command=lambda: self._change_theme("System"),
            fg_color=PRIMARY_COLOR if current_theme == "System" else "gray",
            width=120
        )
        system_btn.pack(side="left", padx=SPACING_SM)
        
        # Store buttons for updating colors
        self.theme_buttons = [light_btn, dark_btn, system_btn]
    
    def _create_backup_section(self, parent):
        """
        Create backup settings section
        """
        # Backup section header
        backup_header = ctk.CTkLabel(
            parent,
            text="💾 Backup & Restore",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        backup_header.pack(pady=(SPACING_LG, SPACING_SM), anchor="w")
        
        # Backup frame
        backup_frame = ctk.CTkFrame(parent)
        backup_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Backup buttons frame
        backup_buttons_frame = ctk.CTkFrame(backup_frame)
        backup_buttons_frame.pack(pady=SPACING_MD)
        
        # Export backup button
        export_btn = ctk.CTkButton(
            backup_buttons_frame,
            text="Export Database Backup",
            command=self._export_backup,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            width=200
        )
        export_btn.pack(side="left", padx=SPACING_SM)
        
        # Import backup button
        import_btn = ctk.CTkButton(
            backup_buttons_frame,
            text="Import Database Backup",
            command=self._import_backup,
            fg_color=WARNING_COLOR,
            text_color="white",
            width=200
        )
        import_btn.pack(side="left", padx=SPACING_SM)
        
        # Auto-backup toggle
        auto_backup_var = ctk.BooleanVar(value=self._get_auto_backup_setting())
        auto_backup_checkbox = ctk.CTkCheckBox(
            backup_frame,
            text="Enable automatic backups (weekly)",
            variable=auto_backup_var,
            command=lambda: self._toggle_auto_backup(auto_backup_var.get())
        )
        auto_backup_checkbox.pack(pady=SPACING_SM)
    
    def _create_notification_section(self, parent):
        """
        Create notification settings section
        """
        # Notification section header
        notification_header = ctk.CTkLabel(
            parent,
            text="🔔 Notification Settings",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        notification_header.pack(pady=(SPACING_LG, SPACING_SM), anchor="w")
        
        # Notification frame
        notification_frame = ctk.CTkFrame(parent)
        notification_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Check interval setting
        interval_frame = ctk.CTkFrame(notification_frame)
        interval_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        ctk.CTkLabel(
            interval_frame,
            text="Reminder Check Interval:",
            font=("Arial", 12)
        ).pack(side="left", padx=SPACING_SM)
        
        interval_var = ctk.StringVar(value=str(self._get_check_interval()))
        interval_entry = ctk.CTkEntry(
            interval_frame,
            textvariable=interval_var,
            width=80
        )
        interval_entry.pack(side="left", padx=SPACING_SM)
        
        ctk.CTkLabel(
            interval_frame,
            text="seconds (minimum 60)",
            font=("Arial", 10),
            text_color="gray"
        ).pack(side="left", padx=SPACING_SM)
        
        # Apply interval button
        apply_interval_btn = ctk.CTkButton(
            interval_frame,
            text="Apply",
            command=lambda: self._update_check_interval(interval_var.get()),
            width=80
        )
        apply_interval_btn.pack(side="right", padx=SPACING_SM)
        
        # Notification toggles
        toggles_frame = ctk.CTkFrame(notification_frame)
        toggles_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Enable notifications toggle
        notifications_var = ctk.BooleanVar(value=self._get_notifications_enabled())
        notifications_checkbox = ctk.CTkCheckBox(
            toggles_frame,
            text="Enable desktop notifications",
            variable=notifications_var,
            command=lambda: self._toggle_notifications(notifications_var.get())
        )
        notifications_checkbox.pack(pady=SPACING_SM)
        
        # Auto-close notifications toggle
        auto_close_var = ctk.BooleanVar(value=self._get_auto_close_notifications())
        auto_close_checkbox = ctk.CTkCheckBox(
            toggles_frame,
            text="Auto-close notifications after 30 seconds",
            variable=auto_close_var,
            command=lambda: self._toggle_auto_close_notifications(auto_close_var.get())
        )
        auto_close_checkbox.pack(pady=SPACING_SM)
    
    def _create_database_section(self, parent):
        """
        Create database settings section
        """
        # Database section header
        database_header = ctk.CTkLabel(
            parent,
            text="🗄️ Database Settings",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        database_header.pack(pady=(SPACING_LG, SPACING_SM), anchor="w")
        
        # Database frame
        database_frame = ctk.CTkFrame(parent)
        database_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Database info
        db_info_frame = ctk.CTkFrame(database_frame)
        db_info_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Get database statistics
        bill_count = len(self._bills_data) if hasattr(self, '_bills_data') else 0
        categories_count = len(fetch_all_categories()) if 'fetch_all_categories' in globals() else 0
        
        ctk.CTkLabel(
            db_info_frame,
            text=f"Total Bills: {bill_count}",
            font=("Arial", 12)
        ).pack(anchor="w", padx=SPACING_SM)
        
        ctk.CTkLabel(
            db_info_frame,
            text=f"Total Categories: {categories_count}",
            font=("Arial", 12)
        ).pack(anchor="w", padx=SPACING_SM)
        
        # Database actions frame
        db_actions_frame = ctk.CTkFrame(database_frame)
        db_actions_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Compact database button
        compact_btn = ctk.CTkButton(
            db_actions_frame,
            text="Compact Database",
            command=self._compact_database,
            fg_color=PRIMARY_COLOR,
            text_color="white",
            width=150
        )
        compact_btn.pack(side="left", padx=SPACING_SM)
        
        # Reset database button
        reset_btn = ctk.CTkButton(
            db_actions_frame,
            text="Reset Database",
            command=self._reset_database,
            fg_color=ERROR_COLOR,
            text_color="white",
            width=150
        )
        reset_btn.pack(side="left", padx=SPACING_SM)
    
    def _create_about_section(self, parent):
        """
        Create about section
        """
        # About section header
        about_header = ctk.CTkLabel(
            parent,
            text="ℹ️ About",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        about_header.pack(pady=(SPACING_LG, SPACING_SM), anchor="w")
        
        # About frame
        about_frame = ctk.CTkFrame(parent)
        about_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # App info
        ctk.CTkLabel(
            about_frame,
            text="Bills Tracker v3",
            font=("Arial", 14, "bold")
        ).pack(pady=SPACING_SM)
        
        ctk.CTkLabel(
            about_frame,
            text="A comprehensive desktop application for managing bills and payments",
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=SPACING_SM)
        
        ctk.CTkLabel(
            about_frame,
            text="Features: Bill management, categories, reminders, notifications, import/export",
            font=("Arial", 10),
            text_color="gray"
        ).pack(pady=SPACING_SM)
    
    def _create_user_management_section(self, parent):
        """
        Create user management section (admin only)
        """
        # User management section header
        user_header = ctk.CTkLabel(
            parent,
            text="👥 User Management",
            font=("Arial", 16, "bold"),
            text_color=PRIMARY_COLOR
        )
        user_header.pack(pady=(SPACING_LG, SPACING_SM), anchor="w")
        
        # User management frame
        user_frame = ctk.CTkFrame(parent)
        user_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Current user info
        if self.current_user:
            user_info = auth_manager.get_user_info(self.current_user['user_id'])
            if user_info:
                ctk.CTkLabel(
                    user_frame,
                    text=f"Current User: {user_info['username']} ({user_info['role']})",
                    font=("Arial", 12)
                ).pack(pady=SPACING_SM)
                
                ctk.CTkLabel(
                    user_frame,
                    text=f"Account created: {user_info['created_at'][:10]}",
                    font=("Arial", 10),
                    text_color="gray"
                ).pack(pady=SPACING_SM)
        
        # Admin actions frame
        admin_actions_frame = ctk.CTkFrame(user_frame)
        admin_actions_frame.pack(fill="x", pady=SPACING_SM, padx=SPACING_SM)
        
        # Create user button
        create_user_btn = ctk.CTkButton(
            admin_actions_frame,
            text="Create New User",
            command=self._show_create_user_dialog,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            width=150
        )
        create_user_btn.pack(side="left", padx=SPACING_SM)
        
        # Manage users button
        manage_users_btn = ctk.CTkButton(
            admin_actions_frame,
            text="Manage Users",
            command=self._show_manage_users_dialog,
            fg_color=PRIMARY_COLOR,
            text_color="white",
            width=150
        )
        manage_users_btn.pack(side="left", padx=SPACING_SM)
    
    def _show_create_user_dialog(self):
        """
        Show dialog to create a new user
        """
        from .login_dialog import RegisterDialog
        
        def on_success(username):
            show_popup(self, "Success", f"User '{username}' created successfully!", color="green")
        
        RegisterDialog(self, on_success)
    
    def _show_manage_users_dialog(self):
        """
        Show dialog to manage users
        """
        # This would be a more complex dialog showing all users
        # For now, just show a simple message
        show_popup(self, "Info", "User management dialog would be implemented here.", color="blue")
    
    def _change_theme(self, theme):
        """
        Change the application theme
        """
        try:
            if theme == "System":
                ctk.set_appearance_mode("System")
            else:
                ctk.set_appearance_mode(theme.lower())
            
            # Update button colors
            for btn in self.theme_buttons:
                if btn.cget("text").lower().startswith(theme.lower()):
                    btn.configure(fg_color=PRIMARY_COLOR)
                else:
                    btn.configure(fg_color="gray")
            
            # Save theme preference
            self._save_theme_preference(theme)
            
        except Exception as e:
            print(f"Error changing theme: {e}")
    
    def _export_backup(self):
        """
        Export database backup
        """
        try:
            from tkinter import filedialog
            import shutil
            import os
            
            # Get backup file path
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Export Database Backup"
            )
            
            if backup_path:
                # Copy database file
                shutil.copy2("bills_tracker.db", backup_path)
                show_popup(self, "Success", f"Database backup exported to:\n{backup_path}", color="green")
                
        except Exception as e:
            show_popup(self, "Error", f"Failed to export backup: {str(e)}", color="red")
    
    def _import_backup(self):
        """
        Import database backup
        """
        try:
            from tkinter import filedialog
            import shutil
            import os
            
            # Get backup file path
            backup_path = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Import Database Backup"
            )
            
            if backup_path:
                # Confirm import
                confirm = ctk.CTkToplevel(self)
                confirm.title("Confirm Import")
                confirm.geometry("400x200")
                
                ctk.CTkLabel(
                    confirm,
                    text="This will replace your current database.\nAre you sure you want to continue?",
                    font=("Arial", 12)
                ).pack(pady=SPACING_MD)
                
                def do_import():
                    try:
                        # Backup current database
                        if os.path.exists("bills_tracker.db"):
                            shutil.copy2("bills_tracker.db", "bills_tracker.db.backup")
                        
                        # Import new database
                        shutil.copy2(backup_path, "bills_tracker.db")
                        
                        # Refresh data
                        self._bills_data = fetch_all_bills()
                        self._filtered_bills = self._bills_data.copy()
                        self.show_bills_view()
                        
                        show_popup(self, "Success", "Database imported successfully!", color="green")
                        confirm.destroy()
                        
                    except Exception as e:
                        show_popup(self, "Error", f"Failed to import database: {str(e)}", color="red")
                        confirm.destroy()
                
                def cancel_import():
                    confirm.destroy()
                
                ctk.CTkButton(confirm, text="Import", fg_color="red", command=do_import).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
                ctk.CTkButton(confirm, text="Cancel", command=cancel_import).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
                
        except Exception as e:
            show_popup(self, "Error", f"Failed to import backup: {str(e)}", color="red")
    
    def _compact_database(self):
        """
        Compact the database to reduce file size
        """
        try:
            import sqlite3
            
            conn = sqlite3.connect("bills_tracker.db")
            conn.execute("VACUUM")
            conn.close()
            
            show_popup(self, "Success", "Database compacted successfully!", color="green")
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to compact database: {str(e)}", color="red")
    
    def _reset_database(self):
        """
        Reset the database (clear all data)
        """
        try:
            confirm = ctk.CTkToplevel(self)
            confirm.title("Confirm Reset")
            confirm.geometry("400x250")
            
            ctk.CTkLabel(
                confirm,
                text="⚠️ WARNING: This will delete ALL data!\n\nThis action cannot be undone.\n\nAre you absolutely sure?",
                font=("Arial", 12),
                text_color="red"
            ).pack(pady=SPACING_MD)
            
            def do_reset():
                try:
                    # Reinitialize database
                    from core.db import initialize_database
                    initialize_database()
                    
                    # Refresh data
                    self._bills_data = fetch_all_bills()
                    self._filtered_bills = self._bills_data.copy()
                    self.show_bills_view()
                    
                    show_popup(self, "Success", "Database reset successfully!", color="green")
                    confirm.destroy()
                    
                except Exception as e:
                    show_popup(self, "Error", f"Failed to reset database: {str(e)}", color="red")
                    confirm.destroy()
            
            def cancel_reset():
                confirm.destroy()
            
            ctk.CTkButton(confirm, text="RESET DATABASE", fg_color="red", command=do_reset).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkButton(confirm, text="Cancel", command=cancel_reset).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to reset database: {str(e)}", color="red")
    
    # Settings helper methods
    def _get_auto_backup_setting(self):
        """
        Get auto-backup setting from config
        """
        try:
            from core.config import config_manager
            return config_manager.get_auto_backup()
        except:
            return False
    
    def _toggle_auto_backup(self, enabled):
        """
        Toggle auto-backup setting
        """
        try:
            from core.config import config_manager
            config_manager.set_auto_backup(enabled)
        except Exception as e:
            print(f"Error toggling auto-backup: {e}")
    
    def _get_check_interval(self):
        """
        Get reminder check interval
        """
        try:
            from core.config import config_manager
            return config_manager.get_reminder_check_interval()
        except:
            return 300
    
    def _update_check_interval(self, interval_str):
        """
        Update reminder check interval
        """
        try:
            interval = int(interval_str)
            if interval < 60:
                show_popup(self, "Error", "Minimum interval is 60 seconds", color="red")
                return
            
            from core.config import config_manager
            config_manager.set_reminder_check_interval(interval)
            
            if hasattr(self, 'reminder_service'):
                self.reminder_service.check_interval = interval
            
            show_popup(self, "Success", f"Check interval updated to {interval} seconds", color="green")
                
        except ValueError:
            show_popup(self, "Error", "Please enter a valid number", color="red")
        except Exception as e:
            show_popup(self, "Error", f"Failed to update interval: {str(e)}", color="red")
    
    def _get_notifications_enabled(self):
        """
        Get notifications enabled setting
        """
        try:
            from core.config import config_manager
            return config_manager.get_notifications_enabled()
        except:
            return True
    
    def _toggle_notifications(self, enabled):
        """
        Toggle notifications
        """
        try:
            from core.config import config_manager
            config_manager.set_notifications_enabled(enabled)
        except Exception as e:
            print(f"Error toggling notifications: {e}")
    
    def _get_auto_close_notifications(self):
        """
        Get auto-close notifications setting
        """
        try:
            from core.config import config_manager
            return config_manager.get_auto_close_notifications()
        except:
            return True
    
    def _toggle_auto_close_notifications(self, enabled):
        """
        Toggle auto-close notifications
        """
        try:
            from core.config import config_manager
            config_manager.set_auto_close_notifications(enabled)
        except Exception as e:
            print(f"Error toggling auto-close notifications: {e}")
    
    def _save_theme_preference(self, theme):
        """
        Save theme preference
        """
        try:
            from core.config import config_manager
            config_manager.set_theme(theme)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def _check_authentication(self):
        """
        Check if user is authenticated
        """
        # For now, always show login dialog
        # In a real app, you'd check for saved session tokens
        self._show_login_dialog()
    
    def _show_login_dialog(self):
        """
        Show login dialog
        """
        LoginDialog(self, self._on_login_success)
    
    def _on_login_success(self, user_data):
        """
        Handle successful login
        """
        self.current_user = user_data
        self.session_token = user_data.get('session_token')
        
        # Update window title with username
        username = user_data.get('username', 'Guest')
        self.title(f"Bills Tracker v3 - {username}")
        
        # Update user info label
        role = user_data.get('role', 'user').title()
        self.user_info_label.configure(text=f"Logged in as: {username}\nRole: {role}")
        
        # Show bills view
        self.show_bills_view()
        
        # Show welcome message
        show_popup(self, "Welcome", f"Welcome back, {username}!", color="green")
    
    def _logout(self):
        """
        Logout current user
        """
        if self.session_token:
            auth_manager.logout(self.session_token)
        
        self.current_user = None
        self.session_token = None
        self.title("Bills Tracker v3")
        
        # Clear content and show login
        self.clear_content()
        self._show_login_dialog()
    
    def _show_change_password_dialog(self):
        """
        Show change password dialog
        """
        if self.current_user:
            ChangePasswordDialog(self, self.current_user['user_id'], self._on_password_changed)
    
    def _on_password_changed(self):
        """
        Handle successful password change
        """
        show_popup(self, "Success", "Password changed successfully!", color="green")

    def edit_selected_bill(self):
        selected = self.bills_table.selection()
        if not selected:
            return
        bill = self.bills_by_id[selected[0]]
        EditBillDialog(self, bill, self.show_bills_view)

    def delete_selected_bill(self):
        selected = self.bills_table.selection()
        if not selected:
            return
        bill = self.bills_by_id[selected[0]]
        
        try:
            # Confirmation dialog
            confirm = ctk.CTkToplevel(self)
            confirm.title("Confirm Delete")
            confirm.geometry("300x120")
            
            def safe_destroy():
                try:
                    if confirm.winfo_exists():
                        confirm.destroy()
                except:
                    pass
            
            ctk.CTkLabel(confirm, text=f"Delete bill '{bill.get('name', '')}'?").pack(pady=SPACING_SM)
            
            def do_delete():
                try:
                    delete_bill(bill["id"])
                    # Success popup removed for faster workflow
                    self.show_bills_view()
                except Exception as e:
                    show_popup(self, "Error", f"Failed to delete bill: {str(e)}", color="red")
                safe_destroy()
            
            ctk.CTkButton(confirm, text="Delete", fg_color="red", command=do_delete).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkButton(confirm, text="Cancel", command=safe_destroy).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
            
            # Use after() to delay the focus operations
            def set_focus():
                try:
                    if confirm.winfo_exists():
                        confirm.lift()
                        confirm.focus_force()
                        confirm.grab_set()
                except:
                    pass
            
            confirm.after(100, set_focus)
            
        except Exception as e:
            print(f"Delete confirm dialog error: {e}")
            # Fallback: delete directly
            try:
                delete_bill(bill["id"])
                # Success popup removed for faster workflow
                self.show_bills_view()
            except Exception as e:
                show_popup(self, "Error", f"Failed to delete bill: {str(e)}", color="red")

    def bulk_delete_selected_bills(self):
        """
        Delete multiple selected bills
        """
        if not self._selected_bills:
            # Info popup removed for faster workflow
            return
        
        selected_count = len(self._selected_bills)
        
        try:
            # Confirmation dialog
            confirm = ctk.CTkToplevel(self)
            confirm.title("Confirm Bulk Delete")
            confirm.geometry("400x150")
            
            def safe_destroy():
                try:
                    if confirm.winfo_exists():
                        confirm.destroy()
                except:
                    pass
            
            ctk.CTkLabel(confirm, text=f"Delete {selected_count} selected bill(s)?").pack(pady=SPACING_SM)
            ctk.CTkLabel(confirm, text="This action cannot be undone.", text_color="red").pack(pady=SPACING_SM)
            
            def do_bulk_delete():
                try:
                    deleted_count = 0
                    failed_count = 0
                    
                    # Delete each selected bill
                    for bill_id in self._selected_bills:
                        try:
                            delete_bill(bill_id)
                            deleted_count += 1
                        except Exception as e:
                            failed_count += 1
                            print(f"Failed to delete bill {bill_id}: {e}")
                    
                    # Clear selection
                    self._selected_bills.clear()
                    
                    # Refresh the view
                    self.show_bills_view()
                    
                    # Show result
                    # Success popup removed for faster workflow
                    
                except Exception as e:
                    show_popup(self, "Error", f"Failed to delete bills: {str(e)}", color="red")
                safe_destroy()
            
            def cancel_bulk_delete():
                safe_destroy()
            
            # Buttons
            button_frame = ctk.CTkFrame(confirm)
            button_frame.pack(pady=SPACING_MD)
            
            ctk.CTkButton(button_frame, text="Delete All", fg_color="red", command=do_bulk_delete).pack(side="left", padx=SPACING_SM)
            ctk.CTkButton(button_frame, text="Cancel", command=cancel_bulk_delete).pack(side="right", padx=SPACING_SM)
            
            # Use after() to delay the focus operations
            def set_focus():
                try:
                    if confirm.winfo_exists():
                        confirm.lift()
                        confirm.focus_force()
                        confirm.grab_set()
                except:
                    pass
            
            confirm.after(100, set_focus)
            
        except Exception as e:
            print(f"Bulk delete confirm dialog error: {e}")
            show_popup(self, "Error", f"Failed to show confirmation dialog: {str(e)}", color="red")

    def export_bills(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Bills to CSV"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'due_date', 'billing_cycle', 'reminder_days', 'web_page', 
                             'company_email', 'support_phone', 'account_number', 'paid', 'payment_method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for bill in self._bills_data:
                    writer.writerow({
                        'name': bill.get('name', ''),
                        'due_date': bill.get('due_date', ''),
                        'billing_cycle': bill.get('billing_cycle', ''),
                        'reminder_days': bill.get('reminder_days', ''),
                        'web_page': bill.get('web_page', ''),
                        'company_email': bill.get('company_email', ''),
                        'support_phone': bill.get('support_phone', ''),
                        'account_number': bill.get('account_number', ''),
                        'paid': 'Yes' if bill.get('paid', False) else 'No',
                        'payment_method': bill.get('payment_method_name', 'Not Set')
                    })
            
            # Success popup removed for faster workflow
        except Exception as e:
            show_popup(self, "Error", f"Failed to export bills: {str(e)}", color="red")

    def import_bills(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Bills from CSV"
        )
        if not file_path:
            return
        
        try:
            imported_count = 0
            skipped_count = 0
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Basic validation
                    if not row.get('name') or not row.get('due_date'):
                        skipped_count += 1
                        continue
                    
                    # Check for duplicate by name and due date
                    is_duplicate = False
                    for existing_bill in self._bills_data:
                        if (existing_bill.get('name') == row['name'] and 
                            existing_bill.get('due_date') == row['due_date']):
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        skipped_count += 1
                        continue
                    
                    # Prepare bill data
                    bill_data = {
                        'name': row.get('name', ''),
                        'due_date': row.get('due_date', ''),
                        'billing_cycle': row.get('billing_cycle', 'monthly'),
                        'reminder_days': int(row.get('reminder_days', 7)),
                        'web_page': row.get('web_page', ''),
                        'company_email': row.get('company_email', ''),
                        'support_phone': row.get('support_phone', ''),
                        'account_number': row.get('account_number', ''),
                        'paid': row.get('paid', 'No').lower() == 'yes',
                        'payment_method_name': row.get('payment_method', 'Not Set')
                    }
                    
                    insert_bill(bill_data)
                    imported_count += 1
            
            # Refresh the bills data and table
            self._bills_data = fetch_all_bills()
            self._filtered_bills = self._bills_data.copy()
            if self._sort_column:
                self.sort_by_column(self._sort_column)
            else:
                self.populate_bills_table(self._filtered_bills)
            
            # Success popup removed for faster workflow
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to import bills: {str(e)}", color="red")

    def on_table_click(self, event):
        """
        Handle table click events for selection and actions.

        Args:
            event: The click event object.
        """
        region = self.bills_table.identify("region", event.x, event.y)
        if region == "cell":
            column = self.bills_table.identify_column(event.x)
            item = self.bills_table.identify_row(event.y)
            
            if not item:
                return
                
            if column == "#1":  # Select column
                self.toggle_bill_selection(item)
            elif column == "#2":  # Paid column (now second column)
                self.toggle_paid_status(item)
    
    def toggle_bill_selection(self, item_id):
        """
        Toggle the selection state of a bill in the table.

        Args:
            item_id: The ID of the bill to toggle selection for.
        """
        if item_id in self.bills_by_id:
            bill = self.bills_by_id[item_id]
            bill_id = bill["id"]
            
            if bill_id in self._selected_bills:
                self._selected_bills.remove(bill_id)
                select_status = "☐"
            else:
                self._selected_bills.add(bill_id)
                select_status = "☑"
            
            # Update the display
            values = list(self.bills_table.item(item_id, "values"))
            values[0] = select_status  # Update select column
            self.bills_table.item(item_id, values=values)
            
            # Update bulk delete button state
            self.update_bulk_actions()
    
    def toggle_select_all(self):
        """
        Toggle selection of all visible bills on the current page.
        """
        all_items = self.bills_table.get_children()
        if not all_items:
            return
        
        # Check if all are selected
        all_selected = True
        for item_id in all_items:
            bill = self.bills_by_id[item_id]
            if bill["id"] not in self._selected_bills:
                all_selected = False
                break
        
        # Toggle selection
        if all_selected:
            # Deselect all visible bills
            for item_id in all_items:
                bill = self.bills_by_id[item_id]
                self._selected_bills.discard(bill["id"])
            select_status = "☐"
            header_text = "☐"
        else:
            # Select all visible bills
            for item_id in all_items:
                bill = self.bills_by_id[item_id]
                self._selected_bills.add(bill["id"])
            select_status = "☑"
            header_text = "☑"
        
        # Update all rows
        for item_id in all_items:
            values = list(self.bills_table.item(item_id, "values"))
            values[0] = select_status
            self.bills_table.item(item_id, values=values)
        
        # Update header
        self.bills_table.heading("Select", text=header_text, command=self.toggle_select_all)
        
        # Update bulk delete button state
        self.update_bulk_actions()
    
    def update_bulk_actions(self):
        """
        Update the state of bulk action buttons based on selection
        """
        selected_count = len(self._selected_bills)
        if selected_count > 0:
            self.bulk_delete_btn.configure(text=f"Delete Selected ({selected_count})", state="normal")
        else:
            self.bulk_delete_btn.configure(text="Delete Selected", state="disabled")
    
    def update_pagination_controls(self):
        """
        Update the pagination controls with current page information.
        """
        try:
            # Update pagination info
            if hasattr(self, 'pagination_info_label') and self.pagination_info_label.winfo_exists():
                total_filtered = len(self._filtered_bills)
                start_item = (self._current_page - 1) * self._items_per_page + 1
                end_item = min(self._current_page * self._items_per_page, total_filtered)
                
                if total_filtered == 0:
                    pagination_text = "No bills to display"
                else:
                    pagination_text = f"Page {self._current_page} of {self._total_pages} | Showing {start_item}-{end_item} of {total_filtered} bills"
                
                self.pagination_info_label.configure(text=pagination_text)
            
            # Update navigation button states
            if hasattr(self, 'first_page_btn') and self.first_page_btn.winfo_exists():
                self.first_page_btn.configure(state="normal" if self._current_page > 1 else "disabled")
                self.prev_page_btn.configure(state="normal" if self._current_page > 1 else "disabled")
                self.next_page_btn.configure(state="normal" if self._current_page < self._total_pages else "disabled")
                self.last_page_btn.configure(state="normal" if self._current_page < self._total_pages else "disabled")
        except Exception as e:
            # Silently ignore errors during initialization
            pass
    
    def go_to_first_page(self):
        """
        Navigate to the first page of results.
        """
        if self._current_page != 1:
            self._current_page = 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_prev_page(self):
        """
        Navigate to the previous page of results.
        """
        if self._current_page > 1:
            self._current_page -= 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_next_page(self):
        """
        Navigate to the next page of results.
        """
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_last_page(self):
        """
        Navigate to the last page of results.
        """
        if self._current_page != self._total_pages:
            self._current_page = self._total_pages
            self.populate_bills_table(self._filtered_bills)
    
    def on_items_per_page_change(self, event=None):
        """
        Handle change in items per page setting.

        Args:
            event: The change event (optional).
        """
        try:
            new_items_per_page = int(self.items_per_page_var.get())
            if new_items_per_page != self._items_per_page:
                self._items_per_page = new_items_per_page
                self._current_page = 1  # Reset to first page
                self.populate_bills_table(self._filtered_bills)
        except ValueError:
            # If conversion fails, revert to current value
            self.items_per_page_var.set(str(self._items_per_page))
    
    def toggle_paid_status(self, item_id):
        """
        Toggle the paid status of a bill.

        Args:
            item_id: The ID of the bill to toggle paid status for.
        """
        if item_id in self.bills_by_id:
            bill = self.bills_by_id[item_id]
            current_paid = bill.get("paid", False)
            new_paid = not current_paid
            
            if new_paid:
                # Mark as paid immediately, no confirmation popup
                pending_bill = bill.copy()
                pending_bill["paid"] = True
                pending_bill["confirmation_number"] = ""  # No confirmation number
                self.pending_changes[item_id] = pending_bill
                paid_status = "✓"
                values = list(self.bills_table.item(item_id, "values"))
                values[1] = paid_status  # Update paid column (now second column)
                values[6] = "Paid"  # Update status column
                self.bills_table.item(item_id, values=values)
                pending_count = len(self.pending_changes)
                if pending_count > 0:
                    self.apply_btn.configure(text=f"Apply Changes ({pending_count})", fg_color="orange")
                else:
                    self.apply_btn.configure(text="Apply Changes", fg_color="green")
            else:
                # Marking as unpaid - no confirmation needed
                pending_bill = bill.copy()
                pending_bill["paid"] = False
                pending_bill["confirmation_number"] = ""  # Clear confirmation number
                self.pending_changes[item_id] = pending_bill
                paid_status = "☐"
                values = list(self.bills_table.item(item_id, "values"))
                values[1] = paid_status  # Update paid column (now second column)
                values[6] = "Pending"  # Update status column
                self.bills_table.item(item_id, values=values)
                pending_count = len(self.pending_changes)
                if pending_count > 0:
                    self.apply_btn.configure(text=f"Apply Changes ({pending_count})", fg_color="orange")
                else:
                    self.apply_btn.configure(text="Apply Changes", fg_color="green")
    
    def _calculate_next_due_date(self, current_due_date, billing_cycle):
        """
        Calculate the next due date based on billing cycle.

        Args:
            current_due_date (str): Current due date in YYYY-MM-DD format.
            billing_cycle (str): The billing cycle (weekly, monthly, etc.).

        Returns:
            str: Next due date in YYYY-MM-DD format.
        """
        try:
            current_date = datetime.strptime(current_due_date, "%Y-%m-%d")
        except ValueError:
            return current_due_date
        
        if billing_cycle == "weekly":
            next_date = current_date + timedelta(weeks=1)
        elif billing_cycle == "bi-weekly":
            next_date = current_date + timedelta(weeks=2)
        elif billing_cycle == "monthly":
            # Add one month, handling year rollover
            if current_date.month == 12:
                next_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                next_date = current_date.replace(month=current_date.month + 1)
        elif billing_cycle == "quarterly":
            # Add 3 months
            new_month = current_date.month + 3
            new_year = current_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            next_date = current_date.replace(year=new_year, month=new_month)
        elif billing_cycle == "semi-annually":
            # Add 6 months
            new_month = current_date.month + 6
            new_year = current_date.year + (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            next_date = current_date.replace(year=new_year, month=new_month)
        elif billing_cycle == "annually":
            next_date = current_date.replace(year=current_date.year + 1)
        else:  # one-time or unknown
            return current_due_date
        
        return next_date.strftime("%Y-%m-%d")
    
    def apply_pending_changes(self):
        """
        Apply all pending changes to bills in the database.
        """
        if not self.pending_changes:
            # Info popup removed for faster workflow
            return
        
        try:
            applied_count = 0
            new_bills_created = 0
            
            for item_id, pending_bill in self.pending_changes.items():
                # Update the current bill in the database (mark as paid)
                update_bill(pending_bill["id"], pending_bill)
                
                # Update the main bills data
                for i, main_bill in enumerate(self._bills_data):
                    if main_bill["id"] == pending_bill["id"]:
                        self._bills_data[i] = pending_bill.copy()
                        break
                
                # Update the bills_by_id reference
                self.bills_by_id[item_id] = pending_bill.copy()
                
                # If the bill was marked as paid, create a new bill for the next cycle
                if pending_bill.get("paid", False):
                    # Get the original bill data to calculate the next due date
                    original_bill = None
                    for main_bill in self._bills_data:
                        if main_bill["id"] == pending_bill["id"]:
                            original_bill = main_bill
                            break
                    
                    if original_bill:
                        # Calculate the next due date based on the original bill's due date and billing cycle
                        next_due_date = self._calculate_next_due_date(
                            original_bill.get("due_date", ""), 
                            original_bill.get("billing_cycle", "monthly")
                        )
                        
                        # Create new bill data for next cycle
                        next_bill_data = pending_bill.copy()
                        next_bill_data["paid"] = False  # New bill is unpaid
                        next_bill_data["due_date"] = next_due_date  # Use the calculated next due date
                        
                        # Remove the id so it creates a new entry
                        if "id" in next_bill_data:
                            del next_bill_data["id"]
                        
                        # Insert the new bill into the database
                        insert_bill(next_bill_data)
                        new_bills_created += 1
                
                applied_count += 1
            
            # Clear pending changes
            self.pending_changes.clear()
            
            # Reset button appearance
            self.apply_btn.configure(text="Apply Changes", fg_color="green")
            
            # Refresh the data to show the new bills
            self._bills_data = fetch_all_bills()
            self._filtered_bills = self._bills_data.copy()
            if self._sort_column:
                self.sort_by_column(self._sort_column)
            else:
                self.populate_bills_table(self._filtered_bills)
            
            # Success popup removed for faster workflow
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to apply changes: {str(e)}", color="red")
    
    def refresh_bills_data(self):
        """
        Refresh the bills data with confirmation dialog.
        """
        # Check if there are pending changes
        if self.pending_changes:
            # Ask user if they want to discard pending changes
            try:
                confirm = ctk.CTkToplevel(self)
                confirm.title("Confirm Refresh")
                confirm.geometry("400x150")
                
                def safe_destroy():
                    try:
                        if confirm.winfo_exists():
                            confirm.destroy()
                    except:
                        pass
                
                ctk.CTkLabel(confirm, text=f"You have {len(self.pending_changes)} pending changes.\nDo you want to discard them and refresh?", 
                            font=("Arial", 12)).pack(pady=SPACING_SM)
                
                def do_refresh():
                    try:
                        self._bills_data = fetch_all_bills()
                        self._filtered_bills = self._bills_data.copy()
                        if self._sort_column:
                            self.sort_by_column(self._sort_column)
                        else:
                            self.populate_bills_table(self._filtered_bills)
                        # Clear pending changes
                        self.pending_changes.clear()
                        self.apply_btn.configure(text="Apply Changes", fg_color="green")
                        # Success popup removed for faster workflow
                    except Exception as e:
                        show_popup(self, "Error", f"Failed to refresh data: {str(e)}", color="red")
                    safe_destroy()
                
                def cancel_refresh():
                    safe_destroy()
                
                ctk.CTkButton(confirm, text="Discard & Refresh", fg_color="red", command=do_refresh).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
                ctk.CTkButton(confirm, text="Cancel", command=cancel_refresh).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
                
                # Use after() to delay the focus operations
                def set_focus():
                    try:
                        if confirm.winfo_exists():
                            confirm.lift()
                            confirm.focus_force()
                            confirm.grab_set()
                    except:
                        pass
                
                confirm.after(100, set_focus)
                
            except Exception as e:
                print(f"Confirm dialog error: {e}")
                # Fallback: refresh directly
                self._refresh_data_direct()
        else:
            # No pending changes, refresh directly
            self._refresh_data_direct()
    
    def _refresh_data_direct(self):
        """
        Refresh bills data directly without confirmation.
        """
        try:
            self._bills_data = fetch_all_bills()
            self._filtered_bills = self._bills_data.copy()
            if self._sort_column:
                self.sort_by_column(self._sort_column)
            else:
                self.populate_bills_table(self._filtered_bills)
            # Success popup removed for faster workflow
        except Exception as e:
            show_popup(self, "Error", f"Failed to refresh data: {str(e)}", color="red")

    # Category management methods
    def populate_categories_table(self):
        """
        Populate the categories table with current data.
        """
        for row in self.categories_table.get_children():
            self.categories_table.delete(row)
        
        try:
            categories = fetch_all_categories()
            for i, category in enumerate(categories):
                # Count bills in this category
                bill_count = sum(1 for bill in self._bills_data if bill.get('category_id') == category['id'])
                
                row = (
                    category['name'],
                    category['color'],
                    category.get('description', ''),
                    str(bill_count)
                )
                item_id = self.categories_table.insert("", "end", values=row)
                
                # Apply alternating row colors using tags
                if i % 2 == 1:  # Odd rows (0-indexed, so i=1,3,5...)
                    self.categories_table.item(item_id, tags=("alternate",))
                    
        except Exception as e:
            print(f"Error populating categories table: {e}")

    def open_add_category_dialog(self):
        """
        Open the dialog for adding a new category.
        """
        AddCategoryDialog(self, self.refresh_categories)

    def edit_selected_category(self):
        """
        Open the edit dialog for the currently selected category.
        """
        selected = self.categories_table.selection()
        if not selected:
            # Info popup removed for faster workflow
            return
        
        # Get category data
        category_name = self.categories_table.item(selected[0], "values")[0]
        categories = fetch_all_categories()
        category_data = None
        for cat in categories:
            if cat['name'] == category_name:
                category_data = cat
                break
        
        if category_data:
            EditCategoryDialog(self, category_data, self.refresh_categories)
        else:
            show_popup(self, "Error", "Category not found.", color="red")

    def delete_selected_category(self):
        """
        Delete the currently selected category with confirmation dialog.
        """
        selected = self.categories_table.selection()
        if not selected:
            # Info popup removed for faster workflow
            return
        
        category_name = self.categories_table.item(selected[0], "values")[0]
        
        # Check if category is in use
        bill_count = int(self.categories_table.item(selected[0], "values")[3])
        if bill_count > 0:
            show_popup(self, "Error", f"Cannot delete category '{category_name}' because it has {bill_count} bills assigned to it.", color="red")
            return
        
        # Confirmation dialog
        try:
            confirm = ctk.CTkToplevel(self)
            confirm.title("Confirm Delete")
            confirm.geometry("400x150")
            
            def safe_destroy():
                try:
                    if confirm.winfo_exists():
                        confirm.destroy()
                except:
                    pass
            
            ctk.CTkLabel(confirm, text=f"Delete category '{category_name}'?", font=("Arial", 12)).pack(pady=SPACING_SM)
            
            def do_delete():
                try:
                    from db import delete_category
                    categories = fetch_all_categories()
                    category_id = None
                    for cat in categories:
                        if cat['name'] == category_name:
                            category_id = cat['id']
                            break
                    
                    if category_id:
                        delete_category(category_id)
                        # Success popup removed for faster workflow
                        self.refresh_categories()
                    else:
                        show_popup(self, "Error", "Category not found.", color="red")
                except Exception as e:
                    show_popup(self, "Error", f"Failed to delete category: {str(e)}", color="red")
                safe_destroy()
            
            ctk.CTkButton(confirm, text="Delete", fg_color="red", command=do_delete).pack(side="left", padx=SPACING_SM, pady=SPACING_SM)
            ctk.CTkButton(confirm, text="Cancel", command=safe_destroy).pack(side="right", padx=SPACING_SM, pady=SPACING_SM)
            
            def set_focus():
                try:
                    if confirm.winfo_exists():
                        confirm.lift()
                        confirm.focus_force()
                        confirm.grab_set()
                except:
                    pass
            
            confirm.after(100, set_focus)
            
        except Exception as e:
            print(f"Delete confirm dialog error: {e}")

    def refresh_categories(self):
        """
        Refresh the categories table with current data.
        """
        self.populate_categories_table()

    def _on_close(self):
        """
        Handle window close event with cleanup and configuration saving.
        """
        try:
            # Save window size
            if hasattr(self, 'config_manager') and self.config_manager:
                try:
                    width = self.winfo_width()
                    height = self.winfo_height()
                    self.config_manager.set_window_size(width, height)
                except Exception as e:
                    print(f"Error saving window size: {e}")
            
            # Stop reminder service with shorter timeout
            if hasattr(self, 'reminder_service'):
                self.reminder_service.stop()
            
            # Close all notifications quickly
            if hasattr(self, 'notification_manager'):
                self.notification_manager.close_all_notifications()
            
            # Quick cleanup - don't wait for all after() calls
            self.quit()
        except Exception as e:
            print(f"Error during close: {e}")
        finally:
            try:
                self.destroy()
            except:
                pass
                
    def _handle_reminder_notification(self, notification_data):
        """
        Handle reminder notifications from the reminder service.
        
        Args:
            notification_data: Dictionary containing notification information
        """
        try:
            # Show notification using the notification manager
            self.notification_manager.show_notification(
                notification_data,
                on_mark_paid=self._mark_bill_as_paid_from_notification,
                on_snooze=self._snooze_reminder_from_notification
            )
        except Exception as e:
            print(f"Error handling reminder notification: {e}")
            # Fallback: just print the notification
            print(f"NOTIFICATION: {notification_data.get('message', 'Bill reminder')}")
            
    def _mark_bill_as_paid_from_notification(self, bill_id):
        """
        Mark a bill as paid from notification.
        
        Args:
            bill_id: ID of the bill to mark as paid
        """
        try:
            # Find the bill in current data
            bill = None
            for b in self._bills_data:
                if b['id'] == bill_id:
                    bill = b
                    break
            
            if bill:
                # Mark as paid
                bill['paid'] = True
                bill['confirmation_number'] = f"PAID-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                # Update in database
                update_bill(bill_id, bill)
                
                # Refresh the view
                self.show_bills_view()
                
                # Do NOT show a success popup
            else:
                show_popup(self, "Error", "Bill not found!", color="red")
        except Exception as e:
            show_popup(self, "Error", f"Failed to mark bill as paid: {str(e)}", color="red")
            
    def _snooze_reminder_from_notification(self, bill_id, snooze_seconds):
        """
        Snooze a reminder from notification.
        
        Args:
            bill_id: ID of the bill to snooze
            snooze_seconds: Number of seconds to snooze
        """
        try:
            # Mark the reminder as sent to prevent immediate re-triggering
            # The reminder service will check again after the snooze period
            bill = None
            for b in self._bills_data:
                if b['id'] == bill_id:
                    bill = b
                    break
                    
            if bill:
                self.reminder_service.mark_reminder_sent(bill_id, bill['due_date'])
                # Info popup removed for faster workflow
            else:
                show_popup(self, "Error", "Bill not found!", color="red")
                
        except Exception as e:
            show_popup(self, "Error", f"Failed to snooze reminder: {str(e)}", color="red")

# Add this function near the top of the file (after color constants)
def is_dark_mode():
    """
    Check if the application is currently in dark mode.

    Returns:
        bool: True if dark mode is active, False otherwise.
    """
    mode = ctk.get_appearance_mode()
    return mode.lower() == "dark"

if __name__ == "__main__":
    app = MainWindow()
    try:
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc() 