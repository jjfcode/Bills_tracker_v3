"""
Transition utilities for smooth fade in/out effects on dialogs.
"""

import customtkinter as ctk
from typing import Optional, Callable
import time


class TransitionManager:
    """
    Manages smooth fade in/out transitions for dialogs.
    """
    
    def __init__(self, dialog: ctk.CTkToplevel, duration_ms: int = 300):
        """
        Initialize the transition manager.
        
        Args:
            dialog: The dialog window to animate
            duration_ms: Duration of the fade animation in milliseconds
        """
        self.dialog = dialog
        self.duration_ms = duration_ms
        self.fade_in_progress = False
        self.fade_out_progress = False
        
        # Store original alpha value
        self.original_alpha = dialog.attributes('-alpha') if hasattr(dialog, 'attributes') else 1.0
        
        # Set initial alpha to 0 for fade in
        if hasattr(dialog, 'attributes'):
            dialog.attributes('-alpha', 0.0)
    
    def fade_in(self, on_complete: Optional[Callable] = None):
        """
        Fade in the dialog from transparent to opaque.
        
        Args:
            on_complete: Optional callback to execute when fade in completes
        """
        if self.fade_in_progress or self.fade_out_progress:
            return
            
        self.fade_in_progress = True
        self._fade_animation(0.0, 1.0, on_complete)
    
    def fade_out(self, on_complete: Optional[Callable] = None):
        """
        Fade out the dialog from opaque to transparent.
        
        Args:
            on_complete: Optional callback to execute when fade out completes
        """
        if self.fade_in_progress or self.fade_out_progress:
            return
            
        self.fade_out_progress = True
        self._fade_animation(1.0, 0.0, on_complete)
    
    def _fade_animation(self, start_alpha: float, end_alpha: float, on_complete: Optional[Callable] = None):
        """
        Perform the fade animation.
        
        Args:
            start_alpha: Starting alpha value (0.0 to 1.0)
            end_alpha: Ending alpha value (0.0 to 1.0)
            on_complete: Optional callback to execute when animation completes
        """
        if not hasattr(self.dialog, 'attributes'):
            # Fallback if alpha attribute is not available
            if on_complete:
                on_complete()
            return
        
        steps = 20  # Number of animation steps
        step_duration = self.duration_ms // steps
        alpha_step = (end_alpha - start_alpha) / steps
        current_alpha = start_alpha
        
        def animate_step(step_count=0):
            if step_count >= steps or not self.dialog.winfo_exists():
                # Animation complete or dialog destroyed
                self.fade_in_progress = False
                self.fade_out_progress = False
                if on_complete:
                    on_complete()
                return
            
            current_alpha = start_alpha + (alpha_step * step_count)
            self.dialog.attributes('-alpha', max(0.0, min(1.0, current_alpha)))
            
            self.dialog.after(step_duration, lambda: animate_step(step_count + 1))
        
        animate_step()


def create_fade_dialog(master, title: str, geometry: str, duration_ms: int = 300) -> tuple[ctk.CTkToplevel, TransitionManager]:
    """
    Create a dialog with fade in/out transitions.
    
    Args:
        master: Parent window
        title: Dialog title
        geometry: Dialog geometry string
        duration_ms: Duration of fade animation in milliseconds
    
    Returns:
        Tuple of (dialog, transition_manager)
    """
    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.geometry(geometry)
    dialog.resizable(False, False)
    
    # Center the dialog
    dialog.update_idletasks()
    width, height = map(int, geometry.split('x'))
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # Make dialog modal
    dialog.transient(master)
    dialog.grab_set()
    dialog.lift()
    
    # Create transition manager
    transition_manager = TransitionManager(dialog, duration_ms)
    
    return dialog, transition_manager


