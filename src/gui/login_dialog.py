import customtkinter as ctk
from tkinter import messagebox
from ..core.auth import auth_manager, AuthenticationError
import json
import os
from ..utils.constants import *
from ..utils.helpers import is_dark_mode

# UI Constants
PRIMARY_COLOR = "#2563eb"  # Modern blue
SECONDARY_COLOR = "#4ecdc4"
ACCENT_COLOR = "#ff6b6b"
BACKGROUND_COLOR = "#f7fafc"  # Very light gray
FRAME_BG = "#f1f5f9"  # Slightly darker for frame
TEXT_COLOR = "#222831"
SUCCESS_COLOR = "#4bb543"
ERROR_COLOR = "#e74c3c"
LINK_COLOR = "#2563eb"
BORDER_COLOR = "#e0e7ef"

SPACING_SM = 10
SPACING_MD = 20
SPACING_LG = 32

class LoginDialog(ctk.CTkToplevel):
    """
    Login dialog for user authentication.

    Presents a modal dialog for users to enter their username and password, with support for dark mode,
    'remember me', and a link to registration. Calls the provided on_success callback with user data on successful login.
    """
    
    def __init__(self, master, on_success):
        """
        Initialize the LoginDialog.

        Args:
            master: The parent window.
            on_success (callable): Callback to invoke with user data on successful login.
        """
        super().__init__(master)
        self.title("Login - Bills Tracker")
        self.geometry("420x600")
        self.resizable(False, False)
        self.on_success = on_success
        self.current_user = None

        # Detect dark mode
        self.dark_mode = is_dark_mode()
        self._set_theme_colors()
        self.configure(fg_color=self.bg_color)
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (420 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"420x600+{x}+{y}")
        
        # Make dialog modal
        self.transient(master)
        self.grab_set()
        self.lift()
        
        # Setup fade transitions
        from ..utils.transition_utils import TransitionManager
        self.transition_manager = TransitionManager(self, 300)
        
        # Load saved credentials
        self.saved_credentials = self._load_saved_credentials()
        
        self._setup_ui()
        self._check_remembered_user()
        
        # Start fade in animation
        self.after(50, self._start_fade_in)
    
    def _start_fade_in(self):
        """Start the fade in animation."""
        if self.transition_manager:
            self.transition_manager.fade_in()
    
    def _fade_out_and_destroy(self, callback=None):
        """Fade out the dialog and then destroy it."""
        if self.transition_manager:
            self.transition_manager.fade_out(lambda: self._destroy_with_callback(callback))
        else:
            self._destroy_with_callback(callback)
    
    def _destroy_with_callback(self, callback=None):
        """Destroy the dialog and execute callback."""
        try:
            if self.winfo_exists():
                self.destroy()
                if callback:
                    callback()
        except:
            pass
    
    def _set_theme_colors(self):
        """
        Set theme colors based on dark mode.
        """
        if self.dark_mode:
            self.bg_color = DARK_BG_COLOR
            self.frame_bg = DARK_FRAME_BG
            self.text_color = DARK_TEXT_COLOR
            self.entry_bg = DARK_ENTRY_BG
            self.border_color = DARK_BORDER_COLOR
            self.primary_color = DARK_PRIMARY_COLOR
            self.link_color = DARK_LINK_COLOR
        else:
            self.bg_color = BACKGROUND_COLOR
            self.frame_bg = FRAME_BG
            self.text_color = TEXT_COLOR
            self.entry_bg = "#f3f4f6"
            self.border_color = BORDER_COLOR
            self.primary_color = PRIMARY_COLOR
            self.link_color = LINK_COLOR
    
    def _setup_ui(self):
        """
        Setup the login UI widgets and layout.
        """
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="💰 Bills Tracker", 
            font=("Segoe UI", 26, "bold"),
            text_color=self.primary_color
        )
        title_label.grid(row=0, column=0, pady=(SPACING_LG, SPACING_SM))
        
        subtitle_label = ctk.CTkLabel(
            self,
            text="Sign in to continue",
            font=("Segoe UI", 15),
            text_color=self.text_color if self.dark_mode else "gray"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, SPACING_LG))
        
        # Login frame
        self.login_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=self.frame_bg, border_width=1, border_color=self.border_color)
        self.login_frame.grid(row=2, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        # Username
        ctk.CTkLabel(self.login_frame, text="Username:", font=("Segoe UI", 12), text_color=self.text_color).grid(
            row=0, column=0, padx=SPACING_SM, pady=(SPACING_MD, SPACING_SM), sticky="w"
        )
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter username", fg_color=self.entry_bg, font=("Segoe UI", 12), text_color=self.text_color)
        self.username_entry.grid(row=1, column=0, padx=SPACING_SM, pady=(0, SPACING_MD), sticky="ew")
        
        # Password
        ctk.CTkLabel(self.login_frame, text="Password:", font=("Segoe UI", 12), text_color=self.text_color).grid(
            row=2, column=0, padx=SPACING_SM, pady=(0, SPACING_SM), sticky="w"
        )
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter password", show="*", fg_color=self.entry_bg, font=("Segoe UI", 12), text_color=self.text_color)
        self.password_entry.grid(row=3, column=0, padx=SPACING_SM, pady=(0, SPACING_MD), sticky="ew")
        
        # Remember me checkbox
        self.remember_var = ctk.BooleanVar()
        remember_checkbox = ctk.CTkCheckBox(
            self.login_frame, 
            text="Remember username", 
            variable=self.remember_var,
            font=("Segoe UI", 11),
            text_color=self.text_color
        )
        remember_checkbox.grid(row=4, column=0, padx=SPACING_SM, pady=(0, SPACING_MD), sticky="w")
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.login_frame, 
            text="", 
            text_color=ERROR_COLOR,
            font=("Segoe UI", 12, "bold")
        )
        self.error_label.grid(row=5, column=0, padx=SPACING_SM, pady=(0, SPACING_MD))
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Sign In",
            command=self._login,
            fg_color=self.primary_color,
            hover_color="#1d4ed8" if not self.dark_mode else self.primary_color,
            text_color="white",
            corner_radius=8,
            font=("Segoe UI", 13, "bold"),
            height=44
        )
        self.login_button.grid(row=6, column=0, padx=SPACING_SM, pady=(0, SPACING_MD), sticky="ew")
        
        # Register clickable label below login button
        new_user_label = ctk.CTkLabel(
            self,
            text="New User?",
            font=("Segoe UI", 13, "underline"),
            text_color=self.link_color,
            cursor="hand2"
        )
        new_user_label.grid(row=3, column=0, pady=(SPACING_MD, 0), sticky="ew")
        new_user_label.bind("<Button-1>", lambda e: self._show_register_dialog())
        
        # Bind Enter key to login
        self.bind("<Return>", lambda e: self._login())
        self.username_entry.bind("<Return>", lambda e: self._login())
        self.password_entry.bind("<Return>", lambda e: self._login())
    
    def _check_remembered_user(self):
        """
        Check if there's a remembered username and pre-fill the username entry if found.
        """
        if self.saved_credentials and 'username' in self.saved_credentials:
            self.username_entry.insert(0, self.saved_credentials['username'])
            self.remember_var.set(True)
            self.password_entry.focus()
    
    def _login(self):
        """
        Handle login attempt. Authenticates the user and calls on_success if successful.
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self._show_error("Please enter both username and password")
            return
        
        try:
            # Disable login button during authentication
            self.login_button.configure(state="disabled", text="Signing in...")
            self.update()
            
            # Attempt login
            user_data = auth_manager.login(username, password)
            
            # Save credentials if remember me is checked
            if self.remember_var.get():
                self._save_credentials(username)
            else:
                self._clear_saved_credentials()
            
            # Store current user
            self.current_user = user_data
            
            # Close dialog and call success callback
            self._fade_out_and_destroy(lambda: self.on_success(user_data))
            
        except AuthenticationError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Login failed: {str(e)}")
        finally:
            # Re-enable login button
            self.login_button.configure(state="normal", text="Sign In")
    
    def _show_error(self, message):
        """
        Show error message in the dialog.

        Args:
            message (str): The error message to display.
        """
        self.error_label.configure(text=message)
        self.error_label.grid()  # Ensure it's visible
    
    def _show_register_dialog(self):
        """
        Open the registration dialog when the user clicks 'New User?'.
        """
        print("Register button clicked!")
        RegisterDialog(self, self._on_register_success)
    
    def _on_register_success(self, username):
        """
        Handle successful registration by pre-filling the username and prompting for login.

        Args:
            username (str): The username of the newly registered user.
        """
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, username)
        self.password_entry.focus()
        self._show_error("Registration successful! Please sign in.")
    
    def _load_saved_credentials(self):
        """
        Load saved credentials from file if 'remember me' was checked.

        Returns:
            dict: The saved credentials, or an empty dict if not found.
        """
        try:
            if os.path.exists("saved_credentials.json"):
                with open("saved_credentials.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_credentials(self, username):
        """
        Save the username to file for 'remember me' functionality.

        Args:
            username (str): The username to save.
        """
        try:
            credentials = {"username": username}
            with open("saved_credentials.json", "w") as f:
                json.dump(credentials, f)
        except Exception:
            pass
    
    def _clear_saved_credentials(self):
        """
        Clear saved credentials from file.
        """
        try:
            if os.path.exists("saved_credentials.json"):
                os.remove("saved_credentials.json")
        except Exception:
            pass

class RegisterDialog(ctk.CTkToplevel):
    """
    Registration dialog for creating a new user account.

    Presents a modal dialog for users to enter a username, email, and password. Calls the provided on_success
    callback with the username on successful registration.
    """
    
    def __init__(self, master, on_success):
        """
        Initialize the RegisterDialog.

        Args:
            master: The parent window.
            on_success (callable): Callback to invoke with the username on successful registration.
        """
        super().__init__(master)
        self.title("Create Account - Bills Tracker")
        self.geometry("400x600")
        self.resizable(False, False)
        self.on_success = on_success
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"400x600+{x}+{y}")
        
        # Make dialog modal
        self.transient(master)
        self.grab_set()
        self.lift()
        
        # Setup fade transitions
        from ..utils.transition_utils import TransitionManager
        self.transition_manager = TransitionManager(self, 300)
        
        self._setup_ui()
        
        # Start fade in animation
        self.after(50, self._start_fade_in)
    
    def _start_fade_in(self):
        """Start the fade in animation."""
        if self.transition_manager:
            self.transition_manager.fade_in()
    
    def _fade_out_and_destroy(self, callback=None):
        """Fade out the dialog and then destroy it."""
        if self.transition_manager:
            self.transition_manager.fade_out(lambda: self._destroy_with_callback(callback))
        else:
            self._destroy_with_callback(callback)
    
    def _destroy_with_callback(self, callback=None):
        """Destroy the dialog and execute callback."""
        try:
            if self.winfo_exists():
                self.destroy()
                if callback:
                    callback()
        except:
            pass
    
    def _setup_ui(self):
        """
        Setup the registration UI widgets and layout.
        """
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Create Account", 
            font=("Arial", 20, "bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=(SPACING_LG, SPACING_MD))
        
        # Registration frame
        self.register_frame = ctk.CTkFrame(self)
        self.register_frame.grid(row=1, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        self.register_frame.grid_columnconfigure(0, weight=1)
        
        # Username
        ctk.CTkLabel(self.register_frame, text="Username:").grid(
            row=0, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.username_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Choose a username")
        self.username_entry.grid(row=1, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Email
        ctk.CTkLabel(self.register_frame, text="Email (optional):").grid(
            row=2, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.email_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Enter email address")
        self.email_entry.grid(row=3, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Password
        ctk.CTkLabel(self.register_frame, text="Password:").grid(
            row=4, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.password_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Choose a password", show="*")
        self.password_entry.grid(row=5, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Confirm Password
        ctk.CTkLabel(self.register_frame, text="Confirm Password:").grid(
            row=6, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.confirm_password_entry = ctk.CTkEntry(self.register_frame, placeholder_text="Confirm password", show="*")
        self.confirm_password_entry.grid(row=7, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.register_frame, 
            text="", 
            text_color=ERROR_COLOR,
            font=("Arial", 11)
        )
        self.error_label.grid(row=8, column=0, padx=SPACING_SM, pady=SPACING_SM)
        
        # Register button
        self.register_button = ctk.CTkButton(
            self.register_frame,
            text="Create Account",
            command=self.do_register,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            height=40
        )
        self.register_button.grid(row=9, column=0, padx=SPACING_SM, pady=SPACING_MD, sticky="ew")
        
        # Back to login button
        back_button = ctk.CTkButton(
            self.register_frame,
            text="Back to Login",
            command=self.destroy,
            fg_color="gray",
            text_color="white",
            height=35
        )
        back_button.grid(row=10, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Bind Enter key to register
        self.bind("<Return>", lambda e: self.do_register())
        self.username_entry.bind("<Return>", lambda e: self.do_register())
        self.password_entry.bind("<Return>", lambda e: self.do_register())
        self.confirm_password_entry.bind("<Return>", lambda e: self.do_register())
    
    def do_register(self):
        """
        Handle registration attempt. Validates input and registers the user.
        """
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not username or not password:
            self._show_error("Please enter username and password")
            return
        
        if len(username) < 3:
            self._show_error("Username must be at least 3 characters long")
            return
        
        if len(password) < 6:
            self._show_error("Password must be at least 6 characters long")
            return
        
        if password != confirm_password:
            self._show_error("Passwords do not match")
            return
        
        if email and "@" not in email:
            self._show_error("Please enter a valid email address")
            return
        
        try:
            # Disable register button during registration
            self.register_button.configure(state="disabled", text="Creating account...")
            self.update()
            
            # Attempt registration
            auth_manager.register_user(username, password, email if email else None)
            
            # Close dialog and call success callback
            self._fade_out_and_destroy(lambda: self.on_success(username))
            
        except AuthenticationError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Registration failed: {str(e)}")
        finally:
            # Re-enable register button
            self.register_button.configure(state="normal", text="Create Account")
    
    def _show_error(self, message):
        """
        Show error message in the dialog.

        Args:
            message (str): The error message to display.
        """
        self.error_label.configure(text=message)
        self.error_label.grid()  # Ensure it's visible

class ChangePasswordDialog(ctk.CTkToplevel):
    """
    Dialog for changing the user's password.

    Presents a modal dialog for users to enter their current password and a new password. Calls the provided
    on_success callback on successful password change.
    """
    
    def __init__(self, master, user_id, on_success):
        """
        Initialize the ChangePasswordDialog.

        Args:
            master: The parent window.
            user_id: The ID of the user changing their password.
            on_success (callable): Callback to invoke on successful password change.
        """
        super().__init__(master)
        self.title("Change Password - Bills Tracker")
        self.geometry("400x400")
        self.resizable(False, False)
        self.user_id = user_id
        self.on_success = on_success
        
        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"400x400+{x}+{y}")
        
        # Make dialog modal
        self.transient(master)
        self.grab_set()
        self.lift()
        
        # Setup fade transitions
        from ..utils.transition_utils import TransitionManager
        self.transition_manager = TransitionManager(self, 300)
        
        self._setup_ui()
        
        # Start fade in animation
        self.after(50, self._start_fade_in)
    
    def _start_fade_in(self):
        """Start the fade in animation."""
        if self.transition_manager:
            self.transition_manager.fade_in()
    
    def _fade_out_and_destroy(self, callback=None):
        """Fade out the dialog and then destroy it."""
        if self.transition_manager:
            self.transition_manager.fade_out(lambda: self._destroy_with_callback(callback))
        else:
            self._destroy_with_callback(callback)
    
    def _destroy_with_callback(self, callback=None):
        """Destroy the dialog and execute callback."""
        try:
            if self.winfo_exists():
                self.destroy()
                if callback:
                    callback()
        except:
            pass
    
    def _setup_ui(self):
        """
        Setup the change password UI widgets and layout.
        """
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Change Password", 
            font=("Arial", 20, "bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=(SPACING_LG, SPACING_MD))
        
        # Password frame
        self.password_frame = ctk.CTkFrame(self)
        self.password_frame.grid(row=1, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        self.password_frame.grid_columnconfigure(0, weight=1)
        
        # Current Password
        ctk.CTkLabel(self.password_frame, text="Current Password:").grid(
            row=0, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.current_password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Enter current password", show="*")
        self.current_password_entry.grid(row=1, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # New Password
        ctk.CTkLabel(self.password_frame, text="New Password:").grid(
            row=2, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.new_password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Enter new password", show="*")
        self.new_password_entry.grid(row=3, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Confirm New Password
        ctk.CTkLabel(self.password_frame, text="Confirm New Password:").grid(
            row=4, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="w"
        )
        self.confirm_password_entry = ctk.CTkEntry(self.password_frame, placeholder_text="Confirm new password", show="*")
        self.confirm_password_entry.grid(row=5, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self.password_frame, 
            text="", 
            text_color=ERROR_COLOR,
            font=("Arial", 11)
        )
        self.error_label.grid(row=6, column=0, padx=SPACING_SM, pady=SPACING_SM)
        
        # Change password button
        self.change_button = ctk.CTkButton(
            self.password_frame,
            text="Change Password",
            command=self._change_password,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            height=40
        )
        self.change_button.grid(row=7, column=0, padx=SPACING_SM, pady=SPACING_MD, sticky="ew")
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            self.password_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray",
            text_color="white",
            height=35
        )
        cancel_button.grid(row=8, column=0, padx=SPACING_SM, pady=SPACING_SM, sticky="ew")
        
        # Bind Enter key to change password
        self.bind("<Return>", lambda e: self._change_password())
        self.current_password_entry.bind("<Return>", lambda e: self._change_password())
        self.new_password_entry.bind("<Return>", lambda e: self._change_password())
        self.confirm_password_entry.bind("<Return>", lambda e: self._change_password())
    
    def _change_password(self):
        """
        Handle password change attempt. Validates input and changes the password.
        """
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            self._show_error("Please fill in all fields")
            return
        
        if len(new_password) < 6:
            self._show_error("New password must be at least 6 characters long")
            return
        
        if new_password != confirm_password:
            self._show_error("New passwords do not match")
            return
        
        if current_password == new_password:
            self._show_error("New password must be different from current password")
            return
        
        try:
            # Disable change button during password change
            self.change_button.configure(state="disabled", text="Changing password...")
            self.update()
            
            # Attempt password change
            auth_manager.change_password(self.user_id, current_password, new_password)
            
            # Close dialog and call success callback
            self._fade_out_and_destroy(lambda: self.on_success())
            
        except AuthenticationError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Password change failed: {str(e)}")
        finally:
            # Re-enable change button
            self.change_button.configure(state="normal", text="Change Password")
    
    def _show_error(self, message):
        """
        Show error message in the dialog.

        Args:
            message (str): The error message to display.
        """
        self.error_label.configure(text=message)
        self.error_label.grid()  # Ensure it's visible 