import json
import os
from typing import Any, Dict, Optional

class ConfigManager:
    """
    Manages application configuration and user preferences.
    Stores settings in a JSON file for persistence.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config."""
        default_config = {
            "theme": "System",
            "auto_backup": False,
            "backup_interval_days": 7,
            "notifications_enabled": True,
            "auto_close_notifications": True,
            "reminder_check_interval": 300,
            "max_notifications": 3,
            "window_width": 1200,
            "window_height": 800,
            "items_per_page": 20,
            "last_backup_date": None,
            "database_version": "3.0"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            else:
                # Create default config file
                self._save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self._save_config(self.config)
    
    def get_theme(self) -> str:
        """Get current theme setting."""
        return self.get("theme", "System")
    
    def set_theme(self, theme: str):
        """Set theme preference."""
        self.set("theme", theme)
    
    def get_auto_backup(self) -> bool:
        """Get auto-backup setting."""
        return self.get("auto_backup", False)
    
    def set_auto_backup(self, enabled: bool):
        """Set auto-backup setting."""
        self.set("auto_backup", enabled)
    
    def get_notifications_enabled(self) -> bool:
        """Get notifications enabled setting."""
        return self.get("notifications_enabled", True)
    
    def set_notifications_enabled(self, enabled: bool):
        """Set notifications enabled setting."""
        self.set("notifications_enabled", enabled)
    
    def get_auto_close_notifications(self) -> bool:
        """Get auto-close notifications setting."""
        return self.get("auto_close_notifications", True)
    
    def set_auto_close_notifications(self, enabled: bool):
        """Set auto-close notifications setting."""
        self.set("auto_close_notifications", enabled)
    
    def get_reminder_check_interval(self) -> int:
        """Get reminder check interval in seconds."""
        return self.get("reminder_check_interval", 300)
    
    def set_reminder_check_interval(self, interval: int):
        """Set reminder check interval in seconds."""
        self.set("reminder_check_interval", interval)
    
    def get_max_notifications(self) -> int:
        """Get maximum number of notifications to show."""
        return self.get("max_notifications", 3)
    
    def set_max_notifications(self, max_count: int):
        """Set maximum number of notifications to show."""
        self.set("max_notifications", max_count)
    
    def get_window_size(self) -> tuple:
        """Get saved window size."""
        width = self.get("window_width", 1200)
        height = self.get("window_height", 800)
        return (width, height)
    
    def set_window_size(self, width: int, height: int):
        """Set saved window size."""
        self.set("window_width", width)
        self.set("window_height", height)
    
    def get_items_per_page(self) -> int:
        """Get items per page setting."""
        return self.get("items_per_page", 20)
    
    def set_items_per_page(self, count: int):
        """Set items per page setting."""
        self.set("items_per_page", count)
    
    def get_last_backup_date(self) -> Optional[str]:
        """Get last backup date."""
        return self.get("last_backup_date")
    
    def set_last_backup_date(self, date: str):
        """Set last backup date."""
        self.set("last_backup_date", date)
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        default_config = {
            "theme": "System",
            "auto_backup": False,
            "backup_interval_days": 7,
            "notifications_enabled": True,
            "auto_close_notifications": True,
            "reminder_check_interval": 300,
            "max_notifications": 3,
            "window_width": 1200,
            "window_height": 800,
            "items_per_page": 20,
            "last_backup_date": None,
            "database_version": "3.0"
        }
        self.config = default_config
        self._save_config(self.config)
    
    def export_config(self, file_path: str):
        """Export configuration to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting config: {e}")
    
    def import_config(self, file_path: str):
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                self.config.update(imported_config)
                self._save_config(self.config)
        except Exception as e:
            print(f"Error importing config: {e}")

# Global config instance
config_manager = ConfigManager() 