def show_fade_popup(master, title: str, message: str, color: str = "green", 
                   duration_ms: int = 300, callback: Optional[Callable] = None) -> None:
    """
    Show a popup with fade in/out effects.
    
    Args:
        master: Parent widget
        title: Popup title
        message: Popup message
        color: Text color
        duration_ms: Duration of fade animation in milliseconds
        callback: Optional callback to execute when popup is closed
    """
    try:
        dialog, transition_manager = create_fade_dialog(master, title, "350x120", duration_ms)
        
        def close_popup():
            try:
                if dialog.winfo_exists():
                    transition_manager.fade_out(lambda: dialog.destroy())
                    if callback:
                        callback()
            except:
                pass
        
        label = ctk.CTkLabel(dialog, text=message, text_color=color, font=("Arial", 14))
        label.pack(pady=20)
        ctk.CTkButton(dialog, text="OK", command=close_popup).pack(pady=10)
        
        # Start fade in animation
        def start_fade_in():
            try:
                if dialog.winfo_exists():
                    dialog.lift()
                    dialog.focus_force()
                    dialog.grab_set()
                    transition_manager.fade_in()
            except:
                pass
        
        dialog.after(100, start_fade_in)
        
    except Exception as e:
        print(f"Fade Popup Error: {title} - {message}")


def show_fade_confirmation_dialog(master, title: str, message: str, 
                                on_confirm: Callable, on_cancel: Optional[Callable] = None,
                                duration_ms: int = 300) -> None:
    """
    Show a confirmation dialog with fade in/out effects.
    
    Args:
        master: Parent widget
        title: Dialog title
        message: Dialog message
        on_confirm: Callback for confirm action
        on_cancel: Optional callback for cancel action
        duration_ms: Duration of fade animation in milliseconds
    """
    try:
        dialog, transition_manager = create_fade_dialog(master, title, "400x150", duration_ms)
        
        def confirm():
            try:
                if dialog.winfo_exists():
                    transition_manager.fade_out(lambda: dialog.destroy())
                    on_confirm()
            except:
                pass
        
        def cancel():
            try:
                if dialog.winfo_exists():
                    transition_manager.fade_out(lambda: dialog.destroy())
                    if on_cancel:
                        on_cancel()
            except:
                pass
        
        # Message label
        label = ctk.CTkLabel(dialog, text=message, font=("Arial", 12))
        label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        from .constants import ERROR_COLOR, SPACING_SM
        ctk.CTkButton(button_frame, text="Confirm", command=confirm, 
                     fg_color=ERROR_COLOR, text_color="white").pack(side="left", padx=SPACING_SM)
        ctk.CTkButton(button_frame, text="Cancel", command=cancel).pack(side="left", padx=SPACING_SM)
        
        # Start fade in animation
        def start_fade_in():
            try:
                if dialog.winfo_exists():
                    dialog.lift()
                    dialog.focus_force()
                    transition_manager.fade_in()
            except:
                pass
        
        dialog.after(100, start_fade_in)
        
    except Exception as e:
        print(f"Fade Confirmation Dialog Error: {title} - {message}")


class FadeDialogMixin:
    """
    Mixin class to add fade transitions to existing dialog classes.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transition_manager = None
        self._setup_transitions()
    
    def _setup_transitions(self):
        """Setup fade transitions for the dialog."""
        if hasattr(self, 'attributes'):
            self.transition_manager = TransitionManager(self, 300)
            # Start fade in after a short delay
            self.after(50, self._start_fade_in)
    
    def _start_fade_in(self):
        """Start the fade in animation."""
        if self.transition_manager:
            self.transition_manager.fade_in()
    
    def _fade_out_and_destroy(self, callback: Optional[Callable] = None):
        """Fade out the dialog and then destroy it."""
        if self.transition_manager:
            self.transition_manager.fade_out(lambda: self._destroy_with_callback(callback))
        else:
            self._destroy_with_callback(callback)
    
    def _destroy_with_callback(self, callback: Optional[Callable] = None):
        """Destroy the dialog and execute callback."""
        try:
            if self.winfo_exists():
                self.destroy()
                if callback:
                    callback()
        except:
            pass 