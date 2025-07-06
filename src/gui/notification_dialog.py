import customtkinter as ctk
import webbrowser
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, Optional, Callable
import threading

# Suppress CustomTkinter widget destruction errors
import tkinter as tk
original_delete = tk.Canvas.delete

def safe_canvas_delete(canvas, *args, **kwargs):
    """
    Safe version of canvas delete that handles destroyed widgets.
    
    Args:
        canvas: The canvas widget to delete from.
        *args: Additional arguments for the delete operation.
        **kwargs: Additional keyword arguments for the delete operation.
    """
    try:
        return original_delete(canvas, *args, **kwargs)
    except tk.TclError as e:
        if "invalid command name" in str(e):
            # Widget was destroyed, ignore the error
            pass
        else:
            raise

# Monkey patch the canvas delete method
tk.Canvas.delete = safe_canvas_delete

# Global error handler to suppress focus-related errors
def suppress_focus_errors():
    """
    Suppress common Tkinter focus errors by replacing the error handler.
    This prevents errors when widgets are destroyed or become invalid.
    """
    import tkinter as tk
    
    # Store original error handler
    original_report_callback_exception = tk.Tk.report_callback_exception
    
    def safe_report_callback_exception(self, exc, val, tb):
        """Safe error handler that suppresses focus-related errors."""
        error_str = str(val)
        if any(keyword in error_str.lower() for keyword in [
            'bad window path name',
            'invalid command name',
            'window was deleted',
            'focus',
            'destroyed'
        ]):
            # Suppress focus and destruction related errors
            return
        else:
            # Call original handler for other errors
            if original_report_callback_exception:
                original_report_callback_exception(self, exc, val, tb)
    
    # Apply the safe error handler
    tk.Tk.report_callback_exception = safe_report_callback_exception

# Initialize error suppression
suppress_focus_errors()

# Add safe focus methods
def safe_focus_set(widget):
    """
    Safely set focus on a widget.
    
    Args:
        widget: The widget to set focus on.
    """
    try:
        if widget and widget.winfo_exists():
            widget.focus_set()
    except tk.TclError:
        # Widget was destroyed or invalid, ignore
        pass

def safe_focus_force(widget):
    """
    Safely force focus on a widget.
    
    Args:
        widget: The widget to force focus on.
    """
    try:
        if widget and widget.winfo_exists():
            widget.focus_force()
    except tk.TclError:
        # Widget was destroyed or invalid, ignore
        pass

def safe_lift(widget):
    """
    Safely lift a widget to front.
    
    Args:
        widget: The widget to lift to front.
    """
    try:
        if widget and widget.winfo_exists():
            widget.lift()
    except tk.TclError:
        # Widget was destroyed or invalid, ignore
        pass

# UI Theme Constants
PRIMARY_COLOR = "#1f538d"
SECONDARY_COLOR = "#4ecdc4"
ACCENT_COLOR = "#ff6b6b"
BACKGROUND_COLOR = "#f7f9fa"
TEXT_COLOR = "#222831"
SUCCESS_COLOR = "#4bb543"
ERROR_COLOR = "#e74c3c"
WARNING_COLOR = "#ffa500"
URGENT_COLOR = "#ff0000"

SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24

