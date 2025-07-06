#!/usr/bin/env python3
"""
Comprehensive icon test script with CustomTkinter initialization.
"""

import os
import sys
import customtkinter as ctk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.icon_utils import icon_manager, ICON_ADD, ICON_EDIT, ICON_DELETE, ICON_SAVE, ICON_CANCEL, ICON_SEARCH, ICON_CALENDAR, ICON_EXPORT, ICON_IMPORT, ICON_REFRESH, ICON_SETTINGS, ICON_CATEGORIES, ICON_BILLS, ICON_APPLY, ICON_CLEAR

def test_direct_image_loading():
    """Test loading images directly with CustomTkinter."""
    print("Testing direct image loading...")
    
    try:
        # Initialize CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Test loading an image directly
        icon_file = os.path.join("resources", "icons", f"{ICON_ADD}.png")
        print(f"Testing direct load of: {icon_file}")
        
        if os.path.exists(icon_file):
            try:
                # Try to create CTkImage directly
                image = ctk.CTkImage(light_image=icon_file, dark_image=icon_file, size=(16, 16))
                print(f"✅ Direct CTkImage creation successful")
                return True
            except Exception as e:
                print(f"❌ Direct CTkImage creation failed: {e}")
                return False
        else:
            print(f"❌ Icon file not found: {icon_file}")
            return False
    except Exception as e:
        print(f"❌ CustomTkinter initialization failed: {e}")
        return False

def test_icon_manager_with_gui():
    """Test icon manager with a proper GUI context."""
    print("\nTesting icon manager with GUI context...")
    
    try:
        # Create a root window
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
        # Test icon loading
        icon = icon_manager.get_icon(ICON_ADD)
        if icon:
            print(f"✅ Icon manager loaded {ICON_ADD} successfully")
            
            # Test button creation
            button = icon_manager.get_button_with_icon(root, "Test", ICON_ADD)
            if button:
                print(f"✅ Button with icon created successfully")
                return True
            else:
                print(f"❌ Button creation failed")
                return False
        else:
            print(f"❌ Icon manager failed to load {ICON_ADD}")
            return False
            
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_all_icons_with_gui():
    """Test all icons with GUI context."""
    print("\nTesting all icons with GUI context...")
    
    try:
        # Create a root window
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
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
                icon = icon_manager.get_icon(icon_name)
                if icon:
                    print(f"✅ {icon_name}: Loaded successfully")
                    success_count += 1
                else:
                    print(f"❌ {icon_name}: Failed to load")
            except Exception as e:
                print(f"❌ {icon_name}: Error loading - {e}")
        
        print(f"\nResults: {success_count}/{total_count} icons loaded successfully")
        return success_count == total_count
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    print("Comprehensive Icon Test for Bills Tracker v3")
    print("=" * 50)
    
    # Test direct image loading
    direct_success = test_direct_image_loading()
    
    # Test icon manager with GUI
    gui_success = test_icon_manager_with_gui()
    
    # Test all icons with GUI
    all_icons_success = test_all_icons_with_gui()
    
    print("\n" + "=" * 50)
    print("Final Results:")
    print(f"Direct image loading: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"Icon manager with GUI: {'✅ PASS' if gui_success else '❌ FAIL'}")
    print(f"All icons with GUI: {'✅ PASS' if all_icons_success else '❌ FAIL'}")
    
    if direct_success and gui_success and all_icons_success:
        print("\n🎉 All tests passed! Icons are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.") 