"""
Unit tests for configuration manager.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from src.core.config_manager import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_init_with_default_config(self, test_config_path):
        """Test initialization with default configuration."""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Check that default config is loaded
                assert config.get_theme() == "light"
                assert config.get_items_per_page() == 20
                assert config.get_notifications_enabled() is True
                assert config.get_auto_backup() is True
    
    def test_init_load_existing_config(self, test_config_path):
        """Test initialization with existing configuration file."""
        existing_config = {
            "theme": "dark",
            "pagination": {"items_per_page": 50},
            "notifications": {"enabled": False}
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(existing_config))):
            with patch('os.path.exists', return_value=True):
                config = ConfigManager(test_config_path)
                
                # Check that existing config is loaded
                assert config.get_theme() == "dark"
                assert config.get_items_per_page() == 50
                assert config.get_notifications_enabled() is False
    
    def test_init_load_invalid_config(self, test_config_path):
        """Test initialization with invalid configuration file."""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with patch('os.path.exists', return_value=True):
                # Should not raise exception, should use defaults
                config = ConfigManager(test_config_path)
                assert config.get_theme() == "light"  # Default value
    
    def test_get_set_basic_values(self, test_config_path):
        """Test getting and setting basic configuration values."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test setting and getting values
                config.set("test_key", "test_value")
                assert config.get("test_key") == "test_value"
                
                config.set("nested.key", "nested_value")
                assert config.get("nested.key") == "nested_value"
    
    def test_get_with_default_value(self, test_config_path):
        """Test getting configuration with default value."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test getting non-existent key with default
                value = config.get("non_existent_key", "default_value")
                assert value == "default_value"
    
    def test_get_nested_key(self, test_config_path):
        """Test getting nested configuration keys."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Set nested configuration
                config.set("ui.settings.color", "blue")
                config.set("ui.settings.size", "large")
                
                # Get nested values
                assert config.get("ui.settings.color") == "blue"
                assert config.get("ui.settings.size") == "large"
                assert config.get("ui.settings") == {"color": "blue", "size": "large"}
    
    def test_theme_management(self, test_config_path):
        """Test theme configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default theme
                assert config.get_theme() == "light"
                
                # Test setting theme
                config.set_theme("dark")
                assert config.get_theme() == "dark"
                
                config.set_theme("system")
                assert config.get_theme() == "system"
    
    def test_window_size_management(self, test_config_path):
        """Test window size configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default window size
                default_size = config.get_window_size()
                assert default_size['width'] == 1200
                assert default_size['height'] == 800
                
                # Test setting window size
                config.set_window_size(1600, 900)
                new_size = config.get_window_size()
                assert new_size['width'] == 1600
                assert new_size['height'] == 900
    
    def test_pagination_settings(self, test_config_path):
        """Test pagination configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default items per page
                assert config.get_items_per_page() == 20
                
                # Test setting items per page
                config.set_items_per_page(50)
                assert config.get_items_per_page() == 50
    
    def test_notification_settings(self, test_config_path):
        """Test notification configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default notification settings
                assert config.get_notifications_enabled() is True
                assert config.get_check_interval() == 300
                assert config.get_auto_close_notifications() is True
                assert config.get_notification_timeout() == 30
                
                # Test setting notification settings
                config.set_notifications_enabled(False)
                config.set_check_interval(600)
                config.set_auto_close_notifications(False)
                config.set_notification_timeout(60)
                
                assert config.get_notifications_enabled() is False
                assert config.get_check_interval() == 600
                assert config.get_auto_close_notifications() is False
                assert config.get_notification_timeout() == 60
    
    def test_backup_settings(self, test_config_path):
        """Test backup configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default backup settings
                assert config.get_auto_backup() is True
                assert config.get_backup_interval() == 7
                assert config.get_max_backups() == 10
                
                # Test setting backup settings
                config.set_auto_backup(False)
                config.set_backup_interval(14)
                config.set_max_backups(20)
                
                assert config.get_auto_backup() is False
                assert config.get_backup_interval() == 14
                assert config.get_max_backups() == 20
    
    def test_database_settings(self, test_config_path):
        """Test database configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default database settings
                assert config.get_auto_compact() is True
                assert config.get_compact_interval() == 30
                
                # Test setting database settings
                config.set_auto_compact(False)
                config.set_compact_interval(60)
                
                assert config.get_auto_compact() is False
                assert config.get_compact_interval() == 60
    
    def test_ui_settings(self, test_config_path):
        """Test UI configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default UI settings
                assert config.get_show_sidebar() is True
                assert config.get_sidebar_width() == 200
                assert config.get_table_row_height() == 30
                assert config.get_alternating_colors() is True
                
                # Test setting UI settings
                config.set_show_sidebar(False)
                config.set_sidebar_width(250)
                config.set_table_row_height(40)
                config.set_alternating_colors(False)
                
                assert config.get_show_sidebar() is False
                assert config.get_sidebar_width() == 250
                assert config.get_table_row_height() == 40
                assert config.get_alternating_colors() is False
    
    def test_export_settings(self, test_config_path):
        """Test export configuration management."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test default export settings
                assert config.get_export_format() == "csv"
                assert config.get_export_headers() is True
                assert config.get_export_date_format() == "2024-02-01"
                
                # Test setting export settings
                config.set_export_format("excel")
                config.set_export_headers(False)
                config.set_export_date_format("MM/DD/YYYY")
                
                assert config.get_export_format() == "excel"
                assert config.get_export_headers() is False
                assert config.get_export_date_format() == "MM/DD/YYYY"
    
    def test_reset_to_defaults(self, test_config_path):
        """Test resetting configuration to defaults."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Modify some settings
                config.set_theme("dark")
                config.set_items_per_page(50)
                config.set_notifications_enabled(False)
                
                # Verify changes
                assert config.get_theme() == "dark"
                assert config.get_items_per_page() == 50
                assert config.get_notifications_enabled() is False
                
                # Reset to defaults
                config.reset_to_defaults()
                
                # Verify defaults are restored
                assert config.get_theme() == "light"
                assert config.get_items_per_page() == 20
                assert config.get_notifications_enabled() is True
    
    def test_export_config(self, test_config_path, temp_dir):
        """Test exporting configuration to file."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Set some custom values
                config.set_theme("dark")
                config.set_items_per_page(50)
                
                # Export configuration
                export_file = f"{temp_dir}/exported_config.json"
                success = config.export_config(export_file)
                
                assert success is True
                assert os.path.exists(export_file)
                
                # Verify exported content
                with open(export_file, 'r') as f:
                    exported_data = json.load(f)
                    assert exported_data['theme'] == "dark"
                    assert exported_data['pagination']['items_per_page'] == 50
    
    def test_export_config_error(self, test_config_path):
        """Test exporting configuration with error."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Try to export to invalid path
                success = config.export_config("/invalid/path/config.json")
                assert success is False
    
    def test_import_config(self, test_config_path, temp_dir):
        """Test importing configuration from file."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Create import file
                import_data = {
                    "theme": "dark",
                    "pagination": {"items_per_page": 100},
                    "notifications": {"enabled": False}
                }
                import_file = f"{temp_dir}/import_config.json"
                with open(import_file, 'w') as f:
                    json.dump(import_data, f)
                
                # Import configuration
                success = config.import_config(import_file)
                assert success is True
                
                # Verify imported values
                assert config.get_theme() == "dark"
                assert config.get_items_per_page() == 100
                assert config.get_notifications_enabled() is False
    
    def test_import_config_error(self, test_config_path):
        """Test importing configuration with error."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Try to import from non-existent file
                success = config.import_config("nonexistent_file.json")
                assert success is False
    
    def test_import_config_invalid_json(self, test_config_path, temp_dir):
        """Test importing configuration with invalid JSON."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Create invalid JSON file
                import_file = f"{temp_dir}/invalid_config.json"
                with open(import_file, 'w') as f:
                    f.write("invalid json content")
                
                # Import should fail
                success = config.import_config(import_file)
                assert success is False
    
    def test_merge_config_partial_update(self, test_config_path):
        """Test merging configuration with partial updates."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Set some initial values
                config.set_theme("light")
                config.set_items_per_page(20)
                config.set_notifications_enabled(True)
                
                # Import partial configuration
                partial_config = {
                    "theme": "dark",
                    "pagination": {"items_per_page": 50}
                    # notifications not included
                }
                
                # Simulate import by directly calling _merge_config
                config._merge_config(config.config, partial_config)
                
                # Verify merged values
                assert config.get_theme() == "dark"  # Updated
                assert config.get_items_per_page() == 50  # Updated
                assert config.get_notifications_enabled() is True  # Unchanged
    
    def test_config_persistence(self, test_config_path):
        """Test that configuration changes are persisted."""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Make changes
                config.set_theme("dark")
                config.set_items_per_page(50)
                
                # Verify that save was called
                assert mock_file.call_count > 0
    
    def test_invalid_key_access(self, test_config_path):
        """Test accessing invalid configuration keys."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Test accessing non-existent keys
                assert config.get("non_existent_key") is None
                assert config.get("deeply.nested.invalid.key") is None
                
                # Test with default value
                assert config.get("non_existent_key", "default") == "default"
    
    def test_complex_nested_structure(self, test_config_path):
        """Test complex nested configuration structure."""
        with patch('builtins.open', mock_open()):
            with patch('os.path.exists', return_value=False):
                config = ConfigManager(test_config_path)
                
                # Set complex nested structure
                config.set("advanced.feature1.enabled", True)
                config.set("advanced.feature1.settings.timeout", 5000)
                config.set("advanced.feature1.settings.retries", 3)
                config.set("advanced.feature2.enabled", False)
                
                # Verify nested access
                assert config.get("advanced.feature1.enabled") is True
                assert config.get("advanced.feature1.settings.timeout") == 5000
                assert config.get("advanced.feature1.settings.retries") == 3
                assert config.get("advanced.feature2.enabled") is False
                
                # Verify partial structure access
                feature1_settings = config.get("advanced.feature1.settings")
                assert feature1_settings == {"timeout": 5000, "retries": 3} 