class BillNotificationDialog(ctk.CTkToplevel):
    """
    Desktop popup notification for bill reminders.
    
    Shows bill information and provides quick actions like marking as paid,
    snoozing reminders, opening websites, and sending emails.
    """
    
    def __init__(self, notification_data: Dict, on_mark_paid: Optional[Callable] = None, on_snooze: Optional[Callable] = None):
        """
        Initialize the notification dialog.
        
        Args:
            notification_data: Dictionary containing notification information including
                              title, message, bill details, urgency level, and contact info.
            on_mark_paid: Callback function when user marks bill as paid.
            on_snooze: Callback function when user snoozes the reminder.
        """
        try:
            super().__init__()
            
            self.notification_data = notification_data
            self.on_mark_paid = on_mark_paid
            self.on_snooze = on_snooze
            self._destroyed = False
            
            # Configure window
            self.title(notification_data.get('title', 'Bill Reminder'))
            self.geometry("450x350")
            self.resizable(False, False)
            
            # Make window always on top
            self.attributes('-topmost', True)
            
            # Center the dialog
            self.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (450 // 2)
            y = (self.winfo_screenheight() // 2) - (350 // 2)
            self.geometry(f"450x350+{x}+{y}")
            
            # Setup UI
            self._setup_ui()
            
            # Auto-close after 30 seconds
            self.auto_close_timer = self.after(30000, self._auto_close)
            
            # Focus and bring to front safely
            self.after(100, self._safe_focus)
            
        except Exception as e:
            print(f"Error creating notification dialog: {e}")
            # If we can't create the dialog, just print the notification
            print(f"NOTIFICATION: {notification_data.get('message', 'Bill reminder')}")
    
    def _safe_focus(self):
        """
        Safely focus and lift the window to ensure it's visible to the user.
        """
        try:
            if not self._destroyed and self.winfo_exists():
                safe_lift(self)
                safe_focus_force(self)
        except Exception as e:
            print(f"Error focusing notification: {e}")
        
    def _setup_ui(self):
        """
        Setup the notification UI with header, message, details, and action buttons.
        """
        # Configure grid
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with urgency indicator
        self._setup_header()
        
        # Main message
        self._setup_message()
        
        # Bill details
        self._setup_details()
        
        # Action buttons
        self._setup_actions()
        
    def _setup_header(self):
        """
        Setup the header section with urgency indicator and close button.
        """
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=SPACING_MD, pady=(SPACING_MD, SPACING_SM))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Urgency icon and color
        urgency = self.notification_data.get('urgency', 'REMINDER')
        if urgency == 'URGENT':
            icon = "⚠️"
            color = URGENT_COLOR
        elif urgency == 'OVERDUE':
            icon = "🚨"
            color = ERROR_COLOR
        else:
            icon = "📅"
            color = WARNING_COLOR
            
        # Urgency label
        urgency_label = ctk.CTkLabel(
            header_frame, 
            text=f"{icon} {urgency}", 
            font=("Arial", 16, "bold"),
            text_color=color
        )
        urgency_label.grid(row=0, column=0, sticky="w", padx=(0, SPACING_SM))
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            command=self._close_notification,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            hover_color=ERROR_COLOR
        )
        close_btn.grid(row=0, column=2, sticky="e")
        
    def _setup_message(self):
        """
        Setup the main message section with notification text and bill name.
        """
        message_frame = ctk.CTkFrame(self, fg_color="transparent")
        message_frame.grid(row=1, column=0, sticky="ew", padx=SPACING_MD, pady=SPACING_SM)
        message_frame.grid_columnconfigure(0, weight=1)
        
        # Main message
        message = self.notification_data.get('message', '')
        message_label = ctk.CTkLabel(
            message_frame,
            text=message,
            font=("Arial", 14, "bold"),
            text_color=TEXT_COLOR,
            wraplength=400
        )
        message_label.grid(row=0, column=0, sticky="w", pady=(0, SPACING_SM))
        
        # Bill name
        bill_name = self.notification_data.get('bill_name', '')
        bill_label = ctk.CTkLabel(
            message_frame,
            text=f"Bill: {bill_name}",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        bill_label.grid(row=1, column=0, sticky="w")
        
    def _setup_details(self):
        """
        Setup the bill details section with additional information.
        """
        details_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        details_frame.grid(row=2, column=0, sticky="ew", padx=SPACING_MD, pady=SPACING_SM)
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Details text
        details = self.notification_data.get('details', '')
        details_label = ctk.CTkLabel(
            details_frame,
            text=details,
            font=("Arial", 11),
            text_color=TEXT_COLOR,
            justify="left",
            wraplength=400
        )
        details_label.grid(row=0, column=0, sticky="w", padx=SPACING_SM, pady=SPACING_SM)
        
    def _setup_actions(self):
        """
        Setup the action buttons section with mark paid, snooze, website, and email buttons.
        """
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=SPACING_MD, pady=SPACING_SM)
        actions_frame.grid_columnconfigure(4, weight=1)
        
        # Mark as paid button
        mark_paid_btn = ctk.CTkButton(
            actions_frame,
            text="Mark Paid",
            command=self._mark_as_paid,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            height=35
        )
        mark_paid_btn.grid(row=0, column=0, padx=SPACING_XS, pady=SPACING_SM)
        
        # Snooze button
        snooze_btn = ctk.CTkButton(
            actions_frame,
            text="Snooze 1h",
            command=self._snooze_reminder,
            fg_color=WARNING_COLOR,
            text_color="white",
            height=35
        )
        snooze_btn.grid(row=0, column=1, padx=SPACING_XS, pady=SPACING_SM)
        
        # Website button (if available)
        web_page = self.notification_data.get('web_page')
        if web_page:
            website_btn = ctk.CTkButton(
                actions_frame,
                text="Website",
                command=self._open_website,
                fg_color=PRIMARY_COLOR,
                text_color="white",
                height=35
            )
            website_btn.grid(row=0, column=2, padx=SPACING_XS, pady=SPACING_SM)
        
        # Email button (if available)
        company_email = self.notification_data.get('company_email')
        if company_email:
            email_btn = ctk.CTkButton(
                actions_frame,
                text="Email",
                command=self._open_email,
                fg_color=SECONDARY_COLOR,
                text_color="white",
                height=35
            )
            email_btn.grid(row=0, column=3, padx=SPACING_XS, pady=SPACING_SM)
            
    def _mark_as_paid(self):
        """
        Mark the bill as paid by calling the on_mark_paid callback and closing the notification.
        """
        try:
            if self.on_mark_paid:
                self.on_mark_paid(self.notification_data.get('bill_id'))
        except Exception as e:
            print(f"Error marking bill as paid: {e}")
        self._close_notification()
        
    def _snooze_reminder(self):
        """
        Snooze the reminder for 1 hour by calling the on_snooze callback and closing the notification.
        """
        try:
            if self.on_snooze:
                self.on_snooze(self.notification_data.get('bill_id'), 3600)  # 1 hour in seconds
        except Exception as e:
            print(f"Error snoozing reminder: {e}")
        self._close_notification()
        
    def _open_website(self):
        """
        Open the bill's website in the default web browser.
        """
        try:
            web_page = self.notification_data.get('web_page')
            if web_page:
                try:
                    webbrowser.open(web_page)
                except Exception as e:
                    print(f"Error opening website: {e}")
        except Exception as e:
            print(f"Error in _open_website: {e}")
                
    def _open_email(self):
        """
        Open default email client with the company email address.
        Supports Windows, macOS, and Linux platforms.
        """
        try:
            company_email = self.notification_data.get('company_email')
            if company_email:
                try:
                    # Try to open default email client
                    if sys.platform.startswith('win'):
                        subprocess.run(['start', f'mailto:{company_email}'], shell=True)
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', f'mailto:{company_email}'])
                    else:
                        subprocess.run(['xdg-open', f'mailto:{company_email}'])
                except Exception as e:
                    print(f"Error opening email client: {e}")
        except Exception as e:
            print(f"Error in _open_email: {e}")
                
    def _close_notification(self):
        """
        Close the notification dialog safely, canceling any pending timers.
        """
        if self._destroyed:
            return
            
        self._destroyed = True
        
        try:
            if hasattr(self, 'auto_close_timer'):
                self.after_cancel(self.auto_close_timer)
        except:
            pass
        
        try:
            if self.winfo_exists():
                self.destroy()
        except:
            pass
        
    def _auto_close(self):
        """
        Auto-close the notification after the timeout period (30 seconds).
        """
        if self._destroyed:
            return
            
        self._destroyed = True
        
        try:
            if self.winfo_exists():
                self.destroy()
        except:
            pass


