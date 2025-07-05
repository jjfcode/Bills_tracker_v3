import customtkinter as ctk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from db import fetch_all_bills, insert_bill, update_bill, delete_bill, fetch_all_categories, fetch_all_payment_methods
from datetime import datetime, timedelta
from tkinter import StringVar
from tkinter import IntVar
import re
import csv
from tkinter import filedialog
from tkcalendar import DateEntry
from tkinter import messagebox
from .icon_utils import icon_manager, ICON_ADD, ICON_EDIT, ICON_DELETE, ICON_SAVE, ICON_CANCEL, ICON_SEARCH, ICON_CALENDAR, ICON_EXPORT, ICON_IMPORT, ICON_REFRESH, ICON_SETTINGS, ICON_CATEGORIES, ICON_BILLS, ICON_APPLY, ICON_CLEAR
from .validation import BillValidator, CategoryValidator, ValidationError, validate_field_in_real_time

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
DISABLED_COLOR = "#b0b0b0"

SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24

def show_popup(master, title, message, color="green"):
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
    """Custom frame for date selection with calendar and quick options"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.selected_date = StringVar()
        self._setup_ui()
    
    def _setup_ui(self):
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
        """Show calendar dialog for date selection"""
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
        """Fallback simple date picker"""
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
        """Get the selected date as string"""
        return self.selected_date.get()
    
    def set_date(self, date_str):
        """Set the date from string"""
        self.selected_date.set(date_str)

class AddBillDialog(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Add Bill")
        self.geometry("550x700")
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
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
        """Load categories into the dropdown"""
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
        """Add a new bill with comprehensive validation"""
        try:
            # Collect all field values
            bill_data = {
                "name": self.name_entry.get().strip(),
                "due_date": self.date_selector.get_date().strip(),
                "paid": self.paid_var.get(),
                "confirmation_number": self.confirmation_entry.get().strip(),
                "billing_cycle": self.billing_cycle_var.get(),
                "reminder_days": self.reminder_days_var.get(),
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
            show_popup(self, "Success", "Bill added successfully!", color="green")
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

class EditBillDialog(ctk.CTkToplevel):
    def __init__(self, master, bill_data, on_success):
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
        """Load categories into the dropdown"""
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
        """Save bill changes with comprehensive validation"""
        try:
            # Collect all field values
            bill_data = {
                "name": self.name_entry.get().strip(),
                "due_date": self.date_selector.get_date().strip(),
                "paid": self.paid_var.get(),
                "confirmation_number": self.confirmation_entry.get().strip(),
                "billing_cycle": self.billing_cycle_var.get(),
                "reminder_days": self.reminder_days_var.get(),
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
            show_popup(self, "Success", "Bill updated successfully!", color="green")
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

class AddCategoryDialog(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.title("Add Category")
        self.geometry("400x300")
        self.on_success = on_success
        self._setup_ui()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
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
        """Add a new category with comprehensive validation"""
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
            show_popup(self, "Success", "Category added successfully!", color="green")
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
    def __init__(self, master, category_data, on_success):
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
        self.error_label.grid(row=row, column=0, columnspan=2)
        row += 1
        
        # Save button with icon
        self.save_button = icon_manager.get_button_with_icon(
            self, text=" Save Changes", icon_name=ICON_SAVE, 
            command=self._on_save, fg_color=ACCENT_COLOR, text_color="white"
        )
        self.save_button.grid(row=row, column=0, columnspan=2, pady=SPACING_MD)

    def _on_save(self):
        """Save category changes with comprehensive validation"""
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
            show_popup(self, "Success", "Category updated successfully!", color="green")
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
    def __init__(self):
        super().__init__()
        self.title("Bills Tracker v3")
        self.geometry("1200x800")
        self.minsize(800, 600)  # Set minimum window size for responsive design

        # Configure the main window
        self.configure(bg_color=BACKGROUND_COLOR)
        
        # Cerrar toda la app si se cierra la ventana principal
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Inicializar pending_changes para evitar errores
        self.pending_changes = {}
        self._selected_bills = set()  # Track selected bill IDs for bulk operations
        
        # Pagination variables
        self._current_page = 1
        self._items_per_page = 20  # Default items per page
        self._total_pages = 1
        
        # Setup UI
        self._setup_ui()
        
        # Show bills view by default
        self.show_bills_view()
    
    def _setup_ui(self):
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
        
        # Configure grid for responsive layout
        self.content.grid_rowconfigure(3, weight=1)  # Table row gets the weight
        self.content.grid_columnconfigure(0, weight=1)
        
        # Button frame for Add, Export, Import with icons
        btn_frame = ctk.CTkFrame(self.content, fg_color=BACKGROUND_COLOR)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        btn_frame.grid_columnconfigure(3, weight=1)
        
        add_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Add Bill", icon_name=ICON_ADD, 
            command=self.open_add_bill_dialog, fg_color=ACCENT_COLOR, text_color="white"
        )
        add_btn.grid(row=0, column=0, padx=(0, SPACING_SM), pady=SPACING_SM)
        
        export_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Export CSV", icon_name=ICON_EXPORT, 
            command=self.export_bills, fg_color=SECONDARY_COLOR, text_color="white"
        )
        export_btn.grid(row=0, column=1, padx=(0, SPACING_SM), pady=SPACING_SM)
        
        import_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Import CSV", icon_name=ICON_IMPORT, 
            command=self.import_bills, fg_color=SECONDARY_COLOR, text_color="white"
        )
        import_btn.grid(row=0, column=2, padx=(0, SPACING_SM), pady=SPACING_SM)

        # Filter options frame
        filter_frame = ctk.CTkFrame(self.content)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # Status filter (Pending/Auto-Pay/Paid/All)
        ctk.CTkLabel(filter_frame, text="Status:").grid(row=0, column=0, padx=(SPACING_SM, SPACING_SM), pady=SPACING_SM)
        self.status_filter_var = ctk.StringVar(value="Pending")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var,
                                   values=["Pending", "Auto-Pay", "Paid", "All"], state="readonly", width=12)
        status_combo.grid(row=0, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="w")
        status_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Period filter
        ctk.CTkLabel(filter_frame, text="Period:").grid(row=0, column=2, padx=(SPACING_MD, SPACING_SM), pady=SPACING_SM)
        self.period_filter_var = ctk.StringVar(value="All")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_filter_var,
                                   values=["All", "This Month", "Last Month", "Previous Month", "Next Month", "This Year", "Last Year"], 
                                   state="readonly", width=15)
        period_combo.grid(row=0, column=3, padx=SPACING_SM, pady=SPACING_SM)
        period_combo.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Clear filters button
        clear_btn = ctk.CTkButton(filter_frame, text="Clear All", command=self.clear_all_filters, width=80)
        clear_btn.grid(row=0, column=4, padx=SPACING_SM, pady=SPACING_SM)

        # Search bar
        search_frame = ctk.CTkFrame(self.content)
        search_frame.grid(row=2, column=0, sticky="ew", padx=SPACING_SM, pady=(0, SPACING_SM))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search:").grid(row=0, column=0, padx=(SPACING_SM, SPACING_SM), pady=SPACING_SM)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        self.search_var.trace("w", self.apply_filters)
        
        self.search_field_var = ctk.StringVar(value="Name")
        search_field_combo = ttk.Combobox(search_frame, textvariable=self.search_field_var, 
                                         values=["Name", "Due Date", "Category", "Status", "Paid", "Confirmation"], 
                                         state="readonly", width=15)
        search_field_combo.grid(row=0, column=2, padx=SPACING_SM, pady=SPACING_SM)
        
        clear_search_btn = ctk.CTkButton(search_frame, text="Clear Search", command=self.clear_search, width=100)
        clear_search_btn.grid(row=0, column=3, padx=SPACING_SM, pady=SPACING_SM)

        self.bills_table_frame = ctk.CTkFrame(self.content)
        self.bills_table_frame.grid(row=2, column=0, sticky="nswe")
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
        
        # Edit, Delete, Apply, and Refresh buttons with icons
        action_btn_frame = ctk.CTkFrame(self.content, fg_color=BACKGROUND_COLOR)
        action_btn_frame.grid(row=4, column=0, sticky="ew", pady=(SPACING_SM, 0))
        
        edit_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Edit", icon_name=ICON_EDIT, 
            command=self.edit_selected_bill, fg_color=PRIMARY_COLOR, text_color="white"
        )
        edit_btn.pack(side="left", padx=SPACING_SM)
        
        delete_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Delete", icon_name=ICON_DELETE, 
            command=self.delete_selected_bill, fg_color=ERROR_COLOR, text_color="white"
        )
        delete_btn.pack(side="left", padx=SPACING_SM)
        
        self.bulk_delete_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text="Delete Selected", icon_name=ICON_DELETE, 
            command=self.bulk_delete_selected_bills, fg_color=ERROR_COLOR, text_color="white", state="disabled"
        )
        self.bulk_delete_btn.pack(side="left", padx=SPACING_SM)
        
        refresh_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Refresh", icon_name=ICON_REFRESH, 
            command=self.refresh_bills_data, fg_color=SECONDARY_COLOR, text_color="white"
        )
        refresh_btn.pack(side="right", padx=SPACING_SM)
        
        self.apply_btn = icon_manager.get_button_with_icon(
            action_btn_frame, text=" Apply Changes", icon_name=ICON_APPLY, 
            command=self.apply_pending_changes, fg_color=SUCCESS_COLOR, text_color="white"
        )
        self.apply_btn.pack(side="right", padx=SPACING_SM)
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(self.content, fg_color=BACKGROUND_COLOR)
        pagination_frame.grid(row=5, column=0, sticky="ew", pady=(SPACING_SM, 0))
        
        # Items per page selector
        ctk.CTkLabel(pagination_frame, text="Items per page:").pack(side="left", padx=SPACING_SM)
        self.items_per_page_var = ctk.StringVar(value=str(self._items_per_page))
        items_combo = ttk.Combobox(pagination_frame, textvariable=self.items_per_page_var,
                                  values=["10", "20", "50", "100"], state="readonly", width=8)
        items_combo.pack(side="left", padx=SPACING_SM)
        items_combo.bind("<<ComboboxSelected>>", self.on_items_per_page_change)
        
        # Pagination info
        self.pagination_info_label = ctk.CTkLabel(pagination_frame, text="", font=("Arial", 12))
        self.pagination_info_label.pack(side="left", padx=SPACING_MD)
        
        # Navigation buttons
        self.first_page_btn = ctk.CTkButton(pagination_frame, text="⏮️ First", width=80, 
                                           command=self.go_to_first_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.first_page_btn.pack(side="right", padx=SPACING_SM)
        
        self.prev_page_btn = ctk.CTkButton(pagination_frame, text="◀️ Prev", width=80, 
                                          command=self.go_to_prev_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.prev_page_btn.pack(side="right", padx=SPACING_SM)
        
        self.next_page_btn = ctk.CTkButton(pagination_frame, text="Next ▶️", width=80, 
                                          command=self.go_to_next_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.next_page_btn.pack(side="right", padx=SPACING_SM)
        
        self.last_page_btn = ctk.CTkButton(pagination_frame, text="Last ⏭️", width=80, 
                                          command=self.go_to_last_page, fg_color=PRIMARY_COLOR, text_color="white")
        self.last_page_btn.pack(side="right", padx=SPACING_SM)

    def apply_filters(self, *args):
        """Apply all filters: status, period, and search"""
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
        """Filter bills by time period"""
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
        """Clear all filters and reset to default (Pending bills)"""
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
        """Clear only the search filter"""
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
        self.clear_content()
        self.settings_frame = ctk.CTkFrame(self.content)
        self.settings_frame.grid(row=0, column=0, sticky="nswe")
        label = ctk.CTkLabel(self.settings_frame, text="Settings View (Coming Soon)", font=("Arial", 18))
        label.pack(padx=SPACING_MD, pady=SPACING_MD)

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
                    show_popup(self, "Success", "Bill deleted successfully!", color="green")
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
                show_popup(self, "Success", "Bill deleted successfully!", color="green")
                self.show_bills_view()
            except Exception as e:
                show_popup(self, "Error", f"Failed to delete bill: {str(e)}", color="red")

    def bulk_delete_selected_bills(self):
        """Delete multiple selected bills"""
        if not self._selected_bills:
            show_popup(self, "Info", "No bills selected for deletion.", color="blue")
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
                    if failed_count == 0:
                        show_popup(self, "Success", f"Successfully deleted {deleted_count} bill(s)!", color="green")
                    else:
                        show_popup(self, "Partial Success", 
                                 f"Deleted {deleted_count} bill(s), failed to delete {failed_count} bill(s).", 
                                 color="orange")
                    
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
            
            show_popup(self, "Success", f"Exported {len(self._bills_data)} bills to {os.path.basename(file_path)}", color="green")
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
            
            message = f"Imported {imported_count} bills successfully!"
            if skipped_count > 0:
                message += f" Skipped {skipped_count} bills (duplicates or invalid data)."
            show_popup(self, "Success", message, color="green")
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to import bills: {str(e)}", color="red")

    def on_table_click(self, event):
        """Handle clicks on the table, specifically for checkbox columns"""
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
        """Toggle the selection status of a bill"""
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
        """Toggle select all/none for all visible bills"""
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
        """Update the state of bulk action buttons based on selection"""
        selected_count = len(self._selected_bills)
        if selected_count > 0:
            self.bulk_delete_btn.configure(text=f"Delete Selected ({selected_count})", state="normal")
        else:
            self.bulk_delete_btn.configure(text="Delete Selected", state="disabled")
    
    def update_pagination_controls(self):
        """Update pagination controls and info"""
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
        """Go to the first page"""
        if self._current_page != 1:
            self._current_page = 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_prev_page(self):
        """Go to the previous page"""
        if self._current_page > 1:
            self._current_page -= 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_next_page(self):
        """Go to the next page"""
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.populate_bills_table(self._filtered_bills)
    
    def go_to_last_page(self):
        """Go to the last page"""
        if self._current_page != self._total_pages:
            self._current_page = self._total_pages
            self.populate_bills_table(self._filtered_bills)
    
    def on_items_per_page_change(self, event=None):
        """Handle items per page change"""
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
        """Toggle the paid status of a bill in the table and store as pending change"""
        if item_id in self.bills_by_id:
            bill = self.bills_by_id[item_id]
            current_paid = bill.get("paid", False)
            new_paid = not current_paid
            
            # If marking as paid, show confirmation dialog
            if new_paid:
                def on_payment_confirmed(confirmation_number):
                    if confirmation_number is not None:  # User didn't cancel
                        # Create a copy of the bill for pending changes
                        pending_bill = bill.copy()
                        pending_bill["paid"] = True
                        pending_bill["confirmation_number"] = confirmation_number
                        
                        # Store the pending change
                        self.pending_changes[item_id] = pending_bill
                        
                        # Update the display
                        paid_status = "✓"
                        values = list(self.bills_table.item(item_id, "values"))
                        values[1] = paid_status  # Update paid column (now second column)
                        values[6] = "Paid"  # Update status column
                        self.bills_table.item(item_id, values=values)
                        
                        # Update the button text to show pending changes
                        pending_count = len(self.pending_changes)
                        if pending_count > 0:
                            self.apply_btn.configure(text=f"Apply Changes ({pending_count})", fg_color="orange")
                        else:
                            self.apply_btn.configure(text="Apply Changes", fg_color="green")
                
                # Show payment confirmation dialog
                PaymentConfirmationDialog(self, bill.get("name", ""), on_payment_confirmed)
            else:
                # Marking as unpaid - no confirmation needed
                # Create a copy of the bill for pending changes
                pending_bill = bill.copy()
                pending_bill["paid"] = False
                pending_bill["confirmation_number"] = ""  # Clear confirmation number
                
                # Store the pending change
                self.pending_changes[item_id] = pending_bill
                
                # Update the display
                paid_status = "☐"
                values = list(self.bills_table.item(item_id, "values"))
                values[1] = paid_status  # Update paid column (now second column)
                values[6] = "Pending"  # Update status column
                self.bills_table.item(item_id, values=values)
                
                # Update the button text to show pending changes
                pending_count = len(self.pending_changes)
                if pending_count > 0:
                    self.apply_btn.configure(text=f"Apply Changes ({pending_count})", fg_color="orange")
                else:
                    self.apply_btn.configure(text="Apply Changes", fg_color="green")
    
    def _calculate_next_due_date(self, current_due_date, billing_cycle):
        """Calculate the next due date based on billing cycle"""
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
        """Apply all pending changes to the database"""
        if not self.pending_changes:
            show_popup(self, "Info", "No changes to apply.", color="blue")
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
            
            # Show success message
            message = f"Applied {applied_count} changes successfully!"
            if new_bills_created > 0:
                message += f" Created {new_bills_created} new bill(s) for next cycle."
            show_popup(self, "Success", message, color="green")
            
        except Exception as e:
            show_popup(self, "Error", f"Failed to apply changes: {str(e)}", color="red")
    
    def refresh_bills_data(self):
        """Refresh bills data from database"""
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
                        show_popup(self, "Success", "Data refreshed successfully!", color="green")
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
        """Helper method to refresh data directly"""
        try:
            self._bills_data = fetch_all_bills()
            self._filtered_bills = self._bills_data.copy()
            if self._sort_column:
                self.sort_by_column(self._sort_column)
            else:
                self.populate_bills_table(self._filtered_bills)
            show_popup(self, "Success", "Data refreshed successfully!", color="green")
        except Exception as e:
            show_popup(self, "Error", f"Failed to refresh data: {str(e)}", color="red")

    # Category management methods
    def populate_categories_table(self):
        """Populate the categories table with data"""
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
        """Open dialog to add a new category"""
        AddCategoryDialog(self, self.refresh_categories)

    def edit_selected_category(self):
        """Edit the selected category"""
        selected = self.categories_table.selection()
        if not selected:
            show_popup(self, "Info", "Please select a category to edit.", color="blue")
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
        """Delete the selected category"""
        selected = self.categories_table.selection()
        if not selected:
            show_popup(self, "Info", "Please select a category to delete.", color="blue")
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
                        show_popup(self, "Success", "Category deleted successfully!", color="green")
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
        """Refresh the categories table"""
        self.populate_categories_table()

    def _on_close(self):
        """Handle window close event"""
        try:
            # Cancel any pending after() calls to prevent invalid command errors
            for after_id in self.tk.eval('after info').split():
                if after_id.isdigit():
                    try:
                        self.after_cancel(int(after_id))
                    except:
                        pass
            
            self.quit()
        except Exception as e:
            print(f"Error during close: {e}")
        finally:
            try:
                self.destroy()
            except:
                pass

class PaymentConfirmationDialog(ctk.CTkToplevel):
    def __init__(self, master, bill_name, on_confirm):
        super().__init__(master)
        self.on_confirm = on_confirm
        self.confirmation_number = ""
        
        self.title("Payment Confirmation")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"400x200+{x}+{y}")
        
        self._setup_ui(bill_name)
        
        # Make dialog modal
        self.transient(master)
        self.grab_set()
        self.focus_force()
    
    def _setup_ui(self, bill_name):
        # Title
        title_label = ctk.CTkLabel(self, text="Payment Confirmation", font=("Arial", 16, "bold"))
        title_label.pack(pady=(SPACING_SM, SPACING_SM))
        
        # Bill name
        bill_label = ctk.CTkLabel(self, text=f"Bill: {bill_name}", font=("Arial", 12))
        bill_label.pack(pady=(0, SPACING_SM))
        
        # Confirmation number entry
        ctk.CTkLabel(self, text="Confirmation Number (optional):", font=("Arial", 12)).pack(pady=(0, SPACING_SM))
        self.confirmation_entry = ctk.CTkEntry(self, width=300, placeholder_text="Enter confirmation number...", fg_color=BACKGROUND_COLOR, text_color=TEXT_COLOR)
        self.confirmation_entry.pack(pady=(0, SPACING_SM))
        self.confirmation_entry.focus()
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=(0, SPACING_SM))
        
        confirm_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Confirm Payment", icon_name=ICON_SAVE, 
            command=self._on_confirm, fg_color=SUCCESS_COLOR, text_color="white"
        )
        confirm_btn.pack(side="left", padx=SPACING_SM)
        
        cancel_btn = icon_manager.get_button_with_icon(
            btn_frame, text=" Cancel", icon_name=ICON_CANCEL, 
            command=self._on_cancel, fg_color=ERROR_COLOR, text_color="white"
        )
        cancel_btn.pack(side="left", padx=SPACING_SM)
        
        # Bind Enter key to confirm
        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self._on_cancel())
    
    def _on_confirm(self):
        self.confirmation_number = self.confirmation_entry.get().strip()
        self.on_confirm(self.confirmation_number)
        self.destroy()
    
    def _on_cancel(self):
        self.on_confirm(None)  # None indicates cancellation
        self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    try:
        app.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc() 