import customtkinter as ctk
import os
from typing import Optional, Tuple
from PIL import Image

class IconManager:
    """
    Utility class for managing icons in the application.
    
    Provides methods to load and cache icons from the filesystem, with fallback
    support when icons are not available. Supports both light and dark themes.
    Now supports multiple icon sets (styles).
    """
    
    def __init__(self, icon_set: str = "default", icon_base_path: str = "resources/icons"):
        """
        Initialize the IconManager.
        
        Args:
            icon_set (str): Name of the icon set (subdirectory in icons/).
            icon_base_path (str): Path to the base directory containing icon sets.
        """
        self.icon_base_path = icon_base_path
        self.icon_set = icon_set
        self._icon_cache = {}
    
    def get_icon_path(self, icon_name: str) -> str:
        """Get the full path to the icon file for the current set."""
        return os.path.join(self.icon_base_path, self.icon_set, f"{icon_name}.png")
    
    def get_icon(self, icon_name: str, size: Tuple[int, int] = (16, 16)) -> Optional[ctk.CTkImage]:
        """
        Get an icon image from the filesystem for the current icon set.
        """
        try:
            icon_file = self.get_icon_path(icon_name)
            if os.path.exists(icon_file):
                pil_image = Image.open(icon_file)
                return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
        except Exception as e:
            print(f"Error loading icon {icon_name} from set '{self.icon_set}': {e}")
        return None
    
    def set_icon_set(self, icon_set: str):
        """Change the current icon set and clear the cache."""
        self.icon_set = icon_set
        self._icon_cache = {}
    
    def get_available_icon_sets(self) -> list:
        """Return a list of available icon set names (subdirectories)."""
        try:
            return [d for d in os.listdir(self.icon_base_path) if os.path.isdir(os.path.join(self.icon_base_path, d))]
        except Exception:
            return ["default"]
    
    def get_button_with_icon(self, master, text: str, icon_name: str = None, 
                           command=None, size: Tuple[int, int] = (16, 16), **kwargs) -> ctk.CTkButton:
        """
        Create a button with optional icon, falling back to text-only if icon not available.
        
        Args:
            master: The parent widget for the button.
            text (str): The text to display on the button.
            icon_name (str, optional): Name of the icon to display (without extension).
            command: The callback function to execute when button is clicked.
            size (Tuple[int, int]): Size of the icon as (width, height) in pixels (default: (16, 16)).
            **kwargs: Additional keyword arguments to pass to CTkButton constructor.
            
        Returns:
            ctk.CTkButton: A button widget with optional icon and text.
        """
        icon = self.get_icon(icon_name, size) if icon_name else None
        
        if icon:
            return ctk.CTkButton(master, text=text, image=icon, command=command, **kwargs)
        else:
            return ctk.CTkButton(master, text=text, command=command, **kwargs)

# Global icon manager instance
icon_manager = IconManager(icon_set="default")

# Icon name constants for consistency
ICON_ADD = "add"          # Add/plus icon
ICON_EDIT = "edit"        # Edit/pencil icon
ICON_DELETE = "delete"    # Delete/trash icon
ICON_SAVE = "save"        # Save/disk icon
ICON_CANCEL = "cancel"    # Cancel/X icon
ICON_SEARCH = "search"    # Search/magnifying glass icon
ICON_CALENDAR = "calendar"  # Calendar icon
ICON_EXPORT = "export"    # Export/download icon
ICON_IMPORT = "import"    # Import/upload icon
ICON_REFRESH = "refresh"  # Refresh/reload icon
ICON_SETTINGS = "settings"  # Settings/gear icon
ICON_CATEGORIES = "categories"  # Categories/tags icon
ICON_BILLS = "bills"      # Bills/document icon
ICON_APPLY = "apply"      # Apply/checkmark icon
ICON_CLEAR = "clear"      # Clear/reset icon 