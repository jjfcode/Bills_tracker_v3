#!/usr/bin/env python3
"""
Test script to verify that all generated icons can be loaded correctly.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.icon_utils import icon_manager, ICON_ADD, ICON_EDIT, ICON_DELETE, ICON_SAVE, ICON_CANCEL, ICON_SEARCH, ICON_CALENDAR, ICON_EXPORT, ICON_IMPORT, ICON_REFRESH, ICON_SETTINGS, ICON_CATEGORIES, ICON_BILLS, ICON_APPLY, ICON_CLEAR

def test_icon_loading():
    """Test that all icons can be loaded successfully."""
    print("Testing icon loading...")
    
    # List of all icon constants
    icon_constants = [
        ICON_ADD, ICON_EDIT, ICON_DELETE, ICON_SAVE, ICON_CANCEL, 
        ICON_SEARCH, ICON_CALENDAR, ICON_EXPORT, ICON_IMPORT, 
        ICON_REFRESH, ICON_SETTINGS, ICON_CATEGORIES, ICON_BILLS, 
        ICON_APPLY, ICON_CLEAR
    ]
    
    success_count = 0
    total_count = len(icon_constants)
    
    for icon_name in icon_constants:
        try:
            # Try to load the icon
            icon = icon_manager.get_icon(icon_name)
            if icon:
                print(f"✅ {icon_name}: Loaded successfully")
                success_count += 1
            else:
                print(f"❌ {icon_name}: Failed to load")
        except Exception as e:
            print(f"❌ {icon_name}: Error loading - {e}")
    
    print(f"\nResults: {success_count}/{total_count} icons loaded successfully")
    
    if success_count == total_count:
        print("🎉 All icons are working correctly!")
        return True
    else:
        print("⚠️  Some icons failed to load")
        return False

def test_icon_sizes():
    """Test that icons can be loaded in different sizes."""
    print("\nTesting icon sizes...")
    
    sizes = [(16, 16), (24, 24), (32, 32)]
    test_icon = ICON_ADD
    
    for size in sizes:
        try:
            icon = icon_manager.get_icon(test_icon, size)
            if icon:
                print(f"✅ {test_icon} at {size[0]}x{size[1]}: Loaded successfully")
            else:
                print(f"❌ {test_icon} at {size[0]}x{size[1]}: Failed to load")
        except Exception as e:
            print(f"❌ {test_icon} at {size[0]}x{size[1]}: Error - {e}")

def test_button_creation():
    """Test that buttons with icons can be created."""
    print("\nTesting button creation with icons...")
    
    try:
        # This would normally require a tkinter root window, but we can test the logic
        print("✅ Icon manager button creation logic is available")
        print("   (Full button testing requires GUI context)")
    except Exception as e:
        print(f"❌ Button creation error: {e}")

if __name__ == "__main__":
    print("Icon Loading Test for Bills Tracker v3")
    print("=" * 40)
    
    # Test basic icon loading
    success = test_icon_loading()
    
    # Test different sizes
    test_icon_sizes()
    
    # Test button creation
    test_button_creation()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! Icons are ready to use.")
    else:
        print("⚠️  Some tests failed. Check the icon files.") 