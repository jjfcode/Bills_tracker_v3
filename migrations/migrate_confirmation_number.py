#!/usr/bin/env python3
"""
Migration script to add confirmation_number column to bills table.
This script adds the confirmation_number column to track payment confirmation numbers.
"""

import sqlite3
import os

def migrate_confirmation_number():
    """Add confirmation_number column to bills table"""
    db_file = '../bills_tracker.db'
    
    if not os.path.exists(db_file):
        print(f"Database file '{db_file}' not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if confirmation_number column already exists
        cursor.execute("PRAGMA table_info(bills)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'confirmation_number' not in columns:
            print("Adding confirmation_number column to bills table...")
            cursor.execute("ALTER TABLE bills ADD COLUMN confirmation_number TEXT")
            conn.commit()
            print("✓ confirmation_number column added successfully!")
        else:
            print("✓ confirmation_number column already exists.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(bills)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'confirmation_number' in columns:
            print("✓ Migration completed successfully!")
        else:
            print("✗ Migration failed: confirmation_number column not found.")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Bills Tracker v3 - Confirmation Number Migration")
    print("=" * 50)
    migrate_confirmation_number()
    print("=" * 50)
    print("Migration script completed.") 