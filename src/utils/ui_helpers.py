"""
UI helper functions for Bills Tracker application.
"""

import customtkinter as ctk
from typing import Optional, Callable
from .constants import *
from .transition_utils import show_fade_popup, show_fade_confirmation_dialog


def show_popup(master, title: str, message: str, color: str = "green", 
               callback: Optional[Callable] = None) -> None:
    """
    Show a popup message with consistent styling and fade transitions.
    
    Args:
        master: Parent widget
        title: Popup title
        message: Popup message
        color: Text color
        callback: Optional callback to execute when popup is closed
    """
    show_fade_popup(master, title, message, color, 300, callback)


def show_confirmation_dialog(master, title: str, message: str, 
                           on_confirm: Callable, on_cancel: Optional[Callable] = None) -> None:
    """
    Show a confirmation dialog with consistent styling and fade transitions.
    
    Args:
        master: Parent widget
        title: Dialog title
        message: Dialog message
        on_confirm: Callback for confirm action
        on_cancel: Optional callback for cancel action
    """
    show_fade_confirmation_dialog(master, title, message, on_confirm, on_cancel, 300)


def center_window(window, width: int, height: int) -> None:
    """
    Center a window on the screen.
    
    Args:
        window: Window to center
        width: Window width
        height: Window height
    """
    try:
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    except:
        pass


def create_styled_button(parent, text: str, command: Callable, 
                        fg_color: str = PRIMARY_COLOR, 
                        text_color: str = "white",
                        width: Optional[int] = None,
                        height: Optional[int] = None) -> ctk.CTkButton:
    """
    Create a consistently styled button.
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button command
        fg_color: Background color
        text_color: Text color
        width: Button width
        height: Button height
        
    Returns:
        Styled CTkButton
    """
    return ctk.CTkButton(
        parent, 
        text=text, 
        command=command,
        fg_color=fg_color,
        text_color=text_color,
        width=width,
        height=height,
        font=("Arial", 12)
    )


def create_styled_label(parent, text: str, 
                       text_color: str = TEXT_COLOR,
                       font_size: int = 12,
                       **kwargs) -> ctk.CTkLabel:
    """
    Create a consistently styled label.
    
    Args:
        parent: Parent widget
        text: Label text
        text_color: Text color
        font_size: Font size
        **kwargs: Additional keyword arguments
        
    Returns:
        Styled CTkLabel
    """
    return ctk.CTkLabel(
        parent,
        text=text,
        text_color=text_color,
        font=("Arial", font_size),
        **kwargs
    )


def create_styled_entry(parent, placeholder: str = "", 
                       text_color: str = TEXT_COLOR,
                       fg_color: str = BACKGROUND_COLOR,
                       **kwargs) -> ctk.CTkEntry:
    """
    Create a consistently styled entry field.
    
    Args:
        parent: Parent widget
        placeholder: Placeholder text
        text_color: Text color
        fg_color: Background color
        **kwargs: Additional keyword arguments
        
    Returns:
        Styled CTkEntry
    """
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        text_color=text_color,
        fg_color=fg_color,
        font=("Arial", 12),
        **kwargs
    )


def create_styled_frame(parent, fg_color: str = BACKGROUND_COLOR, **kwargs) -> ctk.CTkFrame:
    """
    Create a consistently styled frame.
    
    Args:
        parent: Parent widget
        fg_color: Background color
        **kwargs: Additional keyword arguments
        
    Returns:
        Styled CTkFrame
    """
    return ctk.CTkFrame(
        parent,
        fg_color=fg_color,
        **kwargs
    )


def apply_table_styling(treeview, alternating_colors: bool = True) -> None:
    """
    Apply consistent styling to a treeview table.
    
    Args:
        treeview: Treeview widget to style
        alternating_colors: Whether to apply alternating row colors
    """
    try:
        # Configure tags for alternating colors
        if alternating_colors:
            treeview.tag_configure('oddrow', background='#f0f0f0')
            treeview.tag_configure('evenrow', background='#ffffff')
        
        # Configure selection colors
        treeview.tag_configure('selected', background=PRIMARY_COLOR, foreground='white')
        
        # Set row height
        style = treeview.master.tk.call("ttk::style", "theme", "use", "default")
        treeview.master.tk.call("ttk::style", "configure", "Treeview", rowheight=30)
        
    except Exception as e:
        print(f"Table styling error: {e}")


def create_pagination_frame(parent) -> ctk.CTkFrame:
    """
    Create a consistently styled pagination frame.
    
    Args:
        parent: Parent widget
        
    Returns:
        Styled pagination frame
    """
    frame = create_styled_frame(parent)
    
    # Navigation buttons
    btn_frame = create_styled_frame(frame)
    btn_frame.pack(side="left", padx=SPACING_SM)
    
    first_btn = create_styled_button(btn_frame, "⏮", lambda: None, width=40)
    first_btn.pack(side="left", padx=2)
    
    prev_btn = create_styled_button(btn_frame, "◀", lambda: None, width=40)
    prev_btn.pack(side="left", padx=2)
    
    next_btn = create_styled_button(btn_frame, "▶", lambda: None, width=40)
    next_btn.pack(side="left", padx=2)
    
    last_btn = create_styled_button(btn_frame, "⏭", lambda: None, width=40)
    last_btn.pack(side="left", padx=2)
    
    # Info label
    info_label = create_styled_label(frame, "Page 1 of 1")
    info_label.pack(side="left", padx=SPACING_MD)
    
    # Items per page selector
    items_frame = create_styled_frame(frame)
    items_frame.pack(side="right", padx=SPACING_SM)
    
    create_styled_label(items_frame, "Items per page:").pack(side="left", padx=SPACING_SM)
    
    items_combo = ctk.CTkComboBox(
        items_frame,
        values=[str(x) for x in ITEMS_PER_PAGE_OPTIONS],
        width=60,
        font=("Arial", 10)
    )
    items_combo.pack(side="left", padx=SPACING_SM)
    items_combo.set(str(DEFAULT_ITEMS_PER_PAGE))
    
    return frame 