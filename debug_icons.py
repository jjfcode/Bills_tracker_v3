#!/usr/bin/env python3
"""
Debug script to check icon loading issues.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.icon_utils import icon_manager, ICON_ADD

def debug_icon_path():
    """Debug the icon path resolution."""
    print("Debugging icon path...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Icon manager path: {icon_manager.icon_path}")
    
    # Check if the path exists
    icon_path = icon_manager.icon_path
    print(f"Icon path exists: {os.path.exists(icon_path)}")
    
    if os.path.exists(icon_path):
        print(f"Icon path contents:")
        for file in os.listdir(icon_path):
            print(f"  {file}")
    
    # Test specific icon file
    icon_file = os.path.join(icon_path, f"{ICON_ADD}.png")
    print(f"\nTesting icon file: {icon_file}")
    print(f"Icon file exists: {os.path.exists(icon_file)}")
    
    if os.path.exists(icon_file):
        print(f"Icon file size: {os.path.getsize(icon_file)} bytes")
        print(f"Icon file is readable: {os.access(icon_file, os.R_OK)}")

def test_absolute_path():
    """Test with absolute path."""
    print("\nTesting with absolute path...")
    
    # Get absolute path to icons directory
    current_dir = os.getcwd()
    absolute_icon_path = os.path.join(current_dir, "resources", "icons")
    print(f"Absolute icon path: {absolute_icon_path}")
    print(f"Absolute path exists: {os.path.exists(absolute_icon_path)}")
    
    # Test icon file with absolute path
    icon_file = os.path.join(absolute_icon_path, f"{ICON_ADD}.png")
    print(f"Absolute icon file: {icon_file}")
    print(f"Absolute icon file exists: {os.path.exists(icon_file)}")

if __name__ == "__main__":
    print("Icon Debug for Bills Tracker v3")
    print("=" * 40)
    
    debug_icon_path()
    test_absolute_path() 