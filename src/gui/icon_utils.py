import customtkinter as ctk
import os
from typing import Optional, Tuple

class IconManager:
    """Utility class for managing icons in the application"""
    
    def __init__(self, icon_path: str = "resources/icons"):
        self.icon_path = icon_path
        self._icon_cache = {}
    
    def get_icon(self, icon_name: str, size: Tuple[int, int] = (16, 16)) -> Optional[ctk.CTkImage]:
        """Get an icon image, with fallback to None if not found"""
        try:
            icon_file = os.path.join(self.icon_path, f"{icon_name}.png")
            if os.path.exists(icon_file):
                return ctk.CTkImage(light_image=icon_file, dark_image=icon_file, size=size)
        except Exception:
            pass
        return None
    
    def get_button_with_icon(self, master, text: str, icon_name: str = None, 
                           command=None, size: Tuple[int, int] = (16, 16), **kwargs) -> ctk.CTkButton:
        """Create a button with optional icon, falling back to text if icon not available"""
        icon = self.get_icon(icon_name, size) if icon_name else None
        
        if icon:
            return ctk.CTkButton(master, text=text, image=icon, command=command, **kwargs)
        else:
            return ctk.CTkButton(master, text=text, command=command, **kwargs)

# Global icon manager instance
icon_manager = IconManager()

# Icon name constants for consistency
ICON_ADD = "add"
ICON_EDIT = "edit"
ICON_DELETE = "delete"
ICON_SAVE = "save"
ICON_CANCEL = "cancel"
ICON_SEARCH = "search"
ICON_CALENDAR = "calendar"
ICON_EXPORT = "export"
ICON_IMPORT = "import"
ICON_REFRESH = "refresh"
ICON_SETTINGS = "settings"
ICON_CATEGORIES = "categories"
ICON_BILLS = "bills"
ICON_APPLY = "apply"
ICON_CLEAR = "clear" 