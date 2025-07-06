"""
Configuration Manager for Bills Tracker application.
"""

import json
import os
from typing import Dict, Any, Optional
from ..utils.constants import *


class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "theme": "light",
            "window_size": {
                "width": DEFAULT_WINDOW_WIDTH,
                "height": DEFAULT_WINDOW_HEIGHT
            },
            "pagination": {
                "items_per_page": DEFAULT_ITEMS_PER_PAGE
            },
            "notifications": {
                "enabled": True,
                "check_interval": DEFAULT_REMINDER_CHECK_INTERVAL,
                "auto_close": True,
                "timeout": DEFAULT_NOTIFICATION_TIMEOUT
            },
            "backup": {
                "auto_backup": True,
                "backup_interval_days": 7,
                "max_backups": 10
            },
            "database": {
                "auto_compact": True,
                "compact_interval_days": 30
            },
            "ui": {
                "show_sidebar": True,
                "sidebar_width": 200,
                "table_row_height": 30,
                "alternating_colors": True
            },
            "export": {
                "default_format": "csv",
                "include_headers": True,
                "date_format": DATE_FORMAT
            }
        }
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # Merge with defaults, keeping defaults for missing keys
                    self._merge_config(self.config, file_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]):
        """Recursively merge user config with defaults."""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config()
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.get("theme", "light")
    
    def set_theme(self, theme: str):
        """Set theme."""
        self.set("theme", theme)
    
    def get_window_size(self) -> Dict[str, int]:
        """Get window size."""
        return self.get("window_size", {"width": DEFAULT_WINDOW_WIDTH, "height": DEFAULT_WINDOW_HEIGHT})
    
    def set_window_size(self, width: int, height: int):
        """Set window size."""
        self.set("window_size", {"width": width, "height": height})
    
    def get_items_per_page(self) -> int:
        """Get items per page setting."""
        return self.get("pagination.items_per_page", DEFAULT_ITEMS_PER_PAGE)
    
    def set_items_per_page(self, items: int):
        """Set items per page."""
        self.set("pagination.items_per_page", items)
    
    def get_notifications_enabled(self) -> bool:
        """Get notifications enabled setting."""
        return self.get("notifications.enabled", True)
    
    def set_notifications_enabled(self, enabled: bool):
        """Set notifications enabled."""
        self.set("notifications.enabled", enabled)
    
    def get_check_interval(self) -> int:
        """Get reminder check interval."""
        return self.get("notifications.check_interval", DEFAULT_REMINDER_CHECK_INTERVAL)
    
    def set_check_interval(self, interval: int):
        """Set reminder check interval."""
        self.set("notifications.check_interval", interval)
    
    def get_auto_close_notifications(self) -> bool:
        """Get auto close notifications setting."""
        return self.get("notifications.auto_close", True)
    
    def set_auto_close_notifications(self, enabled: bool):
        """Set auto close notifications."""
        self.set("notifications.auto_close", enabled)
    
    def get_notification_timeout(self) -> int:
        """Get notification timeout."""
        return self.get("notifications.timeout", DEFAULT_NOTIFICATION_TIMEOUT)
    
    def set_notification_timeout(self, timeout: int):
        """Set notification timeout."""
        self.set("notifications.timeout", timeout)
    
    def get_auto_backup(self) -> bool:
        """Get auto backup setting."""
        return self.get("backup.auto_backup", True)
    
    def set_auto_backup(self, enabled: bool):
        """Set auto backup."""
        self.set("backup.auto_backup", enabled)
    
    def get_backup_interval(self) -> int:
        """Get backup interval in days."""
        return self.get("backup.backup_interval_days", 7)
    
    def set_backup_interval(self, days: int):
        """Set backup interval."""
        self.set("backup.backup_interval_days", days)
    
    def get_max_backups(self) -> int:
        """Get maximum number of backups to keep."""
        return self.get("backup.max_backups", 10)
    
    def set_max_backups(self, max_backups: int):
        """Set maximum number of backups."""
        self.set("backup.max_backups", max_backups)
    
    def get_auto_compact(self) -> bool:
        """Get auto compact database setting."""
        return self.get("database.auto_compact", True)
    
    def set_auto_compact(self, enabled: bool):
        """Set auto compact database."""
        self.set("database.auto_compact", enabled)
    
    def get_compact_interval(self) -> int:
        """Get database compact interval in days."""
        return self.get("database.compact_interval_days", 30)
    
    def set_compact_interval(self, days: int):
        """Set database compact interval."""
        self.set("database.compact_interval_days", days)
    
    def get_show_sidebar(self) -> bool:
        """Get show sidebar setting."""
        return self.get("ui.show_sidebar", True)
    
    def set_show_sidebar(self, show: bool):
        """Set show sidebar."""
        self.set("ui.show_sidebar", show)
    
    def get_sidebar_width(self) -> int:
        """Get sidebar width."""
        return self.get("ui.sidebar_width", 200)
    
    def set_sidebar_width(self, width: int):
        """Set sidebar width."""
        self.set("ui.sidebar_width", width)
    
    def get_table_row_height(self) -> int:
        """Get table row height."""
        return self.get("ui.table_row_height", 30)
    
    def set_table_row_height(self, height: int):
        """Set table row height."""
        self.set("ui.table_row_height", height)
    
    def get_alternating_colors(self) -> bool:
        """Get alternating colors setting."""
        return self.get("ui.alternating_colors", True)
    
    def set_alternating_colors(self, enabled: bool):
        """Set alternating colors."""
        self.set("ui.alternating_colors", enabled)
    
    def get_export_format(self) -> str:
        """Get default export format."""
        return self.get("export.default_format", "csv")
    
    def set_export_format(self, format_type: str):
        """Set default export format."""
        self.set("export.default_format", format_type)
    
    def get_export_headers(self) -> bool:
        """Get include headers in export setting."""
        return self.get("export.include_headers", True)
    
    def set_export_headers(self, include: bool):
        """Set include headers in export."""
        self.set("export.include_headers", include)
    
    def get_export_date_format(self) -> str:
        """Get export date format."""
        return self.get("export.date_format", DATE_FORMAT)
    
    def set_export_date_format(self, date_format: str):
        """Set export date format."""
        self.set("export.date_format", date_format)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._load_default_config()
        self._save_config()
    
    def export_config(self, filename: str) -> bool:
        """Export configuration to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filename: str) -> bool:
        """Import configuration from file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Merge with current config
            self._merge_config(self.config, imported_config)
            self._save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False


# Global configuration instance
config_manager = ConfigManager() 