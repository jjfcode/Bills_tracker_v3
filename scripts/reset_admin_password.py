#!/usr/bin/env python3
"""
Simple script to reset the admin password to 'admin123'
"""

import sys
import os
sys.path.append('src')

from core.auth import AuthManager

def reset_admin_password():
    """Reset admin password to admin123"""
    try:
        auth_manager = AuthManager()
        
        # Delete existing admin user
        conn = auth_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        conn.commit()
        conn.close()
        
        # Create new admin user with correct password
        auth_manager.register_user(
            username="admin",
            password="admin123",
            email="admin@bills-tracker.local",
            role="admin"
        )
        
        print("Admin password reset successfully!")
        print("You can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"Error resetting admin password: {e}")
        return False

if __name__ == "__main__":
    reset_admin_password() 