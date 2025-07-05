import sys
import os
import tkinter
import customtkinter as ctk

# Configure CustomTkinter to handle DPI scaling issues
ctk.set_appearance_mode("light")  # or "dark"
ctk.set_default_color_theme("blue")

# Disable DPI scaling if it causes issues
try:
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
except:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.core.db import initialize_database
from src.gui.main_window import MainWindow

def handle_tcl_error(error):
    """Handle Tcl errors that are known to be harmless"""
    error_str = str(error)
    
    # Ignore known harmless errors
    if any(keyword in error_str.lower() for keyword in [
        "bad window path name",
        "focus",
        "check_dpi_scaling",
        "update",
        "invalid command name"
    ]):
        return True  # Error handled, don't re-raise
    
    return False  # Error not handled, should re-raise

if __name__ == "__main__":
    # Initialize database before starting the application
    initialize_database()
    
    app = MainWindow()
    
    try:
        app.mainloop()
    except tkinter.TclError as e:
        if not handle_tcl_error(e):
            print(f"Unhandled Tcl error: {e}")
            raise
    except Exception as e:
        print(f"Application error: {e}")
        raise 