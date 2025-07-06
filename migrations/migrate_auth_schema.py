#!/usr/bin/env python3
"""
Migration script to update the users table schema for the new authentication system.
This script will:
1. Backup the existing users table
2. Create a new users table with the correct schema
3. Migrate existing user data
4. Create the sessions table
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_database():
    """Create a backup of the current database"""
    if os.path.exists('bills_tracker.db'):
        backup_name = f'bills_tracker_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2('bills_tracker.db', backup_name)
        print(f"Database backed up to: {backup_name}")
        return backup_name
    return None

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect('bills_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def migrate_users_table():
    """Migrate the users table to the new schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if we need to migrate
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' in columns and 'failed_login_attempts' in columns:
            print("Users table already has the new schema. No migration needed.")
            return
        
        print("Migrating users table to new schema...")
        
        # Backup existing users data
        cursor.execute("SELECT * FROM users")
        existing_users = cursor.fetchall()
        print(f"Found {len(existing_users)} existing users")
        
        # Create new users table with correct schema
        new_users_schema = '''
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        );
        '''
        
        cursor.execute(new_users_schema)
        
        # Migrate existing user data
        for user in existing_users:
            # Convert is_admin to role
            role = 'admin' if user['is_admin'] else 'user'
            
            cursor.execute('''
                INSERT INTO users_new (
                    id, username, email, password_hash, salt, role, 
                    is_active, created_at, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['id'],
                user['username'],
                user['email'],
                user['password_hash'],
                user['salt'],
                role,
                1,  # is_active
                user['created_at'],
                user['last_login']
            ))
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        print("Users table migration completed successfully!")
        
    except Exception as e:
        print(f"Error during users table migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()

def create_sessions_table():
    """Create the sessions table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        if cursor.fetchone():
            print("Sessions table already exists.")
            return
        
        print("Creating sessions table...")
        
        sessions_schema = '''
        CREATE TABLE sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        '''
        
        cursor.execute(sessions_schema)
        print("Sessions table created successfully!")
        
    except Exception as e:
        print(f"Error creating sessions table: {e}")
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()

def create_default_admin():
    """Create default admin user if no users exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("No users found. Creating default admin user...")
            
            # Import auth functions
            import sys
            sys.path.append('src')
            from core.auth import AuthManager
            
            auth_manager = AuthManager()
            auth_manager.register_user(
                username="admin",
                password="admin123",
                email="admin@bills-tracker.local",
                role="admin"
            )
            
            print("Default admin user created: admin/admin123")
            print("IMPORTANT: Change the default password after first login!")
        else:
            print(f"Found {user_count} existing users. No default admin needed.")
            
    except Exception as e:
        print(f"Error creating default admin: {e}")
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()

def main():
    """Run the complete migration"""
    print("Starting authentication schema migration...")
    
    # Backup database
    backup_file = backup_database()
    
    try:
        # Migrate users table
        migrate_users_table()
        
        # Create sessions table
        create_sessions_table()
        
        # Create default admin if needed
        create_default_admin()
        
        print("\nMigration completed successfully!")
        print("You can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        
        if backup_file:
            print(f"\nOriginal database backed up to: {backup_file}")
        
    except Exception as e:
        print(f"\nMigration failed: {e}")
        if backup_file:
            print(f"Original database is available at: {backup_file}")
        return False
    
    return True

if __name__ == "__main__":
    main() 