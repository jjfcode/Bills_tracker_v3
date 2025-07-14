"""
Demo script to showcase fade transition effects in the Bills Tracker application.
"""

import sys
import os
import customtkinter as ctk
from tkinter import messagebox

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.transition_utils import (
    TransitionManager, 
    create_fade_dialog, 
    show_fade_popup, 
    show_fade_confirmation_dialog
)
from utils.constants import *


class FadeTransitionDemo(ctk.CTk):
    """
    Demo application to showcase fade transition effects.
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Fade Transitions Demo - Bills Tracker")
        self.geometry("600x500")
        self.minsize(500, 400)
        
        # Configure the main window
        self.configure(bg_color=BACKGROUND_COLOR)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the demo UI."""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🎬 Fade Transitions Demo",
            font=("Arial", 24, "bold"),
            text_color=PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=SPACING_LG)
        
        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=SPACING_MD, pady=SPACING_MD, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Demo buttons
        buttons_frame = ctk.CTkFrame(content_frame)
        buttons_frame.grid(row=0, column=0, padx=SPACING_LG, pady=SPACING_LG, sticky="n")
        
        # Demo button 1: Simple fade dialog
        btn1 = ctk.CTkButton(
            buttons_frame,
            text="📋 Show Fade Dialog",
            command=self._show_fade_dialog,
            fg_color=PRIMARY_COLOR,
            text_color="white",
            height=50,
            font=("Arial", 14)
        )
        btn1.grid(row=0, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        
        # Demo button 2: Fade popup
        btn2 = ctk.CTkButton(
            buttons_frame,
            text="💬 Show Fade Popup",
            command=self._show_fade_popup,
            fg_color=SECONDARY_COLOR,
            text_color="white",
            height=50,
            font=("Arial", 14)
        )
        btn2.grid(row=1, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        
        # Demo button 3: Fade confirmation dialog
        btn3 = ctk.CTkButton(
            buttons_frame,
            text="❓ Show Fade Confirmation",
            command=self._show_fade_confirmation,
            fg_color=ACCENT_COLOR,
            text_color="white",
            height=50,
            font=("Arial", 14)
        )
        btn3.grid(row=2, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        
        # Demo button 4: Custom fade dialog
        btn4 = ctk.CTkButton(
            buttons_frame,
            text="🎨 Custom Fade Dialog",
            command=self._show_custom_fade_dialog,
            fg_color=SUCCESS_COLOR,
            text_color="white",
            height=50,
            font=("Arial", 14)
        )
        btn4.grid(row=3, column=0, padx=SPACING_MD, pady=SPACING_SM, sticky="ew")
        
        # Info text
        info_text = ctk.CTkTextbox(buttons_frame, height=150, width=400)
        info_text.grid(row=4, column=0, padx=SPACING_MD, pady=SPACING_MD, sticky="ew")
        
        info_content = """
🎬 Fade Transitions Demo

This demo showcases the smooth fade in/out transitions 
implemented in the Bills Tracker application.

Features:
• 300ms smooth fade animations
• All dialogs fade in when opening
• All dialogs fade out when closing
• Popups and confirmations use fade effects
• Graceful fallback for unsupported systems
• Thread-safe animation handling

Try clicking the buttons above to see the transitions in action!
        """
        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")
    
    def _show_fade_dialog(self):
        """Show a simple fade dialog."""
        dialog, transition_manager = create_fade_dialog(
            self, "Fade Dialog Demo", "400x300", 300
        )
        
        # Add content to the dialog
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(expand=True, fill="both", padx=SPACING_MD, pady=SPACING_MD)
        
        # Title
        title = ctk.CTkLabel(
            content_frame,
            text="✨ Fade Dialog",
            font=("Arial", 18, "bold"),
            text_color=PRIMARY_COLOR
        )
        title.pack(pady=SPACING_MD)
        
        # Message
        message = ctk.CTkLabel(
            content_frame,
            text="This dialog fades in when it opens\nand fades out when you close it!",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        message.pack(pady=SPACING_MD)
        
        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="Close",
            command=lambda: transition_manager.fade_out(dialog.destroy),
            fg_color=ACCENT_COLOR,
            text_color="white"
        )
        close_btn.pack(pady=SPACING_MD)
    
    def _show_fade_popup(self):
        """Show a fade popup."""
        show_fade_popup(
            self,
            "Success!",
            "This popup fades in and out smoothly.\nTry clicking OK to see the fade out effect!",
            "green"
        )
    
    def _show_fade_confirmation(self):
        """Show a fade confirmation dialog."""
        def on_confirm():
            show_fade_popup(self, "Confirmed!", "You clicked Confirm!", "blue")
        
        def on_cancel():
            show_fade_popup(self, "Cancelled!", "You clicked Cancel!", "orange")
        
        show_fade_confirmation_dialog(
            self,
            "Confirm Action",
            "This confirmation dialog uses fade transitions.\nClick Confirm or Cancel to see the effect!",
            on_confirm,
            on_cancel
        )
    
    def _show_custom_fade_dialog(self):
        """Show a custom fade dialog with manual transition management."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Custom Fade Dialog")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"450x350+{x}+{y}")
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        dialog.lift()
        
        # Create transition manager
        transition_manager = TransitionManager(dialog, 500)  # 500ms for slower effect
        
        # Add content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(expand=True, fill="both", padx=SPACING_MD, pady=SPACING_MD)
        
        # Title
        title = ctk.CTkLabel(
            content_frame,
            text="🎨 Custom Fade Dialog",
            font=("Arial", 20, "bold"),
            text_color=PRIMARY_COLOR
        )
        title.pack(pady=SPACING_MD)
        
        # Description
        desc = ctk.CTkLabel(
            content_frame,
            text="This dialog uses a custom 500ms fade duration\nfor a more dramatic effect!",
            font=("Arial", 12),
            text_color=TEXT_COLOR
        )
        desc.pack(pady=SPACING_MD)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(content_frame)
        buttons_frame.pack(pady=SPACING_MD)
        
        # Fade in button
        fade_in_btn = ctk.CTkButton(
            buttons_frame,
            text="Fade In",
            command=transition_manager.fade_in,
            fg_color=SUCCESS_COLOR,
            text_color="white"
        )
        fade_in_btn.pack(side="left", padx=SPACING_SM)
        
        # Fade out button
        fade_out_btn = ctk.CTkButton(
            buttons_frame,
            text="Fade Out",
            command=lambda: transition_manager.fade_out(dialog.destroy),
            fg_color=ERROR_COLOR,
            text_color="white"
        )
        fade_out_btn.pack(side="left", padx=SPACING_SM)
        
        # Start fade in
        dialog.after(100, transition_manager.fade_in)


def main():
    """Main function to run the demo."""
    try:
        # Set appearance mode
        ctk.set_appearance_mode("light")
        
        # Create and run demo
        app = FadeTransitionDemo()
        app.mainloop()
        
    except Exception as e:
        print(f"Error running demo: {e}")
        messagebox.showerror("Demo Error", f"Failed to run demo: {e}")


if __name__ == "__main__":
    main() 