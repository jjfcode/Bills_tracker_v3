"""
Configuration Manager for Bills Tracker application.
"""

import json
import os
from typing import Dict, Any, Optional
from ..utils.constants import *


class ConfigManager:
    """
    Manages application configuration and settings.

    Provides methods to get and set configuration values, persist settings, and manage app preferences.
    Supports dot notation for nested keys and includes helpers for all major app settings.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the ConfigManager.

        Args:
            config_file (str): Path to the configuration file.
        """
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
        """
        Get configuration value by key (supports dot notation).

        Args:
            key (str): The configuration key (dot notation supported).
            default (Any): Default value if key is not found.
        Returns:
            Any: The configuration value or default.
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by key (supports dot notation).

        Args:
            key (str): The configuration key (dot notation supported).
            value (Any): The value to set.
        """
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
        """
        Get the current theme (e.g., 'light', 'dark', 'system').

        Returns:
            str: The current theme.
        """
        return self.get("theme", "light")
    
    def set_theme(self, theme: str):
        """
        Set the current theme.

        Args:
            theme (str): The theme to set.
        """
        self.set("theme", theme)
    
    def get_window_size(self) -> Dict[str, int]:
        """
        Get the window size settings.

        Returns:
            Dict[str, int]: Dictionary with 'width' and 'height'.
        """
        return self.get("window_size", {"width": DEFAULT_WINDOW_WIDTH, "height": DEFAULT_WINDOW_HEIGHT})
    
    def set_window_size(self, width: int, height: int):
        """
        Set the window size.

        Args:
            width (int): Window width.
            height (int): Window height.
        """
        self.set("window_size", {"width": width, "height": height})
    
    def get_items_per_page(self) -> int:
        """
        Get the number of items per page for pagination.

        Returns:
            int: Items per page.
        """
        return self.get("pagination.items_per_page", DEFAULT_ITEMS_PER_PAGE)
    
    def set_items_per_page(self, items: int):
        """
        Set the number of items per page for pagination.

        Args:
            items (int): Items per page.
        """
        self.set("pagination.items_per_page", items)
    
    def get_notifications_enabled(self) -> bool:
        """
        Get whether notifications are enabled.

        Returns:
            bool: True if enabled, False otherwise.
        """
        return self.get("notifications.enabled", True)
    
    def set_notifications_enabled(self, enabled: bool):
        """
        Set whether notifications are enabled.

        Args:
            enabled (bool): Enable or disable notifications.
        """
        self.set("notifications.enabled", enabled)
    
    def get_check_interval(self) -> int:
        """
        Get the reminder check interval in seconds.

        Returns:
            int: Check interval in seconds.
        """
        return self.get("notifications.check_interval", DEFAULT_REMINDER_CHECK_INTERVAL)
    
    def set_check_interval(self, interval: int):
        """
        Set the reminder check interval in seconds.

        Args:
            interval (int): Check interval in seconds.
        """
        self.set("notifications.check_interval", interval)
    
    def get_auto_close_notifications(self) -> bool:
        """
        Get whether notifications auto-close.

        Returns:
            bool: True if auto-close is enabled.
        """
        return self.get("notifications.auto_close", True)
    
    def set_auto_close_notifications(self, enabled: bool):
        """
        Set whether notifications auto-close.

        Args:
            enabled (bool): Enable or disable auto-close.
        """
        self.set("notifications.auto_close", enabled)
    
    def get_notification_timeout(self) -> int:
        """
        Get the notification timeout in seconds.

        Returns:
            int: Timeout in seconds.
        """
        return self.get("notifications.timeout", DEFAULT_NOTIFICATION_TIMEOUT)
    
    def set_notification_timeout(self, timeout: int):
        """
        Set the notification timeout in seconds.

        Args:
            timeout (int): Timeout in seconds.
        """
        self.set("notifications.timeout", timeout)
    
    def get_auto_backup(self) -> bool:
        """
        Get whether auto-backup is enabled.

        Returns:
            bool: True if enabled.
        """
        return self.get("backup.auto_backup", True)
    
    def set_auto_backup(self, enabled: bool):
        """
        Set whether auto-backup is enabled.

        Args:
            enabled (bool): Enable or disable auto-backup.
        """
        self.set("backup.auto_backup", enabled)
    
    def get_backup_interval(self) -> int:
        """
        Get the backup interval in days.

        Returns:
            int: Backup interval in days.
        """
        return self.get("backup.backup_interval_days", 7)
    
    def set_backup_interval(self, days: int):
        """
        Set the backup interval in days.

        Args:
            days (int): Backup interval in days.
        """
        self.set("backup.backup_interval_days", days)
    
    def get_max_backups(self) -> int:
        """
        Get the maximum number of backups to keep.

        Returns:
            int: Maximum number of backups.
        """
        return self.get("backup.max_backups", 10)
    
    def set_max_backups(self, max_backups: int):
        """
        Set the maximum number of backups to keep.

        Args:
            max_backups (int): Maximum number of backups.
        """
        self.set("backup.max_backups", max_backups)
    
    def get_auto_compact(self) -> bool:
        """
        Get whether auto-compact is enabled for the database.

        Returns:
            bool: True if enabled.
        """
        return self.get("database.auto_compact", True)
    
    def set_auto_compact(self, enabled: bool):
        """
        Set whether auto-compact is enabled for the database.

        Args:
            enabled (bool): Enable or disable auto-compact.
        """
        self.set("database.auto_compact", enabled)
    
    def get_compact_interval(self) -> int:
        """
        Get the database compact interval in days.

        Returns:
            int: Compact interval in days.
        """
        return self.get("database.compact_interval_days", 30)
    
    def set_compact_interval(self, days: int):
        """
        Set the database compact interval in days.

        Args:
            days (int): Compact interval in days.
        """
        self.set("database.compact_interval_days", days)
    
    def get_show_sidebar(self) -> bool:
        """
        Get whether the sidebar is shown.

        Returns:
            bool: True if sidebar is shown.
        """
        return self.get("ui.show_sidebar", True)
    
    def set_show_sidebar(self, show: bool):
        """
        Set whether the sidebar is shown.

        Args:
            show (bool): Show or hide the sidebar.
        """
        self.set("ui.show_sidebar", show)
    
    def get_sidebar_width(self) -> int:
        """
        Get the sidebar width in pixels.

        Returns:
            int: Sidebar width in pixels.
        """
        return self.get("ui.sidebar_width", 200)
    
    def set_sidebar_width(self, width: int):
        """
        Set the sidebar width in pixels.

        Args:
            width (int): Sidebar width in pixels.
        """
        self.set("ui.sidebar_width", width)
    
    def get_table_row_height(self) -> int:
        """
        Get the table row height in pixels.

        Returns:
            int: Table row height in pixels.
        """
        return self.get("ui.table_row_height", 30)
    
    def set_table_row_height(self, height: int):
        """
        Set the table row height in pixels.

        Args:
            height (int): Table row height in pixels.
        """
        self.set("ui.table_row_height", height)
    
    def get_alternating_colors(self) -> bool:
        """
        Get whether alternating row colors are enabled.

        Returns:
            bool: True if alternating colors are enabled.
        """
        return self.get("ui.alternating_colors", True)
    
    def set_alternating_colors(self, enabled: bool):
        """
        Set whether alternating row colors are enabled.

        Args:
            enabled (bool): Enable or disable alternating colors.
        """
        self.set("ui.alternating_colors", enabled)
    
    def get_export_format(self) -> str:
        """
        Get the default export format (e.g., 'csv', 'excel').

        Returns:
            str: Export format.
        """
        return self.get("export.default_format", "csv")
    
    def set_export_format(self, format_type: str):
        """
        Set the default export format.

        Args:
            format_type (str): Export format (e.g., 'csv', 'excel').
        """
        self.set("export.default_format", format_type)
    
    def get_export_headers(self) -> bool:
        """
        Get whether to include headers in exports.

        Returns:
            bool: True if headers are included.
        """
        return self.get("export.include_headers", True)
    
    def set_export_headers(self, include: bool):
        """
        Set whether to include headers in exports.

        Args:
            include (bool): Include headers or not.
        """
        self.set("export.include_headers", include)
    
    def get_export_date_format(self) -> str:
        """
        Get the export date format string.

        Returns:
            str: Date format string.
        """
        return self.get("export.date_format", DATE_FORMAT)
    
    def set_export_date_format(self, date_format: str):
        """
        Set the export date format string.

        Args:
            date_format (str): Date format string.
        """
        self.set("export.date_format", date_format)
    
    def reset_to_defaults(self):
        """
        Reset all configuration settings to their default values and save.
        """
        self.config = self._load_default_config()
        self._save_config()
    
    def export_config(self, filename: str) -> bool:
        """
        Export the current configuration to a file.

        Args:
            filename (str): Path to the export file.
        Returns:
            bool: True if export succeeded, False otherwise.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, filename: str) -> bool:
        """
        Import configuration from a file, merging with current settings.

        Args:
            filename (str): Path to the import file.
        Returns:
            bool: True if import succeeded, False otherwise.
        """
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