class NotificationManager:
    """
    Manager for handling multiple notifications and preventing spam.
    
    Controls the number of active notifications, manages their lifecycle,
    and provides thread-safe operations for notification handling.
    """
    
    def __init__(self):
        """
        Initialize the notification manager with empty active notifications list.
        """
        self.active_notifications = []
        self.max_notifications = 3  # Maximum number of notifications to show at once
        self._lock = threading.Lock()  # Thread lock for safe access
        
    def show_notification(self, notification_data: Dict, on_mark_paid: Optional[Callable] = None, on_snooze: Optional[Callable] = None):
        """
        Show a new notification dialog with thread-safe management.
        
        Args:
            notification_data: Dictionary containing notification information.
            on_mark_paid: Callback function when user marks bill as paid.
            on_snooze: Callback function when user snoozes the reminder.
        """
        with self._lock:
            try:
                # Clean up destroyed notifications
                self.active_notifications = [n for n in self.active_notifications if n.winfo_exists()]
                
                # Check if we already have too many notifications
                if len(self.active_notifications) >= self.max_notifications:
                    # Close the oldest notification
                    if self.active_notifications:
                        oldest = self.active_notifications.pop(0)
                        try:
                            if oldest.winfo_exists():
                                oldest.destroy()
                        except:
                            pass
                            
                # Create new notification with a small delay to prevent interference
                def create_notification():
                    try:
                        notification = BillNotificationDialog(
                            notification_data, 
                            on_mark_paid=on_mark_paid, 
                            on_snooze=on_snooze
                        )
                        
                        # Add to active notifications
                        self.active_notifications.append(notification)
                        
                        # Remove from active list when closed
                        def on_close():
                            with self._lock:
                                try:
                                    if notification in self.active_notifications:
                                        self.active_notifications.remove(notification)
                                except:
                                    pass
                                
                        notification.protocol("WM_DELETE_WINDOW", on_close)
                        
                    except Exception as e:
                        print(f"Error creating notification: {e}")
                
                # Schedule notification creation with a small delay
                import threading
                timer = threading.Timer(0.5, create_notification)
                timer.start()
                
            except Exception as e:
                print(f"Error showing notification: {e}")
                # Fallback: just print the notification
                print(f"NOTIFICATION: {notification_data.get('message', 'Bill reminder')}")
        
    def close_all_notifications(self):
        """
        Close all active notifications and clear the active notifications list.
        """
        with self._lock:
            for notification in self.active_notifications[:]:
                try:
                    if notification.winfo_exists():
                        notification.destroy()
                except:
                    pass
            self.active_notifications.clear()
        
    def get_active_count(self) -> int:
        """
        Get the number of active notifications.
        
        Returns:
            int: The number of currently active notifications.
        """
        with self._lock:
            # Clean up destroyed notifications first
            self.active_notifications = [n for n in self.active_notifications if n.winfo_exists()]
            return len(self.active_notifications) 